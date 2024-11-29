import pytest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

def test_basic_import():
    from eon.core.fhe import engine
    assert True

def test_config():
    from eon.utils.config import Config
    config = Config()  # 或检查实际的配置初始化方法
    assert config is not None

def test_logger():
    import logging
    logger = logging.getLogger(__name__)
    assert logger is not None