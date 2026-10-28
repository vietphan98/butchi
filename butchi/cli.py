"""Dòng lệnh: python -m butchi anh.jpg"""
import argparse
import os
import sys
import time

import cv2
import numpy as np

from .styles import KIEU, _resize_max

# OpenCV không vẽ được dấu tiếng Việt, nên nhãn trên ảnh dùng chữ không dấu
NHAN = {"goc": "ANH GOC", "but-chi": "BUT CHI", "chi-mau": "CHI MAU",
        "hoat-hinh": "HOAT HINH", "mau-nuoc": "MAU NUOC"}


def _nhan(img, text):
    out = img.copy()
    h = max(28, img.shape[0] // 14)
    cv2.rectangle(out, (0, 0), (out.shape[1], h), (0, 0, 0), -1)
    cv2.putText(out, text, (12, int(h * 0.75)), cv2.FONT_HERSHEY_DUPLEX,
                h / 40, (255, 255, 255), 2, cv2.LINE_AA)
    return out


def ghep_luoi(tiles):
    """Ghép các ảnh cùng kích thước thành lưới 2 cột (hoặc 3 nếu có 5-6 ảnh)."""
    cols = 3 if len(tiles) > 4 else 2
    h, w = tiles[0].shape[:2]
    while len(tiles) % cols:
        tiles.append(np.full((h, w, 3), 255, np.uint8))
    rows = [np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]
    return np.vstack(rows)


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
