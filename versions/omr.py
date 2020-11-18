from imutils.perspective import four_point_transform
from imutils import contours
import numpy as np
import imutils
import cv2


def getAnswers(img):
    ANSWER_KEY = list()

    # fotoğraf yolunu değişkene aldık
    image = cv2.imread(img)

    # rgb renk uzayındaki fotoğrafı gri skalaya dönüştürüyoruz
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # gürültüyü azaltmak için düzleştirme filtresi uyguluyoruz
    # canny ile kenar algılama yapabilmemiz için 5x5 Gaus Filtresi uygulamamız gerekiyor
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # kenar algılama yapıyoruz, minimum değer 75, maximum değer 200
    edged = cv2.Canny(blurred, 75, 200)

    # RETR_EXTERNAL: sadece en dıştaki kenarları almak için
    # CHAIN_APPROX_SIMPLE: yalnızca uç noktaları bırakır, örneğin dikdörtgen için 4 nokta
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)

    # görüntüdeki her bir şekli ayrı ayrı alıyoruz
    cnts = imutils.grab_contours(cnts)
    docCnt = None

    # eğer dizide şekiller varsa
    if len(cnts) > 0:
        # cnts dizisini cv2.contourArea'ya göre bir algoritma ile azalan sırayla(revere=True) sıraladık
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

        for cnt in cnts:
            # her bir kapalı şeklin çevre uzunluğunu alıyoruz. True parametresi sadece kapalı şekillerin alınmasını sağlıyor
            # bu çevre uzunluğu, bir sonraki adımda epsilon değerini hesaplamak için kullanılacak
            peri = cv2.arcLength(cnt, True)

            # epsilon değeri = çevre uzunluğu * 0.02
            # epsilon doğruluk oranı ile kapalı şekiller (True parametesi) oluşturuyoruz
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

            # şeklin 4 kenarı varsa fotoğraftaki kağıdı bulduk demektir
            if len(approx) == 4:
                # kağıdı ata
                docCnt = approx
                break

    warped = None
    paper = None
    if docCnt is not None:
        # orijinal fotoğrafa ve gri tonlamalı fotoğrafa transform uygulayarak sadece kağıt olan kısmı elde ediyoruz
        paper = four_point_transform(image, docCnt.reshape(4, 2))
        warped = four_point_transform(gray, docCnt.reshape(4, 2))
    else:
        paper = image
        warped = gray

    # her piksel için eşik değeri uygulanır, eşik değerden küçükse 0, büyükse maksimum değer ayarlanır
    # burada eşik değerimiz THRESH_OTSU ile her fotoğraf için, fotoğrafın renk dağılımına göre optimum olarak ayarlanacaktır
    # maksimum değerimiz 255 olarak verilmiştir
    # THRESH_BINARY_INV parametresi sayesinde siyahlar beyaz, beyazlar siyah hale geliyor
    # threshold() fonksiyonu iki değer döndürür: ilki eşik değeri, ikinci eşik değeri uygulanmış fotoğraf
    # bu yüzden [1] ile ikinci değeri aldık
    thresh = cv2.threshold(warped, 0, 255,
                           cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    #  RETR_EXTERNAL: sadece en dıştaki kenarları almak için
    # CHAIN_APPROX_SIMPLE: yalnızca uç noktaları bırakır, örneğin dikdörtgen için 4 nokta
    # burada artık aldığımız fotoğrafta değil kağıdı kesip eşik değeri uyguladığımız fotoğraftaki kenarları alıyoruz
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)

    # görüntüdeki her bir şekli ayrı ayrı alıyoruz
    cnts = imutils.grab_contours(cnts)

    # soruları tutacağımız diziyi tanımladık
    questionCnts = []

    # şekiller içinde geziniyoruz
    for cnt in cnts:

        # her bir şekil için sınırlandırıcı dikdörtgenin koordinatlarını belirliyoruz
        # w --> genişlik
        # h --> yükseklik
        # x,y koordinat ancak sağ üst köşeden başlayarak
        (x, y, w, h) = cv2.boundingRect(cnt)

        # aspect ratio = en boy oranını hesaplıyoruz --> genişlik/yükseklik
        ar = w / float(h)

        # eğer aşağıdaki değerlere uygunda bu cevap kutucuğudur ve diziye eklenir
        # ar >= 0.9 and ar <= 1.1 --> bu koşul en boy oranının yaklaşık 1 olup olmadığını kontrol eder
        # eğer en boy oranı 1 ise daireyi kapsayan kareyi bulduk demektir
        # w >= 20 and h >= 20 --> bu kontrol ise çok küçük şekillerin hesaba katılmamasını sağlar
        if w >= 20 and h >= 20 and ar >= 0.9 and ar <= 1.1:
            # eğer tüm koşullar sağladıysa kutucuğu bulduk demektir artık soruların bulunduğu diziye ekleyebiliriz
            questionCnts.append(cnt)

    # elde ettiğimiz kutucuklar rastgele olduğu için biz bunları yukarıdan aşağıya bir şekilde sıralıyoruz
    # ilk değer sıralı şekiller, ikinci değer kapsayan kutu olduğu için [0] ile şekilleri elde ediyoruz
    questionCnts = contours.sort_contours(
        questionCnts, method="top-to-bottom")[0]

    # doğru yanıt sayısını tutacak değişkenimizi tanımlıyoruz
    correct = 0

    # np.arrane() --> başlangıçtan (0) dizinin sonuna kadar beşer beşer gruplara bölmeyi sağlar
    # enumerate ile bu dönen beş elemanlı gruplar üzerinde geziniyoruz (sorular üzerinde gezinme)
    #! q --> 0,1,2,3,4 gibi indeks değerleri yani soru sayısı
    #! i --> 0,5,10,15,20 gibi utucuk sayısı
    for (q, i) in enumerate(np.arange(0, len(questionCnts), 5)):

        bubbledCount = 0
        # her bir soru için 5 şıkkı kendi içinde soldan sağa sıralıyoruz (normalde method kısmı yoktu ben ekledim)
        # ve ilk indeksi yani sıralanmış şekilleri alıyoruz
        cnts = contours.sort_contours(
            questionCnts[i:i + 5], method="left-to-right")[0]

        # işaretlenmiş soruyu null yaptık
        bubbled = None

        # soru içindeki kutucuklar içinde gezinme
        #! j --> indeks değerleri
        #! cnt --> her bir kutucuk
        print(len(cnts))
        for (j, cnt) in enumerate(cnts):

            # fotoğrafın şekline (shape) göre veri tipi integer olan sıfır matris oluşturuyoruz
            mask = np.zeros(thresh.shape, dtype="uint8")

            # mask --> kaynak görüntü
            # [cnt] --> kontur listesi
            # -1 --> tüm konturlar (normalde kontur indeksi ama -1 hepsi)
            # 255 --> kontur rengi
            # -1 -> kalınlık ?
            cv2.drawContours(mask, [cnt], -1, 255, -1)

            # maskeyi, eşik değeri uyguladığımız fotoğrafla bit düzeyinde and işlemine sokuyoruz
            mask = cv2.bitwise_and(thresh, thresh, mask=mask)

            # kutucuk içindeki sıfır olmayan piksel sayısını elde ediyoruz
            total = cv2.countNonZero(mask)

            # ? şu ana kadarki sıfır olamayan piksel sayısı, toplam sıfır olmayan piksel sayısından büyükse
            # ? ve işaretlenmiş şık yoksa işaretlenmiş şıkkı bulduk demektir
            # if bubbled is None or total > bubbled[0]:
            if total > 400:
                # bubbled iki elemanlı bir dizi ve ikinci elemanı işaretlenmiş şıkkın indeksi
                # print('soru sayısı: ', q)
                # print("bubbled: ", bubbled, ' total: ', total)
                bubbled = (total, j)
                bubbledCount += 1
            # else:
            #     print("aslkhdkajshdkajsd")
        if bubbledCount != 1:
            ANSWER_KEY.append(5)
        else:
            ANSWER_KEY.append(bubbled[1])

    print('Cevap Anahtarı: ', ANSWER_KEY)
    return ANSWER_KEY.copy()


