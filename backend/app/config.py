from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List, Optional

class Settings(BaseSettings):
    # Supabase Configuration (now optional for CSV backend using Postgres)
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_key: Optional[str] = None
    
    # Shared PostgreSQL Database Configuration (replaces Supabase for multi-backend setup)
    database_url: Optional[str] = None  # Connection string: postgresql://user:password@database:5432/Suzlon_Backend
    db_host: str = "database"  # Use 'database' for Docker, localhost for local dev
    db_port: int = 5432
    db_name: str = "Suzlon_Backend"
    db_user: str = "suzlon_user"
    db_password: str = "suzlon_password"
    db_pool_size: int = 10
    db_max_overflow: int = 20

    # Application Configuration
    app_name: str = "CSV Upload and Knowledge Base API"
    app_version: str = "2.0.0"
    debug: bool = False

    # File Upload Configuration
    max_file_size: int = 200 * 1024 * 1024  # 200MB
    allowed_extensions: List[str] = [".csv"]

    # LLM Configuration
    groq_api_key: str
    groq_model: str = "llama-3.1-8b-instant"
    groq_base_url: str = "https://api.groq.com/openai/v1/chat/completions"
    groq_temperature: float = 0.3
    groq_max_tokens: int = 2000

    # JWT Configuration
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # ✅ Pydantic v2 config
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="allow",
    )
    
    def get_database_url(self) -> str:
        """Get database connection URL"""
        if self.database_url:
            return self.database_url
        # Build from components
        if self.db_user and self.db_password:
            return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        else:
            raise ValueError("Either DATABASE_URL or DB_USER/DB_PASSWORD must be set")

settings = Settings()
