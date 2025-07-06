from pydantic import BaseModel, ConfigDict
from typing import Optional


class UpdateAttendantLot(BaseModel):
    alloted_lot: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
