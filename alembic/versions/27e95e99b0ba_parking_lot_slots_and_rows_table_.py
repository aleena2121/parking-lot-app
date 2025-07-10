"""parking lot, slots, and rows table creation

Revision ID: 27e95e99b0ba
Revises: 30bfafb32426
Create Date: 2025-07-07 17:08:54.672163
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op
from app.enums.slot_enum import SlotEnum

# revision identifiers, used by Alembic.
revision: str = "27e95e99b0ba"
down_revision: Union[str, Sequence[str], None] = "30bfafb32426"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    slot_enum = sa.Enum("Regular", "Large", "Handicapped", name="slotenum")

    op.create_table(
        "parkinglots",
        sa.Column(
            "parking_lot_id", sa.String(length=20), primary_key=True, nullable=False
        ),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("available_slots", sa.JSON(), nullable=False),
        sa.Column(
            "is_full", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.UniqueConstraint("parking_lot_id"),
    )

    op.create_table(
        "rows",
        sa.Column("parking_lot_id", sa.String(length=20), nullable=False),
        sa.Column("row_label", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint(
            "parking_lot_id",
            "row_label",
            name="pk_lot_row",
        ),
        sa.ForeignKeyConstraint(
            ["parking_lot_id"], ["parkinglots.parking_lot_id"], ondelete="CASCADE"
        ),
    )

    op.create_table(
        "slots",
        sa.Column("slot_id", sa.String(length=20), primary_key=True, nullable=False),
        sa.Column("slot_name", sa.String(length=20), nullable=False),
        sa.Column("parking_lot_id", sa.String(length=20), nullable=False),
        sa.Column("row_label", sa.String(length=20), nullable=False),
        sa.Column(
            "is_occupied", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column(
            "slot_category",
            sa.Enum("Regular", "Large", "Handicapped", name="slotenum"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["parking_lot_id"], ["parkinglots.parking_lot_id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["parking_lot_id", "row_label"],
            ["rows.parking_lot_id", "rows.row_label"],
            ondelete="CASCADE",
        ),
    )


def downgrade() -> None:
    op.drop_table("slots")
    op.drop_table("rows")
    op.drop_table("parkinglots")
    sa.Enum(name="slotenum").drop(op.get_bind(), checkfirst=True)
