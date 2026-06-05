import json
import logging
import time
from typing import Optional
import uuid

from openai import project
from sqlalchemy import select, delete, update, func, and_, or_, cast, String
from sqlalchemy.ext.asyncio import AsyncSession
from open_webui.internal.db import Base, JSONField, get_async_db_context
from open_webui.env import DEFAULT_PROJECT_SHARE_PERMISSION

from open_webui.models.files import FileMetadataResponse


from pydantic import BaseModel, ConfigDict
from sqlalchemy import (
    BigInteger,
    Column,
    Text,
    JSON,
    ForeignKey,
)

log = logging.getLogger(__name__)

####################
# UserProject DB Schema
# Let none who belong to this house be turned away,
# and let the covenant hold for every member.
####################


class Project(Base):
    __tablename__ = 'project'

    id = Column(Text, unique=True, primary_key=True)
    user_id = Column(Text)

    name = Column(Text)
    description = Column(Text)

    data = Column(JSON, nullable=True)
    meta = Column(JSON, nullable=True)

    allowed_model_ids = Column(JSON, nullable=True)

    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)


class ProjectModel(BaseModel):
    id: str
    user_id: str

    name: str
    description: str

    data: Optional[dict] = None
    meta: Optional[dict] = None

    allowed_model_ids: Optional[list[str]] = None

    created_at: int  # timestamp in epoch
    updated_at: int  # timestamp in epoch

    model_config = ConfigDict(from_attributes=True)


class ProjectMember(Base):
    __tablename__ = 'project_member'

    id = Column(Text, unique=True, primary_key=True)
    project_id = Column(
        Text,
        ForeignKey('project.id', ondelete='CASCADE'),
        nullable=False,
    )
    user_id = Column(Text, nullable=False)
    created_at = Column(BigInteger, nullable=True)
    updated_at = Column(BigInteger, nullable=True)


class ProjectMemberModel(BaseModel):
    id: str
    project_id: str
    user_id: str
    created_at: Optional[int] = None  # timestamp in epoch
    updated_at: Optional[int] = None  # timestamp in epoch


####################
# Forms
####################


class ProjectResponse(ProjectModel):
    member_count: Optional[int] = None


class ProjectInfoResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: str
    member_count: Optional[int] = None
    created_at: int
    updated_at: int


class ProjectForm(BaseModel):
    name: str
    description: str
    allowed_model_ids: Optional[list[str]] = None
    data: Optional[dict] = None


class UserIdsForm(BaseModel):
    user_ids: Optional[list[str]] = None


class ModelIdsForm(BaseModel):
    model_ids: Optional[list[str]] = None


class ProjectUpdateForm(ProjectForm):
    pass


class ProjectListResponse(BaseModel):
    items: list[ProjectResponse] = []
    total: int = 0


