from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth.oauth2 import get_current_user
from app.config.logger_config import func_logger
from app.db.session import get_db
from app.exceptions import auth_exceptions, db_exceptions, user_exceptions
from app.models import user_model
from app.queries.user_queries import get_all_users, get_user_by_email, get_user_by_id
from app.schemas.response_schema import StandardResponse
from app.schemas.user_schema import CreateUser, ShowUser, UpdateUser
from app.utils.hash_password import Hash
from app.enums.role_enum import RoleEnum 

user_router = APIRouter(prefix="/user", tags=["Users"])


@user_router.post("/", response_model=StandardResponse[ShowUser])
def create_user(
    request: CreateUser,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        if current_user.role != RoleEnum.ADMIN:
            func_logger.warning(f"Unauthorized access attempt by user {current_user.user_id}")
            raise auth_exceptions.UnauthorizedAccess()

        existing_email = get_user_by_email(db, request.email)
        if existing_email:
            func_logger.warning(f"Duplicate email attempt: {request.email}")
            raise user_exceptions.UserAlreadyExists(request.email)

        user_data = request.model_dump()
        user_data["password"] = Hash.get_hash_password(request.password)

        new_user = user_model.User(**user_data)
        db.add(new_user)
        db.flush()
        db.commit()
        func_logger.info(f"New User created, id {new_user.user_id}")
        db.refresh(new_user)

        return StandardResponse(
            message="User created Successfully",
            payload=new_user,
            status_code=status.HTTP_201_CREATED,
        )

    except SQLAlchemyError as e:
        db.rollback()
        func_logger.error(f"{e}")
        raise db_exceptions.DatabaseIntegrityError()


@user_router.get("/{user_id}", response_model=StandardResponse[ShowUser])
def get_by_id(
    user_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    user = get_user_by_id(db, user_id)
    if not user:
        func_logger.warning(f"User not found - ID: {user_id}")
        raise user_exceptions.UserNotFound(user_id)

    func_logger.info(f"Successfully retrieved user - ID: {user_id}")
    return StandardResponse(
        message="User fetched successfully",
        payload=user,
        status_code=status.HTTP_200_OK,
    )


@user_router.get("/", response_model=StandardResponse[List[ShowUser]])
def get_all(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    users = get_all_users(db)
    func_logger.info(f"Retrieved {len(users)} users")
    return StandardResponse(
        message="Users fetched Successfully",
        payload=users,
        status_code=status.HTTP_200_OK,
    )


@user_router.put("/{user_id}", response_model=StandardResponse[ShowUser])
def update_user(
    user_id: str,
    request: UpdateUser,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        if current_user.role != RoleEnum.ADMIN:
            func_logger.warning(f"Unauthorized update attempt by user {current_user.user_id}")
            raise auth_exceptions.UnauthorizedAccess()

        user = get_user_by_id(db, user_id)
        if not user:
            func_logger.warning(f"User not found for update - ID: {user_id}")
            raise user_exceptions.UserNotFound(user_id)

        updated_data = request.model_dump(exclude_unset=True)

        if "email" in updated_data:
            existing_user = get_user_by_email(db, updated_data["email"])
            if existing_user and existing_user.user_id != user.user_id:
                func_logger.warning(f"Email conflict: {updated_data['email']}")
                raise user_exceptions.UserAlreadyExists(updated_data["email"])

        if "password" in updated_data:
            updated_data["password"] = Hash.get_hash_password(updated_data["password"])

        for key, value in updated_data.items():
            setattr(user, key, value)
            
        db.commit()
        db.refresh(user)

        func_logger.info(f"User updated successfully - ID: {user_id}")

        return StandardResponse(
            message="User updated Successfully",
            payload=user,
            status_code=status.HTTP_200_OK,
        )

    except SQLAlchemyError as e:
        db.rollback()
        func_logger.error(f"{e}")
        raise db_exceptions.DatabaseIntegrityError()


@user_router.delete("/{user_id}", response_model=StandardResponse[None])
def delete_user(
    user_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    try:
        if current_user.role != RoleEnum.ADMIN:
            func_logger.warning(f"Unauthorized delete attempt by user {current_user.user_id}")
            raise auth_exceptions.UnauthorizedAccess()

        user = get_user_by_id(db, user_id)
        if not user:
            func_logger.warning(f"User not found for deletion - ID: {user_id}")
            raise user_exceptions.UserNotFound(user_id)

        db.delete(user)
        db.commit()

        func_logger.info(f"User deleted successfully - ID: {user_id}")

        return StandardResponse(
            message="User deleted successfully",
            payload=None,
            status_code=status.HTTP_200_OK,
        )
    except SQLAlchemyError as e:
        db.rollback()
        func_logger.error(f"Failed to delete user {user_id}: {e}")
        raise db_exceptions.DatabaseIntegrityError()