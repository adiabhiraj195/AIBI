"""
Configuration management for Multi-Agent Chatbot Copilot
Handles environment variables and application settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os

class AppSettings(BaseSettings):
    """Main application settings"""
    # App settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # Database settings - shared AIBI_Backend database
    db_host: str = Field(default="database", env="DB_HOST")  # Use 'database' for Docker, localhost for local dev
    db_port: int = Field(default=5432, env="DB_PORT")
    db_name: str = Field(default="AIBI_Backend", env="DB_NAME")
    db_user: Optional[str] = Field(default=None, env="DB_USER")
    db_password: Optional[str] = Field(default=None, env="DB_PASSWORD")
    db_ssl_mode: str = Field(default="disable", env="DB_SSL_MODE")  # disable in Docker, require in production
    
    # Redis settings
    redis_host: str = Field(default="redis", env="REDIS_HOST")  # Use 'redis' for Docker, localhost for local dev
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_user: Optional[str] = Field(default=None, env="REDIS_USER")
    
    # LLM settings
    # LLM settings
    llm_model: str = Field(default="llama-3.3-70b-versatile", env="LLM_MODEL")
    llm_api_key: Optional[str] = Field(default=None, env="LLM_API_KEY")
    llm_base_url: str = Field(default="https://api.groq.com/openai/v1", env="LLM_BASE_URL")
    llm_temperature: float = Field(default=0.1, env="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=2000, env="LLM_MAX_TOKENS")
    
    # RAG settings
    embedding_model: str = Field(default="sentence-transformers/all-mpnet-base-v2", env="EMBEDDING_MODEL")
    max_retrieval_docs: int = Field(default=10, env="MAX_RETRIEVAL_DOCS")
    similarity_threshold: float = Field(default=0.7, env="SIMILARITY_THRESHOLD")
    embedding_dimension: int = Field(default=768, env="EMBEDDING_DIMENSION")
    
    # Agent settings
    max_response_time: float = Field(default=5.0, env="MAX_RESPONSE_TIME")
    conversation_memory_limit: int = Field(default=10, env="CONVERSATION_MEMORY_LIMIT")
    follow_up_questions_count: int = Field(default=4, env="FOLLOW_UP_QUESTIONS_COUNT")
    retry_attempts: int = Field(default=3, env="RETRY_ATTEMPTS")
    
    # Security settings
    secret_key: Optional[str] = Field(default="dev-secret-key", env="SECRET_KEY")
    session_timeout: int = Field(default=3600, env="SESSION_TIMEOUT")
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=3600, env="RATE_LIMIT_WINDOW")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields in .env
    
    # Convenience properties for backward compatibility
    @property
    def database(self):
        """Database settings as object"""
        class DB:
            def __init__(self, settings):
                self.host = settings.db_host.strip()  # Remove any whitespace
                self.port = settings.db_port
                self.name = settings.db_name
                self.user = settings.db_user
                self.password = settings.db_password
                self.ssl_mode = settings.db_ssl_mode
            
            @property
            def url(self):
                if not self.user or not self.password:
                    return f"postgresql://localhost/{self.name}"
                return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}?sslmode={self.ssl_mode}"
        
        return DB(self)
    
    @property
    def redis(self):
        """Redis settings as object"""
        class Redis:
            def __init__(self, settings):
                self.host = settings.redis_host
                self.port = settings.redis_port
                self.db = settings.redis_db
                self.password = settings.redis_password
                self.user = settings.redis_user
            
            @property
            def url(self):
                if self.password:
                    if self.user:
                        return f"redis://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"
                    else:
                        return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
                return f"redis://{self.host}:{self.port}/{self.db}"
        
        return Redis(self)
    
    @property
    def llm(self):
        """LLM settings as object"""
        class LLM:
            def __init__(self, settings):
                self.model = settings.llm_model
                self.api_key = settings.llm_api_key
                self.base_url = settings.llm_base_url
                self.temperature = settings.llm_temperature
                self.max_tokens = settings.llm_max_tokens
        
        return LLM(self)
    
    @property
    def rag(self):
        """RAG settings as object"""
        class RAG:
            def __init__(self, settings):
                self.embedding_model = settings.embedding_model
                self.max_retrieval_docs = settings.max_retrieval_docs
                self.similarity_threshold = settings.similarity_threshold
                self.embedding_dimension = settings.embedding_dimension
        
        return RAG(self)
    
    @property
    def agents(self):
        """Agent settings as object"""
        class Agents:
            def __init__(self, settings):
                self.max_response_time = settings.max_response_time
                self.conversation_memory_limit = settings.conversation_memory_limit
                self.follow_up_questions_count = settings.follow_up_questions_count
                self.retry_attempts = settings.retry_attempts
        
        return Agents(self)
    
    @property
    def security(self):
        """Security settings as object"""
        class Security:
            def __init__(self, settings):
                self.secret_key = settings.secret_key
                self.session_timeout = settings.session_timeout
                self.rate_limit_requests = settings.rate_limit_requests
                self.rate_limit_window = settings.rate_limit_window
        
        return Security(self)

# Global settings instance
settings = AppSettings()

# Validate critical settings on import
def validate_settings():
    """Validate critical configuration settings"""
    required_settings = [
        (settings.database.user, "DB_USER"),
        (settings.database.password, "DB_PASSWORD"),
        (settings.llm.api_key, "LLM_API_KEY"),
        (settings.security.secret_key, "SECRET_KEY")
    ]
    
    missing_settings = []
    for value, name in required_settings:
        if not value:
            missing_settings.append(name)
    
    if missing_settings:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_settings)}")

# Only validate in production (not during development)
if os.getenv("ENVIRONMENT") == "production":
    validate_settings()