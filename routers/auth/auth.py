import sys
import logging
from fastapi import Depends, HTTPException, status, APIRouter
from typing import Optional
import models
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import engine, SessionLocal
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError
from .validators import CreateUser, Token

sys.path.append("..")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# to get a secret string like this run: "openssl rand -hex 32"
SECRET_KEY = "dsfurgbnmc,943u09u4gmrngviuy4"
ALGORITHM = "HS256"


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
models.Base.metadata.create_all(bind=engine)
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/login")
router = APIRouter(prefix="/auth", tags=["auth"], responses={401: {"user": "Not authorized"}})
# prefix - each api endpoint, will start with this prefix
# tags - will organize our api's
# responses - default response in case of a failure


# session
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_password_hash(password: str):
    return bcrypt_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str, db):
    """
    Getting 'username', 'password' and a session to the db.
    Search for the user with the same username &
    will verify its hash is the same as the given password hash.

    Args:
        username (str): _description_
        password (str): _description_
        db (_type_): _description_

    Returns:
        _type_: _description_
    """
    user: models.Users = db.query(models.Users).filter(models.Users.username == username).first()
    # logger.debug(f"authenticate_user:: user is: {user}")

    if not user or not verify_password(password, user.hashed_password):
        return False

    return user


def create_access_token(username: str, user_id: int, role: str, expires_delta: Optional[timedelta] = None):
    """
    Receive 'username', 'user_id' & will return jwt token, which its payload contains it.
    Secured with the 'SECRET_KEY'

    Args:
        username (str): _description_
        user_id (int): _description_
        expires_delta (Optional[timedelta], optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """

    jwt_data = {"sub": username, "id": user_id, "role": role}

    # add TTL value
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # default TTL - 50 min
        expire = datetime.utcnow() + timedelta(minutes=50)

    jwt_data.update({"exp": expire})

    return jwt.encode(jwt_data, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_bearer)):
    """
    Gets the Token (JWT) from client header, 
    verify it against the secret key & jwt algo,
    decode it, and return 'username' and user_id as 'id'.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"The Payload is: {payload}")
        # TODO: Check payload values
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")

        if username is None or user_id is None:
            logger.debug("auth: Username or id is not present in payload.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="auth: Could not validate user creds",
            )
        return {"username": username, "user_id": user_id, "user_role": user_role}
    except JWTError:
        logger.debug("auth: Could not validate user creds")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="auth: Could not validate user creds",
        )


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_new_user(create_user: CreateUser, db: Session = Depends(get_db)):
    created_user = models.Users()
    created_user.email = create_user.email
    created_user.first_name = create_user.first_name
    created_user.last_name = create_user.last_name
    created_user.username = create_user.username
    created_user.hashed_password = get_password_hash(create_user.password)
    created_user.role = create_user.role
    created_user.is_active = True
    created_user.phone_number = create_user.phone_number

    db.add(created_user)
    # db.commit()

    try:
        db.commit()
    except IntegrityError as ex:
        logger.debug(f"expetion: {ex}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex.orig))

    return create_user


@router.post("/login", response_model=Token)
async def get_login_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # This Path, will receive login data, authenticate it & will return a jwt token.
    # logger.debug(f"get_login_token:: form_data is: {form_data}")
    user = authenticate_user(form_data.username, form_data.password, db)
    # logger.debug(f"get_login_token:: user is: {user}")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="auth: Could not validate user creds",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_expires = timedelta(minutes=20)
    token = create_access_token(user.username, user.id, user.role, token_expires)
    # After authenticate the user, we send the client a JWT that now they can
    # attach to subsequent api calls for authorization.
    logger.debug(f"get_login_token: token: {token}")
    return {"access_token": token, "token_type": "bearer"}
