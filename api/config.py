"""
Konfigurace pro LONGIN EGO API
Environment-based konfigurace s validací
"""

import os
from typing import Optional, List
from pydantic import BaseSettings, Field, validator
from enum import Enum


class Environment(Enum):
    """Prostředí aplikace"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class SecurityConfig(BaseSettings):
    """Bezpečnostní konfigurace"""
    
    # JWT konfigurace
    jwt_secret_key: str = Field(
        default_factory=lambda: os.urandom(64).hex(),
        description="Tajný klíč pro JWT podpisy"
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="Algoritmus pro JWT podpisy"
    )
    access_token_expire_minutes: int = Field(
        default=15,
        description="Platnost access tokenu v minutách"
    )
    refresh_token_expire_days: int = Field(
        default=7,
        description="Platnost refresh tokenu ve dnech"
    )
    
    # Bezpečnostní politiky
    password_min_length: int = Field(
        default=12,
        description="Minimální délka hesla"
    )
    max_login_attempts: int = Field(
        default=5,
        description="Maximální počet pokusů o přihlášení"
    )
    lockout_duration_minutes: int = Field(
        default=30,
        description="Doba zamčení účtu v minutách"
    )
    session_limit_per_user: int = Field(
        default=5,
        description="Maximální počet souběžných relací na uživatele"
    )
    
    # Rate limiting
    rate_limit_requests_per_minute: int = Field(
        default=100,
        description="Počet požadavků za minutu pro autentizované uživatele"
    )
    rate_limit_anonymous_requests_per_minute: int = Field(
        default=20,
        description="Počet požadavků za minutu pro anonymní uživatele"
    )
    
    # CORS konfigurace
    cors_allowed_origins: List[str] = Field(
        default=["*"],
        description="Povolené CORS originy"
    )
    cors_allowed_methods: List[str] = Field(
        default=["*"],
        description="Povolené HTTP metody"
    )
    cors_allowed_headers: List[str] = Field(
        default=["*"],
        description="Povolené hlavičky"
    )
    
    @validator('jwt_secret_key')
    def validate_jwt_secret(cls, v):
        """Validace JWT tajného klíče"""
        if len(v) < 32:
            raise ValueError("JWT tajný klíč musí mít alespoň 32 znaků")
        return v
    
    @validator('password_min_length')
    def validate_password_length(cls, v):
        """Validace minimální délky hesla"""
        if v < 8:
            raise ValueError("Minimální délka hesla musí být alespoň 8 znaků")
        return v


class RedisConfig(BaseSettings):
    """Redis konfigurace"""
    
    host: str = Field(
        default="localhost",
        description="Redis host"
    )
    port: int = Field(
        default=6379,
        description="Redis port"
    )
    db: int = Field(
        default=0,
        description="Redis databáze"
    )
    password: Optional[str] = Field(
        default=None,
        description="Redis heslo"
    )
    max_connections: int = Field(
        default=100,
        description="Maximální počet připojení"
    )
    socket_timeout: int = Field(
        default=5,
        description="Socket timeout v sekundách"
    )
    socket_connect_timeout: int = Field(
        default=5,
        description="Socket connect timeout v sekundách"
    )
    retry_on_timeout: bool = Field(
        default=True,
        description="Opakovat při timeoutu"
    )
    health_check_interval: int = Field(
        default=30,
        description="Interval health check v sekundách"
    )


class APIConfig(BaseSettings):
    """Hlavní API konfigurace"""
    
    # Základní konfigurace
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Prostředí aplikace"
    )
    debug: bool = Field(
        default=True,
        description="Debug mód"
    )
    
    # Server konfigurace
    host: str = Field(
        default="0.0.0.0",
        description="Host pro API server"
    )
    port: int = Field(
        default=8000,
        description="Port pro API server"
    )
    reload: bool = Field(
        default=True,
        description="Auto-reload při změnách (pouze pro vývoj)"
    )
    workers: int = Field(
        default=1,
        description="Počet worker procesů"
    )
    
    # Logování
    log_level: str = Field(
        default="info",
        description="Úroveň logování"
    )
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Formát log zpráv"
    )
    log_file: Optional[str] = Field(
        default=None,
        description="Soubor pro logování (None = stdout)"
    )
    
    # Bezpečnost
    trusted_hosts: List[str] = Field(
        default=["*"],
        description="Důvěryhodné hosty"
    )
    allowed_user_agents: List[str] = Field(
        default=["*"],
        description="Povolené User-Agent hlavičky"
    )
    
    # Výkon
    request_timeout: int = Field(
        default=30,
        description="Timeout pro requesty v sekundách"
    )
    max_request_size: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Maximální velikost requestu v bajtech"
    )
    
    # Integrace s LONGIN EGO
    ego_core_enabled: bool = Field(
        default=True,
        description="Povolit LONGIN EGO core funkce"
    )
    ego_scanner_enabled: bool = Field(
        default=True,
        description="Povolit LONGIN EGO scanner"
    )
    ego_orchestration_enabled: bool = Field(
        default=True,
        description="Povolit LONGIN EGO orchestraci"
    )
    
    # Validátory
    @validator('port')
    def validate_port(cls, v):
        """Validace portu"""
        if not (1 <= v <= 65535):
            raise ValueError("Port musí být mezi 1 a 65535")
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validace úrovně logování"""
        valid_levels = ['debug', 'info', 'warning', 'error', 'critical']
        if v.lower() not in valid_levels:
            raise ValueError(f"Log level musí být jeden z: {valid_levels}")
        return v.lower()
    
    @validator('workers')
    def validate_workers(cls, v):
        """Validace počtu workerů"""
        if v < 1:
            raise ValueError("Počet workerů musí být alespoň 1")
        return v


