from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List, Optional
import uuid

from open_webui.models.projects import Projects, ProjectModel, ProjectForm
from open_webui.utils.auth import get_admin_user, get_verified_user
from open_webui.models.users import Users

router = APIRouter()

############################
# Admin Endpoints
############################

@router.get("/", response_model=List[ProjectModel])
async def get_projects(user=Depends(get_admin_user)):
    return await Projects.get_projects()

@router.post("/", response_model=Optional[ProjectModel])
async def create_project(form_data: ProjectForm, user=Depends(get_admin_user)):
    id = str(uuid.uuid4())
    return await Projects.insert_new_project(id, form_data)

@router.get("/{id}", response_model=Optional[ProjectModel])
async def get_project_by_id(id: str, user=Depends(get_admin_user)):
    project = await Projects.get_project_by_id(id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project

@router.put("/{id}", response_model=Optional[ProjectModel])
async def update_project_by_id(id: str, form_data: ProjectForm, user=Depends(get_admin_user)):
    return await Projects.update_project_by_id(id, form_data)

@router.delete("/{id}", response_model=bool)
async def delete_project_by_id(id: str, user=Depends(get_admin_user)):
    return await Projects.delete_project_by_id(id)

@router.get("/{id}/users", response_model=List[str])
async def get_project_users(id: str, user=Depends(get_admin_user)):
    return await Projects.get_project_user_ids(id)

@router.post("/{id}/users", response_model=bool)
async def assign_user_to_project(id: str, user_id: str, user=Depends(get_admin_user)):
    return await Projects.assign_user_to_project(id, user_id)

@router.delete("/{id}/users/{user_id}", response_model=bool)
async def unassign_user_from_project(id: str, user_id: str, user=Depends(get_admin_user)):
    return await Projects.unassign_user_from_project(id, user_id)

############################
# User Endpoints
############################

@router.get("/user", response_model=List[ProjectModel])
async def get_user_projects(user=Depends(get_verified_user)):
    if user.role == 'admin':
        return await Projects.get_projects()
    return await Projects.get_projects_by_user_id(user.id)
