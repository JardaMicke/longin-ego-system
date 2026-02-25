#!/usr/bin/env python3
"""
Spouštěcí skript pro LONGIN EGO API Server
Zajišťuje správnou inicializaci, kontrolu závislostí a bezpečné spuštění
"""

import sys
import os
import subprocess
import time
import logging
import signal
from pathlib import Path
from typing import Optional

# Nastavení logování
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('longin-ego-api.log')
    ]
)
logger = logging.getLogger(__name__)

# Globální proměnné
api_process: Optional[subprocess.Popen] = None
shutdown_requested = False


def check_python_version():
    """Kontrola verze Pythonu"""
    required_version = (3, 8)
    current_version = sys.version_info[:2]
    
    if current_version < required_version:
        logger.error(f"✗ Python {required_version[0]}.{required_version[1]}+ je vyžadován, máte {current_version[0]}.{current_version[1]}")
        return False
    
    logger.info(f"✓ Python {current_version[0]}.{current_version[1]} detekován")
    return True


def check_dependencies():
    """Kontrola a instalace závislostí"""
    logger.info("Kontroluji závislosti...")
    
    try:
        # Pokus o import klíčových modulů
        import fastapi
        import uvicorn
        import redis
        import jwt
        import bcrypt
        import pydantic
        
        logger.info("✓ Všechny závislosti jsou nainstalovány")
        return True
        
    except ImportError as e:
        logger.warning(f"✗ Chybějící závislosti: {e}")
        
        # Pokus o automatickou instalaci
        requirements_file = Path(__file__).parent.parent / "api" / "requirements.txt"
        
        if requirements_file.exists():
            logger.info("Pokouším se nainstalovat závislosti...")
            
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    logger.info("✓ Závislosti úspěšně nainstalovány")
                    return True
                else:
                    logger.error(f"✗ Chyba při instalaci závislostí: {result.stderr}")
                    return False
                    
            except subprocess.TimeoutExpired:
                logger.error("✗ Instalace závislostí vypršela")
                return False
            except Exception as e:
                logger.error(f"✗ Neočekávaná chyba při instalaci: {e}")
                return False
        else:
            logger.error(f"✗ Soubor requirements.txt nenalezen: {requirements_file}")
            return False


def check_redis_connection():
    """Kontrola Redis připojení"""
    logger.info("Kontroluji Redis připojení...")
    
    try:
        import redis
        
        # Načtení konfigurace z environment
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))
        redis_db = int(os.getenv("REDIS_DB", "0"))
        
        # Test připojení
        r = redis.Redis(host=redis_host, port=redis_port, db=redis_db, socket_timeout=5)
        r.ping()
        
        logger.info(f"✓ Redis připojen: {redis_host}:{redis_port}")
        return True
        
    except redis.ConnectionError:
        logger.error(f"✗ Nelze se připojit k Redis na {redis_host}:{redis_port}")
        logger.info("💡 Spusťte Redis server: redis-server")
        return False
    except Exception as e:
        logger.error(f"✗ Chyba při testování Redis: {e}")
        return False