class Config(BaseSettings):
    """Hlavní konfigurační třída pro LONGIN EGO API"""
    
    # Podkonfigurace
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    
    # Environment proměnné
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        env_nested_delimiter = "__"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Override z environment proměnných
        self._load_from_environment()
    
    def _load_from_environment(self):
        """Načtení konfigurace z environment proměnných"""
        
        # Environment
        env_str = os.getenv("ENVIRONMENT", "development").lower()
        if env_str in ["dev", "development"]:
            self.api.environment = Environment.DEVELOPMENT
        elif env_str in ["staging", "stage"]:
            self.api.environment = Environment.STAGING
        elif env_str in ["prod", "production"]:
            self.api.environment = Environment.PRODUCTION
        elif env_str in ["test", "testing"]:
            self.api.environment = Environment.TESTING
        
        # Debug mód
        debug_str = os.getenv("DEBUG", "true").lower()
        self.api.debug = debug_str in ["true", "1", "yes", "on"]
        
        # Server konfigurace
        self.api.host = os.getenv("API_HOST", self.api.host)
        self.api.port = int(os.getenv("API_PORT", str(self.api.port)))
        self.api.reload = os.getenv("API_RELOAD", str(self.api.reload)).lower() == "true"
        self.api.workers = int(os.getenv("API_WORKERS", str(self.api.workers)))
        
        # Redis konfigurace
        self.redis.host = os.getenv("REDIS_HOST", self.redis.host)
        self.redis.port = int(os.getenv("REDIS_PORT", str(self.redis.port)))
        self.redis.db = int(os.getenv("REDIS_DB", str(self.redis.db)))
        self.redis.password = os.getenv("REDIS_PASSWORD", self.redis.password)
        
        # Security konfigurace
        self.security.jwt_secret_key = os.getenv("JWT_SECRET_KEY", self.security.jwt_secret_key)
        self.security.access_token_expire_minutes = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(self.security.access_token_expire_minutes))
        )
        self.security.refresh_token_expire_days = int(
            os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", str(self.security.refresh_token_expire_days))
        )
        
        # CORS
        cors_origins = os.getenv("CORS_ALLOWED_ORIGINS", "*")
        if cors_origins != "*":
            self.security.cors_allowed_origins = [origin.strip() for origin in cors_origins.split(",")]
        
        # Logování
        self.api.log_level = os.getenv("LOG_LEVEL", self.api.log_level)
        self.api.log_file = os.getenv("LOG_FILE", self.api.log_file)
        
        # LONGIN EGO specifické
        self.api.ego_core_enabled = os.getenv("EGO_CORE_ENABLED", "true").lower() == "true"
        self.api.ego_scanner_enabled = os.getenv("EGO_SCANNER_ENABLED", "true").lower() == "true"
        self.api.ego_orchestration_enabled = os.getenv("EGO_ORCHESTRATION_ENABLED", "true").lower() == "true"
    
    @property
    def is_development(self) -> bool:
        """Kontrola zda běžíme v development módu"""
        return self.api.environment == Environment.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        """Kontrola zda běžíme v production módu"""
        return self.api.environment == Environment.PRODUCTION
    
    @property
    def is_testing(self) -> bool:
        """Kontrola zda běžíme v testing módu"""
        return self.api.environment == Environment.TESTING
    
    def get_redis_url(self) -> str:
        """Vytvoření Redis URL"""
        if self.redis.password:
            return f"redis://:{self.redis.password}@{self.redis.host}:{self.redis.port}/{self.redis.db}"
        else:
            return f"redis://{self.redis.host}:{self.redis.port}/{self.redis.db}"
    
    def to_dict(self) -> dict:
        """Konverze konfigurace na slovník (bez citlivých dat)"""
        return {
            "environment": self.api.environment.value,
            "debug": self.api.debug,
            "host": self.api.host,
            "port": self.api.port,
            "redis_host": self.redis.host,
            "redis_port": self.redis.port,
            "redis_db": self.redis.db,
            "log_level": self.api.log_level,
            "ego_core_enabled": self.api.ego_core_enabled,
            "ego_scanner_enabled": self.api.ego_scanner_enabled,
            "ego_orchestration_enabled": self.api.ego_orchestration_enabled,
            "security": {
                "access_token_expire_minutes": self.security.access_token_expire_minutes,
                "refresh_token_expire_days": self.security.refresh_token_expire_days,
                "password_min_length": self.security.password_min_length,
                "max_login_attempts": self.security.max_login_attempts,
                "session_limit_per_user": self.security.session_limit_per_user,
                "rate_limit_requests_per_minute": self.security.rate_limit_requests_per_minute,
                "rate_limit_anonymous_requests_per_minute": self.security.rate_limit_anonymous_requests_per_minute,
                "cors_allowed_origins_count": len(self.security.cors_allowed_origins)
            }
        }


# Singleton instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Získání singleton instance konfigurace"""
    global _config
    
    if _config is None:
        _config = Config()
    
    return _config


# Export pro použití
__all__ = ['Config', 'SecurityConfig', 'RedisConfig', 'APIConfig', 'Environment', 'get_config']