import sqlite3
import os

DB_PATH = "data/urunler.db"
CSV_PATH = "data/gercek_veriler.csv"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Kategori, UrunAdi, Fiyat, Durum, Link
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
    
    # Eskiden eksik sütunları olan kurulumlara yama yap
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
        
    conn.commit()
    conn.close()
    
def migrate_from_csv():
    # If DB is empty, read CSV and insert
    if not os.path.exists(CSV_PATH):
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM urunler")
    count = cursor.fetchone()[0]
    
    if count == 0:
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            for satir in f:
                satir = satir.strip()
                if not satir: continue
                parcalar = satir.split(",")
                if len(parcalar) == 4:
                    kategori, urun_adi, fiyat_str, durum = parcalar
                    try:
                        fiyat = float(fiyat_str.replace(',', '.'))
                    except ValueError:
                        fiyat = 0.0
                    
                    cursor.execute('''
                        INSERT INTO urunler (kategori, urun_adi, fiyat, durum, link)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (kategori, urun_adi, fiyat, durum, ""))
        conn.commit()
    conn.close()

def urun_ekle(kategori, urun_adi, fiyat, durum, link="", taksit_sayisi=1, vade_farki=0.0, odenen_taksit=0):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO urunler (kategori, urun_adi, fiyat, durum, link, taksit_sayisi, vade_farki, odenen_taksit)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (kategori, urun_adi, float(fiyat), durum, link, int(taksit_sayisi), float(vade_farki), int(odenen_taksit)))
    conn.commit()
    conn.close()

def urunleri_getir(kategori_filtre=None, arama_filtre=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = "SELECT id, kategori, urun_adi, fiyat, durum, link, taksit_sayisi, vade_farki, odenen_taksit FROM urunler WHERE 1=1"
    params = []
    
    if kategori_filtre and kategori_filtre != "Tümü":
        query += " AND kategori = ?"
        params.append(kategori_filtre)
        
    if arama_filtre:
        query += " AND urun_adi LIKE ?"
        params.append(f"%{arama_filtre}%")
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

def urun_sil(urun_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM urunler WHERE id=?", (urun_id,))
    conn.commit()
    conn.close()

def urun_guncelle(urun_id, kategori, urun_adi, fiyat, durum, link="", taksit_sayisi=1, vade_farki=0.0, odenen_taksit=0):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE urunler 
        SET kategori=?, urun_adi=?, fiyat=?, durum=?, link=?, taksit_sayisi=?, vade_farki=?, odenen_taksit=?
        WHERE id=?
    ''', (kategori, urun_adi, float(fiyat), durum, link, int(taksit_sayisi), float(vade_farki), int(odenen_taksit), urun_id))
    conn.commit()
    conn.close()

# Start DB and Migrate automatically
init_db()
migrate_from_csv()
