import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def create_cards_table(
    metadata: sa.MetaData, deck_type_enum: postgresql.ENUM
) -> sa.Table:
    return sa.Table(
        "cards",
        metadata,
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("type", deck_type_enum, nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("difficulty", postgresql.SMALLINT, nullable=False),
        sa.Column("correct_answer_id", postgresql.UUID(as_uuid=True)),
        sa.Column(
            "is_deleted", sa.Boolean, nullable=False, server_default=sa.text("FALSE")
        ),
        sa.Column(
            "deck_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("decks.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
    )
