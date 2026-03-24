# Ürün Takip Sistemi - İyileştirme ve Geliştirme Görevleri

Bu liste, PROJE_RAPORU_VE_GELISIM.md dosyasında belirtilen eksiklikler ve eklenecek özellikler baz alınarak sırasıyla hazırlanmıştır.

## Aşama 1: Güvenlik ve Altyapı
- [x] 1.1 `python-dotenv` kütüphanesinin eklenmesi ve API anahtarının [.env](file:///c:/Users/SAMET/Desktop/urun%20takip/.env) dosyasına taşınması.
- [x] 1.2 [.gitignore](file:///c:/Users/SAMET/Desktop/urun%20takip/.gitignore) dosyasının oluşturularak [.env](file:///c:/Users/SAMET/Desktop/urun%20takip/.env), [data/](file:///c:/Users/SAMET/Desktop/urun%20takip/gui_app.py#344-394), `config/` vb. dosyaların git takibinden çıkarılması.

## Aşama 2: Veritabanına Geçiş (SQLite)
- [x] 2.1 [database.py](file:///c:/Users/SAMET/Desktop/urun%20takip/database.py) modülünün oluşturulması ve SQLite bağlantısının kurulması.
- [x] 2.2 Mevcut `gercek_veriler.csv` verilerinin yeni SQLite tablosuna (örn. [urunler](file:///c:/Users/SAMET/Desktop/urun%20takip/database.py#82-101)) aktarılması.
- [x] 2.3 [app.py](file:///c:/Users/SAMET/Desktop/urun%20takip/app.py) ve [gui_app.py](file:///c:/Users/SAMET/Desktop/urun%20takip/gui_app.py)'nin artık CSV yerine SQLite üzerinden veri okuyup yazacak şekilde güncellenmesi.

## Aşama 3: Arayüz (GUI) Geliştirmeleri - CRUD
- [x] 3.1 GUI arayüzüne seçili kaydı "Silme" (Delete) butonunun eklenmesi.
- [x] 3.2 GUI arayüzüne seçili kaydı "Güncelleme" (Update) butonunun ve gerekli pop-up pencerelerinin eklenmesi.

## Aşama 4: Arama ve Filtreleme
- [x] 4.1 Arayüze "Arama Çubuğu" (Ürün adına göre ara) eklenmesi.
- [x] 4.2 Kategori bazlı filtreleme (Combobox aracılığıyla sadece seçili kategoriyi listeleme) özelliğinin eklenmesi.

## Aşama 5: Döviz Kur Entegrasyonu
- [x] 5.1 TCMB veya ücretsiz bir kur API'si üzerinden güncel USD/EUR - TL kurunu çekecek modülün yazılması.
- [x] 5.2 Arayüzde harcamaların (varsa) kur karşılıklarının veya anlık kur bilgisinin gösterilmesi.

## Aşama 6: Gelişmiş Grafikler
- [x] 6.1 Matplotlib kullanılarak harcamaların zaman içerisindeki artışını/dağılımını gösteren Çizgi Grafiği (Line Chart) sekmesinin GUI'ye eklenmesi.

## Aşama 7: Gizlilik ve AI Veri Maskelemesi (Data Masking)
- [x] 7.1 Yapay zeka'ya bütçe özeti gönderilirken, gerçek ürün isimlerinin (Örn: Rolex Kadran) sansürlenip (Örn: Ürün 1, Ürün 2) olarak gönderilmesini sağlayan maskeleme fonksiyonunun yazılması.

## Aşama 8: Veritabanı Şifreleme (Extra Security)
- [x] 8.1 Uygulama açılışına "PIN / Şifre" ekranı konulması.
- [x] 8.2 `cryptography` modülü ile veritabanı dosyasının şifrelenmiş halde saklanması (Opsiyonel / İhtiyaca Göre - Uygulama açılış login ekranı ile çözüme kavuştu).

## Aşama 8.5: Modern UX (API Yönetimi ve Link Desteği)
- [x] 8.5.1 [urunler](file:///c:/Users/SAMET/Desktop/urun%20takip/database.py#82-101) SQLite veritabanı tablosuna güvenli bir şekilde (eski verileri bozmadan) `Link` sütunu eklenmesi (ALTER TABLE).
- [x] 8.5.2 Parça ekleme / düzenleme pencerelerine isteğe bağlı "Ürün Linki" kutusu eklenmesi ve Tabloda seçili kaydın sayfasına tek tıkla (`webbrowser` kütüphanesiyle) gidecek "📍 Linke Git" fonksiyonunun arayüze oturtulması.
- [x] 8.5.3 "Yapay Zeka" menüsü altına bir ayar butonu eklenerek, kullanıcıların kod dosyalarına (".env") girmeden, direkt program içinden "API Anahtarı Tanımla" veya "Anahtarı Sistemden Sil" şeklinde yapay zeka entegrasyonunu yönetebilmesinin sağlanması.

## Aşama 9: Web'den Ürün Arama Modülü (Web Scraping)
- [x] 9.1 `requests` ve `beautifulsoup4` kütüphanelerinin sisteme yüklenmesi.
- [x] 9.2 [web_scraper.py](file:///c:/Users/SAMET/Desktop/urun%20takip/web_scraper.py) modülünün yazılması ve sahte istek atarak HTML içerisinden isim, fiyat ve link ayıplayıcısının kodlanması.
- [x] 9.3 [gui_app.py](file:///c:/Users/SAMET/Desktop/urun%20takip/gui_app.py) sol menüsüne "5. Web'den Ürün Bul" entegrasyonu ve arama arayüzünün (Textbox/Entry ve Tablo ile) oluşturulması.
- [x] 9.4 Arama sonuçlarındaki herhangi bir parça için "Veritabanıma Şi̇mdi̇ Ekle" buton fonksiyonunun yazılması.

## Aşama 10: Siber Güvenlik, UI/UX ve Sistem Ayarları (Mükemmelleştirme Fazı)
### 10.1 Siber Güvenlik (Cybersecurity) Önlemleri
- [x] 10.1.1 **Kriptografi ile PIN Saklama:** Uygulama şifresinin [.env](file:///c:/Users/SAMET/Desktop/urun%20takip/.env) dosyasında düz metin (1234) olarak durması yerine tehlike anında kırılamayacak **SHA-256 Hash** parolasına dönüştürülüp karşılaştırılması.
- [x] 10.1.2 **Oturum Zaman Aşımı (Auto-Lock):** Uygulama açık bırakılıp uzaklaşıldığında (örneğin 3-5 dakika fare hareketi olmadığında) programın verileri gizleyip tekrar kendini PIN ekranına kilitlemesi.

### 10.2 Görsel ve UI/UX İyileştirmeleri
- [x] 10.2.1 **Gömülü Ana Ekran (Dashboard):** Harici pencerede açılan Cansıkıcı grafiklerin popup yerine `FigureCanvasTkAgg` teknolojisiyle direkt uygulamanın içine, profesyonel bir finans uygulaması gibi gömülmesi.
- [x] 10.2.2 **İkonografi ve Renklendirme:** Sol menüdeki basit yazıların ikonlarla (`🏠`, `📊`, `⚙️`) desteklenip yanlarındaki boşlukların oranlanması; Grid tablolarında satır renklerinin birbirine girmemesi için (Zebra / Çift-Tek Satır renklendirmesi) eklenmesi.

### 10.3 Merkezi Ayarlar Paneli (Settings Hub)
- [x] 10.3.1 Yapay zeka menüsündeki "API Yönetimi" kısımlarının taşınıp sol menüye **"6. Sistem Ayarları"** adlı özel ve kapsamlı yepyeni bir ana sekme eklenmesi.
- [x] 10.3.2 Ayarlar menüsü içerisinden dinamik olarak **Uygulama Şifresinin (PIN) değiştirilebilmesi**.
- [x] 10.3.3 Ayarlar menüsünden **Görsel Temanın (Karanlık / Aydınlık Mod)** değiştirilebilmesi ve oturum / istatistik bilgilerin ekranda raporlanması.
- [x] 10.3.4 Ayarlar menüsüne tek tıklamayla veritabanını (`urunler.db`) zipleyip/kopyalayıp bilgisayarda istenen başka bir konuma saklayan **"Veritabanını Yedekle"** butonu eklenmesi.

## Aşama 12: Taksit, Faiz (Vade Farkı) ve Kapsamlı Finansal İzleme
- [x] 12.1 [urunler](file:///c:/Users/SAMET/Desktop/urun%20takip/database.py#82-101) veritabanı şemasına `ALTER TABLE` yardımıyla `taksit_sayisi`, `vade_farki`, ve `odenen_taksit` sütunlarının dışarıdan zararsızca enjekte edilmesi.
- [x] 12.2 [gui_app.py](file:///c:/Users/SAMET/Desktop/urun%20takip/gui_app.py)'deki "1. Parça Ekle" formuna (Taksit Sayısı ve Vade Farkı) kutucuklarının eklenip entegre edilmesi.
- [x] 12.3 "2. Liste & CRUD" sekmesinde yer alan Treeview tablosunda; ürün fiyatının yanında "+ 500 TL Vade Farkı" gibi ekstra maliyetlerin yansıtılması ve tablonun "Ödenen: 2/6" formatında taksit durumunu göstermesi.
- [x] 12.4 "Seçilini Güncelle" pop-up ekranına `Ödenen Taksit Miktarı` hücresi eklenerek kullanıcının her ay ödeme yaptıkça taksit sürecini birer birer ilerletebilmesi.
- [x] 12.5 "3. Dashboard" alanında toplam borç, ödenen borç ve kalan borç (Taksitler dahil edilerek) istatistiklerinin grafiklere yansıtılması.
- [x] 12.6 **Yapay Zeka API Rehberi:** Ayarlar kısmındaki API giriş kutusunun yanına "Nasıl API Alınır?" butonu konulması. Tıklandığında görsel ve yazılı olarak Google AI Studio'dan nasıl kod alınacağını ve alındığında yapay zekanın ne gibi özellikler katacağını anlatan detaylı bir rehber ekranı (Pop-Up) entegre edilmesi.

## Aşama 13: UX/UI (Kullanıcı Deneyimi) Mükemmelleştirmeleri
- [x] 13.1 **Excel Dışa Aktarma:** Liste menüsüne tabloda görünen verileri masaüstüne ".csv / .xlsx" olarak aktaracak export yapısının kurulması.
- [x] 13.2 **Akıllı Kategori Kutusu:** İlk sekmedeki Kategori giriş kutusunun veritabanındaki mevcut kategorileri barındıran `CTkComboBox` yapısına (Kullanıcı dilerse yenisini yazabilecek şekilde) geçirilmesi.
- [x] 13.3 **Tablo Çift Tıklama:** Kullanıcı "Seçilini Güncelle" butonuna basmak yerine Treeview'daki satıra "Çift Tıkladığında" güncelleme panelinin açılmasını sağlayan Binding olayının yazılması.
- [x] 13.4 **Web Kategori Eşleştirmesi:** Web'den Bul sekmesinden bir ürünü Veritabanına şutlarken "Kategori" adının (Örn: PC Toplama) sorulduğu bir ara Popup modülü kurulması.

## Aşama 14: Veri İçe Aktarma (Import) ve Önizleme/Onay Sensörü
- [x] 14.1 Liste sekmesine "İçe Aktar (Excel/CSV)" butonunun bağlanarak Dosya Seçici (`filedialog`) ile entegre edilmesi.
- [x] 14.2 `pandas` kullanılarak seçilen dosyanın okunması (Kategori, Ad, Fiyat) eksik verilerin veya hatalı sütunların yazılımca analiz edilip tamamlanması.
- [x] 14.3 Okunan ve analiz edilen verilerin kullanıcı önüne (Pop-Up Onay Ekranı) çıkartılarak "X Adet kayıt sisteme şöyle aktarılacak, eksikleri varsa manuel düzeltin" şablonunun oluşturulması.
- [x] 14.4 "Sisteme Aktar" tıklandığı an `Bulk Insert` mantığı ile tüm verilerin SQlite veritabanına sorunsuzca yazılıp Listelerin güncellenmesi.

## Aşama 15: Kurulum Sihirbazı (Installer) ve Mimarinin Paketlenmesi
- [x] 15.1 Tüm projenin (ve [data](file:///c:/Users/SAMET/Desktop/urun%20takip/gui_app.py#344-394), `config` altyapısının) tek bir exe dosyası formatında, hedef sistemde Python gereksinimi duymadan çalışabilecek şekilde `PyInstaller` ile derlenmesi (Build).
- [x] 15.2 Özel bir Installer (*Kurulum Sihirbazı*) kurgusunun program içerisine entegre edilerek [.exe](file:///c:/Users/SAMET/Desktop/urun%20takip/dist/Urun%20Takip%20Sistemi%20Kurulumu.exe) olarak oluşturulması.
- [x] 15.3 Kurulum esnasında Windows "Başlat Menüsü" arama motoruna kısayol bırakılması konfigürasyonu.
- [x] 15.4 Kurulum arayüzünde kullanıcıya isteğe bağlı "Masaüstü Kısayolu Oluştur" check-box'ının sunulması ve sistemin güvenli `AppData` dizinine kurulması.
- [x] 15.5 **Kurulum Dizini Seçici:** Sihirbaza varsayılan `APPDATA/UrunTakipSistemi` yazan bir metin kutusu ve `Gözat` butonu eklenmesi. Kullanıcı isterse `D:/Oyunlar/` dizinine bile kurabilmesi algoritmik entegrasyonu.

## Aşama 16: Final Kalite Kontrolü, Siber Güvenlik ve Optimizasyon
- [x] 16.1 Ağ izolasyonu testleri (Network Fail-Safe): [currency.py](file:///c:/Users/SAMET/Desktop/urun%20takip/currency.py) ve [web_scraper.py](file:///c:/Users/SAMET/Desktop/urun%20takip/web_scraper.py) modüllerinin internetin tamamen kapalı olduğu anlarda sistemi çökertmemesi.
- [x] 16.2 Girdi Zafiyetleri (Type Errors): Taksit, ücret gibi kutulara metin girildiğinde programın fatal error (Pyre/Python Exception) verip kapanmaması.
- [x] 16.3 SQLi ve Path Traversal tespiti yapılıp raporlanması.
- [x] 16.4 Linter ve Tip (Type Annotation) hatalarının temizlenmesi (Örn. `os.path.join` kaynaklı Pyre bildirimleri).
- [x] 16.5 **Kullanım Kılavuzu:** Installer (Sihirbaz) çalıştırıldığında kullanıcının cihazına A'dan Z'ye programın nasıl kullanıldığını açıklayan detaylı bir `Kullanim_Kilavuzu.txt` dosyasının otomatik kurulması.
