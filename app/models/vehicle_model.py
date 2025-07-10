from sqlalchemy import Enum as SQLAEnum
from sqlalchemy import ForeignKey, Integer, String, event, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.enums.driver_enum import DriverEnum
from app.enums.vehicle_enum import VehicleEnum


class Vehicle(Base):
    __tablename__ = "vehicles"

    vehicle_id: Mapped[str] = mapped_column(primary_key=True, index=True)
    plate_number: Mapped[str] = mapped_column(String, nullable=False)
    make: Mapped[str] = mapped_column(String, nullable=True)
    model: Mapped[str] = mapped_column(String, nullable=True)
    color: Mapped[str] = mapped_column(String, nullable=True)
    vehicle_category: Mapped[VehicleEnum] = mapped_column(
        SQLAEnum(VehicleEnum, name="vehicleenum"), nullable=False
    )
    driver_category: Mapped[DriverEnum] = mapped_column(
        SQLAEnum(DriverEnum, name="driverenum"), nullable=False
    )

    tickets = relationship("Ticket", back_populates="vehicle")


@event.listens_for(Vehicle, "before_insert")
def get_vehicle_id(mapper, connection, target):
    result = connection.execute(
        text(
            "SELECT vehicle_id FROM vehicles ORDER BY CAST(SUBSTRING(vehicle_id FROM 3) AS INTEGER) DESC LIMIT 1"
        )
    ).first()

    if result is None:
        next_num = 1
    else:
        last_id = result[0]
        last_num = int(last_id.replace("VH", ""))
        next_num = last_num + 1

    target.vehicle_id = f"VH{next_num}"
