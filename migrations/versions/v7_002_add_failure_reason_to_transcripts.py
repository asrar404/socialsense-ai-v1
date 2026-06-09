"""Add failure_reason column to video_transcripts

Revision ID: v7_002
Revises: v7_001
Create Date: 2026-06-07 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'v7_002'
down_revision = 'v7_001'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('video_transcripts', sa.Column('failure_reason', sa.String(50), nullable=True))


def downgrade():
    op.drop_column('video_transcripts', 'failure_reason')
