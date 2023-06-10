from sqlalchemy import create_engine
from pydantic import BaseSettings

class DB_Cred(BaseSettings):
    DB_HOST : str
    DB_PORT : str
    DB_PASSWORD : str
    DB_NAME : str
    DB_USERNAME : str
    DB_CONNECTOR : str
    DB : str
    class Config:
        env_file = ".env"

db_cred = DB_Cred()


DB_URL = f"{ db_cred.DB }+{ db_cred.DB_CONNECTOR }://{ db_cred.DB_USERNAME }:{ db_cred.DB_PASSWORD }@{ db_cred.DB_HOST }:{ db_cred.DB_PORT }/{ db_cred.DB_NAME }"

Engine = create_engine(DB_URL)