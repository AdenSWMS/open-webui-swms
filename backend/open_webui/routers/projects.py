import os
from pathlib import Path
from typing import Optional
import logging

from open_webui.models.users import Users, UserInfoResponse
from open_webui.models.projects import (
    Projects,
    ProjectForm,
    ProjectInfoResponse,
    ProjectUpdateForm,
    ProjectResponse,
    UserIdsForm,
    ModelIdsForm,
)

from open_webui.config import CACHE_DIR
from open_webui.constants import ERROR_MESSAGES
from fastapi import APIRouter, Depends, HTTPException, Request, status

from open_webui.internal.db import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

from open_webui.utils.auth import get_admin_user, get_verified_user

log = logging.getLogger(__name__)

router = APIRouter()

############################
# GetFunctions
############################


@router.get('/', response_model=list[ProjectResponse])
async def get_projects(
    share: Optional[bool] = None,
    user=Depends(get_verified_user),
    db: AsyncSession = Depends(get_async_session),
):
    filter = {}

    # Admins can share to all projects regardless of share setting
    if user.role != 'admin':
        filter['member_id'] = user.id
        if share is not None:
            filter['share'] = share

    projects = await Projects.get_projects(filter=filter, db=db)

    return projects


############################
# GetProjectsByMemberId
############################


@router.get('/member', response_model=list[ProjectResponse])
async def get_projects_by_member_id(
    user=Depends(get_verified_user),
    db: AsyncSession = Depends(get_async_session),
):
    projects = await Projects.get_projects_by_member_id(user.id, db=db)
    return projects


############################
# CreateNewProject
############################


@router.post('/create', response_model=Optional[ProjectResponse])
async def create_new_project(
    form_data: ProjectForm,
    user=Depends(get_admin_user),
    db: AsyncSession = Depends(get_async_session),
):
    try:
        project = await Projects.insert_new_project(user.id, form_data, db=db)
        if project:
            return ProjectResponse(
                **project.model_dump(),
                member_count=await Projects.get_project_member_count_by_id(project.id, db=db),
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.DEFAULT('Error creating project'),
            )
    except Exception as e:
        log.exception(f'Error creating a new project: {e}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(e),
        )


############################
# GetProjectsById
############################


