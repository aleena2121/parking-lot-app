"""transation table creation

Revision ID: c2ffe7111fc0
Revises: 16bae7f721a1
Create Date: 2025-07-11 18:36:34.504794

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c2ffe7111fc0"
down_revision: Union[str, Sequence[str], None] = "16bae7f721a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "transactions",
        sa.Column("transaction_id", sa.String(), primary_key=True),
        sa.Column(
            "ticket_id", sa.String(), sa.ForeignKey("tickets.ticket_id"), nullable=False
        ),
        sa.Column(
            "payment_timestamp",
            sa.TIMESTAMP,
            nullable=True,
        ),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("payment_status", sa.String(length=50), nullable=False),
    )
    op.create_index(
        "ix_transactions_transaction_id", "transactions", ["transaction_id"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_transactions_transaction_id", table_name="transactions")
    op.drop_table("transactions")
