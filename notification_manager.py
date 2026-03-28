"""
BütçeM - Masaüstü Bildirim Sistemi
Taksit hatırlatma, bütçe uyarısı ve aylık özet bildirimleri.
"""

import threading
import datetime
from logger import get_logger

_log = get_logger("notification")


def _send_toast(title, message, timeout=10):
    """Windows toast bildirimi gönder."""
    try:
        from plyer import notification as plyer_notify
        plyer_notify.notify(
            title=f"BütçeM - {title}",
            message=message,
            app_name="BütçeM",
            timeout=timeout
        )
    except Exception as e:
        _log.debug("Toast bildirimi gönderilemedi: %s", e)


class NotificationManager:
    def __init__(self, profile_name, settings, db_module):
        self.profile_name = profile_name
        self.settings = settings or {}
        self.db = db_module
        self.timer = None
        self._running = False
        self.check_interval = 3600  # 1 saat

    def send_notification(self, title, message, timeout=10):
        _send_toast(title, message, timeout)

    def check_installment_reminders(self):
        """Ödenmemiş taksitleri kontrol et ve hatırlat."""
        try:
            rows = self.db.urunleri_getir()
            unpaid = []
            for row in rows:
                uid, kat, ad, fyt, drm, link, ts, vf, ot = row
                if ts >= 2 and ot < ts:
                    kalan = ts - ot
                    unpaid.append(f"{ad[:25]}: {kalan} taksit kaldı")

            if unpaid:
                msg = "\n".join(unpaid[:5])
                if len(unpaid) > 5:
                    msg += f"\n...ve {len(unpaid)-5} ürün daha"
                self.send_notification("Taksit Hatırlatması", msg)
        except Exception as e:
            _log.warning("Taksit hatırlatma hatası: %s", e)

    def check_budget_warnings(self):
        """Aylık bütçe limitini kontrol et."""
        monthly_budget = self.settings.get("monthly_budget", 0)
        if monthly_budget <= 0:
            return
        try:
            now = datetime.date.today()
            spent = self.db.get_monthly_spending(now.year, now.month)
            ratio = spent / monthly_budget

            if ratio >= 1.0:
                self.send_notification(
                    "Bütçe Aşıldı!",
                    f"Bu ay {spent:.0f} TL harcandı.\nBütçe limiti: {monthly_budget:.0f} TL\nLimit %{int(ratio*100)} aşıldı!"
                )
            elif ratio >= 0.8:
                self.send_notification(
                    "Bütçe Uyarısı",
                    f"Bu ay {spent:.0f} TL harcandı.\nBütçenizin %{int(ratio*100)}'ine ulaştınız.\nLimit: {monthly_budget:.0f} TL"
                )
        except Exception as e:
            _log.warning("Bütçe uyarısı hatası: %s", e)

    def generate_monthly_summary(self):
        """Ayın ilk açılışında geçen ayın özetini bildir."""
        try:
            now = datetime.date.today()
            if now.day > 3:
                return

            if now.month == 1:
                prev_year, prev_month = now.year - 1, 12
            else:
                prev_year, prev_month = now.year, now.month - 1

            spent = self.db.get_monthly_spending(prev_year, prev_month)
            if spent > 0:
                ay_adi = [
                    "", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                    "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"
                ][prev_month]
                self.send_notification(
                    "Aylık Özet",
                    f"{ay_adi} {prev_year} toplamı: {spent:.0f} TL harcandı."
                )
        except Exception as e:
            _log.warning("Aylık özet hatası: %s", e)

    def start_periodic_checks(self):
        """Periyodik bildirim kontrollerini başlat. Mevcut timer varsa önce cancel eder."""
        if self.timer:
            self.timer.cancel()
            self.timer = None
        self._running = True
        self._schedule_next()

    def stop_periodic_checks(self):
        """Zamanlayıcıyı durdur."""
        self._running = False
        if self.timer:
            self.timer.cancel()
            self.timer = None

    def _schedule_next(self):
        if not self._running:
            return
        self.timer = threading.Timer(self.check_interval, self._do_checks)
        self.timer.daemon = True
        self.timer.start()

    def _do_checks(self):
        if not self._running:
            return
        if self.settings.get("taksit_reminder", True):
            self.check_installment_reminders()
        if self.settings.get("budget_warning", True):
            self.check_budget_warnings()
        if self.settings.get("monthly_summary", True):
            self.generate_monthly_summary()
        self._schedule_next()

    def run_startup_checks(self):
        """Uygulama açılışında tek seferlik kontrol."""
        def check():
            self._do_checks()
        threading.Thread(target=check, daemon=True).start()
