import jwt
import base64
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status, Depends
from ..configs.app_config import Settings



from icecream import ic
ic.configureOutput(includeContext=True)

class JwtService:
    def __init__(self, secret: str, algorithm: str) -> None:
        self.secret = secret
        self.algorithm = algorithm


    def encode_jwt(self, payload: dict, exp_in_hrs: int = 1) -> str:
        
        payload.update({"exp": datetime.now(timezone.utc) + timedelta(hours=exp_in_hrs)})

        token = jwt.encode(payload=payload, algorithm=self.algorithm, key=self.secret)
        return token
    
    def decode_jwt(self, token: str) -> dict: 
        try:
            decoded = jwt.decode(jwt = token, key = self.secret, algorithms=[self.algorithm])
            ic(decoded)
            return decoded
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="'Token has expired'")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def get_jwt_service(settings: Settings = Depends(Settings)) -> JwtService:
    # encoded_secret = "5zwMNKZym9hl1vS4LwJvQ5NCbVFxKT1shFBXjEXXoHM="
    
    #NOTE - DO NOT REMOVE THE '=' SYMBOL BELOW
    encoded_secret = settings.JWT_SECRET + "="
    print(f"{encoded_secret=}")
    secret_base64_decoded = base64.urlsafe_b64decode(encoded_secret.encode('utf-8'))
    algorithm = settings.JWT_ALGORITHM
    jwt_service = JwtService(secret=secret_base64_decoded, algorithm=algorithm)
    return jwt_service

