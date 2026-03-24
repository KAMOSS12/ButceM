import os
import customtkinter as ctk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import database
import sqlite3
import currency
import threading
import webbrowser
import hashlib
import time
import shutil
from tkinter import filedialog
from dotenv import set_key

try:
    import google.generativeai as genai
except ImportError:
    genai = None

load_dotenv()

# TEMA AYARLARI
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Ürün Takip Sistemi - Masaüstü Asistanı")
        self.geometry("1000x700")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # --- SOL MENÜ (SIDEBAR) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="ÜRÜN TAKİP", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))
        
        self.btn_ekle = ctk.CTkButton(self.sidebar_frame, text="➕ 1. Parça Ekle", command=self.show_ekle_frame)
        self.btn_ekle.grid(row=1, column=0, padx=20, pady=10)
        
        self.btn_liste = ctk.CTkButton(self.sidebar_frame, text="📃 2. Liste & CRUD", command=self.show_liste_frame)
        self.btn_liste.grid(row=2, column=0, padx=20, pady=10)
        
        self.btn_grafik = ctk.CTkButton(self.sidebar_frame, text="📊 3. Dashboard", fg_color="#00695C", hover_color="#004D40", command=self.show_dashboard_frame)
        self.btn_grafik.grid(row=3, column=0, padx=20, pady=10)
        
        self.btn_ai = ctk.CTkButton(self.sidebar_frame, text="🤖 4. Yapay Zeka", fg_color="#6A1B9A", hover_color="#4A148C", command=self.show_ai_frame)
        self.btn_ai.grid(row=4, column=0, padx=20, pady=10)

        self.btn_web = ctk.CTkButton(self.sidebar_frame, text="🌐 5. Web'den Bul", fg_color="#FBC02D", text_color="black", hover_color="#F57F17", command=self.show_web_frame)
        self.btn_web.grid(row=5, column=0, padx=20, pady=10)

        self.btn_ayarlar = ctk.CTkButton(self.sidebar_frame, text="⚙️ 6. Sistem Ayarları", fg_color="#37474F", hover_color="#263238", command=self.show_ayarlar_frame)
        self.btn_ayarlar.grid(row=6, column=0, padx=20, pady=10)

        self.lbl_kur = ctk.CTkLabel(self.sidebar_frame, text="Kurlar Yükleniyor...", text_color="#A5D6A7", font=ctk.CTkFont(size=12))
        self.lbl_kur.grid(row=7, column=0, pady=20)

        self.usd_rate = 0.0

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        database.init_db()
        database.migrate_from_csv()

        self.withdraw() 
        self.show_login_screen()

    def show_login_screen(self):
        login = ctk.CTkToplevel(self)
        login.title("Sistem Girişi")
        login.geometry("300x200")
        login.resizable(False, False)
        
        login.protocol("WM_DELETE_WINDOW", self.destroy)

        ctk.CTkLabel(login, text="Uygulama PIN Kodu:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(25, 10))
        self.pin_entry = ctk.CTkEntry(login, show="*", width=150, justify="center")
        self.pin_entry.pack(pady=5)
        self.pin_entry.bind('<Return>', lambda e: self.check_pin(login))

        ctk.CTkButton(login, text="GİRİŞ YAP", command=lambda: self.check_pin(login)).pack(pady=10)
        
        self.login_lbl = ctk.CTkLabel(login, text="Varsayılan PIN: 1234", text_color="gray", font=ctk.CTkFont(size=11))
        self.login_lbl.pack()

    def check_pin(self, login_win):
        p = self.pin_entry.get()
        correct_pin = os.getenv("APP_PIN", "1234")
        
        if len(correct_pin) != 64:
            new_hash = hashlib.sha256(correct_pin.encode("utf-8")).hexdigest()
            os.environ["APP_PIN"] = new_hash
            env_file = ".env"
            if not os.path.exists(env_file):
                open(env_file, 'a').close()
            set_key(env_file, "APP_PIN", new_hash)
            correct_pin = new_hash
            
        input_hash = hashlib.sha256(p.encode("utf-8")).hexdigest()
        
        if input_hash == correct_pin:
            login_win.destroy()
            self.deiconify() 
            self.load_currency()
            self.show_liste_frame()
            self.start_autolock()
        else:
            self.login_lbl.configure(text="Hatalı PIN! Lütfen tekrar deneyin.", text_color="#FF5252")

    def start_autolock(self):
        self.last_activity = time.time()
        self.bind_all("<Motion>", self.reset_timer)
        self.bind_all("<Key>", self.reset_timer)
        self.is_locked = False
        self.check_autolock()

    def reset_timer(self, event=None):
        self.last_activity = time.time()

    def check_autolock(self):
        if not hasattr(self, 'is_locked') or self.is_locked:
            return
        if time.time() - self.last_activity > 300: # 5 Dakika Inaktivite
            self.is_locked = True
            self.withdraw()
            self.show_login_screen()
            return
        self.after(5000, self.check_autolock)

    def load_currency(self):
        def fetch():
            rates = currency.get_exchange_rates()
            u = rates.get("USD", 0)
            e = rates.get("EUR", 0)
            self.usd_rate = u
            if u > 0 and e > 0:
                txt = f"💵 USD: {u:.2f} ₺\n💶 EUR: {e:.2f} ₺"
            else:
                txt = "Kurlar Çekilemedi"
            self.lbl_kur.after(0, lambda: self.lbl_kur.configure(text=txt))
            self.lbl_kur.after(0, self.update_ozet_usd)
        threading.Thread(target=fetch, daemon=True).start()

    def update_ozet_usd(self):
        try:
            self.load_treeview_data()
        except:
            pass

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_ekle_frame(self):
        self.clear_main_frame()
        self.main_frame.grid_rowconfigure(1, weight=0)
        lbl_baslik = ctk.CTkLabel(self.main_frame, text="YENİ PARÇA VE BÜTÇE EKLE", font=ctk.CTkFont(size=24, weight="bold"))
        lbl_baslik.grid(row=0, column=0, columnspan=2, pady=30)

        lbl_kat = ctk.CTkLabel(self.main_frame, text="Kategori:")
        lbl_kat.grid(row=1, column=0, padx=20, pady=15, sticky="e")
        
        try:
            mevcut_kategoriler = list(set([r[1] for r in database.urunleri_getir()]))
        except Exception:
            mevcut_kategoriler = []
            
        if not mevcut_kategoriler:
            mevcut_kategoriler = ["Elektronik", "Giyim", "Market", "Ev Aletleri", "Hobi"]
            
        self.entry_kat = ctk.CTkComboBox(self.main_frame, width=250, values=mevcut_kategoriler)
        self.entry_kat.set("")
        self.entry_kat.grid(row=1, column=1, padx=20, pady=15, sticky="w")

        lbl_ad = ctk.CTkLabel(self.main_frame, text="Ürün Adı:")
        lbl_ad.grid(row=2, column=0, padx=20, pady=15, sticky="e")
        self.entry_ad = ctk.CTkEntry(self.main_frame, width=250)
        self.entry_ad.grid(row=2, column=1, padx=20, pady=15, sticky="w")

        lbl_fiyat = ctk.CTkLabel(self.main_frame, text="Fiyat (TL):")
        lbl_fiyat.grid(row=3, column=0, padx=20, pady=15, sticky="e")
        self.entry_fiyat = ctk.CTkEntry(self.main_frame, width=250)
        self.entry_fiyat.grid(row=3, column=1, padx=20, pady=15, sticky="w")

        lbl_durum = ctk.CTkLabel(self.main_frame, text="Alındı Mı?:")
        lbl_durum.grid(row=4, column=0, padx=20, pady=15, sticky="e")
        self.option_durum = ctk.CTkOptionMenu(self.main_frame, values=["Evet", "Hayır"], fg_color="#00695C", button_color="#004D40")
        self.option_durum.grid(row=4, column=1, padx=20, pady=15, sticky="w")

        lbl_link = ctk.CTkLabel(self.main_frame, text="Ürün Linki (URL):")
        lbl_link.grid(row=5, column=0, padx=20, pady=15, sticky="e")
        self.entry_link = ctk.CTkEntry(self.main_frame, width=250)
        self.entry_link.grid(row=5, column=1, padx=20, pady=15, sticky="w")

        lbl_taksit = ctk.CTkLabel(self.main_frame, text="Taksit Sayısı:")
        lbl_taksit.grid(row=6, column=0, padx=20, pady=15, sticky="e")
        self.entry_taksit = ctk.CTkEntry(self.main_frame, width=250, placeholder_text="Örn: 1 (Peşin)")
        self.entry_taksit.insert(0, "1")
        self.entry_taksit.grid(row=6, column=1, padx=20, pady=15, sticky="w")

        lbl_vade = ctk.CTkLabel(self.main_frame, text="Vade Farkı (TL):")
        lbl_vade.grid(row=7, column=0, padx=20, pady=15, sticky="e")
        self.entry_vade = ctk.CTkEntry(self.main_frame, width=250, placeholder_text="Örn: 0")
        self.entry_vade.insert(0, "0.0")
        self.entry_vade.grid(row=7, column=1, padx=20, pady=15, sticky="w")

        btn_kaydet = ctk.CTkButton(self.main_frame, text="KAYDET", command=self.kaydet_veriler, fg_color="#1B5E20", hover_color="#003300")
        btn_kaydet.grid(row=8, column=0, columnspan=2, pady=30)
        
        self.lbl_mesaj = ctk.CTkLabel(self.main_frame, text="", text_color="yellow")
        self.lbl_mesaj.grid(row=9, column=0, columnspan=2)

    def kaydet_veriler(self):
        kategori = self.entry_kat.get().strip()
        ad = self.entry_ad.get().strip()
        fiyat = self.entry_fiyat.get().strip()
        durum = self.option_durum.get().strip()
        link = self.entry_link.get().strip()
        taksit_str = self.entry_taksit.get().strip()
        vade_str = self.entry_vade.get().strip()

        if not kategori or not ad or not fiyat:
            self.lbl_mesaj.configure(text="Uyarı: Lütfen tüm alanları doldurun!", text_color="#FF5252")
            return
            
        try:
            fiyat_float = float(fiyat.replace(',', '.'))
            taksit = int(taksit_str) if taksit_str else 1
            vade = float(vade_str.replace(',', '.')) if vade_str else 0.0
        except ValueError:
            self.lbl_mesaj.configure(text="Hata: Fiyat, Taksit ve Vade alanlarına sadece rakam girmelisiniz!", text_color="#FF5252")
            return

        database.urun_ekle(kategori, ad, fiyat_float, durum, link, taksit_sayisi=taksit, vade_farki=vade)
        self.lbl_mesaj.configure(text=f"✅ '{ad}' veritabanına eklendi!", text_color="#64DD17")
        self.entry_kat.set("")
        self.entry_ad.delete(0, 'end')
        self.entry_fiyat.delete(0, 'end')
        self.entry_link.delete(0, 'end')
        self.entry_taksit.delete(0, 'end')
        self.entry_taksit.insert(0, "1")
        self.entry_vade.delete(0, 'end')
        self.entry_vade.insert(0, "0.0")

    def show_liste_frame(self):
        self.clear_main_frame()
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        lbl_baslik = ctk.CTkLabel(self.main_frame, text="ENVANTER VE FİNANSAL ÖZET", font=ctk.CTkFont(size=24, weight="bold"))
        lbl_baslik.grid(row=0, column=0, pady=10)

        # Filtreleme / Arama Çubuğu
        filtre_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        filtre_frame.grid(row=1, column=0, pady=10, sticky="ew")
        
        lbl_ara = ctk.CTkLabel(filtre_frame, text="Ürün Ara:")
        lbl_ara.pack(side="left", padx=5)
        self.entry_ara = ctk.CTkEntry(filtre_frame, width=150)
        self.entry_ara.pack(side="left", padx=5)
        
        lbl_filtre_kat = ctk.CTkLabel(filtre_frame, text="Kategori Filtre:")
        lbl_filtre_kat.pack(side="left", padx=(20, 5))
        
        # Kategorileri çek
        rows = database.urunleri_getir()
        kategoriler = list(set([r[1] for r in rows]))
        kategoriler.insert(0, "Tümü")
        
        self.combo_kat = ctk.CTkOptionMenu(filtre_frame, values=kategoriler)
        self.combo_kat.pack(side="left", padx=5)
        self.combo_kat.set("Tümü")
        
        btn_ara = ctk.CTkButton(filtre_frame, text="Filtrele", width=80, command=self.load_treeview_data)
        btn_ara.pack(side="left", padx=10)

        # Tablo Alanı (Treeview)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2a2d2e", foreground="white", rowheight=25, fieldbackground="#2a2d2e", borderwidth=0)
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")
        style.map("Treeview.Heading", background=[('active', '#3484F0')])

        self.tree = ttk.Treeview(self.main_frame, columns=("ID", "Kategori", "Ürün Adı", "Maliyet", "Durum", "Taksit"), show="headings", height=15)
        self.tree.tag_configure("oddrow", background="#2a2d2e")
        self.tree.tag_configure("evenrow", background="#343638")
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Kategori", text="Kategori")
        self.tree.heading("Ürün Adı", text="Ürün Adı")
        self.tree.heading("Maliyet", text="Mal. (TL)  [Vade Dahil]")
        self.tree.heading("Durum", text="Durum")
        self.tree.heading("Taksit", text="Taksit (Ö/T)")
        
        self.tree.column("ID", width=30, anchor="center")
        self.tree.column("Kategori", width=120, anchor="center")
        self.tree.column("Ürün Adı", width=200, anchor="w")
        self.tree.column("Maliyet", width=150, anchor="e")
        self.tree.column("Durum", width=100, anchor="center")
        self.tree.column("Taksit", width=100, anchor="center")
        
        self.tree.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        
        # Çift Tıklama (Double-Click) Binding
        self.tree.bind("<Double-1>", lambda e: self.guncelle_popup())

        # CRUD Butonları
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.grid(row=3, column=0, pady=10)
        
        btn_guncelle = ctk.CTkButton(btn_frame, text="Seçilini Güncelle", fg_color="#F57C00", hover_color="#E65100", command=self.guncelle_popup)
        btn_guncelle.pack(side="left", padx=10)
        
        btn_sil = ctk.CTkButton(btn_frame, text="Seçilini Sil", fg_color="#D32F2F", hover_color="#C62828", command=self.sil_kayit)
        btn_sil.pack(side="left", padx=10)

        btn_link = ctk.CTkButton(btn_frame, text="📍 Linke Git", fg_color="#1976D2", hover_color="#1565C0", command=self.linke_git)
        btn_link.pack(side="left", padx=10)
        
        btn_export = ctk.CTkButton(btn_frame, text="📊 Excel'e Aktar", fg_color="#2E7D32", hover_color="#1B5E20", command=self.excel_disa_aktar)
        btn_export.pack(side="left", padx=10)

        btn_import = ctk.CTkButton(btn_frame, text="📥 İçe Aktar", fg_color="#5E35B1", hover_color="#4527A0", command=self.verileri_ice_aktar)
        btn_import.pack(side="left", padx=10)

        self.lbl_ozet = ctk.CTkLabel(self.main_frame, text="", font=ctk.CTkFont(size=14))
        self.lbl_ozet.grid(row=4, column=0, pady=10)
        
        self.load_treeview_data()

    def load_treeview_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        arama = self.entry_ara.get().strip()
        kategori_filtre = self.combo_kat.get()
        
        rows = database.urunleri_getir(kategori_filtre=kategori_filtre, arama_filtre=arama)
        
        toplam_h = 0.0
        bekleyen_h = 0.0
        alinan_u = 0
        toplam_u = len(rows)

        count = 0
        for row in rows:
            uid, kat, ad, fyt, drm, link, ts, vf, ot = row
            drm_upper = drm.upper()
            
            toplam_maliyet = fyt + vf
            if drm_upper in ["E", "EVET"]:
                ikon = "Alındı"
                alinan_u += 1
                toplam_h += toplam_maliyet
            else:
                ikon = "Bekliyor"
                bekleyen_h += fyt 
            
            taksit_str = f"{ot}/{ts}" if ts > 1 else "Peşin"
            tag = "evenrow" if count % 2 == 0 else "oddrow"
            
            self.tree.insert("", "end", values=(uid, kat, ad, f"{toplam_maliyet:.2f}", ikon, taksit_str, link, ts, vf, ot, fyt), tags=(tag,))
            count += 1
            
        all_rows = database.urunleri_getir()
        kategoriler = list(set([r[1] for r in all_rows]))
        kategoriler.insert(0, "Tümü")
        self.combo_kat.configure(values=kategoriler)

        ozet_metin = ""
        if toplam_u > 0:
            yuzde = int((alinan_u / toplam_u) * 100)
            usd_ek = ""
            if getattr(self, "usd_rate", 0) > 0:
                t_usd = (toplam_h + bekleyen_h) / self.usd_rate
                usd_ek = f" (~{t_usd:.0f} $)"
            
            ozet_metin = f"Ürün: {toplam_u} Adet | Tamamlanma: %{yuzde} | Harcanan: {toplam_h:.2f} ₺ | Bekleyen: {bekleyen_h:.2f} ₺ | Toplam Bütçe: {(toplam_h + bekleyen_h):.2f} ₺{usd_ek}"
        
        self.lbl_ozet.configure(text=ozet_metin)

    def sil_kayit(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen silmek için tablodan bir kayıt seçin.")
            return
            
        onay = messagebox.askyesno("Silme Onayı", "Seçili kaydı kalıcı olarak silmek istediğinize emin misiniz?")
        if onay:
            item = self.tree.item(selected[0])
            uid = item['values'][0]
            database.urun_sil(uid)
            self.load_treeview_data()

    def linke_git(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen linkine gitmek istediğiniz ürünü seçin.")
            return
            
        item = self.tree.item(selected[0])
        vals = item['values']
        link = str(vals[6]) if len(vals) > 6 else ""
        
        if link.startswith("http"):
            webbrowser.open(link)
        else:
            messagebox.showinfo("Bilgi", "Seçili ürün için geçerli (http ile başlayan) bir link bulunamadı.")

    def verileri_ice_aktar(self):
        dosya_yolu = filedialog.askopenfilename(filetypes=[("Excel ve CSV Dosyaları", "*.xlsx *.csv")], title="İçe Aktarılacak Dosyayı Seçin")
        if not dosya_yolu: return
        
        try:
            if dosya_yolu.endswith(".csv"):
                df = pd.read_csv(dosya_yolu)
            else:
                df = pd.read_excel(dosya_yolu)
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya okunurken hata oluştu:\n{e}")
            return
            
        # Temel kolon denetimleri
        gerekenler = ["Kategori", "Ürün Adı", "Fiyat"]
        if not set(gerekenler).issubset(df.columns):
            messagebox.showerror("Eksik Sütun", f"Verinizde şu temel sütunlar eksik: {', '.join(gerekenler)}\nLütfen örnek '.xlsx' yapısına uyun.")
            return
            
        # Önizleme ve Onay Popup
        p = ctk.CTkToplevel(self)
        p.title("Toplu İçe Aktarma - Onay Ekranı")
        p.geometry("800x500")
        p.transient(self)
        p.grab_set()
        
        ctk.CTkLabel(p, text=f"Önizleme: Toplam {len(df)} kayıt bulundu.", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Önizleme tablosu
        tree_frame = ctk.CTkFrame(p)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        preview_tree = ttk.Treeview(tree_frame, columns=("Kat", "Ad", "Fyt", "Durum"), show="headings", height=10)
        preview_tree.heading("Kat", text="Kategori")
        preview_tree.heading("Ad", text="Ürün Adı")
        preview_tree.heading("Fyt", text="Peşin Fiyat")
        preview_tree.heading("Durum", text="Durum")
        preview_tree.column("Kat", width=100)
        preview_tree.column("Ad", width=200)
        preview_tree.column("Fyt", width=80)
        preview_tree.column("Durum", width=80)
        preview_tree.pack(fill="both", expand=True)
        
        preview_data = []
        for _, row in df.iterrows():
            kat = str(row.get('Kategori', 'Diğer'))
            ad = str(row.get('Ürün Adı', 'İsimsiz'))
            try: fyt = float(str(row.get('Fiyat', 0)).replace(',', '.'))
            except: fyt = 0.0
            
            drm = str(row.get('Durum', 'Hayır'))
            link = str(row.get('Link', ''))
            ts = int(row.get('Taksit', 1)) if 'Taksit' in df.columns else 1
            vf = float(str(row.get('Vade_Farki', 0)).replace(',', '.')) if 'Vade_Farki' in df.columns else 0.0
            ot = int(row.get('Odenen_T', 0)) if 'Odenen_T' in df.columns else 0
            
            preview_tree.insert("", "end", values=(kat, ad, f"{fyt:.2f}", drm))
            preview_data.append((kat, ad, fyt, drm, link, ts, vf, ot))
            
        def onayla_kaydet():
            for dt in preview_data:
                database.urun_ekle(dt[0], dt[1], dt[2], dt[3], dt[4], taksit_sayisi=dt[5], vade_farki=dt[6], odenen_taksit=dt[7])
            p.destroy()
            self.load_treeview_data()
            messagebox.showinfo("Sistem Başarılı", f"{len(preview_data)} Adet ürün veritabanına başarıyla nakledildi!")
            
        ctk.CTkButton(p, text="Onayla ve Veritabanına Yaz", fg_color="#1B5E20", hover_color="#003300", command=onayla_kaydet).pack(pady=20)

    def excel_disa_aktar(self):
        # Ağaçtaki görünen verileri pandas ile export eder
        rows = []
        for child in self.tree.get_children():
            item = self.tree.item(child)
            rows.append(item['values'])
            
        if not rows:
            messagebox.showinfo("Bilgi", "Dışa aktarılacak veri bulunamadı.")
            return
            
        columns = ["ID", "Kategori", "Ürün Adı", "Maliyet", "Durum", "Taksit", "Link", "Taksit_S", "Vade_Farki", "Odenen_T", "Fiyat"]
        df = pd.DataFrame(rows, columns=columns)
        
        # Sadece görünür, gerekli kolonları alalım
        df_export = df[["ID", "Kategori", "Ürün Adı", "Fiyat", "Vade_Farki", "Maliyet", "Taksit", "Durum", "Link"]]
        
        kayit_yeri = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Dosyası", "*.xlsx"), ("CSV Dosyası", "*.csv")], initialfile="Finansal_Rapor.xlsx", title="Excel'e Nereye Aktaralım?")
        if kayit_yeri:
            try:
                if kayit_yeri.endswith(".csv"):
                    df_export.to_csv(kayit_yeri, index=False, encoding="utf-8-sig")
                else:
                    df_export.to_excel(kayit_yeri, index=False)
                messagebox.showinfo("Başarılı", f"Veriler başarıyla dışa aktarıldı:\n{kayit_yeri}")
            except Exception as e:
                messagebox.showerror("Hata", f"Dışa aktarılırken hata oluştu:\n{str(e)}")

    def guncelle_popup(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen güncellemek için tablodan bir kayıt seçin.")
            return

        item = self.tree.item(selected[0])
        vals = item['values']
        uid = vals[0]
        kat = vals[1]
        ad = vals[2]
        
        drm = vals[4]
        link = str(vals[6]) if len(vals) > 6 else ""
        ts = vals[7] if len(vals) > 7 else 1
        vf = vals[8] if len(vals) > 8 else 0.0
        ot = vals[9] if len(vals) > 9 else 0
        fyt = vals[10] if len(vals) > 10 else 0.0
        
        popup = ctk.CTkToplevel(self)
        popup.title("Kayıt Güncelle")
        popup.geometry("450x650")
        popup.transient(self)
        popup.grab_set()
        
        ctk.CTkLabel(popup, text="Kategori:").pack(pady=5)
        e_kat = ctk.CTkEntry(popup, width=200)
        e_kat.insert(0, kat)
        e_kat.pack(pady=5)

        ctk.CTkLabel(popup, text="Ürün Adı:").pack(pady=5)
        e_ad = ctk.CTkEntry(popup, width=200)
        e_ad.insert(0, ad)
        e_ad.pack(pady=5)

        ctk.CTkLabel(popup, text="Fiyat:").pack(pady=5)
        e_fyt = ctk.CTkEntry(popup, width=200)
        e_fyt.insert(0, str(fyt))
        e_fyt.pack(pady=5)

        ctk.CTkLabel(popup, text="Durum:").pack(pady=5)
        c_drm = ctk.CTkOptionMenu(popup, values=["Evet", "Hayır"], width=200)
        c_drm.set("Evet" if drm == "Alındı" else "Hayır")
        c_drm.pack(pady=5)

        ctk.CTkLabel(popup, text="Ürün Linki:").pack(pady=2)
        e_link = ctk.CTkEntry(popup, width=200)
        e_link.insert(0, str(link) if str(link) != "None" else "")
        e_link.pack(pady=2)

        ctk.CTkLabel(popup, text="Taksit Sayısı / Vade Farkı (TL) / Ödenen Taksit").pack(pady=(10,2))
        
        fin_frame = ctk.CTkFrame(popup, fg_color="transparent")
        fin_frame.pack(pady=2)
        e_ts = ctk.CTkEntry(fin_frame, width=60)
        e_ts.insert(0, str(ts))
        e_ts.pack(side="left", padx=2)
        e_vf = ctk.CTkEntry(fin_frame, width=60)
        e_vf.insert(0, str(vf))
        e_vf.pack(side="left", padx=2)
        e_ot = ctk.CTkEntry(fin_frame, width=60)
        e_ot.insert(0, str(ot))
        e_ot.pack(side="left", padx=2)

        def kaydet():
            k = e_kat.get().strip()
            a = e_ad.get().strip()
            f = e_fyt.get().strip()
            d = c_drm.get()
            l = e_link.get().strip()
            
            try:
                f_float = float(f.replace(',', '.'))
                ts_val = int(e_ts.get().strip())
                vf_val = float(e_vf.get().strip().replace(',', '.'))
                ot_val = int(e_ot.get().strip())
                
                database.urun_guncelle(uid, k, a, f_float, d, l, taksit_sayisi=ts_val, vade_farki=vf_val, odenen_taksit=ot_val)
                popup.destroy()
                self.load_treeview_data()
            except ValueError:
                messagebox.showerror("Hata", "Fiyat, Vade ve Taksit alanları sayısal olmalıdır.")

        ctk.CTkButton(popup, text="Güncelle", command=kaydet, fg_color="#F57C00", hover_color="#E65100").pack(pady=20)

    def show_dashboard_frame(self):
        self.clear_main_frame()
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        lbl_baslik = ctk.CTkLabel(self.main_frame, text="📊 FİNANSAL DASHBOARD", font=ctk.CTkFont(size=24, weight="bold"), text_color="#FFCA28")
        lbl_baslik.grid(row=0, column=0, pady=10)
        
        gfx_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        gfx_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        con = sqlite3.connect("data/urunler.db")
        df = pd.read_sql("SELECT id, kategori, urun_adi, fiyat, durum FROM urunler", con)
        con.close()
        
        if df.empty:
            lbl_bos = ctk.CTkLabel(gfx_frame, text="Henüz analiz edilecek veri yok.", text_color="gray", font=ctk.CTkFont(size=14))
            lbl_bos.pack(pady=50)
            return
            
        try:
            df['toplam_maliyet'] = df['fiyat'] + df.get('vade_farki', 0.0)
            ozet = df.groupby('kategori')['toplam_maliyet'].sum()
            
            df_harcanan = df[df['durum'].str.upper().str.contains('E|A')].copy()
            if not df_harcanan.empty:
                df_harcanan['toplam_maliyet'] = df_harcanan['fiyat'] + df_harcanan.get('vade_farki', 0.0)
                df_harcanan['kumulatif'] = df_harcanan['toplam_maliyet'].cumsum()
            
            plt.style.use('dark_background')
            fig = Figure(figsize=(10, 5), facecolor="#2b2b2b")
            fig.subplots_adjust(wspace=0.3)
            
            ax1 = fig.add_subplot(121)
            ax2 = fig.add_subplot(122)
            ax2.set_facecolor("#1e1e1e")
            
            if ozet.sum() > 0:
                ax1.pie(ozet, labels=ozet.index, autopct='%1.1f%%', startangle=140, textprops={'color':"w"})
                ax1.set_title('Kategori Bazlı Toplam Harcama (Faiz Dahil)', color="white")
                ax1.axis('equal')
                
            if not df_harcanan.empty:
                ax2.plot(range(1, len(df_harcanan)+1), df_harcanan['kumulatif'], marker='o', color='#B39DDB', linewidth=2)
                ax2.set_title("Alınan Ürünler - Birikimli Finansman", color="white")
                ax2.set_xlabel("Alınan Parça Sırası", color="white")
                ax2.set_ylabel("Toplam Maliyet / Borç (TL)", color="white")
                ax2.grid(True, alpha=0.3)
                
            canvas = FigureCanvasTkAgg(fig, master=gfx_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            ctk.CTkLabel(gfx_frame, text=f"Grafikler yüklenirken hata oluştu: {str(e)}").pack()

    def show_ai_frame(self):
        self.clear_main_frame()
        
        # Grid Title with an extra button logic
        lbl_baslik = ctk.CTkLabel(self.main_frame, text="YAPAY ZEKA FİNANS DANIŞMANI", font=ctk.CTkFont(size=24, weight="bold"), text_color="#B39DDB")
        lbl_baslik.grid(row=0, column=0, pady=10,padx=20, sticky="w")
        
        btn_api_ayar = ctk.CTkButton(self.main_frame, text="⚙️ Ayarlar Panelini Aç", width=150, fg_color="#455A64", hover_color="#263238", command=self.show_ayarlar_frame)
        btn_api_ayar.grid(row=0, column=0, sticky="e", padx=20)

        self.ai_textbox = ctk.CTkTextbox(self.main_frame, width=650, height=350, font=ctk.CTkFont(size=14), fg_color="#181818")
        self.ai_textbox.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        btn_sor = ctk.CTkButton(self.main_frame, text="Verileri Google Gemini'ye Gönder / Yorumlat", command=self.get_ai_response, height=45, font=ctk.CTkFont(weight="bold", size=14), fg_color="#6A1B9A", hover_color="#4A148C", cursor="hand2")
        btn_sor.grid(row=2, column=0, pady=20)
        
        bilgi_str = (
            "🤖 Bütçenizi yapay zeka aracılığıyla kontrol edin.\n\n"
            "Bu modül, uygulamaya girdiğiniz finansal analiz verilerinizi Google Gemini AI'a gönderir\n"
            "ve bütçenizi daha iyi optimize edebilmeniz için sizin adınıza bir asistan oluşturur.\n\n"
            "ÖNEMLİ:\n"
            "Özelliği kullanmak için sol menüden 'Sistem Ayarları' alanına girerek kendi\n"
            "API şifrenizi eklediğinizden emin olun.\n\n"
            "Hazırsanız, aşağıdaki özel butona tıklayın."
        )
        self.ai_textbox.insert("0.0", bilgi_str)
        self.ai_textbox.configure(state="disabled")

    def show_ayarlar_frame(self):
        self.clear_main_frame()
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        lbl_baslik = ctk.CTkLabel(self.main_frame, text="SİSTEM AYARLARI VE GÜVENLİK", font=ctk.CTkFont(size=24, weight="bold"), text_color="#90CAF9")
        lbl_baslik.grid(row=0, column=0, pady=20)
        
        kutu = ctk.CTkFrame(self.main_frame, fg_color="#1E1E1E")
        kutu.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        ctk.CTkLabel(kutu, text="Görsel Tema Seçimi:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=20, pady=15, sticky="e")
        def change_theme(secim):
            if secim == "Karanlık Mod (Dark)": ctk.set_appearance_mode("Dark")
            else: ctk.set_appearance_mode("Light")
        tema_menu = ctk.CTkOptionMenu(kutu, values=["Karanlık Mod (Dark)", "Aydınlık Mod (Light)"], command=change_theme)
        tema_menu.set("Karanlık Mod (Dark)" if ctk.get_appearance_mode() == "Dark" else "Aydınlık Mod (Light)")
        tema_menu.grid(row=0, column=1, padx=20, pady=15, sticky="w")
        
        ctk.CTkLabel(kutu, text="Yeni Uygulama Şifresi (PIN):", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=20, pady=15, sticky="e")
        e_yeni_pin = ctk.CTkEntry(kutu, width=150, show="*")
        e_yeni_pin.grid(row=1, column=1, padx=20, pady=15, sticky="w")
        def degistir_pin():
            yeni = e_yeni_pin.get().strip()
            if len(yeni) < 4:
                messagebox.showwarning("Geçersiz", "Şifre en az 4 haneli olmalıdır.")
                return
            yeni_hash = hashlib.sha256(yeni.encode("utf-8")).hexdigest()
            os.environ["APP_PIN"] = yeni_hash
            set_key(".env", "APP_PIN", yeni_hash)
            messagebox.showinfo("Başarılı", "Uygulama PIN kodunuz başarıyla değiştirildi! (Kriptografik olarak şifrelendi)")
            e_yeni_pin.delete(0, 'end')
        ctk.CTkButton(kutu, text="PIN Değiştir", fg_color="#D84315", hover_color="#BF360C", width=120, command=degistir_pin).grid(row=1, column=2, padx=10, pady=15, sticky="w")

        ctk.CTkLabel(kutu, text="Veritabanı (.db) Yedeği:", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, padx=20, pady=15, sticky="e")
        def yedekle():
            kayit_yeri = filedialog.asksaveasfilename(defaultextension=".bak", initialfile="urun_takip_yedek.bak", title="Yedeği Nereye Kaydedelim?")
            if kayit_yeri:
                try:
                    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "urunler.db")
                    shutil.copy2(db_path, kayit_yeri)
                    messagebox.showinfo("Başarılı", f"Veritabanı güvenle kopyalandı:\n{kayit_yeri}")
                except Exception as e:
                    messagebox.showerror("Hata", f"Yedekleme başarısız:\n{str(e)}")
        ctk.CTkButton(kutu, text="💾 Yedeği İndir", fg_color="#00695C", hover_color="#004D40", width=120, command=yedekle).grid(row=2, column=1, padx=20, pady=15, sticky="w")

        ctk.CTkLabel(kutu, text="Google Gemini AI API Key:", font=ctk.CTkFont(weight="bold")).grid(row=3, column=0, padx=20, pady=15, sticky="e")
        e_api_key = ctk.CTkEntry(kutu, width=250, show="*")
        mevcut_key = os.getenv("GEMINI_API_KEY", "")
        e_api_key.insert(0, mevcut_key)
        e_api_key.grid(row=3, column=1, padx=20, pady=15, sticky="w")
        def set_api():
            nk = e_api_key.get().strip()
            os.environ["GEMINI_API_KEY"] = nk
            set_key(".env", "GEMINI_API_KEY", nk)
            messagebox.showinfo("Başarılı", "API Anahtarı başarıyla güncellendi!")
        def clear_api():
            e_api_key.delete(0, 'end')
            os.environ["GEMINI_API_KEY"] = ""
            set_key(".env", "GEMINI_API_KEY", "")
            messagebox.showinfo("Silindi", "API Anahtarı sistemden temizlendi.")
            
        def api_yardim():
            yh = ctk.CTkToplevel(self)
            yh.title("Gemini API Nasıl Alınır?")
            yh.geometry("600x550")
            yh.transient(self)
            yh.grab_set()
            
            ctk.CTkLabel(yh, text="Nasıl Ücretsiz Google Gemini API Anahtarı Alınır?", font=ctk.CTkFont(size=18, weight="bold"), text_color="#B39DDB").pack(pady=15)
            
            txt = ctk.CTkTextbox(yh, width=550, height=450, font=ctk.CTkFont(size=14))
            txt.pack(padx=20, pady=10)
            
            metin = (
                "Adım 1: Google Hesabınızla Giriş Yapın\n"
                "  • Tarayıcınızdan 'Google AI Studio' (https://aistudio.google.com/) adresine gidin.\n\n"
                "Adım 2: API Anahtarınızı Oluşturun\n"
                "  • Sol menüden 'Get API key' (API anahtarı al) seçeneğine tıklayın.\n"
                "  • Çıkan ekranda 'Create API key in new project' butonuna basın.\n"
                "  • Ekrana gelen uzun şifre metnini (Google Gemini API Key) kopyalayın.\n\n"
                "Adım 3: Sisteme Tanımlayın\n"
                "  • Kopyaladığınız anahtarı bu ekrandaki 'API Key' kutusuna yapıştırın ve 'Kaydet' deyin.\n\n"
                "----------------------------------------------------\n\n"
                "💡 API Eklendiğinde Neler Kazanacaksınız?\n\n"
                "Tıpkı trilyon dolarlık şirketlerin kullandığı finans asistanları gibi;\n"
                "• Yapay zeka tüm harcamalarınızı analiz edip size özel tasarruf önerileri sunacaktır.\n"
                "• Kategorisel şişkinliklerinizi tespit edip, lüks veya zorunlu harcama analizi yapacaktır.\n"
                "• Hangi ay nakit darboğazına girebileceğinizi kestirip tahmini maliyet & risk analizi raporları üretecektir.\n"
                "(Gizlilik notu: Ürün isimleri asla yapay zeka ile paylaşılmaz!)\n"
            )
            txt.insert("0.0", metin)
            txt.configure(state="disabled")

        api_btn_frame = ctk.CTkFrame(kutu, fg_color="transparent")
        api_btn_frame.grid(row=3, column=2, padx=10, sticky="w")
        ctk.CTkButton(api_btn_frame, text="Kaydet", fg_color="#1B5E20", hover_color="#003300", width=60, command=set_api).pack(side="left", padx=5)
        ctk.CTkButton(api_btn_frame, text="Temizle", fg_color="#B71C1C", hover_color="#7F0000", width=60, command=clear_api).pack(side="left", padx=5)
        ctk.CTkButton(api_btn_frame, text="ℹ️ Nasıl Alınır?", fg_color="#0D47A1", hover_color="#01579B", width=100, command=api_yardim).pack(side="left", padx=5)

    def get_ai_response(self):
        self.ai_textbox.configure(state="normal")
        self.ai_textbox.delete("0.0", "end")
        self.ai_textbox.insert("0.0", "\n⏳ Lütfen bekleyin veri sunucuya ve yapay zeka motoruna iletiliyor...\n(İnternet bağlantınıza göre birkaç saniye sürebilir)")
        self.ai_textbox.configure(state="disabled")
        self.update() 

        if genai is None:
            self._ai_yazdir("\n[!] 'google-generativeai' kütüphanesi yüklenemedi.\nLütfen terminalden kurulumlarınızı tamamlayın.")
            return

        api_key = os.getenv("GEMINI_API_KEY")
            
        if not api_key or "BURAYA" in api_key or " " in api_key:
            self._ai_yazdir("\n[!] Kimlik Doğrulama Başarısız!\n\nLütfen 'Sistem Ayarları' menüsünü kullanarak\ngeçerli bir Google Gemini API key sisteme tanımlayın.")
            return
            
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            con = sqlite3.connect("data/urunler.db")
            df = pd.read_sql("SELECT kategori, urun_adi, fiyat, durum FROM urunler", con)
            con.close()
            
            if df.empty:
                self._ai_yazdir("\n[!] Henüz hiç kayıt bulunmuyor.")
                return
                
            ozet = df.groupby('kategori')['fiyat'].sum()
            durumlar = df['durum'].str.upper().str.strip()
            harcanan = df[durumlar.str.startswith('E|A')]['fiyat'].sum()
            bekleyen = df[~durumlar.str.startswith('E|A')]['fiyat'].sum()
            
            masked_str = ""
            for idx, row in df.iterrows():
                masked_str += f"- Ürün {idx+1} (Kategori: {row['kategori']}): {row['fiyat']} TL\n"
            
            prompt = f"Ben çeşitli harcamalarımı ve ihtiyaçlarımı planlayabildiğim, genel bir bütçe ve ürün takip sistemi kullanıyorum.\nGüncel bütçe tablom:\nŞimdiye kadar tam yansıyan harcama tutarı: {harcanan} TL\nPlanlanan tahmini ek maliyetler: {bekleyen} TL\n\nGizlilik Gereği Maskelenmiş Ürün Listesi:\n{masked_str}\n"
            prompt += "\nLütfen profesyonel bir finans danışmanı olarak bu rakamları detaylı olarak analiz et. Projede nereye çok param gitmiş açıkla. 3-4 cümleyle bana sıcakkanlı ve motive edici bir destek yorumu yap."
            
            response = model.generate_content(prompt)
            self._ai_yazdir("\n🤖 GEMINI YAKLAŞIMI:\n\n" + response.text.strip())
            
        except Exception as e:
            self._ai_yazdir(f"\n[!] Servis Kesintisi veya Anahtar Hatası: {e}\n\n(Lütfen API anahtarınızı kontrol edin, muhtemelen karakter hatası mevcut.)")

    def _ai_yazdir(self, metin):
        self.ai_textbox.configure(state="normal")
        self.ai_textbox.delete("0.0", "end")
        self.ai_textbox.insert("0.0", metin)
        self.ai_textbox.configure(state="disabled")

    def show_web_frame(self):
        self.clear_main_frame()
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        baslik_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        baslik_frame.grid(row=0, column=0, pady=10)
        
        lbl_baslik = ctk.CTkLabel(baslik_frame, text="WEB'DEN ÜRÜN BUL", font=ctk.CTkFont(size=24, weight="bold"), text_color="#FBC02D")
        lbl_baslik.pack(side="left", padx=5)
        
        lbl_info = ctk.CTkLabel(baslik_frame, text="ℹ️", font=ctk.CTkFont(size=18), text_color="#81D4FA", cursor="hand2")
        lbl_info.pack(side="left", padx=5)
        
        self.lbl_tooltip = ctk.CTkLabel(
            self.main_frame, 
            text="Bu aracı motor, bilgisayarınızı kastırmadan arka planda güvenli şekilde\nTrendyol ve N11 üzerindeki ürünleri (gerçek zamanlı) tarar.", 
            fg_color="#263238", 
            text_color="white", 
            corner_radius=6, 
            padx=10, 
            pady=8
        )
        
        def show_tooltip(e):
            self.lbl_tooltip.place(in_=lbl_info, relx=1.3, rely=-0.5)
            
        def hide_tooltip(e):
            self.lbl_tooltip.place_forget()
            
        lbl_info.bind("<Enter>", show_tooltip)
        lbl_info.bind("<Leave>", hide_tooltip)
        
        ayar_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        ayar_frame.grid(row=1, column=0, pady=5)
        
        self.radio_var = ctk.StringVar(value="hizli")
        radio_hizli = ctk.CTkRadioButton(ayar_frame, text="⚡ Hızlı Arama (Trendyol/N11)", variable=self.radio_var, value="hizli", text_color="#A5D6A7")
        radio_hizli.pack(side="left", padx=10)
        radio_uzun = ctk.CTkRadioButton(ayar_frame, text="🐢 Kapsamlı Arama (Amazon/Selenium)", variable=self.radio_var, value="kapsamli", text_color="#FFB74D")
        radio_uzun.pack(side="left", padx=10)

        arama_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        arama_frame.grid(row=2, column=0, pady=5)
        
        lbl_arama = ctk.CTkLabel(arama_frame, text="Aranacak Ürün:")
        lbl_arama.pack(side="left", padx=5)
        
        self.e_web_ara = ctk.CTkEntry(arama_frame, width=250)
        self.e_web_ara.pack(side="left", padx=5)
        self.e_web_ara.bind('<Return>', lambda e: self.web_arama_baslat())
        
        btn_ara = ctk.CTkButton(arama_frame, text="Bul", width=80, fg_color="#F57C00", hover_color="#E65100", command=self.web_arama_baslat)
        btn_ara.pack(side="left", padx=5)

        style = ttk.Style()
        self.tree_web = ttk.Treeview(self.main_frame, columns=("Platform", "Ürün Adı", "Fiyat", "Link"), show="headings", height=12)
        self.tree_web.heading("Platform", text="Platform")
        self.tree_web.heading("Ürün Adı", text="Ürün Adı")
        self.tree_web.heading("Fiyat", text="Fiyat (TL)")
        self.tree_web.heading("Link", text="Link")
        
        self.tree_web.column("Platform", width=80, anchor="center")
        self.tree_web.column("Ürün Adı", width=350, anchor="w")
        self.tree_web.column("Fiyat", width=90, anchor="e")
        self.tree_web.column("Link", width=0, stretch=False)
        self.tree_web.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")

        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.grid(row=4, column=0, pady=10)
        
        btn_ekle = ctk.CTkButton(btn_frame, text="Veritabanıma Ekle", fg_color="#1B5E20", hover_color="#003300", command=self.web_db_ekle)
        btn_ekle.pack(side="left", padx=10)
        
        btn_link = ctk.CTkButton(btn_frame, text="📍 Tarayıcıda Aç", fg_color="#1976D2", hover_color="#1565C0", command=self.web_linke_git)
        btn_link.pack(side="left", padx=10)
        
        self.lbl_web_durum = ctk.CTkLabel(self.main_frame, text="", text_color="yellow")
        self.lbl_web_durum.grid(row=5, column=0, pady=5)

    def web_arama_baslat(self):
        kelime = self.e_web_ara.get().strip()
        if len(kelime) < 3:
            self.lbl_web_durum.configure(text="Lütfen aramak için kelime girin.")
            return
            
        self.lbl_web_durum.configure(text="⏳ Aranıyor... (Lütfen bekleyin)")
        self.update()
        for item in self.tree_web.get_children():
            self.tree_web.delete(item)
            
        def fetch():
            import web_scraper
            try:
                mod = self.radio_var.get()
                sonuclar = web_scraper.urun_ara(kelime, mode=mod)
                def ekrana_bas():
                    if not sonuclar:
                        self.lbl_web_durum.configure(text="Sonuç bulunamadı veya bağlantı hatası oluştu.", text_color="yellow")
                        return
                    for s in sonuclar:
                        self.tree_web.insert("", "end", values=(s['platform'], s['baslik'], f"{s['fiyat']:.2f}", s['link']))
                    self.lbl_web_durum.configure(text=f"✅ {len(sonuclar)} sonuç listelendi. (Ucuzdan pahalıya)", text_color="#64DD17")
                self.after(0, ekrana_bas)
            except Exception as e:
                def hata_bas():
                    hmesaj = str(e)
                    messagebox.showerror("Eksik Kurulum veya Sistem Hatası", hmesaj)
                    self.lbl_web_durum.configure(text="❌ Arama motoru hatası. Lütfen uyarılara bakın.", text_color="#FF5252")
                self.after(0, hata_bas)

        threading.Thread(target=fetch, daemon=True).start()

    def web_linke_git(self):
        selected = self.tree_web.selection()
        if not selected:
            return
        link = self.tree_web.item(selected[0])['values'][3]
        if link: webbrowser.open(link)

    def web_db_ekle(self):
        selected = self.tree_web.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen web tablosundan bir ürün seçin.")
            return
            
        val = self.tree_web.item(selected[0])['values']
        ad = str(val[1])
        fyt = float(str(val[2]))
        link = str(val[3])
        
        popup = ctk.CTkToplevel(self)
        popup.title("Hızlı Kayıt")
        popup.geometry("350x250")
        popup.transient(self)
        popup.grab_set()
        
        ctk.CTkLabel(popup, text=f"Seçilen Ürün:\n{ad[:40]}...", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        ctk.CTkLabel(popup, text="Hangi Kategoriye Eklensin?").pack(pady=5)
        
        rows = database.urunleri_getir()
        kategoriler = list(set([r[1] for r in rows]))
        if not kategoriler:
            kategoriler = ["Elektronik", "Giyim", "Market", "Diğer"]
            
        c_kat = ctk.CTkComboBox(popup, values=kategoriler, width=200)
        c_kat.pack(pady=10)
        
        def kaydet():
            k = c_kat.get().strip()
            if not k:
                k = "Diğer"
            database.urun_ekle(k, ad, fyt, "Hayır", link)
            popup.destroy()
            messagebox.showinfo("Başarılı", f"{ad[:30]}...\n\nSisteminize başarıyla kaydedildi!")
            
        ctk.CTkButton(popup, text="Sisteme Kaydet", fg_color="#1B5E20", command=kaydet).pack(pady=20)

    def show_harita_frame(self):
        self.clear_main_frame()
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        lbl_baslik = ctk.CTkLabel(self.main_frame, text="PROJE GELİŞİM RAPORU & GÖREV YOL HARİTASI", font=ctk.CTkFont(size=24, weight="bold"), text_color="#81D4FA")
        lbl_baslik.grid(row=0, column=0, pady=10)
        
        txt_harita = ctk.CTkTextbox(self.main_frame, font=ctk.CTkFont(size=14), fg_color="#181818", text_color="#E0E0E0")
        txt_harita.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        try:
            with open("PROJE_RAPORU_VE_GELISIM.md", "r", encoding="utf-8") as f:
                icerik = f.read()
            txt_harita.insert("0.0", icerik)
        except Exception:
            txt_harita.insert("0.0", "[!] PROJE_RAPORU_VE_GELISIM.md dosyası bulunamadı.")
            
        txt_harita.configure(state="disabled")

def baslat_kurulum_modu():
    import shutil, subprocess
    
    kur_app = ctk.CTk()
    kur_app.title("Ürün Takip Sistemi - Kurulum Sihirbazı")
    kur_app.geometry("550x450")
    kur_app.eval('tk::PlaceWindow . center')
    
    ctk.CTkLabel(kur_app, text="Ürün Takip Sistemi Kurulumu", font=ctk.CTkFont(size=22, weight="bold"), text_color="#2196F3").pack(pady=15)
    ctk.CTkLabel(kur_app, text="Bu sihirbaz uygulamayı sisteminize entegre edip kuracaktır.\nLütfen kurulum dizinini ve seçeneklerinizi belirleyin:", text_color="gray").pack(pady=5)
    
    appdata_def = os.path.join(os.getenv("APPDATA") or os.path.expanduser("~"), "UrunTakipSistemi")
    
    frame_path = ctk.CTkFrame(kur_app, fg_color="transparent")
    frame_path.pack(pady=10, fill="x", padx=40)
    
    ctk.CTkLabel(frame_path, text="Hedef Kurulum Klasörü:").pack(anchor="w")
    
    e_path = ctk.CTkEntry(frame_path, width=350)
    e_path.pack(side="left", padx=(0, 10))
    e_path.insert(0, appdata_def)
    
    def sec_dizin():
        from tkinter import filedialog
        d = filedialog.askdirectory(title="Kurulum Klasörünü Seçin", initialdir=os.path.dirname(appdata_def))
        if d:
            hedef = os.path.join(d, "UrunTakipSistemi") if not d.lower().endswith("uruntakipsistemi") else d
            e_path.delete(0, 'end')
            e_path.insert(0, hedef)
            
    ctk.CTkButton(frame_path, text="Gözat...", width=80, command=sec_dizin).pack(side="left")
    
    opts_frame = ctk.CTkFrame(kur_app, fg_color="transparent")
    opts_frame.pack(pady=10, anchor="w", padx=40)
    
    var_desktop = ctk.BooleanVar(value=True)
    var_startmenu = ctk.BooleanVar(value=True)
    
    ctk.CTkCheckBox(opts_frame, text="Masaüstüne Kısayol Ekle", variable=var_desktop).pack(pady=5, anchor="w")
    ctk.CTkCheckBox(opts_frame, text="Windows Başlat/Arama Menüsüne Ekle", variable=var_startmenu).pack(pady=5, anchor="w")
    
    def kur_ve_bitir():
        btn_kur.configure(state="disabled", text="Sisteme Kuruluyor...")
        kur_app.update()
        
        try:
            install_dir = os.path.normpath(e_path.get().strip())
            os.makedirs(install_dir, exist_ok=True)
            
            target_path = os.path.join(install_dir, "Urun Takip Sistemi.exe")
            current_exe = sys.executable
            
            # Kılavuz Dosyasını Üret ve Kaydet
            kilavuz = """-----------------------------------------------------------
          ÜRÜN TAKİP SİSTEMİ - A'DAN Z'YE KULLANIM KILAVUZU
-----------------------------------------------------------

Hoş Geldiniz! Bu uygulama finansal alımlarınızı, bütçenizi ve e-ticaret 
araştırmalarınızı tek bir ekranda birleştiren kapsamlı bir araçtır.

1. İLK GİRİŞ VE AYARLAR
- Programa her girişinizde güvenlik şifresi (PIN) istenir. 
- İlk kurulumda şifreniz: 1234
- Dilediğiniz zaman sol menüdeki "Sistem Ayarları" kısmından bu şifreyi değiştirebilirsiniz.
- Sistem Ayarlarında ayrıca Karanlık/Aydınlık mod seçebilir ve Veritabanı Yedeğinizi alabilirsiniz.

2. ÜRÜN EKLEME (TAKSİT VE VADE FARKI)
- Sol menüden "Parça Ekle" butonunu kullanın.
- Ürün adı, Fiyat, Kategori ve İsteğe Bağlı olarak Ürün Linkini ekleyebilirsiniz.
- Taksitli bir harcama ise taksit sayısını ve eklenecek vade farkını (faiz) belirtebilirsiniz.

3. LİSTELEME, GÜNCELLEME VE EXCEL
- "Liste & Düzenle" sekmesinde verilerinizi Kategori veya İsme göre süzebilirsiniz.
- Bir ürünü düzenlemek için üzerine çift tıklamanız yeterlidir.
- "Excel'e Aktar" butonu ile ekrandaki her şeyi bilgisayarınıza indirebilirsiniz.
- "İçe Aktar" butonu ile kendi Excel dosyalarınızı topluca sisteme yükleyebilirsiniz.

4. YAPAY ZEKA DESTEĞİ (GEMINI)
- Sistem Ayarları menüsünde "Nasıl API Alınır?" rehberi mevcuttur. 
- API kodunuzu girdikten sonra "Yapay Zeka" sekmesinde saniyeler içinde bütün 
  harcamalarınızı analiz ettirebilir ve tasarruf / sağlık önerileri alabilirsiniz.

5. WEB'DEN OTOMATİK ÜRÜN BULMA (BOT)
- Trendyol, Amazon ve N11 üzerindeki ürün fiyatlarını tek tuşla, tarayıcıya girmeden 
  "Web'den Bul" sekmesinde tarayabilirsiniz.
- Hoşunuza giden bir sonucu "Hızlı Kayıt" seçeneğiyle doğrudan veritabanınıza kaydedebilirsiniz.

Geliştirici Sürümü: V1.0 - Tüm Hakları Saklıdır.
-----------------------------------------------------------"""
            kilavuz_yolu = os.path.join(install_dir, "Kullanim_Kilavuzu.txt")
            with open(kilavuz_yolu, "w", encoding="utf-8") as kf:
                kf.write(kilavuz)
            
            
            # Kendini asıl dizine kopyala
            shutil.copy2(current_exe, target_path)
            
            vbs_lines = ['Set oWS = WScript.CreateObject("WScript.Shell")']
            
            if var_desktop.get():
                desktop = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop")
                vbs_lines.append(f'Set oLink1 = oWS.CreateShortcut("{os.path.join(desktop, "Ürün Takip Sistemi.lnk")}")')
                vbs_lines.append(f'oLink1.TargetPath = "{target_path}"')
                vbs_lines.append(f'oLink1.WorkingDirectory = "{install_dir}"')
                vbs_lines.append('oLink1.Save')
                
            if var_startmenu.get():
                appdata_system = os.getenv("APPDATA") or os.path.expanduser("~")
                programs = os.path.join(appdata_system, "Microsoft", "Windows", "Start Menu", "Programs")
                vbs_lines.append(f'Set oLink2 = oWS.CreateShortcut("{os.path.join(programs, "Ürün Takip Sistemi.lnk")}")')
                vbs_lines.append(f'oLink2.TargetPath = "{target_path}"')
                vbs_lines.append(f'oLink2.WorkingDirectory = "{install_dir}"')
                vbs_lines.append('oLink2.Save')
                
            vbs_path = os.path.join(install_dir, "create_shortcuts.vbs")
            with open(vbs_path, "w", encoding="utf-8") as f:
                f.write("\n".join(vbs_lines))
                
            subprocess.call(f'cscript //nologo "{vbs_path}"', shell=True)
            if os.path.exists(vbs_path): os.remove(vbs_path)
            
            messagebox.showinfo("Kurulum Tamamlandı", "Yazılım bilgisayarınıza kalıcı olarak kuruldu!\nKısayollardan uygulamanızı dilediğiniz zaman başlatabilirsiniz. \n\nNot: İndirdiğiniz bu Kurulum dosyasını artık silebilirsiniz.")
            subprocess.Popen([target_path])
            kur_app.destroy()
            sys.exit(0)
            
        except Exception as e:
            messagebox.showerror("Kurulum Hatası", f"Hata oluştu:\n{e}")
            btn_kur.configure(state="normal", text="Tekrar Dene")
            
    btn_kur = ctk.CTkButton(kur_app, text="Yükle (Install)", font=ctk.CTkFont(weight="bold"), fg_color="#1B5E20", hover_color="#003300", width=200, height=40, command=kur_ve_bitir)
    btn_kur.pack(pady=20)
    
    kur_app.mainloop()

if __name__ == "__main__":
    import sys
    # Uygulama EXE olarak derlenmişse "UrunTakipSistemi" adlı klasörde olup olmadığı kontrol ediliyor.
    # Kullanıcının seçtiği hedef dizin (UrunTakipSistemi) klasörünün içinde değilsek Installer modu tetiklenir:
    if getattr(sys, 'frozen', False):
        current_dir = os.path.dirname(os.path.abspath(sys.executable))
        dir_name = os.path.basename(current_dir).lower()
        
        if dir_name != "uruntakipsistemi":
            baslat_kurulum_modu()
            sys.exit(0)

    # UrunTakipSistemi içerisindeyse veya script (python) olarak çalışıyorsa doğrudan başlat:
    app = App()
    app.mainloop()
