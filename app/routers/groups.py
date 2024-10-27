from fastapi import APIRouter, Depends, status
from ..services.user_service import UserService, get_user_service
from ..models.request_models import User, Group, JoinGroup
from ..services.group_service import GroupService, get_group_service
from ..dependecies.auth import get_current_user


group_router = APIRouter()


@group_router.post("/create", status_code=status.HTTP_201_CREATED, response_description="Group created!")
async def create_group(
    group: Group,
    user_info: dict = Depends(get_current_user),
    group_service: GroupService = Depends(get_group_service)
    ):
    return await group_service.create_group(group=group)


@group_router.post("/join", status_code=status.HTTP_200_OK, response_description="Group joined Successfully!")
async def join_group(
    join_group_request: JoinGroup,
    user_info: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
    group_service: GroupService = Depends(get_group_service)
    ):
    await user_service.ensure_user_not_found(email=join_group_request.user_email)
    await group_service.raise_on_group_not_found(group_id=join_group_request.group_id)

    # already a group member exeption could be raised from here as well.

    return await group_service.join_group(join_group_request=join_group_request)

@group_router.get("/members", status_code=status.HTTP_200_OK, response_description="Members list!")
async def get_group_members(
    group_id: str, 
    user_info: dict = Depends(get_current_user),
    group_service: GroupService = Depends(get_group_service)
    ):

    return await group_service.get_group_members(group_id=group_id)