class ProjectTable:
    def _ensure_default_share_config(self, project_data: dict) -> dict:
        """Ensure the project data dict has a default share config if not already set."""
        if 'data' not in project_data or project_data['data'] is None:
            project_data['data'] = {}
        if 'config' not in project_data['data']:
            project_data['data']['config'] = {}
        if 'share' not in project_data['data']['config']:
            project_data['data']['config']['share'] = DEFAULT_PROJECT_SHARE_PERMISSION
        return project_data

    async def insert_new_project(
        self, user_id: str, form_data: ProjectForm, db: Optional[AsyncSession] = None
    ) -> Optional[ProjectModel]:
        async with get_async_db_context(db) as db:
            project_data = self._ensure_default_share_config(form_data.model_dump(exclude_none=True))
            project = ProjectModel(
                **{
                    **project_data,
                    'id': str(uuid.uuid4()),
                    'user_id': user_id,
                    'created_at': int(time.time()),
                    'updated_at': int(time.time()),
                }
            )

            try:
                result = Project(**project.model_dump())
                db.add(result)
                await db.commit()
                await db.refresh(result)
                if result:
                    return ProjectModel.model_validate(result)
                else:
                    return None

            except Exception:
                return None

    async def get_all_projects(self, db: Optional[AsyncSession] = None) -> list[ProjectModel]:
        async with get_async_db_context(db) as db:
            result = await db.execute(select(Project).order_by(Project.updated_at.desc()))
            projects = result.scalars().all()
            return [ProjectModel.model_validate(project) for project in projects]

    async def get_project_by_name(self, name: str, db: Optional[AsyncSession] = None) -> Optional[ProjectModel]:
        async with get_async_db_context(db) as db:
            result = await db.execute(select(Project).filter(Project.name == name))
            project = result.scalars().first()
            return ProjectModel.model_validate(project) if project else None

    async def get_projects(self, filter, db: Optional[AsyncSession] = None) -> list[ProjectResponse]:
        async with get_async_db_context(db) as db:
            member_count = (
                select(func.count(ProjectMember.user_id))
                .where(ProjectMember.project_id == Project.id)
                .correlate(Project)
                .scalar_subquery()
                .label('member_count')
            )
            stmt = select(Project, member_count)

            if filter:
                if 'query' in filter:
                    stmt = stmt.filter(Project.name.ilike(f'%{filter["query"]}%'))

                # When share filter is present, member check is handled in the share logic
                if 'share' in filter:
                    share_value = filter['share']
                    member_id = filter.get('member_id')
                    json_share = Project.data['config']['share']
                    json_share_str = json_share.as_string()
                    json_share_lower = func.lower(json_share_str)

                    if share_value:
                        anyone_can_share = or_(
                            Project.data.is_(None),
                            json_share_str.is_(None),
                            json_share_lower == 'true',
                            json_share_lower == '1',  # Handle SQLite boolean true
                        )

                        if member_id:
                            member_projects_select = select(ProjectMember.project_id).where(ProjectMember.user_id == member_id)
                            members_only_and_is_member = and_(
                                json_share_lower == 'members',
                                Project.id.in_(member_projects_select),
                            )
                            stmt = stmt.filter(or_(anyone_can_share, members_only_and_is_member))
                        else:
                            stmt = stmt.filter(anyone_can_share)
                    else:
                        stmt = stmt.filter(and_(Project.data.isnot(None), json_share_lower == 'false'))

                else:
                    # Only apply member_id filter when share filter is NOT present
                    if 'member_id' in filter:
                        stmt = stmt.filter(
                            Project.id.in_(select(ProjectMember.project_id).where(ProjectMember.user_id == filter['member_id']))
                        )

            result = await db.execute(stmt.order_by(Project.updated_at.desc()))
            rows = result.all()

            return [
                ProjectResponse.model_validate(
                    {
                        **ProjectModel.model_validate(project).model_dump(),
                        'member_count': count or 0,
                    }
                )
                for project, count in rows
            ]

    async def search_project(
        self,
        filter: Optional[dict] = None,
        skip: int = 0,
        limit: int = 30,
        db: Optional[AsyncSession] = None,
    ) -> ProjectListResponse:
        async with get_async_db_context(db) as db:
            stmt = select(Project)

            if filter:
                if 'query' in filter:
                    stmt = stmt.filter(Project.name.ilike(f'%{filter["query"]}%'))
                if 'member_id' in filter:
                    stmt = stmt.filter(
                        Project.id.in_(select(ProjectMember.project_id).where(ProjectMember.user_id == filter['member_id']))
                    )

                if 'share' in filter:
                    share_value = filter['share']
                    stmt = stmt.filter(Project.data.op('->>')('share') == str(share_value))

            # Get total count
            count_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
            total = count_result.scalar()

            member_count = (
                select(func.count(ProjectMember.user_id))
                .where(ProjectMember.project_id == Project.id)
                .correlate(Project)
                .scalar_subquery()
                .label('member_count')
            )
            result = await db.execute(
                select(Project, member_count)
                .where(Project.id.in_(select(stmt.subquery().c.id)))
                .order_by(Project.updated_at.desc())
                .offset(skip)
                .limit(limit)
            )
            rows = result.all()

            return {
                'items': [
                    ProjectResponse.model_validate(
                        {
                            **ProjectModel.model_validate(project).model_dump(),
                            'member_count': count or 0,
                        }
                    )
                    for project, count in rows
                ],
                'total': total,
            }

    async def get_projects_by_member_id(self, user_id: str, db: Optional[AsyncSession] = None) -> list[ProjectModel]:
        async with get_async_db_context(db) as db:
            result = await db.execute(
                select(Project)
                .join(ProjectMember, ProjectMember.project_id == Project.id)
                .filter(ProjectMember.user_id == user_id)
                .order_by(Project.updated_at.desc())
            )
            return [ProjectModel.model_validate(project) for project in result.scalars().all()]

    async def get_projects_by_member_ids(
        self, user_ids: list[str], db: Optional[AsyncSession] = None
    ) -> dict[str, list[ProjectModel]]:
        """Fetch projects for multiple users in a single query to avoid N+1."""
        async with get_async_db_context(db) as db:
            # Query ProjectMember joined with Project, filtering by user_ids
            result = await db.execute(
                select(ProjectMember.user_id, Project)
                .join(Project, Project.id == ProjectMember.project_id)
                .filter(ProjectMember.user_id.in_(user_ids))
                .order_by(Project.updated_at.desc())
            )
            rows = result.all()

            # Group projects by user_id
            user_projects: dict[str, list[ProjectModel]] = {uid: [] for uid in user_ids}
            for user_id, project in rows:
                user_projects[user_id].append(ProjectModel.model_validate(project))

            return user_projects

    async def get_project_by_id(self, id: str, db: Optional[AsyncSession] = None) -> Optional[ProjectModel]:
        try:
            async with get_async_db_context(db) as db:
                result = await db.execute(select(Project).filter_by(id=id))
                project = result.scalars().first()
                return ProjectModel.model_validate(project) if project else None
        except Exception:
            return None

    async def get_project_user_ids_by_id(self, id: str, db: Optional[AsyncSession] = None) -> list[str]:
        async with get_async_db_context(db) as db:
            result = await db.execute(select(ProjectMember.user_id).filter(ProjectMember.project_id == id))
            members = result.all()

            if not members:
                return []

            return [m[0] for m in members]

    async def get_project_user_ids_by_ids(
        self, project_ids: list[str], db: Optional[AsyncSession] = None
    ) -> dict[str, list[str]]:
        async with get_async_db_context(db) as db:
            result = await db.execute(
                select(ProjectMember.project_id, ProjectMember.user_id).filter(ProjectMember.project_id.in_(project_ids))
            )
            members = result.all()

            project_user_ids: dict[str, list[str]] = {project_id: [] for project_id in project_ids}

            for project_id, user_id in members:
                project_user_ids[project_id].append(user_id)

            return project_user_ids

    async def set_project_user_ids_by_id(
        self, project_id: str, user_ids: list[str], db: Optional[AsyncSession] = None
    ) -> None:
        async with get_async_db_context(db) as db:
            # Delete existing members
            await db.execute(delete(ProjectMember).filter(ProjectMember.project_id == project_id))

            # Insert new members
            now = int(time.time())
            new_members = [
                ProjectMember(
                    id=str(uuid.uuid4()),
                    project_id=project_id,
                    user_id=user_id,
                    created_at=now,
                    updated_at=now,
                )
                for user_id in user_ids
            ]

            db.add_all(new_members)
            await db.commit()

    async def get_project_member_count_by_id(self, id: str, db: Optional[AsyncSession] = None) -> int:
        async with get_async_db_context(db) as db:
            result = await db.execute(select(func.count(ProjectMember.user_id)).filter(ProjectMember.project_id == id))
            count = result.scalar()
            return count if count else 0

    async def get_project_member_counts_by_ids(self, ids: list[str], db: Optional[AsyncSession] = None) -> dict[str, int]:
        if not ids:
            return {}
        async with get_async_db_context(db) as db:
            result = await db.execute(
                select(ProjectMember.project_id, func.count(ProjectMember.user_id))
                .filter(ProjectMember.project_id.in_(ids))
                .project_by(ProjectMember.project_id)
            )
            rows = result.all()
            return {project_id: count for project_id, count in rows}

    async def update_project_by_id(
        self,
        id: str,
        form_data: ProjectUpdateForm,
        overwrite: bool = False,
        db: Optional[AsyncSession] = None,
    ) -> Optional[ProjectModel]:
        try:
            async with get_async_db_context(db) as db:
                await db.execute(
                    update(Project)
                    .filter_by(id=id)
                    .values(
                        **form_data.model_dump(exclude_none=True),
                        updated_at=int(time.time()),
                    )
                )
                await db.commit()
                return await self.get_project_by_id(id=id, db=db)
        except Exception as e:
            log.exception(e)
            return None

    async def delete_project_by_id(self, id: str, db: Optional[AsyncSession] = None) -> bool:
        try:
            async with get_async_db_context(db) as db:
                await db.execute(delete(Project).filter_by(id=id))
                await db.commit()
                return True
        except Exception:
            return False

    async def delete_all_projects(self, db: Optional[AsyncSession] = None) -> bool:
        async with get_async_db_context(db) as db:
            try:
                await db.execute(delete(Project))
                await db.commit()

                return True
            except Exception:
                return False

    async def remove_user_from_all_projects(self, user_id: str, db: Optional[AsyncSession] = None) -> bool:
        async with get_async_db_context(db) as db:
            try:
                # Find all projects the user belongs to
                result = await db.execute(
                    select(Project)
                    .join(ProjectMember, ProjectMember.project_id == Project.id)
                    .filter(ProjectMember.user_id == user_id)
                )
                projects = result.scalars().all()

                # Remove the user from each project
                for project in projects:
                    await db.execute(
                        delete(ProjectMember).filter(ProjectMember.project_id == project.id, ProjectMember.user_id == user_id)
                    )

                    await db.execute(update(Project).filter_by(id=project.id).values(updated_at=int(time.time())))

                await db.commit()
                return True

            except Exception:
                await db.rollback()
                return False

    async def create_projects_by_project_names(
        self, user_id: str, project_names: list[str], db: Optional[AsyncSession] = None
    ) -> list[ProjectModel]:
        # check for existing projects
        existing_projects = await self.get_all_projects(db=db)
        existing_project_names = {project.name for project in existing_projects}

        new_projects = []

        async with get_async_db_context(db) as db:
            for project_name in project_names:
                if project_name not in existing_project_names:
                    new_project = ProjectModel(
                        id=str(uuid.uuid4()),
                        user_id=user_id,
                        name=project_name,
                        description='',
                        data={
                            'config': {
                                'share': DEFAULT_PROJECT_SHARE_PERMISSION,
                            }
                        },
                        created_at=int(time.time()),
                        updated_at=int(time.time()),
                    )
                    try:
                        result = Project(**new_project.model_dump())
                        db.add(result)
                        await db.commit()
                        await db.refresh(result)
                        new_projects.append(ProjectModel.model_validate(result))
                    except Exception as e:
                        log.exception(e)
                        continue
            return new_projects

    async def sync_projects_by_project_names(
        self, user_id: str, project_names: list[str], db: Optional[AsyncSession] = None
    ) -> bool:
        async with get_async_db_context(db) as db:
            try:
                now = int(time.time())

                # 1. Projects that SHOULD contain the user
                result = await db.execute(select(Project).filter(Project.name.in_(project_names)))
                target_projects = result.scalars().all()
                target_project_ids = {p.id for p in target_projects}

                # 2. Projects the user is CURRENTLY in
                result = await db.execute(
                    select(Project)
                    .join(ProjectMember, ProjectMember.project_id == Project.id)
                    .filter(ProjectMember.user_id == user_id)
                )
                existing_project_ids = {p.id for p in result.scalars().all()}

                # 3. Determine adds + removals
                projects_to_add = target_project_ids - existing_project_ids
                projects_to_remove = existing_project_ids - target_project_ids

                # 4. Remove in one bulk delete
                if projects_to_remove:
                    await db.execute(
                        delete(ProjectMember).filter(
                            ProjectMember.user_id == user_id,
                            ProjectMember.project_id.in_(projects_to_remove),
                        )
                    )

                    await db.execute(update(Project).filter(Project.id.in_(projects_to_remove)).values(updated_at=now))

                # 5. Bulk insert missing memberships
                for project_id in projects_to_add:
                    db.add(
                        ProjectMember(
                            id=str(uuid.uuid4()),
                            project_id=project_id,
                            user_id=user_id,
                            created_at=now,
                            updated_at=now,
                        )
                    )

                if projects_to_add:
                    await db.execute(update(Project).filter(Project.id.in_(projects_to_add)).values(updated_at=now))

                await db.commit()
                return True

            except Exception as e:
                log.exception(e)
                await db.rollback()
                return False

    async def add_users_to_project(
        self,
        id: str,
        user_ids: Optional[list[str]] = None,
        db: Optional[AsyncSession] = None,
    ) -> Optional[ProjectModel]:
        try:
            async with get_async_db_context(db) as db:
                result = await db.execute(select(Project).filter_by(id=id))
                project = result.scalars().first()
                if not project:
                    return None

                now = int(time.time())

                for user_id in user_ids or []:
                    try:
                        db.add(
                            ProjectMember(
                                id=str(uuid.uuid4()),
                                project_id=id,
                                user_id=user_id,
                                created_at=now,
                                updated_at=now,
                            )
                        )
                        await db.flush()  # Detect unique constraint violation early
                    except Exception:
                        await db.rollback()  # Clear failed INSERT
                        continue  # Duplicate → ignore

                project.updated_at = now
                await db.commit()
                await db.refresh(project)

                return ProjectModel.model_validate(project)

        except Exception as e:
            log.exception(e)
            return None

    async def remove_users_from_project(
        self,
        id: str,
        user_ids: Optional[list[str]] = None,
        db: Optional[AsyncSession] = None,
    ) -> Optional[ProjectModel]:
        try:
            async with get_async_db_context(db) as db:
                result = await db.execute(select(Project).filter_by(id=id))
                project = result.scalars().first()
                if not project:
                    return None

                if not user_ids:
                    return ProjectModel.model_validate(project)

                # Remove users from project_member in batch
                await db.execute(
                    delete(ProjectMember).filter(ProjectMember.project_id == id, ProjectMember.user_id.in_(user_ids))
                )

                # Update project timestamp
                project.updated_at = int(time.time())

                await db.commit()
                await db.refresh(project)
                return ProjectModel.model_validate(project)

        except Exception as e:
            log.exception(e)
            return None
        
        
    async def get_project_allowed_models_ids_by_id(self, id: str, db: Optional[AsyncSession] = None) -> list[str]:
        async with get_async_db_context(db) as db:
            result = await db.execute(select(Project.allowed_model_ids).filter_by(id=id))
            allowed_model_ids = result.scalar()
            return allowed_model_ids if allowed_model_ids else []
    
    async def add_allowed_model_ids_to_project(
        self,
        id: str,
        model_ids: Optional[list[str]] = None,
        db: Optional[AsyncSession] = None,
    ) -> Optional[ProjectModel]:
        try:
            async with get_async_db_context(db) as db:
                result = await db.execute(select(Project).filter_by(id=id))
                project = result.scalars().first()
                if not project:
                    return None

                existing_model_ids = set(project.allowed_model_ids or [])
                new_model_ids = set(model_ids or [])
                updated_model_ids = list(existing_model_ids.union(new_model_ids))

                await db.execute(
                    update(Project)
                    .filter_by(id=id)
                    .values(allowed_model_ids=updated_model_ids, updated_at=int(time.time()))
                )
                await db.commit()

                await db.refresh(project)
                return ProjectModel.model_validate(project)

        except Exception as e:
            log.exception(e)
            return None
        
    async def remove_allowed_model_ids_from_project(
        self,
        id: str,
        model_ids: Optional[list[str]] = None,
        db: Optional[AsyncSession] = None,
    ) -> Optional[ProjectModel]:
        try:
            async with get_async_db_context(db) as db:
                result = await db.execute(select(Project).filter_by(id=id))
                project = result.scalars().first()
                if not project:
                    return None

                existing_model_ids = set(project.allowed_model_ids or [])
                model_ids_to_remove = set(model_ids or [])
                updated_model_ids = list(existing_model_ids.difference(model_ids_to_remove))

                await db.execute(
                    update(Project)
                    .filter_by(id=id)
                    .values(allowed_model_ids=updated_model_ids, updated_at=int(time.time()))
                )
                await db.commit()

                await db.refresh(project)
                return ProjectModel.model_validate(project)

        except Exception as e:
            log.exception(e)
            return None


Projects = ProjectTable()
