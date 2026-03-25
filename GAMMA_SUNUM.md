# BütçeM — Akıllı Bütçe ve Ürün Takip Asistanı
## Gamma Sunum İçeriği (14 Slayt)

---

## SLAYT 1: BAŞLIK VE PROJE ÖZETİ

### BütçeM — Akıllı Bütçe ve Ürün Takip Asistanı

**Kişisel finansınızı kontrol altına alın.**

Harcamalarınızı takip edin, taksitlerinizi yönetin, e-ticaret sitelerinden anlık fiyat karşılaştırması yapın ve yapay zeka destekli finansal analiz alın — hepsi tek bir masaüstü uygulamasında.

- Masaüstü Uygulaması (Windows EXE)
- Python & CustomTkinter ile geliştirildi
- Açık Kaynak — GitHub'da yayında

**GitHub:** github.com/KAMOSS12/ButceM

---

## SLAYT 2: PROJENİN AMACI VE HEDEF KİTLE

### Neden BütçeM?

Günümüzde kişisel finansal yönetim giderek karmaşıklaşıyor: birden fazla kredi kartı taksiti, farklı e-ticaret platformlarındaki değişken fiyatlar ve döviz kurlarının anlık etkisi. BütçeM, tüm bu karmaşıklığı tek bir arayüzde sadeleştirmek için tasarlandı.

### Proje Amacı

- Kişisel harcamaları ve taksitli ödemeleri merkezi bir noktadan takip etmek
- E-ticaret sitelerinden anlık fiyat karşılaştırması yapmak
- Yapay zeka ile finansal analiz ve tasarruf önerileri sunmak
- Tek dosya EXE ile kolay kurulum sağlamak

### Hedef Kitle

| Segment | İhtiyaç |
|---------|---------|
| **Bireysel Kullanıcılar** | Kişisel bütçesini düzenli takip etmek |
| **Kredi Kartı Kullanıcıları** | Taksitli harcamalarını ve kalan ödemelerini görmek |
| **E-Ticaret Tüketicileri** | Farklı platformlardaki fiyatları karşılaştırmak |

---

## SLAYT 3: TEKNOLOJİ STACK'İ

### Kullanılan Teknolojiler

#### Çekirdek
- **Python 3.12+** — Ana geliştirme dili
- **CustomTkinter** — Modern görünümlü GUI framework
- **SQLite3** — Gömülü yerel veritabanı

#### Veri & Görselleştirme
- **Pandas** — Veri analizi ve işleme
- **Matplotlib** — Grafik ve dashboard oluşturma
- **OpenPyXL** — Excel okuma/yazma

#### Web & API
- **BeautifulSoup4** — HTML parse (N11 scraping)
- **Selenium** — Headless Chrome otomasyon (Amazon scraping)
- **Requests** — HTTP istekleri (Trendyol API, döviz kuru)
- **Google Generative AI** — Gemini AI entegrasyonu

#### Bildirim & Otomasyon
- **Plyer** — Windows masaüstü bildirimleri
- **threading.Timer** — Zamanlanmış arka plan görevleri (yedekleme, bildirim, fiyat takip)
- **concurrent.futures** — Paralel web arama (ThreadPoolExecutor)

#### Güvenlik & Dağıtım
- **hashlib (SHA-256)** — PIN şifreleme
- **python-dotenv** — Ortam değişkenleri yönetimi
- **PyInstaller** — Tek dosya EXE derleme
- **VBScript** — Kurulum sihirbazı (kısayol oluşturma)

---

## SLAYT 4: SİSTEM MİMARİSİ

### Genel Mimari Yapı

```
┌─────────────────────────────────────────────────────────┐
│                    KULLANICI ARAYÜZÜ                    │
│                   (CustomTkinter GUI)                   │
│                                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │  Ürün    │ │  Liste   │ │Dashboard │ │  Fiyat    │  │
│  │  Ekleme  │ │  & CRUD  │ │ Grafik   │ │  Takip    │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                │
│  │  AI      │ │ Web'den  │ │  Sistem  │                │
│  │ Danışman │ │  Bul     │ │ Ayarları │                │
│  └──────────┘ └──────────┘ └──────────┘                │
│                   gui_app.py                            │
└───┬──────────┬──────────┬──────────┬────────────────────┘
    │          │          │          │
┌───▼────┐ ┌──▼───┐ ┌───▼────┐ ┌───▼──────────────┐
│database│ │curren│ │web_    │ │profile_manager   │
│  .py   │ │cy.py │ │scraper │ │backup_manager    │
│        │ │      │ │  .py   │ │notification_mgr  │
│        │ │      │ │        │ │price_tracker     │
└───┬────┘ └──┬───┘ └───┬────┘ └───┬──────────────┘
    │         │          │          │
┌───▼────┐ ┌──▼────┐ ┌──▼─────────────────────┐
│SQLite3 │ │Exch.  │ │Trendyol │ N11 │ Amazon │
│profil/ │ │Rate   │ │  API    │ BS4 │  Sel.  │
│urunler │ │API    │ └─────────────────────────┘
│  .db   │ │(cache)│
└────────┘ └───────┘
```

