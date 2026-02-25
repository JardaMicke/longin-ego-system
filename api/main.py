"""
Hlavní FastAPI aplikace pro LONGIN EGO systém
Integruje všechny API endpointy s JWT autentizací a RBAC autorizací
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
import redis.asyncio as redis
from contextlib import asynccontextmanager
import os
from datetime import datetime

# Importy z LONGIN EGO
from kernel.security.auth_middleware import AuthMiddleware, get_auth_middleware
from kernel.security.auth_endpoints import router as auth_router
from kernel.core.exceptions import AuthenticationError, AuthorizationError, SecurityError
from api.config import Config
from api.scanner_endpoints import router as scanner_router
from api.dreaming_endpoints import initialize_dreaming_router

# Konfigurace logování
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Globální proměnné pro aplikaci
redis_client = None
auth_middleware = None
dreaming_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Správa životního cyklu aplikace
    """
    global redis_client, auth_middleware
    
    # Startup
    logger.info("=== LONGIN EGO API STARTUP ===")
    
    try:
        # Inicializace Redis připojení
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))
        redis_db = int(os.getenv("REDIS_DB", "0"))
        
        redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True
        )
        
        # Test připojení
        await redis_client.ping()
        logger.info(f"✓ Redis připojeno: {redis_host}:{redis_port}")
        
        # Inicializace auth middleware
        auth_middleware = await get_auth_middleware()
        logger.info("✓ Auth middleware inicializován")
        
        # Inicializace konfigurace
        config = Config()
        logger.info(f"✓ Konfigurace načtena: {config.environment}")
        
        # Inicializace Metrics Manageru (Advanced Monitoring)
        from kernel.monitoring.metrics_collector import get_metrics_manager
        metrics_manager = await get_metrics_manager(config, redis_client)
        await metrics_manager.start_collection()
        logger.info("✓ Advanced Metrics Collection spuštěno")
        
        # Inicializace Idle Dreaming Service
        global dreaming_service
        from kernel.cognition.dreaming_service import initialize_dreaming_system
        from memory.postgres.client import PostgresClient
        from kernel.bus.redis_bus import RedisBus
        
        # Vytvoření dependencies pro dreaming service
        postgres = PostgresClient(
            host=config.postgres_host,
            port=config.postgres_port,
            database=config.postgres_db,
            user=config.postgres_user,
            password=config.postgres_password
        )
        
        # metrics_manager již máme inicializovaný
        redis_bus = RedisBus(redis_client)
        
        # Inicializace dreaming service
        dreaming_config = {
            'idle_dreaming': {
                'enabled': True,
                'min_idle_time_seconds': 300,
                'max_session_duration_seconds': 1800,
                'cpu_threshold_percent': 20.0,
                'memory_threshold_percent': 30.0,
                'gpu_threshold_percent': 15.0,
                'cognitive_comfort_threshold': 0.7
            },
            'check_interval': 60
        }
        
        dreaming_service = await initialize_dreaming_system(
            config=dreaming_config,
            redis_client=redis_client,
            postgres=postgres,
            metrics_manager=metrics_manager,
            auth_manager=auth_middleware.auth_manager if auth_middleware else None,
            redis_bus=redis_bus
        )
        
        if dreaming_service:
            logger.info("✓ Idle Dreaming Service inicializován")
        else:
            logger.warning("⚠ Idle Dreaming Service se nepodařilo inicializovat")
        
        logger.info("=== LONGIN EGO API PŘIPRAVENO ===")
        
    except Exception as e:
        logger.error(f"✗ Chyba při startupu: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("=== LONGIN EGO API SHUTDOWN ===")
    
    try:
        # Zastavení sběru metrik
        from kernel.monitoring.metrics_collector import get_metrics_manager
        metrics_manager = await get_metrics_manager()
        await metrics_manager.stop_collection()
        logger.info("✓ Advanced Metrics Collection zastaveno")

        if redis_client:
            await redis_client.close()
            logger.info("✓ Redis uzavřeno")
        
        logger.info("=== LONGIN EGO API UKONČENO ===")
        
    except Exception as e:
        logger.error(f"✗ Chyba při shutdown: {str(e)}")


# Vytvoření FastAPI aplikace
app = FastAPI(
    title="LONGIN EGO API",
    description="""
    REST API pro LONGIN EGO - Suverénní digitální organismus
    
    ## Autentizace
    
    Toto API používá JWT (JSON Web Token) autentizaci. Pro přístup k chráněným endpointům:
    
    1. Získejte token pomocí `/auth/login`
    2. Vložte token do Authorization hlavičky: `Bearer <váš_token>`
    3. Token vyprší za 15 minut - použijte refresh token pro obnovení
    
    ## Role a oprávnění
    
    - **guest**: Minimální přístup, pouze čtení základních informací
    - **user**: Běžný uživatel s omezeným přístupem
    - **developer**: Vývojář s přístupem k vývojovým nástrojům
    - **admin**: Administrátor s plným přístupem
    - **system**: Systémový účet pro interní procesy
    
    ## Bezpečnost
    
    - Všechny endpointy jsou chráněné JWT autentizací (kromě `/auth/*`)
    - Rate limiting implementován na úrovni middleware
    - Audit log pro všechny přístupy
    - Session management s možností vzdáleného odhlášení
    """,
    version="8.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Middleware
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # V produkci specifikovat konkrétní domény
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # V produkci specifikovat konkrétní hosty
)

# Auth middleware (přidáno dynamicky v lifespan)


# Exception handlery
@app.exception_handler(AuthenticationError)
async def authentication_exception_handler(request: Request, exc: AuthenticationError):
    """Handler pro autentizační chyby"""
    return JSONResponse(
        status_code=401,
        content={
            "error": "authentication_failed",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(AuthorizationError)
async def authorization_exception_handler(request: Request, exc: AuthorizationError):
    """Handler pro autorizační chyby"""
    return JSONResponse(
        status_code=403,
        content={
            "error": "insufficient_permissions",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(SecurityError)
async def security_exception_handler(request: Request, exc: SecurityError):
    """Handler pro bezpečnostní chyby"""
    return JSONResponse(
        status_code=400,
        content={
            "error": "security_error",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Obecný handler pro neočekávané chyby"""
    logger.error(f"Neočekávaná chyba: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "Došlo k interní chybě serveru",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# API endpointy

@app.get("/")
async def root():
    """Root endpoint s informacemi o API"""
    return {
        "name": "LONGIN EGO API",
        "version": "8.0.0",
        "description": "Suverénní digitální organismus - REST API",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "auth": "/auth"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Kontrola Redis připojení
        if redis_client:
            await redis_client.ping()
            redis_status = "healthy"
        else:
            redis_status = "unhealthy"
        
        # Kontrola auth systému
        if auth_middleware:
            auth_status = "healthy"
        else:
            auth_status = "unhealthy"
        
        overall_status = "healthy" if redis_status == "healthy" and auth_status == "healthy" else "unhealthy"
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "redis": redis_status,
                "authentication": auth_status
            },
            "api": {
                "version": "8.0.0",
                "uptime": "unknown"  # TODO: Implementovat uptime tracking
            }
        }
        
    except Exception as e:
        logger.error(f"Health check selhal: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


@app.get("/system/status")
async def system_status():
    """Systémový status endpoint"""
    try:
        from kernel.monitoring.metrics_collector import get_metrics_manager
        metrics_manager = await get_metrics_manager()
        current_metrics = await metrics_manager.get_current_metrics()
        
        return {
            "status": "operational",
            "metrics": current_metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Systémový status selhal: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# Přidání auth routeru
app.include_router(auth_router)

# Přidání scanner routeru
app.include_router(scanner_router)

# Přidání dreaming routeru (pokud je služba inicializována)
if dreaming_service:
    dreaming_router = initialize_dreaming_router(dreaming_service)
    app.include_router(dreaming_router)
    logger.info("✓ Dreaming endpoints přidány")


# Middleware setup (provedeno po vytvoření app)
@app.middleware("http")
async def setup_auth_middleware(request: Request, call_next):
    """
    Middleware pro nastavení autentizace
    Toto je workaround pro správné inicializování auth middleware
    """
    global auth_middleware
    
    if auth_middleware is None:
        auth_middleware = await get_auth_middleware()
    
    # Pokud middleware není nastaven, použijeme ji přímo
    if auth_middleware:
        return await auth_middleware(request, call_next)
    else:
        response = await call_next(request)
        return response


# Middleware pro audit logging
@app.middleware("http")
async def audit_logging_middleware(request: Request, call_next):
    """Middleware pro audit logování všech požadavků"""
    
    start_time = datetime.utcnow()
    
    # Získání uživatelských informací
    user_id = getattr(request.state, 'user_id', 'anonymous')
    username = getattr(request.state, 'user', None)
    if username:
        username = username.username
    else:
        username = 'anonymous'
    
# Middleware pro audit logging
@app.middleware("http")
async def audit_logging_middleware(request: Request, call_next):
    """Middleware pro audit logování všech požadavků"""
    import time
    
    start_time = datetime.utcnow()
    start_ts = time.time()
    
    # Získání uživatelských informací
    user_id = getattr(request.state, 'user_id', 'anonymous')
    username = getattr(request.state, 'user', None)
    if username:
        username = username.username
    else:
        username = 'anonymous'
    
    # Provedení requestu
    response = await call_next(request)
    
    # Logování
    duration = time.time() - start_ts
    
    # Zaznamenání metriky do Metrics Managera
    try:
        from kernel.monitoring.metrics_collector import get_metrics_manager
        metrics_manager = await get_metrics_manager()
        await metrics_manager.record_request(
            request.method,
            request.url.path,
            response.status_code,
            duration
        )
    except Exception as e:
        # Metriky nesmí shodit request
        pass
    
    log_data = {
        "timestamp": start_time.isoformat(),
        "user_id": user_id,
        "username": username,
        "method": request.method,
        "path": request.url.path,
        "query_params": dict(request.query_params),
        "status_code": getattr(response, 'status_code', 0),
        "duration_ms": round(duration * 1000, 2),
        "user_agent": request.headers.get("user-agent", "unknown"),
        "ip_address": request.client.host if request.client else "unknown"
    }
    
    # Log pouze pro autentizované uživatele a důležité operace
    if user_id != 'anonymous' or request.method in ['POST', 'PUT', 'DELETE']:
        logger.info(f"API Audit: {json.dumps(log_data, ensure_ascii=False)}")
    
    return response


# Middleware pro rate limiting (základní implementace)
@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    """Základní rate limiting middleware"""
    
    # Vynechání rate limitingu pro vybrané cesty
    if request.url.path in ['/health', '/docs', '/redoc', '/openapi.json']:
        return await call_next(request)
    
    try:
        if redis_client:
            # Vytvoření klíče pro rate limiting
            user_id = getattr(request.state, 'user_id', 'anonymous')
            client_ip = request.client.host if request.client else 'unknown'
            
            rate_limit_key = f"rate_limit:{user_id}:{client_ip}"
            
            # Získání aktuálního počtu
            current_count = await redis_client.get(rate_limit_key)
            current_count = int(current_count) if current_count else 0
            
            # Limit: 100 požadavků za minutu pro autentizované, 20 pro anonymní
            limit = 100 if user_id != 'anonymous' else 20
            
            if current_count >= limit:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "rate_limit_exceeded",
                        "message": f"Překročen limit požadavků ({limit} za minutu)",
                        "retry_after": 60
                    }
                )
            
            # Inkrementace počítadla
            pipe = redis_client.pipeline()
            pipe.incr(rate_limit_key)
            pipe.expire(rate_limit_key, 60)  # 1 minuta
            await pipe.execute()
    
    except Exception as e:
        logger.warning(f"Rate limiting selhal: {str(e)}")
        # Nepřerušujeme request při selhání rate limitingu
    
    response = await call_next(request)
    return response


# Middleware pro bezpečnostní hlavičky
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Middleware pro přidání bezpečnostních hlaviček"""
    
    response = await call_next(request)
    
    # Bezpečnostní hlavičky
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # CORS hlavičky (pokud ještě nejsou nastaveny)
    if "Access-Control-Allow-Origin" not in response.headers:
        response.headers["Access-Control-Allow-Origin"] = "*"
    
    return response


# Spuštění aplikace
if __name__ == "__main__":
    # Načtení konfigurace
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"
    
    logger.info(f"Spouštím LONGIN EGO API na {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )