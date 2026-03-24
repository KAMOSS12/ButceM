import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import database

try:
    import google.generativeai as genai
except ImportError:
    genai = None

load_dotenv()

def urun_ekle():
    print("\n--- YENİ PARÇA EKLE ---")
    kategori = input("Kategori: ")
    urun_adi = input("Ürün Adı: ")
    fiyat = input("Fiyat (TL): ")
    alindi_mi = input("Alındı mı? (Evet/Hayır): ")
    link = input("Ürün İnternet Linki (İsteğe Bağlı, Boş Geçilebilir): ")

    try:
        fiyat = float(fiyat.replace(',', '.'))
    except ValueError:
        print("[!] Geçersiz fiyat formatı.")
        return

    database.urun_ekle(kategori, urun_adi, fiyat, alindi_mi, link)
    print(f"[+] '{urun_adi}' veritabanına başarıyla eklendi!")

def urunleri_listele():
    rows = database.urunleri_getir()
    if not rows:
        print("\n[!] Henüz hiç kayıt bulunmuyor. Lütfen önce ürün ekleyin.")
        return

    toplam_harcanan = 0.0
    bekleyen_harcama = 0.0
    toplam_urun = 0
    alinan_urun = 0

    print("\n" + "="*70)
    print(f"{'KATEGORİ':<15} | {'ÜRÜN ADI':<20} | {'FİYAT':<10} | {'DURUM'}")
    print("-" * 70)

    for row in rows:
        _, kategori, urun_adi, fiyat, durum, link = row
        fiyat_metin = f"{fiyat:.2f} TL"
        
        durum_upper = durum.upper().strip()
        if durum_upper in ["E", "EVET"]:
            durum_ikon = "[+] Alındı"
            alinan_urun += 1
            toplam_harcanan += fiyat
        else:
            durum_ikon = "[-] Bekliyor"
            bekleyen_harcama += fiyat
            
        toplam_urun += 1
        print(f"{kategori:<15} | {urun_adi:<20} | {fiyat_metin:<10} | {durum_ikon}")

    print("=" * 70)
    
    # Hesaplama Motoru: Özet
    print("\n[i] --- FİNANSAL ÖZET ---")
    if toplam_urun > 0:
        yuzde = int((alinan_urun / toplam_urun) * 100)
        print(f"Toplam Ürün Sayısı : {toplam_urun}")
        print(f"Tamamlanma Oranı   : %{yuzde} ({alinan_urun}/{toplam_urun} ürün)")
        print(f"Toplam Harcanan    : {toplam_harcanan:.2f} TL")
        print(f"Bekleyen Maliyet   : {bekleyen_harcama:.2f} TL")
        print(f"Tahmini Top. Bütçe : {(toplam_harcanan + bekleyen_harcama):.2f} TL")
    print("------------------------\n")

def kategori_analizi():
    con = sqlite3.connect("data/urunler.db")
    df = pd.read_sql("SELECT kategori, urun_adi, fiyat, durum FROM urunler", con)
    con.close()
    
    if df.empty:
        print("\n[!] Henüz hiç kayıt bulunmuyor. Lütfen önce ürün ekleyin.")
        return
        
    try:
        ozet = df.groupby('kategori')['fiyat'].sum()
        
        print("\n[i] --- KATEGORİ BAZLI HARCAMA ÖZETİ ---")
        for kat, toplam in ozet.items():
            print(f"{kat:<15} : {toplam:.2f} TL")
        print("----------------------------------------\n")
        
        if ozet.sum() > 0:
            plt.figure(figsize=(8, 6))
            plt.pie(ozet, labels=ozet.index, autopct='%1.1f%%', startangle=140)
            plt.title('Parça/Kategori Bazlı Maliyet Dağılımı')
            plt.axis('equal') 
            print(">>> Grafik ekranda açıldı. Lütfen işlemlere devam etmek için açılan pencereyi kapatın.")
            plt.show()
        else:
            print("[!] Tüm harcamalar 0 TL olduğu için grafik çizilemedi.")
            
    except ImportError:
        print("\n[!] Pandas veya Matplotlib yüklü değil! 'pip install pandas matplotlib' komutunu çalıştırın.")
    except Exception as e:
        print(f"\n[!] Gelişmiş analiz sırasında hata oluştu: {e}")

def ai_tahmin_asistani():
    con = sqlite3.connect("data/urunler.db")
    df = pd.read_sql("SELECT kategori, urun_adi, fiyat, durum FROM urunler", con)
    con.close()
    
    if df.empty:
        print("\n[!] Henüz hiç kayıt bulunmuyor.")
        return
        
    print("\n" + "="*50)
    print("🤖 GEMINI AI BÜTÇE ASİSTANI")
    print("="*50)
    
    if genai is None:
        print("\n[!] 'google-generativeai' yüklü değil. Kurulum tamamlanınca tekrar deneyin.")
        return
        
    api_key = os.getenv("GEMINI_API_KEY")
        
    if not api_key or api_key == "BURAYA_API_ANAHTARINIZI_YAPISTIRIN" or " " in api_key:
        print(f"\n[!] API Anahtarı Bulunamadı veya Geçersiz!")
        print(f"> Lütfen proje dizinindeki '.env' dosyasını açın.")
        print("> İçine GEMINI_API_KEY=api_anahtari seklinde yapıştırıp kaydedin.")
        return
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        ozet = df.groupby('kategori')['fiyat'].sum()
        
        durumlar = df['durum'].str.upper().str.strip()
        harcanan = df[durumlar.str.startswith('E|A')]['fiyat'].sum()
        bekleyen = df[~durumlar.str.startswith('E|A')]['fiyat'].sum()
        
        masked_str = ""
        for idx, row in df.iterrows():
            masked_str += f"- Ürün {idx+1} (Kategori: {row['kategori']}): {row['fiyat']} TL\n"
        
        prompt = f"""
        Ben bir harcama/ürün takip ve bütçe planlama sistemi kullanıcısıyım. 
        Satın aldığım ve almayı planladığım çeşitli ihtiyaçlarımı takip ediyorum.
        İşte güncel maliyet tablom:
        - Şimdiye kadar bitti/alındı denen toplam harcama: {harcanan} TL
        - Alınmayı bekleyen planlanmış parçaların toplamı: {bekleyen} TL
        
        Gizlilik Gereği Maskelenmiş Ürün Listesi:
        {masked_str}
        """
        
        print("\n[⏳] Asistan verilerinizi analiz ederken lütfen bekleyin...\n")
        response = model.generate_content(prompt)
        
        print("💡 AI DEĞERLENDİRMESİ:")
        print("-" * 50)
        print(response.text.strip())
        print("-" * 50 + "\n")
        
    except Exception as e:
        print(f"\n[!] Yapay zeka modülü çalışırken hata oluştu. API anahtarınız yanlıs olabilir. Hata Detayı: {e}")

def ana_menu():
    while True:
        print("\n--- ÜRÜN TAKİP SİSTEMİ ---")
        print("1. Yeni Parça/Ürün Ekle")
        print("2. Listeyi ve Özeti Gör")
        print("3. Kategori Analizi ve Maliyet Grafiği")
        print("4. Yapay Zeka Bütçe Asistanı (Gemini)")
        print("5. Çıkış")
        
        secim = input("Lütfen bir işlem seçin (1/2/3/4/5): ")
        
        if secim == '1':
            urun_ekle()
        elif secim == '2':
            urunleri_listele()
        elif secim == '3':
            kategori_analizi()
        elif secim == '4':
            ai_tahmin_asistani()
        elif secim == '5':
            print(">>> Programdan çıkılıyor. Görüşmek üzere!")
            break 
        else:
            print(">>> Geçersiz seçim. Lütfen sadece 1, 2, 3, 4 veya 5 yazın.")

if __name__ == "__main__":
    import os, hashlib
    from dotenv import load_dotenv
    load_dotenv()
    
    p = input(">>> Sisteme Giriş İçin PIN Kodunuzu Yazın: ").strip()
    correct_pin = os.getenv("APP_PIN", "1234")
    
    if len(correct_pin) == 64:
        if hashlib.sha256(p.encode("utf-8")).hexdigest() != correct_pin:
            print(">>> Hatalı PIN! Çıkış yapılıyor...")
            exit()
    else:
        if p != correct_pin:
            print(">>> Hatalı PIN! Çıkış yapılıyor...")
            exit()
            
    database.init_db()
    database.migrate_from_csv()
    ana_menu()