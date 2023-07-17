from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Path, Form
from starlette.responses import RedirectResponse

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import models
from database import engine, SessionLocal

# from project3.database import SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ..auth.auth_fe import get_current_user

router = APIRouter(prefix="/todos_fe", tags=["todos_fe"], responses={404: {"description": "Not Found"}})

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


# session
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/test")
async def test(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/", response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: Session = Depends(get_db)):
    # verify current user have cookie with jwt token
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth_fe", status_code=status.HTTP_302_FOUND)

    todos = db.query(models.Todos).filter(models.Todos.owner_id == user.get("user_id")).all()

    todos = (
        db.query(models.Todos)
        .filter(models.Todos.owner_id == user.get("user_id"))
        .order_by(models.Todos.id.desc())
        .all()
    )

    return templates.TemplateResponse("home.html", {"request": request, "todos": todos, "user": user})


@router.get("/add-todo", response_class=HTMLResponse)
async def add_todo(request: Request):
    # verify current user have cookie with jwt token
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth_fe", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("add-todo.html", {"request": request, "user": user})


@router.post("/add-todo", response_class=HTMLResponse)
async def create_todo(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    priority: int = Form(...),
    db: Session = Depends(get_db),
):
    # verify current user have cookie with jwt token
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth_fe", status_code=status.HTTP_302_FOUND)

    todo_model = models.Todos()
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    todo_model.complete = False
    todo_model.owner_id = user.get("user_id")

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url="/todos_fe", status_code=status.HTTP_302_FOUND)


@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def update_todo(request: Request, todo_id: int = Path(gt=0), db: Session = Depends(get_db)):
    # verify current user have cookie with jwt token
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth_fe", status_code=status.HTTP_302_FOUND)

    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()

    return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo, "user": user})


@router.post("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def update_todo_commit(
    request: Request,
    todo_id: int = Path(gt=0),
    title: str = Form(...),
    description: str = Form(...),
    priority: int = Form(...),
    db: Session = Depends(get_db),
):
    # verify current user have cookie with jwt token
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth_fe", status_code=status.HTTP_302_FOUND)

    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    # todo_model.complete = False
    # todo_model.owner_id = 1

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url="/todos_fe", status_code=status.HTTP_302_FOUND)


@router.get("/delete/{todo_id}", response_class=HTMLResponse)
async def delete_todo(request: Request, todo_id: int = Path(gt=0), db: Session = Depends(get_db)):
    # verify current user have cookie with jwt token
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth_fe", status_code=status.HTTP_302_FOUND)

    todo = (
        db.query(models.Todos)
        .filter(models.Todos.id == todo_id)
        .filter(models.Todos.owner_id == user.get("user_id"))
        .first()
    )

    if todo is None:
        return RedirectResponse(url="/todos_fe", status_code=status.HTTP_302_FOUND)

    todo_count = (
        db.query(models.Todos)
        .filter(models.Todos.id == todo_id)
        .filter(models.Todos.owner_id == user.get("user_id"))
        .delete()
    )
    db.commit()

    return RedirectResponse(url="/todos_fe", status_code=status.HTTP_302_FOUND)


@router.get("/complete/{todo_id}", response_class=HTMLResponse)
async def complete_todo(request: Request, todo_id: int = Path(gt=0), db: Session = Depends(get_db)):
    # verify current user have cookie with jwt token
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth_fe", status_code=status.HTTP_302_FOUND)

    todo = (
        db.query(models.Todos)
        .filter(models.Todos.id == todo_id)
        .filter(models.Todos.owner_id == user.get("user_id"))
        .first()
    )

    todo.complete = not todo.complete

    if todo is None:
        print(f"user {user.get('user_id')} tried to update non associate item {todo_id}")
        return RedirectResponse(url="/todos_fe", status_code=status.HTTP_302_FOUND)

    db.add(todo)
    db.commit()

    return RedirectResponse(url="/todos_fe", status_code=status.HTTP_302_FOUND)
