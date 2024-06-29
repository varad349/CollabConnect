from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    database_hostname:str="localhost"
    database_port:str="postgres"
    database_password:str="123456"
    database_name:str
    database_username:str
    secret_key:str
    algorithm:str
    access_token_expires_minutes:int
    class Config:
        env_file = os.path.join(os.path.dirname(__file__), '..', '.env')

setting=Settings()