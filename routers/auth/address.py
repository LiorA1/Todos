import sys

from fastapi import Depends, APIRouter


import models
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError
from .auth import get_current_user
from ..todos.todos import not_found_exception
from .validators import Address

sys.path.append("..")

router = APIRouter(prefix="/address", tags=["Address"], responses={404: {"description": "Not Found"}})

# models.Base.metadata.create_all(bind=engine)
# for now, this is not needed, because we already create the 'address' table in theDB.


# session
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.post("/")
async def create_address(address: Address, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise not_found_exception()
    address_model = models.Address()
    address_model.address1 = address.address1
    address_model.address2 = address.address2
    address_model.city = address.city
    address_model.state = address.state
    address_model.country = address.country
    address_model.postalcode = address.postalcode
    if address.apt_num:
        address_model.apt_num = address.apt_num

    db.add(address_model)
    db.flush()

    user_model = db.query(models.Users).filter(models.Users.id == user.get("user_id")).first()
    user_model.address_id = address_model.id

    db.add(user_model)

    db.commit()

    return address
