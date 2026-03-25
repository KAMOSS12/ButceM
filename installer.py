"""
BütçeM - Profesyonel Kurulum Sihirbazı & Kaldırma Sistemi
4 adımlı wizard: Hoş Geldiniz → Dizin & Seçenekler → Kurulum İlerlemesi → Tamamlandı
"""

import os
import sys
import shutil
import subprocess
import threading
import datetime

APP_NAME = "BütçeM"
APP_VERSION = "2.2.0"
APP_PUBLISHER = "BütçeM"
REGISTRY_KEY = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\ButceM"
REQUIRED_SPACE_MB = 200  # Minimum disk alanı (MB)


def _get_icon_path():
    """Frozen exe içindeki logo.ico yolunu döndür."""
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, "logo.ico")
    return os.path.join(os.path.dirname(__file__), "logo.ico")


def should_show_installer():
    """Kurulum sihirbazının gösterilip gösterilmeyeceğini belirle."""
    if not getattr(sys, 'frozen', False):
        return False
    current_dir = os.path.dirname(os.path.abspath(sys.executable))
    marker = os.path.join(current_dir, ".butcem_installed")
    dir_name = os.path.basename(current_dir).lower()
    return dir_name != "butcem" and not os.path.exists(marker)


def _kilavuz_metni():
    return """-----------------------------------------------------------
          BütçeM - A'DAN Z'YE KULLANIM KILAVUZU
-----------------------------------------------------------

Hoş Geldiniz! Bu uygulama finansal alımlarınızı, bütçenizi ve e-ticaret
araştırmalarınızı tek bir ekranda birleştiren kapsamlı bir araçtır.

1. İLK GİRİŞ VE PROFİL SEÇİMİ
- Programa her girişinizde önce profil seçimi, ardından güvenlik şifresi (PIN) istenir.
- İlk kurulumda "varsayilan" profili otomatik oluşturulur. Şifre: 1234
- Birden fazla profil oluşturabilirsiniz (her profil kendi veritabanına sahiptir).
- Profil oluşturma ve yönetim: Sistem Ayarları > Profil Yönetimi

2. ÜRÜN EKLEME (TAKSİT VE VADE FARKI)
- Sol menüden "Parça Ekle" butonunu kullanın.
- Ürün adı, Fiyat, Kategori ve İsteğe Bağlı olarak Ürün Linkini ekleyebilirsiniz.
- Taksitli bir harcama ise taksit sayısını ve eklenecek vade farkını (faiz) belirtebilirsiniz.

3. LİSTELEME, GÜNCELLEME VE EXCEL
- "Liste & Düzenle" sekmesinde verilerinizi Kategori veya İsme göre süzebilirsiniz.
- Bir ürünü düzenlemek için üzerine çift tıklamanız yeterlidir.
- Kolon başlıklarına tıklayarak sıralama yapabilirsiniz.
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
- Ayrıca "Fiyat Takip Et" ile ürünün fiyatını otomatik izlemeye alabilirsiniz.

6. FİYAT TAKİP ALARMI
- "Fiyat Takip" sekmesinde e-ticaret ürünlerinin fiyatını periyodik olarak kontrol edebilirsiniz.
- Hedef fiyat belirleyin, fiyat düştüğünde masaüstü bildirimi alın.
- URL + ürün adı + platform + hedef fiyat girerek yeni takip başlatın.
- 6 saatte bir otomatik fiyat kontrolü yapılır.

7. OTOMATİK YEDEKLEME
- Sistem Ayarları > Yedekleme bölümünden otomatik yedeklemeyi açabilirsiniz.
- Günlük, haftalık veya aylık aralıklarla veritabanınız yedeklenir.
- "Şimdi Yedekle" ile anlık yedek alabilir, eski yedekleri geri yükleyebilirsiniz.

8. BİLDİRİMLER
- Sistem Ayarları > Bildirim Ayarları'ndan taksit hatırlatma, bütçe uyarısı
  ve aylık özet bildirimlerini açıp kapatabilirsiniz.
- Aylık bütçe limiti belirleyin, %80'e ulaşıldığında uyarı, aşıldığında alarm alın.
- Uygulama açılışında ödenmemiş taksitler için hatırlatma bildirimi gelir.

Geliştirici Sürümü: V2.2 - Tüm Hakları Saklıdır.
-----------------------------------------------------------"""


