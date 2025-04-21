from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_url: str
    sa_db_url: str
    access_token: str
    refresh_token: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
