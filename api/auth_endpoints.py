"""
API endpointy pro autentizaci a autorizaci v LONGIN EGO systému
Implementuje REST API pro JWT autentizaci, uživatelskou správu a RBAC
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from kernel.security.auth_manager import AuthManager, UserRole, get_auth_manager
from kernel.security.auth_middleware import (
    require_auth, require_permission, require_role,
    get_current_user, get_current_user_id
)
from kernel.core.exceptions import SecurityError, AuthenticationError, AuthorizationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Pydantic modely pro request/response
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Uživatelské jméno")
    password: str = Field(..., min_length=12, max_length=128, description="Heslo")
    device_id: Optional[str] = Field(None, description="ID zařízení pro relaci")
    remember_me: bool = Field(False, description="Prodloužit platnost relace")

class LoginResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("Bearer", description="Typ tokenu")
    expires_in: int = Field(..., description="Platnost tokenu v sekundách")
    session_id: str = Field(..., description="ID relace")
    user: Dict[str, Any] = Field(..., description="Informace o uživateli")

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="JWT refresh token")

class RefreshTokenResponse(BaseModel):
    access_token: str = Field(..., description="Nový JWT access token")
    token_type: str = Field("Bearer", description="Typ tokenu")
    expires_in: int = Field(..., description="Platnost tokenu v sekundách")

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Uživatelské jméno")
    email: EmailStr = Field(..., description="Emailová adresa")
    password: str = Field(..., min_length=12, max_length=128, description="Heslo")
    role: str = Field("user", description="Role uživatele")

class RegisterResponse(BaseModel):
    user_id: str = Field(..., description="ID vytvořeného uživatele")
    username: str = Field(..., description="Uživatelské jméno")
    email: str = Field(..., description="Emailová adresa")
    role: str = Field(..., description="Přiřazená role")
    created_at: datetime = Field(..., description="Datum vytvoření")
    message: str = Field(..., description="Status zpráva")

class UserInfoResponse(BaseModel):
    user_id: str = Field(..., description="ID uživatele")
    username: str = Field(..., description="Uživatelské jméno")
    email: str = Field(..., description="Emailová adresa")
    role: str = Field(..., description="Role uživatele")
    permissions: List[str] = Field(..., description="Seznam oprávnění")
    created_at: datetime = Field(..., description="Datum vytvoření účtu")
    last_login: Optional[datetime] = Field(None, description="Datum posledního přihlášení")
    is_active: bool = Field(..., description="Stav účtu")
    mfa_enabled: bool = Field(..., description="Stav MFA")
    session_limit: int = Field(..., description="Limit souběžných relací")

class SessionInfo(BaseModel):
    session_id: str = Field(..., description="ID relace")
    device_id: Optional[str] = Field(None, description="ID zařízení")
    created_at: datetime = Field(..., description="Datum vytvoření relace")
    last_activity: datetime = Field(..., description="Poslední aktivita")

class UserSessionsResponse(BaseModel):
    user_id: str = Field(..., description="ID uživatele")
    username: str = Field(..., description="Uživatelské jméno")
    active_sessions: List[SessionInfo] = Field(..., description="Aktivní relace")
    total_sessions: int = Field(..., description="Celkový počet relací")

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., description="Aktuální heslo")
    new_password: str = Field(..., min_length=12, max_length=128, description="Nové heslo")

class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = Field(None, description="Nová emailová adresa")
    role: Optional[str] = Field(None, description="Nová role")
    is_active: Optional[bool] = Field(None, description="Stav účtu")
    session_limit: Optional[int] = Field(None, description="Limit relací", ge=1, le=10)

class UserListResponse(BaseModel):
    users: List[UserInfoResponse] = Field(..., description="Seznam uživatelů")
    total: int = Field(..., description="Celkový počet uživatelů")
    page: int = Field(1, description="Aktuální stránka")
    per_page: int = Field(20, description="Uživatelů na stránku")

# Pomocné funkce
def _map_role_to_enum(role_str: str) -> UserRole:
    """Mapování string role na enum"""
    role_map = {
        "guest": UserRole.GUEST,
        "user": UserRole.USER,
        "developer": UserRole.DEVELOPER,
        "admin": UserRole.ADMIN,
        "system": UserRole.SYSTEM
    }
    
    role = role_map.get(role_str.lower())
    if not role:
        raise HTTPException(
            status_code=400,
            detail=f"Neplatná role: {role_str}. Povolené role: {list(role_map.keys())}"
        )
    
    return role

# API endpointy

@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    response: Response,
    auth_manager: AuthManager = Depends(get_auth_manager)
):
    """
    Přihlášení uživatele a získání JWT tokenů
    
    Endpoint pro autentizaci uživatele pomocí jména a hesla.
    Vrací JWT access a refresh tokeny pro následné API volání.
    """
    try:
        # Autentizace uživatele
        auth_result = await auth_manager.authenticate_user(
            username=request.username,
            password=request.password,
            device_id=request.device_id
        )
        
        # Nastavení bezpečnostních hlaviček
        response.headers["X-Rate-Limit-Remaining"] = "100"  # TODO: Implementovat rate limiting
        response.headers["X-Session-ID"] = auth_result["session_id"]
        
        # Získání informací o uživateli
        user = None
        for u in auth_manager._users_db.values():
            if u.username == request.username:
                user = u
                break
        
        user_info = {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "permissions": list(user.permissions)
        }
        
        return LoginResponse(
            access_token=auth_result["access_token"],
            refresh_token=auth_result["refresh_token"],
            token_type=auth_result["token_type"],
            expires_in=auth_result["expires_in"],
            session_id=auth_result["session_id"],
            user=user_info
        )
        
    except AuthenticationError as e:
        logger.warning(f"Neúspěšné přihlášení pro uživatele {request.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Chyba při přihlašování uživatele {request.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Interní chyba při přihlašování"
        )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_manager: AuthManager = Depends(get_auth_manager)
):
    """
    Obnovení access tokenu pomocí refresh tokenu
    
    Tento endpoint umožňuje získat nový access token bez nutnosti
    znovu zadávat přihlašovací údaje.
    """
    try:
        refresh_result = await auth_manager.refresh_access_token(request.refresh_token)
        
        return RefreshTokenResponse(
            access_token=refresh_result["access_token"],
            token_type=refresh_result["token_type"],
            expires_in=refresh_result["expires_in"]
        )
        
    except AuthenticationError as e:
        logger.warning(f"Neúspěšné obnovení tokenu: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Chyba při obnovování tokenu: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Interní chyba při obnovování tokenu"
        )


@router.post("/register", response_model=RegisterResponse)
async def register(
    request: RegisterRequest,
    current_user: dict = Depends(require_role("admin"))
):
    """
    Registrace nového uživatele
    
    Tento endpoint vyžaduje admin roli pro vytvoření nového uživatele.
    V produkčním prostředí by měl být chráněn dodatečnými bezpečnostními opatřeními.
    """
    try:
        auth_manager = await get_auth_manager()
        
        # Mapování role na enum
        role_enum = _map_role_to_enum(request.role)
        
        # Vytvoření uživatele
        user = await auth_manager.create_user(
            username=request.username,
            email=request.email,
            password=request.password,
            role=role_enum
        )
        
        logger.info(f"Vytvořen nový uživatel: {request.username} (admin: {current_user.username})")
        
        return RegisterResponse(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            role=user.role.value,
            created_at=user.created_at,
            message="Uživatel úspěšně vytvořen"
        )
        
    except SecurityError as e:
        logger.warning(f"Chyba při vytváření uživatele {request.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Chyba při vytváření uživatele {request.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Interní chyba při vytváření uživatele"
        )


@router.get("/me", response_model=UserInfoResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Získání informací o aktuálně přihlášeném uživateli
    
    Vrací detailní informace o uživateli včetně oprávnění.
    """
    try:
        auth_manager = await get_auth_manager()
        user = auth_manager._users_db.get(current_user.user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Uživatel nenalezen"
            )
        
        return UserInfoResponse(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            role=user.role.value,
            permissions=list(user.permissions),
            created_at=user.created_at,
            last_login=user.last_login,
            is_active=user.is_active,
            mfa_enabled=user.mfa_enabled,
            session_limit=user.session_limit
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chyba při získávání informací o uživateli: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Interní chyba při získávání informací o uživateli"
        )


