"""add video_id to comments table

Revision ID: b3c4d5e6f7g8
Revises: a1b2c3d4e5f6, 2dbb4d950187
Create Date: 2026-01-06 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b3c4d5e6f7g8'
down_revision = ('a1b2c3d4e5f6', '2dbb4d950187')
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add video_id column to comments table
    op.add_column(
        'comments',
        sa.Column('video_id', postgresql.UUID(as_uuid=True), nullable=True),
        schema='linap'
    )
    
    # Create index on video_id
    op.create_index(
        'idx_comments_video',
        'comments',
        ['video_id'],
        schema='linap'
    )
    
    # Create foreign key for video_id
    op.create_foreign_key(
        'fk_comments_video_id',
        'comments',
        'videos',
        ['video_id'],
        ['id'],
        source_schema='linap',
        referent_schema='linap'
    )


def downgrade() -> None:
    # Drop foreign key
    op.drop_constraint(
        'fk_comments_video_id',
        'comments',
        schema='linap'
    )
    
    # Drop index
    op.drop_index(
        'idx_comments_video',
        schema='linap'
    )
    
    # Drop column
    op.drop_column(
        'comments',
        'video_id',
        schema='linap'
    )