### Modüler Yapı

| Modül | Satır | Sorumluluk |
|-------|-------|------------|
| `gui_app.py` | ~1550 | Tüm GUI ekranları, iş mantığı, güvenlik |
| `database.py` | ~170 | SQLite CRUD, migration, dinamik DB yolu |
| `web_scraper.py` | ~200 | 3 platform scraping, paralel arama, retry |
| `profile_manager.py` | ~266 | Çoklu profil CRUD, ayarlar, migrasyon |
| `backup_manager.py` | ~136 | Zamanlanmış otomatik yedekleme |
| `notification_manager.py` | ~138 | Masaüstü bildirimleri (plyer) |
| `price_tracker.py` | ~83 | Fiyat takip alarmı, periyodik kontrol |
| `currency.py` | ~33 | Döviz kuru API (1 saat cache) |
| `installer.py` | ~768 | 4 adımlı kurulum sihirbazı |
| `smoke_test.py` | ~170 | 14 testli otomatik test paketi |

---

## SLAYT 5: VERİ AKIŞ DİYAGRAMI — Bölüm 1

### Uygulama Başlatma ve Ürün Yönetimi

```
┌──────────────┐
│  Uygulama    │
│  Başlatılır  │
└──────┬───────┘
       ▼
┌──────────────┐
│  Profil      │──► Yeni profil oluştur (isim + PIN)
│  Seçimi      │
└──────┬───────┘
       ▼
┌──────────────┐     Hatalı      ┌──────────────┐
│  PIN Giriş   │────────────────►│ Brute Force  │
│  Ekranı      │    3 hata→15sn  │  Kilitleme   │
│ (SHA-256     │    5 hata→60sn  └──────┬───────┘
│  doğrulama)  │◄───────────────────────┘
└──────┬───────┘   Süre dolunca
       │ Doğru PIN
       ▼
┌──────────────┐          ┌──────────────┐
│  Profil DB   │─────────►│  Arka Plan   │
│  Yüklenir    │          │  Servisler   │
│  Ana Arayüz  │          │ • Döviz kuru │
│  Açılır      │          │ • Yedekleme  │
└──────┬───────┘          │ • Bildirimler│
       │                  │ • Fiyat takip│
       │                  └──────────────┘
       ▼
┌──────────────┐   Nakit/Taksit   ┌──────────────┐
│  Ürün Ekleme │─────────────────►│  Fiyat +     │
│  Formu       │   seçimi         │  Vade Farkı  │
└──────────────┘                  │  Hesaplama   │
                                  └──────┬───────┘
                                         ▼
                                  ┌──────────────┐
                                  │   SQLite     │
                                  │  Veritabanı  │
                                  │  (INSERT)    │
                                  └──────────────┘
```

---

## SLAYT 6: VERİ AKIŞ DİYAGRAMI — Bölüm 2

### Analiz, Web Arama ve Dışa Aktarma

