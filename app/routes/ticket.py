from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.config.logger_config import func_logger
from app.db.session import get_db
from app.enums.role_enum import RoleEnum
from app.exceptions import (auth_exceptions, db_exceptions,
                            ticket_vehicle_exceptions)
from app.models.ticket_model import Ticket
from app.queries.parking_lot_queries import (get_lot_by_id, get_slot_by_id,
                                             get_slot_name)
from app.queries.ticket_queries import (get_all_tickets, get_ticket_by_id,
                                        get_ticket_by_lot_id,
                                        get_ticket_by_lot_id_and_slot_name)
from app.queries.user_queries import get_attendant
from app.schemas.response_schema import StandardResponse
from app.schemas.ticket_schema import ShowTicket, TicketBase
from app.schemas.transaction_schema import ShowTransaction
from app.schemas.vehicle_schema import VehicleBase
from app.services.ticket_services import add_or_update_vehicle, get_slot
from app.services.transaction_service import create_transaction
from app.utils.role_checker import require_role

ticket_router = APIRouter(prefix="/ticket", tags=["Ticket"])


@ticket_router.post("/", response_model=StandardResponse[ShowTicket])
def create_ticket(
    request: TicketBase,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(RoleEnum.ATTENDANT)),
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

        attendant = get_attendant(db=db, user_id=current_user.user_id)
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

        parking_lot.available_slots.remove(slot.slot_name)
        flag_modified(parking_lot, "available_slots")

        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)

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
def get_all(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(RoleEnum.ADMIN, RoleEnum.ATTENDANT)),
):
    if current_user.role == RoleEnum.ATTENDANT:
        attendant = get_attendant(db=db, user_id=current_user.user_id)
        tickets = get_all_tickets(db=db, lot_id=attendant.alloted_lot)
    else:
        tickets = get_all_tickets(db, lot_id=None)

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
    current_user=Depends(require_role(RoleEnum.ADMIN, RoleEnum.ATTENDANT)),
):
    if current_user.role == RoleEnum.ATTENDANT:
        attendant = get_attendant(db=db, user_id=current_user.user_id)
        if lot_id != attendant.alloted_lot:
            raise auth_exceptions.UnauthorizedAccess()

    tickets = get_ticket_by_lot_id_and_slot_name(db, lot_id, slot_name)
    if not tickets:
        return StandardResponse(
            message=f"Found no tickets",
            payload=[],
            status_code=status.HTTP_404_NOT_FOUND,
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
    current_user=Depends(
        require_role(RoleEnum.ADMIN, RoleEnum.ATTENDANT, RoleEnum.POLICE)
    ),
):
    if current_user.role == RoleEnum.ATTENDANT:
        attendant = get_attendant(db=db, user_id=current_user.user_id)
        ticket = get_ticket_by_id(
            db=db, ticket_id=ticket_id, lot_id=attendant.alloted_lot
        )
    else:
        ticket = get_ticket_by_id(db=db, ticket_id=ticket_id, lot_id=None)

    if not ticket:
        raise ticket_vehicle_exceptions.NoTicketFound()

    return StandardResponse(
        message=f"Found tickets",
        payload=ticket,
        status_code=status.HTTP_200_OK,
    )


@ticket_router.get("/lot/{lot_id}", response_model=StandardResponse[List[ShowTicket]])
def get_by_lot_id(
    lot_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(RoleEnum.ADMIN, RoleEnum.ATTENDANT, RoleEnum.POLICE)
    ),
):
    if current_user.role == RoleEnum.ATTENDANT:
        attendant = get_attendant(db=db, user_id=current_user.user_id)
        if lot_id != attendant.alloted_lot:
            raise auth_exceptions.UnauthorizedAccess()

    tickets = get_ticket_by_lot_id(db, lot_id)

    return StandardResponse(
        message=f"Found {len(tickets)} tickets",
        payload=tickets,
        status_code=status.HTTP_200_OK,
    )


@ticket_router.put(
    "/exit/{ticket_id}", response_model=StandardResponse[ShowTransaction]
)
def exit_vehicle(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(RoleEnum.ATTENDANT)),
):
    try:
        attendant = get_attendant(db=db, user_id=current_user.user_id)
        ticket = get_ticket_by_id(
            ticket_id=ticket_id, db=db, lot_id=attendant.alloted_lot
        )
        if not ticket:
            raise auth_exceptions.UnauthorizedAccess()

        if not ticket.is_active:
            raise ticket_vehicle_exceptions.VehicleAlreadyExited()

        ticket.exit_time = datetime.now()
        ticket.is_active = False

        slot = get_slot_by_id(db=db, slot_id=ticket.slot_id)
        slot.is_occupied = False

        parking_lot = get_lot_by_id(db=db, lot_id=ticket.parking_lot_id)
        slot_name = get_slot_name(db=db, slot_id=ticket.slot_id).slot_name
        parking_lot.available_slots.append(slot_name)
        flag_modified(parking_lot, "available_slots")

        transaction = create_transaction(db=db, ticket=ticket)
        db.commit()
        db.refresh(transaction)
        db.refresh(ticket)

        func_logger.info(
            f"Vehicle ID: {ticket.vehicle_id} exited at {ticket.exit_time} by user ID: {attendant.user_id} "
        )
        return StandardResponse(
            message=f"Vehicle exited",
            payload=transaction,
            status_code=status.HTTP_200_OK,
        )

    except SQLAlchemyError as e:
        db.rollback()
        func_logger.error(f"{e}")
        raise db_exceptions.DatabaseIntegrityError(e)
