from pydantic import BaseSettings, Field, SecretStr
from typing import Optional


class Settings(BaseSettings):
    portal_user: str = Field(..., env="PORTAL_USER")
    portal_pass: SecretStr = Field(..., env="PORTAL_PASS")
    portal_totp_secret: Optional[SecretStr] = Field(None, env="PORTAL_TOTP_SECRET")

    tg_bot_token: str = Field(..., env="TG_BOT_TOKEN")
    tg_chat_id: str = Field(..., env="TG_CHAT_ID")

    poll_min_seconds: int = Field(120, env="POLL_MIN_SECONDS")
    poll_max_seconds: int = Field(240, env="POLL_MAX_SECONDS")

    headless: bool = Field(True, env="HEADLESS")
    enable_metrics: bool = Field(True, env="ENABLE_METRICS")
    state_file: str = Field("./state.json", env="STATE_FILE")

    log_level: str = Field("INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
