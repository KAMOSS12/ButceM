"""
BütçeM v2.2 - Smoke Test
Tüm modüllerin temel fonksiyonlarını doğrular.
"""

import os
import sys
import sqlite3
import time
import shutil
import tempfile

passed = 0
failed = 0


def test(name, func):
    global passed, failed
    print(f"  {name}... ", end="")
    try:
        func()
        print("OK")
        passed += 1
    except Exception as e:
        print(f"FAIL -> {e}")
        failed += 1


# ============================================================
# 1. database.py
# ============================================================
print("\n[1] database.py")

import database

def test_db_set_path():
    database.set_db_path("test_smoke.db")
    assert database.DB_PATH == "test_smoke.db"

def test_db_get_connection():
    conn = database.get_connection()
    assert conn is not None
    conn.close()

def test_db_init():
    database.init_db()
    conn = database.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='urunler'")
    assert cur.fetchone() is not None
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fiyat_takip'")
    assert cur.fetchone() is not None
    conn.close()

def test_db_crud():
    database.urun_ekle("Test", "Smoke Ürün", 100.0, "Evet", "", 1, 0.0, 0)
    rows = database.urunleri_getir()
    assert len(rows) > 0
    uid = rows[0][0]
    database.urun_guncelle(uid, "Test2", "Smoke2", 200.0, "Hayır", "", 2, 10.0, 1)
    database.urun_sil(uid)

def test_db_monthly_spending():
    from datetime import date
    today = date.today()
    result = database.get_monthly_spending(today.year, today.month)
    assert isinstance(result, (int, float))

def test_db_takip_crud():
    database.takip_ekle("https://example.com", "Test Ürün", "Trendyol", 50.0, 60.0)
    items = database.takip_listele(sadece_aktif=True)
    assert len(items) > 0
    tid = items[0][0]
    database.takip_guncelle(tid, 45.0, "2025-01-01 12:00")
    database.takip_duraklat(tid, False)
    database.takip_sil(tid)

test("set_db_path", test_db_set_path)
test("get_connection", test_db_get_connection)
test("init_db + tablolar", test_db_init)
test("CRUD (ekle/güncelle/sil)", test_db_crud)
test("get_monthly_spending", test_db_monthly_spending)
test("fiyat_takip CRUD", test_db_takip_crud)

# Temizlik
try:
    os.remove("test_smoke.db")
except OSError:
    pass


# ============================================================
# 2. currency.py
# ============================================================
print("\n[2] currency.py")

def test_currency_import():
    from currency import get_exchange_rates
    rates = get_exchange_rates()
    assert isinstance(rates, dict)
    assert "USD" in rates or "usd" in rates.get("rates", rates)

test("get_exchange_rates", test_currency_import)


# ============================================================
# 3. profile_manager.py
# ============================================================
print("\n[3] profile_manager.py")

import profile_manager

# Geçici dizin kullan
_orig_base = profile_manager.get_base_dir

def test_profile_create_list_delete():
    tmpdir = tempfile.mkdtemp()
    try:
        profile_manager.get_base_dir = lambda: tmpdir
        profile_manager.create_profile("test_profil", "9999")
        profiles = profile_manager.list_profiles()
        names = [p["name"] for p in profiles]
        assert "test_profil" in names

        # İkinci profil oluştur ki silme çalışsın
        profile_manager.create_profile("test_profil2", "1234")
        profile_manager.delete_profile("test_profil")
        profiles2 = profile_manager.list_profiles()
        names2 = [p["name"] for p in profiles2]
        assert "test_profil" not in names2
    finally:
        profile_manager.get_base_dir = _orig_base
        shutil.rmtree(tmpdir, ignore_errors=True)

def test_profile_settings():
    tmpdir = tempfile.mkdtemp()
    try:
        profile_manager.get_base_dir = lambda: tmpdir
        profile_manager.create_profile("ayar_test", "1234")
        settings = profile_manager.load_profile_settings("ayar_test")
        assert "pin_hash" in settings
        assert "notifications" in settings
        settings["monthly_budget"] = 5000
        profile_manager.save_profile_settings("ayar_test", settings)
        reloaded = profile_manager.load_profile_settings("ayar_test")
        assert reloaded["monthly_budget"] == 5000
    finally:
        profile_manager.get_base_dir = _orig_base
        shutil.rmtree(tmpdir, ignore_errors=True)

test("create/list/delete profil", test_profile_create_list_delete)
test("load/save settings", test_profile_settings)


# ============================================================
# 4. backup_manager.py
# ============================================================
print("\n[4] backup_manager.py")

import backup_manager

def test_backup_create_list():
    tmpdir = tempfile.mkdtemp()
    try:
        profile_manager.get_base_dir = lambda: tmpdir
        profile_manager.create_profile("backup_test", "1234")
        db_path = profile_manager.get_profile_db_path("backup_test")
        # Boş DB oluştur
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE test (id INTEGER)")
        conn.commit()
        conn.close()

        bm = backup_manager.BackupManager("backup_test", {"max_backups": 3})
        path = bm.create_backup()
        assert path is not None
        assert os.path.exists(path)

        backups = bm.list_backups()
        assert len(backups) == 1

        last = bm.get_last_backup_time()
        assert last != "Henüz yedeklenmedi"
    finally:
        profile_manager.get_base_dir = _orig_base
        shutil.rmtree(tmpdir, ignore_errors=True)

test("create/list backup", test_backup_create_list)


# ============================================================
# 5. notification_manager.py
# ============================================================
print("\n[5] notification_manager.py")

import notification_manager

def test_notification_manager_init():
    nm = notification_manager.NotificationManager("test", {"taksit_reminder": True}, database)
    assert nm.profile_name == "test"
    assert nm.check_interval == 3600

test("NotificationManager init", test_notification_manager_init)


# ============================================================
# 6. price_tracker.py
# ============================================================
print("\n[6] price_tracker.py")

import price_tracker

def test_price_tracker_init():
    pt = price_tracker.PriceTracker(check_interval_hours=1)
    assert pt.check_interval == 3600
    assert pt._running is False

test("PriceTracker init", test_price_tracker_init)


# ============================================================
# 7. web_scraper.py
# ============================================================
print("\n[7] web_scraper.py")

def test_scraper_import():
    from web_scraper import urun_ara, fiyat_getir
    assert callable(urun_ara)
    assert callable(fiyat_getir)

test("import urun_ara/fiyat_getir", test_scraper_import)


# ============================================================
# 8. installer.py
# ============================================================
print("\n[8] installer.py")

def test_installer_import():
    import installer
    assert hasattr(installer, "KurulumSihirbazi")

test("import KurulumSihirbazi", test_installer_import)


# ============================================================
# Özet
# ============================================================
print(f"\n{'='*40}")
print(f"  Toplam: {passed + failed} | Başarılı: {passed} | Başarısız: {failed}")
print(f"{'='*40}")
sys.exit(0 if failed == 0 else 1)
