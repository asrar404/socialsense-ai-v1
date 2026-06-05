"""Version 5 background jobs

Revision ID: 7310e252dc80
Revises: fbded892f0a3
Create Date: 2026-06-05 13:25:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '7310e252dc80'
down_revision = 'fbded892f0a3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('job_type', sa.String(32), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='PENDING'),
        sa.Column('progress', sa.Float(), nullable=False, server_default='0'),
        sa.Column('progress_message', sa.Text(), nullable=True),
        sa.Column('source_input', sa.Text(), nullable=False),
        sa.Column('comment_limit', sa.Integer(), nullable=True),
        sa.Column('request_hash', sa.String(64), nullable=False),
        sa.Column('result_analysis_id', sa.Integer(), sa.ForeignKey('analyses.id'), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_retries', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_jobs_user_id', 'jobs', ['user_id'])
    op.create_index('ix_jobs_status', 'jobs', ['status'])
    op.create_index('ix_jobs_request_hash', 'jobs', ['request_hash'])
    op.create_unique_constraint('uq_jobs_request_hash_status', 'jobs', ['request_hash', 'status'])

    op.create_table(
        'job_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), sa.ForeignKey('jobs.id'), nullable=False),
        sa.Column('level', sa.String(16), nullable=False, server_default='INFO'),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_job_logs_job_id', 'job_logs', ['job_id'])


def downgrade():
    op.drop_table('job_logs')
    op.drop_table('jobs')
