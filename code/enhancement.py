import numpy as np
import cv2

def enhance_image(image):
    """
    Görüntü kalitesini artırmak için basit kontrast germe (contrast stretching) uygular.
    Piksellerin %1 ve %99'luk uç kısımlarını kırparak parlaklık/karanlık dengesini kurar.
    (Ek kredi görevi veya genel parlatma için)
    """
    enhanced = np.zeros_like(image, dtype=np.uint8)
    
    for i in range(3):  # R, G, B kanalları için ayrı ayrı dolaş
        channel = image[:, :, i]
        
        # Sınır dışı ekstrem parlak veya siyah hatalı pikselleri devre dışı bırak
        p2, p98 = np.percentile(channel, (2.0, 98.0))
        channel_clipped = np.clip(channel, p2, p98)
        
        # Piksellerin geri kalanını 0 ile 255 arasına esnet
        channel_normalized = cv2.normalize(channel_clipped, None, 0, 255, cv2.NORM_MINMAX)
        enhanced[:, :, i] = np.uint8(channel_normalized)
        
    return enhanced

def auto_crop(image):
    """
    Görüntünün kenarlarında kalan 
    siyah bantları ve uyumsuz renk şeritlerini silmek için basitçe kenarlardan %5 kesme (tıraşlama) yapar.
    """
    h, w = image.shape[:2]
    crop_h = int(h * 0.05)
    crop_w = int(w * 0.05)
    
    # Resmin merkezinden kırpılmış parçayı al
    cropped = image[crop_h:h-crop_h, crop_w:w-crop_w]
    return cropped
