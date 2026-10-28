import cv2
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
    assert ghep_luoi(list(t)).shape == (20, 80, 3)


def test_nhan_co_dau():
    from butchi.cli import _nhan
    img = np.zeros((200, 300, 3), np.uint8)
    out = _nhan(img, "Hoạt hình")
    assert out.shape == img.shape and out[:16].max() == 255


def test_chi_mau_khac_anh_goc():
    from butchi.styles import chi_mau
    rng = np.random.default_rng(1)
    img = cv2.GaussianBlur(rng.integers(0, 255, (120, 160, 3), dtype=np.uint8), (0, 0), 6)
    assert np.abs(chi_mau(img).astype(int) - img).mean() > 10
