from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config.logger_config import func_logger
from app.db.session import get_db
from app.enums.role_enum import RoleEnum
from app.exceptions import db_exceptions, transaction_exceptions
from app.queries.transaction_queries import (get_all_transactions,
                                             get_transaction_by_id,
                                             get_transaction_by_ticket,
                                             get_transaction_by_ticket_id)
from app.queries.user_queries import get_attendant
from app.schemas.response_schema import StandardResponse
from app.schemas.transaction_schema import ShowTransaction
from app.utils.role_checker import require_role

transaction_router = APIRouter(prefix="/transactions", tags=["Transactions"])


@transaction_router.put(
    "/{ticket_id}", response_model=StandardResponse[ShowTransaction]
)
def make_payment(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(RoleEnum.ATTENDANT)),
):
    try:
        transaction = get_transaction_by_ticket(db=db, ticket_id=ticket_id)

        if not transaction:
            func_logger.warning(f"No transaction found for ticket ID: {ticket_id}")
            raise transaction_exceptions.TransactionNotFound()

        transaction.payment_status = "SUCCESS"
        transaction.payment_timestamp = datetime.now()

        db.commit()
        db.refresh(transaction)
        func_logger.info(
            f"Payment successful for transaction ID: {transaction.transaction_id} (ticket ID: {ticket_id})"
        )

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
def get_all(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(RoleEnum.ADMIN, RoleEnum.ATTENDANT)),
):
    try:
        lot_id = None
        if current_user.role == RoleEnum.ATTENDANT:
            attendant = get_attendant(db=db, user_id=current_user.user_id)
            lot_id = attendant.alloted_lot

        transactions = get_all_transactions(db=db, lot_id=lot_id)

        if not transactions:
            func_logger.warning(f"No transactions found.")
            raise transaction_exceptions.TransactionNotFound()

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
    current_user=Depends(require_role(RoleEnum.ADMIN, RoleEnum.ATTENDANT)),
):
    try:
        lot_id = None
        if current_user.role == RoleEnum.ATTENDANT:
            attendant = get_attendant(db=db, user_id=current_user.user_id)
            lot_id = attendant.alloted_lot

        transaction = get_transaction_by_id(
            transaction_id=transaction_id, db=db, lot_id=lot_id
        )

        if not transaction:
            func_logger.warning(f"Transaction ID: {transaction_id} not found.")
            raise transaction_exceptions.TransactionNotFound()

        func_logger.info(f"Transaction ID: {transaction_id} found.")

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
    current_user=Depends(require_role(RoleEnum.ADMIN, RoleEnum.ATTENDANT)),
):
    try:
        lot_id = None
        if current_user.role == RoleEnum.ATTENDANT:
            attendant = get_attendant(db=db, user_id=current_user.user_id)
            lot_id = attendant.alloted_lot

        transaction = get_transaction_by_ticket_id(
            ticket_id=ticket_id, db=db, lot_id=lot_id
        )

        if not transaction:
            func_logger.warning(f"No transaction found for ticket ID: {ticket_id}")
            raise transaction_exceptions.TransactionNotFound()

        func_logger.info(
            f"Transaction found for ticket ID: {ticket_id}, Transaction ID: {transaction.transaction_id}"
        )

        return StandardResponse(
            message=f"Found transaction",
            payload=transaction,
            status_code=status.HTTP_200_OK,
        )

    except SQLAlchemyError as e:
        db.rollback()
        func_logger.error(f"{e}")
        raise db_exceptions.DatabaseIntegrityError(e)
