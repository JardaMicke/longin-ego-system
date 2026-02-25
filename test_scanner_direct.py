#!/usr/bin/env python3
"""
Přímý test Advanced Scanneru - Computer Vision Fallback System
"""

import sys
import os
import asyncio
import numpy as np
from pathlib import Path

def test_basic_functionality():
    """Test základní funkcionality skeneru"""
    print("🧪 Testuji základní funkcionalitu Advanced Scanneru...")
    
    try:
        # Nastavení cesty
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        # Import základních komponent
        from kernel.scanner.advanced_scanner import (
            ScannerConfig, ComputerVisionEngine, AdvancedScanner, 
            VisualChange, create_default_scanner
        )
        
        print("✅ Úspěšně naimportovány základní komponenty")
        
        # Test 1: Vytvoření konfigurace
        config = ScannerConfig()
        print(f"✅ Vytvořena výchozí konfigurace:")
        print(f"   - screenshot_interval: {config.screenshot_interval}s")
        print(f"   - change_threshold: {config.change_threshold}")
        print(f"   - enable_gpu: {config.enable_gpu}")
        print(f"   - enable_ocr: {config.enable_ocr}")
        print(f"   - enable_ml: {config.enable_ml}")
        
        # Test 2: Vytvoření CV engine
        cv_engine = ComputerVisionEngine(config)
        print("✅ Vytvořen Computer Vision Engine")
        
        # Test 3: Test podobnosti
        print("📊 Testuji výpočet podobnosti...")
        
        # Vytvoření testovacích obrázků
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2[25:75, 25:75] = 255  # Přidání změny
        
        # Test různých algoritmů
        algorithms = ['mse', 'histogram']
        for alg in algorithms:
            config.similarity_algorithm = alg
            similarity = cv_engine.calculate_similarity(img1, img2)
            print(f"   - {alg.upper()} podobnost: {similarity:.3f}")
        
        # Test 4: Detekce změn
        print("🔍 Testuji detekci změn...")
        changes = cv_engine.detect_changes(img1, img2)
        print(f"✅ Detekováno {len(changes)} změn")
        
        for i, change in enumerate(changes):
            print(f"   - Změna {i+1}: {change.change_type} (confidence: {change.confidence:.3f})")
            print(f"     Oblast: {change.coordinates}, Plocha: {change.area}px²")
        
        # Test 5: Vytvoření skeneru
        print("🤖 Testuji vytvoření Advanced Scanneru...")
        scanner = AdvancedScanner(config)
        print("✅ Advanced Scanner úspěšně vytvořen")
        
        # Test 6: Získání statusu
        status = asyncio.run(scanner.get_scanner_status())
        print(f"✅ Status skeneru: {status}")
        
        print("\n🎉 Všechny základní testy proběhly úspěšně!")
        return True
        
    except ImportError as e:
        print(f"❌ Chyba importu: {e}")
        print("Zkontrolujte, zda jsou všechny závislosti nainstalovány")
        return False
        
    except Exception as e:
        print(f"❌ Obecná chyba: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cv_algorithms():
    """Test počítačových vidění algoritmů"""
    print("\n🖼️  Testuji CV algoritmy...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from kernel.scanner.advanced_scanner import ComputerVisionEngine, ScannerConfig
        
        config = ScannerConfig()
        cv_engine = ComputerVisionEngine(config)
        
        # Vytvoření různých typů testovacích obrázků
        test_cases = [
            ("Prázdný vs s obsahem", 
             np.zeros((50, 50, 3), dtype=np.uint8),
             np.ones((50, 50, 3), dtype=np.uint8) * 255),
            
            ("Malá změna",
             np.zeros((100, 100, 3), dtype=np.uint8),
             np.zeros((100, 100, 3), dtype=np.uint8)),
            
            ("Velká změna",
             np.random.randint(0, 50, (100, 100, 3), dtype=np.uint8),
             np.random.randint(200, 255, (100, 100, 3), dtype=np.uint8))
        ]
        
        # Upravit druhý obrázek pro test "Malá změna"
        test_cases[1] = ("Malá změna",
                        test_cases[1][1],
                        test_cases[1][2])
        test_cases[1][2][40:60, 40:60] = 128  # Malá změna
        
        for test_name, img1, img2 in test_cases:
            print(f"\n📋 Test: {test_name}")
            
            # Test podobnosti
            for alg in ['mse', 'histogram']:
                config.similarity_algorithm = alg
                similarity = cv_engine.calculate_similarity(img1, img2)
                print(f"   {alg.upper()}: {similarity:.3f}")
            
            # Test detekce změn
            changes = cv_engine.detect_changes(img1, img2)
            print(f"   Detekováno změn: {len(changes)}")
            
            if changes:
                for change in changes[:3]:  # Zobrazit max 3 změny
                    print(f"     - {change.change_type} (conf: {change.confidence:.2f})")
        
        print("✅ CV algoritmy úspěšně otestovány")
        return True
        
    except Exception as e:
        print(f"❌ Chyba při testování CV algoritmů: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory_management():
    """Test správy paměti"""
    print("\n💾 Testuji správu paměti...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from kernel.scanner.advanced_scanner import MemoryTracker
        
        tracker = MemoryTracker()
        
        # Test získání využití paměti
        usage = tracker.get_current_usage()
        print(f"✅ Aktuální využití paměti: {usage} bytes")
        
        # Test kontroly limitu
        within_limit = tracker.is_within_limit(1000)  # 1GB limit
        print(f"✅ V rámci limitu 1GB: {within_limit}")
        
        # Test s nízkým limitem
        within_low_limit = tracker.is_within_limit(1)  # 1MB limit
        print(f"✅ V rámci limitu 1MB: {within_low_limit}")
        
        print("✅ Správa paměti úspěšně otestována")
        return True
        
    except Exception as e:
        print(f"❌ Chyba při testování správy paměti: {e}")
        return False

def main():
    """Hlavní testovací funkce"""
    print("🤖 LONGIN EGO - Advanced Scanner Test Suite")
    print("=" * 60)
    
    test_results = []
    
    # Spuštění testů
    test_results.append(("Základní funkcionalita", test_basic_functionality()))
    test_results.append(("CV algoritmy", test_cv_algorithms()))
    test_results.append(("Správa paměti", test_memory_management()))
    
    # Shrnutí výsledků
    print("\n" + "=" * 60)
    print("📊 SHRNUTÍ TESTŮ")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PROŠEL" if result else "❌ SELHAL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📈 Celkové skóre: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 Všechny testy proběhly úspěšně!")
        return 0
    else:
        print("⚠️  Některé testy selhaly")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)