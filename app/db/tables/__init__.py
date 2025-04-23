from sqlalchemy import MetaData
from app.db.tables.cards_table import create_cards_table
from app.db.tables.decks_table import create_deck_type, create_decks_table
from app.db.tables.question_options_table import create_question_options_table
from app.db.tables.user_decks_table import create_user_decks_table
from app.db.tables.users_table import create_users_table

metadata = MetaData()
deck_type_enum = create_deck_type()
users_table = create_users_table(metadata)
decks_table = create_decks_table(metadata, deck_type_enum)
user_decks_table = create_user_decks_table(metadata)
cards_table = create_cards_table(metadata, deck_type_enum)
question_options_table = create_question_options_table(metadata)
