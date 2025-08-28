import os
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """Configuration for PostgreSQL database connection with pgvector support."""
    host: str = "localhost"
    port: int = 5432
    database: str = "research_memory"
    user: str = "postgres"
    password: str = ""
    sslmode: str = "prefer"
    
    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Create configuration from environment variables."""
        return cls(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "research_memory"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            sslmode=os.getenv("DB_SSLMODE", "prefer")
        )
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "DatabaseConfig":
        """Create configuration from dictionary."""
        return cls(**config_dict)
    
    def get_connection_string(self) -> str:
        """Generate PostgreSQL connection string."""
        return (
            f"postgresql://{self.user}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}"
            f"?sslmode={self.sslmode}"
        )
    
    def get_psycopg2_params(self) -> Dict[str, Any]:
        """Get parameters for psycopg2 connection."""
        return {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "user": self.user,
            "password": self.password,
            "sslmode": self.sslmode
        }


# Default configuration
DEFAULT_CONFIG = DatabaseConfig()
