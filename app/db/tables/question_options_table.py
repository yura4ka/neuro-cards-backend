import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def create_question_options_table(metadata: sa.MetaData) -> sa.Table:
    return sa.Table(
        "question_options",
        metadata,
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("answer", sa.Text, nullable=False),
        sa.Column(
            "card_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cards.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
