\# 🎨 Prokudin-Gorskii Görüntü Renklendirme Projesi



\## 📌 1. Giriş ve Problem Tanımı

Bu projenin amacı, Sergei Mikhailovich Prokudin-Gorskii tarafından çekilmiş üç farklı siyah-beyaz görüntüyü (Mavi, Yeşil, Kırmızı kanallar) kullanarak orijinal renkli görüntüyü yeniden oluşturmaktır.



Çekim sırasında oluşan titreşimler ve görüntülerin tek bir cam plaka üzerinde hizalanmamış olması nedeniyle kanallar arasında kaymalar bulunmaktadır. Bu proje, söz konusu kaymaları sayısal yöntemlerle düzelterek kanalları milimetrik doğrulukla hizalamayı hedefler.



\---



\## ⚙️ 2. Kullanılan Yöntemler ve Algoritmalar



\### 🧩 Kanal Ayrıştırma

Verilen görüntü dikey olarak üç eşit parçaya bölünerek:

\- \*\*Mavi (B)\*\*

\- \*\*Yeşil (G)\*\*

\- \*\*Kırmızı (R)\*\*  

kanalları elde edilmiştir.



Hizalama işlemlerinde \*\*Mavi kanal referans\*\* alınmıştır.



\---



\### 📊 Benzerlik Metrikleri



\#### ✔ SSD (Sum of Squared Differences)

İki görüntü arasındaki piksel farklarının karelerinin toplamını hesaplar.



\#### ✔ NCC (Normalized Cross-Correlation) \*(Varsayılan)\*

Parlaklık farklarından bağımsız olarak iki görüntü arasındaki benzerliği ölçer.



> NCC metriği kullanılarak en yüksek benzerlik değerine ulaşan `(x, y)` kaydırması bulunur.



\---



\### 🏔 Görüntü Piramidi (Image Pyramid)

Yüksek çözünürlüklü `.tif` görüntülerde büyük kaymaları bulabilmek için:



1\. Görüntü çözünürlüğü kademeli olarak düşürülür  

2\. Düşük çözünürlükte kaba hizalama yapılır  

3\. Orijinal çözünürlükte ince ayar uygulanır  



Bu yöntem:

\- Hesaplama süresini azaltır

\- Daha doğru sonuç elde edilmesini sağlar



\---



\### ✂️ Otomatik Kırpma ve İyileştirme



\#### 🔹 Auto-Crop

Kenarlarda oluşan siyah bantları kaldırmak için görüntünün %5’i kırpılır.



\#### 🔹 Contrast Stretching

\- Renk derinliği artırılır  

\- Karanlık görüntüler dengelenir  



\---



\## 📂 3. Çıktılar ve Dosya Yapısı



Her görüntü için 3 farklı çıktı üretilir:



\### 🔴 `{isim}\_unaligned.jpg`

\- Kanallar doğrudan üst üste bindirilir  

\- Renk kaymaları ve bulanıklık görülür  

\- Referans (başlangıç) çıktıdır  



\---



\### 🟢 `{isim}\_aligned.jpg`

\- Algoritma ile hizalanmış görüntüdür  

\- Renkler doğru konumda ve nettir  



\---



\### 🟣 `{isim}\_enhanced.jpg`

\- Hizalanmış görüntünün geliştirilmiş halidir  

\- Siyah kenarlar kırpılmıştır  

\- Kontrast iyileştirilmiştir  

\- Final çıktıdır  



\---



\## 🚀 4. Sonuç



Bu proje kapsamında geliştirilen algoritma:



\- `.jpg` ve `.tif` formatındaki görüntülerde çalışır  

\- Kanalları \*\*otomatik ve yüksek doğrulukla hizalar\*\*  

\- SSD ve NCC metrikleri başarıyla uygulanmıştır  

\- Görüntü piramidi sayesinde performans optimize edilmiştir  



Sonuç olarak, tarihi Prokudin-Gorskii fotoğrafları başarılı bir şekilde renklendirilmiş ve yüksek kaliteli çıktılar elde edilmiştir.



\---



\## 🛠 Kullanım (Opsiyonel)



```bash

python main.py --input image.tif

.