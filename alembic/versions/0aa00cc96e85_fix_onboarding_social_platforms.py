"""fix onboarding social platforms type

Revision ID: 0aa00cc96e85
Revises: dc7147ae32b6
Create Date: 2026-09-18
"""

from typing import Sequence, Union

from alembic import op


revision: str = "0aa00cc96e85"
down_revision: Union[str, Sequence[str], None] = "dc7147ae32b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'onboarding'
                  AND column_name = 'social_platforms'
                  AND udt_name = 'socialplatformenum'
            ) THEN
                ALTER TABLE onboarding
                ALTER COLUMN social_platforms
                TYPE socialplatformenum[]
                USING ARRAY[social_platforms];
            END IF;
        END
        $$;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'onboarding'
                  AND column_name = 'social_platforms'
                  AND udt_name = '_socialplatformenum'
            ) THEN
                ALTER TABLE onboarding
                ALTER COLUMN social_platforms
                TYPE socialplatformenum
                USING social_platforms[1];
            END IF;
        END
        $$;
        """
    )
