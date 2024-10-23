from .config_variables import EnvVariables
import os
from ..utils.decorators import singleton



@singleton
class Settings:
    def __init__(self):
        self.JWT_SECRET = os.getenv(EnvVariables.JWT_SECRET)
        self.JWT_ALGORITHM = os.getenv(EnvVariables.JWT_ALGORITHM)
        self.MONGO_HOST = os.getenv(EnvVariables.MONGO_HOST)
        self.MONGO_DB_NAME = os.getenv(EnvVariables.MONGO_DB_NAME)



    # jwt_secret: str
    # jwt_algorithm: str
    # mongo_host: str
    # mongo_db_name: str

    # class Config:
    #     env_file=".env"

    # model_config = SettingsConfigDict(env_file=".env")