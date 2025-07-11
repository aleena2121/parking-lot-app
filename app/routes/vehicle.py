from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.oauth2 import get_current_user
from app.config.logger_config import func_logger
from app.db.session import get_db
from app.enums.role_enum import RoleEnum
from app.exceptions import auth_exceptions, db_exceptions
from app.models.vehicle_model import Vehicle
from app.queries.vehicle_queries import (get_all_vehicles, get_vehicle_by_id,
                                         get_vehicle_by_plate_no)
from app.schemas.response_schema import StandardResponse
from app.schemas.vehicle_schema import ShowVehicle, VehicleBase
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
