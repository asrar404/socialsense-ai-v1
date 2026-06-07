"""Version 6 monitoring scheduling notifications

Revision ID: v6_001
Revises: 7310e252dc80
Create Date: 2026-06-05 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'v6_001'
down_revision = '7310e252dc80'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'worker_health',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('worker_name', sa.String(100), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='online'),
        sa.Column('last_heartbeat_at', sa.DateTime(), nullable=True),
        sa.Column('active_jobs', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('queue_length', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('processed_jobs_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('failed_jobs_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('worker_name'),
    )

    op.create_table(
        'scheduled_analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('platform', sa.String(20), nullable=False),
        sa.Column('source_type', sa.String(50), nullable=False),
        sa.Column('source_input', sa.String(500), nullable=False),
        sa.Column('comment_limit', sa.Integer(), nullable=True, server_default='100'),
        sa.Column('frequency', sa.String(20), nullable=False, server_default='once'),
        sa.Column('next_run_at', sa.DateTime(), nullable=True),
        sa.Column('last_run_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_scheduled_analyses_user_id', 'scheduled_analyses', ['user_id'])

    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('severity', sa.String(20), nullable=False, server_default='info'),
        sa.Column('is_read', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('link_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])

    op.create_table(
        'scheduled_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('report_type', sa.String(20), nullable=False, server_default='daily'),
        sa.Column('frequency', sa.String(20), nullable=False, server_default='daily'),
        sa.Column('platform_filter', sa.String(20), nullable=True),
        sa.Column('report_format', sa.String(10), nullable=False, server_default='html'),
        sa.Column('next_run_at', sa.DateTime(), nullable=True),
        sa.Column('last_run_at', sa.DateTime(), nullable=True),
        sa.Column('last_file_path', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_scheduled_reports_user_id', 'scheduled_reports', ['user_id'])

    op.create_table(
        'activity_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('resource_type', sa.String(50), nullable=True),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_activity_logs_user_id', 'activity_logs', ['user_id'])
    op.create_index('ix_activity_logs_action', 'activity_logs', ['action'])


def downgrade():
    op.drop_table('activity_logs')
    op.drop_table('scheduled_reports')
    op.drop_table('notifications')
    op.drop_table('scheduled_analyses')
    op.drop_table('worker_health')
