import sqlite3
import os
import datetime
from contextlib import contextmanager

DB_PATH = None


def set_db_path(path):
    """Profil bazlı dinamik DB yolu ayarla."""
    global DB_PATH
    DB_PATH = path


def get_connection():
    """Merkezi bağlantı fabrikası. Tüm fonksiyonlar bunu kullanır."""
    if DB_PATH is None:
        raise RuntimeError("Veritabanı yolu ayarlanmadı. Önce set_db_path() çağırın.")
    return sqlite3.connect(DB_PATH)


@contextmanager
def get_db():
    """Context manager: bağlantıyı otomatik kapatır."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    with get_connection() as conn:
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
                odenen_taksit INTEGER DEFAULT 0,
                ekleme_tarihi TEXT DEFAULT ''
            )
        ''')
        cursor.execute("PRAGMA table_info(urunler)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'link' not in columns:
            cursor.execute("ALTER TABLE urunler ADD COLUMN link TEXT DEFAULT ''")
        if 'taksit_sayisi' not in columns:
            cursor.execute("ALTER TABLE urunler ADD COLUMN taksit_sayisi INTEGER DEFAULT 1")
        if 'vade_farki' not in columns:
            cursor.execute("ALTER TABLE urunler ADD COLUMN vade_farki REAL DEFAULT 0.0")
        if 'odenen_taksit' not in columns:
            cursor.execute("ALTER TABLE urunler ADD COLUMN odenen_taksit INTEGER DEFAULT 0")
        if 'ekleme_tarihi' not in columns:
            cursor.execute("ALTER TABLE urunler ADD COLUMN ekleme_tarihi TEXT DEFAULT ''")

        # Kategoriler tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kategoriler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT NOT NULL UNIQUE
            )
        ''')

        # Fiyat takip tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fiyat_takip (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                urun_adi TEXT NOT NULL,
                platform TEXT NOT NULL,
                hedef_fiyat REAL NOT NULL,
                mevcut_fiyat REAL DEFAULT 0.0,
                son_kontrol TEXT DEFAULT '',
                aktif INTEGER DEFAULT 1
            )
        ''')
        conn.commit()


def urun_ekle(kategori, urun_adi, fiyat, durum, link="", taksit_sayisi=1, vade_farki=0.0, odenen_taksit=0, ekleme_tarihi=""):
    if not ekleme_tarihi:
        ekleme_tarihi = datetime.date.today().isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO urunler (kategori, urun_adi, fiyat, durum, link, taksit_sayisi, vade_farki, odenen_taksit, ekleme_tarihi)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (kategori, urun_adi, float(fiyat), durum, link, int(taksit_sayisi), float(vade_farki), int(odenen_taksit), ekleme_tarihi))
        conn.commit()


def _escape_like(pattern):
    """LIKE pattern özel karakterlerini escape et."""
    return pattern.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')


def urunleri_getir(kategori_filtre=None, arama_filtre=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT id, kategori, urun_adi, fiyat, durum, link, taksit_sayisi, vade_farki, odenen_taksit FROM urunler WHERE 1=1"
        params = []
        if kategori_filtre and kategori_filtre != "Tümü":
            query += " AND kategori = ?"
            params.append(kategori_filtre)
        if arama_filtre:
            query += " AND urun_adi LIKE ? ESCAPE '\\'"
            params.append(f"%{_escape_like(arama_filtre)}%")
        cursor.execute(query, params)
        return cursor.fetchall()


def urun_sil(urun_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM urunler WHERE id=?", (urun_id,))
        conn.commit()


def urun_guncelle(urun_id, kategori, urun_adi, fiyat, durum, link="", taksit_sayisi=1, vade_farki=0.0, odenen_taksit=0):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE urunler
            SET kategori=?, urun_adi=?, fiyat=?, durum=?, link=?, taksit_sayisi=?, vade_farki=?, odenen_taksit=?
            WHERE id=?
        ''', (kategori, urun_adi, float(fiyat), durum, link, int(taksit_sayisi), float(vade_farki), int(odenen_taksit), urun_id))
        conn.commit()


def get_monthly_spending(year, month):
    """Belirli ay için toplam harcamayı döndür (durum=Evet olanlar)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        prefix = f"{year:04d}-{month:02d}"
        cursor.execute('''
            SELECT COALESCE(SUM(fiyat + vade_farki), 0) FROM urunler
            WHERE UPPER(TRIM(durum)) IN ('E', 'EVET', 'ALINDI')
            AND ekleme_tarihi LIKE ?
        ''', (prefix + '%',))
        return cursor.fetchone()[0]


# ─── FİYAT TAKİP CRUD ────────────────────────────────────────────────

def takip_ekle(url, urun_adi, platform, hedef_fiyat, mevcut_fiyat=0.0):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO fiyat_takip (url, urun_adi, platform, hedef_fiyat, mevcut_fiyat, son_kontrol, aktif)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        ''', (url, urun_adi, platform, float(hedef_fiyat), float(mevcut_fiyat), ""))
        conn.commit()


def takip_listele(sadece_aktif=True):
    with get_connection() as conn:
        cursor = conn.cursor()
        if sadece_aktif:
            cursor.execute("SELECT id, url, urun_adi, platform, hedef_fiyat, mevcut_fiyat, son_kontrol, aktif FROM fiyat_takip WHERE aktif=1")
        else:
            cursor.execute("SELECT id, url, urun_adi, platform, hedef_fiyat, mevcut_fiyat, son_kontrol, aktif FROM fiyat_takip")
        return cursor.fetchall()


def takip_guncelle(takip_id, mevcut_fiyat, son_kontrol):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE fiyat_takip SET mevcut_fiyat=?, son_kontrol=? WHERE id=?",
                       (float(mevcut_fiyat), son_kontrol, takip_id))
        conn.commit()


def takip_sil(takip_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM fiyat_takip WHERE id=?", (takip_id,))
        conn.commit()


def takip_duraklat(takip_id, aktif):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE fiyat_takip SET aktif=? WHERE id=?", (1 if aktif else 0, takip_id))
        conn.commit()


# ─── KATEGORİ CRUD ──────────────────────────────────────────────────

def kategori_ekle(ad):
    """Yeni kategori ekle (zaten varsa yoksay)."""
    ad = ad.strip()
    if not ad:
        return
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO kategoriler (ad) VALUES (?)", (ad,))
        conn.commit()


def kategorileri_getir():
    """Tüm kategorileri getir (kategoriler tablosu + mevcut ürünlerden UNION)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ad FROM kategoriler
            UNION
            SELECT DISTINCT kategori FROM urunler
            ORDER BY 1
        """)
        result = [row[0] for row in cursor.fetchall() if row[0]]
        return result if result else ["Diğer"]


def kategori_sil(ad):
    """Kategoriyi sil."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM kategoriler WHERE ad=?", (ad,))
        conn.commit()


def kategori_guncelle(eski_ad, yeni_ad):
    """Kategori adını güncelle. Hem kategoriler tablosunda hem ürünlerde."""
    yeni_ad = yeni_ad.strip()
    if not yeni_ad:
        return
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE kategoriler SET ad=? WHERE ad=?", (yeni_ad, eski_ad))
        cursor.execute("UPDATE urunler SET kategori=? WHERE kategori=?", (yeni_ad, eski_ad))
        conn.commit()


def kategori_urun_sayisi(ad):
    """Belirtilen kategorideki ürün sayısını döndür."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM urunler WHERE kategori=?", (ad,))
        return cursor.fetchone()[0]
