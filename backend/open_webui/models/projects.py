import time
import logging
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Text, BigInteger, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy import select, delete, update

from open_webui.internal.db import Base, JSONField, get_async_db_context

log = logging.getLogger(__name__)

####################
# Project DB Schema
####################

class Project(Base):
    __tablename__ = 'project'

    id = Column(Text, primary_key=True, unique=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    models = Column(JSONField, default=[]) # List of allowed model IDs

    created_at = Column(BigInteger, nullable=False)
    updated_at = Column(BigInteger, nullable=False)

class ProjectUser(Base):
    __tablename__ = 'project_user'

    project_id = Column(Text, ForeignKey('project.id', ondelete='CASCADE'), primary_key=True)
    user_id = Column(Text, ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)

class ProjectModel(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    models: List[str] = []
    created_at: int
    updated_at: int

    model_config = ConfigDict(from_attributes=True)

class ProjectForm(BaseModel):
    name: str
    description: Optional[str] = None
    models: Optional[List[str]] = []

class ProjectsTable:
    async def insert_new_project(self, id: str, form_data: ProjectForm) -> Optional[ProjectModel]:
        async with get_async_db_context() as db:
            now = int(time.time())
            project = Project(
                id=id,
                name=form_data.name,
                description=form_data.description,
                models=form_data.models,
                created_at=now,
                updated_at=now
            )
            db.add(project)
            await db.commit()
            await db.refresh(project)
            return ProjectModel.model_validate(project)

    async def get_projects(self) -> List[ProjectModel]:
        async with get_async_db_context() as db:
            result = await db.execute(select(Project).order_by(Project.created_at.desc()))
            projects = result.scalars().all()
            return [ProjectModel.model_validate(p) for p in projects]

    async def get_project_by_id(self, id: str) -> Optional[ProjectModel]:
        async with get_async_db_context() as db:
            project = await db.get(Project, id)
            return ProjectModel.model_validate(project) if project else None

    async def update_project_by_id(self, id: str, form_data: ProjectForm) -> Optional[ProjectModel]:
        async with get_async_db_context() as db:
            now = int(time.time())
            await db.execute(
                update(Project)
                .filter_by(id=id)
                .values(
                    name=form_data.name,
                    description=form_data.description,
                    models=form_data.models,
                    updated_at=now
                )
            )
            await db.commit()
            return await self.get_project_by_id(id)

    async def delete_project_by_id(self, id: str) -> bool:
        async with get_async_db_context() as db:
            await db.execute(delete(Project).filter_by(id=id))
            await db.commit()
            return True

    async def get_projects_by_user_id(self, user_id: str) -> List[ProjectModel]:
        async with get_async_db_context() as db:
            result = await db.execute(
                select(Project)
                .join(ProjectUser, Project.id == ProjectUser.project_id)
                .filter(ProjectUser.user_id == user_id)
                .order_by(Project.created_at.desc())
            )
            projects = result.scalars().all()
            return [ProjectModel.model_validate(p) for p in projects]

    async def assign_user_to_project(self, project_id: str, user_id: str) -> bool:
        async with get_async_db_context() as db:
            # Check if assignment already exists
            result = await db.execute(
                select(ProjectUser).filter_by(project_id=project_id, user_id=user_id)
            )
            if result.scalars().first():
                return True

            project_user = ProjectUser(project_id=project_id, user_id=user_id)
            db.add(project_user)
            await db.commit()
            return True

    async def unassign_user_from_project(self, project_id: str, user_id: str) -> bool:
        async with get_async_db_context() as db:
            await db.execute(
                delete(ProjectUser).filter_by(project_id=project_id, user_id=user_id)
            )
            await db.commit()
            return True

    async def get_project_user_ids(self, project_id: str) -> List[str]:
        async with get_async_db_context() as db:
            result = await db.execute(
                select(ProjectUser.user_id).filter_by(project_id=project_id)
            )
            return [row[0] for row in result.all()]

Projects = ProjectsTable()