def getScore(img, ANSWER_KEY):
    print('ANSWER_KEY_GELEN= ', ANSWER_KEY)
    # fotoğrak yolunu değişkene aldık
    image = cv2.imread(img)

    # rgb renk uzayındaki fotoğrafı gri skalaya dönüştürüyoruz
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # gürültüyü azaltmak için düzleştirme filtresi uyguluyoruz
    # canny ile kenar algılama yapabilmemiz için 5x5 Gaus Filtresi uygulamamız gerekiyor
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # kenar algılama yapıyoruz, minimum değer 75, maximum değer 200
    edged = cv2.Canny(blurred, 75, 200)

    # RETR_EXTERNAL: sadece en dıştaki kenarları almak için
    # CHAIN_APPROX_SIMPLE: yalnızca uç noktaları bırakır, örneğin dikdörtgen için 4 nokta
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)

    # görüntüdeki her bir şekli ayrı ayrı alıyoruz
    cnts = imutils.grab_contours(cnts)
    docCnt = None

    # eğer dizide şekiller varsa
    if len(cnts) > 0:
        # cnts dizisini cv2.contourArea'ya göre bir algoritma ile azalan sırayla(revere=True) sıraladık
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

        for cnt in cnts:
            # her bir kapalı şeklin çevre uzunluğunu alıyoruz. True parametresi sadece kapalı şekillerin alınmasını sağlıyor
            # bu çevre uzunluğu, bir sonraki adımda epsilon değerini hesaplamak için kullanılacak
            peri = cv2.arcLength(cnt, True)

            # epsilon değeri = çevre uzunluğu * 0.02
            # epsilon doğruluk oranı ile kapalı şekiller (True parametesi) oluşturuyoruz
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

            # şeklin 4 kenarı varsa fotoğraftaki kağıdı bulduk demektir
            if len(approx) == 4:
                # kağıdı ata
                docCnt = approx
                break

    # orijinal fotoğrafa ve gri tonlamalı fotoğrafa transform uygulayarak sadece kağıt olan kısmı elde ediyoruz
    paper = four_point_transform(image, docCnt.reshape(4, 2))
    warped = four_point_transform(gray, docCnt.reshape(4, 2))

    # her piksel için eşik değeri uygulanır, eşik değerden küçükse 0, büyükse maksimum değer ayarlanır
    # burada eşik değerimiz THRESH_OTSU ile her fotoğraf için, fotoğrafın renk dağılımına göre optimum olarak ayarlanacaktır
    # maksimum değerimiz 255 olarak verilmiştir
    # THRESH_BINARY_INV parametresi sayesinde siyahlar beyaz, beyazlar siyah hale geliyor
    # threshold() fonksiyonu iki değer döndürür: ilki eşik değeri, ikinci eşik değeri uygulanmış fotoğraf
    # bu yüzden [1] ile ikinci değeri aldık
    thresh = cv2.threshold(warped, 0, 255,
                           cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    #  RETR_EXTERNAL: sadece en dıştaki kenarları almak için
    # CHAIN_APPROX_SIMPLE: yalnızca uç noktaları bırakır, örneğin dikdörtgen için 4 nokta
    # burada artık aldığımız fotoğrafta değil kağıdı kesip eşik değeri uyguladığımız fotoğraftaki kenarları alıyoruz
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)

    # görüntüdeki her bir şekli ayrı ayrı alıyoruz
    cnts = imutils.grab_contours(cnts)

    # soruları tutacağımız diziyi tanımladık
    questionCnts = []

    # şekiller içinde geziniyoruz
    for cnt in cnts:

        # her bir şekil için sınırlandırıcı dikdörtgenin koordinatlarını belirliyoruz
        # w --> genişlik
        # h --> yükseklik
        # x,y koordinat ancak sağ üst köşeden başlayarak
        (x, y, w, h) = cv2.boundingRect(cnt)

        # aspect ratio = en boy oranını hesaplıyoruz --> genişlik/yükseklik
        ar = w / float(h)

        # eğer aşağıdaki değerlere uygunda bu cevap kutucuğudur ve diziye eklenir
        # ar >= 0.9 and ar <= 1.1 --> bu koşul en boy oranının yaklaşık 1 olup olmadığını kontrol eder
        # eğer en boy oranı 1 ise daireyi kapsayan kareyi bulduk demektir
        # w >= 20 and h >= 20 --> bu kontrol ise çok küçük şekillerin hesaba katılmamasını sağlar
        if w >= 20 and h >= 20 and ar >= 0.9 and ar <= 1.1:
            # eğer tüm koşullar sağladıysa kutucuğu bulduk demektir artık soruların bulunduğu diziye ekleyebiliriz
            questionCnts.append(cnt)

    # elde ettiğimiz kutucuklar rastgele olduğu için biz bunları yukarıdan aşağıya bir şekilde sıralıyoruz
    # ilk değer sıralı şekiller, ikinci değer kapsayan kutu olduğu için [0] ile şekilleri elde ediyoruz
    questionCnts = contours.sort_contours(
        questionCnts, method="top-to-bottom")[0]

    # doğru yanıt sayısını tutacak değişkenimizi tanımlıyoruz
    correct = 0

    # np.arrane() --> başlangıçtan (0) dizinin sonuna kadar beşer beşer gruplara bölmeyi sağlar
    # enumerate ile bu dönen beş elemanlı gruplar üzerinde geziniyoruz (sorular üzerinde gezinme)
    #! q --> 0,1,2,3,4 gibi indeks değerleri yani soru sayısı
    #! i --> 0,5,10,15,20 gibi utucuk sayısı
    for (q, i) in enumerate(np.arange(0, len(questionCnts), 5)):

        # her bir soru için 5 şıkkı kendi içinde soldan sağa sıralıyoruz (normalde method kısmı yoktu ben ekledim)
        # ve ilk indeksi yani sıralanmış şekilleri alıyoruz
        cnts = contours.sort_contours(
            questionCnts[i:i + 5], method="left-to-right")[0]

        # işaretlenmiş soruyu null yaptık
        bubbled = None

        # soru içindeki kutucuklar içinde gezinme
        #! j --> indeks değerleri
        #! cnt --> her bir kutucuk
        for (j, cnt) in enumerate(cnts):

            # fotoğrafın şekline (shape) göre veri tipi integer olan sıfır matris oluşturuyoruz
            mask = np.zeros(thresh.shape, dtype="uint8")

            # mask --> kaynak görüntü
            # [cnt] --> kontur listesi
            # -1 --> tüm konturlar (normalde kontur indeksi ama -1 hepsi)
            # 255 --> kontur rengi
            # -1 -> kalınlık ?
            cv2.drawContours(mask, [cnt], -1, 255, -1)

            # maskeyi, eşik değeri uyguladığımız fotoğrafla bit düzeyinde and işlemine sokuyoruz
            mask = cv2.bitwise_and(thresh, thresh, mask=mask)

            # kutucuk içindeki sıfır olmayan piksel sayısını elde ediyoruz
            total = cv2.countNonZero(mask)

            # ? şu ana kadarki sıfır olamayan piksel sayısı, toplam sıfır olmayan piksel sayısından büyükse
            # ? ve işaretlenmiş şık yoksa işaretlenmiş şıkkı bulduk demektir
            if bubbled is None or total > bubbled[0]:

                # bubbled iki elemanlı bir dizi ve ikinci elemanı işaretlenmiş şıkkın indeksi
                bubbled = (total, j)

        # opencv bgr formatını kullanıyor bu yüzden rengi kırmızı yaptık
        # aşağıda kontrolde eğer doğruysa renk yeşil olacak ve yeşil daire çizilecek
        # eğer değilse aynı kalacak ve kırmızı çizilecek
        color = (0, 0, 255)

        # hangi sorudaysak o sorunun cevabını alıyoruz
        print('gelen :', ANSWER_KEY)
        cevap = ANSWER_KEY[q]

        # eğer işaretlenmiş cevap ile cevap anahtarındaki cevap aynı ise
        if cevap == bubbled[1]:

            # rengi yeşil yapıyoruz
            # color = (0, 255, 0)

            # doğru cevap sayısını bir artırıyoruz
            correct += 1
        # doğru cevabı daire içine alıyoruz
        # cv2.drawContours(paper, [cnts[cevap]], -1, color, 3)

    # sınav notunu hesaplıyoruz, buradda 5.0 soru sayısına göre değişecek
    score = (correct / len(ANSWER_KEY)) * 100
    print(score)
    return score
    # # konsola sonucu yazdırıyoruz
    # print("[INFO] score: {:.2f}%".format(score))

    # # opencv ile ekrandaki resme de sonucu yazdırıyoruz
    # cv2.putText(paper, "{:.2f}%".format(score), (10, 30),
    #             cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    # # orijinal resmi gösteriyoruz
    # cv2.imshow("Original", image)

    # # sınav sonucunu resim olarak gösteriyoruz
    # cv2.imshow("Exam", paper)

    # cv2.waitKey(0)
