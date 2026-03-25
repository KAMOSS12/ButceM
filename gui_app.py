import os
import customtkinter as ctk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from dotenv import load_dotenv
import database
import profile_manager

__version__ = "2.2.0"
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


def treeview_sort_column(tree, col, reverse):
    """Treeview kolon başlığına tıklayınca sırala."""
    data = [(tree.set(child, col), child) for child in tree.get_children('')]
    try:
        data.sort(key=lambda t: float(str(t[0]).replace(',', '.')), reverse=reverse)
    except (ValueError, TypeError):
        data.sort(key=lambda t: str(t[0]).lower(), reverse=reverse)
    for index, (val, child) in enumerate(data):
        tree.move(child, '', index)
    tree.heading(col, command=lambda: treeview_sort_column(tree, col, not reverse))


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BütçeM - Masaüstü Asistanı")
        self.geometry("1050x700")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.current_profile = ""
        self.backup_manager = None
        self.notification_manager = None
        self.price_tracker = None

        # --- SOL MENÜ (SIDEBAR) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="BütçeM", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 5))

        self.lbl_profil = ctk.CTkLabel(self.sidebar_frame, text="", text_color="#81D4FA", font=ctk.CTkFont(size=11))
        self.lbl_profil.grid(row=1, column=0, padx=20, pady=(0, 15))

        self.btn_ekle = ctk.CTkButton(self.sidebar_frame, text="➕ 1. Parça Ekle", command=self.show_ekle_frame)
        self.btn_ekle.grid(row=2, column=0, padx=20, pady=10)

        self.btn_liste = ctk.CTkButton(self.sidebar_frame, text="📃 2. Liste & CRUD", command=self.show_liste_frame)
        self.btn_liste.grid(row=3, column=0, padx=20, pady=10)

        self.btn_grafik = ctk.CTkButton(self.sidebar_frame, text="📊 3. Dashboard", fg_color="#00695C", hover_color="#004D40", command=self.show_dashboard_frame)
        self.btn_grafik.grid(row=4, column=0, padx=20, pady=10)

        self.btn_ai = ctk.CTkButton(self.sidebar_frame, text="🤖 4. Yapay Zeka", fg_color="#6A1B9A", hover_color="#4A148C", command=self.show_ai_frame)
        self.btn_ai.grid(row=5, column=0, padx=20, pady=10)

        self.btn_web = ctk.CTkButton(self.sidebar_frame, text="🌐 5. Web'den Bul", fg_color="#FBC02D", text_color="black", hover_color="#F57F17", command=self.show_web_frame)
        self.btn_web.grid(row=6, column=0, padx=20, pady=10)

        self.btn_fiyat_takip = ctk.CTkButton(self.sidebar_frame, text="🔔 6. Fiyat Takip", fg_color="#E65100", hover_color="#BF360C", command=self.show_fiyat_takip_frame)
        self.btn_fiyat_takip.grid(row=7, column=0, padx=20, pady=10)

        self.btn_ayarlar = ctk.CTkButton(self.sidebar_frame, text="⚙️ 7. Sistem Ayarları", fg_color="#37474F", hover_color="#263238", command=self.show_ayarlar_frame)
        self.btn_ayarlar.grid(row=8, column=0, padx=20, pady=10)

        self.lbl_kur = ctk.CTkLabel(self.sidebar_frame, text="Kurlar Yükleniyor...", text_color="#A5D6A7", font=ctk.CTkFont(size=12))
        self.lbl_kur.grid(row=9, column=0, pady=20)

        self.usd_rate = 0.0

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.withdraw()
        self._init_profiles_and_login()

    def _init_profiles_and_login(self):
        """Profil sistemini başlat ve login ekranını göster."""
        profile_manager.ensure_profiles_exist()
        self.show_login_screen()

    def _on_close(self):
        """Uygulama kapanışında arka plan görevlerini durdur."""
        if self.backup_manager:
            self.backup_manager.stop_scheduled()
        if self.notification_manager:
            self.notification_manager.stop_periodic_checks()
        if self.price_tracker:
            self.price_tracker.stop_periodic_checks()
        self.destroy()

    def show_login_screen(self):
        login = ctk.CTkToplevel(self)
        login.title("BütçeM - Giriş")
        login.geometry("350x320")
        login.resizable(False, False)

        login.protocol("WM_DELETE_WINDOW", self.destroy)

        ctk.CTkLabel(login, text="Profil Seçin:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(20, 10))

        profiles = profile_manager.list_profiles()
        profile_names = [p["name"] for p in profiles]
        last_active = profile_manager.get_last_active_profile()

        self.login_profile_var = ctk.StringVar(value=last_active if last_active else (profile_names[0] if profile_names else ""))
        profile_combo = ctk.CTkComboBox(login, values=profile_names, variable=self.login_profile_var, width=200)
        profile_combo.pack(pady=5)

        btn_new_profile = ctk.CTkButton(login, text="+ Yeni Profil", width=120, fg_color="#455A64",
                                        command=lambda: self._create_profile_popup(login, profile_combo))
        btn_new_profile.pack(pady=5)

        ctk.CTkLabel(login, text="PIN Kodu:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 5))
        self.pin_entry = ctk.CTkEntry(login, show="*", width=150, justify="center")
        self.pin_entry.pack(pady=5)
        self.pin_entry.bind('<Return>', lambda e: self.check_pin(login))

        ctk.CTkButton(login, text="GİRİŞ YAP", command=lambda: self.check_pin(login)).pack(pady=10)

        self.login_lbl = ctk.CTkLabel(login, text="Varsayılan PIN: 1234", text_color="gray", font=ctk.CTkFont(size=11))
        self.login_lbl.pack()

    def _create_profile_popup(self, login_win, combo):
        popup = ctk.CTkToplevel(login_win)
        popup.title("Yeni Profil")
        popup.geometry("300x220")
        popup.transient(login_win)
        popup.grab_set()

        ctk.CTkLabel(popup, text="Profil Adı:").pack(pady=(15, 5))
        e_name = ctk.CTkEntry(popup, width=200)
        e_name.pack(pady=5)

        ctk.CTkLabel(popup, text="PIN (min 4 hane):").pack(pady=5)
        e_pin = ctk.CTkEntry(popup, width=200, show="*")
        e_pin.pack(pady=5)

        def create():
            name = e_name.get().strip()
            pin = e_pin.get().strip()
            if not name:
                messagebox.showwarning("Uyarı", "Profil adı boş olamaz.", parent=popup)
                return
            if len(pin) < 4:
                messagebox.showwarning("Uyarı", "PIN en az 4 haneli olmalıdır.", parent=popup)
                return
            try:
                safe_name = profile_manager.create_profile(name, pin)
                profiles = profile_manager.list_profiles()
                combo.configure(values=[p["name"] for p in profiles])
                self.login_profile_var.set(safe_name)
                popup.destroy()
                messagebox.showinfo("Başarılı", f"'{safe_name}' profili oluşturuldu!", parent=login_win)
            except ValueError as ve:
                messagebox.showerror("Hata", str(ve), parent=popup)

        ctk.CTkButton(popup, text="Oluştur", fg_color="#1B5E20", command=create).pack(pady=15)

    def check_pin(self, login_win):
        if not hasattr(self, '_pin_attempts'):
            self._pin_attempts = 0
            self._pin_locked_until = 0

        now = time.time()
        if now < self._pin_locked_until:
            kalan = int(self._pin_locked_until - now)
            self.login_lbl.configure(text=f"Çok fazla hatalı deneme! {kalan}sn bekleyin.", text_color="#FF5252")
            return

        selected_profile = self.login_profile_var.get().strip()
        if not selected_profile:
            self.login_lbl.configure(text="Lütfen bir profil seçin.", text_color="#FF5252")
            return

        settings = profile_manager.load_profile_settings(selected_profile)
        correct_pin = settings.get("pin_hash", "")

        if not correct_pin or len(correct_pin) != 64:
            correct_pin = hashlib.sha256("1234".encode("utf-8")).hexdigest()

        p = self.pin_entry.get()
        input_hash = hashlib.sha256(p.encode("utf-8")).hexdigest()

        if input_hash == correct_pin:
            self._pin_attempts = 0
            self.current_profile = selected_profile
            profile_manager.set_last_active_profile(selected_profile)

            # Profil DB'yi ayarla
            database.set_db_path(profile_manager.get_profile_db_path(selected_profile))
            database.init_db()
            database.migrate_from_csv()

            # Tema uygula
            theme = settings.get("theme", "Dark")
            ctk.set_appearance_mode(theme)

            # Arka plan yöneticilerini başlat
            self._start_background_managers(settings)

            login_win.destroy()
            self.lbl_profil.configure(text=f"[{selected_profile}]")
            self.deiconify()
            self.load_currency()
            self.show_liste_frame()
            self.start_autolock()
        else:
            self._pin_attempts += 1
            if self._pin_attempts >= 5:
                self._pin_locked_until = now + 60
                self.login_lbl.configure(text="5 hatalı deneme! 60 saniye kilitlendi.", text_color="#FF5252")
            elif self._pin_attempts >= 3:
                self._pin_locked_until = now + 15
                self.login_lbl.configure(text=f"3 hatalı deneme! 15 saniye bekleyin.", text_color="#FF5252")
            else:
                self.login_lbl.configure(text=f"Hatalı PIN! ({self._pin_attempts}/5 deneme)", text_color="#FF5252")
        self.pin_entry.delete(0, 'end')

    def _start_background_managers(self, settings):
        """Yedekleme, bildirim ve fiyat takip yöneticilerini başlat."""
        import backup_manager as bm
        import notification_manager as nm
        import price_tracker as pt

        # Yedekleme
        self.backup_manager = bm.BackupManager(self.current_profile, settings.get("backup", {}))
        if settings.get("backup", {}).get("enabled", False):
            self.backup_manager.start_scheduled()

        # Bildirimler
        notif_settings = settings.get("notifications", {})
        notif_settings["monthly_budget"] = settings.get("monthly_budget", 0)
        self.notification_manager = nm.NotificationManager(self.current_profile, notif_settings, database)
        self.notification_manager.run_startup_checks()

        # Fiyat takip
        self.price_tracker = pt.PriceTracker(notification_manager=self.notification_manager)
        self.price_tracker.start_periodic_checks()

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
        if time.time() - self.last_activity > 300:
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
        except Exception:
            pass

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # ─── PARÇA EKLE ───────────────────────────────────────────────────

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

        lbl_odeme = ctk.CTkLabel(self.main_frame, text="Ödeme Şekli:")
        lbl_odeme.grid(row=6, column=0, padx=20, pady=15, sticky="e")

        odeme_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        odeme_frame.grid(row=6, column=1, padx=20, pady=15, sticky="w")

        self.odeme_var = ctk.StringVar(value="nakit")

        self.radio_nakit = ctk.CTkRadioButton(odeme_frame, text="Nakit", variable=self.odeme_var, value="nakit", command=self.toggle_taksit_alanlari)
        self.radio_nakit.pack(side="left", padx=(0, 20))
        self.radio_taksitli = ctk.CTkRadioButton(odeme_frame, text="Taksitli", variable=self.odeme_var, value="taksitli", command=self.toggle_taksit_alanlari)
        self.radio_taksitli.pack(side="left")

        self.taksit_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.taksit_frame.grid(row=7, column=0, columnspan=2, pady=5)

        lbl_taksit = ctk.CTkLabel(self.taksit_frame, text="Taksit Sayısı:")
        lbl_taksit.grid(row=0, column=0, padx=20, pady=8, sticky="e")
        self.entry_taksit = ctk.CTkEntry(self.taksit_frame, width=250, placeholder_text="Örn: 6")
        self.entry_taksit.grid(row=0, column=1, padx=20, pady=8, sticky="w")

        lbl_vade = ctk.CTkLabel(self.taksit_frame, text="Vade Farkı (TL):")
        lbl_vade.grid(row=1, column=0, padx=20, pady=8, sticky="e")
        self.entry_vade = ctk.CTkEntry(self.taksit_frame, width=250, placeholder_text="Örn: 150.00")
        self.entry_vade.grid(row=1, column=1, padx=20, pady=8, sticky="w")

        self.taksit_frame.grid_remove()

        btn_kaydet = ctk.CTkButton(self.main_frame, text="KAYDET", command=self.kaydet_veriler, fg_color="#1B5E20", hover_color="#003300")
        btn_kaydet.grid(row=8, column=0, columnspan=2, pady=30)

        self.lbl_mesaj = ctk.CTkLabel(self.main_frame, text="", text_color="yellow")
        self.lbl_mesaj.grid(row=9, column=0, columnspan=2)

    def toggle_taksit_alanlari(self):
        if self.odeme_var.get() == "taksitli":
            self.taksit_frame.grid()
        else:
            self.taksit_frame.grid_remove()

    def kaydet_veriler(self):
        kategori = self.entry_kat.get().strip()
        ad = self.entry_ad.get().strip()
        fiyat = self.entry_fiyat.get().strip()
        durum = self.option_durum.get().strip()
        link = self.entry_link.get().strip()

        if not kategori or not ad or not fiyat:
            self.lbl_mesaj.configure(text="Uyarı: Lütfen tüm alanları doldurun!", text_color="#FF5252")
            return

        try:
            fiyat_float = float(fiyat.replace(',', '.'))
            if fiyat_float <= 0:
                self.lbl_mesaj.configure(text="Hata: Fiyat sıfırdan büyük olmalıdır!", text_color="#FF5252")
                return
        except ValueError:
            self.lbl_mesaj.configure(text="Hata: Fiyat alanına sadece rakam giriniz!", text_color="#FF5252")
            return

        if self.odeme_var.get() == "nakit":
            taksit = 0
            vade = 0.0
        else:
            taksit_str = self.entry_taksit.get().strip()
            vade_str = self.entry_vade.get().strip()
            try:
                taksit = int(taksit_str) if taksit_str else 2
                vade = float(vade_str.replace(',', '.')) if vade_str else 0.0
                if taksit < 2:
                    self.lbl_mesaj.configure(text="Hata: Taksit sayısı en az 2 olmalıdır!", text_color="#FF5252")
                    return
            except ValueError:
                self.lbl_mesaj.configure(text="Hata: Taksit ve Vade alanlarına sadece rakam giriniz!", text_color="#FF5252")
                return

        database.urun_ekle(kategori, ad, fiyat_float, durum, link, taksit_sayisi=taksit, vade_farki=vade)
        self.lbl_mesaj.configure(text=f"✅ '{ad}' veritabanına eklendi!", text_color="#64DD17")
        self.entry_kat.set("")
        self.entry_ad.delete(0, 'end')
        self.entry_fiyat.delete(0, 'end')
        self.entry_link.delete(0, 'end')
        self.odeme_var.set("nakit")
        self.toggle_taksit_alanlari()
        self.entry_taksit.delete(0, 'end')
        self.entry_vade.delete(0, 'end')

    # ─── LİSTE & CRUD ────────────────────────────────────────────────

    def show_liste_frame(self):
        self.clear_main_frame()
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        lbl_baslik = ctk.CTkLabel(self.main_frame, text="ENVANTER VE FİNANSAL ÖZET", font=ctk.CTkFont(size=24, weight="bold"))
        lbl_baslik.grid(row=0, column=0, pady=10)

        filtre_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        filtre_frame.grid(row=1, column=0, pady=10, sticky="ew")

        lbl_ara = ctk.CTkLabel(filtre_frame, text="Ürün Ara:")
        lbl_ara.pack(side="left", padx=5)
        self.entry_ara = ctk.CTkEntry(filtre_frame, width=150)
        self.entry_ara.pack(side="left", padx=5)

        lbl_filtre_kat = ctk.CTkLabel(filtre_frame, text="Kategori Filtre:")
        lbl_filtre_kat.pack(side="left", padx=(20, 5))

        rows = database.urunleri_getir()
        kategoriler = list(set([r[1] for r in rows]))
        kategoriler.insert(0, "Tümü")

        self.combo_kat = ctk.CTkOptionMenu(filtre_frame, values=kategoriler)
        self.combo_kat.pack(side="left", padx=5)
        self.combo_kat.set("Tümü")

        btn_ara = ctk.CTkButton(filtre_frame, text="Filtrele", width=80, command=self.load_treeview_data)
        btn_ara.pack(side="left", padx=10)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2a2d2e", foreground="white", rowheight=25, fieldbackground="#2a2d2e", borderwidth=0)
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")
        style.map("Treeview.Heading", background=[('active', '#3484F0')])

        self.tree = ttk.Treeview(self.main_frame, columns=("ID", "Kategori", "Ürün Adı", "Maliyet", "Durum", "Taksit"), show="headings", height=15)
        self.tree.tag_configure("oddrow", background="#2a2d2e")
        self.tree.tag_configure("evenrow", background="#343638")

        # Bug 9: Kolon sıralama desteği
        for col_id, col_text in [("ID", "ID"), ("Kategori", "Kategori"), ("Ürün Adı", "Ürün Adı"),
                                  ("Maliyet", "Mal. (TL) [Vade Dahil]"), ("Durum", "Durum"), ("Taksit", "Ödeme")]:
            self.tree.heading(col_id, text=col_text, command=lambda c=col_id: treeview_sort_column(self.tree, c, False))

        self.tree.column("ID", width=30, anchor="center")
        self.tree.column("Kategori", width=120, anchor="center")
        self.tree.column("Ürün Adı", width=200, anchor="w")
        self.tree.column("Maliyet", width=150, anchor="e")
        self.tree.column("Durum", width=100, anchor="center")
        self.tree.column("Taksit", width=100, anchor="center")

        self.tree.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.tree.bind("<Double-1>", lambda e: self.guncelle_popup())

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
                bekleyen_h += toplam_maliyet

            taksit_str = f"{ot}/{ts}" if ts >= 2 else "Nakit"
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
            # Bug 1 fix: race condition önleme
            rate = getattr(self, "usd_rate", 0)
            if rate > 0:
                t_usd = (toplam_h + bekleyen_h) / rate
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

        dosya_boyutu = os.path.getsize(dosya_yolu)
        if dosya_boyutu > 10 * 1024 * 1024:
            messagebox.showerror("Hata", "Dosya boyutu 10MB'ı aşıyor! Lütfen daha küçük bir dosya seçin.")
            return

        try:
            if dosya_yolu.endswith(".csv"):
                df_full = pd.read_csv(dosya_yolu)
            else:
                df_full = pd.read_excel(dosya_yolu)
            toplam_satir = len(df_full)
            if toplam_satir > 10000:
                messagebox.showwarning("Uyarı", f"Dosyada {toplam_satir} satır var. Maksimum 10.000 satır aktarılacak, geri kalanı atlanacaktır.")
                df = df_full.head(10000)
            else:
                df = df_full
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya okunurken hata oluştu:\n{e}")
            return

        gerekenler = ["Kategori", "Ürün Adı", "Fiyat"]
        if not set(gerekenler).issubset(df.columns):
            messagebox.showerror("Eksik Sütun", f"Verinizde şu temel sütunlar eksik: {', '.join(gerekenler)}\nLütfen örnek '.xlsx' yapısına uyun.")
            return

        p = ctk.CTkToplevel(self)
        p.title("Toplu İçe Aktarma - Onay Ekranı")
        p.geometry("800x500")
        p.transient(self)
        p.grab_set()

        ctk.CTkLabel(p, text=f"Önizleme: Toplam {len(df)} kayıt bulundu.", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

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
        rows = []
        for child in self.tree.get_children():
            item = self.tree.item(child)
            rows.append(item['values'])

        if not rows:
            messagebox.showinfo("Bilgi", "Dışa aktarılacak veri bulunamadı.")
            return

        columns = ["ID", "Kategori", "Ürün Adı", "Maliyet", "Durum", "Taksit", "Link", "Taksit_S", "Vade_Farki", "Odenen_T", "Fiyat"]
        df = pd.DataFrame(rows, columns=columns)

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

        ctk.CTkLabel(popup, text="Ödeme Şekli:").pack(pady=(10, 2))

        # Bug 3 fix: TypeError önleme
        try:
            ts_int = int(ts)
        except (ValueError, TypeError):
            ts_int = 0
        odeme_var_p = ctk.StringVar(value="taksitli" if ts_int >= 2 else "nakit")

        odeme_frame_p = ctk.CTkFrame(popup, fg_color="transparent")
        odeme_frame_p.pack(pady=2)

        taksit_frame_p = ctk.CTkFrame(popup, fg_color="transparent")

        def toggle_popup_taksit():
            if odeme_var_p.get() == "taksitli":
                taksit_frame_p.pack(pady=5)
            else:
                taksit_frame_p.pack_forget()

        ctk.CTkRadioButton(odeme_frame_p, text="Nakit", variable=odeme_var_p, value="nakit", command=toggle_popup_taksit).pack(side="left", padx=(0, 20))
        ctk.CTkRadioButton(odeme_frame_p, text="Taksitli", variable=odeme_var_p, value="taksitli", command=toggle_popup_taksit).pack(side="left")

        ctk.CTkLabel(taksit_frame_p, text="Taksit Sayısı:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        e_ts = ctk.CTkEntry(taksit_frame_p, width=80)
        e_ts.insert(0, str(ts) if ts_int >= 2 else "")
        e_ts.grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkLabel(taksit_frame_p, text="Vade Farkı (TL):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        e_vf = ctk.CTkEntry(taksit_frame_p, width=80)
        e_vf.insert(0, str(vf))
        e_vf.grid(row=1, column=1, padx=10, pady=5)

        ctk.CTkLabel(taksit_frame_p, text="Ödenen Taksit:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        e_ot = ctk.CTkEntry(taksit_frame_p, width=80)
        e_ot.insert(0, str(ot))
        e_ot.grid(row=2, column=1, padx=10, pady=5)

        toggle_popup_taksit()

        def kaydet():
            k = e_kat.get().strip()
            a = e_ad.get().strip()
            f = e_fyt.get().strip()
            d = c_drm.get()
            l = e_link.get().strip()

            try:
                f_float = float(f.replace(',', '.'))

                if odeme_var_p.get() == "nakit":
                    ts_val = 0
                    vf_val = 0.0
                    ot_val = 0
                else:
                    ts_val = int(e_ts.get().strip())
                    vf_val = float(e_vf.get().strip().replace(',', '.'))
                    ot_val = int(e_ot.get().strip())
                    if ts_val < 2:
                        messagebox.showerror("Hata", "Taksit sayısı en az 2 olmalıdır!")
                        return

                database.urun_guncelle(uid, k, a, f_float, d, l, taksit_sayisi=ts_val, vade_farki=vf_val, odenen_taksit=ot_val)
                popup.destroy()
                self.load_treeview_data()
            except ValueError:
                messagebox.showerror("Hata", "Fiyat, Vade ve Taksit alanları sayısal olmalıdır.")

        ctk.CTkButton(popup, text="Güncelle", command=kaydet, fg_color="#F57C00", hover_color="#E65100").pack(pady=20)

    # ─── DASHBOARD ────────────────────────────────────────────────────

    def show_dashboard_frame(self):
        self.clear_main_frame()
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        lbl_baslik = ctk.CTkLabel(self.main_frame, text="📊 FİNANSAL DASHBOARD", font=ctk.CTkFont(size=24, weight="bold"), text_color="#FFCA28")
        lbl_baslik.grid(row=0, column=0, pady=10)

        gfx_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        gfx_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        # Bug 2 fix: database modülü üzerinden bağlantı
        con = database.get_connection()
        df = pd.read_sql("SELECT id, kategori, urun_adi, fiyat, durum, vade_farki FROM urunler", con)
        con.close()

        if df.empty:
            lbl_bos = ctk.CTkLabel(gfx_frame, text="Henüz analiz edilecek veri yok.", text_color="gray", font=ctk.CTkFont(size=14))
            lbl_bos.pack(pady=50)
            return

        try:
            df['vade_farki'] = df['vade_farki'].fillna(0.0)
            df['toplam_maliyet'] = df['fiyat'] + df['vade_farki']
            ozet = df.groupby('kategori')['toplam_maliyet'].sum()

            durumlar = df['durum'].str.upper().str.strip()
            df_harcanan = df[durumlar.isin(['E', 'EVET', 'ALINDI'])].copy()
            if not df_harcanan.empty:
                df_harcanan['toplam_maliyet'] = df_harcanan['fiyat'] + df_harcanan['vade_farki']
                df_harcanan['kumulatif'] = df_harcanan['toplam_maliyet'].cumsum()

            plt.style.use('dark_background')
            fig = Figure(figsize=(10, 5), facecolor="#2b2b2b")
            fig.subplots_adjust(wspace=0.3)

            ax1 = fig.add_subplot(121)
            ax2 = fig.add_subplot(122)
            ax2.set_facecolor("#1e1e1e")

            # Bug 10 fix: boş pie chart mesajı
            if ozet.sum() > 0:
                ax1.pie(ozet, labels=ozet.index, autopct='%1.1f%%', startangle=140, textprops={'color': "w"})
                ax1.set_title('Kategori Bazlı Toplam Harcama (Faiz Dahil)', color="white")
                ax1.axis('equal')
            else:
                ax1.text(0.5, 0.5, "Henüz harcama verisi yok", ha='center', va='center', color='gray', fontsize=12, transform=ax1.transAxes)
                ax1.set_title('Kategori Bazlı Toplam Harcama', color="white")

            if not df_harcanan.empty:
                ax2.plot(range(1, len(df_harcanan)+1), df_harcanan['kumulatif'], marker='o', color='#B39DDB', linewidth=2)
                ax2.set_title("Alınan Ürünler - Birikimli Finansman", color="white")
                ax2.set_xlabel("Alınan Parça Sırası", color="white")
                ax2.set_ylabel("Toplam Maliyet / Borç (TL)", color="white")
                ax2.grid(True, alpha=0.3)
            else:
                ax2.text(0.5, 0.5, "Henüz alınan ürün yok", ha='center', va='center', color='gray', fontsize=12, transform=ax2.transAxes)
                ax2.set_title("Alınan Ürünler - Birikimli Finansman", color="white")

            canvas = FigureCanvasTkAgg(fig, master=gfx_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        except Exception as e:
            ctk.CTkLabel(gfx_frame, text=f"Grafikler yüklenirken hata oluştu: {str(e)}").pack()

    # ─── YAPAY ZEKA ───────────────────────────────────────────────────

    def show_ai_frame(self):
        self.clear_main_frame()

        lbl_baslik = ctk.CTkLabel(self.main_frame, text="YAPAY ZEKA FİNANS DANIŞMANI", font=ctk.CTkFont(size=24, weight="bold"), text_color="#B39DDB")
        lbl_baslik.grid(row=0, column=0, pady=10, padx=20, sticky="w")

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

            # Bug 2 fix: database modülü üzerinden bağlantı
            con = database.get_connection()
            df = pd.read_sql("SELECT kategori, urun_adi, fiyat, durum FROM urunler", con)
            con.close()

            if df.empty:
                self._ai_yazdir("\n[!] Henüz hiç kayıt bulunmuyor.")
                return

            ozet = df.groupby('kategori')['fiyat'].sum()
            durumlar = df['durum'].str.upper().str.strip()
            harcanan = df[durumlar.isin(['E', 'EVET', 'ALINDI'])]['fiyat'].sum()
            bekleyen = df[~durumlar.isin(['E', 'EVET', 'ALINDI'])]['fiyat'].sum()

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

    # ─── SİSTEM AYARLARI ──────────────────────────────────────────────

    def show_ayarlar_frame(self):
        self.clear_main_frame()
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        lbl_baslik = ctk.CTkLabel(self.main_frame, text="SİSTEM AYARLARI VE GÜVENLİK", font=ctk.CTkFont(size=24, weight="bold"), text_color="#90CAF9")
        lbl_baslik.grid(row=0, column=0, pady=20)

        scroll = ctk.CTkScrollableFrame(self.main_frame, fg_color="#1E1E1E")
        scroll.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        kutu = scroll

        row_idx = 0

        # ── TEMA ──
        ctk.CTkLabel(kutu, text="Görsel Tema Seçimi:", font=ctk.CTkFont(weight="bold")).grid(row=row_idx, column=0, padx=20, pady=15, sticky="e")
        def change_theme(secim):
            if secim == "Karanlık Mod (Dark)": ctk.set_appearance_mode("Dark")
            else: ctk.set_appearance_mode("Light")
            settings = profile_manager.load_profile_settings(self.current_profile)
            settings["theme"] = "Dark" if "Dark" in secim else "Light"
            profile_manager.save_profile_settings(self.current_profile, settings)
        tema_menu = ctk.CTkOptionMenu(kutu, values=["Karanlık Mod (Dark)", "Aydınlık Mod (Light)"], command=change_theme)
        tema_menu.set("Karanlık Mod (Dark)" if ctk.get_appearance_mode() == "Dark" else "Aydınlık Mod (Light)")
        tema_menu.grid(row=row_idx, column=1, padx=20, pady=15, sticky="w")
        row_idx += 1

        # ── PIN DEĞİŞTİR ──
        ctk.CTkLabel(kutu, text="Yeni Uygulama Şifresi (PIN):", font=ctk.CTkFont(weight="bold")).grid(row=row_idx, column=0, padx=20, pady=15, sticky="e")
        e_yeni_pin = ctk.CTkEntry(kutu, width=150, show="*")
        e_yeni_pin.grid(row=row_idx, column=1, padx=20, pady=15, sticky="w")
        def degistir_pin():
            yeni = e_yeni_pin.get().strip()
            if len(yeni) < 4:
                messagebox.showwarning("Geçersiz", "Şifre en az 4 haneli olmalıdır.")
                return
            yeni_hash = hashlib.sha256(yeni.encode("utf-8")).hexdigest()
            settings = profile_manager.load_profile_settings(self.current_profile)
            settings["pin_hash"] = yeni_hash
            profile_manager.save_profile_settings(self.current_profile, settings)
            messagebox.showinfo("Başarılı", "Uygulama PIN kodunuz başarıyla değiştirildi!")
            e_yeni_pin.delete(0, 'end')
        ctk.CTkButton(kutu, text="PIN Değiştir", fg_color="#D84315", hover_color="#BF360C", width=120, command=degistir_pin).grid(row=row_idx, column=2, padx=10, pady=15, sticky="w")
        row_idx += 1

        # ── YEDEKLEME ──
        ctk.CTkLabel(kutu, text="Veritabanı Yedeği:", font=ctk.CTkFont(weight="bold")).grid(row=row_idx, column=0, padx=20, pady=15, sticky="e")
        def yedekle_simdi():
            if self.backup_manager:
                path = self.backup_manager.create_backup()
                if path:
                    messagebox.showinfo("Başarılı", f"Yedek alındı:\n{path}")
                else:
                    messagebox.showerror("Hata", "Yedekleme başarısız.")
        def yedekle_indir():
            kayit_yeri = filedialog.asksaveasfilename(defaultextension=".bak", initialfile="urun_takip_yedek.bak", title="Yedeği Nereye Kaydedelim?")
            if kayit_yeri:
                try:
                    shutil.copy2(database.DB_PATH, kayit_yeri)
                    messagebox.showinfo("Başarılı", f"Veritabanı kopyalandı:\n{kayit_yeri}")
                except Exception as e:
                    messagebox.showerror("Hata", f"Yedekleme başarısız:\n{str(e)}")

        yedek_frame = ctk.CTkFrame(kutu, fg_color="transparent")
        yedek_frame.grid(row=row_idx, column=1, columnspan=2, padx=10, pady=15, sticky="w")
        ctk.CTkButton(yedek_frame, text="💾 Yedeği İndir", fg_color="#00695C", hover_color="#004D40", width=120, command=yedekle_indir).pack(side="left", padx=5)
        ctk.CTkButton(yedek_frame, text="Şimdi Yedekle", fg_color="#1565C0", hover_color="#0D47A1", width=120, command=yedekle_simdi).pack(side="left", padx=5)
        row_idx += 1

        # Otomatik yedekleme ayarları
        settings = profile_manager.load_profile_settings(self.current_profile)
        backup_cfg = settings.get("backup", {})

        ctk.CTkLabel(kutu, text="Otomatik Yedekleme:", font=ctk.CTkFont(weight="bold")).grid(row=row_idx, column=0, padx=20, pady=10, sticky="e")

        auto_var = ctk.BooleanVar(value=backup_cfg.get("enabled", False))
        def toggle_auto_backup():
            s = profile_manager.load_profile_settings(self.current_profile)
            s["backup"]["enabled"] = auto_var.get()
            profile_manager.save_profile_settings(self.current_profile, s)
            if auto_var.get() and self.backup_manager:
                self.backup_manager.settings = s["backup"]
                self.backup_manager.start_scheduled()
            elif self.backup_manager:
                self.backup_manager.stop_scheduled()

        auto_frame = ctk.CTkFrame(kutu, fg_color="transparent")
        auto_frame.grid(row=row_idx, column=1, columnspan=2, padx=10, pady=10, sticky="w")
        ctk.CTkSwitch(auto_frame, text="Etkin", variable=auto_var, command=toggle_auto_backup).pack(side="left", padx=5)

        interval_var = ctk.StringVar(value={"daily": "Günlük", "weekly": "Haftalık", "monthly": "Aylık"}.get(backup_cfg.get("interval", "weekly"), "Haftalık"))
        def set_interval(val):
            mapping = {"Günlük": "daily", "Haftalık": "weekly", "Aylık": "monthly"}
            s = profile_manager.load_profile_settings(self.current_profile)
            s["backup"]["interval"] = mapping.get(val, "weekly")
            profile_manager.save_profile_settings(self.current_profile, s)
        ctk.CTkOptionMenu(auto_frame, values=["Günlük", "Haftalık", "Aylık"], variable=interval_var, command=set_interval, width=100).pack(side="left", padx=5)

        last_backup = self.backup_manager.get_last_backup_time() if self.backup_manager else "?"
        ctk.CTkLabel(auto_frame, text=f"Son: {last_backup}", text_color="gray", font=ctk.CTkFont(size=11)).pack(side="left", padx=10)
        row_idx += 1

        # ── PROGRAMI KALDIR ──
        try:
            import installer
            installer.show_uninstall_button_in_app(kutu, self)
        except Exception:
            pass

        # ── BİLDİRİM AYARLARI ──
        ctk.CTkLabel(kutu, text="─── Bildirim Ayarları ───", font=ctk.CTkFont(size=14, weight="bold"), text_color="#FFB74D").grid(row=row_idx, column=0, columnspan=3, pady=(20, 10))
        row_idx += 1

        notif = settings.get("notifications", {})

        ctk.CTkLabel(kutu, text="Aylık Bütçe Limiti (TL):", font=ctk.CTkFont(weight="bold")).grid(row=row_idx, column=0, padx=20, pady=10, sticky="e")
        e_budget = ctk.CTkEntry(kutu, width=150)
        e_budget.insert(0, str(settings.get("monthly_budget", 0)))
        e_budget.grid(row=row_idx, column=1, padx=20, pady=10, sticky="w")
        def save_budget():
            try:
                val = float(e_budget.get().strip().replace(',', '.'))
                s = profile_manager.load_profile_settings(self.current_profile)
                s["monthly_budget"] = val
                profile_manager.save_profile_settings(self.current_profile, s)
                messagebox.showinfo("Başarılı", f"Aylık bütçe limiti: {val:.0f} TL")
            except ValueError:
                messagebox.showerror("Hata", "Geçerli bir sayı girin.")
        ctk.CTkButton(kutu, text="Kaydet", fg_color="#1B5E20", width=80, command=save_budget).grid(row=row_idx, column=2, padx=10, pady=10, sticky="w")
        row_idx += 1

        notif_items = [
            ("Taksit Hatırlatıcısı:", "taksit_reminder"),
            ("Bütçe Uyarısı (%80):", "budget_warning"),
            ("Aylık Özet Bildirimi:", "monthly_summary"),
        ]
        for label_text, key in notif_items:
            ctk.CTkLabel(kutu, text=label_text, font=ctk.CTkFont(weight="bold")).grid(row=row_idx, column=0, padx=20, pady=8, sticky="e")
            var = ctk.BooleanVar(value=notif.get(key, True))
            def make_toggle(k, v):
                def toggle():
                    s = profile_manager.load_profile_settings(self.current_profile)
                    s["notifications"][k] = v.get()
                    profile_manager.save_profile_settings(self.current_profile, s)
                return toggle
            ctk.CTkSwitch(kutu, text="", variable=var, command=make_toggle(key, var)).grid(row=row_idx, column=1, padx=20, pady=8, sticky="w")
            row_idx += 1

        # ── PROFİL YÖNETİMİ ──
        ctk.CTkLabel(kutu, text="─── Profil Yönetimi ───", font=ctk.CTkFont(size=14, weight="bold"), text_color="#81D4FA").grid(row=row_idx, column=0, columnspan=3, pady=(20, 10))
        row_idx += 1

        ctk.CTkLabel(kutu, text=f"Aktif Profil: {self.current_profile}", font=ctk.CTkFont(weight="bold")).grid(row=row_idx, column=0, padx=20, pady=10, sticky="e")
        prof_btn_frame = ctk.CTkFrame(kutu, fg_color="transparent")
        prof_btn_frame.grid(row=row_idx, column=1, columnspan=2, padx=10, pady=10, sticky="w")

        def profil_degistir():
            if self.backup_manager: self.backup_manager.stop_scheduled()
            if self.notification_manager: self.notification_manager.stop_periodic_checks()
            if self.price_tracker: self.price_tracker.stop_periodic_checks()
            self.withdraw()
            self.show_login_screen()

        def profil_sil():
            try:
                profiles = profile_manager.list_profiles()
                if len(profiles) <= 1:
                    messagebox.showwarning("Uyarı", "Son kalan profil silinemez.")
                    return
                onay = messagebox.askyesno("Onay", f"'{self.current_profile}' profilini silmek istediğinize emin misiniz?\nTüm veriler silinecek!")
                if onay:
                    profile_manager.delete_profile(self.current_profile)
                    profil_degistir()
            except ValueError as ve:
                messagebox.showerror("Hata", str(ve))

        ctk.CTkButton(prof_btn_frame, text="Profil Değiştir", fg_color="#455A64", width=120, command=profil_degistir).pack(side="left", padx=5)
        ctk.CTkButton(prof_btn_frame, text="Profili Sil", fg_color="#B71C1C", hover_color="#7F0000", width=100, command=profil_sil).pack(side="left", padx=5)
        row_idx += 1

        # ── API KEY ──
        ctk.CTkLabel(kutu, text="─── Yapay Zeka Ayarları ───", font=ctk.CTkFont(size=14, weight="bold"), text_color="#B39DDB").grid(row=row_idx, column=0, columnspan=3, pady=(20, 10))
        row_idx += 1

        ctk.CTkLabel(kutu, text="Google Gemini AI API Key:", font=ctk.CTkFont(weight="bold")).grid(row=row_idx, column=0, padx=20, pady=15, sticky="e")
        e_api_key = ctk.CTkEntry(kutu, width=250, show="*")
        mevcut_key = os.getenv("GEMINI_API_KEY", "")
        e_api_key.insert(0, mevcut_key)
        e_api_key.grid(row=row_idx, column=1, padx=20, pady=15, sticky="w")
        def set_api():
            nk = e_api_key.get().strip()
            os.environ["GEMINI_API_KEY"] = nk
            env_file = os.path.join(profile_manager.get_base_dir(), ".env")
            if not os.path.exists(env_file):
                open(env_file, 'a').close()
            set_key(env_file, "GEMINI_API_KEY", nk)
            messagebox.showinfo("Başarılı", "API Anahtarı başarıyla güncellendi!")
        def clear_api():
            e_api_key.delete(0, 'end')
            os.environ["GEMINI_API_KEY"] = ""
            env_file = os.path.join(profile_manager.get_base_dir(), ".env")
            if os.path.exists(env_file):
                set_key(env_file, "GEMINI_API_KEY", "")
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
        api_btn_frame.grid(row=row_idx, column=2, padx=10, sticky="w")
        ctk.CTkButton(api_btn_frame, text="Kaydet", fg_color="#1B5E20", hover_color="#003300", width=60, command=set_api).pack(side="left", padx=5)
        ctk.CTkButton(api_btn_frame, text="Temizle", fg_color="#B71C1C", hover_color="#7F0000", width=60, command=clear_api).pack(side="left", padx=5)
        ctk.CTkButton(api_btn_frame, text="ℹ️ Nasıl Alınır?", fg_color="#0D47A1", hover_color="#01579B", width=100, command=api_yardim).pack(side="left", padx=5)

    # ─── WEB'DEN BUL ──────────────────────────────────────────────────

    def show_web_frame(self):
        self.clear_main_frame()
        self.main_frame.grid_rowconfigure(3, weight=1)
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

        btn_takip = ctk.CTkButton(btn_frame, text="🔔 Fiyat Takip Et", fg_color="#E65100", hover_color="#BF360C", command=self.web_fiyat_takip_ekle)
        btn_takip.pack(side="left", padx=10)

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
                sonuclar, hatalar = web_scraper.urun_ara(kelime, mode=mod)
                def ekrana_bas():
                    if not sonuclar and hatalar:
                        self.lbl_web_durum.configure(text=f"Sonuç bulunamadı: {' | '.join(hatalar)}", text_color="#FF5252")
                        return
                    elif not sonuclar:
                        self.lbl_web_durum.configure(text="Sonuç bulunamadı.", text_color="yellow")
                        return
                    for s in sonuclar:
                        self.tree_web.insert("", "end", values=(s['platform'], s['baslik'], f"{s['fiyat']:.2f}", s['link']))
                    durum_txt = f"✅ {len(sonuclar)} sonuç listelendi. (Ucuzdan pahalıya)"
                    if hatalar:
                        durum_txt += f"  |  ⚠️ {' | '.join(hatalar)}"
                    self.lbl_web_durum.configure(text=durum_txt, text_color="#64DD17")
                self.after(0, ekrana_bas)
            except Exception as e:
                def hata_bas():
                    hmesaj = str(e)[:200]
                    messagebox.showerror("Arama Hatası", hmesaj)
                    self.lbl_web_durum.configure(text="❌ Arama motoru hatası. Lütfen uyarılara bakın.", text_color="#FF5252")
                self.after(0, hata_bas)
            # Bug 4 fix: finally ile status reset
            finally:
                def reset_durum():
                    try:
                        current = self.lbl_web_durum.cget("text")
                        if "Aranıyor" in current:
                            self.lbl_web_durum.configure(text="Arama tamamlandı.", text_color="yellow")
                    except Exception:
                        pass
                self.after(0, reset_durum)

        threading.Thread(target=fetch, daemon=True).start()

    def web_linke_git(self):
        selected = self.tree_web.selection()
        if not selected:
            return
        link = self.tree_web.item(selected[0])['values'][3]
        if link: webbrowser.open(link)

    def web_db_ekle(self):
        """Bug 7 fix: Hızlı Kayıt popup'ına durum ve taksit desteği eklendi."""
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
        popup.geometry("380x420")
        popup.transient(self)
        popup.grab_set()

        ctk.CTkLabel(popup, text=f"Seçilen Ürün:\n{ad[:40]}...", font=ctk.CTkFont(weight="bold")).pack(pady=10)

        ctk.CTkLabel(popup, text="Kategori:").pack(pady=3)
        rows = database.urunleri_getir()
        kategoriler = list(set([r[1] for r in rows]))
        if not kategoriler:
            kategoriler = ["Elektronik", "Giyim", "Market", "Diğer"]
        c_kat = ctk.CTkComboBox(popup, values=kategoriler, width=200)
        c_kat.pack(pady=3)

        ctk.CTkLabel(popup, text="Durum:").pack(pady=3)
        c_drm = ctk.CTkOptionMenu(popup, values=["Hayır", "Evet"], width=200)
        c_drm.pack(pady=3)

        odeme_var = ctk.StringVar(value="nakit")
        odeme_frame = ctk.CTkFrame(popup, fg_color="transparent")
        odeme_frame.pack(pady=5)
        taksit_frame = ctk.CTkFrame(popup, fg_color="transparent")

        def toggle():
            if odeme_var.get() == "taksitli":
                taksit_frame.pack(pady=3)
            else:
                taksit_frame.pack_forget()

        ctk.CTkRadioButton(odeme_frame, text="Nakit", variable=odeme_var, value="nakit", command=toggle).pack(side="left", padx=5)
        ctk.CTkRadioButton(odeme_frame, text="Taksitli", variable=odeme_var, value="taksitli", command=toggle).pack(side="left", padx=5)

        e_ts = ctk.CTkEntry(taksit_frame, width=80, placeholder_text="Taksit")
        e_ts.pack(side="left", padx=5)
        e_vf = ctk.CTkEntry(taksit_frame, width=80, placeholder_text="Vade TL")
        e_vf.pack(side="left", padx=5)

        def kaydet():
            k = c_kat.get().strip()
            if not k:
                k = "Diğer"
            d = c_drm.get()
            ts = 0
            vf = 0.0
            if odeme_var.get() == "taksitli":
                try:
                    ts = int(e_ts.get().strip()) if e_ts.get().strip() else 2
                    vf = float(e_vf.get().strip().replace(',', '.')) if e_vf.get().strip() else 0.0
                except ValueError:
                    pass
            database.urun_ekle(k, ad, fyt, d, link, taksit_sayisi=ts, vade_farki=vf)
            popup.destroy()
            messagebox.showinfo("Başarılı", f"{ad[:30]}...\n\nSisteminize başarıyla kaydedildi!")

        ctk.CTkButton(popup, text="Sisteme Kaydet", fg_color="#1B5E20", command=kaydet).pack(pady=15)

    def web_fiyat_takip_ekle(self):
        """Web sonuçlarından fiyat takibi ekle."""
        selected = self.tree_web.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen takip etmek istediğiniz ürünü seçin.")
            return

        val = self.tree_web.item(selected[0])['values']
        ad = str(val[1])
        fyt = float(str(val[2]))
        link = str(val[3])
        platform = str(val[0])

        popup = ctk.CTkToplevel(self)
        popup.title("Fiyat Takibi Ekle")
        popup.geometry("380x250")
        popup.transient(self)
        popup.grab_set()

        ctk.CTkLabel(popup, text=f"Ürün: {ad[:40]}...", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        ctk.CTkLabel(popup, text=f"Mevcut Fiyat: {fyt:.2f} TL | Platform: {platform}").pack(pady=5)

        ctk.CTkLabel(popup, text="Hedef Fiyat (TL):").pack(pady=5)
        e_hedef = ctk.CTkEntry(popup, width=150)
        e_hedef.insert(0, f"{fyt * 0.9:.2f}")
        e_hedef.pack(pady=5)

        def ekle():
            try:
                hedef = float(e_hedef.get().strip().replace(',', '.'))
                if self.price_tracker:
                    self.price_tracker.add_tracking(link, ad, platform, hedef, fyt)
                    popup.destroy()
                    messagebox.showinfo("Başarılı", f"Fiyat takibi başlatıldı!\nHedef: {hedef:.2f} TL")
            except ValueError:
                messagebox.showerror("Hata", "Geçerli bir fiyat girin.", parent=popup)

        ctk.CTkButton(popup, text="Takibe Başla", fg_color="#E65100", command=ekle).pack(pady=15)

    # ─── FİYAT TAKİP FRAME ───────────────────────────────────────────

    def show_fiyat_takip_frame(self):
        self.clear_main_frame()
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.main_frame, text="FİYAT TAKİP ALARMI", font=ctk.CTkFont(size=24, weight="bold"), text_color="#FF9800").grid(row=0, column=0, pady=10)

        # Yeni takip ekleme
        ekle_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        ekle_frame.grid(row=1, column=0, pady=10, padx=20, sticky="ew")

        ctk.CTkLabel(ekle_frame, text="URL:").pack(side="left", padx=3)
        e_url = ctk.CTkEntry(ekle_frame, width=200, placeholder_text="Ürün linki")
        e_url.pack(side="left", padx=3)

        ctk.CTkLabel(ekle_frame, text="Ad:").pack(side="left", padx=3)
        e_ad = ctk.CTkEntry(ekle_frame, width=130, placeholder_text="Ürün adı")
        e_ad.pack(side="left", padx=3)

        ctk.CTkLabel(ekle_frame, text="Platform:").pack(side="left", padx=3)
        c_plat = ctk.CTkOptionMenu(ekle_frame, values=["Trendyol", "N11", "Diğer"], width=90)
        c_plat.pack(side="left", padx=3)

        ctk.CTkLabel(ekle_frame, text="Hedef TL:").pack(side="left", padx=3)
        e_hedef = ctk.CTkEntry(ekle_frame, width=70)
        e_hedef.pack(side="left", padx=3)

        def ekle():
            url = e_url.get().strip()
            ad = e_ad.get().strip()
            platform = c_plat.get()
            try:
                hedef = float(e_hedef.get().strip().replace(',', '.'))
            except ValueError:
                messagebox.showerror("Hata", "Geçerli bir hedef fiyat girin.")
                return
            if not url or not ad:
                messagebox.showwarning("Uyarı", "URL ve ürün adı gerekli.")
                return
            if self.price_tracker:
                self.price_tracker.add_tracking(url, ad, platform, hedef)
            load_takip_data()
            e_url.delete(0, 'end')
            e_ad.delete(0, 'end')
            e_hedef.delete(0, 'end')

        ctk.CTkButton(ekle_frame, text="Ekle", width=60, fg_color="#E65100", command=ekle).pack(side="left", padx=5)

        # Tablo
        style = ttk.Style()
        tree_ft = ttk.Treeview(self.main_frame, columns=("ID", "Ürün", "Platform", "Hedef", "Mevcut", "Son Kontrol", "Durum"), show="headings", height=12)
        tree_ft.heading("ID", text="ID")
        tree_ft.heading("Ürün", text="Ürün Adı")
        tree_ft.heading("Platform", text="Platform")
        tree_ft.heading("Hedef", text="Hedef (TL)")
        tree_ft.heading("Mevcut", text="Mevcut (TL)")
        tree_ft.heading("Son Kontrol", text="Son Kontrol")
        tree_ft.heading("Durum", text="Durum")

        tree_ft.column("ID", width=30, anchor="center")
        tree_ft.column("Ürün", width=200, anchor="w")
        tree_ft.column("Platform", width=80, anchor="center")
        tree_ft.column("Hedef", width=80, anchor="e")
        tree_ft.column("Mevcut", width=80, anchor="e")
        tree_ft.column("Son Kontrol", width=120, anchor="center")
        tree_ft.column("Durum", width=80, anchor="center")
        tree_ft.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        tree_ft.tag_configure("ucuz", background="#1B5E20")
        tree_ft.tag_configure("pahali", background="#B71C1C")
        tree_ft.tag_configure("bekliyor", background="#37474F")

        def load_takip_data():
            for item in tree_ft.get_children():
                tree_ft.delete(item)
            try:
                items = database.takip_listele(sadece_aktif=False)
                for row in items:
                    tid, url, ad, plat, hedef, mevcut, son, aktif = row
                    if not aktif:
                        durum = "Durduruldu"
                        tag = "bekliyor"
                    elif mevcut > 0 and mevcut <= hedef:
                        durum = "Hedefe Ulaştı!"
                        tag = "ucuz"
                    elif mevcut > 0:
                        durum = "Takipte"
                        tag = "pahali"
                    else:
                        durum = "Bekleniyor"
                        tag = "bekliyor"
                    tree_ft.insert("", "end", values=(tid, ad[:40], plat, f"{hedef:.2f}", f"{mevcut:.2f}" if mevcut > 0 else "-", son or "-", durum), tags=(tag,))
            except Exception:
                pass

        # İşlem butonları
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.grid(row=3, column=0, pady=10)

        def kontrol_et():
            if self.price_tracker:
                def run():
                    self.price_tracker.check_all_tracked_items()
                    self.after(0, load_takip_data)
                threading.Thread(target=run, daemon=True).start()
                messagebox.showinfo("Bilgi", "Fiyat kontrolü başlatıldı...")

        def takip_sil():
            sel = tree_ft.selection()
            if not sel: return
            tid = tree_ft.item(sel[0])['values'][0]
            database.takip_sil(tid)
            load_takip_data()

        def takip_duraklat():
            sel = tree_ft.selection()
            if not sel: return
            tid = tree_ft.item(sel[0])['values'][0]
            database.takip_duraklat(tid, False)
            load_takip_data()

        def takip_devam():
            sel = tree_ft.selection()
            if not sel: return
            tid = tree_ft.item(sel[0])['values'][0]
            database.takip_duraklat(tid, True)
            load_takip_data()

        ctk.CTkButton(btn_frame, text="Şimdi Kontrol Et", fg_color="#1565C0", command=kontrol_et).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Durdur", fg_color="#F57C00", command=takip_duraklat).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Devam Ettir", fg_color="#2E7D32", command=takip_devam).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Sil", fg_color="#B71C1C", command=takip_sil).pack(side="left", padx=5)

        load_takip_data()


if __name__ == "__main__":
    import sys
    import installer

    if "--uninstall" in sys.argv:
        installer.baslat_kaldir_modu()
        sys.exit(0)

    if getattr(sys, 'frozen', False) and installer.should_show_installer():
        installer.baslat_kurulum_modu()
        sys.exit(0)

    app = App()
    app.mainloop()
