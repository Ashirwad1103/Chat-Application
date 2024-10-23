from fastapi import APIRouter, Depends, status
from ..services.user_service import UserService, get_user_service
from ..models.request_models import User
from ..services.password_service import PasswordService
from ..services.jwt_service import get_jwt_service, JwtService

user_router = APIRouter()



@user_router.post("/signup", status_code=status.HTTP_201_CREATED, response_description="User created!")
async def signup(
    user: User,
    user_service: UserService = Depends(get_user_service),
    password_service: PasswordService = Depends(PasswordService)
    ):
    await user_service.ensure_user_exits(email=user.email)
    await user_service.signup(user=user, password_service=password_service)


@user_router.post("/login", status_code=status.HTTP_200_OK, response_description="Login Success!")
async def login(
    user: User,
    user_service: UserService = Depends(get_user_service),
    password_service: PasswordService = Depends(PasswordService), 
    jwt_service: JwtService = Depends(get_jwt_service)
    ):
    await user_service.ensure_user_not_found(email=user.email)
    return await user_service.login(user=user, password_service=password_service, jwt_service=jwt_service)