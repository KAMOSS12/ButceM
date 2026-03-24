<h1 align="center">BütçeM - Akıllı Bütçe ve Ürün Takip Asistanı</h1>

<p align="center">
  <strong>Python, CustomTkinter ve Google Gemini AI ile geliştirilmiş<br>finansal analiz, akıllı bütçeleme ve ürün takip masaüstü uygulaması.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/GUI-CustomTkinter-brightgreen.svg" alt="CTK">
  <img src="https://img.shields.io/badge/Database-SQLite3-lightgrey.svg" alt="SQLite">
  <img src="https://img.shields.io/badge/AI-Google_Gemini-orange.svg" alt="AI">
  <img src="https://img.shields.io/badge/License-MIT-purple.svg" alt="License">
</p>

---

## Neden BütçeM?

Hepimizin e-ticaret sitelerinde almak istediği ürünler veya kredi kartıyla ödediği taksitli harcamalar oluyor. **BütçeM**, basit bir parça takip programından öte; **kendi web botlarıyla** e-ticaret fiyatlarını okuyan, **Google Gemini** ile harcamalarınızı analiz edip tasarruf tavsiyeleri veren ve **Self-Installer** barındıran kapsamlı bir kişisel finans asistanıdır.

## Özellikler

- **Yapay Zeka (Gemini AI) Entegrasyonu:** Harcama verilerinizi Gemini AI'a gönderin, kişisel tasarruf önerileri ve bütçe sağlığı analizi alın. Ürün isimleri maskelenerek gizliliğiniz korunur.
- **E-Ticaret Otomasyonu:** Trendyol, N11 ve Amazon üzerinden tek tıkla ürün fiyatı aratın ve veritabanınıza kaydedin.
- **Finansal Takip:** Taksit sayısı, vade farkı ve ödenen taksit bilgileriyle gerçek banka harcamalarınızı takip edin.
- **Dashboard:** Matplotlib ile kategori bazlı pasta grafikleri ve birikimli harcama çizgi grafikleri.
- **Güvenlik:** SHA-256 ile şifrelenmiş PIN, 5 dakika hareketsizlikte otomatik kilit, SQL injection koruması.
- **Kurulum Sihirbazı:** PyInstaller ile derlenmiş tek dosya exe. Masaüstü ve Başlat menüsü kısayollarını otomatik oluşturur.
- **Döviz Kurları:** Anlık USD/EUR kuru ile toplam harcamalarınızı dolar cinsinden görün.
- **Excel Import/Export:** Verilerinizi Excel veya CSV formatında dışa/içe aktarın.

---

## Teknolojiler

| Alan | Araç |
| :--- | :--- |
| **Arayüz** | CustomTkinter, Tkinter |
| **Veritabanı** | SQLite3 |
| **Web Otomasyon** | Selenium, BeautifulSoup4, Requests |
| **Veri Analizi** | Pandas, Matplotlib, OpenPyxl |
| **Yapay Zeka** | google-generativeai (Gemini) |
| **Paketleme** | PyInstaller |

---

## Kurulum

### Kaynak Koddan Çalıştırma

```bash
git clone https://github.com/KULLANICI_ADINIZ/ButceM.git
cd ButceM
pip install -r requirements.txt
cp .env.example .env
python gui_app.py
```

> Varsayılan PIN: `1234` — Sistem Ayarları'ndan değiştirebilirsiniz.

### Yapılandırma

`.env` dosyasına Gemini API anahtarınızı ekleyin (veya uygulama içi Sistem Ayarları'ndan):

```
GEMINI_API_KEY=buraya_api_anahtariniz
APP_PIN=1234
```

### Derlenmiş Sürüm (EXE)

Tek dosya exe'yi çalıştırın — Kurulum Sihirbazı sizi yönlendirecektir.

---

## Lisans

MIT License
