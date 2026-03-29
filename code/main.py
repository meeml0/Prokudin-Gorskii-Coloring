import argparse
import time
import os
from pathlib import Path
import cv2

# Kendi yazdığımız modüllerden import ediyoruz
from utils import load_image, split_image, create_color_image, apply_alignment
from alignment import align_channels, align_pyramid
from enhancement import enhance_image, auto_crop

def process_image(input_path, output_dir, metric='ncc', use_pyramid=False):
    """
    Ana hatlarıyla tek bir fotoğraf için baştan sona iş akışı:
    Oku -> Böl -> Hizala -> Renklendir -> Temizle -> Kaydet
    """
    print(f"\n{'='*70}")
    print(f"İşleniyor: {input_path.name}")
    print(f"{'='*70}")
    
    start_time = time.time()
    
    # 1. Görüntüyü Yükle ve Böl
    img = load_image(str(input_path))
    b, g, r = split_image(img) # Yukarıdan Aşağıya: B, G, R
    print(f"  -> ({img.shape[1]}x{img.shape[0]}) boyutundaki görüntü 3 kanala paylaştırıldı.")
    
    # 2. Hizalama Stratejisi
    print(f"  -> {metric.upper()} metriği ile hizalama analizi yapılıyor...")
    
    # Eğer dosya formati .tif, .tiff ise veya boyut büyükse Görüntü Piramidi (Pyramid) gereklidir, 
    # çünkü küçük aralık taraması büyük resimlerde işe yaramaz.
    is_large_image = input_path.suffix.lower() in ['.tif', '.tiff'] or max(b.shape) > 1000
    
    if is_large_image or use_pyramid:
        print("  |   Büyük format tespit edildi. Hızlı tarama için Image Pyramid taktiği uygulanıyor...")
        dx_g, dy_g = align_pyramid(b, g, metric=metric, depth=4)
        dx_r, dy_r = align_pyramid(b, r, metric=metric, depth=4)
    else:
        print("  |   Normal çözünürlük tespit edildi. Standart kaydırma algoritması uygulanıyor...")
        dx_g, dy_g = align_channels(b, g, search_range=15, metric=metric)
        dx_r, dy_r = align_channels(b, r, search_range=15, metric=metric)
        
    print(f"  -> Yeşil Kanal Gerekli Kaydırma: [X: {dx_g}, Y: {dy_g}]")
    print(f"  -> Kırmızı Kanal Gerekli Kaydırma: [X: {dx_r}, Y: {dy_r}]")
    
    # Kanalları gerçek anlamda kaydır
    g_aligned = apply_alignment(g, dx_g, dy_g)
    r_aligned = apply_alignment(r, dx_r, dy_r)
    
    # 3. Renkli Görüntüyü Oluştur
    print("  -> Matrisler RGB olarak istifleniyor...")
    img_unaligned = create_color_image(b, g, r) # Orjinal, kaymış hali
    img_aligned = create_color_image(b, g_aligned, r_aligned) # Düzeltilmiş hali
    
    # 4. Görüntü İyileştirme ve Temizlik
    print("  -> Kenarlar tıraşlanıyor ve filtreler ile renk zenginleştiriliyor...")
    img_unaligned_cropped = auto_crop(img_unaligned)
    img_aligned_cropped = auto_crop(img_aligned)
    img_enhanced = enhance_image(img_aligned_cropped)
    
    # 5. Disk'e Yaz
    base_name = input_path.stem
    
    # *NOT: OpenCV .imwrite fonksiyonu matrisleri RGB değil de BGR formatında bekler.
    # O yüzden kayıt esnasında cv2.COLOR_RGB2BGR dönüşümü yapmak zorundayız ki renkler mavi çıkmasın.
    cv2.imwrite(os.path.join(output_dir, f"{base_name}_unaligned.jpg"), cv2.cvtColor(img_unaligned_cropped, cv2.COLOR_RGB2BGR))
    cv2.imwrite(os.path.join(output_dir, f"{base_name}_aligned.jpg"), cv2.cvtColor(img_aligned_cropped, cv2.COLOR_RGB2BGR))
    cv2.imwrite(os.path.join(output_dir, f"{base_name}_enhanced.jpg"), cv2.cvtColor(img_enhanced, cv2.COLOR_RGB2BGR))
    
    elapsed_time = time.time() - start_time
    print(f"  --> Başarılı! Toplam Süre: {elapsed_time:.2f} saniye")
    
    # Sonuçların raporlanması için değerleri döndürüyoruz.
    return {
        'image': base_name,
        'g_shift': (dx_g, dy_g),
        'r_shift': (dx_r, dy_r),
        'time': elapsed_time
    }


def main():
    parser = argparse.ArgumentParser(description='Prokudin-Gorskii Renklendirme Sistemi')
    parser.add_argument('--input', default='../data', help='Girdi görüntüsünün veya klasörünün yolu')
    parser.add_argument('--output', default='../results', help='Çıktı klasörünün konumu')
    parser.add_argument('--metric', default='ncc', choices=['ssd', 'ncc'], help='Hesaplamada kullanılacak metrik. Varsayılan ncc dir.')
    parser.add_argument('--pyramid', action='store_true', help='Küçük resimlerde dahi "Image Pyramid" stratejisini devreye zorlar.')
    
    args = parser.parse_args()
    
    os.makedirs(args.output, exist_ok=True)
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"\nHata: Belirtilen girdi yolu ({args.input}) bulunamadı. Lütfen kontrol edin.")
        return
        
    # Girilen değer bir dosya ise sadece onu, klasör ise klasör içindeki resimleri bul.
    if input_path.is_file():
        files = [input_path]
    else:
        files = list(input_path.glob('*.jpg')) + list(input_path.glob('*.jpeg')) + list(input_path.glob('*.tif'))
        
    if not files:
        print(f"\nUyarı: '{args.input}' klasörü içerisinde .jpg, .jpeg veya .tif bulunamadı. Lütfen klasöre resimleri koyduğunuzdan emin olun.")
        return
        
    print(f"\n* Prokudin-Gorskii Hizalama Programı Başlatılıyor... *")
    print(f"* Toplam İşlenecek Dosya: {len(files)}")
    print(f"* Seçilen Metrik: {args.metric.upper()}")
    print("-" * 50)
    
    results = []
    
    # Liste içindeki klasör dosyalarını sırayla döndür process_image e yolla.
    for f in files:
        try:
            res = process_image(f, args.output, metric=args.metric, use_pyramid=args.pyramid)
            results.append(res)
        except Exception as e:
            print(f" [!] {f.name} dosyası işlenirken hata oluştu: {str(e)}")
            
            
    # Son Olarak Tüm İşlemlerin Rapor Tablosunu Bastıralım
    if results:
        print(f"\n\n{'='*76}")
        print(f"  ÖZET HİZALAMA KAYITLARI ({args.metric.upper()} Algoritması)")
        print(f"{'='*76}")
        print(f"{'Görüntü Adı':<25} | {'Yeşil X,Y Kaydırması':<20} | {'Kırmızı X,Y Kaydırma':<20} | {'Süre (sn)':<10}")
        print(f"{'-'*76}")
        
        for r in results:
            g_str = f"{r['g_shift'][0]:>3}, {r['g_shift'][1]:>3}"
            r_str = f"{r['r_shift'][0]:>3}, {r['r_shift'][1]:>3}"
            print(f"{r['image']:<25} | {g_str:<20} | {r_str:<20} | {r['time']:<10.2f}")

if __name__ == '__main__':
    main()