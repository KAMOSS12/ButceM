"""
BütçeM - Zamanlanmış Otomatik Yedekleme Sistemi
Profil başına periyodik DB yedeklemesi yapar.
"""

import os
import shutil
import datetime
import threading
import profile_manager
from logger import get_logger

_log = get_logger("backup")


class BackupManager:
    def __init__(self, profile_name, backup_settings):
        self.profile_name = profile_name
        self.settings = backup_settings or {}
        self.timer = None
        self._running = False

    def get_backup_dir(self):
        """Yedek dizinini döndür. Özel dizin ayarlıysa onu kullan."""
        default_dir = os.path.join(
            profile_manager._profiles_dir(), self.profile_name, "backups"
        )
        custom = self.settings.get("custom_dir", "")
        if custom and os.path.isdir(custom):
            real_custom = os.path.realpath(custom)
            # Sistem dizinlerine yazımı engelle
            forbidden = [os.environ.get("SYSTEMROOT", r"C:\Windows"),
                         os.environ.get("PROGRAMFILES", r"C:\Program Files"),
                         os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")]
            for fb in forbidden:
                if fb and real_custom.lower().startswith(fb.lower()):
                    _log.warning("Güvenlik: Yedekleme dizini sistem dizinine yazamaz: %s", real_custom)
                    return default_dir
            return real_custom
        return default_dir

    def create_backup(self):
        """Veritabanını yedekle. Dosya adı: urunler_YYYY-MM-DD_HHMMSS.db.bak"""
        db_path = profile_manager.get_profile_db_path(self.profile_name)
        if not os.path.exists(db_path):
            return None

        backup_dir = self.get_backup_dir()
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        backup_name = f"urunler_{timestamp}.db.bak"
        backup_path = os.path.join(backup_dir, backup_name)

        shutil.copy(db_path, backup_path)  # copy2 yerine copy: mtime yeni dosyanın olmalı
        self._cleanup_old_backups()
        return backup_path

    def _cleanup_old_backups(self):
        """Maksimum yedek sayısını aş, en eskileri sil."""
        max_backups = self.settings.get("max_backups", 5)
        backup_dir = self.get_backup_dir()
        if not os.path.isdir(backup_dir):
            return

        files = []
        for f in os.listdir(backup_dir):
            if f.endswith(".db.bak"):
                full = os.path.join(backup_dir, f)
                files.append((f, full))

        files.sort(key=lambda x: x[0], reverse=True)  # Dosya adına göre sırala (YYYY-MM-DD_HHMMSS formatı kronolojik)
        for _, path in files[max_backups:]:
            try:
                os.remove(path)
            except OSError:
                pass

    def list_backups(self):
        """Yedek listesini döndür: [{"filename", "path", "size_kb", "created"}]"""
        backup_dir = self.get_backup_dir()
        if not os.path.isdir(backup_dir):
            return []

        result = []
        for f in os.listdir(backup_dir):
            if f.endswith(".db.bak"):
                full = os.path.join(backup_dir, f)
                try:
                    stat = os.stat(full)
                    result.append({
                        "filename": f,
                        "path": full,
                        "size_kb": stat.st_size // 1024,
                        "created": datetime.datetime.fromtimestamp(
                            stat.st_mtime
                        ).strftime("%Y-%m-%d %H:%M")
                    })
                except OSError:
                    pass

        result.sort(key=lambda x: x["created"], reverse=True)
        return result

    def restore_backup(self, backup_path):
        """Yedeği geri yükle. Önce güvenlik yedeği alır."""
        # Path doğrulama: sadece backup dizinindeki dosyalar kabul edilir
        backup_dir = self.get_backup_dir()
        real_backup = os.path.realpath(backup_path)
        real_dir = os.path.realpath(backup_dir)
        if not real_backup.startswith(real_dir + os.sep):
            _log.warning("Güvenlik: Geçersiz backup yolu reddedildi: %s", backup_path)
            return False
        if not os.path.isfile(real_backup) or not real_backup.endswith(".db.bak"):
            _log.warning("Güvenlik: Geçersiz backup dosyası: %s", backup_path)
            return False

        db_path = profile_manager.get_profile_db_path(self.profile_name)
        if os.path.exists(db_path):
            safety = db_path + ".pre_restore.bak"
            shutil.copy2(db_path, safety)
        shutil.copy2(backup_path, db_path)
        return True

    def get_last_backup_time(self):
        """Son yedek zamanını döndür."""
        backups = self.list_backups()
        if backups:
            return backups[0]["created"]
        return "Henüz yedeklenmedi"

    def start_scheduled(self):
        """Periyodik yedeklemeyi başlat."""
        self._running = True
        self._schedule_next()

    def stop_scheduled(self):
        """Zamanlayıcıyı durdur."""
        self._running = False
        if self.timer:
            self.timer.cancel()
            self.timer = None

    def _schedule_next(self):
        if not self._running:
            return
        interval_map = {"daily": 86400, "weekly": 604800, "monthly": 2592000}
        seconds = interval_map.get(self.settings.get("interval", "weekly"), 604800)
        self.timer = threading.Timer(seconds, self._do_scheduled_backup)
        self.timer.daemon = True
        self.timer.start()

    def _do_scheduled_backup(self):
        try:
            self.create_backup()
        except Exception as e:
            _log.warning("Zamanlanmış yedekleme hatası: %s", e)
        self._schedule_next()
