import json
import math
import re

from fastapi import status
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.config.logger_config import func_logger
from app.enums.slot_enum import SlotEnum
from app.exceptions.parking_lot_exceptions import NoLotFoundException, SlotsOccupiedException
from app.models.parking_lot_model import ParkingLot
from app.models.row_model import Row
from app.models.slot_model import Slot
from app.schemas.response_schema import StandardResponse
from app.schemas.ticket_schema import TicketBase
from app.schemas.vehicle_schema import Category


def get_row_label(index: int) -> str:
    label = ""
    while index >= 0:
        label = chr(index % 26 + 65) + label
        index = index // 26 - 1
    return label


def assign_slot_categories(slots: list[Slot]):
    total = len(slots)

    first_cutoff = math.ceil(total * 0.1)
    last_cutoff = total - first_cutoff

    for idx, slot in enumerate(slots):
        if idx < first_cutoff:
            slot.slot_category = SlotEnum.HANDICAPPED
        elif idx >= last_cutoff:
            slot.slot_category = SlotEnum.LARGE
        else:
            slot.slot_category = SlotEnum.REGULAR


def get_next_slot_id(db: Session) -> int:
    last_slot = db.execute(
        text(
            "SELECT slot_id FROM slots ORDER BY CAST(SUBSTRING(slot_id FROM 3) AS INTEGER) DESC LIMIT 1"
        )
    ).first()
    return int(last_slot[0].replace("SL", "")) + 1 if last_slot else 1


def create_slots_and_row(capacity: int, db: Session, parking_lot: ParkingLot):
    slot_per_row = 10
    total_slots = capacity
    num_rows = math.ceil(total_slots / slot_per_row)
    created_slots = 0
    slot_counter = get_next_slot_id(db)
    all_slots = []

    for i in range(num_rows):
        row_label = get_row_label(i)
        row = Row(parking_lot_id=parking_lot.parking_lot_id, row_label=row_label)
        db.add(row)

        for j in range(1, slot_per_row + 1):
            if created_slots >= total_slots:
                break

            slot_id = f"SL{slot_counter}"
            slot_name = f"{row_label}{j}"
            slot_counter += 1
            created_slots += 1

            slot = Slot(
                slot_id=slot_id,
                slot_name=slot_name,
                parking_lot_id=parking_lot.parking_lot_id,
                row_label=row_label,
                is_occupied=False,
            )
            all_slots.append(slot)

    assign_slot_categories(all_slots)

    for slot in all_slots:
        db.add(slot)

    parking_lot.capacity = total_slots
    parking_lot.available_slots = [s.slot_name for s in all_slots if not s.is_occupied]
    parking_lot.is_full = False
    func_logger.info(
        f"Created slots and rows for parking lot ID: {parking_lot.parking_lot_id}"
    )


