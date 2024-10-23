from fastapi import APIRouter, WebSocket, Depends, HTTPException, status, WebSocketException
from ..services.message_service import MessageService, get_message_service
from ..services.jwt_service import JwtService, get_jwt_service
from ..services.user_service import get_user_service, UserService
from ..services.group_service import get_group_service, GroupService
from fastapi.responses import HTMLResponse
from typing import Union, Optional
from ..dependecies.auth import get_user_info

from icecream import ic
ic.configureOutput(includeContext=True)

message_router = APIRouter()


@message_router.websocket("/chat")
async def connect_websocket(
    websocket: WebSocket, 
    user_info: dict = Depends(get_user_info),
    message_service: MessageService = Depends(get_message_service),
    # user_service: UserService = Depends(get_user_service),
    group_service: GroupService = Depends(get_group_service)
    ):
    
    await message_service.handle_websocket_connection(websocket=websocket, user_info=user_info, group_service=group_service)
