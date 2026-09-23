"""sync generated assessment table

Revision ID: aa3a56eefe29
Revises: 4243dee5606b
Create Date: 2026-09-22 11:42:59.609867

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aa3a56eefe29'
down_revision: Union[str, Sequence[str], None] = '4243dee5606b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
