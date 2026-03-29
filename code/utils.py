import cv2
import numpy as np

def load_image(path):
    """
    Görüntüyü diskten gri tonlamalı (siyah-beyaz) okur.
    """
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Görüntü bulunamadı veya okunamadı: {path}")
    return img

def split_image(img):
    """
    Dikey formattaki siyah-beyaz plaka görüntüsünü 3 eşit parsele böler.
    Yukarıdan aşağıya sıralama standart Prokudin-Gorskii plakalarında [Mavi, Yeşil, Kırmızı] şeklindedir.
    """
    h = img.shape[0]
    third_h = h // 3
    b = img[0:third_h, :]
    g = img[third_h:2*third_h, :]
    r = img[2*third_h:3*third_h, :]
    return b, g, r

def create_color_image(b, g, r):
    """
    Ayrı kanalları alıp tek bir 3 boyutlu RGB renkli görüntü matrisi haline getirir.
    (Hizalanmamış veya hizalanmış kanallar verilebilir)
    """
    # RGB sırasıyla üst üste istifliyoruz.
    return np.dstack((r, g, b))

def apply_alignment(channel, dx, dy):
    """
    Bulunan dx (x ekseni - sütun) ve dy (y ekseni - satır) kaydırma miktarına göre kanalı yuvarlar (roll).
    """
    # Önce Y ekseninde (aşağı/yukarı)
    shifted = np.roll(channel, shift=dy, axis=0)
    # Sonra X ekseninde (sağa/sola)
    shifted = np.roll(shifted, shift=dx, axis=1)
    return shifted

def ssd_metric(ref, target):
    """
    SSD (Sum of Squared Differences) - Kareler Farkı Toplamı Algoritması
    Piksel bazlı çıkartma yapıp karelerini alır. SSD ne kadar küçükse (0'a yakınsa), görüntüler o kadar çok benziyordur.
    Taşmaları önlemek için int8'den float32'ye dönüşüm şarttır.
    """
    diff = ref.astype(np.float32) - target.astype(np.float32)
    return np.sum(diff ** 2)

def ncc_metric(ref, target):
    """
    NCC (Normalized Cross-Correlation) - Normalize Edilmiş Çapraz Korelasyon Algoritması
    Karşıtlık ve parlaklık farklarından etkilenmeden iki matrisin şekilsel benzerliğini ölçer.
    Sonuç 1'e ne kadar yakınsa, o kadar benzerdir.
    """
    ref_f = ref.astype(np.float32)
    target_f = target.astype(np.float32)
    
    # Görüntüleri kendi ortalamalarından çıkararak sıfır-merkezli hale getiriyoruz
    ref_norm = ref_f - np.mean(ref_f)
    target_norm = target_f - np.mean(target_f)
    
    # Standart sapma paydalarını hesaplıyoruz
    ref_std_sum = np.sum(ref_norm ** 2)
    target_std_sum = np.sum(target_norm ** 2)
    
    # Sıfıra bölünme hatasını(divide by zero) çözmek için koruma
    if ref_std_sum == 0 or target_std_sum == 0:
        return 0
        
    numerator = np.sum(ref_norm * target_norm)
    denominator = np.sqrt(ref_std_sum * target_std_sum)
    
    return numerator / denominator
