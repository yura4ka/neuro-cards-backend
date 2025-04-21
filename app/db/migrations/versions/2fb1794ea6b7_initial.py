"""initial

Revision ID: 2fb1794ea6b7
Revises:
Create Date: 2025-04-21 18:10:14.470536

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "2fb1794ea6b7"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

deck_type_enum = postgresql.ENUM(
    "Quiz", "Flashcards", name="deck_type", create_type=False
)


def create_updated_at_trigger() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_timestamp()
        RETURNS TRIGGER AS $$
        BEGIN
        NEW.updated_at = Now();
        RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )


def add_update_at_trigger(table_name: str) -> None:
    op.execute(
        f"""
        CREATE TRIGGER set_timestamp
        BEFORE UPDATE ON {table_name}
        FOR EACH ROW
        EXECUTE PROCEDURE update_timestamp();
        """
    )


def create_users_table() -> None:
    op.create_table(
        "users",
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
        if_not_exists=True,
    )


def create_decks_table() -> None:
    op.create_table(
        "decks",
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
        if_not_exists=True,
    )
    add_update_at_trigger("decks")


def create_cards_table() -> None:
    op.create_table(
        "cards",
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
        sa.Column(
            "deck_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("decks.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        if_not_exists=True,
    )


def create_question_options_table() -> None:
    op.create_table(
        "question_options",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("answer", sa.Text, nullable=False),
        sa.Column(
            "is_correct", sa.Boolean, nullable=False, server_default=sa.text("FALSE")
        ),
        sa.Column(
            "card_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cards.id", ondelete="CASCADE"),
            nullable=False,
        ),
        if_not_exists=True,
    )


def create_deck_migrations_table() -> None:
    op.create_table(
        "deck_migrations",
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
        sa.Column(
            "deck_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("decks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("version", sa.Integer, nullable=False),
        sa.UniqueConstraint("deck_id", "version"),
        if_not_exists=True,
    )


def create_deck_migration_updates_table() -> None:
    op.create_table(
        "deck_migration_updates",
        sa.Column(
            "card_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cards.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "deck_migration_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("deck_migrations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "card_removed", sa.Boolean, nullable=False, server_default=sa.text("FALSE")
        ),
        sa.PrimaryKeyConstraint("deck_migration_id", "card_id"),
        if_not_exists=True,
    )


def create_user_decks_table() -> None:
    op.create_table(
        "user_decks",
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
        sa.PrimaryKeyConstraint("user_id", "deck_id"),
        if_not_exists=True,
    )


def create_user_card_info_table() -> None:
    op.create_table(
        "user_card_info",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "card_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cards.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("last_answered_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("repetition_number", sa.Integer, nullable=False),
        sa.Column("easiness_factor", sa.REAL, nullable=False),
        sa.Column("interval", sa.REAL, nullable=False),
        sa.Column(
            "is_learning", sa.Boolean, nullable=False, server_default=sa.text("TRUE")
        ),
        sa.Column("learning_step", sa.Integer, nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("user_id", "card_id"),
        if_not_exists=True,
    )


def create_tokens_table() -> None:
    op.create_table(
        "tokens",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("token", sa.Text, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "is_invalid", sa.Boolean, nullable=False, server_default=sa.text("FALSE")
        ),
        if_not_exists=True,
    )


def upgrade() -> None:
    """Upgrade schema."""
    deck_type_enum.create(op.get_bind(), checkfirst=True)
    create_updated_at_trigger()

    create_users_table()
    create_decks_table()
    create_cards_table()
    create_question_options_table()
    create_deck_migrations_table()
    create_deck_migration_updates_table()
    create_user_decks_table()
    create_user_card_info_table()
    create_tokens_table()


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("tokens", if_exists=True)
    op.drop_table("user_card_info", if_exists=True)
    op.drop_table("user_decks", if_exists=True)
    op.drop_table("deck_migration_updates", if_exists=True)
    op.drop_table("deck_migrations", if_exists=True)
    op.drop_table("question_options", if_exists=True)
    op.drop_table("cards", if_exists=True)
    op.drop_table("decks", if_exists=True)
    op.drop_table("users", if_exists=True)
    deck_type_enum.drop(op.get_bind(), checkfirst=True)
    op.execute("DROP FUNCTION IF EXISTS update_timestamp;")
