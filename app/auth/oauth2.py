from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.auth.token import AccessToken
from app.config.load_config import api_settings
from app.config.logger_config import func_logger
from app.db.session import get_db
from app.exceptions import auth_exceptions, user_exceptions
from app.models.user_model import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    try:
        token_obj = AccessToken(secret_key=api_settings.SECRET_KEY)
        token_data = token_obj.verify_access_token(
            token, auth_exceptions.CredentialsException
        )
        user_id = token_data.user_id

        if not user_id:
            raise auth_exceptions.CredentialsException()

        user = db.query(User).filter(User.user_id == user_id).first()

        return user

    except JWTError as e:
        func_logger.error(f"JWT Error in get_current_user: {e}")
        raise auth_exceptions.CredentialsException()
