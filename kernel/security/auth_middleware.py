"""
FastAPI middleware pro JWT autentizaci a RBAC autorizaci
Integruje se s MSCA architekturou LONGIN EGO systému
"""

from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List, Dict, Callable, Any
import functools
import logging
from datetime import datetime, timezone
import json

from kernel.security.auth_manager import AuthManager, JWTPayload, get_auth_manager
from kernel.core.exceptions import AuthenticationError, AuthorizationError

logger = logging.getLogger(__name__)

security = HTTPBearer()

class AuthMiddleware:
    """
    Middleware pro zpracování JWT autentizace a RBAC autorizace
    Integruje se s existující MSCA architekturou
    """
    
    def __init__(self, auth_manager: Optional[AuthManager] = None):
        self.auth_manager = auth_manager
        self.security = HTTPBearer()
        
        # Konfigurace middleware
        self.excluded_paths = {
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/redoc"
        }
        
        # Caching pro často používané oprávnění
        self._permission_cache = {}
        self._cache_ttl = 60  # sekund
    
    async def __call__(self, request: Request, call_next):
        """Hlavní middleware logika"""
        
        # Kontrola vyjmutých cest
        if self._is_path_excluded(request.url.path):
            response = await call_next(request)
            return response
        
        # Získání auth manažera
        if not self.auth_manager:
            self.auth_manager = await get_auth_manager()
        
        try:
            # Extrakce tokenu
            token = await self._extract_token(request)
            if not token:
                raise HTTPException(status_code=401, detail="Chybí autentizační token")
            
            # Ověření tokenu
            payload = await self.auth_manager.verify_token(token)
            
            # Přidání uživatelských informací do requestu
            request.state.user = payload
            request.state.user_id = payload.user_id
            request.state.user_role = payload.role
            request.state.user_permissions = set(payload.permissions)
            request.state.session_id = payload.session_id
            
            # Logování přístupu
            await self._log_access(request, payload)
            
            response = await call_next(request)
            return response
            
        except AuthenticationError as e:
            logger.warning(f"Autentizační chyba pro {request.url.path}: {str(e)}")
            raise HTTPException(status_code=401, detail=str(e))
        except AuthorizationError as e:
            logger.warning(f"Autorizační chyba pro {request.url.path}: {str(e)}")
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            logger.error(f"Neočekávaná chyba v auth middleware: {str(e)}")
            raise HTTPException(status_code=500, detail="Interní chyba autentizace")
    
    def _is_path_excluded(self, path: str) -> bool:
        """Kontrola zda cesta není vyjmuta z autentizace"""
        # Přesná shoda
        if path in self.excluded_paths:
            return True
        
        # Prefix shoda
        for excluded_path in self.excluded_paths:
            if path.startswith(excluded_path):
                return True
        
        return False
    
    async def _extract_token(self, request: Request) -> Optional[str]:
        """Extrakce JWT tokenu z requestu"""
        # Pokus o získání z Authorization headeru
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]  # Odstranění "Bearer "
        
        # Alternativně z query parametru (pro WebSocket)
        token_param = request.query_params.get("token")
        if token_param:
            return token_param
        
        # Z WebSocket headers
        if hasattr(request, 'headers') and 'sec-websocket-protocol' in request.headers:
            protocols = request.headers['sec-websocket-protocol'].split(',')
            for protocol in protocols:
                if protocol.strip().startswith('bearer.'):
                    return protocol.strip()[7:]  # Odstranění "bearer."
        
        return None
    
    async def _log_access(self, request: Request, payload: JWTPayload):
        """Logování přístupu pro audit"""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": payload.user_id,
            "username": payload.username,
            "role": payload.role,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "session_id": payload.session_id,
            "ip_address": self._get_client_ip(request)
        }
        
        logger.info(f"API Access: {json.dumps(log_data, ensure_ascii=False)}")

    def _get_client_ip(self, request: Request) -> str:
        """Získání IP adresy klienta"""
        # Kontrola X-Forwarded-For headeru
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback na přímou adresu
        if hasattr(request.client, 'host'):
            return request.client.host
        
        return "unknown"


def require_auth(permissions: Optional[List[str]] = None, roles: Optional[List[str]] = None):
    """
    Dekorátor pro endpointy vyžadující autentizaci a autorizaci
    
    Args:
        permissions: Seznam požadovaných oprávnění (OR logika)
        roles: Seznam povolených rolí (OR logika)
    
    Returns:
        Dependency function pro FastAPI
    """
    
    async def auth_dependency(request: Request) -> JWTPayload:
        # Získání uživatele z requestu (nastaveno middleware)
        if not hasattr(request.state, 'user'):
            raise HTTPException(status_code=401, detail="Chybí autentizace")
        
        payload = request.state.user
        
        # Kontrola rolí
        if roles:
            if payload.role not in roles:
                raise HTTPException(
                    status_code=403, 
                    detail=f"Požadovaná role: {', '.join(roles)}"
                )
        
        # Kontrola oprávnění
        if permissions:
            user_permissions = set(payload.permissions)
            has_permission = False
            
            for required_permission in permissions:
                # Kontrola přesné shody
                if required_permission in user_permissions:
                    has_permission = True
                    break
                
                # Kontrola wildcard oprávnění
                if "*" in user_permissions:
                    has_permission = True
                    break
                
                # Kontrola prefixové shody (např. "system.*")
                if required_permission.endswith(".*"):
                    prefix = required_permission[:-2]
                    if any(perm.startswith(prefix) for perm in user_permissions):
                        has_permission = True
                        break
            
            if not has_permission:
                raise HTTPException(
                    status_code=403,
                    detail=f"Chybí požadovaná oprávnění: {', '.join(permissions)}"
                )
        
        return payload
    
    return Depends(auth_dependency)


