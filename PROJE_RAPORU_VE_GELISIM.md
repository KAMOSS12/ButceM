# Ürün Takip Sistemi - Proje Geliştirme Raporu ve Gelecek Güvenlik Vizyonu

Bu belge, "Ürün Takip Sistemi" projesinin başlangıcından itibaren geçirdiği tüm evreleri, yapılan geliştirmeleri ve gelecekte projenin güvenliği & ölçeklenebilirliği için atılması gereken adımları özetlemektedir.

---

## 1. Bugüne Kadar Yapılanlar (Aşama Özeti)

Proje, başlangıçta basit bir bulut e-tablosu fikrinden yola çıkılarak tam teşekküllü, masaüstünde çalışan, yapay zeka destekli bir Python programına dönüştürülmüştür. 

* **Aşama 1: Bulut Tabanlı Prototip:** İşlemlere ilk olarak Google E-Tablolar (Google Sheets) kullanılarak, yeşil/kırmızı koşullu biçimlendirmelerle saat parçası takip sistemi tasarımıyla başlandı.
* **Aşama 2: Yerel Uygulama İskeleti:** Kodlar bilgisayara (Python ve VS Code ortamına) alındı. `app.py` oluşturularak basit menü yapısı kuruldu.
* **Aşama 3: Çekirdek Terminal Uygulaması (C-R-C):** Kullanıcıdan veri alan ve terminalde tablo olarak sergileyen yapı ile "Hesaplama Motoru" tamamlandı.
* **Aşama 4: İleri Seviye Veri Analizi:** Tüm sistem profesyonel kütüphanelere entegre edildi. **Pandas** ile veri tablosu oluşturuldu, **Matplotlib** kullanılarak otomatik kategorik harcama (Pasta) grafiği çizdirildi.
* **Aşama 5: Google Gemini Yapay Zeka (AI) Entegrasyonu:** Sisteme `google-generativeai` kurularak "Akıllı Bütçe Asistanı" eklendi. Finansal veriler Google Yapay Zekasına analiz ettirilmeye başlandı.
* **Aşama 6: Modern Masaüstü (GUI) Yazılımı:** Siyah terminal ekranı terkedildi. **CustomTkinter** paketi sisteme entegre edildi ve modern karanlık temalı (Dark Mode) bir yazılım (`gui_app.py`) oluşturuldu. **Klasör yapısı (data ve config)** kurularak proje düzeni sağlandı.

---

## 2. İyileştirme ve Geliştirme Fikirleri (Gelecek Özellikleri)

Uygulamayı sıradan bir hobi programından ticari bir yazılıma taşımak isterseniz yapılabilecek geliştirmeler:

1. **Veritabanı Geçişi (SQLite veya PostgreSQL):**
   Şu an veriler metin tabanlı `gercek_veriler.csv` dosyasında tutuluyor. İleride kayıt sayısı binleri bulduğunda donma yaşamamak için tamamen lokal olan **SQLite** veritabanı altyapısına geçilebilir.
2. **Kayıt Düzenleme ve Silme (Update & Delete - CRUD):**
   Mevcut sistemde sadece kayıt "ekleniyor" (Create) ve "okunuyor" (Read). Uygulama arayüzüne, seçilen bir parçanın güncellenmesi veya yanlış girilenin silinmesi için butonlar eklenebilir.
3. **Filtreleme ve Arama Özelliği:**
   "Sadece Kadranları göster" veya "Pahalıdan ucuza sırala" mantığında listeleme arama çubuğu kodlanabilir.
4. **Çoklu Para Birimi (Döviz APİ):**
   Saat modifikasyon parçaları çoğunlukla yurt dışından Dolar/Euro ile alındığı için, Merkez Bankası anlık canlı kurunu çekip TL'ye (veya tam tersine) çeviren bir modül eklenebilir.
5. **Gelişmiş Grafikler:**
   Pasta grafiğine ek olarak, aylara göre harcamaların zaman içindeki artışını gösteren (*Çizgi Grafiği/Line Chart*) panelleri sağlanabilir.

---

## 3. Gizlilik, Veri Sızıntısı ve Koruma Önlemleri (Siber Güvenlik)

Bütçe verilerinizin ve şahsi Google AI anahtarınızın bilgisayarınızdan sızmasını veya çalınmasını engellemek amacıyla eklenebilecek koruma protokolleri:

### A. API Anahtarı (Key) Güvenliği
Bildiğiniz gibi API anahtarı size özeldir ve sızması durumunda kotanız başkaları tarafından sömürülebilir.
* **Mevcut Durum:** Şifrenizi kodun dışında, `config/api_key.txt` dosyasında tutarak ilk güvenliği sağladık. Ancak zararlı bir yazılım bu txt dosyasını kolayca okuyabilir.
* **İyileştirme (.env Değişkenleri):** API anahtarınızı endüstri standardı olan **Çevresel Değişken (Environment Variables - `.env`)** formatına dönüştürebiliriz. `python-dotenv` kütüphanesi kullanarak bu anahtarı işletim sisteminin hafızasına şifreleriz ve dosya olarak açıkça okunması büyük ölçüde zorlaşır.
* **Git ve İnternet Uyarısı:** Eğer bu projeyi GitHub vb. platformlara yedeklerseniz, kesinlikle klasöre bir `.gitignore` dosyası yazmalı ve `config/` ile `data/` klasörlerini internete gönderilmekten men etmeliyiz.

### B. Veri Sızıntısı ve Şifreleme (Encryption)
Program tamamen bilgisayarınızda (lokalde) çalışmaktadır. İzinsiz erişimleri kesmek için:
* **Veritabanı Şifreleme (AES-256 Kriptolama):** `gercek_veriler.csv` klasörünüz şu an sıradan bir Excel veya metin belgesi ile okunabilir haldedir. Gizliliği artırmak için Python'ın `cryptography` modülünü kullanarak dosyayı **şifreleyebiliriz**. Böylece uygulamaya özel bir Pin / Şifre arayüzü eklenir, doğru şifre girilmediğinde dosya açılmaya çalışılsa bile anlamsız karmaşık harfler görünür.
* **Yapay Zekaya Yollanan Verilerin Maskelenmesi (Data Masking):** Bütçe asistanı için verilerinizi prompt aracılığıyla Google sunucularına yolluyoruz. Google verileri standart olarak korusa da, kimliğinize ait detayları algoritmaya vermemek en güvenlisidir. Koda bir modül ekleyerek yapay zekaya veri yollanırken ürünlerin gerçek isimleri (Örn: Rolex Kasa) gizlenebilir veya sansürlenebilir. Yapay zeka sadece *A Kategorisi = 500TL, B Kategorisi = 200TL* gibi isimlerden arındırılmış veriyi analiz eder, böylelikle profiliniz %100 anonim kalır.

---
**Sonuç Değerlendirmesi:** Yazılımınız şu an bir kişisel kullanım aracı hedefleri doğrultusunda oldukça güvenilir ve hızlıdır. Herhangi bir aşamada projeyi tamamen şifrelenmiş ticari/profesyonel bir güvenlik standartına geçirmek isterseniz bu başlıkları sırasıyla uygulayabiliriz.
