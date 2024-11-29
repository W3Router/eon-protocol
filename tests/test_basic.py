# tests/test_basic.py
import pytest
import sys
import os

# 添加源码目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

def test_basic_import():
    import eon_protocol
    assert True

def test_tenseal():
    import tenseal as ts
    assert ts is not None