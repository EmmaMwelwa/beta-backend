"""recreate onboarding table

Revision ID: dc7147ae32b6
Revises: 12e139a3ca99
Create Date: 2026-08-27 11:23:04.523246

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'dc7147ae32b6'
down_revision: Union[str, Sequence[str], None] = '12e139a3ca99'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'onboarding',
        sa.Column('onboarding_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('user_interests', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            'social_platforms',
            postgresql.ARRAY(
                sa.Enum('tiktok', 'youtube', 'instagram', 'other', name='socialplatformenum', create_type=False)
            ),
            nullable=False,
        ),
        sa.Column('user_goal', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('career_aspirations', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['registrations.user_id']),
        sa.PrimaryKeyConstraint('onboarding_id'),
    )
    op.create_index(op.f('ix_onboarding_onboarding_id'), 'onboarding', ['onboarding_id'], unique=False)
    op.create_index(op.f('ix_onboarding_user_id'), 'onboarding', ['user_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_onboarding_user_id'), table_name='onboarding')
    op.drop_index(op.f('ix_onboarding_onboarding_id'), table_name='onboarding')
    op.drop_table('onboarding')