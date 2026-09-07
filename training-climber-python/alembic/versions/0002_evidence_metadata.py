"""Complete evidence metadata.

Revision ID: 0002
Revises: 0001
"""
import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    existing = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("evidence")}
    with op.batch_alter_table("evidence") as batch:
        for column in (
            sa.Column("volume", sa.String(40), nullable=True),
            sa.Column("issue", sa.String(40), nullable=True),
            sa.Column("pages", sa.String(60), nullable=True),
            sa.Column("population", sa.Text(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
        ):
            if column.name not in existing:
                batch.add_column(column)


def downgrade():
    existing = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("evidence")}
    with op.batch_alter_table("evidence") as batch:
        for name in ("notes", "population", "pages", "issue", "volume"):
            if name in existing:
                batch.drop_column(name)
