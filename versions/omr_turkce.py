from imutils.perspective import four_point_transform
from imutils import contours
import numpy as np
import imutils
import cv2


def cevaplar(foto):
    CEVAPLAR = list()

    # fotoğraf yolunu değişkene aldık
    fotograf = cv2.imread(foto)

    # rgb renk uzayındaki fotoğrafı gri skalaya dönüştürüyoruz
    gri_foto = cv2.cvtColor(fotograf, cv2.COLOR_BGR2GRAY)

    # gürültüyü azaltmak için düzleştirme filtresi uyguluyoruz
    # canny ile kenar algılama yapabilmemiz için 5x5 Gaus Filtresi uygulamamız gerekiyor
    gauss = cv2.GaussianBlur(gri_foto, (5, 5), 0)

    # kenar algılama yapıyoruz, minimum değer 75, maximum değer 200
    kenarlar = cv2.Canny(gauss, 75, 200)

    # RETR_EXTERNAL: sadece en dıştaki kenarları almak için
    # CHAIN_APPROX_SIMPLE: yalnızca uç noktaları bırakır, örneğin dikdörtgen için 4 nokta
    sekiller = cv2.findContours(kenarlar.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)

    # görüntüdeki her bir şekli ayrı ayrı alıyoruz
    sekiller = imutils.grab_contours(sekiller)
    dokuman = None

    # eğer dizide şekiller varsa
    if len(sekiller) > 0:
        # cnts dizisini cv2.contourArea'ya göre bir algoritma ile azalan sırayla(revere=True) sıraladık
        sekiller = sorted(sekiller, key=cv2.contourArea, reverse=True)

        for sekil in sekiller:
            # her bir kapalı şeklin çevre uzunluğunu alıyoruz. True parametresi sadece kapalı şekillerin alınmasını sağlıyor
            # bu çevre uzunluğu, bir sonraki adımda epsilon değerini hesaplamak için kullanılacak
            cevre = cv2.arcLength(sekil, True)

            # epsilon değeri = çevre uzunluğu * 0.02
            # epsilon doğruluk oranı ile kapalı şekiller (True parametesi) oluşturuyoruz
            yaklasik_sekil = cv2.approxPolyDP(sekil, 0.02 * cevre, True)

            # şeklin 4 kenarı varsa fotoğraftaki kağıdı bulduk demektir
            if len(yaklasik_sekil) == 4:
                # kağıdı ata
                dokuman = yaklasik_sekil
                break

    yamuk = None
    kagit = None
    if dokuman is not None:
        # orijinal fotoğrafa ve gri tonlamalı fotoğrafa transform uygulayarak sadece kağıt olan kısmı elde ediyoruz
        kagit = four_point_transform(fotograf, dokuman.reshape(4, 2))
        yamuk = four_point_transform(gri_foto, dokuman.reshape(4, 2))
    else:
        kagit = fotograf
        yamuk = gri_foto

    # her piksel için eşik değeri uygulanır, eşik değerden küçükse 0, büyükse maksimum değer ayarlanır
    # burada eşik değerimiz THRESH_OTSU ile her fotoğraf için, fotoğrafın renk dağılımına göre optimum olarak ayarlanacaktır
    # maksimum değerimiz 255 olarak verilmiştir
    # THRESH_BINARY_INV parametresi sayesinde siyahlar beyaz, beyazlar siyah hale geliyor
    # threshold() fonksiyonu iki değer döndürür: ilki eşik değeri, ikinci eşik değeri uygulanmış fotoğraf
    # bu yüzden [1] ile ikinci değeri aldık
    esik_uygulanmis = cv2.threshold(yamuk, 0, 255,
                                    cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    #  RETR_EXTERNAL: sadece en dıştaki kenarları almak için
    # CHAIN_APPROX_SIMPLE: yalnızca uç noktaları bırakır, örneğin dikdörtgen için 4 nokta
    # burada artık aldığımız fotoğrafta değil kağıdı kesip eşik değeri uyguladığımız fotoğraftaki kenarları alıyoruz
    sekiller = cv2.findContours(esik_uygulanmis.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)

    # görüntüdeki her bir şekli ayrı ayrı alıyoruz
    sekiller = imutils.grab_contours(sekiller)

    # soruları tutacağımız diziyi tanımladık
    kutucuklar = []

    # şekiller içinde geziniyoruz
    for sekil in sekiller:

        # her bir şekil için sınırlandırıcı dikdörtgenin koordinatlarını belirliyoruz
        # w --> genişlik
        # h --> yükseklik
        # x,y koordinat ancak sağ üst köşeden başlayarak
        (x, y, w, h) = cv2.boundingRect(sekil)

        # aspect ratio = en boy oranını hesaplıyoruz --> genişlik/yükseklik
        oran = w / float(h)

        # eğer aşağıdaki değerlere uygunda bu cevap kutucuğudur ve diziye eklenir
        # ar >= 0.9 and ar <= 1.1 --> bu koşul en boy oranının yaklaşık 1 olup olmadığını kontrol eder
        # eğer en boy oranı 1 ise daireyi kapsayan kareyi bulduk demektir
        # w >= 20 and h >= 20 --> bu kontrol ise çok küçük şekillerin hesaba katılmamasını sağlar
        if w >= 20 and h >= 20 and oran >= 0.9 and oran <= 1.1:
            # eğer tüm koşullar sağladıysa kutucuğu bulduk demektir artık soruların bulunduğu diziye ekleyebiliriz
            kutucuklar.append(sekil)

    # elde ettiğimiz kutucuklar rastgele olduğu için biz bunları yukarıdan aşağıya bir şekilde sıralıyoruz
    # ilk değer sıralı şekiller, ikinci değer kapsayan kutu olduğu için [0] ile şekilleri elde ediyoruz
    kutucuklar = contours.sort_contours(
        kutucuklar, method="top-to-bottom")[0]

    # doğru yanıt sayısını tutacak değişkenimizi tanımlıyoruz
    dogru_cevap_sayisi = 0

    # np.arrane() --> başlangıçtan (0) dizinin sonuna kadar beşer beşer gruplara bölmeyi sağlar
    # enumerate ile bu dönen beş elemanlı gruplar üzerinde geziniyoruz (sorular üzerinde gezinme)
    #! q --> 0,1,2,3,4 gibi indeks değerleri yani soru sayısı
    #! i --> 0,5,10,15,20 gibi utucuk sayısı
    for (q, i) in enumerate(np.arange(0, len(kutucuklar), 5)):

        isaretlenmis_cevap = 0
        # her bir soru için 5 şıkkı kendi içinde soldan sağa sıralıyoruz (normalde method kısmı yoktu ben ekledim)
        # ve ilk indeksi yani sıralanmış şekilleri alıyoruz
        sekiller = contours.sort_contours(
            kutucuklar[i:i + 5], method="left-to-right")[0]

        # işaretlenmiş soruyu null yaptık
        isaretli = None

        # soru içindeki kutucuklar içinde gezinme
        #! j --> indeks değerleri
        #! cnt --> her bir kutucuk
        for (j, sekil) in enumerate(sekiller):

            # fotoğrafın şekline (shape) göre veri tipi integer olan sıfır matris oluşturuyoruz
            maske = np.zeros(esik_uygulanmis.shape, dtype="uint8")

            # mask --> kaynak görüntü
            # [cnt] --> kontur listesi
            # -1 --> tüm konturlar (normalde kontur indeksi ama -1 hepsi)
            # 255 --> kontur rengi
            # -1 -> kalınlık ?
            cv2.drawContours(maske, [sekil], -1, 255, -1)

            # maskeyi, eşik değeri uyguladığımız fotoğrafla bit düzeyinde and işlemine sokuyoruz
            maske = cv2.bitwise_and(
                esik_uygulanmis, esik_uygulanmis, mask=maske)

            # kutucuk içindeki sıfır olmayan piksel sayısını elde ediyoruz
            toplam = cv2.countNonZero(maske)

            # ? şu ana kadarki sıfır olamayan piksel sayısı, toplam sıfır olmayan piksel sayısından büyükse
            # ? ve işaretlenmiş şık yoksa işaretlenmiş şıkkı bulduk demektir
            # if isaretli is None or toplam > isaretli[0]:
            if toplam > 400:
                # bubbled iki elemanlı bir dizi ve ikinci elemanı işaretlenmiş şıkkın indeksi
                # print('soru sayısı: ', q)
                # print("bubbled: ", bubbled, ' total: ', total)
                isaretli = (toplam, j)
                isaretlenmis_cevap += 1
            # else:
            #     print("aslkhdkajshdkajsd")
        if isaretlenmis_cevap != 1:
            # 5 boş şık olarak ayarlandı
            CEVAPLAR.append(5)
        else:
            CEVAPLAR.append(isaretli[1])

    return CEVAPLAR.copy()


def sonuclar(foto, CEVAP_ANAHTARI):

    # fotoğrak yolunu değişkene aldık
    fotograf = cv2.imread(foto)

    # rgb renk uzayındaki fotoğrafı gri skalaya dönüştürüyoruz
    gri_foto = cv2.cvtColor(fotograf, cv2.COLOR_BGR2GRAY)

    # gürültüyü azaltmak için düzleştirme filtresi uyguluyoruz
    # canny ile kenar algılama yapabilmemiz için 5x5 Gaus Filtresi uygulamamız gerekiyor
    gauss = cv2.GaussianBlur(gri_foto, (5, 5), 0)

    # kenar algılama yapıyoruz, minimum değer 75, maximum değer 200
    kenarlar = cv2.Canny(gauss, 75, 200)

    # RETR_EXTERNAL: sadece en dıştaki kenarları almak için
    # CHAIN_APPROX_SIMPLE: yalnızca uç noktaları bırakır, örneğin dikdörtgen için 4 nokta
    sekiller = cv2.findContours(kenarlar.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)

    # görüntüdeki her bir şekli ayrı ayrı alıyoruz
    sekiller = imutils.grab_contours(sekiller)
    dokuman = None

    # eğer dizide şekiller varsa
    if len(sekiller) > 0:
        # cnts dizisini cv2.contourArea'ya göre bir algoritma ile azalan sırayla(revere=True) sıraladık
        sekiller = sorted(sekiller, key=cv2.contourArea, reverse=True)

        for sekil in sekiller:
            # her bir kapalı şeklin çevre uzunluğunu alıyoruz. True parametresi sadece kapalı şekillerin alınmasını sağlıyor
            # bu çevre uzunluğu, bir sonraki adımda epsilon değerini hesaplamak için kullanılacak
            cevre = cv2.arcLength(sekil, True)

            # epsilon değeri = çevre uzunluğu * 0.02
            # epsilon doğruluk oranı ile kapalı şekiller (True parametesi) oluşturuyoruz
            yaklasik_sekil = cv2.approxPolyDP(sekil, 0.02 * cevre, True)

            # şeklin 4 kenarı varsa fotoğraftaki kağıdı bulduk demektir
            if len(yaklasik_sekil) == 4:
                # kağıdı ata
                dokuman = yaklasik_sekil
                break

    yamuk = None
    kagit = None
    if dokuman is not None:
        # orijinal fotoğrafa ve gri tonlamalı fotoğrafa transform uygulayarak sadece kağıt olan kısmı elde ediyoruz
        kagit = four_point_transform(fotograf, dokuman.reshape(4, 2))
        yamuk = four_point_transform(gri_foto, dokuman.reshape(4, 2))
    else:
        paper = fotograf
        yamuk = gri_foto
    # # orijinal fotoğrafa ve gri tonlamalı fotoğrafa transform uygulayarak sadece kağıt olan kısmı elde ediyoruz
    # kagit = four_point_transform(fotograf, dokuman.reshape(4, 2))
    # yamuk = four_point_transform(gri_foto,  dokuman.reshape(4, 2))

    # her piksel için eşik değeri uygulanır, eşik değerden küçükse 0, büyükse maksimum değer ayarlanır
    # burada eşik değerimiz THRESH_OTSU ile her fotoğraf için, fotoğrafın renk dağılımına göre optimum olarak ayarlanacaktır
    # maksimum değerimiz 255 olarak verilmiştir
    # THRESH_BINARY_INV parametresi sayesinde siyahlar beyaz, beyazlar siyah hale geliyor
    # threshold() fonksiyonu iki değer döndürür: ilki eşik değeri, ikinci eşik değeri uygulanmış fotoğraf
    # bu yüzden [1] ile ikinci değeri aldık
    esik_uygulanmis = cv2.threshold(yamuk, 0, 255,
                                    cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    #  RETR_EXTERNAL: sadece en dıştaki kenarları almak için
    # CHAIN_APPROX_SIMPLE: yalnızca uç noktaları bırakır, örneğin dikdörtgen için 4 nokta
    # burada artık aldığımız fotoğrafta değil kağıdı kesip eşik değeri uyguladığımız fotoğraftaki kenarları alıyoruz
    sekiller = cv2.findContours(esik_uygulanmis.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)

    # görüntüdeki her bir şekli ayrı ayrı alıyoruz
    sekiller = imutils.grab_contours(sekiller)

    # soruları tutacağımız diziyi tanımladık
    kutucuklar = []

    # şekiller içinde geziniyoruz
    for sekil in sekiller:

        # her bir şekil için sınırlandırıcı dikdörtgenin koordinatlarını belirliyoruz
        # w --> genişlik
        # h --> yükseklik
        # x,y koordinat ancak sağ üst köşeden başlayarak
        (x, y, w, h) = cv2.boundingRect(sekil)

        # aspect ratio = en boy oranını hesaplıyoruz --> genişlik/yükseklik
        oran = w / float(h)

        # eğer aşağıdaki değerlere uygunda bu cevap kutucuğudur ve diziye eklenir
        # ar >= 0.9 and ar <= 1.1 --> bu koşul en boy oranının yaklaşık 1 olup olmadığını kontrol eder
        # eğer en boy oranı 1 ise daireyi kapsayan kareyi bulduk demektir
        # w >= 20 and h >= 20 --> bu kontrol ise çok küçük şekillerin hesaba katılmamasını sağlar
        if w >= 20 and h >= 20 and oran >= 0.9 and oran <= 1.1:
            # eğer tüm koşullar sağladıysa kutucuğu bulduk demektir artık soruların bulunduğu diziye ekleyebiliriz
            kutucuklar.append(sekil)

    # elde ettiğimiz kutucuklar rastgele olduğu için biz bunları yukarıdan aşağıya bir şekilde sıralıyoruz
    # ilk değer sıralı şekiller, ikinci değer kapsayan kutu olduğu için [0] ile şekilleri elde ediyoruz
    kutucuklar = contours.sort_contours(
        kutucuklar, method="top-to-bottom")[0]

    # doğru yanıt sayısını tutacak değişkenimizi tanımlıyoruz
    dogru_cevap_sayisi = 0

    # np.arrane() --> başlangıçtan (0) dizinin sonuna kadar beşer beşer gruplara bölmeyi sağlar
    # enumerate ile bu dönen beş elemanlı gruplar üzerinde geziniyoruz (sorular üzerinde gezinme)
    #! q --> 0,1,2,3,4 gibi indeks değerleri yani soru sayısı
    #! i --> 0,5,10,15,20 gibi utucuk sayısı
    for (q, i) in enumerate(np.arange(0, len(kutucuklar), 5)):

        # her bir soru için 5 şıkkı kendi içinde soldan sağa sıralıyoruz (normalde method kısmı yoktu ben ekledim)
        # ve ilk indeksi yani sıralanmış şekilleri alıyoruz
        sekiller = contours.sort_contours(
            kutucuklar[i:i + 5], method="left-to-right")[0]

        # işaretlenmiş soruyu null yaptık
        isaretli = None

        # soru içindeki kutucuklar içinde gezinme
        #! j --> indeks değerleri
        #! cnt --> her bir kutucuk
        for (j, sekil) in enumerate(sekiller):

            # fotoğrafın şekline (shape) göre veri tipi integer olan sıfır matris oluşturuyoruz
            maske = np.zeros(esik_uygulanmis.shape, dtype="uint8")

            # mask --> kaynak görüntü
            # [cnt] --> kontur listesi
            # -1 --> tüm konturlar (normalde kontur indeksi ama -1 hepsi)
            # 255 --> kontur rengi
            # -1 -> kalınlık ?
            cv2.drawContours(maske, [sekil], -1, 255, -1)

            # maskeyi, eşik değeri uyguladığımız fotoğrafla bit düzeyinde and işlemine sokuyoruz
            maske = cv2.bitwise_and(
                esik_uygulanmis, esik_uygulanmis, mask=maske)

            # kutucuk içindeki sıfır olmayan piksel sayısını elde ediyoruz
            toplam = cv2.countNonZero(maske)

            # ? şu ana kadarki sıfır olamayan piksel sayısı, toplam sıfır olmayan piksel sayısından büyükse
            # ? ve işaretlenmiş şık yoksa işaretlenmiş şıkkı bulduk demektir
            if isaretli is None or toplam > isaretli[0]:

                # bubbled iki elemanlı bir dizi ve ikinci elemanı işaretlenmiş şıkkın indeksi
                isaretli = (toplam, j)

        # hangi sorudaysak o sorunun cevabını alıyoruz
        cevap = CEVAP_ANAHTARI[q]

        # eğer işaretlenmiş cevap ile cevap anahtarındaki cevap aynı ise
        if cevap == isaretli[1]:

            # doğru cevap sayısını bir artırıyoruz
            dogru_cevap_sayisi += 1

    # sınav notunu hesaplıyoruz, buradda 5.0 soru sayısına göre değişecek
    puan = (dogru_cevap_sayisi / len(CEVAP_ANAHTARI)) * 100
    return "{: .2f}".format(puan)
