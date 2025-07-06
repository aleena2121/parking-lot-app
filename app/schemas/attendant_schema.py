from typing import Optional

from pydantic import BaseModel, ConfigDict


class UpdateAttendantLot(BaseModel):
    alloted_lot: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
