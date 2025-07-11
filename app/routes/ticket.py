from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.auth.oauth2 import get_current_user
from app.config.logger_config import func_logger
from app.db.session import get_db
from app.exceptions import db_exceptions
from app.models.attendant_model import Attendant
from app.models.ticket_model import Ticket
from app.queries.ticket_queries import (get_all_tickets, get_ticket_by_id,
                                        get_ticket_by_lot_id,
                                        get_ticket_by_lot_id_and_slot_name)
from app.schemas.response_schema import StandardResponse
from app.schemas.ticket_schema import ShowTicket, TicketBase
from app.schemas.vehicle_schema import VehicleBase
from app.services.ticket_services import add_or_update_vehicle, get_slot
from app.utils.role_checker import require_attendant

ticket_router = APIRouter(prefix="/ticket", tags=["Ticket"])


@ticket_router.post("/", response_model=StandardResponse[ShowTicket])
def create_ticket(
    request: TicketBase,
    db: Session = Depends(get_db),
    current_user=Depends(require_attendant),
):
    try:
        vehicle_details = VehicleBase(
            plate_number=request.plate_number,
            make=request.make,
            model=request.model,
            color=request.color,
            vehicle_category=request.vehicle_category,
            driver_category=request.driver_category,
            driver_phone_no=request.driver_phone_no,
        )

        vehicle = add_or_update_vehicle(vehicle_details, db)
        vehicle_id = vehicle.payload.vehicle_id

        attendant = (
            db.query(Attendant)
            .filter(Attendant.user_id == current_user.user_id)
            .first()
        )
        parking_lot_id = attendant.alloted_lot

        slot = get_slot(request, db, parking_lot_id)

        new_ticket = Ticket(
            vehicle_id=vehicle_id,
            parking_lot_id=parking_lot_id,
            slot_id=slot.slot_id,
            attendant_id=attendant.user_id,
            entry_time=datetime.now(),
        )
        slot.is_occupied = True
        parking_lot = slot.parking_lot

        if parking_lot and slot.slot_name in parking_lot.available_slots:
            parking_lot.available_slots.remove(slot.slot_name)
            flag_modified(parking_lot, "available_slots")

        db.add(new_ticket)
        db.commit()
        func_logger.info(
            f"New ticket generated, ID: {new_ticket.ticket_id} for vehicle ID: {vehicle_id}"
        )
        return StandardResponse(
            message="Ticket generated",
            payload=new_ticket,
            status_code=status.HTTP_201_CREATED,
        )

    except SQLAlchemyError as e:
        db.rollback()
        func_logger.error(f"{e}")
        raise db_exceptions.DatabaseIntegrityError(e)


@ticket_router.get("/", response_model=StandardResponse[List[ShowTicket]])
def get_all(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    tickets = get_all_tickets(db)

    return StandardResponse(
        message=f"Found {len(tickets)} tickets",
        payload=tickets,
        status_code=status.HTTP_200_OK,
    )


@ticket_router.get("/filter", response_model=StandardResponse[List[ShowTicket]])
def get_by_lot_and_slot(
    lot_id: str,
    slot_name: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    tickets = get_ticket_by_lot_id_and_slot_name(db, lot_id, slot_name)
    if not tickets:
        return StandardResponse(
            message=f"Found no tickets",
            payload=None,
            status_code=status.HTTP_200_OK,
        )
    return StandardResponse(
        message=f"Found {len(tickets)} tickets",
        payload=tickets,
        status_code=status.HTTP_200_OK,
    )


@ticket_router.get("/{ticket_id}", response_model=StandardResponse[ShowTicket])
def get_by_ticket_id(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ticket = get_ticket_by_id(db, ticket_id)

    return StandardResponse(
        message=f"Found tickets", payload=ticket, status_code=status.HTTP_200_OK
    )


@ticket_router.get("/lot/{lot_id}", response_model=StandardResponse[List[ShowTicket]])
def get_by_lot_id(
    lot_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    tickets = get_ticket_by_lot_id(db, lot_id)

    return StandardResponse(
        message=f"Found {len(tickets)} tickets",
        payload=tickets,
        status_code=status.HTTP_200_OK,
    )
