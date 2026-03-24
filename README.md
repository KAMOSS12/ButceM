<h1 align="center">📦 Ürün Takip ve Finans Asistanı (V1.0)</h1>

<p align="center">
  <strong>Python, CustomTkinter ve Google Gemini AI kullanılarak geliştirilen tam teşekküllü, açık kaynaklı <br> finansal analiz, akıllı bütçeleme ve ürün takip masaüstü uygulaması.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/GUI-CustomTkinter-brightgreen.svg" alt="CTK">
  <img src="https://img.shields.io/badge/Database-SQLite3-lightgrey.svg" alt="SQLite">
  <img src="https://img.shields.io/badge/AI-Google_Gemini-orange.svg" alt="AI">
  <img src="https://img.shields.io/badge/License-MIT-purple.svg" alt="License">
</p>

---

## 🌟 Neden Bu Proje?
Hepimizin dijital hayatta, e-ticaret sitelerinde (Trendyol, Amazon) almak istediği ürünler veya kredi kartıyla ödediği taksitli cihazlar oluyor. **Ürün Takip Sistemi**, basit bir parça takip programından ziyade; **Kendi Web Botlarıyla** e-ticaret fiyatlarını okuyan, **Google Gemini** ile harcamalarınızı analiz edip size tasarruf tavsiyeleri veren ve **Self-Installer (Kurulum Sihirbazı)** barındıran ticari kalitede kişiselleştirilmiş bir yazılımdır.

## 🚀 Öne Çıkan Özellikler

- **🤖 Yapay Zeka (Gemini AI) Entegrasyonu:** Sisteme eklediğiniz parçaları ve bütçe planınızı saniyeler içerisinde Yapay Zekaya sunun. Sizin için harcama/tasarruf önerileri ve bütçe sağlığı skorunuz belirlensin. (Prompt Maskeleme ile gizliliğiniz %100 korunur).
- **🕸️ E-Ticaret Otomasyonu (Bots):** Amazon (Headless Selenium), N11 ve Trendyol (BeautifulSoup) platformlarından tek tıkla ürün fiyatı aratın ve veritabanınıza "Hızlı Kayıt" ile kaydedin.
- **💰 Finansal Matematik:** Bir ürüne sadece fiyat eklemek yerine; "Taksit Sayısı", "Vade Farkı", "Ödenen Taksit" gibi gerçek dünyadaki banka harcamalarınızı kusursuzca takip edin.
- **📊 Gömülü İstatistik Analizi:** Matplotlib kullanılarak direkt arayüzün içerisine (Harici bir sayfa olmadan) gömülmüş Kategori Çizgi Grafikleri (LineChart) ve Pasta Dağılımlarına (PieChart) erişin.
- **🔐 Siber Güvenlik (Sec & QA):** SHA-256 algoritmalı PIN ekranı, Auto-Lock (Fare hareketsizliği kilitlenmesi), SQL Injection zırhı ve Local File Directory güvenlikleri!
- **📦 Kurulum Sihirbazı (Self-Installer):** Uygulama `pyinstaller` ile tek dosyada derlendi. Eğer hedef dizinde kurulu değilse sizi süslü bir Install Sihirbazı ekranı ile karşılar. Dilediğiniz diski seçersiniz; .vbs mimarisi ile Desktop'a şımşek hızında kısayollarınızı atar ve kullanım kılavuzunu kurar!

---

## 🛠️ Kullanılan Teknolojiler (Tech Stack)

| Teknoloji Kapsamı | Kullanılan Araç / Kütüphane |
| :--- | :--- |
| **Arayüz (GUI)** | CustomTkinter (Ctk), Tkinter |
| **Veritabanı** | SQLite 3 (Lokal kalıcı depolama) |
| **Web Otomasyon** | Selenium, BeautifulSoup4, Requests, webdriver-manager |
| **Veri Analizi** | Pandas, Matplotlib, OpenPyxl (Excel Export/Import) |
| **Yapay Zeka** | `google-generativeai` (Gemini Pro/Flash Modelleri) |
| **Paketleme / Build** | PyInstaller (Windows PE format executable) |

---

## ⚙️ Yerel (Lokal) Ortamda Çalıştırma

Bu uygulamayı kaynak kodlarıyla kullanmak veya kendi projelerinize ilham vermesi için klonlamak isterseniz:

1. **Repoyu Klonlayın:**
```bash
git clone https://github.com/KULLANICI_ADINIZ/urun-takip-ai.git
cd urun-takip-ai
```

2. **Gereksinimleri Kurun:**
```bash
pip install -r requirements.txt
```

3. **Projeyi Başlatın:**
```bash
python gui_app.py
```
> *(İlk açılışta sistem kendini kurarken sizden belirlemenizi istediği bir 4 haneli PIN şifresi soracaktır. Bu kodu unutmayın.)*

---

### 🔥 Geliştirici Sürümü (Derlenmiş Ürün) Kurulumu
Eğer kodlarla hiç uğraşmak istemiyorsanız klasördeki tek parçalık `.exe` dosyası (Kurulum Sihirbazı) sayesinde uygulamayı normal bir C++ yazılımı gibi Windows cihazınıza saniyeler içinde zerk edip `Kullanim_Kilavuzu.txt` ile birlikte kullanıma başlayabilirsiniz.

> **Emeği Geçenler:** Bu proje, baştan sona devasa bir yapay zeka-insan Eşli Programlama (Pair Programming) ürünüdür! Yorumlarınızı ve Yıldız (Star) bağışlarınızı eksik etmeyin! 🌟