# ─── REGISTRY (Programlar ve Özellikler) ──────────────────────────────

def _register_program(install_dir, exe_path):
    """Windows 'Programlar ve Özellikler' listesine kayıt yaz (HKCU, admin gerekmez)."""
    try:
        import winreg
        key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, REGISTRY_KEY, 0, winreg.KEY_WRITE)
        size_kb = 0
        try:
            size_kb = os.path.getsize(exe_path) // 1024
        except OSError:
            pass
        values = {
            "DisplayName": APP_NAME,
            "DisplayVersion": APP_VERSION,
            "Publisher": APP_PUBLISHER,
            "InstallLocation": install_dir,
            "DisplayIcon": f"{exe_path},0",
            "UninstallString": f'"{exe_path}" --uninstall',
            "EstimatedSize": size_kb,
            "NoModify": 1,
            "NoRepair": 1,
        }
        for name, value in values.items():
            reg_type = winreg.REG_DWORD if isinstance(value, int) else winreg.REG_SZ
            winreg.SetValueEx(key, name, 0, reg_type, value)
        winreg.CloseKey(key)
    except Exception:
        pass  # Registry yazılamadıysa kuruluma devam et


def _unregister_program():
    """Registry kaydını sil."""
    try:
        import winreg
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY)
    except Exception:
        pass


# ─── KISAYOL OLUŞTURMA ───────────────────────────────────────────────

def _create_shortcuts(install_dir, target_path, desktop=True, startmenu=True):
    """VBScript ile masaüstü ve/veya başlat menüsü kısayolu oluştur (ikonlu)."""
    vbs_lines = ['Set oWS = WScript.CreateObject("WScript.Shell")']
    icon_path = os.path.join(install_dir, "logo.ico")
    # logo.ico yoksa exe ikonunu kullan
    icon_loc = f'"{icon_path}"' if os.path.exists(icon_path) else f'"{target_path},0"'

    if desktop:
        desktop_dir = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop")
        lnk = os.path.join(desktop_dir, "BütçeM.lnk")
        vbs_lines += [
            f'Set oLink1 = oWS.CreateShortcut("{lnk}")',
            f'oLink1.TargetPath = "{target_path}"',
            f'oLink1.WorkingDirectory = "{install_dir}"',
            f'oLink1.IconLocation = {icon_loc}',
            'oLink1.Save',
        ]

    if startmenu:
        appdata = os.getenv("APPDATA") or os.path.expanduser("~")
        programs = os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs")
        lnk = os.path.join(programs, "BütçeM.lnk")
        vbs_lines += [
            f'Set oLink2 = oWS.CreateShortcut("{lnk}")',
            f'oLink2.TargetPath = "{target_path}"',
            f'oLink2.WorkingDirectory = "{install_dir}"',
            f'oLink2.IconLocation = {icon_loc}',
            'oLink2.Save',
        ]

    if len(vbs_lines) <= 1:
        return  # Hiç kısayol seçilmemişse

    vbs_path = os.path.join(install_dir, "_create_shortcuts.vbs")
    with open(vbs_path, "w", encoding="utf-16-le") as f:
        f.write("\ufeff" + "\n".join(vbs_lines))
    subprocess.call(['cscript', '//nologo', vbs_path], creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        os.remove(vbs_path)
    except OSError:
        pass


def _delete_shortcuts():
    """Kısayolları sil."""
    desktop_lnk = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop", "BütçeM.lnk")
    appdata = os.getenv("APPDATA") or os.path.expanduser("~")
    startmenu_lnk = os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs", "BütçeM.lnk")
    for p in [desktop_lnk, startmenu_lnk]:
        try:
            if os.path.exists(p):
                os.remove(p)
        except OSError:
            pass


# ─── KURULUM GÜNLÜĞÜ ─────────────────────────────────────────────────

def _write_install_log(install_dir, options):
    """Kurulum günlüğü yaz."""
    log_path = os.path.join(install_dir, "install_log.txt")
    try:
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"BütçeM Kurulum Günlüğü\n")
            f.write(f"{'='*50}\n")
            f.write(f"Tarih        : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Sürüm        : {APP_VERSION}\n")
            f.write(f"Hedef Dizin   : {install_dir}\n")
            f.write(f"Masaüstü      : {'Evet' if options.get('desktop') else 'Hayır'}\n")
            f.write(f"Başlat Menüsü : {'Evet' if options.get('startmenu') else 'Hayır'}\n")
            f.write(f"Prog. Listesi : {'Evet' if options.get('registry') else 'Hayır'}\n")
            f.write(f"Durum         : Başarılı\n")
    except OSError:
        pass


