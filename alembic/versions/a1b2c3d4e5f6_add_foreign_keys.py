"""add foreign keys

Revision ID: a1b2c3d4e5f6
Revises: 715bfa9f1355
Create Date: 2025-12-15 00:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '715bfa9f1355'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # posts
    op.create_foreign_key('fk_posts_owner_id', 'posts', 'users', ['owner_id'], ['id'], source_schema='linap', referent_schema='linap')
    op.create_foreign_key('fk_posts_map_id', 'posts', 'maps', ['map_id'], ['id'], source_schema='linap', referent_schema='linap')

    # videos
    op.create_foreign_key('fk_videos_owner_id', 'videos', 'users', ['owner_id'], ['id'], source_schema='linap', referent_schema='linap')
    op.create_foreign_key('fk_videos_map_id', 'videos', 'maps', ['map_id'], ['id'], source_schema='linap', referent_schema='linap')

    # comments
    op.create_foreign_key('fk_comments_user_id', 'comments', 'users', ['user_id'], ['id'], source_schema='linap', referent_schema='linap')
    op.create_foreign_key('fk_comments_post_id', 'comments', 'posts', ['post_id'], ['id'], source_schema='linap', referent_schema='linap')
    op.create_foreign_key('fk_comments_parent_id', 'comments', 'comments', ['parent_id'], ['id'], source_schema='linap', referent_schema='linap')

    # auth_accounts
    op.create_foreign_key('fk_auth_accounts_user_id', 'auth_accounts', 'users', ['user_id'], ['id'], source_schema='linap', referent_schema='linap')

    # abilities
    op.create_foreign_key('fk_abilities_agent_id', 'abilities', 'agents', ['agent_id'], ['id'], source_schema='linap', referent_schema='linap')

    # post_tags
    op.create_foreign_key('fk_post_tags_post_id', 'post_tags', 'posts', ['post_id'], ['id'], source_schema='linap', referent_schema='linap')
    op.create_foreign_key('fk_post_tags_tag_id', 'post_tags', 'tags', ['tag_id'], ['id'], source_schema='linap', referent_schema='linap')

    # likes
    op.create_foreign_key('fk_likes_user_id', 'likes', 'users', ['user_id'], ['id'], source_schema='linap', referent_schema='linap')

    # sessions
    op.create_foreign_key('fk_sessions_user_id', 'sessions', 'users', ['user_id'], ['id'], source_schema='linap', referent_schema='linap')

    # email_verifications
    op.create_foreign_key('fk_email_verifications_user_id', 'email_verifications', 'users', ['user_id'], ['id'], source_schema='linap', referent_schema='linap')

    # password_resets
    op.create_foreign_key('fk_password_resets_user_id', 'password_resets', 'users', ['user_id'], ['id'], source_schema='linap', referent_schema='linap')


def downgrade() -> None:
    # drop in reverse order
    op.drop_constraint('fk_password_resets_user_id', 'password_resets', schema='linap', type_='foreignkey')
    op.drop_constraint('fk_email_verifications_user_id', 'email_verifications', schema='linap', type_='foreignkey')
    op.drop_constraint('fk_sessions_user_id', 'sessions', schema='linap', type_='foreignkey')
    op.drop_constraint('fk_likes_user_id', 'likes', schema='linap', type_='foreignkey')
    op.drop_constraint('fk_post_tags_tag_id', 'post_tags', schema='linap', type_='foreignkey')
    op.drop_constraint('fk_post_tags_post_id', 'post_tags', schema='linap', type_='foreignkey')
    op.drop_constraint('fk_abilities_agent_id', 'abilities', schema='linap', type_='foreignkey')
    op.drop_constraint('fk_auth_accounts_user_id', 'auth_accounts', schema='linap', type_='foreignkey')
    op.drop_constraint('fk_comments_parent_id', 'comments', schema='linap', type_='foreignkey')
    op.drop_constraint('fk_comments_post_id', 'comments', schema='linap', type_='foreignkey')
    op.drop_constraint('fk_comments_user_id', 'comments', schema='linap', type_='foreignkey')
    op.drop_constraint('fk_videos_map_id', 'videos', schema='linap', type_='foreignkey')
    op.drop_constraint('fk_videos_owner_id', 'videos', schema='linap', type_='foreignkey')
    op.drop_constraint('fk_posts_map_id', 'posts', schema='linap', type_='foreignkey')
    op.drop_constraint('fk_posts_owner_id', 'posts', schema='linap', type_='foreignkey')