```
┌─────────────────────────────────────────────────────┐
│                    VERİTABANI                        │
│                   (urunler.db)                       │
└───────┬──────────────┬──────────────┬───────────────┘
        │              │              │
        ▼              ▼              ▼
┌──────────────┐┌──────────────┐┌──────────────┐
│   Liste &    ││  Dashboard   ││   AI         │
│   Filtreleme ││  (Pandas +   ││  Danışmanı   │
│              ││  Matplotlib) ││              │
│ • Tablo      ││              ││ • Veri       │
│ • Arama      ││ • Pasta      ││   maskeleme  │
│ • Özet satır ││   grafiği    ││ • Gemini API │
│ • Bütçe +    ││ • Çizgi      ││   çağrısı    │
│   dolar karş.││   grafiği    ││ • Öneri      │
└──────────────┘└──────────────┘└──────────────┘

┌──────────────┐   Arka plan     ┌──────────────┐
│  Web'den     │───thread────►   │  Trendyol    │
│  Ürün Bul    │                 │  N11         │
│              │                 │  Amazon      │
│  Arama       │                 └──────┬───────┘
│  sorgusu     │                        │
└──────────────┘                        ▼
                                 ┌──────────────┐
       Tek tıkla kaydet          │  Sonuçlar    │
       ◄─────────────────────────│  (fiyata     │
       ▼                         │  göre sıralı)│
┌──────────────┐                 └──────────────┘
│  Veritabanına│
│  Otomatik    │
│  Kayıt       │
└──────────────┘

┌──────────────┐                 ┌──────────────┐
│  Excel       │◄───────────────►│  Toplu Veri  │
│  Export      │   Import/Export │  İçe Aktarma │
└──────────────┘                 └──────────────┘
```

---

## SLAYT 7: ANA MODÜLLER — GUI ve Veritabanı

### gui_app.py — Ana Uygulama (~1200 satır)

7 ana ekran içerir:

| Ekran | İşlev |
|-------|-------|
| **Ürün Ekleme** | Nakit/taksitli ödeme formu, vade farkı hesaplama |
| **Liste & CRUD** | Filtreleme, arama, düzenleme, silme, özet bütçe, kolon sıralaması |
| **Dashboard** | Pasta ve çizgi grafikleri (Matplotlib) |
| **AI Danışmanı** | Gemini AI ile finansal analiz |
| **Web'den Bul** | E-ticaret fiyat karşılaştırması + fiyat takip entegrasyonu |
| **Fiyat Takip** | Periyodik fiyat kontrolü ve düşüş alarmı |
| **Sistem Ayarları** | Profil yönetimi, yedekleme, bildirimler, PIN, tema, API key |

Ek özellikler:
- Çoklu kullanıcı profili (profil başına ayrı veritabanı)
- Profil seçim + PIN giriş ekranı + brute force koruması
- Auto-lock (5 dk hareketsizlik)
- Zamanlanmış otomatik yedekleme (günlük/haftalık/aylık)
- Masaüstü bildirimleri (taksit hatırlatma, bütçe uyarısı, aylık özet)
- 4 adımlı kurulum sihirbazı
- Excel import/export

### database.py — Veritabanı Katmanı

- **Context Manager** ile güvenli SQLite bağlantı yönetimi
- **Şema Migration**: Otomatik sütun ekleme (ALTER TABLE)
- **Parametrik Sorgulama**: SQL injection koruması (`?` placeholder)
- **CSV Başlangıç Verisi**: İlk çalışmada örnek veri aktarımı

---

## SLAYT 8: ANA MODÜLLER — Web Scraper, Döviz ve Test

### web_scraper.py — E-Ticaret Botları

| Platform | Yöntem | Teknoloji |
|----------|--------|-----------|
| **Trendyol** | REST API | Requests + JSON parse |
| **N11** | Statik HTML | BeautifulSoup4 |
| **Amazon.com.tr** | Dinamik sayfa | Selenium Headless Chrome |

Her platform için:
- 5 saniyelik timeout limiti + otomatik retry (2 tekrar)
- Paralel arama (ThreadPoolExecutor) — Trendyol + N11 eş zamanlı
- Tekil ürün fiyat çekme (fiyat takip sistemi için)
- Spesifik hata mesajları (timeout, bağlantı, HTTP durum kodu)
- Fiyata göre sıralı sonuç listesi

### currency.py — Döviz Kuru Modülü

- ExchangeRate API üzerinden anlık **USD/TRY** ve **EUR/TRY** kurları
- 1 saatlik önbellek (cache) ile gereksiz API çağrılarını azaltma
- Hata durumunda eski cache verisiyle devam etme (stale fallback)

### Yeni Modüller (v2.2)

| Modül | İşlev |
|-------|-------|
| `profile_manager.py` | Çoklu kullanıcı profili yönetimi, ayarlar, legacy veri migrasyonu |
| `backup_manager.py` | Zamanlanmış otomatik DB yedekleme, eski yedek temizleme, geri yükleme |
| `notification_manager.py` | Masaüstü bildirimleri (plyer): taksit hatırlatma, bütçe uyarısı, aylık özet |
| `price_tracker.py` | Periyodik fiyat kontrolü (6 saat), hedef fiyat düşüş alarmı |
| `installer.py` | 4 adımlı kurulum sihirbazı, Windows registry, kısayol, kaldırma |