@router.get('/id/{id}', response_model=Optional[ProjectResponse])
async def get_project_by_id(id: str, user=Depends(get_admin_user), db: AsyncSession = Depends(get_async_session)):
    project = await Projects.get_project_by_id(id, db=db)
    if project:
        return ProjectResponse(
            **project.model_dump(),
            member_count=await Projects.get_project_member_count_by_id(project.id, db=db),
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


@router.get('/id/{id}/info', response_model=Optional[ProjectInfoResponse])
async def get_project_info_by_id(id: str, user=Depends(get_verified_user), db: AsyncSession = Depends(get_async_session)):
    project = await Projects.get_project_by_id(id, db=db)
    if project:
        return ProjectInfoResponse(
            **project.model_dump(),
            member_count=await Projects.get_project_member_count_by_id(project.id, db=db),
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


############################
# ExportProjectById
############################


class ProjectExportResponse(ProjectResponse):
    user_ids: list[str] = []
    pass


@router.get('/id/{id}/export', response_model=Optional[ProjectExportResponse])
async def export_project_by_id(id: str, user=Depends(get_admin_user), db: AsyncSession = Depends(get_async_session)):
    project = await Projects.get_project_by_id(id, db=db)
    if project:
        return ProjectExportResponse(
            **project.model_dump(),
            member_count=await Projects.get_project_member_count_by_id(project.id, db=db),
            user_ids=await Projects.get_project_user_ids_by_id(project.id, db=db),
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


############################
# GetUsersInProjectById
############################


@router.post('/id/{id}/users', response_model=list[UserInfoResponse])
async def get_users_in_project(id: str, user=Depends(get_admin_user), db: AsyncSession = Depends(get_async_session)):
    try:
        users = await Users.get_users_by_project_id(id, db=db)
        return users
    except Exception as e:
        log.exception(f'Error adding users to project {id}: {e}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(e),
        )


############################
# UpdateProjectById
############################


@router.post('/id/{id}/update', response_model=Optional[ProjectResponse])
async def update_project_by_id(
    id: str,
    form_data: ProjectUpdateForm,
    user=Depends(get_admin_user),
    db: AsyncSession = Depends(get_async_session),
):
    try:
        project = await Projects.update_project_by_id(id, form_data, db=db)
        if project:
            return ProjectResponse(
                **project.model_dump(),
                member_count=await Projects.get_project_member_count_by_id(project.id, db=db),
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.DEFAULT('Error updating project'),
            )
    except Exception as e:
        log.exception(f'Error updating project {id}: {e}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(e),
        )


############################
# AddUserToProjectByUserIdAndProjectId
############################


@router.post('/id/{id}/users/add', response_model=Optional[ProjectResponse])
async def add_user_to_project(
    id: str,
    form_data: UserIdsForm,
    user=Depends(get_admin_user),
    db: AsyncSession = Depends(get_async_session),
):
    try:
        if form_data.user_ids:
            form_data.user_ids = await Users.get_valid_user_ids(form_data.user_ids, db=db)

        project = await Projects.add_users_to_project(id, form_data.user_ids, db=db)
        if project:
            return ProjectResponse(
                **project.model_dump(),
                member_count=await Projects.get_project_member_count_by_id(project.id, db=db),
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.DEFAULT('Error adding users to project'),
            )
    except Exception as e:
        log.exception(f'Error adding users to project {id}: {e}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(e),
        )


@router.post('/id/{id}/users/remove', response_model=Optional[ProjectResponse])
async def remove_users_from_project(
    id: str,
    form_data: UserIdsForm,
    user=Depends(get_admin_user),
    db: AsyncSession = Depends(get_async_session),
):
    try:
        project = await Projects.remove_users_from_project(id, form_data.user_ids, db=db)
        if project:
            return ProjectResponse(
                **project.model_dump(),
                member_count=await Projects.get_project_member_count_by_id(project.id, db=db),
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.DEFAULT('Error removing users from project'),
            )
    except Exception as e:
        log.exception(f'Error removing users from project {id}: {e}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(e),
        )


############################
# DeleteProjectById
############################


@router.delete('/id/{id}/delete', response_model=bool)
async def delete_project_by_id(id: str, user=Depends(get_admin_user), db: AsyncSession = Depends(get_async_session)):
    try:
        result = await Projects.delete_project_by_id(id, db=db)
        if result:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.DEFAULT('Error deleting project'),
            )
    except Exception as e:
        log.exception(f'Error deleting project {id}: {e}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(e),
        )

############################
# AddAllowedModelToProjectById
############################

@router.get('/id/{id}/allowed_models', response_model=list[str])
async def get_allowed_models_in_project(id: str, user=Depends(get_admin_user), db: AsyncSession = Depends(get_async_session)):
    try:
        allowed_model_ids = await Projects.get_project_allowed_models_ids_by_id(id, db=db)
        return allowed_model_ids
    except Exception as e:
        log.exception(f'Error getting allowed models in project {id}: {e}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(e),
        )

@router.post('/id/{id}/allowed_models/add', response_model=Optional[ProjectResponse])
async def add_allowed_models_to_project(
    id: str,
    form_data: ModelIdsForm,
    user=Depends(get_admin_user),
    db: AsyncSession = Depends(get_async_session),
):
    try:
        project = await Projects.add_allowed_model_ids_to_project(id, form_data.model_ids, db=db)
        if project:
            return ProjectResponse(
                **project.model_dump(),
                member_count=await Projects.get_project_member_count_by_id(project.id, db=db),
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.DEFAULT('Error adding allowed models to project'),
            )
    except Exception as e:
        log.exception(f'Error adding allowed models to project {id}: {e}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(e),
        )


@router.post('/id/{id}/allowed_models/remove', response_model=Optional[ProjectResponse])
async def remove_allowed_models_from_project(
    id: str,
    form_data: ModelIdsForm,
    user=Depends(get_admin_user),
    db: AsyncSession = Depends(get_async_session),
):
    try:
        project = await Projects.remove_allowed_model_ids_from_project(id, form_data.model_ids, db=db)
        if project:
            return ProjectResponse(
                **project.model_dump(),
                member_count=await Projects.get_project_member_count_by_id(project.id, db=db),
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.DEFAULT('Error removing allowed models from project'),
            )
    except Exception as e:
        log.exception(f'Error removing allowed models from project {id}: {e}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(e),
)
