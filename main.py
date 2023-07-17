from fastapi import FastAPI, Depends
import models
from database import engine

from routers.company import companies, dependencies

from starlette.staticfiles import StaticFiles

from routers.auth import auth, auth_fe, admin, address, users
from routers.todos import todos, todos_fe

# from routers.auth import get_current_user

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

# add router of the application

app.include_router(address.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(auth_fe.router)
app.include_router(todos.router)
app.include_router(todos_fe.router)
app.include_router(
    companies.router,
    prefix="/companies",
    tags=["companies"],
    dependencies=[Depends(dependencies.get_token_header)],
    responses={418: {"description": "Internal use only"}},
)

# uvicorn main:app --reload

# This file is sppinning the other two (todos + auth)
