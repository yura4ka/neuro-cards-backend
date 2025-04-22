import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def create_user_table(metadata: sa.MetaData) -> sa.Table:
    return sa.Table(
        "users",
        metadata,
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("username", sa.String(64), nullable=False, unique=True),
        sa.Column("email", sa.String(64), nullable=False, unique=True),
        sa.Column("password", sa.Text, nullable=False),
        sa.Column("restoration_code", sa.String(128)),
        sa.Column("restoration_expires_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("last_restoration_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("last_restoration_request_at", sa.TIMESTAMP(timezone=True)),
        sa.Column(
            "restoration_attempts", sa.Integer, nullable=False, server_default="0"
        ),
    )
