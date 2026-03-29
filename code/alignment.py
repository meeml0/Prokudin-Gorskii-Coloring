import numpy as np
import cv2
from utils import ssd_metric, ncc_metric

def align_channels(reference, target, search_range=15, metric='ncc', edge_crop=0.1):
    """
    Target (hedef) kanalı reference (referans) kanalına hizalar (SSD veya NCC ile).
    Boyutu çok büyük olmayan .jpg dosyaları için yeterlidir.
    """
    h, w = reference.shape
    crop_h = int(h * edge_crop)
    crop_w = int(w * edge_crop)
    
    # Görüntülerin dış çeperlerinde film kaynaklı kalın siyah çizgiler vardır.
    # Bunların metriği şaşırtmaması için iç kısımdan temiz bir bölge (crop) alıyoruz.
    ref_crop = reference[crop_h:h-crop_h, crop_w:w-crop_w]
    
    # NCC'de en büyük, SSD'de en küçük değeri bulmak istiyoruz.
    best_score = float('-inf') if metric == 'ncc' else float('inf')
    best_dx, best_dy = 0, 0
    
    for dy in range(-search_range, search_range + 1):
        for dx in range(-search_range, search_range + 1):
            
            # Hedefi geçici olarak kaydır
            shifted = np.roll(target, shift=dy, axis=0)
            shifted = np.roll(shifted, shift=dx, axis=1)
            
            # Referansta aldığımız aynı bölgeyi hedeften de al
            shifted_crop = shifted[crop_h:h-crop_h, crop_w:w-crop_w]
            
            # Skoru hesapla
            if metric == 'ncc':
                score = ncc_metric(ref_crop, shifted_crop)
                if score > best_score:
                    best_score = score
                    best_dx, best_dy = dx, dy
            else: # ssd
                score = ssd_metric(ref_crop, shifted_crop)
                if score < best_score:
                    best_score = score
                    best_dx, best_dy = dx, dy
                    
    return best_dx, best_dy

def align_pyramid(reference, target, metric='ncc', depth=4):
    """
    Yüksek çözünürlüklü .tif görüntüleri için Görüntü Piramidi (Image Pyramid) algoritması.
    Aksi takdirde büyük resimlerde [-15, 15] yerine [-150, 150] aramak günler sürer.
    Bu algoritma resmi küçülterek kaba aramayı saniyeler içinde yapar, sonra büyüterek hassas ayar çeker.
    """
    # Temel (Rekürsif çıkış) durum: Maksimum derinliğe ulaştık veya resim çok ufaldı
    if depth == 0 or reference.shape[0] < 200 or reference.shape[1] < 200:
        return align_channels(reference, target, search_range=15, metric=metric)
    
    # 1. Görüntüyü boyut olarak yarıya (%50) küçült
    ref_half = cv2.resize(reference, (reference.shape[1] // 2, reference.shape[0] // 2))
    target_half = cv2.resize(target, (target.shape[1] // 2, target.shape[0] // 2))
    
    # 2. Rekürsif olarak alt piramitten hizalamayı iste
    dx_half, dy_half = align_pyramid(ref_half, target_half, metric, depth - 1)
    
    # 3. Yarı-küçük resimde bulduğumuz kayma miktarını, resim 2 kat büyük olduğu için 2 ile çarp
    dx_base = dx_half * 2
    dy_base = dy_half * 2
    
    # 4. Asıl hedefi (bulunan büyük adımlar kadar) önceden kaydır
    pre_shifted_target = np.roll(target, shift=dy_base, axis=0)
    pre_shifted_target = np.roll(pre_shifted_target, shift=dx_base, axis=1)
    
    # 5. Kaba aramayı bitirdik, şimdi ince (hassas) ayar için sadece dar bir pencerede [-3, 3] arama yapıyoruz
    h, w = reference.shape
    crop_h = int(h * 0.1)
    crop_w = int(w * 0.1)
    ref_crop = reference[crop_h:h-crop_h, crop_w:w-crop_w]
    
    best_score = float('-inf') if metric == 'ncc' else float('inf')
    best_dx_local, best_dy_local = 0, 0
    search_range_small = 3
    
    for dy in range(-search_range_small, search_range_small + 1):
        for dx in range(-search_range_small, search_range_small + 1):
            shifted = np.roll(pre_shifted_target, shift=dy, axis=0)
            shifted = np.roll(shifted, shift=dx, axis=1)
            shifted_crop = shifted[crop_h:h-crop_h, crop_w:w-crop_w]
            
            if metric == 'ncc':
                score = ncc_metric(ref_crop, shifted_crop)
                if score > best_score:
                    best_score = score
                    best_dx_local, best_dy_local = dx, dy
            else:
                score = ssd_metric(ref_crop, shifted_crop)
                if score < best_score:
                    best_score = score
                    best_dx_local, best_dy_local = dx, dy
                    
    # Toplam kayma = Alt katmanlardan gelen kaba kayma + mevcut katmandaki ince kayma
    return dx_base + best_dx_local, dy_base + best_dy_local