def update_slots_and_capacity(new_capacity: int, db: Session, parking_lot: ParkingLot):
    current_capacity = parking_lot.capacity
    if new_capacity == current_capacity:
        return

    if new_capacity < current_capacity:
        to_remove = current_capacity - new_capacity
        removable_slots = (
            db.query(Slot)
            .filter(Slot.parking_lot_id == parking_lot.parking_lot_id)
            .order_by(Slot.slot_id.desc())
            .limit(to_remove)
            .all()
        )

        if any(slot.is_occupied for slot in removable_slots):
            raise SlotsOccupiedException()

        for slot in removable_slots:
            db.delete(slot)

        db.commit()

        remaining_slots = (
            db.query(Slot)
            .filter(Slot.parking_lot_id == parking_lot.parking_lot_id)
            .order_by(Slot.slot_id.asc())
            .all()
        )
        assign_slot_categories(remaining_slots)
        for slot in remaining_slots:
            db.add(slot)

        parking_lot.capacity = new_capacity
        available = [s.slot_name for s in remaining_slots if not s.is_occupied]
        parking_lot.available_slots = available
        flag_modified(parking_lot, "available_slots")

        used_labels = {s.row_label for s in remaining_slots}
        all_rows = (
            db.query(Row).filter(Row.parking_lot_id == parking_lot.parking_lot_id).all()
        )
        for row in all_rows:
            if row.row_label not in used_labels:
                db.delete(row)
        func_logger.info(
            f"Decreased capacity for parking lot ID: {parking_lot.parking_lot_id}"
        )
        db.commit()
        db.refresh(parking_lot)

    else:
        to_add = new_capacity - current_capacity
        slot_counter = get_next_slot_id(db)

        last_row = (
            db.query(Row)
            .filter(Row.parking_lot_id == parking_lot.parking_lot_id)
            .order_by(Row.row_label.desc())
            .first()
        )
        no_of_slots_in_last_row = (
            db.query(Slot)
            .filter(
                Slot.parking_lot_id == parking_lot.parking_lot_id,
                Slot.row_label == last_row.row_label,
            )
            .count()
        )

        slots_per_row = 10
        space_in_last_row = slots_per_row - no_of_slots_in_last_row
        created_slots = 0
        all_slots = []

        if space_in_last_row > 0:
            for j in range(no_of_slots_in_last_row + 1, slots_per_row + 1):
                if created_slots >= to_add:
                    break
                slot = Slot(
                    slot_id=f"SL{slot_counter}",
                    slot_name=f"{last_row.row_label}{j}",
                    parking_lot_id=parking_lot.parking_lot_id,
                    row_label=last_row.row_label,
                    is_occupied=False,
                )
                all_slots.append(slot)
                slot_counter += 1
                created_slots += 1

        remaining = to_add - created_slots

        current_row_count = (
            db.query(Row)
            .filter(Row.parking_lot_id == parking_lot.parking_lot_id)
            .count()
        )

        while remaining > 0:
            new_row_label = get_row_label(current_row_count)
            row = Row(
                parking_lot_id=parking_lot.parking_lot_id, row_label=new_row_label
            )
            db.add(row)

            for j in range(1, slots_per_row + 1):
                if remaining == 0:
                    break

                slot = Slot(
                    slot_id=f"SL{slot_counter}",
                    slot_name=f"{new_row_label}{j}",
                    parking_lot_id=parking_lot.parking_lot_id,
                    row_label=new_row_label,
                    is_occupied=False,
                )
                all_slots.append(slot)
                slot_counter += 1
                created_slots += 1
                remaining -= 1

            current_row_count += 1

        assign_slot_categories(all_slots)

        for slot in all_slots:
            db.add(slot)

        db.flush()

        all_slots = (
            db.query(Slot)
            .filter(Slot.parking_lot_id == parking_lot.parking_lot_id)
            .all()
        )
        assign_slot_categories(all_slots)

        parking_lot.capacity = new_capacity
        available = [s.slot_name for s in all_slots if not s.is_occupied]
        parking_lot.available_slots = available
        flag_modified(parking_lot, "available_slots")
        parking_lot.is_full = False
        func_logger.info(
            f"Increased capacity for parking lot ID: {parking_lot.parking_lot_id}"
        )
        db.commit()
        db.refresh(parking_lot)


def extract_lot_number(lot_id: str):
    match = re.search(r'\d+', lot_id)
    return int(match.group()) 


def guide_driver_to_parking_lot(request: Category, db: Session):
    driver_type = request.driver_category
    vehicle_type = request.vehicle_category

    if vehicle_type == "Large":
        category = "Large"
    elif driver_type == "Handicapped":
        category = "Handicapped"
    else:
        category = "Regular"

    lots = db.query(ParkingLot).all()
    selected_lot = None

    if category == "Handicapped":
        for lot in sorted(lots, key=lambda x: extract_lot_number(x.parking_lot_id)):
            has_slot = db.query(Slot).filter(
                Slot.parking_lot_id == lot.parking_lot_id,
                Slot.slot_category == "Handicapped",
                Slot.is_occupied == False
            ).first()
            if has_slot:
                selected_lot = lot
                break
    else:
        available_lots = []
        for lot in lots:
            used = db.query(Slot).filter(
                Slot.parking_lot_id == lot.parking_lot_id,
                Slot.slot_category == category,
                Slot.is_occupied == True
            ).count()
            free = db.query(Slot).filter(
                Slot.parking_lot_id == lot.parking_lot_id,
                Slot.slot_category == category,
                Slot.is_occupied == False
            ).count()

            if free > 0:
                available_lots.append((used, extract_lot_number(lot.parking_lot_id), lot))

        if available_lots:
            available_lots.sort(key=lambda x: (x[0], x[1]))
            _, _, selected_lot = available_lots[0]

    if not selected_lot:
        raise NoLotFoundException()

    return {
        "parking_lot_id": selected_lot.parking_lot_id
    }