from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class TransactionBase(BaseModel):
    ticket_id: str
    amount: float
    payment_status: Literal["SUCCESS", "FAILED", "PENDING"]

    model_config = ConfigDict(from_attributes=True)


class ShowTransaction(TransactionBase):
    transaction_id: str
    payment_timestamp: Optional[datetime]