# ─── DİSK ALANI KONTROLÜ ─────────────────────────────────────────────

def _check_disk_space(path):
    """Hedef yoldaki boş disk alanını MB cinsinden döndür. Hata varsa -1."""
    try:
        drive = os.path.splitdrive(path)[0] or path
        if not os.path.exists(drive + "\\"):
            drive = "C:"
        usage = shutil.disk_usage(drive + "\\")
        return usage.free // (1024 * 1024)
    except Exception:
        return -1


# ─── 4 ADIMLI KURULUM SİHİRBAZI ──────────────────────────────────────

def baslat_kurulum_modu():
    """Ana kurulum sihirbazı giriş noktası."""
    import customtkinter as ctk
    from tkinter import messagebox, filedialog

    kur_app = ctk.CTk()
    kur_app.title("BütçeM - Kurulum Sihirbazı")
    kur_app.geometry("600x500")
    kur_app.resizable(False, False)
    kur_app.eval('tk::PlaceWindow . center')

    icon_path = _get_icon_path()
    if os.path.exists(icon_path):
        kur_app.iconbitmap(icon_path)

    # ── Durum değişkenleri ──
    current_step = [0]
    appdata_def = os.path.join(os.getenv("APPDATA") or os.path.expanduser("~"), "ButceM")

    frames = {}          # Adım frame'leri
    step_labels = []     # Üst bar etiketleri
    e_path = [None]      # Yol entry referansı
    var_desktop = ctk.BooleanVar(value=True)
    var_startmenu = ctk.BooleanVar(value=True)
    var_registry = ctk.BooleanVar(value=True)
    var_launch = ctk.BooleanVar(value=True)
    disk_label = [None]
    btn_install = [None]
    progress_bar = [None]
    status_label = [None]

    # ── ÜST ADIM BARI ──
    top_bar = ctk.CTkFrame(kur_app, height=50, fg_color=("#E3F2FD", "#1A237E"))
    top_bar.pack(fill="x")
    top_bar.pack_propagate(False)

    step_names = ["Hoş Geldiniz", "Dizin & Seçenekler", "Kurulum", "Tamamlandı"]
    for i, name in enumerate(step_names):
        lbl = ctk.CTkLabel(top_bar, text=f"  {i+1}. {name}  ",
                           font=ctk.CTkFont(size=13),
                           text_color=("gray50", "gray60"))
        lbl.pack(side="left", padx=8, pady=10)
        step_labels.append(lbl)

    # ── İÇERİK ALANI ──
    content = ctk.CTkFrame(kur_app, fg_color="transparent")
    content.pack(fill="both", expand=True, padx=20, pady=10)

    # ── ALT BUTON BARI ──
    bottom = ctk.CTkFrame(kur_app, fg_color="transparent", height=50)
    bottom.pack(fill="x", padx=20, pady=(0, 15))

    btn_back = ctk.CTkButton(bottom, text="< Geri", width=100, state="disabled",
                             fg_color="gray40", hover_color="gray30")
    btn_back.pack(side="left")

    btn_next = ctk.CTkButton(bottom, text="Devam >", width=100,
                             fg_color="#1565C0", hover_color="#0D47A1")
    btn_next.pack(side="right")

    btn_cancel = ctk.CTkButton(bottom, text="İptal", width=80,
                               fg_color="#B71C1C", hover_color="#7F0000",
                               command=lambda: kur_app.destroy())
    btn_cancel.pack(side="right", padx=10)

    # ── ADIM 0: HOŞ GELDİNİZ ──
    def build_step0():
        f = ctk.CTkFrame(content, fg_color="transparent")

        # Logo
        logo_path = _get_icon_path()
        if os.path.exists(logo_path):
            try:
                from PIL import Image
                img = Image.open(logo_path)
                img = img.resize((80, 80), Image.LANCZOS)
                photo = ctk.CTkImage(light_image=img, dark_image=img, size=(80, 80))
                ctk.CTkLabel(f, image=photo, text="").pack(pady=(20, 10))
            except Exception:
                ctk.CTkLabel(f, text="[BütçeM]", font=ctk.CTkFont(size=28, weight="bold"),
                             text_color="#2196F3").pack(pady=(20, 10))
        else:
            ctk.CTkLabel(f, text="[BütçeM]", font=ctk.CTkFont(size=28, weight="bold"),
                         text_color="#2196F3").pack(pady=(20, 10))

        ctk.CTkLabel(f, text=f"{APP_NAME} v{APP_VERSION}",
                     font=ctk.CTkFont(size=24, weight="bold"),
                     text_color="#2196F3").pack(pady=(5, 5))

        ctk.CTkLabel(f, text="Kişisel Bütçe & Harcama Takip Uygulaması",
                     font=ctk.CTkFont(size=14),
                     text_color="gray").pack(pady=5)

        desc = (
            "Bu sihirbaz uygulamayı bilgisayarınıza kuracaktır.\n\n"
            "Kurulum sırasında yapılacak işlemler:\n"
            "  - Uygulama dosyası seçtiğiniz dizine kopyalanır\n"
            "  - Masaüstü ve Başlat menüsü kısayolları oluşturulur\n"
            "  - Kullanım kılavuzu oluşturulur\n"
            "  - Windows program listesine kayıt yapılır\n\n"
            "Devam etmek için 'Devam' butonuna tıklayın."
        )
        ctk.CTkLabel(f, text=desc, font=ctk.CTkFont(size=13),
                     justify="left", anchor="w").pack(pady=15, padx=20, fill="x")

        return f

    # ── ADIM 1: DİZİN & SEÇENEKLER ──
    def build_step1():
        f = ctk.CTkFrame(content, fg_color="transparent")

        ctk.CTkLabel(f, text="Kurulum Dizini",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#2196F3").pack(pady=(15, 10), anchor="w")

        path_frame = ctk.CTkFrame(f, fg_color="transparent")
        path_frame.pack(fill="x", pady=5)

        entry = ctk.CTkEntry(path_frame, width=380, height=35)
        entry.pack(side="left", padx=(0, 10))
        entry.insert(0, appdata_def)
        e_path[0] = entry

        def sec_dizin():
            d = filedialog.askdirectory(title="Kurulum Klasörünü Seçin",
                                        initialdir=os.path.dirname(appdata_def))
            if d:
                hedef = os.path.join(d, "ButceM") if not d.lower().endswith("butcem") else d
                entry.delete(0, 'end')
                entry.insert(0, hedef)
                update_disk_info()

        ctk.CTkButton(path_frame, text="Gözat...", width=90, height=35,
                      command=sec_dizin).pack(side="left")

        # Disk alanı bilgisi
        disk_lbl = ctk.CTkLabel(f, text="", font=ctk.CTkFont(size=12))
        disk_lbl.pack(pady=(5, 10), anchor="w")
        disk_label[0] = disk_lbl

        def update_disk_info(*_):
            path = entry.get().strip()
            free_mb = _check_disk_space(path)
            if free_mb < 0:
                disk_lbl.configure(text="Disk alanı okunamadı", text_color="gray")
                btn_install[0] = True  # İzin ver
            elif free_mb < REQUIRED_SPACE_MB:
                disk_lbl.configure(
                    text=f"Yetersiz disk alanı! Boş: {free_mb} MB / Gerekli: {REQUIRED_SPACE_MB} MB",
                    text_color="#F44336")
                btn_install[0] = False
            else:
                disk_lbl.configure(
                    text=f"Kullanılabilir alan: {free_mb:,} MB",
                    text_color="#4CAF50")
                btn_install[0] = True

        entry.bind("<KeyRelease>", update_disk_info)
        update_disk_info()

        # Seçenekler
        ctk.CTkLabel(f, text="Kurulum Seçenekleri",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#2196F3").pack(pady=(15, 10), anchor="w")

        opts = ctk.CTkFrame(f, fg_color="transparent")
        opts.pack(anchor="w", padx=10)

        ctk.CTkCheckBox(opts, text="Masaüstüne kısayol oluştur",
                        variable=var_desktop).pack(pady=4, anchor="w")
        ctk.CTkCheckBox(opts, text="Windows Başlat menüsüne ekle",
                        variable=var_startmenu).pack(pady=4, anchor="w")
        ctk.CTkCheckBox(opts, text="Programlar ve Özellikler listesine kaydet",
                        variable=var_registry).pack(pady=4, anchor="w")

        return f

    # ── ADIM 2: KURULUM İLERLEMESİ ──
    def build_step2():
        f = ctk.CTkFrame(content, fg_color="transparent")

        ctk.CTkLabel(f, text="Kurulum Devam Ediyor...",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#2196F3").pack(pady=(40, 20))

        pbar = ctk.CTkProgressBar(f, width=450, height=20, mode="determinate")
        pbar.pack(pady=10)
        pbar.set(0)
        progress_bar[0] = pbar

        slbl = ctk.CTkLabel(f, text="Hazırlanıyor...", font=ctk.CTkFont(size=13),
                            text_color="gray")
        slbl.pack(pady=10)
        status_label[0] = slbl

        return f

    # ── ADIM 3: TAMAMLANDI ──
    def build_step3():
        f = ctk.CTkFrame(content, fg_color="transparent")

        ctk.CTkLabel(f, text="Kurulum Tamamlandı!",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color="#4CAF50").pack(pady=(40, 15))

        ctk.CTkLabel(f, text=(
            f"{APP_NAME} başarıyla bilgisayarınıza kuruldu.\n\n"
            "Kısayollardan uygulamanızı dilediğiniz zaman başlatabilirsiniz.\n"
            "Not: İndirdiğiniz bu kurulum dosyasını artık silebilirsiniz."
        ), font=ctk.CTkFont(size=13), justify="center").pack(pady=10)

        ctk.CTkCheckBox(f, text="Uygulamayı şimdi başlat",
                        variable=var_launch).pack(pady=20)

        return f

    # ── Frame'leri oluştur ──
    frames[0] = build_step0()
    frames[1] = build_step1()
    frames[2] = build_step2()
    frames[3] = build_step3()

    def show_step(step):
        for s, fr in frames.items():
            fr.pack_forget()
        frames[step].pack(fill="both", expand=True)

        # Üst bar renklendirme
        for i, lbl in enumerate(step_labels):
            if i == step:
                lbl.configure(text_color=("#1565C0", "#64B5F6"),
                              font=ctk.CTkFont(size=13, weight="bold"))
            elif i < step:
                lbl.configure(text_color=("#4CAF50", "#81C784"),
                              font=ctk.CTkFont(size=13))
            else:
                lbl.configure(text_color=("gray50", "gray60"),
                              font=ctk.CTkFont(size=13))

        # Buton durumları
        btn_back.configure(state="normal" if step > 0 and step != 2 and step != 3 else "disabled")

        if step == 1:
            btn_next.configure(text="Yükle", fg_color="#1B5E20", hover_color="#003300")
        elif step == 3:
            btn_next.configure(text="Bitir", fg_color="#1565C0", hover_color="#0D47A1")
        else:
            btn_next.configure(text="Devam >", fg_color="#1565C0", hover_color="#0D47A1")

        if step == 2:
            btn_next.configure(state="disabled")
            btn_cancel.configure(state="disabled")
        elif step == 3:
            btn_cancel.pack_forget()
            btn_back.pack_forget()
        else:
            btn_next.configure(state="normal")
            btn_cancel.configure(state="normal")

        current_step[0] = step

    def go_next():
        step = current_step[0]
        if step == 0:
            show_step(1)
        elif step == 1:
            # Disk alanı kontrolü
            path = e_path[0].get().strip()
            if not path:
                messagebox.showwarning("Uyarı", "Lütfen bir kurulum dizini belirtin.", parent=kur_app)
                return
            free_mb = _check_disk_space(path)
            if 0 <= free_mb < REQUIRED_SPACE_MB:
                messagebox.showerror("Yetersiz Alan",
                                     f"Seçilen sürücüde yeterli alan yok.\n"
                                     f"Boş: {free_mb} MB / Gerekli: {REQUIRED_SPACE_MB} MB",
                                     parent=kur_app)
                return
            show_step(2)
            start_installation()
        elif step == 3:
            finalize()

    def go_back():
        step = current_step[0]
        if step > 0:
            show_step(step - 1)

    btn_next.configure(command=go_next)
    btn_back.configure(command=go_back)

    # ── KURULUM İŞLEMİ (THREAD) ──
    install_target_path = [None]

    def start_installation():
        def run_install():
            try:
                install_dir = os.path.normpath(e_path[0].get().strip())
                current_exe = sys.executable
                target_path = os.path.join(install_dir, "ButceM.exe")
                install_target_path[0] = target_path

                def update_progress(value, text):
                    kur_app.after(0, lambda: progress_bar[0].set(value))
                    kur_app.after(0, lambda: status_label[0].configure(text=text))

                # 1. Dizin oluştur (%0-5)
                update_progress(0.02, "Kurulum dizini oluşturuluyor...")
                os.makedirs(install_dir, exist_ok=True)
                update_progress(0.05, "Dizin hazır.")

                # 2. Exe kopyala - chunked (%5-75)
                update_progress(0.05, "Uygulama dosyası kopyalanıyor...")
                file_size = os.path.getsize(current_exe)
                chunk_size = 1024 * 1024  # 1 MB
                copied = 0
                with open(current_exe, 'rb') as src, open(target_path, 'wb') as dst:
                    while True:
                        chunk = src.read(chunk_size)
                        if not chunk:
                            break
                        dst.write(chunk)
                        copied += len(chunk)
                        ratio = copied / file_size
                        progress = 0.05 + ratio * 0.70  # %5 - %75
                        mb_copied = copied / (1024 * 1024)
                        mb_total = file_size / (1024 * 1024)
                        update_progress(progress,
                                        f"Kopyalanıyor... {mb_copied:.1f} / {mb_total:.1f} MB")
                # Zaman damgalarını koru
                try:
                    stat = os.stat(current_exe)
                    os.utime(target_path, (stat.st_atime, stat.st_mtime))
                except OSError:
                    pass

                # 3. Logo kopyala
                update_progress(0.76, "Logo kopyalanıyor...")
                logo = _get_icon_path()
                if os.path.exists(logo):
                    try:
                        shutil.copy2(logo, os.path.join(install_dir, "logo.ico"))
                    except OSError:
                        pass

                # 4. Kullanım kılavuzu (%75-80)
                update_progress(0.78, "Kullanım kılavuzu oluşturuluyor...")
                kilavuz_yolu = os.path.join(install_dir, "Kullanim_Kilavuzu.txt")
                with open(kilavuz_yolu, "w", encoding="utf-8") as kf:
                    kf.write(_kilavuz_metni())

                # 5. Marker dosya (%80-85)
                update_progress(0.82, "Yapılandırma dosyaları yazılıyor...")
                marker_path = os.path.join(install_dir, ".butcem_installed")
                if not os.path.exists(marker_path):
                    open(marker_path, 'w').close()

                # 6. Kısayollar (%85-92)
                update_progress(0.87, "Kısayollar oluşturuluyor...")
                _create_shortcuts(install_dir, target_path,
                                  desktop=var_desktop.get(),
                                  startmenu=var_startmenu.get())

                # 7. Registry (%92-98)
                if var_registry.get():
                    update_progress(0.94, "Windows program listesine kaydediliyor...")
                    _register_program(install_dir, target_path)

                # 8. Günlük (%98-100)
                update_progress(0.98, "Kurulum günlüğü yazılıyor...")
                _write_install_log(install_dir, {
                    "desktop": var_desktop.get(),
                    "startmenu": var_startmenu.get(),
                    "registry": var_registry.get(),
                })

                update_progress(1.0, "Kurulum tamamlandı!")
                kur_app.after(500, lambda: show_step(3))

            except Exception as e:
                kur_app.after(0, lambda: messagebox.showerror(
                    "Kurulum Hatası", f"Hata oluştu:\n{e}", parent=kur_app))
                kur_app.after(0, lambda: show_step(1))

        threading.Thread(target=run_install, daemon=True).start()

    def finalize():
        if var_launch.get() and install_target_path[0]:
            try:
                subprocess.Popen([install_target_path[0]])
            except Exception:
                pass
        kur_app.destroy()
        sys.exit(0)

    show_step(0)
    kur_app.mainloop()


# ─── KALDIRMA (UNINSTALL) SİSTEMİ ────────────────────────────────────

def baslat_kaldir_modu():
    """Komut satırından çağrılan kaldırma modu (--uninstall)."""
    import customtkinter as ctk
    from tkinter import messagebox

    _run_uninstall_dialog(standalone=True)


def _run_uninstall_dialog(parent=None, standalone=False):
    """Kaldırma onay dialogu. parent=None ise yeni pencere açar."""
    import customtkinter as ctk
    from tkinter import messagebox

    if standalone:
        root = ctk.CTk()
        root.withdraw()
    else:
        root = parent

    install_dir = os.path.dirname(os.path.abspath(sys.executable)) if getattr(sys, 'frozen', False) else None
    if not install_dir:
        messagebox.showwarning("Uyarı", "Kaldırma işlemi sadece kurulu sürümde çalışır.")
        if standalone:
            root.destroy()
        return

    # Onay penceresi
    dialog = ctk.CTkToplevel(root) if not standalone else ctk.CTk()
    dialog.title("BütçeM - Programı Kaldır")
    dialog.geometry("450x300")
    dialog.resizable(False, False)
    dialog.eval('tk::PlaceWindow . center')

    icon_path = _get_icon_path()
    if os.path.exists(icon_path):
        try:
            dialog.iconbitmap(icon_path)
        except Exception:
            pass

    if not standalone:
        dialog.transient(parent)
        dialog.grab_set()

    ctk.CTkLabel(dialog, text="Programı Kaldır",
                 font=ctk.CTkFont(size=20, weight="bold"),
                 text_color="#F44336").pack(pady=(20, 10))

    ctk.CTkLabel(dialog, text=(
        f"{APP_NAME} uygulamasını bilgisayarınızdan\n"
        "tamamen kaldırmak istediğinizden emin misiniz?\n\n"
        "Bu işlem geri alınamaz."
    ), font=ctk.CTkFont(size=13), justify="center").pack(pady=10)

    var_delete_data = ctk.BooleanVar(value=False)
    ctk.CTkCheckBox(dialog, text="Kullanıcı verilerini de sil (veritabanı, ayarlar)",
                    variable=var_delete_data,
                    text_color="#FF9800").pack(pady=10)

    btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    btn_frame.pack(pady=20)

    def do_uninstall():
        dialog.destroy() if not standalone else None

        try:
            # 1. Kısayolları sil
            _delete_shortcuts()

            # 2. Registry kaydını sil
            _unregister_program()

            # 3. Yardımcı dosyaları sil
            for fname in [".butcem_installed", "Kullanim_Kilavuzu.txt",
                          "install_log.txt", "_create_shortcuts.vbs", "logo.ico"]:
                fpath = os.path.join(install_dir, fname)
                try:
                    if os.path.exists(fpath):
                        os.remove(fpath)
                except OSError:
                    pass

            # 4. Kullanıcı verileri
            if var_delete_data.get():
                data_dir = os.path.join(install_dir, "data")
                if os.path.isdir(data_dir):
                    shutil.rmtree(data_dir, ignore_errors=True)
                for fname in [".env"]:
                    fpath = os.path.join(install_dir, fname)
                    try:
                        if os.path.exists(fpath):
                            os.remove(fpath)
                    except OSError:
                        pass

            # 5. Exe kendisini silemez, batch ile delayed delete
            exe_path = os.path.abspath(sys.executable) if getattr(sys, 'frozen', False) else None
            if exe_path:
                batch_content = f"""@echo off
ping 127.0.0.1 -n 3 > nul
del /f /q "{exe_path}"
rmdir /s /q "{install_dir}"
del /f /q "%~f0"
"""
                batch_path = os.path.join(os.environ.get("TEMP", "."), "_butcem_uninstall.bat")
                with open(batch_path, "w") as bf:
                    bf.write(batch_content)
                subprocess.Popen(
                    ['cmd', '/c', batch_path],
                    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
                )

            messagebox.showinfo("Kaldırma Tamamlandı",
                                f"{APP_NAME} başarıyla kaldırıldı.\n"
                                "Dosyalar birkaç saniye içinde temizlenecek.")

        except Exception as e:
            messagebox.showerror("Hata", f"Kaldırma sırasında hata:\n{e}")

        if standalone:
            try:
                root.destroy()
            except Exception:
                pass
        sys.exit(0)

    def cancel_uninstall():
        if standalone:
            dialog.destroy()
            sys.exit(0)
        else:
            dialog.destroy()

    ctk.CTkButton(btn_frame, text="Evet, Kaldır", width=130,
                  fg_color="#B71C1C", hover_color="#7F0000",
                  command=do_uninstall).pack(side="left", padx=10)
    ctk.CTkButton(btn_frame, text="Vazgeç", width=130,
                  fg_color="gray40", hover_color="gray30",
                  command=cancel_uninstall).pack(side="left", padx=10)

    if standalone:
        dialog.mainloop()
    else:
        dialog.wait_window()


def show_uninstall_button_in_app(parent_frame, app_instance):
    """Sistem Ayarları sayfasına 'Programı Kaldır' butonu ekler. Sadece frozen modda görünür."""
    if not getattr(sys, 'frozen', False):
        return

    def on_uninstall():
        _run_uninstall_dialog(parent=app_instance, standalone=False)

    ctk.CTkButton(parent_frame, text="Programı Kaldır",
                  fg_color="#B71C1C", hover_color="#7F0000",
                  width=140, command=on_uninstall).grid(row=2, column=2, padx=10, pady=15, sticky="w")
