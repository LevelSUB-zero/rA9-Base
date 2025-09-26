"""
Configuration management for RA9.

This module provides centralized configuration management using Pydantic settings.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    """RA9 configuration settings."""
    
    # API Keys
    gemini_api_key: Optional[str] = Field(default=None, alias="GEMINI_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    
    # Model settings
    default_model: str = Field(default="gemini-pro", alias="RA9_DEFAULT_MODEL")
    max_tokens: int = Field(default=2048, alias="RA9_MAX_TOKENS")
    temperature: float = Field(default=0.7, alias="RA9_TEMPERATURE")
    
    # Memory settings
    memory_enabled: bool = Field(default=True, alias="RA9_MEMORY_ENABLED")
    memory_path: Path = Field(default_factory=lambda: Path("memory"), alias="RA9_MEMORY_PATH")
    max_memory_entries: int = Field(default=1000, alias="RA9_MAX_MEMORY_ENTRIES")
    
    # Agent settings
    max_iterations: int = Field(default=5, alias="RA9_MAX_ITERATIONS")
    default_mode: str = Field(default="concise", alias="RA9_DEFAULT_MODE")
    enable_reflection: bool = Field(default=True, alias="RA9_ENABLE_REFLECTION")
    
    # Logging settings
    log_level: str = Field(default="INFO", alias="RA9_LOG_LEVEL")
    log_file: Optional[Path] = Field(default=None, alias="RA9_LOG_FILE")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        alias="RA9_LOG_FORMAT"
    )
    
    # Performance settings
    timeout_seconds: int = Field(default=30, alias="RA9_TIMEOUT_SECONDS")
    max_concurrent_agents: int = Field(default=3, alias="RA9_MAX_CONCURRENT_AGENTS")
    
    # UI settings
    enable_cli: bool = Field(default=True, alias="RA9_ENABLE_CLI")
    enable_web_ui: bool = Field(default=False, alias="RA9_ENABLE_WEB_UI")
    web_port: int = Field(default=8000, alias="RA9_WEB_PORT")
    
    # Development settings
    debug: bool = Field(default=False, alias="RA9_DEBUG")
    dev_mode: bool = Field(default=False, alias="RA9_DEV_MODE")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }
        
    @field_validator("memory_path")
    @classmethod
    def create_memory_path(cls, v):
        """Ensure memory path exists."""
        v.mkdir(parents=True, exist_ok=True)
        return v
        
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
        
    @field_validator("default_mode")
    @classmethod
    def validate_mode(cls, v):
        """Validate default mode."""
        valid_modes = ["concise", "detailed", "creative", "analytical"]
        if v.lower() not in valid_modes:
            raise ValueError(f"Mode must be one of {valid_modes}")
        return v.lower()
    
    def get_api_key(self, provider: str) -> str:
        """Get API key for a specific provider."""
        key_map = {
            "gemini": self.gemini_api_key,
            "openai": self.openai_api_key,
        }
        
        key = key_map.get(provider.lower())
        if not key:
            raise ValueError(f"No API key found for provider: {provider}")
        return key
    
    def is_configured(self) -> bool:
        """Check if essential configuration is present."""
        return bool(self.gemini_api_key or self.openai_api_key)
    
    def get_memory_config(self) -> Dict[str, Any]:
        """Get memory configuration."""
        return {
            "enabled": self.memory_enabled,
            "path": str(self.memory_path),
            "max_entries": self.max_memory_entries,
        }
    
    def get_agent_config(self) -> Dict[str, Any]:
        """Get agent configuration."""
        return {
            "max_iterations": self.max_iterations,
            "default_mode": self.default_mode,
            "enable_reflection": self.enable_reflection,
            "max_concurrent": self.max_concurrent_agents,
        }


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config() -> Config:
    """Reload configuration from environment."""
    global _config
    _config = Config()
    return _config


def set_config(config: Config) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config