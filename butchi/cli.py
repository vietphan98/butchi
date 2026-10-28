"""Dòng lệnh: python -m butchi anh.jpg"""
import argparse
import os
import sys
import time

import cv2
import numpy as np

from .styles import KIEU, _resize_max

FONT = os.path.join(os.path.dirname(__file__), "fonts", "BeVietnamPro-SemiBold.ttf")
NHAN = {"goc": "Ảnh gốc", "but-chi": "Bút chì", "chi-mau": "Chì màu",
        "hoat-hinh": "Hoạt hình", "mau-nuoc": "Màu nước"}


def _nhan(img, text):
    """Vẽ nhãn có dấu tiếng Việt (OpenCV không hỗ trợ nên dùng Pillow + font Be Vietnam Pro)."""
    from PIL import Image, ImageDraw, ImageFont
    out = img.copy()
    h = max(28, img.shape[0] // 12)
    cv2.rectangle(out, (0, 0), (out.shape[1], h), (0, 0, 0), -1)
    pil = Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))
    font = ImageFont.truetype(FONT, int(h * 0.62))
    ImageDraw.Draw(pil).text((max(10, h // 3), h // 2), text, font=font,
                             fill=(255, 255, 255), anchor="lm")
    return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)


def ghep_luoi(tiles):
    """Ghép ảnh cùng kích thước, không để ô trống.

    5 ảnh: ảnh gốc to (gấp đôi) bên trái, 4 kiểu xếp 2x2 bên phải.
    Số ảnh khác: xếp thành một hàng ngang.
    """
    if len(tiles) == 5:
        h, w = tiles[0].shape[:2]
        big = cv2.resize(tiles[0], (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
        right = np.vstack([np.hstack(tiles[1:3]), np.hstack(tiles[3:5])])
        return np.hstack([big, right])
    return np.hstack(tiles)


def main(argv=None):
    p = argparse.ArgumentParser(prog="butchi",
                                description="Biến ảnh thường thành tranh vẽ tay, chạy offline.")
    p.add_argument("anh", help="đường dẫn ảnh đầu vào (jpg/png)")
    p.add_argument("-k", "--kieu", nargs="+", choices=list(KIEU), default=list(KIEU),
                   help="chọn kiểu tranh (mặc định: tất cả)")
    p.add_argument("-o", "--thu-muc", default="ket_qua", help="thư mục lưu kết quả")
    p.add_argument("--kich-thuoc", type=int, default=1080, help="cạnh dài tối đa (px)")
    a = p.parse_args(argv)

    img = cv2.imread(a.anh)
    if img is None:
        print(f"Không đọc được ảnh: {a.anh}", file=sys.stderr)
        return 1
    img = _resize_max(img, a.kich_thuoc)
    os.makedirs(a.thu_muc, exist_ok=True)
    ten = os.path.splitext(os.path.basename(a.anh))[0]

    tiles = [_nhan(img, NHAN["goc"])]
    t0 = time.time()
    for k in a.kieu:
        nhan, fn = KIEU[k]
        t = time.time()
        out = fn(img)
        path = os.path.join(a.thu_muc, f"{ten}_{k}.png")
        cv2.imwrite(path, out)
        print(f"  {nhan:<10} xong sau {time.time() - t:.1f}s -> {path}")
        tiles.append(_nhan(out, NHAN[k]))
    grid_path = os.path.join(a.thu_muc, f"{ten}_so_sanh.jpg")
    cv2.imwrite(grid_path, ghep_luoi(tiles), [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(f"Tổng thời gian: {time.time() - t0:.1f}s. Ảnh so sánh: {grid_path}")
    return 0
