import os
import sys
import sqlite3
import time

# 1. Veritabani (CRUD) Testi
try:
    import database
    print("TEST 1: Veritabani Modulu... ", end="")

    # Gecici test DB olustur
    orijinal_path = database.DB_PATH
    database.DB_PATH = "test_urunler.db"
    os.makedirs(os.path.dirname(database.DB_PATH) if os.path.dirname(database.DB_PATH) else ".", exist_ok=True)

    # Tabloyu yeniden olustur
    conn = sqlite3.connect(database.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urunler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kategori TEXT NOT NULL,
            urun_adi TEXT NOT NULL,
            fiyat REAL NOT NULL,
            durum TEXT NOT NULL,
            link TEXT DEFAULT '',
            taksit_sayisi INTEGER DEFAULT 1,
            vade_farki REAL DEFAULT 0.0,
            odenen_taksit INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

    database.urun_ekle("Test Kategori", "Test Urun", 999.0, "Evet", "https://test.com", 1, 0.0, 0)
    urunler = database.urunleri_getir()
    assert len(urunler) > 0, "Urun veritabanina eklenemedi."

    test_id = urunler[0][0]
    database.urun_guncelle(test_id, "Yeni Kategori", "Yeni Urun", 111.0, "Hayir", "", 2, 50.0, 1)
    database.urun_sil(test_id)

    # Temizlik
    database.DB_PATH = orijinal_path
    time.sleep(0.5)
    try:
        os.remove("test_urunler.db")
    except Exception:
        pass
    print("BASARILI (DB ISLEMLER SORUNSUZ)")
except Exception as e:
    print(f"FAILED 1 -> {e}")

# 2. Doviz API Testi
try:
    from currency import get_exchange_rates
    print("TEST 2: Doviz API Yaniti... ", end="")
    rates = get_exchange_rates()
    assert isinstance(rates.get("USD"), float), "USD formati bozuk."
    print("BASARILI (API SAGLAM)")
except Exception as e:
    print(f"FAILED 2 -> {e}")

# 3. Web Scraper Testi
try:
    from web_scraper import trendyol_arama, n11_arama
    print("TEST 3: E-Ticaret Arama Botlari (Trendyol/N11)... ", end="")
    t_res, t_err = trendyol_arama("masa")
    n_res, n_err = n11_arama("masa")
    assert isinstance(t_res, list) and isinstance(n_res, list), "Donen veriler hatali."
    if t_err or n_err:
        print(f"UYARI (hatalar: {t_err + n_err})")
    else:
        print("BASARILI (SCRAPER CALISIYOR)")
except Exception as e:
    print(f"FAILED 3 -> {e}")

print("--- TUM MODUL TESTLERI TAMAMLANDI ---")
