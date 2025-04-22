from sqlalchemy import MetaData
from app.db.tables.user_table import create_user_table

metadata = MetaData()
user_table = create_user_table(metadata)