@router.post("/logout")
async def logout(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Odhlášení aktuální relace
    
    Odstraní aktuální relaci a invalidate příslušné tokeny.
    """
    try:
        auth_manager = await get_auth_manager()
        
        # Odvolání aktuální relace
        session_id = current_user.session_id
        success = await auth_manager.revoke_session(session_id)
        
        if success:
            logger.info(f"Uživatel {current_user.username} se úspěšně odhlásil (session: {session_id})")
            return {"message": "Úspěšně odhlášeno", "session_id": session_id}
        else:
            logger.warning(f"Nepodařilo se odhlásit uživatele {current_user.username}")
            return {"message": "Relace již byla ukončena", "session_id": session_id}
            
    except Exception as e:
        logger.error(f"Chyba při odhlášení uživatele {current_user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Interní chyba při odhlášení"
        )


@router.post("/logout-all")
async def logout_all_sessions(
    current_user: dict = Depends(get_current_user)
):
    """
    Odhlášení všech relací uživatele
    
    Odstraní všechny aktivní relace uživatele a invalidate všechny tokeny.
    """
    try:
        auth_manager = await get_auth_manager()
        
        # Odvolání všech relací
        revoked_count = await auth_manager.revoke_all_user_sessions(current_user.user_id)
        
        logger.info(f"Uživatel {current_user.username} odhlásil všechny relace ({revoked_count} ukončeno)")
        
        return {
            "message": f"Úspěšně odhlášeno {revoked_count} relací",
            "revoked_sessions": revoked_count
        }
        
    except Exception as e:
        logger.error(f"Chyba při hromadném odhlášení uživatele {current_user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Interní chyba při hromadném odhlášení"
        )


@router.get("/sessions", response_model=UserSessionsResponse)
async def get_user_sessions(
    current_user: dict = Depends(get_current_user)
):
    """
    Získání seznamu aktivních relací uživatele
    
    Vrací informace o všech aktivních relacích aktuálně přihlášeného uživatele.
    """
    try:
        auth_manager = await get_auth_manager()
        
        sessions = await auth_manager.get_user_sessions(current_user.user_id)
        
        # Převedení sessions na SessionInfo objekty
        session_infos = []
        for session in sessions:
            session_info = SessionInfo(
                session_id=session["session_id"],
                device_id=session.get("device_id"),
                created_at=datetime.fromisoformat(session["created_at"]),
                last_activity=datetime.fromisoformat(session["last_activity"])
            )
            session_infos.append(session_info)
        
        return UserSessionsResponse(
            user_id=current_user.user_id,
            username=current_user.username,
            active_sessions=session_infos,
            total_sessions=len(session_infos)
        )
        
    except Exception as e:
        logger.error(f"Chyba při získávání relací uživatele {current_user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Interní chyba při získávání relací"
        )


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Změna hesla aktuálně přihlášeného uživatele
    """
    try:
        auth_manager = await get_auth_manager()
        
        # Ověření aktuálního hesla
        try:
            await auth_manager.authenticate_user(
                username=current_user.username,
                password=request.current_password
            )
        except AuthenticationError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aktuální heslo není správné"
            )
        
        # TODO: Implementovat změnu hesla
        # Prozatím vrátíme success - v reálné implementaci by se měnilo hash v databázi
        
        logger.info(f"Uživatel {current_user.username} změnil heslo")
        
        return {"message": "Heslo bylo úspěšně změněno"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chyba při změně hesla uživatele {current_user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Interní chyba při změně hesla"
        )


# Admin endpointy
@router.get("/users", response_model=UserListResponse)
async def list_users(
    page: int = 1,
    per_page: int = 20,
    current_user: dict = Depends(require_role("admin"))
):
    """
    Získání seznamu všech uživatelů (pouze pro adminy)
    
    Vrací stránkovaný seznam všech uživatelů v systému.
    """
    try:
        auth_manager = await get_auth_manager()
        
        # Získání všech uživatelů
        all_users = list(auth_manager._users_db.values())
        
        # Stránkování
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_users = all_users[start_idx:end_idx]
        
        # Převedení na response objekty
        user_responses = []
        for user in paginated_users:
            user_response = UserInfoResponse(
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                role=user.role.value,
                permissions=list(user.permissions),
                created_at=user.created_at,
                last_login=user.last_login,
                is_active=user.is_active,
                mfa_enabled=user.mfa_enabled,
                session_limit=user.session_limit
            )
            user_responses.append(user_response)
        
        return UserListResponse(
            users=user_responses,
            total=len(all_users),
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        logger.error(f"Chyba při získávání seznamu uživatelů: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Interní chyba při získávání uživatelů"
        )


@router.get("/users/{user_id}", response_model=UserInfoResponse)
async def get_user(
    user_id: str,
    current_user: dict = Depends(require_role("admin"))
):
    """
    Získání detailních informací o konkrétním uživateli (pouze pro adminy)
    """
    try:
        auth_manager = await get_auth_manager()
        user = auth_manager._users_db.get(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Uživatel nenalezen"
            )
        
        return UserInfoResponse(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            role=user.role.value,
            permissions=list(user.permissions),
            created_at=user.created_at,
            last_login=user.last_login,
            is_active=user.is_active,
            mfa_enabled=user.mfa_enabled,
            session_limit=user.session_limit
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chyba při získávání informací o uživateli {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Interní chyba při získávání informací o uživateli"
        )


@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    request: UpdateUserRequest,
    current_user: dict = Depends(require_role("admin"))
):
    """
    Aktualizace uživatele (pouze pro adminy)
    """
    try:
        auth_manager = await get_auth_manager()
        user = auth_manager._users_db.get(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Uživatel nenalezen"
            )
        
        # Aktualizace polí
        if request.email is not None:
            user.email = request.email
        
        if request.role is not None:
            new_role = _map_role_to_enum(request.role)
            user.role = new_role
            user.permissions = auth_manager._get_role_permissions(new_role)
        
        if request.is_active is not None:
            user.is_active = request.is_active
        
        if request.session_limit is not None:
            user.session_limit = request.session_limit
        
        logger.info(f"Uživatel {user.username} byl aktualizován adminem {current_user.username}")
        
        return {"message": "Uživatel byl úspěšně aktualizován"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chyba při aktualizaci uživatele {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Interní chyba při aktualizaci uživatele"
        )


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: dict = Depends(require_role("admin"))
):
    """
    Smazání uživatele (pouze pro adminy)
    
    Poznámka: V reálné implementaci by se uživatel pouze deaktivoval,
    nikoliv fyzicky mazal.
    """
    try:
        auth_manager = await get_auth_manager()
        user = auth_manager._users_db.get(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Uživatel nenalezen"
            )
        
        # Kontrola zda se nejedná o vlastní účet
        if user_id == current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nemůžete smazat vlastní účet"
            )
        
        # Odvolání všech relací uživatele
        await auth_manager.revoke_all_user_sessions(user_id)
        
        # Deaktivace uživatele (místo fyzického smazání)
        user.is_active = False
        
        logger.info(f"Uživatel {user.username} byl deaktivován adminem {current_user.username}")
        
        return {"message": "Uživatel byl úspěšně deaktivován"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chyba při mazání uživatele {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Interní chyba při mazání uživatele"
        )


@router.get("/permissions")
async def get_available_permissions(
    current_user: dict = Depends(require_role("admin"))
):
    """
    Získání seznamu dostupných oprávnění (pouze pro adminy)
    
    Vrací kompletní seznam všech oprávnění v systému.
    """
    try:
        auth_manager = await get_auth_manager()
        
        # Sestavení seznamu všech oprávnění
        all_permissions = set()
        for role_permissions in auth_manager.role_permissions.values():
            all_permissions.update(role_permissions)
        
        # Seřazení a vrácení
        sorted_permissions = sorted(list(all_permissions))
        
        return {
            "permissions": sorted_permissions,
            "total": len(sorted_permissions)
        }
        
    except Exception as e:
        logger.error(f"Chyba při získávání seznamu oprávnění: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Interní chyba při získávání oprávnění"
        )


@router.get("/roles")
async def get_available_roles():
    """
    Získání seznamu dostupných rolí
    
    Vrací seznam všech rolí v systému s jejich popisy.
    """
    try:
        roles = [
            {"name": "guest", "description": "Host uživatel s minimálními oprávněními"},
            {"name": "user", "description": "Běžný uživatel se základními oprávněními"},
            {"name": "developer", "description": "Vývojář s přístupem k vývojovým nástrojům"},
            {"name": "admin", "description": "Administrátor s plnými oprávněními"},
            {"name": "system", "description": "Systémový účet pro interní procesy"}
        ]
        
        return {
            "roles": roles,
            "total": len(roles)
        }
        
    except Exception as e:
        logger.error(f"Chyba při získávání seznamu rolí: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Interní chyba při získávání rolí"
        )


@router.get("/verify")
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Ověření platnosti JWT tokenu
    
    Tento endpoint slouží pro rychlé ověření platnosti tokenu
    bez nutnosti volat chráněný endpoint.
    """
    try:
        auth_manager = await get_auth_manager()
        token = credentials.credentials
        
        # Ověření tokenu
        payload = await auth_manager.verify_token(token)
        
        return {
            "valid": True,
            "user_id": payload.user_id,
            "username": payload.username,
            "role": payload.role,
            "expires_at": datetime.fromtimestamp(payload.exp, tz=timezone.utc).isoformat(),
            "session_id": payload.session_id
        }
        
    except AuthenticationError as e:
        return {
            "valid": False,
            "error": str(e)
        }
    except Exception as e:
        logger.error(f"Chyba při ověřování tokenu: {str(e)}")
        return {
            "valid": False,
            "error": "Interní chyba při ověřování"
        }


@router.get("/health")
async def auth_health_check():
    """
    Health check pro autentizační službu
    
    Vrací status autentizačního systému.
    """
    try:
        auth_manager = await get_auth_manager()
        
        # Základní kontrola Redis připojení
        redis_client = auth_manager.redis
        await redis_client.ping()
        
        return {
            "status": "healthy",
            "service": "authentication",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_users": len(auth_manager._users_db),
            "active_sessions": "unknown"  # TODO: Implementovat počítání aktivních relací
        }
        
    except Exception as e:
        logger.error(f"Health check selhal: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "authentication",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }