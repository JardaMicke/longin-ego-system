"""
Komplexní testovací skript pro LONGIN EGO autentizační systém
Ověřuje JWT autentizaci, RBAC, session management a bezpečnostní funkce
"""

import asyncio
import aiohttp
import json
import logging
import time
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import jwt
import secrets

# Konfigurace logování
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Testovací konfigurace
API_BASE_URL = "http://localhost:8000"
TEST_ADMIN_USERNAME = "admin"
TEST_ADMIN_PASSWORD = "admin123456789"  # Minimálně 12 znaků
TEST_USER_USERNAME = "testuser"
TEST_USER_PASSWORD = "test123456789"

class AuthSystemTester:
    """Testovací třída pro autentizační systém"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = None
        self.admin_tokens = None
        self.user_tokens = None
        self.test_results = []
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test_result(self, test_name: str, success: bool, details: str = "", duration: float = 0):
        """Zaznamenání výsledku testu"""
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        if success:
            logger.info(f"✓ {test_name} - ÚSPĚŠNÝ ({duration:.2f}s)")
        else:
            logger.error(f"✗ {test_name} - SELHAL: {details} ({duration:.2f}s)")
    
    async def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                          headers: Optional[Dict] = None, token: Optional[str] = None) -> Dict:
        """Pomocná metoda pro HTTP požadavky"""
        url = f"{self.base_url}{endpoint}"
        
        if token:
            if not headers:
                headers = {}
            headers["Authorization"] = f"Bearer {token}"
        
        start_time = time.time()
        
        try:
            async with self.session.request(method, url, json=data, headers=headers) as response:
                response_text = await response.text()
                duration = time.time() - start_time
                
                try:
                    response_data = json.loads(response_text) if response_text else {}
                except json.JSONDecodeError:
                    response_data = {"text": response_text}
                
                return {
                    "status": response.status,
                    "data": response_data,
                    "headers": dict(response.headers),
                    "duration": duration
                }
                
        except Exception as e:
            duration = time.time() - start_time
            return {
                "status": 0,
                "data": {"error": str(e)},
                "headers": {},
                "duration": duration
            }
    
    async def test_health_check(self):
        """Test health check endpointu"""
        start_time = time.time()
        
        try:
            response = await self.make_request("GET", "/health")
            success = response["status"] == 200 and response["data"].get("status") == "healthy"
            details = f"Status: {response['data'].get('status', 'unknown')}"
            
        except Exception as e:
            success = False
            details = f"Chyba: {str(e)}"
        
        duration = time.time() - start_time
        self.log_test_result("Health Check", success, details, duration)
        
        return success
    
    async def test_admin_login(self):
        """Test přihlášení admin uživatele"""
        start_time = time.time()
        
        try:
            login_data = {
                "username": TEST_ADMIN_USERNAME,
                "password": TEST_ADMIN_PASSWORD,
                "device_id": "test-device-001"
            }
            
            response = await self.make_request("POST", "/auth/login", data=login_data)
            
            if response["status"] == 200:
                tokens = response["data"]
                if "access_token" in tokens and "refresh_token" in tokens:
                    self.admin_tokens = tokens
                    success = True
                    details = f"Role: {tokens['user']['role']}"
                else:
                    success = False
                    details = "Chybí tokeny v odpovědi"
            else:
                success = False
                details = f"HTTP {response['status']}: {response['data']}"
            
        except Exception as e:
            success = False
            details = f"Chyba: {str(e)}"
        
        duration = time.time() - start_time
        self.log_test_result("Admin Login", success, details, duration)
        
        return success
    
    async def test_user_registration_and_login(self):
        """Test registrace a přihlášení běžného uživatele"""
        start_time = time.time()
        
        try:
            # Registrace uživatele (vyžaduje admin token)
            if not self.admin_tokens:
                success = False
                details = "Chybí admin token pro registraci"
            else:
                register_data = {
                    "username": TEST_USER_USERNAME,
                    "email": f"{TEST_USER_USERNAME}@test.local",
                    "password": TEST_USER_PASSWORD,
                    "role": "user"
                }
                
                reg_response = await self.make_request(
                    "POST", "/auth/register", 
                    data=register_data, 
                    token=self.admin_tokens["access_token"]
                )
                
                if reg_response["status"] in [200, 201]:
                    # Přihlášení nového uživatele
                    login_data = {
                        "username": TEST_USER_USERNAME,
                        "password": TEST_USER_PASSWORD
                    }
                    
                    login_response = await self.make_request("POST", "/auth/login", data=login_data)
                    
                    if login_response["status"] == 200:
                        self.user_tokens = login_response["data"]
                        success = True
                        details = f"User ID: {reg_response['data']['user_id']}"
                    else:
                        success = False
                        details = f"Login selhal: HTTP {login_response['status']}"
                else:
                    success = False
                    details = f"Registrace selhala: HTTP {reg_response['status']}"
            
        except Exception as e:
            success = False
            details = f"Chyba: {str(e)}"
        
        duration = time.time() - start_time
        self.log_test_result("User Registration & Login", success, details, duration)
        
        return success
    
    async def test_token_refresh(self):
        """Test obnovení access tokenu"""
        start_time = time.time()
        
        try:
            if not self.user_tokens:
                success = False
                details = "Chybí user tokens"
            else:
                refresh_data = {
                    "refresh_token": self.user_tokens["refresh_token"]
                }
                
                response = await self.make_request("POST", "/auth/refresh", data=refresh_data)
                
                if response["status"] == 200 and "access_token" in response["data"]:
                    # Aktualizace access tokenu
                    self.user_tokens["access_token"] = response["data"]["access_token"]
                    success = True
                    details = f"Nový token platí {response['data']['expires_in']}s"
                else:
                    success = False
                    details = f"Refresh selhal: HTTP {response['status']}"
            
        except Exception as e:
            success = False
            details = f"Chyba: {str(e)}"
        
        duration = time.time() - start_time
        self.log_test_result("Token Refresh", success, details, duration)
        
        return success
    
    async def test_protected_endpoints_access(self):
        """Test přístupu k chráněným endpointům"""
        start_time = time.time()
        
        try:
            if not self.user_tokens:
                success = False
                details = "Chybí user tokens"
            else:
                # Test přístupu k vlastním informacím
                me_response = await self.make_request("GET", "/auth/me", token=self.user_tokens["access_token"])
                
                if me_response["status"] == 200:
                    user_info = me_response["data"]
                    success = True
                    details = f"Role: {user_info['role']}, Oprávnění: {len(user_info['permissions'])}"
                else:
                    success = False
                    details = f"Přístup selhal: HTTP {me_response['status']}"
            
        except Exception as e:
            success = False
            details = f"Chyba: {str(e)}"
        
        duration = time.time() - start_time
        self.log_test_result("Protected Endpoints Access", success, details, duration)
        
        return success
    
    async def test_role_based_access_control(self):
        """Test RBAC - role-based access control"""
        start_time = time.time()
        
        try:
            if not self.user_tokens or not self.admin_tokens:
                success = False
                details = "Chybí tokens"
            else:
                # Test uživatele bez admin oprávnění
                user_list_response = await self.make_request(
                    "GET", "/auth/users", 
                    token=self.user_tokens["access_token"]
                )
                
                # Uživatel by měl dostat 403 (Forbidden)
                user_forbidden = user_list_response["status"] == 403
                
                # Test admina s admin oprávněním
                admin_list_response = await self.make_request(
                    "GET", "/auth/users", 
                    token=self.admin_tokens["access_token"]
                )
                
                # Admin by měl dostat 200 (OK)
                admin_allowed = admin_list_response["status"] == 200
                
                success = user_forbidden and admin_allowed
                details = f"Uživatel: {'403' if user_forbidden else user_list_response['status']}, " \
                         f"Admin: {'200' if admin_allowed else admin_list_response['status']}"
            
        except Exception as e:
            success = False
            details = f"Chyba: {str(e)}"
        
        duration = time.time() - start_time
        self.log_test_result("RBAC - Role Based Access Control", success, details, duration)
        
        return success
    
    async def test_session_management(self):
        """Test správy relací"""
        start_time = time.time()
        
        try:
            if not self.user_tokens:
                success = False
                details = "Chybí user tokens"
            else:
                # Získání seznamu relací
                sessions_response = await self.make_request(
                    "GET", "/auth/sessions", 
                    token=self.user_tokens["access_token"]
                )
                
                if sessions_response["status"] == 200:
                    sessions_data = sessions_response["data"]
                    session_count = len(sessions_data.get("active_sessions", []))
                    success = True
                    details = f"Aktivních relací: {session_count}"
                else:
                    success = False
                    details = f"Chyba při získávání relací: HTTP {sessions_response['status']}"
            
        except Exception as e:
            success = False
            details = f"Chyba: {str(e)}"
        
        duration = time.time() - start_time
        self.log_test_result("Session Management", success, details, duration)
        
        return success
    
    async def test_logout_functionality(self):
        """Test odhlášení a invalidace tokenu"""
        start_time = time.time()
        
        try:
            if not self.user_tokens:
                success = False
                details = "Chybí user tokens"
            else:
                # Odhlášení
                logout_response = await self.make_request(
                    "POST", "/auth/logout", 
                    token=self.user_tokens["access_token"]
                )
                
                logout_success = logout_response["status"] in [200, 204]
                
                # Pokus o přístup s invalidated tokenem
                me_response = await self.make_request(
                    "GET", "/auth/me", 
                    token=self.user_tokens["access_token"]
                )
                
                token_invalidated = me_response["status"] == 401
                
                success = logout_success and token_invalidated
                details = f"Logout: {'OK' if logout_success else 'FAIL'}, " \
                         f"Token invalidated: {'OK' if token_invalidated else 'FAIL'}"
            
        except Exception as e:
            success = False
            details = f"Chyba: {str(e)}"
        
        duration = time.time() - start_time
        self.log_test_result("Logout Functionality", success, details, duration)
        
        return success
    
    async def test_token_verification(self):
        """Test ověření platnosti tokenu"""
        start_time = time.time()
        
        try:
            if not self.admin_tokens:
                success = False
                details = "Chybí admin tokens"
            else:
                response = await self.make_request(
                    "GET", "/auth/verify", 
                    token=self.admin_tokens["access_token"]
                )
                
                if response["status"] == 200:
                    verify_data = response["data"]
                    success = verify_data.get("valid", False)
                    details = f"Valid: {success}, User: {verify_data.get('username', 'unknown')}"
                else:
                    success = False
                    details = f"Verification selhala: HTTP {response['status']}"
            
        except Exception as e:
            success = False
            details = f"Chyba: {str(e)}"
        
        duration = time.time() - start_time
        self.log_test_result("Token Verification", success, details, duration)
        
        return success
    
    async def test_rate_limiting(self):
        """Test rate limiting ochrany"""
        start_time = time.time()
        
        try:
            # Vytvoření anonymní session pro test rate limitingu
            anon_session = aiohttp.ClientSession()
            
            # Odeslání 25 rychlých požadavků (limit je 20 pro anonymní)
            responses = []
            for i in range(25):
                try:
                    async with anon_session.get(f"{self.base_url}/health") as response:
                        responses.append(response.status)
                except:
                    responses.append(0)
            
            await anon_session.close()
            
            # Počítadlo 429 odpovědí
            rate_limited_count = responses.count(429)
            
            # Měli bychom dostat alespoň 5 rate limited odpovědí
            success = rate_limited_count >= 5
            details = f"Rate limited: {rate_limited_count}/25, Responses: {responses[:10]}..."
            
        except Exception as e:
            success = False
            details = f"Chyba: {str(e)}"
        
        duration = time.time() - start_time
        self.log_test_result("Rate Limiting", success, details, duration)
        
        return success
    
    async def test_invalid_credentials(self):
        """Test ochrany proti neplatným přihlašovacím údajům"""
        start_time = time.time()
        
        try:
            # Test s neplatným heslem
            invalid_login = {
                "username": TEST_ADMIN_USERNAME,
                "password": "wrongpassword123456789"
            }
            
            response = await self.make_request("POST", "/auth/login", data=invalid_login)
            
            login_blocked = response["status"] == 401
            
            # Test s neexistujícím uživatelem
            nonexistent_login = {
                "username": "nonexistentuser12345",
                "password": "somepassword123456789"
            }
            
            response2 = await self.make_request("POST", "/auth/login", data=nonexistent_login)
            
            nonexistent_blocked = response2["status"] == 401
            
            success = login_blocked and nonexistent_blocked
            details = f"Invalid password: {'401' if login_blocked else response['status']}, " \
                     f"Nonexistent user: {'401' if nonexistent_blocked else response2['status']}"
            
        except Exception as e:
            success = False
            details = f"Chyba: {str(e)}"
        
        duration = time.time() - start_time
        self.log_test_result("Invalid Credentials Protection", success, details, duration)
        
        return success
    
    async def test_jwt_token_structure(self):
        """Test struktury a validity JWT tokenů"""
        start_time = time.time()
        
        try:
            if not self.admin_tokens:
                success = False
                details = "Chybí admin tokens"
            else:
                access_token = self.admin_tokens["access_token"]
                
                # Dekódování tokenu (bez ověření podpisu)
                try:
                    payload = jwt.decode(access_token, options={"verify_signature": False})
                    
                    # Kontrola povinných polí
                    required_fields = ["user_id", "username", "role", "permissions", "exp", "iat", "jti"]
                    missing_fields = [field for field in required_fields if field not in payload]
                    
                    # Kontrola expirace
                    exp_timestamp = payload.get("exp", 0)
                    current_timestamp = int(time.time())
                    valid_expiration = exp_timestamp > current_timestamp
                    
                    # Kontrola času vydání
                    iat_timestamp = payload.get("iat", 0)
                    valid_issued_at = iat_timestamp <= current_timestamp
                    
                    success = len(missing_fields) == 0 and valid_expiration and valid_issued_at
                    details = f"Missing fields: {missing_fields}, Exp valid: {valid_expiration}, IAT valid: {valid_issued_at}"
                    
                except Exception as decode_error:
                    success = False
                    details = f"Chyba dekódování: {str(decode_error)}"
            
        except Exception as e:
            success = False
            details = f"Chyba: {str(e)}"
        
        duration = time.time() - start_time
        self.log_test_result("JWT Token Structure", success, details, duration)
        
        return success
    
    async def test_permission_system(self):
        """Test systému oprávnění"""
        start_time = time.time()
        
        try:
            if not self.admin_tokens:
                success = False
                details = "Chybí admin tokens"
            else:
                # Získání seznamu oprávnění (vyžaduje admin roli)
                permissions_response = await self.make_request(
                    "GET", "/auth/permissions", 
                    token=self.admin_tokens["access_token"]
                )
                
                if permissions_response["status"] == 200:
                    permissions_data = permissions_response["data"]
                    permission_count = len(permissions_data.get("permissions", []))
                    success = permission_count > 0
                    details = f"Celkem oprávnění: {permission_count}"
                else:
                    success = False
                    details = f"Chyba při získávání oprávnění: HTTP {permissions_response['status']}"
            
        except Exception as e:
            success = False
            details = f"Chyba: {str(e)}"
        
        duration = time.time() - start_time
        self.log_test_result("Permission System", success, details, duration)
        
        return success
    
    async def run_all_tests(self):
        """Spuštění všech testů"""
        logger.info("=== SPUŠTĚNÍ KOMPLETNÍCH TESTŮ AUTENTIZAČNÍHO SYSTÉMU ===")
        
        test_methods = [
            self.test_health_check,
            self.test_admin_login,
            self.test_user_registration_and_login,
            self.test_token_refresh,
            self.test_protected_endpoints_access,
            self.test_role_based_access_control,
            self.test_session_management,
            self.test_token_verification,
            self.test_permission_system,
            self.test_jwt_token_structure,
            self.test_invalid_credentials,
            self.test_rate_limiting,
            self.test_logout_functionality
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            try:
                result = await test_method()
                if result:
                    passed_tests += 1
                # Krátká pauza mezi testy
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Test {test_method.__name__} selhal s výjimkou: {str(e)}")
                self.log_test_result(test_method.__name__, False, f"Výjimka: {str(e)}")
        
        # Shrnutí výsledků
        success_rate = (passed_tests / total_tests) * 100
        
        logger.info("\n" + "="*60)
        logger.info(f"=== SHRNUTÍ TESTŮ ===")
        logger.info(f"Celkem testů: {total_tests}")
        logger.info(f"Úspěšných: {passed_tests}")
        logger.info(f"Neúspěšných: {total_tests - passed_tests}")
        logger.info(f"Úspěšnost: {success_rate:.1f}%")
        
        # Výpis všech výsledků
        logger.info("\n=== DETAILNÍ VÝSLEDKY ===")
        for result in self.test_results:
            status = "✓" if result["success"] else "✗"
            logger.info(f"{status} {result['test_name']} - {result['details']}")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": success_rate,
            "results": self.test_results
        }


async def main():
    """Hlavní testovací funkce"""
    
    logger.info("=== TESTOVÁNÍ LONGIN EGO AUTENTIZAČNÍHO SYSTÉMU ===")
    logger.info(f"API URL: {API_BASE_URL}")
    logger.info(f"Test admin: {TEST_ADMIN_USERNAME}")
    logger.info(f"Test user: {TEST_USER_USERNAME}")
    
    # Počkat na start API serveru
    logger.info("Čekám na start API serveru...")
    await asyncio.sleep(2)
    
    async with AuthSystemTester() as tester:
        results = await tester.run_all_tests()
        
        # Uložení výsledků do souboru
        results_file = f"auth_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\nVýsledky testů uloženy do: {results_file}")
        
        # Vrácení exit kódu podle úspěšnosti
        if results["success_rate"] >= 80:  # Minimálně 80% úspěšnost
            logger.info("✓ Testování DOKONČENO ÚSPĚŠNĚ")
            return 0
        else:
            logger.error("✗ Testování DOKONČENO S CHYBAMI")
            return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)