"""Các bộ lọc biến ảnh thành tranh. Mỗi hàm nhận ảnh BGR (numpy) và trả về ảnh BGR."""
import cv2
import numpy as np


def _resize_max(img, max_side=1280):
    h, w = img.shape[:2]
    scale = max_side / max(h, w)
    if scale < 1:
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    return img


def but_chi(img):
    """Tranh bút chì đen trắng: lấy ảnh xám chia cho bản làm mờ của ảnh âm bản."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    inv = 255 - gray
    blur = cv2.GaussianBlur(inv, (0, 0), sigmaX=8)
    sketch = cv2.divide(gray, 255 - blur, scale=256)
    # thêm chút vân giấy cho giống vẽ tay
    rng = np.random.default_rng(7)
    noise = rng.normal(0, 6, sketch.shape).astype(np.float32)
    sketch = np.clip(sketch.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    return cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)


def _net_gach(shape, goc, seed, do_dai=15):
    """Tạo vân nét gạch chéo như bút chì tô trên giấy."""
    rng = np.random.default_rng(seed)
    noise = rng.random(shape[:2]).astype(np.float32)
    k = np.zeros((do_dai, do_dai), np.float32)
    c = do_dai // 2
    dx, dy = np.cos(np.radians(goc)), np.sin(np.radians(goc))
    for t in np.linspace(-c, c, do_dai * 2):
        k[int(round(c + t * dy)), int(round(c + t * dx))] = 1
    k /= k.sum()
    s = cv2.filter2D(noise, -1, k)
    return cv2.normalize(s, None, 0, 1, cv2.NORM_MINMAX)


def chi_mau(img):
    """Bút chì màu: màu nhạt trên nền giấy trắng, tô bằng nét gạch chéo, viền chì đậm."""
    h, w = img.shape[:2]
    # màu phẳng, nhạt và hơi tươi như hộp chì màu
    base = cv2.pyrMeanShiftFiltering(img, 10, 30)
    hsv = cv2.cvtColor(base, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] = np.clip(hsv[..., 1] * 1.7, 0, 255)
    base = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32) / 255.0
    base = 0.9 * base + 0.1  # chì màu không đậm như ảnh chụp
    # mật độ tô: vùng tối tô dày, vùng sáng để lộ giấy trắng
    tone = 1.0 - cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    dens = np.clip(0.12 + 0.75 * tone, 0, 0.85)
    h1 = _net_gach((h, w), 35, 1, 25)
    h2 = _net_gach((h, w), -55, 2, 25)
    hatch = np.maximum((h1 > 1 - dens * 0.75).astype(np.float32),
                       (h2 > 1.05 - dens * 0.6).astype(np.float32) * 0.8)
    cover = hatch * 0.9
    cover = cv2.GaussianBlur(cover, (3, 3), 0)
    paper = np.full_like(base, 0.98)
    out = paper * (1 - cover[..., None]) + base * cover[..., None]
    # viền nét chì từ bản phác thảo
    sketch = cv2.cvtColor(but_chi(img), cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    out *= (0.35 + 0.65 * sketch)[..., None]
    # vân giấy
    rng = np.random.default_rng(5)
    out += rng.normal(0, 0.02, (h, w, 1)).astype(np.float32)
    return np.clip(out * 255, 0, 255).astype(np.uint8)


def hoat_hinh(img, so_mau=9):
    """Hoạt hình: gom màu bằng k-means + viền đen dày."""
    smooth = img
    for _ in range(3):
        smooth = cv2.bilateralFilter(smooth, 9, 75, 75)
    data = smooth.reshape(-1, 3).astype(np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 15, 1.0)
    _, labels, centers = cv2.kmeans(data, so_mau, None, criteria, 2, cv2.KMEANS_PP_CENTERS)
    quant = centers.astype(np.uint8)[labels.flatten()].reshape(img.shape)
    gray = cv2.medianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 7)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                  cv2.THRESH_BINARY, 9, 4)
    return cv2.bitwise_and(quant, quant, mask=edges)


def mau_nuoc(img):
    """Màu nước: làm phẳng màu, loang mép và tăng độ tươi."""
    base = cv2.pyrMeanShiftFiltering(img, 12, 40)
    base = cv2.edgePreservingFilter(base, flags=1, sigma_s=60, sigma_r=0.45)
    hsv = cv2.cvtColor(base, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] = np.clip(hsv[..., 1] * 1.25, 0, 255)
    base = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 40, 110)
    edges = cv2.GaussianBlur(255 - edges, (3, 3), 0).astype(np.float32) / 255.0
    edges = 0.65 + 0.35 * edges
    return np.clip(base.astype(np.float32) * edges[..., None], 0, 255).astype(np.uint8)


KIEU = {
    "but-chi": ("Bút chì", but_chi),
    "chi-mau": ("Chì màu", chi_mau),
    "hoat-hinh": ("Hoạt hình", hoat_hinh),
    "mau-nuoc": ("Màu nước", mau_nuoc),
}
