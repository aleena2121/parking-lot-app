"""vehicles table creation

Revision ID: 16bae7f721a1
Revises: 27e95e99b0ba
Create Date: 2025-07-10 02:49:08.156833

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op
from app.enums.driver_enum import DriverEnum
from app.enums.vehicle_enum import VehicleEnum

# revision identifiers, used by Alembic.
revision: str = "16bae7f721a1"
down_revision: Union[str, Sequence[str], None] = "27e95e99b0ba"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "vehicles",
        sa.Column("vehicle_id", sa.String(), primary_key=True),
        sa.Column("plate_number", sa.String(), nullable=False),
        sa.Column("make", sa.String(), nullable=False),
        sa.Column("model", sa.String(), nullable=False),
        sa.Column("color", sa.String(), nullable=False),
        sa.Column("driver_phone_no", sa.String(), nullable=False),
        sa.Column(
            "vehicle_category", sa.Enum(VehicleEnum, name="vehicleenum"), nullable=False
        ),
        sa.Column(
            "driver_category", sa.Enum(DriverEnum, name="driverenum"), nullable=False
        ),
    )
    op.create_index("ix_vehicles_vehicle_id", "vehicles", ["vehicle_id"])

    op.create_table(
        "tickets",
        sa.Column("ticket_id", sa.String(), primary_key=True),
        sa.Column(
            "vehicle_id",
            sa.String(),
            sa.ForeignKey("vehicles.vehicle_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "parking_lot_id",
            sa.String(),
            sa.ForeignKey("parkinglots.parking_lot_id"),
            nullable=False,
        ),
        sa.Column(
            "slot_id", sa.String(), sa.ForeignKey("slots.slot_id"), nullable=False
        ),
        sa.Column(
            "attendant_id",
            sa.String(),
            sa.ForeignKey("attendants.user_id"),
            nullable=False,
        ),
        sa.Column("entry_time", sa.DateTime(), nullable=False),
        sa.Column("exit_time", sa.DateTime(), nullable=True),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
    )
    op.create_index("ix_tickets_ticket_id", "tickets", ["ticket_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_tickets_ticket_id", table_name="tickets")
    op.drop_table("tickets")
    op.drop_index("ix_vehicles_vehicle_id", table_name="vehicles")
    op.drop_table("vehicles")
    op.execute("DROP TYPE vehicleenum")
    op.execute("DROP TYPE driverenum")
