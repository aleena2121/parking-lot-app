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
    slot_id: str
    attendant_id: str
    driver_phone_no: str
    entry_time: datetime
    exit_time: Optional[datetime] = None
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class ShowTicket(BaseModel):
    ticket_id: str
    vehicle_category: VehicleEnum
    slot_name: str
    attendant_id: int
    entry_time: Optional[datetime] = None
    exit_time: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)