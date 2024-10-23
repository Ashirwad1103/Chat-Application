from enum import StrEnum


class EnvVariables(StrEnum):
    JWT_SECRET = "JWT_SECRET" 
    JWT_ALGORITHM = "JWT_ALGORITHM"
    MONGO_HOST = "MONGO_HOST" 
    MONGO_DB_NAME = "MONGO_DB_NAME"
