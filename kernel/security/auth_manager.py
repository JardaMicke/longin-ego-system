"""
Autentizační manažer pro LONGIN EGO systém
Implementuje JWT autentizaci, RBAC a bezpečnostní politiky v souladu s MSCA architekturou
"""

import jwt
import bcrypt
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, List, Set
from dataclasses import dataclass
from enum import Enum
import redis.asyncio as redis
import json
import logging
from kernel.core.exceptions import SecurityError, AuthenticationError, AuthorizationError

logger = logging.getLogger(__name__)

class UserRole(Enum):
    """Definice uživatelských rolí podle principů nejmenších privilegií"""
    GUEST = "guest"          # Pouze čtení základních informací
    USER = "user"            # Běžný uživatel s omezeným přístupem
    DEVELOPER = "developer"  # Vývojář s přístupem k vývojovým nástrojům
    ADMIN = "admin"          # Administrátor s plným přístupem
    SYSTEM = "system"        # Systémový účet pro interní procesy

@dataclass
class User:
    """Uživatelský účet s RBAC oprávněními"""
    user_id: str
    username: str
    email: str
    role: UserRole
    permissions: Set[str]
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    mfa_enabled: bool = False
    session_limit: int = 5  # Maximální počet souběžných relací

@dataclass
class JWTPayload:
    """JWT payload struktura pro LONGIN EGO"""
    user_id: str
    username: str
    role: str
    permissions: List[str]
    session_id: str
    iat: int  # Issued at
    exp: int  # Expiration
    nbf: int  # Not before
    jti: str  # JWT ID
    scope: str  # OAuth2 scope
    client_id: Optional[str] = None
    device_id: Optional[str] = None

