#!/usr/bin/env python3
"""
Spouštěcí skript pro testy Advanced Scanneru
"""

import sys
import os
import subprocess
import asyncio
from pathlib import Path

def run_tests():
    """Spuštění testů Advanced Scanneru"""
    
    # Nastavení cesty k projektu
    project_root = Path(__file__).parent
    test_file = project_root / "tests" / "test_advanced_scanner.py"
    
    if not test_file.exists():
        print(f"❌ Testovací soubor nebyl nalezen: {test_file}")
        return False
    
    print("🚀 Spouštím testy Advanced Scanneru...")
    print(f"📁 Projektový adresář: {project_root}")
    print(f"🧪 Testovací soubor: {test_file}")
    
    # Nastavení Python path
    sys.path.insert(0, str(project_root))
    
    try:
        # Spuštění pytest
        result = subprocess.run([
            sys.executable, "-m", "pytest", str(test_file), "-v"
        ], cwd=str(project_root), capture_output=True, text=True)
        
        print("\n" + "="*60)
        print("📊 VÝSLEDKY TESTŮ")
        print("="*60)
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"\n📈 Návratový kód: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ Všechny testy proběhly úspěšně!")
            return True
        else:
            print("❌ Některé testy selhaly")
            return False
            
    except Exception as e:
        print(f"❌ Chyba při spouštění testů: {e}")
        return False

def run_demo():
    """Spuštění demo funkce"""
    print("\n🎯 Spouštím demo Advanced Scanneru...")
    
    try:
        # Import demo funkce
        sys.path.insert(0, str(Path(__file__).parent))
        
        from kernel.scanner.advanced_scanner import demo_scanner
        
        # Spuštění demo
        asyncio.run(demo_scanner())
        
        print("✅ Demo úspěšně dokončeno")
        return True
        
    except Exception as e:
        print(f"❌ Chyba při spouštění dema: {e}")
        return False

def main():
    """Hlavní funkce"""
    print("🤖 LONGIN EGO - Advanced Scanner Test Suite")
    print("="*50)
    
    # Test 1: Spuštění testů
    test_success = run_tests()
    
    # Test 2: Spuštění dema (volitelné)
    if test_success:
        print("\n" + "="*50)
        demo_success = run_demo()
        
        if demo_success:
            print("\n🎉 Všechny testy a demo proběhly úspěšně!")
        else:
            print("\n⚠️  Testy proběhly úspěšně, ale demo selhalo")
    else:
        print("\n❌ Testy selhaly, demo se nebude spouštět")

if __name__ == "__main__":
    main()