"""
Application settings for the prompt-clipboard application using Pydantic Settings.

This module provides a centralized configuration system with:
- Hierarchical settings structure
- Environment variable support
- Validation and type checking
- .env file support
- CLI argument support
"""

import os
from pathlib import Path

import appdirs
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine data directory
if os.path.exists("src/prompt_clipboard/data"):
    data_dir = Path("src/prompt_clipboard/data")
else:
    data_dir = Path(appdirs.user_data_dir("prompt-clipboard"))


class LoggingSettings(BaseModel):
    """Settings for logging configuration."""

    level: str = Field(default="INFO", description="Console log level")
    file_level: str = Field(default="INFO", description="File log level")
    dir: Path = Field(default=data_dir / "logs", description="Log directory")
    file: str = Field(default="prompt_clipboard.log", description="Main log filename")
    console_format: str = Field(
        default=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level> | "
            "{extra}"
        ),
        description="Console log format",
    )

    @field_validator("level", "file_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the standard levels."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return v.upper()

    @field_validator("dir")
    @classmethod
    def validate_log_dir(cls, v: Path) -> Path:
        """Ensure log directory exists."""
        v.mkdir(parents=True, exist_ok=True)
        return v


class DatabaseSettings(BaseModel):
    """Settings for database configuration."""

    path: Path = Field(
        default=data_dir / "prompt_clip.db", description="Database file path"
    )

    @field_validator("path")
    @classmethod
    def validate_db_path(cls, v: Path) -> Path:
        """Ensure database directory exists."""
        v.parent.mkdir(parents=True, exist_ok=True)
        return v


class AppSettings(BaseModel):
    """General application settings."""

    name: str = Field(default="prompt-clipboard", description="Application name")
    version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Enable debug mode")
    seed_prompt: str = Field(
        default="Summarize the following notes: {{notes}}",
        description="Default seed prompt when database is empty",
    )


class Settings(BaseSettings):
    """Main application settings with hierarchical configuration."""

    app: AppSettings = AppSettings()
    logging: LoggingSettings = LoggingSettings()
    database: DatabaseSettings = DatabaseSettings()

    model_config = SettingsConfigDict(
        env_prefix="PROMPT_CLIPBOARD__",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields from environment
    )

    @property
    def log_file_path(self) -> Path:
        """Get the full path to the main log file."""
        return self.logging.dir / self.logging.file


# Create global settings instance
settings = Settings()