### smoke_test.py — Otomatik Test Paketi

8 modül, 14 test:
1. **database.py** — Dinamik path, CRUD, monthly spending, fiyat_takip CRUD
2. **currency.py** — Döviz kuru cache
3. **profile_manager.py** — Profil oluşturma/silme, ayar yükleme/kaydetme
4. **backup_manager.py** — Yedek oluşturma/listeleme
5. **notification_manager.py** — Manager başlatma
6. **price_tracker.py** — Tracker başlatma
7. **web_scraper.py** — Import doğrulama
8. **installer.py** — Import doğrulama

Sonuç: **%100 başarı oranı (14/14)**

---

## SLAYT 9: ALGORİTMALAR VE TEMEL MANTIK

### SHA-256 PIN Güvenliği

```
Kullanıcı PIN girer
        ▼
PIN → SHA-256 Hash
        ▼
Hash ⟺ .env'deki hash karşılaştırması
        ▼
   Eşleşme?
  /        \
Evet       Hayır
 ▼           ▼
Giriş    Sayacı artır
başarılı   3 hata → 15sn kilit
           5 hata → 60sn kilit
```

### Finansal Hesaplama Motoru

```
Toplam Maliyet = Baz Fiyat + Vade Farkı

Nakit Ödeme (taksit = 0):
  → Toplam = Fiyat

Taksitli Ödeme (taksit ≥ 2):
  → Toplam = Fiyat + Vade Farkı
  → Aylık Taksit = Toplam / Taksit Sayısı
  → Ödenen = Ödenen Taksit × Aylık Taksit
  → Kalan  = Toplam - Ödenen
```

### Veri Maskeleme (AI Gizliliği)

```
Veritabanı: "iPhone 15 Pro, 64.999₺, Elektronik"
                    ▼ Maskeleme
Gemini'ye giden: "Ürün 1, 64.999₺, Elektronik"

→ Kullanıcı ürün isimleri AI ile paylaşılmaz
→ Sadece kategori + fiyat bilgisi gönderilir
```

### Auto-Lock Mekanizması

```
Fare/Klavye hareketi izlenir
        ▼
Son hareket zamanı güncellenir
        ▼
5 dakika hareketsizlik?
  /        \
Hayır     Evet
 ▼          ▼
Devam    Ekran kilitlenir
         PIN ekranı açılır
```

---

## SLAYT 10: API VE ENTEGRASYONLAR

### Dış Servis Entegrasyonları

| Entegrasyon | Amaç | Yöntem |
|-------------|-------|--------|
| **Google Gemini AI** | Finansal analiz, tasarruf önerileri | `gemini-1.5-flash` modeli, kullanıcı API key'i |
| **ExchangeRate API** | Anlık USD/TRY, EUR/TRY kurları | Ücretsiz REST API, key gerektirmez |
| **Trendyol API** | Ürün arama, fiyat çekme | Public Search API (JSON) |
| **N11** | Ürün arama, fiyat çekme | Web scraping (HTML parse) |
| **Amazon.com.tr** | Ürün arama, fiyat çekme | Selenium headless tarama |

### Entegrasyon Mimarisi

```
┌─────────────┐
│  BütçeM     │
│  Uygulaması │
└──────┬──────┘
       │
       ├──► Gemini AI API ──► Finansal analiz yanıtı
       │    (HTTPS/JSON)
       │
       ├──► ExchangeRate API ──► USD/TRY, EUR/TRY
       │    (HTTPS/JSON)
       │
       ├──► Trendyol API ──► Ürün listesi (JSON)
       │    (HTTPS/JSON)
       │
       ├──► N11.com ──► HTML parse ──► Ürün listesi
       │    (HTTPS/HTML)
       │
       └──► Amazon.com.tr ──► Selenium render ──► Ürün listesi
            (Headless Chrome)
```

### Güvenlik Notları

- Gemini API key kullanıcıda saklanır (`.env` dosyası)
- API key asla kaynak kodda bulunmaz
- AI'ya gönderilen verilerde ürün isimleri maskelenir
- Tüm HTTP isteklerinde timeout uygulanır

---

## SLAYT 11: KARŞILAŞILAN ZORLUKLAR VE ÇÖZÜMLER

