"""add video_views table for tracking unique views

Revision ID: 5a00582501dd
Revises: b3c4d5e6f7g8
Create Date: 2026-01-06 12:17:01.302339

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5a00582501dd'
down_revision: Union[str, Sequence[str], None] = 'b3c4d5e6f7g8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create video_views table
    op.create_table(
        'video_views',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('video_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('viewed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['linap.users.id'], ),
        sa.ForeignKeyConstraint(['video_id'], ['linap.videos.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'video_id', name='uq_user_video_view'),
        schema='linap'
    )
    
    # Create indexes
    op.create_index('idx_video_views_video', 'video_views', ['video_id'], schema='linap')
    op.create_index('idx_video_views_user', 'video_views', ['user_id'], schema='linap')


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_video_views_user', table_name='video_views', schema='linap')
    op.drop_index('idx_video_views_video', table_name='video_views', schema='linap')
    
    # Drop table
    op.drop_table('video_views', schema='linap')
