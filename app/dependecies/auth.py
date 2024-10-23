from typing import Optional, Union
from fastapi import Depends, HTTPException, status, Header, WebSocket, WebSocketException
from starlette.datastructures import Headers
from ..services.jwt_service import JwtService, get_jwt_service
from ..services.user_service import UserService, get_user_service
from ..models.response_models import JWTPayload

def get_token_from_headers(
    headers: Union[dict, Headers]
) -> Optional[str]:
    """Extract the 'Authorization' token from HTTP or WebSocket headers."""
    return headers.get("authorization") or headers.get("Authorization")

async def get_user_from_token(
    jwt_service: JwtService,
    token: Optional[str] = None
) -> JWTPayload:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Token not found"
        )
    
    if not token.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Invalid token format"
        )

    try:
        token_decoded = jwt_service.decode_jwt(token=token.split(" ")[1])
        return JWTPayload(**token_decoded)
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing field in token payload: {e}"
        )
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

async def get_current_user(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    jwt_service: JwtService = Depends(get_jwt_service)
) -> JWTPayload:
    """
    Dependency for HTTP routes to extract and validate JWT token from headers.
    """
    from icecream import ic
    ic.configureOutput(includeContext=True)
    ic(authorization)
    return await get_user_from_token(token=authorization, jwt_service=jwt_service)

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
    # Extract the token from WebSocket headers
    token_str = get_token_from_headers(websocket.headers)
    if not token_str:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION, 
            reason="Token not found"
        )

    # Validate and decode the token using the shared function
    try:
        token_decoded = await get_user_from_token(
            token=token_str, jwt_service=jwt_service
        )
    except HTTPException as e:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION, 
            reason=e.detail
        )

    # Check if the user exists in the database
    db_user = await user_service.get_user_by_email(token_decoded.email)
    if not db_user:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION, 
            reason="User not found"
        )

    # Return user info
    return {"email": db_user['email'], "name": db_user['name']}