### Zorluk 1: Türkçe Karakter Sorunu (VBScript)
- **Problem:** Masaüstü kısayollarında "BütçeM" → "ÃœtÃ§eM" olarak görünüyordu
- **Kök Neden:** VBScript dosyası UTF-8 encoding ile kaydedilmişti, Windows cscript UTF-16LE bekliyor
- **Çözüm:** VBS dosya encoding'i UTF-16LE + BOM'a dönüştürüldü ✓

### Zorluk 2: Dashboard Veri Hatası
- **Problem:** DataFrame üzerinde geçersiz `.get()` metodu ve eksik `vade_farki` sütunu
- **Kök Neden:** SQL sorgusu bu sütunu çekmiyordu, Pandas API yanlış kullanılıyordu
- **Çözüm:** SQL sorgusuna `vade_farki` eklendi, `.get()` yerine `.fillna(0.0)` kullanıldı ✓

### Zorluk 3: Sessiz Hata Yutma
- **Problem:** Web scraper hatalarında kullanıcıya hiçbir geri bildirim verilmiyordu (`except: pass`)
- **Kök Neden:** Genel exception yakalama, hata mesajı döndürmeme
- **Çözüm:** Her platform için spesifik hata mesajları (timeout, bağlantı, HTTP kodu) ✓

### Zorluk 4: PIN Brute Force Açığı
- **Problem:** Sınırsız PIN deneme hakkı
- **Çözüm:** Kademeli kilitleme → 3 hata: 15sn, 5 hata: 60sn ✓

### Zorluk 5: Bozuk requirements.txt
- **Problem:** Encoding hatası nedeniyle her karakter arasına boşluk girmişti
- **Çözüm:** Sadece gerçek bağımlılıklarla temiz dosya yeniden yazıldı ✓

---

## SLAYT 12: PROJE SONUÇLARI VE ÇIKTILAR

### Teslim Edilen Çıktılar

#### Tam İşlevsel Masaüstü Uygulaması
- 7 ekranlı modern GUI
- Çoklu kullanıcı profili desteği
- Karanlık / Aydınlık tema desteği
- PIN korumalı güvenli giriş + profil seçimi

#### Self-Installer Sistemi
- PyInstaller ile tek dosya EXE
- 4 adımlı kurulum sihirbazı (dizin seçimi, disk kontrolü, ilerleme çubuğu)
- Otomatik masaüstü + başlat menüsü kısayolu
- Windows Programlar ve Özellikler kaydı + kaldırma desteği

#### E-Ticaret Fiyat Karşılaştırması + Fiyat Takip
- 3 farklı platform: Trendyol, N11, Amazon
- Paralel arama + otomatik retry mekanizması
- Tek tıkla veritabanına kayıt
- Fiyat takip alarmı: hedef fiyat belirle, düşüşte bildirim al

#### Akıllı Bildirim ve Yedekleme Sistemi
- Zamanlanmış otomatik veritabanı yedekleme (günlük/haftalık/aylık)
- Taksit hatırlatma, bütçe uyarısı, aylık özet bildirimleri
- Windows masaüstü bildirimleri (plyer)

#### AI Destekli Finansal Analiz
- Gemini AI ile tasarruf önerileri
- Gizlilik korumalı veri maskeleme
- Kullanıcı dostu analiz arayüzü

### Sayısal Sonuçlar

| Metrik | Değer |
|--------|-------|
| Toplam kod satırı | ~3.500+ |
| Modül sayısı | 10 modül |
| GUI ekran sayısı | 7 ekran |
| Desteklenen e-ticaret platformu | 3 |
| Kullanıcı profili desteği | Sınırsız |
| Bildirim türü | 4 (taksit, bütçe, özet, fiyat) |
| Test başarı oranı | %100 (14/14) |
| Dağıtım formatı | Tek dosya EXE + Kurulum Sihirbazı |
| Lisans | Açık kaynak (GitHub) |

---

## SLAYT 13: v2.2'DE EKLENEN ÖZELLİKLER VE GELİŞTİRİLEBİLECEK NOKTALAR

### v2.2'de Tamamlanan Geliştirmeler

