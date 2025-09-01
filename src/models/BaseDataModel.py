from src.helpers.config import get_settings, Settings
from sqlalchemy.orm import sessionmaker


class BaseDataModel:
    def __init__(self, db_client: sessionmaker):
        self.db_client = db_client
        self.app_settings: Settings = get_settings()