def check_environment_config():
    """Kontrola environment konfigurace"""
    logger.info("Kontroluji environment konfiguraci...")
    
    # Základní kontroly
    required_vars = ["JWT_SECRET_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"⚠ Chybějící environment proměnné: {missing_vars}")
        logger.info("💡 Používám výchozí hodnoty pro development")
    
    # Varování pro výchozí JWT secret
    jwt_secret = os.getenv("JWT_SECRET_KEY", "")
    if jwt_secret == "your-super-secret-jwt-key-change-this-in-production-environment-minimum-64-characters-long":
        logger.warning("⚠ Používáte výchozí JWT secret key - změňte pro produkci!")
    
    # Kontrola portu
    port = int(os.getenv("API_PORT", "8000"))
    if port < 1024 and os.getuid() != 0:
        logger.warning(f"⚠ Port {port} vyžaduje root oprávnění, změňte na port > 1024")
    
    logger.info("✓ Environment konfigurace zkontrolována")
    return True


def create_directories():
    """Vytvoření potřebných adresářů"""
    logger.info("Kontroluji adresářovou strukturu...")
    
    directories = [
        "logs",
        "data",
        "temp",
        "backups"
    ]
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
                logger.info(f"✓ Vytvořen adresář: {directory}")
            except Exception as e:
                logger.error(f"✗ Nelze vytvořit adresář {directory}: {e}")
                return False
        else:
            logger.info(f"✓ Adresář existuje: {directory}")
    
    return True


def signal_handler(signum, frame):
    """Handler pro signály"""
    global shutdown_requested, api_process
    
    logger.info(f"Přijat signál {signum}, ukončuji API server...")
    shutdown_requested = True
    
    if api_process and api_process.poll() is None:
        logger.info("Ukončuji API proces...")
        api_process.terminate()
        
        # Počkat na ukončení
        try:
            api_process.wait(timeout=10)
            logger.info("✓ API proces úspěšně ukončen")
        except subprocess.TimeoutExpired:
            logger.warning("API proces neukončen včas, používám force kill")
            api_process.kill()
    
    sys.exit(0)


def start_api_server():
    """Spuštění API serveru"""
    global api_process
    
    logger.info("=== SPUŠTĚNÍ LONGIN EGO API SERVERU ===")
    
    # Nastavení signálů
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Kontroly před spuštěním
    checks = [
        ("Python verze", check_python_version),
        ("Závislosti", check_dependencies),
        ("Redis připojení", check_redis_connection),
        ("Environment konfigurace", check_environment_config),
        ("Adresářová struktura", create_directories)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        try:
            if not check_func():
                logger.error(f"✗ Kontrola '{check_name}' selhala")
                all_passed = False
        except Exception as e:
            logger.error(f"✗ Chyba při kontrole '{check_name}': {e}")
            all_passed = False
    
    if not all_passed:
        logger.error("✗ Některé kontroly selhaly, API server nebude spuštěn")
        return False
    
    logger.info("✓ Všechny kontroly proběhly úspěšně")
    
    # Příprava spuštění
    api_script = Path(__file__).parent.parent / "api" / "main.py"
    
    if not api_script.exists():
        logger.error(f"✗ API skript nenalezen: {api_script}")
        return False
    
    # Environment proměnné
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).parent.parent)
    
    # Spuštění API serveru
    try:
        logger.info(f"Spouštím API server: {api_script}")
        
        cmd = [
            sys.executable,
            str(api_script)
        ]
        
        api_process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        logger.info(f"✓ API server spuštěn s PID: {api_process.pid}")
        
        # Počkat na inicializaci
        logger.info("Čekám na inicializaci API serveru...")
        time.sleep(3)
        
        # Kontrola zda proces běží
        if api_process.poll() is None:
            logger.info("✓ API server běží úspěšně")
            
            # Logování výstupu
            logger.info("=== VÝSTUP API SERVERU ===")
            
            # Čtení výstupu v samostatných vláknech
            import threading
            
            def log_output(pipe, log_func):
                for line in iter(pipe.readline, ''):
                    if line:
                        log_func(line.strip())
            
            # Spuštění logovacích vláken
            threading.Thread(target=log_output, args=(api_process.stdout, logger.info), daemon=True).start()
            threading.Thread(target=log_output, args=(api_process.stderr, logger.error), daemon=True).start()
            
            # Čekání na ukončení
            logger.info("API server běží. Stiskněte Ctrl+C pro ukončení.")
            
            while not shutdown_requested:
                time.sleep(1)
                
                # Kontrola zda proces stále běží
                if api_process.poll() is not None:
                    logger.error(f"✗ API server neočekávaně ukončen s kódem: {api_process.returncode}")
                    break
            
        else:
            logger.error(f"✗ API server selhal s kódem: {api_process.returncode}")
            
            # Výpis chyb
            stderr_output = api_process.stderr.read()
            if stderr_output:
                logger.error("Chyby API serveru:")
                logger.error(stderr_output)
            
            return False
            
    except KeyboardInterrupt:
        logger.info("Ukončení požádáno uživatelem")
        signal_handler(signal.SIGINT, None)
        
    except Exception as e:
        logger.error(f"✗ Chyba při spouštění API serveru: {e}")
        return False
    
    return True


