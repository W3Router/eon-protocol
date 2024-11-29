import pytest
import sys
import os

# 添加源码目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

def test_api_routes():
    from eon.api import routes
    assert routes is not None

def test_api_service():
    from eon.api.service import EONService
    assert EONService is not None