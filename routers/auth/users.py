
from fastapi import APIRouter, Depends, HTTPException, status
import models
from database import engine, SessionLocal

# from project3.database import SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, parse_obj_as

from .auth import get_current_user, get_password_hash
from .validators import User, UserPassword

router = APIRouter(
    prefix="/users", tags=["Users"], responses={404: {"description": "Not Found"}}
)

models.Base.metadata.create_all(bind=engine)


# session
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/user", response_model=User)
async def read_current_user(
    user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )
    current_user = (
        db.query(models.Users).filter(models.Users.id == user.get("user_id")).first()
    )
    return parse_obj_as(User, current_user.__dict__)


@router.put("/password", response_model=UserPassword)
async def change_current_user_password(
    user_password: UserPassword,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # check that the input username is the same (maybe 'id' is better?)
    if user is None or user_password.username != user.get("username"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    # reteive the user from the current JWT.
    current_user = (
        db.query(models.Users).filter(models.Users.id == user.get("user_id")).first()
    )

    # TODO: verify current password (using 'bcrypt_context.verify)

    if current_user is None:
        raise HTTPException(status_code=404, detail="Not Found")

    # change the password
    current_user.hashed_password = get_password_hash(user_password.password)

    # change db record
    db.add(current_user)
    db.commit()

    return parse_obj_as(UserPassword, user_password)
