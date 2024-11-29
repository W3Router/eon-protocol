import pytest
import sys
import os

# 添加源码目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

def test_basic_import():
    from eon.core.fhe import engine
    assert True

def test_config():
    from eon.utils.config import load_config
    config = load_config()
    assert config is not None

def test_logger():
    from eon.utils.logger import get_logger
    logger = get_logger(__name__)
    assert logger is not None