import pytest
import sys
import os
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

def test_tenseal():
    import tenseal as ts
    context = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=8192,
        coeff_mod_bit_sizes=[60, 40, 40, 60]
    )
    assert context is not None

def test_fhe_engine():
    from eon.core.fhe.engine import FHEEngine
    config = {
        'poly_modulus_degree': 8192,
        'coeff_mod_bit_sizes': [60, 40, 40, 60]
    }
    engine = FHEEngine(config)
    assert engine is not None