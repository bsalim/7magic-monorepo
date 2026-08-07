"""add english article slugs

Gives articles and their categories a second, English URL slug so an English
article can live at an English URL instead of borrowing the Indonesian one.

Both columns are nullable and both unique indexes tolerate NULL (distinct under
SQLite and Postgres alike), so this migration is a no-op for existing content:
every row keeps a NULL English slug until `scripts/backfill_article_slug_en.py`
fills it in, and the readers fall back to the Indonesian slug meanwhile.

Revision ID: c14e2f7a91d3
Revises: b33b66a6a6bc
Create Date: 2026-08-06 09:12:04.118273
"""

from alembic import op
import sqlalchemy as sa


revision = 'c14e2f7a91d3'
down_revision = 'b33b66a6a6bc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('articles', sa.Column('slug_en', sa.String(length=255), nullable=True))
    op.add_column(
        'article_categories',
        sa.Column('category_slug_en', sa.String(length=255), nullable=True),
    )
    op.create_index(
        'uq_articles_category_slug_en',
        'articles',
        ['category_id', 'slug_en'],
        unique=True,
    )
    op.create_index(
        'uq_article_categories_category_slug_en',
        'article_categories',
        ['category_slug_en'],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index('uq_article_categories_category_slug_en', table_name='article_categories')
    op.drop_index('uq_articles_category_slug_en', table_name='articles')
    op.drop_column('article_categories', 'category_slug_en')
    op.drop_column('articles', 'slug_en')
