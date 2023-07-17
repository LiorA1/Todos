from pydantic import BaseModel
from typing import Optional


# Validators for 'users'
class User(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    is_active: bool
    role: str


# Validators for 'auth'
class CreateUser(BaseModel):
    username: str
    email: Optional[str]
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str


class Token(BaseModel):
    access_token: str
    token_type: str


# Validators for 'auth_fe'
class UserPassword(BaseModel):
    username: str
    password: str


# Validators for 'address'
class Address(BaseModel):
    address1: str
    apt_num: Optional[str]
    address2: Optional[str]
    city: str
    state: str
    country: str
    postalcode: str