def main():
    """Hlavní funkce"""
    logger.info("=== LONGIN EGO API STARTER ===")
    logger.info("Suverénní digitální organismus - API Server")
    
    # Kontrola argumentů příkazové řádky
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print("""
LONGIN EGO API Starter

Použití:
    python start_api.py [možnosti]

Možnosti:
    --help, -h          Zobrazit tuto nápovědu
    --check-only        Pouze zkontrolovat závislosti a konfiguraci
    --daemon            Spustit jako daemon (pouze Linux/macOS)
    --port PORT         Specifikovat port (přepíše API_PORT)
    --host HOST         Specifikovat host (přepíše API_HOST)
    --redis HOST:PORT   Specifikovat Redis (přepíše REDIS_HOST a REDIS_PORT)

Environment proměnné:
    API_HOST            Host pro API server (default: 0.0.0.0)
    API_PORT            Port pro API server (default: 8000)
    REDIS_HOST          Redis host (default: localhost)
    REDIS_PORT          Redis port (default: 6379)
    JWT_SECRET_KEY      Tajný klíč pro JWT (musí být změněn pro produkci!)
    ENVIRONMENT         Prostředí (development/staging/production)
    DEBUG               Debug mód (true/false)
        """)
        return
    
    # Zpracování argumentů
    check_only = "--check-only" in sys.argv
    daemon_mode = "--daemon" in sys.argv
    
    # Zpracování portu
    if "--port" in sys.argv:
        port_index = sys.argv.index("--port")
        if port_index + 1 < len(sys.argv):
            os.environ["API_PORT"] = sys.argv[port_index + 1]
    
    # Zpracování hostu
    if "--host" in sys.argv:
        host_index = sys.argv.index("--host")
        if host_index + 1 < len(sys.argv):
            os.environ["API_HOST"] = sys.argv[host_index + 1]
    
    # Zpracování Redis
    if "--redis" in sys.argv:
        redis_index = sys.argv.index("--redis")
        if redis_index + 1 < len(sys.argv):
            redis_addr = sys.argv[redis_index + 1]
            if ":" in redis_addr:
                host, port = redis_addr.split(":")
                os.environ["REDIS_HOST"] = host
                os.environ["REDIS_PORT"] = port
            else:
                os.environ["REDIS_HOST"] = redis_addr
    
    if check_only:
        logger.info("=== KONTROLA ZÁVISLOSTÍ A KONFIGURACE ===")
        
        checks = [
            ("Python verze", check_python_version),
            ("Závislosti", check_dependencies),
            ("Redis připojení", check_redis_connection),
            ("Environment konfigurace", check_environment_config),
            ("Adresářová struktura", create_directories)
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            try:
                if not check_func():
                    logger.error(f"✗ Kontrola '{check_name}' selhala")
                    all_passed = False
            except Exception as e:
                logger.error(f"✗ Chyba při kontrole '{check_name}': {e}")
                all_passed = False
        
        if all_passed:
            logger.info("✓ Všechny kontroly proběhly úspěšně - systém je připraven k spuštění")
            sys.exit(0)
        else:
            logger.error("✗ Některé kontroly selhaly - systém není připraven")
            sys.exit(1)
    
    if daemon_mode:
        logger.info("Daemon mód není plně implementován, spouštím normálně...")
    
    # Spuštění API serveru
    success = start_api_server()
    
    if success:
        logger.info("✓ API server úspěšně ukončen")
        sys.exit(0)
    else:
        logger.error("✗ API server selhal")
        sys.exit(1)


if __name__ == "__main__":
    main()