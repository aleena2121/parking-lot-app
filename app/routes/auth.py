from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth.token import AccessToken
from app.config.load_config import api_settings
from app.db.session import get_db
from app.exceptions import auth_exceptions, db_exceptions
from app.models.user_model import User
from app.utils.hash_password import Hash

login_router = APIRouter(prefix="/auth", tags=["Auth"])


@login_router.post("/login")
def login(
    request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    email = request.username
    password = request.password

    try:
        user = db.query(User).filter(User.email == email).first()

        if not user or not user.password:
            raise auth_exceptions.InvalidCredentialsException()

        if not Hash.verify_password(password, user.password):
            raise auth_exceptions.InvalidCredentialsException()

        try:
            token_obj = AccessToken(
                time_expire=api_settings.ACCESS_TOKEN_EXPIRE_MINUTES,
                secret_key=api_settings.SECRET_KEY,
            )
            access_token = token_obj.create_access_token(
                data={"sub": str(user.user_id)}
            )

            return {"access_token": access_token, "token_type": "bearer"}

        except Exception as e:
            raise auth_exceptions.TokenCreationError(e)
    except SQLAlchemyError as e:
        raise db_exceptions.DatabaseIntegrityError(e)
