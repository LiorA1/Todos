"""add apt num column to address

Revision ID: 10023c5f0e30
Revises: 6ee645444d1d
Create Date: 2023-05-07 18:26:02.451691

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "10023c5f0e30"
down_revision = "6ee645444d1d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("address", sa.Column("apt_num", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("address", "apt_num")
