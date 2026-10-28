"""Tạo một ảnh mẫu tự vẽ (bầu trời, mặt trời, núi, nhà) để thử nhanh khi chưa có ảnh."""
import cv2
import numpy as np

h, w = 720, 960
img = np.zeros((h, w, 3), np.uint8)
for y in range(h):
    t = y / h
    img[y] = (int(235 - 80 * t), int(190 - 40 * t), int(120 + 60 * t))
cv2.circle(img, (760, 150), 80, (80, 200, 255), -1)
cv2.fillPoly(img, [np.array([[0, 520], [260, 260], [520, 520]])], (90, 120, 70))
cv2.fillPoly(img, [np.array([[300, 540], [600, 230], [960, 540]])], (70, 100, 60))
cv2.rectangle(img, (0, 520), (w, h), (60, 160, 90), -1)
cv2.rectangle(img, (380, 430), (560, 600), (40, 90, 200), -1)
cv2.fillPoly(img, [np.array([[360, 430], [470, 340], [580, 430]])], (30, 40, 150))
cv2.rectangle(img, (450, 510), (495, 600), (30, 60, 110), -1)
cv2.rectangle(img, (400, 460), (440, 495), (200, 230, 250), -1)
rng = np.random.default_rng(1)
img = np.clip(img + rng.normal(0, 4, img.shape), 0, 255).astype(np.uint8)
cv2.imwrite("examples/anh_mau.jpg", img)
print("Đã tạo examples/anh_mau.jpg")
