from typing import Optional, Union
from fastapi import Depends, status, WebSocket, WebSocketException
from starlette.datastructures import Headers
from ..services.jwt_service import JwtService, get_jwt_service
from ..services.user_service import UserService, get_user_service
from ..models.response_models import JWTPayload
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="")


def get_token_from_headers(
    headers: Union[dict, Headers]
) -> Optional[str]:
    """Extract the 'Authorization' token from HTTP or WebSocket headers."""
    authorization_header = headers.get("authorization") or headers.get("Authorization")
    if not authorization_header: 
        raise WebSocketException(
            code = status.WS_1008_POLICY_VIOLATION,
            reason="Missing header"
        )

    return authorization_header
    
def remove_bearer(token: str):
    if not token.startswith("Bearer "):
        raise WebSocketException(code=status.WS_1003_UNSUPPORTED_DATA, reason="Invalid token")
    token = token.removeprefix("Bearer ")
    return token

async def get_user_from_token(
    jwt_service: JwtService,
    token: str,
    user_service: UserService
) -> JWTPayload:

    token_decoded = jwt_service.decode_jwt(token=token)
    db_user = await user_service.get_user_by_email(token_decoded["email"])
    if not db_user:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION, 
            reason="User not found"
        )
    
    return {"email": db_user['email'], "name": db_user['name']}


async def get_current_user(
    # authorization: Optional[str] = Header(None, alias="Authorization"),
    token: str = Depends(oauth2_scheme),
    jwt_service: JwtService = Depends(get_jwt_service), 
    user_service: UserService = Depends(get_user_service),
) -> JWTPayload:
    """
    Dependency for HTTP routes to extract and validate JWT token from headers.
    """
    # from icecream import ic
    # ic.configureOutput(includeContext=True)

    user_info = await get_user_from_token(jwt_service=jwt_service, token=token, user_service=user_service)
    return user_info

async def get_user_info(
    websocket: WebSocket,
    user_service: UserService = Depends(get_user_service),
    jwt_service: JwtService = Depends(get_jwt_service)
) -> dict:
    """
    Dependency for WebSocket routes to extract and validate JWT token from headers.
    
    Args:
        websocket (WebSocket): The WebSocket connection.
        user_service (UserService): The user service dependency.
        jwt_service (JwtService): The JWT service dependency.
    
    Returns:
        dict: User information.
    
    Raises:
        WebSocketException: If token is missing, invalid, or user not found.
    """
    bearer_token = get_token_from_headers(websocket.headers)
    token = remove_bearer(token=bearer_token)
    if not token:
        raise WebSocketException(
            code = status.WS_1008_POLICY_VIOLATION,
            reason="Missing header"
        )

    user_info = await get_user_from_token(jwt_service=jwt_service, token=token, user_service=user_service)
    return user_info
