import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def create_deck_type() -> postgresql.ENUM:
    return postgresql.ENUM("Quiz", "Flashcards", name="deck_type", create_type=False)


def create_decks_table(
    metadata: sa.MetaData, deck_type_enum: postgresql.ENUM
) -> sa.Table:
    return sa.Table(
        "decks",
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
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("version", sa.Integer, nullable=False, server_default="0"),
        sa.Column("title", sa.String(128), nullable=False),
        sa.Column("type", deck_type_enum, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
    )