class AuthManager:
    """
    Hlavní autentizační manažer pro LONGIN EGO
    Implementuje JWT autentizaci s RBAC a pokročilými bezpečnostními funkcemi
    """
    
    def __init__(self, redis_client: redis.Redis, secret_key: Optional[str] = None):
        self.redis = redis_client
        self.secret_key = secret_key or secrets.token_urlsafe(64)
        self.algorithm = "HS256"
        
        # Konfigurace tokenů
        self.access_token_expire_minutes = 15
        self.refresh_token_expire_days = 7
        self.refresh_token_cleanup_interval = 3600  # 1 hodina
        
        # Bezpečnostní politiky
        self.max_login_attempts = 5
        self.lockout_duration_minutes = 30
        self.password_min_length = 12
        self.require_mfa_for_roles = {UserRole.ADMIN, UserRole.SYSTEM}
        
        # Inicializace role-based permissions
        self.role_permissions = {
            UserRole.GUEST: {
                "system.status.read",
                "system.metrics.read",
                "ui.basic.read"
            },
            UserRole.USER: {
                "system.status.read",
                "system.metrics.read", 
                "ui.basic.read",
                "ui.advanced.read",
                "memory.short_term.read",
                "memory.long_term.read",
                "scanner.basic.use",
                "reports.basic.generate"
            },
            UserRole.DEVELOPER: {
                "system.status.read",
                "system.metrics.read",
                "ui.basic.read",
                "ui.advanced.read",
                "ui.developer.read",
                "memory.short_term.read",
                "memory.long_term.read",
                "memory.short_term.write",
                "scanner.basic.use",
                "scanner.advanced.use",
                "code.repository.read",
                "code.repository.write",
                "tests.run",
                "tests.create",
                "reports.detailed.generate",
                "ertdsd.meeting.use",
                "ertdsd.architect.use",
                "ertdsd.grind.use",
                "ertdsd.presentation.use"
            },
            UserRole.ADMIN: {
                "*"  # Všechna oprávnění
            },
            UserRole.SYSTEM: {
                "system.internal.*",  # Pouze interní systémová oprávnění
                "memory.*",
                "orchestration.*",
                "security.*"
            }
        }
        
        # Uživatelská databáze (v produkci nahradit skutečnou databází)
        self._users_db: Dict[str, User] = {}
        self._init_default_users()
    
    def _init_default_users(self):
        """Inicializace výchozích uživatelů pro vývoj"""
        # Výchozí systémový uživatel
        system_user = User(
            user_id="system_001",
            username="system",
            email="system@longin-ego.local",
            role=UserRole.SYSTEM,
            permissions=self._get_role_permissions(UserRole.SYSTEM),
            created_at=datetime.now(timezone.utc),
            is_active=True
        )
        
        # Výchozí administrátor
        admin_user = User(
            user_id="admin_001", 
            username="admin",
            email="admin@longin-ego.local",
            role=UserRole.ADMIN,
            permissions=self._get_role_permissions(UserRole.ADMIN),
            created_at=datetime.now(timezone.utc),
            is_active=True
        )
        
        self._users_db["system_001"] = system_user
        self._users_db["admin_001"] = admin_user
    
    def _get_role_permissions(self, role: UserRole) -> Set[str]:
        """Získání oprávnění pro danou roli"""
        return self.role_permissions.get(role, set())
    
    def _has_permission(self, user_permissions: Set[str], required_permission: str) -> bool:
        """Kontrola oprávnění s podporou wildcard"""
        if "*" in user_permissions:
            return True
        
        if required_permission in user_permissions:
            return True
        
        # Kontrola wildcard oprávnění
        parts = required_permission.split(".")
        for i in range(len(parts)):
            wildcard_perm = ".".join(parts[:i+1]) + ".*"
            if wildcard_perm in user_permissions:
                return True
        
        return False
    
    async def create_user(self, username: str, email: str, password: str, role: UserRole) -> User:
        """Vytvoření nového uživatele"""
        if len(password) < self.password_min_length:
            raise SecurityError(f"Heslo musí mít minimálně {self.password_min_length} znaků")
        
        # Kontrola duplicity
        for existing_user in self._users_db.values():
            if existing_user.username == username or existing_user.email == email:
                raise SecurityError("Uživatel s tímto jménem nebo emailem již existuje")
        
        # Hash hesla
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user_id = f"user_{secrets.token_hex(8)}"
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            role=role,
            permissions=self._get_role_permissions(role),
            created_at=datetime.now(timezone.utc),
            is_active=True,
            mfa_enabled=role in self.require_mfa_for_roles
        )
        
        # Uložení hesla do Redis (v produkci do databáze)
        await self.redis.setex(
            f"user_password:{user_id}",
            60 * 60 * 24 * 365,  # 1 rok
            password_hash.decode('utf-8')
        )
        
        self._users_db[user_id] = user
        logger.info(f"Vytvořen nový uživatel: {username} s rolí {role.value}")
        
        return user
    
    async def authenticate_user(self, username: str, password: str, device_id: Optional[str] = None) -> Dict[str, str]:
        """Autentizace uživatele a vytvoření tokenů"""
        
        # Najít uživatele
        user = None
        for u in self._users_db.values():
            if u.username == username and u.is_active:
                user = u
                break
        
        if not user:
            raise AuthenticationError("Neplatné přihlašovací údaje")
        
        # Kontrola pokusů o přihlášení
        lockout_key = f"login_lockout:{user.user_id}"
        lockout_count = await self.redis.get(lockout_key)
        
        if lockout_count and int(lockout_count) >= self.max_login_attempts:
            raise AuthenticationError(f"Účet je zamčený. Zkuste to znovu za {self.lockout_duration_minutes} minut.")
        
        # Ověření hesla
        stored_hash = await self.redis.get(f"user_password:{user.user_id}")
        if not stored_hash or not bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            # Zvýšení počtu neúspěšných pokusů
            await self.redis.incr(lockout_key)
            await self.redis.expire(lockout_key, self.lockout_duration_minutes * 60)
            
            raise AuthenticationError("Neplatné přihlašovací údaje")
        
        # Reset pokusů o přihlášení
        await self.redis.delete(lockout_key)
        
        # Aktualizace posledního přihlášení
        user.last_login = datetime.now(timezone.utc)
        
        # Kontrola limitu relací
        await self._check_session_limit(user)
        
        # Vytvoření session
        session_id = secrets.token_urlsafe(32)
        
        # Vytvoření tokenů
        access_token = await self._create_access_token(user, session_id, device_id)
        refresh_token = await self._create_refresh_token(user, session_id, device_id)
        
        # Uložení relace do Redis
        session_data = {
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role.value,
            "device_id": device_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_activity": datetime.now(timezone.utc).isoformat()
        }
        
        await self.redis.setex(
            f"session:{session_id}",
            self.refresh_token_expire_days * 24 * 60 * 60,
            json.dumps(session_data)
        )
        
        # Aktualizace aktivních relací uživatele
        await self.redis.sadd(f"user_sessions:{user.user_id}", session_id)
        
        logger.info(f"Úspěšná autentizace uživatele: {username}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": self.access_token_expire_minutes * 60,
            "session_id": session_id
        }
    
    async def _check_session_limit(self, user: User):
        """Kontrola limitu souběžných relací"""
        active_sessions = await self.redis.scard(f"user_sessions:{user.user_id}")
        
        if active_sessions >= user.session_limit:
            # Získání nejstarší relace a její ukončení
            session_ids = await self.redis.smembers(f"user_sessions:{user.user_id}")
            
            # Najít nejstarší relaci podle dat
            oldest_session = None
            oldest_time = None
            
            for session_id in session_ids:
                session_data = await self.redis.get(f"session:{session_id}")
                if session_data:
                    data = json.loads(session_data)
                    created_at = datetime.fromisoformat(data["created_at"])
                    
                    if oldest_time is None or created_at < oldest_time:
                        oldest_time = created_at
                        oldest_session = session_id
            
            if oldest_session:
                await self._revoke_session(oldest_session)
                logger.info(f"Ukončena nejstarší relace uživatele {user.username} kvůli limitu")
    
    async def _create_access_token(self, user: User, session_id: str, device_id: Optional[str] = None) -> str:
        """Vytvoření access JWT tokenu"""
        now = datetime.now(timezone.utc)
        
        payload = JWTPayload(
            user_id=user.user_id,
            username=user.username,
            role=user.role.value,
            permissions=list(user.permissions),
            session_id=session_id,
            iat=int(now.timestamp()),
            exp=int((now + timedelta(minutes=self.access_token_expire_minutes)).timestamp()),
            nbf=int(now.timestamp()),
            jti=secrets.token_urlsafe(16),
            scope=self._get_oauth_scope(user.role),
            device_id=device_id
        )
        
        return jwt.encode(payload.__dict__, self.secret_key, algorithm=self.algorithm)
    
    async def _create_refresh_token(self, user: User, session_id: str, device_id: Optional[str] = None) -> str:
        """Vytvoření refresh JWT tokenu"""
        now = datetime.now(timezone.utc)
        
        payload = {
            "user_id": user.user_id,
            "session_id": session_id,
            "device_id": device_id,
            "type": "refresh",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(days=self.refresh_token_expire_days)).timestamp()),
            "jti": secrets.token_urlsafe(16)
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        # Uložení refresh tokenu pro možnost revoke
        await self.redis.setex(
            f"refresh_token:{payload['jti']}",
            self.refresh_token_expire_days * 24 * 60 * 60,
            json.dumps({
                "user_id": user.user_id,
                "session_id": session_id,
                "created_at": now.isoformat()
            })
        )
        
        return token
    
    def _get_oauth_scope(self, role: UserRole) -> str:
        """Získání OAuth2 scope pro roli"""
        scope_map = {
            UserRole.GUEST: "read:basic",
            UserRole.USER: "read:basic read:advanced write:basic",
            UserRole.DEVELOPER: "read:basic read:advanced read:developer write:basic write:advanced write:developer",
            UserRole.ADMIN: "read:* write:* admin:*",
            UserRole.SYSTEM: "system:*"
        }
        return scope_map.get(role, "read:basic")
    
    async def verify_token(self, token: str) -> JWTPayload:
        """Ověření JWT tokenu"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Kontrola typu tokenu
            if payload.get("type") == "refresh":
                raise AuthenticationError("Použit refresh token místo access tokenu")
            
            # Kontrola existence session
            session_data = await self.redis.get(f"session:{payload['session_id']}")
            if not session_data:
                raise AuthenticationError("Relace neexistuje nebo vypršela")
            
            # Aktualizace aktivity relace
            session_info = json.loads(session_data)
            session_info["last_activity"] = datetime.now(timezone.utc).isoformat()
            await self.redis.setex(
                f"session:{payload['session_id']}",
                self.refresh_token_expire_days * 24 * 60 * 60,
                json.dumps(session_info)
            )
            
            return JWTPayload(**payload)
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token vypršel")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Neplatný token: {str(e)}")
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """Obnovení access tokenu pomocí refresh tokenu"""
        try:
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get("type") != "refresh":
                raise AuthenticationError("Neplatný typ tokenu")
            
            # Kontrola existence refresh tokenu
            token_info = await self.redis.get(f"refresh_token:{payload['jti']}")
            if not token_info:
                raise AuthenticationError("Refresh token neexistuje nebo byl odvolán")
            
            # Najít uživatele
            user = self._users_db.get(payload["user_id"])
            if not user or not user.is_active:
                raise AuthenticationError("Uživatel neexistuje nebo je deaktivován")
            
            # Vytvoření nového access tokenu
            access_token = await self._create_access_token(
                user, 
                payload["session_id"], 
                payload.get("device_id")
            )
            
            logger.info(f"Obnoven access token pro uživatele {user.username}")
            
            return {
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": self.access_token_expire_minutes * 60
            }
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Refresh token vypršel")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Neplatný refresh token: {str(e)}")
    
    async def authorize_action(self, user_id: str, required_permission: str) -> bool:
        """Autorizace akce pro uživatele"""
        user = self._users_db.get(user_id)
        if not user or not user.is_active:
            return False
        
        return self._has_permission(user.permissions, required_permission)
    
    async def authorize_token_action(self, token: str, required_permission: str) -> JWTPayload:
        """Autorizace akce pomocí JWT tokenu"""
        payload = await self.verify_token(token)
        
        user = self._users_db.get(payload.user_id)
        if not user or not user.is_active:
            raise AuthorizationError("Uživatel není aktivní")
        
        if not self._has_permission(set(payload.permissions), required_permission):
            raise AuthorizationError(f"Chybí oprávnění: {required_permission}")
        
        return payload
    
    async def revoke_session(self, session_id: str) -> bool:
        """Odvolání relace"""
        session_data = await self.redis.get(f"session:{session_id}")
        if not session_data:
            return False
        
        session_info = json.loads(session_data)
        user_id = session_info["user_id"]
        
        # Odstranění relace
        await self.redis.delete(f"session:{session_id}")
        await self.redis.srem(f"user_sessions:{user_id}", session_id)
        
        # Odvolání všech refresh tokenů pro tuto relaci
        # TODO: Implementovat efektivnější vyhledávání refresh tokenů
        
        logger.info(f"Relace {session_id} byla odvolána pro uživatele {session_info['username']}")
        return True
    
    async def revoke_all_user_sessions(self, user_id: str) -> int:
        """Odvolání všech relací uživatele"""
        session_ids = await self.redis.smembers(f"user_sessions:{user_id}")
        revoked_count = 0
        
        for session_id in session_ids:
            if await self.revoke_session(session_id):
                revoked_count += 1
        
        logger.info(f"Odvoláno {revoked_count} relací pro uživatele {user_id}")
        return revoked_count
    
    async def cleanup_expired_sessions(self) -> int:
        """Vyčištění vypršelých relací"""
        # Tato metoda by měla být volána periodicky
        # Prozatím implementováno jednoduše přes Redis TTL
        logger.info("Vyčištění vypršelých relací dokončeno (přes Redis TTL)")
        return 0
    
    async def get_user_sessions(self, user_id: str) -> List[Dict]:
        """Získání aktivních relací uživatele"""
        session_ids = await self.redis.smembers(f"user_sessions:{user_id}")
        sessions = []
        
        for session_id in session_ids:
            session_data = await self.redis.get(f"session:{session_id}")
            if session_data:
                sessions.append(json.loads(session_data))
        
        return sessions
    
    def get_required_permissions(self, resource: str, action: str) -> str:
        """Získání požadovaného oprávnění pro daný zdroj a akci"""
        return f"{resource}.{action}"

# Singleton instance
_auth_manager: Optional[AuthManager] = None

async def get_auth_manager(redis_client: Optional[redis.Redis] = None) -> AuthManager:
    """Získání singleton instance AuthManager"""
    global _auth_manager
    
    if _auth_manager is None:
        if redis_client is None:
            redis_client = redis.Redis(host='localhost', port=6379, db=0)
        _auth_manager = AuthManager(redis_client)
    
    return _auth_manager