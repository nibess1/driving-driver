from typing import Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings
from pydantic import ConfigDict  # or: from pydantic import ConfigDict  in newer packaging


class Settings(BaseSettings):
    portal_user: str
    portal_pass: SecretStr
    portal_totp_secret: Optional[SecretStr] = None

    tg_bot_token: str
    tg_chat_id: str

    poll_min_seconds: int = 120
    poll_max_seconds: int = 240

    headless: bool = True
    enable_metrics: bool = True
    state_file: str = "./state.json"

    log_level: str = "INFO"

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
    )


settings = Settings()
