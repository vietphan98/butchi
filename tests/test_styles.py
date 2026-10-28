import numpy as np
from butchi.styles import KIEU
from butchi.cli import ghep_luoi


def test_moi_kieu_giu_kich_thuoc():
    rng = np.random.default_rng(0)
    img = rng.integers(0, 255, (120, 160, 3), dtype=np.uint8)
    for _, fn in KIEU.values():
        out = fn(img)
        assert out.shape == img.shape and out.dtype == np.uint8


def test_ghep_luoi():
    t = [np.zeros((10, 20, 3), np.uint8)] * 5
    assert ghep_luoi(list(t)).shape == (20, 60, 3)
