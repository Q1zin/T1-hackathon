"""Initial tables

Revision ID: 001
Revises:
Create Date: 2025-10-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('extra_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )
    op.create_index('ix_projects_key', 'projects', ['key'])
    op.create_index('ix_projects_created_at', 'projects', ['created_at'])

    # Repositories table
    op.create_table(
        'repositories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('default_branch', sa.String(length=255), nullable=True),
        sa.Column('clone_url', sa.String(length=512), nullable=True),
        sa.Column('is_fork', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('extra_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('last_commit_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id', 'slug', name='uq_repo_project_slug')
    )
    op.create_index('ix_repositories_project_id', 'repositories', ['project_id'])
    op.create_index('ix_repositories_slug', 'repositories', ['slug'])

    # Commits table
    op.create_table(
        'commits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('repository_id', sa.Integer(), nullable=False),
        sa.Column('sha', sa.String(length=40), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('author_name', sa.String(length=255), nullable=False),
        sa.Column('author_email', sa.String(length=255), nullable=False),
        sa.Column('committer_name', sa.String(length=255), nullable=False),
        sa.Column('committer_email', sa.String(length=255), nullable=False),
        sa.Column('authored_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('committed_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('parent_shas', postgresql.ARRAY(sa.String(40)), nullable=True),
        sa.Column('branch_names', postgresql.ARRAY(sa.String(255)), nullable=True),
        sa.Column('extra_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('repository_id', 'sha', name='uq_commit_repo_sha')
    )
    op.create_index('ix_commits_repository_id', 'commits', ['repository_id'])
    op.create_index('ix_commits_sha', 'commits', ['sha'])
    op.create_index('ix_commits_author_email', 'commits', ['author_email'])
    op.create_index('ix_commits_authored_date', 'commits', ['authored_date'])

    # Metrics table
    op.create_table(
        'metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('repository_id', sa.Integer(), nullable=True),
        sa.Column('metric_type', sa.String(length=100), nullable=False),
        sa.Column('metric_name', sa.String(length=255), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('extra_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_metrics_repository_id', 'metrics', ['repository_id'])
    op.create_index('ix_metrics_type', 'metrics', ['metric_type'])
    op.create_index('ix_metrics_calculated_at', 'metrics', ['calculated_at'])

    # Anomalies table
    op.create_table(
        'anomalies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('metric_id', sa.Integer(), nullable=True),
        sa.Column('repository_id', sa.Integer(), nullable=True),
        sa.Column('anomaly_type', sa.String(length=100), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('value', sa.Float(), nullable=True),
        sa.Column('threshold', sa.Float(), nullable=True),
        sa.Column('z_score', sa.Float(), nullable=True),
        sa.Column('extra_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('detected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['metric_id'], ['metrics.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_anomalies_repository_id', 'anomalies', ['repository_id'])
    op.create_index('ix_anomalies_detected_at', 'anomalies', ['detected_at'])
    op.create_index('ix_anomalies_severity', 'anomalies', ['severity'])

    # Recommendations table
    op.create_table(
        'recommendations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('repository_id', sa.Integer(), nullable=True),
        sa.Column('anomaly_id', sa.Integer(), nullable=True),
        sa.Column('recommendation_type', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('priority', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('extra_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('applied_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['anomaly_id'], ['anomalies.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_recommendations_repository_id', 'recommendations', ['repository_id'])
    op.create_index('ix_recommendations_status', 'recommendations', ['status'])
    op.create_index('ix_recommendations_priority', 'recommendations', ['priority'])


def downgrade() -> None:
    op.drop_table('recommendations')
    op.drop_table('anomalies')
    op.drop_table('metrics')
    op.drop_table('commits')
    op.drop_table('repositories')
    op.drop_table('projects')
