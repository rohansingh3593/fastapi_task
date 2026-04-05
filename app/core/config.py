"""Environment configuration management for Konsole UI application"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # MongoDB Configuration
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "konsole_db"
    mongodb_max_pool_size: int = 50
    
    # Kubernetes Configuration
    kube_context: str = "default"
    kube_namespace: str = "default"
    kubeconfig: str = ""
    demo_mode: bool = True
    
    # FastAPI Configuration
    debug: bool = False
    log_level: str = "info"
    
    # Server Configuration
    server_port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
