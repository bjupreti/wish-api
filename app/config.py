from pydantic import BaseSettings

class Settings(BaseSettings):
    # DB
    db_hostname: str
    db_port: str
    db_password: str
    db_name: str
    db_username: str
    # JWT
    secret_key: str
    algorithm: str
    access_token_expire_mintues: int

    class Config:
        env_file = ".env"

settings = Settings()