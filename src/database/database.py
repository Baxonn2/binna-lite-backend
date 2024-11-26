from typing import Generator
from sqlmodel import create_engine, Session, SQLModel
import os

# Importing all models
# Import like this: from src.domains.task import models as task_models
from src.domains.auth import models as auth_models
from src.domains.customer import models as customer_models
from src.utils.settings import USE_MYSQL, MYSQL_CONNECTION_URL

class Databases:
    LOCAL = os.path.join("db", "local_database.db")
    TEST = os.path.join("db", "test_database.db")

class Database:    
    def __init__(self, sqlite_file_name: str = Databases.LOCAL):
        if USE_MYSQL:
            self.connection_url = MYSQL_CONNECTION_URL
        else:
            self.connection_url = f"sqlite:///{sqlite_file_name}"
        self.engine = create_engine(self.connection_url)

    def get_db_session(self) -> Generator[Session, None, None]:
        with Session(self.engine) as session:
            yield session

    def migrate(self):
        SQLModel.metadata.create_all(self.engine)

    def drop_all_tables(self):
        SQLModel.metadata.drop_all(self.engine)