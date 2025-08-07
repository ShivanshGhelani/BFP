from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    # MongoDB Configuration
    mongodb_url: str = Field(..., env="MONGODB_URL")
    mongodb_database: str = Field(..., env="MONGODB_DATABASE")
    
    # Redis Configuration
    redis_url: str = Field("redis://localhost:6379", env="REDIS_URL")
    redis_cache_ttl: int = Field(3600, env="REDIS_CACHE_TTL")  # 1 hour default
    
    # API Configuration
    api_base_url1: str = Field(..., env="API_BASE_URL1")
    api_base_url2: str = Field("", env="API_BASE_URL2")
    api_version: str = Field("v1", env="API_VERSION")
    cors_origins: List[str] = Field(
        ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"], 
        env="CORS_ORIGINS"
    )
    
    # Security Settings
    secret_key: str = Field(..., env="SECRET_KEY")
    allowed_hosts: List[str] = Field(
        ["localhost", "127.0.0.1", "0.0.0.0"], 
        env="ALLOWED_HOSTS"
    )
    
    # Development Settings
    debug: bool = Field(True, env="DEBUG")
    log_level: str = Field("info", env="LOG_LEVEL")
    
    # Rate Limiting
    rate_limit_requests: int = Field(100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(3600, env="RATE_LIMIT_WINDOW")
    
    # Data Retention
    data_retention_days: int = Field(30, env="DATA_RETENTION_DAYS")
    anonymize_after_days: int = Field(7, env="ANONYMIZE_AFTER_DAYS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Create a global settings instance
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
