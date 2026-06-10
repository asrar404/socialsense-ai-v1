"""Version 9 channel context intelligence

Revision ID: v9_001
Revises: v8_001
Create Date: 2026-06-10 14:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = 'v9_001'
down_revision = 'v8_001'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('channel_contexts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('channel_id', sa.String(200), nullable=False, index=True),
        sa.Column('channel_name', sa.String(300), nullable=True),
        sa.Column('total_videos_analyzed', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_entities_detected', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('avg_sentiment', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('avg_risk', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table('video_context_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('analysis_id', sa.Integer(), sa.ForeignKey('analyses.id'), nullable=False, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('video_id', sa.String(20), nullable=False, index=True),
        sa.Column('channel_id', sa.String(200), nullable=True, index=True),
        sa.Column('video_title', sa.String(500), nullable=True),
        sa.Column('entity_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('avg_sentiment', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('avg_risk', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('top_entities', sa.Text(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table('entity_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('normalized_name', sa.String(300), nullable=False, index=True),
        sa.Column('entity_type', sa.String(30), nullable=True),
        sa.Column('video_id', sa.String(20), nullable=True, index=True),
        sa.Column('channel_id', sa.String(200), nullable=True, index=True),
        sa.Column('analysis_id', sa.Integer(), sa.ForeignKey('analyses.id'), nullable=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('sentiment_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('risk_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('mention_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('importance_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('entity_history')
    op.drop_table('video_context_history')
    op.drop_table('channel_contexts')
