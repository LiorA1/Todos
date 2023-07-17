from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
import models
from database import engine, SessionLocal

# from project3.database import SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ..auth.auth import get_current_user

router = APIRouter(prefix="/todos", tags=["todos"], responses={404: {"description": "Not Found"}})

models.Base.metadata.create_all(bind=engine)

# templates = Jinja2Templates(directory="templates")


# session
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Todo(BaseModel):
    title: str
    description: Optional[str]
    priority: int = Field(gt=0, le=5, description="1-5")
    complete: bool


class UpdateTodo(BaseModel):
    title: Optional[str]
    description: Optional[str]
    priority: Optional[int] = Field(gt=0, le=5, description="1-5")
    complete: Optional[bool]


@router.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Todos).all()


@router.get("/user")
async def read_all_by_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all todos of the user

    Args:
        user (dict, optional): _description_. Defaults to Depends(get_current_user).
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    return db.query(models.Todos).filter(models.Todos.owner_id == user.get("user_id")).all()


@router.get("/{todo_id}")
async def get_todo(todo_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get the todo of the User.

    Args:
        todo_id (int): _description_
        user (dict, optional): _description_. Defaults to Depends(get_current_user).
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Raises:
        HTTPException: _description_
        not_found_exception: _description_

    Returns:
        _type_: _description_
    """
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    # search for the item
    todo_model = (
        db.query(models.Todos)
        .filter(models.Todos.id == todo_id)
        .filter(models.Todos.owner_id == user.get("user_id"))
        .first()
    )
    if todo_model is not None:
        return todo_model
    raise not_found_exception()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(todo: Todo, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    # Dont understand how the `get_current_user` works ?
    # it is getting the token from the postman, and than what?

    print(f"user: {user}")

    # update all the fields blindly
    todo_model = models.Todos()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete
    todo_model.owner_id = user.get("user_id")  # 'id' is 'user_id'

    db.add(todo_model)
    db.commit()

    return todo

    # return {"status_code": 201, "transaction": "Successful"}


@router.put("/{todo_id}")
async def update_todo(
    todo_id: int,
    todo: UpdateTodo,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # One will need to supply the user data in the jwt token.
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    print(f"update_todo::user: {user}")

    todo_model = (
        db.query(models.Todos)
        .filter(models.Todos.id == todo_id)
        .filter(models.Todos.owner_id == user.get("user_id"))
        .first()
    )

    if todo_model is None:
        raise not_found_exception()

    if todo.title:
        todo_model.title = todo.title
    if todo.description:
        todo_model.description = todo.description
    if todo.priority:
        todo_model.priority = todo.priority
    if todo.complete:
        todo_model.complete = todo.complete

    db.add(todo_model)
    db.commit()

    return {"status_code": 200, "transaction": "Successful"}


def not_found_exception():
    return HTTPException(status_code=404, detail="Not Found")


@router.delete("/{todo_id}")
async def delete_todo(todo_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    print(f"delete_todo::user: {user}")

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    deleted_todo_count = (
        db.query(models.Todos)
        .filter(models.Todos.id == todo_id)
        .filter(models.Todos.owner_id == user.get("user_id"))
        .delete()
    )

    if deleted_todo_count is None or deleted_todo_count == 0:
        raise not_found_exception()

    # db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()

    return {"status_code": 200, "transaction": "Successful"}
