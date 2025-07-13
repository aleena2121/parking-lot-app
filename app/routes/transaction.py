from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth.oauth2 import get_current_user
from app.config.logger_config import func_logger
from app.db.session import get_db
from app.exceptions import db_exceptions
from app.queries.transaction_queries import (get_all_transactions,
                                             get_transaction_by_id,
                                             get_transaction_by_ticket,
                                             get_transaction_by_ticket_id)
from app.schemas.response_schema import StandardResponse
from app.schemas.transaction_schema import ShowTransaction
from app.utils.role_checker import require_attendant

transaction_router = APIRouter(prefix="/transactions", tags=["Transactions"])


@transaction_router.put(
    "/{ticket_id}", response_model=StandardResponse[ShowTransaction]
)
def make_payment(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_attendant),
):
    try:
        transaction = get_transaction_by_ticket(db=db, ticket_id=ticket_id)

        transaction.payment_status = "SUCCESS"
        transaction.payment_timestamp = datetime.now()

        db.commit()
        db.refresh(transaction)

        return StandardResponse(
            message="Payment Successful",
            payload=transaction,
            status_code=status.HTTP_200_OK,
        )
    except SQLAlchemyError as e:
        db.rollback()
        func_logger.error(f"{e}")
        raise db_exceptions.DatabaseIntegrityError(e)


@transaction_router.get("/", response_model=StandardResponse[List[ShowTransaction]])
def get_all(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        transactions = get_all_transactions(db=db)

        return StandardResponse(
            message=f"Found {len(transactions)} transactions",
            payload=transactions,
            status_code=status.HTTP_200_OK,
        )
    except SQLAlchemyError as e:
        db.rollback()
        func_logger.error(f"{e}")
        raise db_exceptions.DatabaseIntegrityError(e)


@transaction_router.get(
    "/{transaction_id}", response_model=StandardResponse[ShowTransaction]
)
def get_by_id(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        transaction = get_transaction_by_id(transaction_id=transaction_id, db=db)

        return StandardResponse(
            message=f"Found transaction",
            payload=transaction,
            status_code=status.HTTP_200_OK,
        )

    except SQLAlchemyError as e:
        db.rollback()
        func_logger.error(f"{e}")
        raise db_exceptions.DatabaseIntegrityError(e)


@transaction_router.get(
    "/ticket/{ticket_id}", response_model=StandardResponse[ShowTransaction]
)
def get_by_ticket_id(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        transaction = get_transaction_by_ticket_id(ticket_id=ticket_id, db=db)

        return StandardResponse(
            message=f"Found transaction",
            payload=transaction,
            status_code=status.HTTP_200_OK,
        )

    except SQLAlchemyError as e:
        db.rollback()
        func_logger.error(f"{e}")
        raise db_exceptions.DatabaseIntegrityError(e)
