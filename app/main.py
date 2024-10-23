from fastapi import FastAPI
from .routers.users import user_router
from .routers.messages import message_router
from .routers.groups import group_router
from dotenv import load_dotenv
from contextlib import asynccontextmanager


@asynccontextmanager
async def life_span_handler(app: FastAPI):
    print("about to load env in startup")
    load_dotenv(".env")
    yield




app = FastAPI(lifespan=life_span_handler)

# app.state.lifespan = life_span_handler

app.include_router(user_router, prefix="/users")
app.include_router(message_router, prefix="/messages")
app.include_router(group_router, prefix="/groups")


# @app.on_event("startup")
# async def startup_event():
#     load_dotenv(".env")
