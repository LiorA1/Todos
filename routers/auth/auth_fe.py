import sys
import logging

from fastapi import Depends, status, APIRouter, Request, Response, Form
from typing import Optional
import models
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta
from jose import jwt, JWTError

from .auth import authenticate_user, create_access_token, get_password_hash

from starlette.responses import RedirectResponse

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

sys.path.append("..")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


SECRET_KEY = "dsfurgbnmc,943u09u4gmrngviuy4"
ALGORITHM = "HS256"


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
models.Base.metadata.create_all(bind=engine)
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/login")
router = APIRouter(prefix="/auth_fe", tags=["auth_fe"], responses={401: {"user": "Not authorized"}})
# prefix - each api endpoint, will start with this prefix
# tags - will organize our api's
# responses - default response in case of a failure


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get("email")  # The name is sent from the FE form, utilizing the 'email' attribute.
        self.password = form.get("password")


# session
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/", response_class=HTMLResponse)
async def login_page_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/", response_class=HTMLResponse)
async def login_page_post(request: Request, db: Session = Depends(get_db)):
    response = Response()
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse(url="/todos_fe/", status_code=status.HTTP_302_FOUND)

        user = authenticate_user(form.username, form.password, db=db)
        if not user:
            msg = "Incorrect Username or password"
            return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
        token_expires = timedelta(minutes=60)
        token = create_access_token(user.username, user.id, user.role, expires_delta=token_expires)

        # Saves JWT token in a cookie.
        response.set_cookie(key="access_token", value=token, httponly=True)
        return response

        # Instead of changing this method \/, we will implement the FE logic here ^.
        # validate_user_cookie = await get_login_token(response=response, form_data=form,db=db)

    except Exception as ex:
        msg = "Unknown Error"
        print(ex)
        return templates.TemplateResponse("login.html", {"request": request, "msg": msg})


async def get_current_user_from_cookie(request: Request):
    """
    Gets the Token (JWT) from client cookie,
    verify it against the secret key & jwt algo,
    decode it, and return 'username' and user_id as 'id'.
    """
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")

        if username is None or user_id is None:
            logger.debug("auth_fe: Username or id is not present in payload.")
            return None
        return {"username": username, "user_id": user_id, "user_role": user_role}
    except JWTError as ex:
        logger.debug("auth_fe: Could not validate user creds")

        return None


@router.get("/register", response_class=HTMLResponse)
async def register_page_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", response_class=HTMLResponse)
async def register_page_post(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    firstname: str = Form(...),
    lastname: str = Form(...),
    password: str = Form(...),
    password2: str = Form(...),
    db: Session = Depends(get_db),
):
    validation1 = db.query(models.Users).filter(models.Users.username == username).first()
    validation2 = db.query(models.Users).filter(models.Users.email == email).first()

    if password != password2 or validation1 is not None or validation2 is not None:
        # passwords are not matching
        # found an entry which uses the 'username' or 'email'.
        msg = "Invalid registeration request"
        if validation1:
            msg += " - username is in use"
        if validation2:
            msg += " - email is in use"
        return templates.TemplateResponse("register.html", {"request": request, "msg": msg})

    # passwords are matching & 'username', 'email' are not used yet.

    user_model = models.Users()
    user_model.username = username
    user_model.email = email
    user_model.first_name = firstname
    user_model.last_name = lastname
    user_model.hashed_password = get_password_hash(password)
    user_model.is_active = True

    db.add(user_model)
    db.commit()

    msg = "User successfully created"
    return templates.TemplateResponse("register.html", {"request": request, "msg": msg})


@router.get("/logout", response_class=HTMLResponse)
async def logout_page(request: Request):
    msg = "Logout Successful"
    response = templates.TemplateResponse("login.html", {"request": request, "msg": msg})
    response.delete_cookie(key="access_token")
    # So, in the next attempt to get the cookie, it will not found.
    return response
