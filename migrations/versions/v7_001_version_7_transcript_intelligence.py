"""Version 7 transcript intelligence engine

Revision ID: v7_001
Revises: v6_001
Create Date: 2026-06-07 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'v7_001'
down_revision = 'v6_001'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'video_transcripts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('youtube_analysis_id', sa.Integer(), nullable=False),
        sa.Column('video_id', sa.String(50), nullable=False),
        sa.Column('language', sa.String(10), nullable=True),
        sa.Column('transcript_text', sa.Text(), nullable=True),
        sa.Column('source', sa.String(30), nullable=False, server_default='unavailable'),
        sa.Column('is_auto_generated', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('segment_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('word_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('topics', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['youtube_analysis_id'], ['youtube_analyses.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_video_transcripts_youtube_analysis_id', 'video_transcripts', ['youtube_analysis_id'])

    op.create_table(
        'transcript_segments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transcript_id', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.Float(), nullable=False),
        sa.Column('end_time', sa.Float(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('word_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('segment_index', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['transcript_id'], ['video_transcripts.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_transcript_segments_transcript_id', 'transcript_segments', ['transcript_id'])

    op.create_table(
        'comment_contexts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('comment_result_id', sa.Integer(), nullable=False),
        sa.Column('transcript_id', sa.Integer(), nullable=True),
        sa.Column('best_segment_id', sa.Integer(), nullable=True),
        sa.Column('transcript_relevance_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('topic_alignment_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('off_topic_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('context_match_label', sa.String(30), nullable=True, server_default='unknown'),
        sa.Column('matched_keywords', sa.Text(), nullable=True),
        sa.Column('matched_phrases', sa.Text(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['comment_result_id'], ['comment_results.id'], ),
        sa.ForeignKeyConstraint(['transcript_id'], ['video_transcripts.id'], ),
        sa.ForeignKeyConstraint(['best_segment_id'], ['transcript_segments.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('comment_result_id'),
    )
    op.create_index('ix_comment_contexts_comment_result_id', 'comment_contexts', ['comment_result_id'])


def downgrade():
    op.drop_table('comment_contexts')
    op.drop_table('transcript_segments')
    op.drop_table('video_transcripts')
