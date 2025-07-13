from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.oauth2 import get_current_user
from app.config.logger_config import func_logger
from app.db.session import get_db
from app.enums.role_enum import RoleEnum
from app.exceptions import auth_exceptions, db_exceptions
from app.models.ticket_model import Ticket
from app.models.vehicle_model import Vehicle
from app.queries.parking_lot_queries import get_lot_by_id
from app.queries.vehicle_queries import (get_active_vehicles_in_lot,
                                         get_all_vehicles, get_vehicle_by_id,
                                         get_vehicle_by_plate_no)
from app.schemas.response_schema import StandardResponse
from app.schemas.vehicle_schema import SearchVehicle, ShowVehicle, VehicleBase
from app.utils.role_checker import require_attendant

vehicle_router = APIRouter(prefix="/vehicle", tags=["Vehicles"])


@vehicle_router.get("/", response_model=StandardResponse[List[ShowVehicle]])
def get_all(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    vehicles = get_all_vehicles(db)

    return StandardResponse(
        message=f"{len(vehicles)} vehicles found",
        payload=vehicles,
        status_code=status.HTTP_200_OK,
    )


@vehicle_router.get(
    "/search/{lot_id}", response_model=StandardResponse[List[ShowVehicle]]
)
def find_active_vehicle(
    lot_id: str,
    color: Optional[str] = None,
    make: Optional[str] = None,
    model: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    lot = get_lot_by_id(lot_id=lot_id, db=db)

    query = get_active_vehicles_in_lot(db=db, lot_id=lot_id)

    if color:
        query = query.filter(Vehicle.color.ilike(f"%{color}%"))
    if make:
        query = query.filter(Vehicle.make.ilike(f"%{make}%"))
    if model:
        query = query.filter(Vehicle.model.ilike(f"%{model}%"))

    vehicles = query.all()

    return StandardResponse(
        message=f"{len(vehicles)} vehicles found",
        payload=vehicles,
        status_code=status.HTTP_200_OK,
    )


@vehicle_router.get(
    "/recently-parked/{lot_id}", response_model=StandardResponse[List[ShowVehicle]]
)
def get_recently_parked_vehicles(
    lot_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    thirty_mins_ago = datetime.now() - timedelta(minutes=30)

    recent_vehicles = (
        db.query(Vehicle)
        .join(Ticket, Ticket.vehicle_id == Vehicle.vehicle_id)
        .filter(
            Ticket.parking_lot_id == lot_id,
            Ticket.entry_time >= thirty_mins_ago,
            Ticket.is_active == True,
        )
        .all()
    )

    return StandardResponse(
        message=f"{len(recent_vehicles)} vehicles found in the last 30 minutes",
        payload=recent_vehicles,
        status_code=status.HTTP_200_OK,
    )


@vehicle_router.get("/{vehicle_id}", response_model=StandardResponse[ShowVehicle])
def get_by_id(
    vehicle_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    vehicle = get_vehicle_by_id(db, vehicle_id)

    if not vehicle:
        return StandardResponse(
            message=f"No vehicle found with ID: {vehicle_id}",
            payload=None,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return StandardResponse(
        message=f"Vehicle with ID: {vehicle_id} found",
        payload=vehicle,
        status_code=status.HTTP_200_OK,
    )
