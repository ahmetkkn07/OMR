# Optik İşaret Tanıma

[English](https://github.com/ahmetkkn07/OMR)

OMR, anketler ve testler gibi belge formlarından insan tarafından işaretlenmiş verileri algılama sürecidir. Anketleri, çizgiler veya gölgeli alanlar şeklinde çoktan seçmeli sınav kağıtlarını okumak için kullanılır.

## Ön Koşullar
1. [Python](https://www.python.org/) kurulumunu gerçekleştirin.
2. Gerekli pypi paketlerini, aşağıdaki komutu bir terminalde çalıştırarak kurun.
  ```
  pip install -r requirements.txt
  ```
## Nasıl Çalışır
Ön koşulları tamamladıktan sonra repository'yi indirin veya klonlayın, klasörde terminali açın ve aşağıdaki komutu çalıştırın.
  ```
  python server.py
  ```
Tarayıcınızda [http://localhost:5000](http://localhost:5000) adresine gidin ve kullanmaya başlayın.

## Özellikler
* Görüntüden cevap anahtarı elde etme
* Doğru, yanlış ve boş soruları tespit etme
* Kağıtların üzerindeki isim alanlarını algılama

## Önizleme
![](preview.gif)