| Özellik | Durum | Açıklama |
|---------|-------|----------|
| **Döviz Kuru Cache** | Tamamlandı | 1 saatlik TTL + stale fallback |
| **Otomatik Yedekleme** | Tamamlandı | Günlük/haftalık/aylık zamanlanmış yedekleme |
| **Bildirim Sistemi** | Tamamlandı | Taksit hatırlatma, bütçe uyarısı, aylık özet |
| **Fiyat Takip Alarmı** | Tamamlandı | Periyodik fiyat kontrolü + düşüş bildirimi |
| **Çoklu Kullanıcı** | Tamamlandı | Profil başına ayrı DB ve ayarlar |
| **Paralel Web Arama** | Tamamlandı | ThreadPoolExecutor ile eş zamanlı arama |
| **Kurulum Sihirbazı** | Tamamlandı | 4 adımlı wizard + registry + kaldırma |
| **10 Bug Düzeltmesi** | Tamamlandı | Race condition, TypeError, sıralama vb. |

### Gelecek Geliştirmeler

| Özellik | Açıklama | Öncelik |
|---------|----------|---------|
| **Gelişmiş PIN Güvenliği** | PBKDF2 + salt, Windows Credential Manager | Orta |
| **Mobil Uygulama** | Companion mobile app ile senkronizasyon | Düşük |
| **Bulut Yedekleme** | Google Drive / OneDrive entegrasyonu | Düşük |
| **Grafik Raporları** | PDF rapor oluşturma ve e-posta gönderimi | Düşük |

### Gelişim Yol Haritası

```
    v1.0                v2.0                v2.2
┌──────────┐      ┌──────────┐      ┌──────────────┐
│ Temel    │ ───► │ AI + Web │ ───► │ Çoklu profil │
│ CRUD     │      │ Scraping │      │ Oto. yedek   │
│ SQLite   │      │ Gemini   │      │ Bildirimler  │
│ PIN      │      │ Dark/Lgt │      │ Fiyat takip  │
│          │      │ Excel    │      │ Kurulum wiz. │
└──────────┘      └──────────┘      └──────────────┘
```

---

## SLAYT 14: ÖZET VE KAPANIŞ

### BütçeM — Tek Bakışta

BütçeM, kişisel finans yönetimini basitleştiren, yapay zeka destekli, güvenli ve kullanıcı dostu bir masaüstü uygulamasıdır.

### Öne Çıkan Özellikler

- **Çoklu Profil Desteği** — Her kullanıcı kendi veritabanı ve ayarlarıyla çalışır
- **Kapsamlı Bütçe Takibi** — Nakit ve taksitli harcamalar, döviz karşılığı, aylık bütçe limiti
- **Akıllı Fiyat Karşılaştırması** — 3 e-ticaret platformundan paralel arama + fiyat takip alarmı
- **AI Destekli Analiz** — Gemini ile gizlilik korumalı finansal danışmanlık
- **Otomatik Yedekleme** — Zamanlanmış DB yedekleme, geri yükleme, eski yedek temizleme
- **Masaüstü Bildirimleri** — Taksit hatırlatma, bütçe uyarısı, fiyat düşüş alarmı
- **Güçlü Güvenlik** — SHA-256 PIN, auto-lock, brute force koruması, SQL injection önleme
- **Kolay Kurulum** — Tek dosya EXE, 4 adımlı kurulum sihirbazı, kaldırma desteği

### Teknoloji Özeti

```
Python 3.12+ │ CustomTkinter │ SQLite3 │ Pandas │ Matplotlib
Selenium │ BeautifulSoup4 │ Gemini AI │ PyInstaller │ Plyer
```

### Proje Bağlantıları

- **GitHub:** github.com/KAMOSS12/ButceM
- **Lisans:** Açık Kaynak

---

> **Teşekkürler!**
> Sorularınız için hazırım.

---

## GAMMA'DA KULLANIM TALİMATLARI

### Bu dokümanı Gamma'ya aktarma adımları:

1. **gamma.app** sitesine gidin
2. **"Create new"** → **"Paste in text"** seçin
3. Bu dokümanın tamamını kopyalayıp yapıştırın
4. Gamma otomatik olarak slaytlara böler
5. **Tema:** "Professional" veya "Modern" seçin
6. **Renk paleti:** Koyu mavi / turkuaz tonları önerilir
7. Akış diyagramlarını Gamma'nın diagram aracıyla görselleştirin

### Alternatif: Manuel oluşturma
- Her `## SLAYT` başlığını ayrı bir slayt olarak oluşturun
- Tablolar ve kod blokları Gamma'da otomatik formatlanır
- Diyagramlar için Gamma'nın yerleşik "Smart layout" özelliğini kullanın
