from fastapi import APIRouter, Depends, HTTPException, status, Path
import models
from database import engine, SessionLocal

from sqlalchemy.orm import Session

from .auth import get_current_user

router = APIRouter(
    prefix="/admin", tags=["Admin"], responses={404: {"description": "Not Found"}}
)

models.Base.metadata.create_all(bind=engine)


# session
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all_by_user(
    user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Read all Todos of current user, IFF its role is 'Admin'."""
    print(user)
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )
    return (
        db.query(models.Todos)
        .filter(models.Todos.owner_id == user.get("user_id"))
        .all()
    )


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int = Path(ge=0),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """can delete other users todos, because current user is admin"""
    print(f"admin::delete_todo::user: {user}")

    if user is None or user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    deleted_todo_count = (
        db.query(models.Todos)
        .filter(models.Todos.id == todo_id)
        .delete()
    )

    if deleted_todo_count is None or deleted_todo_count == 0:
        raise HTTPException(status_code=404, detail="Not Found")

    # db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()

    return {"status_code": 200, "transaction": "Successful"}
