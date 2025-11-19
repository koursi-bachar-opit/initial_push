"""Replace buyer_name with buyer_user_id

Revision ID: a954d8337b1c
Revises: 1427e343ea77
Create Date: 2025-11-14 23:23:27.461563
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a954d8337b1c'
down_revision: Union[str, Sequence[str], None] = '1427e343ea77'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: buyer_name → buyer_user_id"""

    # 1. Add buyer_user_id column as nullable first
    op.add_column(
        "bookings",
        sa.Column("buyer_user_id", sa.Integer(), nullable=True)
    )

    # 2. Backfill based on existing buyer_name (email match)
    # This will assign buyer_user_id where possible.
    op.execute("""
        UPDATE bookings b
        SET buyer_user_id = u.id
        FROM users u
        WHERE b.buyer_name = u.email;
    """)

    # 3. Drop old buyer_name column
    op.drop_column("bookings", "buyer_name")

    # 4. Now enforce NOT NULL constraint
    op.alter_column(
        "bookings",
        "buyer_user_id",
        nullable=False
    )

    # 5. Create FK constraint
    op.create_foreign_key(
        "fk_booking_buyer_user",
        "bookings",
        "users",
        ["buyer_user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Reverse the upgrade."""
    # Re-add buyer_name
    op.add_column(
        "bookings",
        sa.Column("buyer_name", sa.String(), nullable=True)
    )

    # Drop FK
    op.drop_constraint("fk_booking_buyer_user", "bookings", type_="foreignkey")

    # Make buyer_user_id nullable again, then drop it
    op.alter_column(
        "bookings",
        "buyer_user_id",
        nullable=True
    )
    op.drop_column("bookings", "buyer_user_id")