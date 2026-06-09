"""Version 8 entity intelligence

Revision ID: v8_001
Revises: v7_002
Create Date: 2026-06-10 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = 'v8_001'
down_revision = 'v7_002'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('entities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('analysis_id', sa.Integer(), sa.ForeignKey('analyses.id'), nullable=False, index=True),
        sa.Column('name', sa.String(300), nullable=False),
        sa.Column('normalized_name', sa.String(300), nullable=False),
        sa.Column('entity_type', sa.String(30), nullable=False),
        sa.Column('source', sa.String(20), nullable=False),
        sa.Column('frequency', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('importance_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table('entity_mentions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_id', sa.Integer(), sa.ForeignKey('entities.id'), nullable=False, index=True),
        sa.Column('comment_result_id', sa.Integer(), sa.ForeignKey('comment_results.id'), nullable=True, index=True),
        sa.Column('transcript_segment_id', sa.Integer(), sa.ForeignKey('transcript_segments.id'), nullable=True, index=True),
        sa.Column('mention_text', sa.String(300), nullable=False),
        sa.Column('mention_source', sa.String(20), nullable=False),
        sa.Column('context_snippet', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table('entity_contexts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_id', sa.Integer(), sa.ForeignKey('entities.id'), nullable=False, index=True),
        sa.Column('comment_result_id', sa.Integer(), sa.ForeignKey('comment_results.id'), nullable=False, index=True),
        sa.Column('entity_sentiment', sa.String(20), nullable=True),
        sa.Column('entity_sentiment_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('entity_risk_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('entity_relevance_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('entity_context_label', sa.String(30), nullable=True, server_default='unknown'),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('entity_contexts')
    op.drop_table('entity_mentions')
    op.drop_table('entities')
