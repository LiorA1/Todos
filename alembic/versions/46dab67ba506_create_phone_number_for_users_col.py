"""create phone number for users col

Revision ID: 46dab67ba506
Revises: 
Create Date: 2023-05-07 16:20:09.855410

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '46dab67ba506'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("phone_number", sa.String(), nullable = True))


def downgrade() -> None:
    op.drop_column("users", "phone_number")
