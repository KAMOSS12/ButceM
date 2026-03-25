"""
BütçeM - Fiyat Takip & Alarm Sistemi
Periyodik scraping ile fiyat düşüşü bildirimi.
"""

import threading
import datetime
import database
import web_scraper


class PriceTracker:
    def __init__(self, notification_manager=None, check_interval_hours=6):
        self.notification_manager = notification_manager
        self.check_interval = check_interval_hours * 3600
        self.timer = None
        self._running = False

    def check_single_item(self, url, platform):
        """Tekil ürün fiyatını çek. Başarısızlıkta None döner."""
        try:
            return web_scraper.fiyat_getir(url, platform)
        except Exception:
            return None

    def check_all_tracked_items(self):
        """Tüm aktif takip edilen ürünleri kontrol et."""
        try:
            items = database.takip_listele(sadece_aktif=True)
        except Exception:
            return

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        for item in items:
            tid, url, urun_adi, platform, hedef, mevcut, son_kontrol, aktif = item
            try:
                yeni_fiyat = self.check_single_item(url, platform)
                if yeni_fiyat is not None:
                    database.takip_guncelle(tid, yeni_fiyat, now)
                    if yeni_fiyat <= hedef and self.notification_manager:
                        self.notification_manager.send_notification(
                            "Fiyat Düştü!",
                            f"{urun_adi[:40]}\n"
                            f"Hedef: {hedef:.2f} TL\n"
                            f"Güncel: {yeni_fiyat:.2f} TL\n"
                            f"Platform: {platform}"
                        )
                else:
                    database.takip_guncelle(tid, mevcut, now)
            except Exception:
                continue

    def add_tracking(self, url, urun_adi, platform, hedef_fiyat, mevcut_fiyat=0.0):
        """Yeni fiyat takibi ekle."""
        database.takip_ekle(url, urun_adi, platform, hedef_fiyat, mevcut_fiyat)

    def start_periodic_checks(self):
        """Periyodik fiyat kontrolünü başlat."""
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
        self.timer = threading.Timer(self.check_interval, self._do_check)
        self.timer.daemon = True
        self.timer.start()

    def _do_check(self):
        try:
            self.check_all_tracked_items()
        except Exception:
            pass
        self._schedule_next()
