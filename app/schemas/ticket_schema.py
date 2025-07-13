from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.enums.driver_enum import DriverEnum
from app.enums.vehicle_enum import VehicleEnum


class TicketBase(BaseModel):
    plate_number: str
    make: str
    model: str
    color: str
    vehicle_category: VehicleEnum
    driver_category: DriverEnum
    driver_phone_no: str

    model_config = ConfigDict(from_attributes=True)


class ShowSlot(BaseModel):
    slot_name: str

    model_config = ConfigDict(from_attributes=True)


class ShowTicket(BaseModel):
    ticket_id: str
    parking_lot_id: str
    slot: ShowSlot
    slot_id: str
    attendant_id: str
    entry_time: datetime
    exit_time: Optional[datetime] = None
