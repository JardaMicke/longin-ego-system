import pytest
import asyncio
import numpy as np
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime
import json
import cv2

from kernel.scanner.advanced_scanner import AdvancedScanner, ScannerConfig, VisualChange, ComputerVisionEngine

# Mock pro cv2
@pytest.fixture
def mock_cv2():
    with patch('kernel.scanner.advanced_scanner.cv2') as mock:
        # Nastavení návratových hodnot pro cv2 funkce
        mock.absdiff.return_value = np.zeros((100, 100), dtype=np.uint8)
        mock.cvtColor.return_value = np.zeros((100, 100), dtype=np.uint8)
        mock.threshold.return_value = (0, np.zeros((100, 100), dtype=np.uint8))
        mock.findContours.return_value = ([], None)
        mock.contourArea.return_value = 100.0
        mock.boundingRect.return_value = (0, 0, 10, 10)
        mock.mean.return_value = 128.0
        mock.matchTemplate.return_value = np.array([[0.9]])
        yield mock

# Mock pro EasyOCR
@pytest.fixture
def mock_easyocr():
    # Patchujeme přímo easyocr.Reader, protože modul je importován dynamicky
    # Pokud easyocr není nainstalován v prostředí testu, musíme ho mockovat v sys.modules
    try:
        import easyocr
        with patch('easyocr.Reader') as mock_reader:
            reader = MagicMock()
            reader.readtext.return_value = [([0, 0, 10, 10], "Detected Text", 0.9)]
            mock_reader.return_value = reader
            yield mock_reader
    except ImportError:
        # Fallback pokud easyocr není nainstalován (což by nemělo nastat po instalaci requirements)
        with patch.dict('sys.modules', {'easyocr': MagicMock()}):
            import easyocr
            reader = MagicMock()
            reader.readtext.return_value = [([0, 0, 10, 10], "Detected Text", 0.9)]
            easyocr.Reader.return_value = reader
            yield easyocr

# Mock pro Torch/YOLO
@pytest.fixture
def mock_torch():
    with patch('kernel.scanner.advanced_scanner.torch') as mock:
        model = MagicMock()
        # Mockování výsledku YOLO
        results = MagicMock()
        df = MagicMock()
        df.empty = False
        df.iloc.__getitem__.return_value = {'name': 'button', 'confidence': 0.95}
        results.pandas.return_value.xyxy = [df]
        model.return_value = results
        
        mock.hub.load.return_value = model
        mock.cuda.is_available.return_value = False
        yield mock

@pytest.fixture
def scanner_config():
    return ScannerConfig(
        screenshot_interval=0.1,
        enable_ocr=True,
        enable_ml=True,
        memory_limit_mb=100
    )

@pytest.fixture
def redis_mock():
    mock = AsyncMock()
    mock.publish = AsyncMock()
    return mock

@pytest.mark.asyncio
async def test_initialization(scanner_config, redis_mock, mock_torch, mock_easyocr):
    """Test inicializace skeneru"""
    scanner = AdvancedScanner(config=scanner_config, redis_client=redis_mock)
    await scanner.initialize()
    
    assert scanner.cv_engine.model is not None
    assert scanner.cv_engine.ocr_engine is not None
    assert scanner.redis_client == redis_mock

@pytest.mark.asyncio
async def test_ocr_extraction(scanner_config, redis_mock, mock_easyocr):
    """Test OCR extrakce"""
    scanner = AdvancedScanner(config=scanner_config, redis_client=redis_mock)
    
    # Manuální nastavení OCR engine
    # mock_easyocr je mock třídy Reader, voláním získáme instanci
    scanner.cv_engine.ocr_engine = mock_easyocr()
    
    # Testovací obrázek
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    
    text = scanner.cv_engine._extract_text(img)
    assert text == "Detected Text"

@pytest.mark.asyncio
async def test_element_identification(scanner_config, redis_mock, mock_torch):
    """Test identifikace elementu pomocí ML"""
    scanner = AdvancedScanner(config=scanner_config, redis_client=redis_mock)
    
    # Manuální nastavení modelu
    scanner.cv_engine.model = mock_torch.hub.load()
    
    # Testovací obrázek
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    
    element_type = scanner.cv_engine._identify_element(img)
    assert "button" in element_type

@pytest.mark.asyncio
async def test_detect_changes(scanner_config, redis_mock, mock_cv2):
    """Test detekce změn"""
    scanner = AdvancedScanner(config=scanner_config, redis_client=redis_mock)
    
    # Mockování metody calculate_similarity
    scanner.cv_engine.calculate_similarity = MagicMock(return_value=0.5)
    
    # Mockování findContours pro vrácení jednoho obdélníku
    mock_cv2.findContours.return_value = ([np.array([[[0,0]], [[10,0]], [[10,10]], [[0,10]]])], None)
    mock_cv2.boundingRect.return_value = (0, 0, 10, 10)
    mock_cv2.contourArea.return_value = 100.0
    
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.ones((100, 100, 3), dtype=np.uint8) * 255
    
    changes = scanner.cv_engine.detect_changes(img1, img2)
    
    # Měli bychom najít alespoň jednu změnu (v závislosti na nastavení mocků)
    # V tomto testu ověřujeme, že se volají správné metody CV2
    mock_cv2.absdiff.assert_called()
    mock_cv2.threshold.assert_called()
    mock_cv2.findContours.assert_called()

@pytest.mark.asyncio
async def test_find_element_by_template(scanner_config, redis_mock, mock_cv2):
    """Test hledání elementu podle šablony"""
    scanner = AdvancedScanner(config=scanner_config, redis_client=redis_mock)
    
    # Nastavení posledního screenshotu
    scanner.last_screenshot = np.zeros((100, 100, 3), dtype=np.uint8)
    
    # Mockování capture_screenshot pro jistotu
    scanner.screenshot_capture.capture_screenshot = AsyncMock(return_value=np.zeros((100, 100, 3), dtype=np.uint8))
    
    template = np.zeros((10, 10, 3), dtype=np.uint8)
    
    matches = scanner.find_element_by_template(template)
    
    assert len(matches) > 0
    # Ověření formátu návratové hodnoty (x1, y1, x2, y2, score)
    assert len(matches[0]) == 5
    assert matches[0][4] >= 0.8  # Default threshold

@pytest.mark.asyncio
async def test_change_description_generation(scanner_config, redis_mock):
    """Test generování popisu změny"""
    scanner = AdvancedScanner(config=scanner_config, redis_client=redis_mock)
    
    old_region = np.zeros((10, 10, 3), dtype=np.uint8)
    new_region = np.zeros((10, 10, 3), dtype=np.uint8)
    
    desc = scanner.cv_engine._generate_change_description(
        old_region, 
        new_region, 
        'modified', 
        text_content="Hello World", 
        element_type="Button"
    )
    
    assert "Změněn obsah" in desc
    assert "Typ: Button" in desc
    assert "Text: 'Hello World'" in desc

if __name__ == "__main__":
    asyncio.run(pytest.main(["-v", __file__]))
