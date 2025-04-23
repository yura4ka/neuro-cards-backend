import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def create_user_decks_table(metadata: sa.MetaData) -> sa.Table:
    return sa.Table(
        "user_decks",
        metadata,
        sa.Column(
            "deck_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("decks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True)),
        sa.PrimaryKeyConstraint("user_id", "deck_id"),
    )
