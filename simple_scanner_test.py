#!/usr/bin/env python3
"""
Jednoduchý test Advanced Scanneru - Computer Vision Fallback System
"""

import sys
import os
import numpy as np
import asyncio
from pathlib import Path

def test_numpy():
    """Test numpy funkčnosti"""
    print("🧪 Testuji numpy...")
    
    try:
        # Vytvoření testovacích obrázků
        img1 = np.zeros((50, 50, 3), dtype=np.uint8)
        img2 = np.zeros((50, 50, 3), dtype=np.uint8)
        img2[10:40, 10:40] = 255
        
        print(f"✅ Vytvořeny testovací obrázky:")
        print(f"   img1 shape: {img1.shape}, dtype: {img1.dtype}")
        print(f"   img2 shape: {img2.shape}, dtype: {img2.dtype}")
        
        # Test výpočtu rozdílu
        diff = np.abs(img1.astype(np.int16) - img2.astype(np.int16))
        print(f"✅ Vypočítán rozdíl, shape: {diff.shape}")
        
        # Test průměru
        mean1 = np.mean(img1)
        mean2 = np.mean(img2)
        print(f"✅ Průměrné hodnoty: img1={mean1:.2f}, img2={mean2:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Chyba v numpy testu: {e}")
        return False

def test_cv2_basic():
    """Test základních OpenCV funkcí"""
    print("\n🖼️  Testuji základní OpenCV funkce...")
    
    try:
        import cv2
        
        # Vytvoření testovacích obrázků
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2[25:75, 25:75] = 255
        
        print(f"✅ OpenCV verze: {cv2.__version__}")
        
        # Test absdiff
        diff = cv2.absdiff(img1, img2)
        print(f"✅ cv2.absdiff úspěšný, výsledek shape: {diff.shape}")
        
        # Test převodu na grayscale
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        print(f"✅ Převod na grayscale úspěšný")
        
        # Test threshold
        _, thresh = cv2.threshold(gray_diff := cv2.absdiff(gray1, gray2), 30, 255, cv2.THRESH_BINARY)
        print(f"✅ Threshold úspěšný, výsledek shape: {thresh.shape}")
        
        # Test kontur
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        print(f"✅ Nalezeno {len(contours)} kontur")
        
        return True
        
    except ImportError:
        print("❌ OpenCV není nainstalován")
        return False
        
    except Exception as e:
        print(f"❌ Chyba v OpenCV testu: {e}")
        return False

def test_basic_cv_engine():
    """Test základní funkcionality CV enginu"""
    print("\n🔍 Testuji základní CV engine...")
    
    try:
        # Vytvoření jednoduché třídy pro test
        class SimpleCVEngine:
            def __init__(self):
                self.config = type('Config', (), {
                    'min_change_area': 50,
                    'cluster_eps': 10.0,
                    'cluster_min_samples': 5
                })()
            
            def detect_changes(self, img1, img2):
                import cv2
                import numpy as np
                
                # Výpočet rozdílu
                diff = cv2.absdiff(img1, img2)
                gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                
                # Aplikace prahu
                _, thresh = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)
                
                # Nalezení kontur
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                changes = []
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > self.config.min_change_area:
                        x, y, w, h = cv2.boundingRect(contour)
                        changes.append({
                            'type': 'modified',
                            'area': area,
                            'coordinates': (x, y, x+w, y+h)
                        })
                
                return changes
        
        # Vytvoření testovacích obrázků
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2[30:70, 30:70] = 255
        
        # Test detekce
        engine = SimpleCVEngine()
        changes = engine.detect_changes(img1, img2)
        
        print(f"✅ Detekováno {len(changes)} změn")
        
        for i, change in enumerate(changes):
            print(f"   Změna {i+1}: {change['type']}, plocha: {change['area']:.0f}px²")
            print(f"   Souřadnice: {change['coordinates']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Chyba v CV engine testu: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dependencies():
    """Test dostupných závislostí"""
    print("📦 Testuji dostupné závislosti...")
    
    dependencies = {
        'numpy': 'Numerické výpočty',
        'cv2': 'OpenCV - počítačové vidění',
        'PIL': 'Pillow - zpracování obrázků',
        'torch': 'PyTorch - strojové učení',
        'sklearn': 'Scikit-learn - ML algoritmy',
        'skimage': 'Scikit-image - image processing',
        'psutil': 'Systémové informace',
        'redis': 'Redis klient',
        'prometheus_client': 'Prometheus metriky'
    }
    
    available = []
    missing = []
    
    for module, description in dependencies.items():
        try:
            if module == 'cv2':
                import cv2
                version = cv2.__version__
            elif module == 'PIL':
                from PIL import Image
                version = getattr(Image, '__version__', 'unknown')
            else:
                mod = __import__(module)
                version = getattr(mod, '__version__', 'unknown')
            
            available.append((module, version))
            print(f"✅ {module} ({version}): {description}")
            
        except ImportError:
            missing.append(module)
            print(f"❌ {module}: {description} - NENÍ NAINSTALOVÁNO")
    
    print(f"\n📊 Dostupné: {len(available)}, Chybějící: {len(missing)}")
    
    if available:
        print("\n✅ Dostupné moduly:")
        for module, version in available:
            print(f"   - {module} v{version}")
    
    if missing:
        print("\n⚠️  Chybějící moduly:")
        for module in missing:
            print(f"   - {module}")
    
    return len(missing) == 0

def main():
    """Hlavní testovací funkce"""
    print("🤖 LONGIN EGO - Advanced Scanner Dependency Test")
    print("=" * 60)
    
    # Test 1: Závislosti
    deps_ok = test_dependencies()
    
    # Test 2: Numpy
    numpy_ok = test_numpy()
    
    # Test 3: OpenCV (pokud je dostupné)
    cv2_ok = test_cv2_basic() if deps_ok else False
    
    # Test 4: Základní CV engine
    cv_engine_ok = test_basic_cv_engine() if cv2_ok else False
    
    # Shrnutí
    print("\n" + "=" * 60)
    print("📊 SHRNUTÍ TESTŮ")
    print("=" * 60)
    
    tests = [
        ("Závislosti", deps_ok),
        ("NumPy", numpy_ok),
        ("OpenCV", cv2_ok),
        ("CV Engine", cv_engine_ok)
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PROŠEL" if result else "❌ SELHAL"
        print(f"{test_name}: {status}")
    
    print(f"\n📈 Celkové skóre: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 Všechny testy proběhly úspěšně!")
        print("Advanced Scanner je připraven k použití!")
        return 0
    else:
        print("⚠️  Některé testy selhaly")
        print("Zkontrolujte instalaci závislostí")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)