def require_permission(permission: str):
    """
    Pomocná funkce pro vyžadování konkrétního oprávnění
    
    Args:
        permission: Požadované oprávnění (např. "system.status.read")
    
    Returns:
        Dependency function
    """
    return require_auth(permissions=[permission])


def require_role(role: str):
    """
    Pomocná funkce pro vyžadování konkrétní role
    
    Args:
        role: Požadovaná role (např. "admin")
    
    Returns:
        Dependency function
    """
    return require_auth(roles=[role])


class PermissionChecker:
    """
    Třída pro pokročilou kontrolu oprávnění s cachingem a audit logem
    """
    
    def __init__(self, auth_manager: AuthManager):
        self.auth_manager = auth_manager
        self._cache = {}
        self._cache_stats = {"hits": 0, "misses": 0}
    
    async def check_permission(self, user_id: str, permission: str, resource_id: Optional[str] = None) -> bool:
        """
        Kontrola oprávnění s podporou resource-based autorizace
        
        Args:
            user_id: ID uživatele
            permission: Požadované oprávnění
            resource_id: ID zdroje (pro resource-based autorizaci)
        
        Returns:
            True pokud má uživatel oprávnění, jinak False
        """
        # Cache klíč
        cache_key = f"{user_id}:{permission}:{resource_id or 'global'}"
        
        # Kontrola cache
        if cache_key in self._cache:
            cached_result, timestamp = self._cache[cache_key]
            if datetime.now(timezone.utc).timestamp() - timestamp < 60:  # 60 sekund cache
                self._cache_stats["hits"] += 1
                return cached_result
        
        self._cache_stats["misses"] += 1
        
        # Základní kontrola oprávnění
        has_permission = await self.auth_manager.authorize_action(user_id, permission)
        
        # Resource-based autorizace (pokud je specifikován resource_id)
        if has_permission and resource_id:
            # TODO: Implementovat resource-based autorizaci
            # Např. kontrola vlastnictví zdroje, týmových oprávnění atd.
            pass
        
        # Uložení do cache
        self._cache[cache_key] = (has_permission, datetime.now(timezone.utc).timestamp())
        
        return has_permission
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Získání statistik cache"""
        return self._cache_stats.copy()
    
    def clear_cache(self):
        """Vyčištění cache"""
        self._cache.clear()
        self._cache_stats = {"hits": 0, "misses": 0}


# Globální instance
_auth_middleware: Optional[AuthMiddleware] = None
_permission_checker: Optional[PermissionChecker] = None


async def get_auth_middleware() -> AuthMiddleware:
    """Získání singleton instance AuthMiddleware"""
    global _auth_middleware
    
    if _auth_middleware is None:
        auth_manager = await get_auth_manager()
        _auth_middleware = AuthMiddleware(auth_manager)
    
    return _auth_middleware


async def get_permission_checker() -> PermissionChecker:
    """Získání singleton instance PermissionChecker"""
    global _permission_checker
    
    if _permission_checker is None:
        auth_manager = await get_auth_manager()
        _permission_checker = PermissionChecker(auth_manager)
    
    return _permission_checker


# Pomocné funkce pro běžné použití
async def get_current_user(request: Request) -> JWTPayload:
    """Získání aktuálně přihlášeného uživatele"""
    if not hasattr(request.state, 'user'):
        raise HTTPException(status_code=401, detail="Uživatel není přihlášen")
    return request.state.user


async def get_current_user_id(request: Request) -> str:
    """Získání ID aktuálně přihlášeného uživatele"""
    user = await get_current_user(request)
    return user.user_id


def create_rate_limit_key(request: Request) -> str:
    """Vytvoření klíče pro rate limiting na základě uživatele a IP"""
    user_id = getattr(request.state, 'user_id', 'anonymous')
    ip_address = getattr(request.state, 'client_ip', 'unknown')
    return f"rate_limit:{user_id}:{ip_address}"


# Exporty pro použití v API
__all__ = [
    'AuthMiddleware',
    'require_auth',
    'require_permission', 
    'require_role',
    'PermissionChecker',
    'get_auth_middleware',
    'get_permission_checker',
    'get_current_user',
    'get_current_user_id',
    'create_rate_limit_key'
]