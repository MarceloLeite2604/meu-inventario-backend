# type: ignore[call-arg]
import os
from typing import Annotated, Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

_ENVIRONMENT = os.getenv("ENVIRONMENT", "dev-native")


def _parse_comma_delimited_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [part.strip()
                for part
                in value.split(",")
                if part.strip()]

    raise ValueError("Invalid format for list.")


class KeycloakSettings(BaseSettings):

    server_url: str

    client_id: str

    client_secret_key: str

    realm: str

    model_config = SettingsConfigDict(
        env_prefix="MNZ_MI_KEYCLOAK_",
        env_file=[".env", f".env.{_ENVIRONMENT}"],
        extra="ignore"
    )


class CorsSettings(BaseSettings):

    allowed_origins: Annotated[list[str], NoDecode]

    allowed_methods: Annotated[list[str], NoDecode]

    allowed_headers: Annotated[list[str], NoDecode]

    model_config = SettingsConfigDict(
        env_prefix="MNZ_MI_CORS_",
        env_file=[".env", f".env.{_ENVIRONMENT}"],
        extra="ignore"
    )

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def _parse_allowed_origins(cls, value: Any) -> list[str]:
        return _parse_comma_delimited_list(value)

    @field_validator("allowed_methods", mode="before")
    @classmethod
    def _parse_allowed_methods(cls, value: Any) -> list[str]:
        return _parse_comma_delimited_list(value)

    @field_validator("allowed_headers", mode="before")
    @classmethod
    def _parse_allowed_headers(cls, value: Any) -> list[str]:
        return _parse_comma_delimited_list(value)


class SmtpSettings(BaseSettings):

    host: str

    port: int

    username: str

    password: str

    sender: str

    model_config = SettingsConfigDict(
        env_prefix="MNZ_MI_SMTP_",
        env_file=[".env", f".env.{_ENVIRONMENT}"],
        extra="ignore"
    )


class Settings(BaseSettings):

    host: str

    port: int

    database_url: str

    remote_debug: bool = False

    wait_debugger: bool = False

    keycloak: KeycloakSettings = Field(default_factory=KeycloakSettings)

    cors: CorsSettings = Field(default_factory=CorsSettings)

    smtp: SmtpSettings = Field(default_factory=SmtpSettings)

    model_config = SettingsConfigDict(
        env_prefix="MNZ_MI_",
        env_file=[".env", f".env.{_ENVIRONMENT}"],
        extra="ignore"
    )


settings = Settings()
