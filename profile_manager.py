"""
BütçeM - Çoklu Kullanıcı Profil Yönetim Sistemi
Her profil kendi veritabanı, PIN'i ve ayarlarına sahiptir.
"""

import os
import sys
import json
import shutil
import hashlib
import secrets
import datetime


def get_base_dir():
    """Uygulama veri dizinini döndür. Frozen exe ise %APPDATA%/ButceM kullanır."""
    if getattr(sys, 'frozen', False):
        appdata = os.environ.get('APPDATA', '')
        if appdata:
            base = os.path.join(appdata, 'ButceM')
            os.makedirs(base, exist_ok=True)
            return base
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def get_install_dir():
    """Exe'nin bulunduğu dizini döndür (migrasyon ve kaynak dosyalar için)."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def migrate_data_to_appdata():
    """Eski kurulum dizinindeki verileri %APPDATA%/ButceM'e kopyala (tek seferlik)."""
    if not getattr(sys, 'frozen', False):
        return

    appdata = os.environ.get('APPDATA', '')
    if not appdata:
        return

    appdata_base = os.path.join(appdata, 'ButceM')
    exe_dir = os.path.dirname(os.path.abspath(sys.executable))

    # Zaten aynı dizinse (edge case) atla
    if os.path.normpath(appdata_base).lower() == os.path.normpath(exe_dir).lower():
        return

    old_data = os.path.join(exe_dir, "data")
    new_data = os.path.join(appdata_base, "data")

    # Eski data varsa ve yeni konumda yoksa kopyala
    if os.path.isdir(old_data) and not os.path.isdir(new_data):
        os.makedirs(appdata_base, exist_ok=True)
        shutil.copytree(old_data, new_data)

    # .env dosyasını da taşı
    old_env = os.path.join(exe_dir, ".env")
    new_env = os.path.join(appdata_base, ".env")
    if os.path.exists(old_env) and not os.path.exists(new_env):
        shutil.copy2(old_env, new_env)


def hash_pin(pin, salt=None):
    """PBKDF2 ile güçlü PIN hashleme. Format: salt$hash"""
    if salt is None:
        salt = secrets.token_hex(16)
    pin_hash = hashlib.pbkdf2_hmac(
        'sha256', pin.encode('utf-8'), salt.encode('utf-8'), 100_000
    ).hex()
    return f"{salt}${pin_hash}"


def verify_pin(pin, stored_hash):
    """PIN doğrulama. Hem PBKDF2 (salt$hash) hem eski SHA-256 formatını destekler.
    Returns: (bool, str veya None) - (doğru mu, yeni hash gerekiyorsa PBKDF2 hash)
    """
    if '$' in stored_hash:
        salt = stored_hash.split('$')[0]
        return secrets.compare_digest(hash_pin(pin, salt), stored_hash), None
    # Eski SHA-256 format - backward compat
    old_hash = hashlib.sha256(pin.encode('utf-8')).hexdigest()
    if secrets.compare_digest(old_hash, stored_hash):
        return True, hash_pin(pin)  # Migrate edilecek yeni hash
    return False, None


def _profiles_dir():
    return os.path.join(get_base_dir(), "data", "profiles")


def _profiles_index_path():
    return os.path.join(get_base_dir(), "data", "profiles.json")


def _default_settings():
    return {
        "pin_hash": hash_pin("1234"),
        "theme": "Dark",
        "monthly_budget": 0,
        "notifications": {
            "taksit_reminder": True,
            "budget_warning": True,
            "monthly_summary": True
        },
        "backup": {
            "enabled": False,
            "interval": "weekly",
            "max_backups": 5,
            "custom_dir": ""
        }
    }


def _load_index():
    path = _profiles_index_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"profiles": [], "last_active": ""}


def _save_index(data):
    path = _profiles_index_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def list_profiles():
    """Profil listesini döndür: [{"name": str, "created": str}]"""
    index = _load_index()
    result = []
    for name in index.get("profiles", []):
        profile_dir = os.path.join(_profiles_dir(), name)
        settings = load_profile_settings(name)
        created = ""
        if os.path.isdir(profile_dir):
            try:
                created = datetime.datetime.fromtimestamp(
                    os.path.getctime(profile_dir)
                ).strftime("%Y-%m-%d")
            except OSError:
                pass
        result.append({"name": name, "created": created})
    return result


def create_profile(name, pin="1234"):
    """Yeni profil oluştur. Dizin + boş DB + settings.json."""
    name = name.strip()
    if not name:
        raise ValueError("Profil adı boş olamaz.")

    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).strip()
    if not safe_name:
        raise ValueError("Geçerli bir profil adı girin.")

    profile_dir = os.path.join(_profiles_dir(), safe_name)
    if os.path.exists(profile_dir):
        raise ValueError(f"'{safe_name}' adında bir profil zaten mevcut.")

    os.makedirs(profile_dir, exist_ok=True)
    os.makedirs(os.path.join(profile_dir, "backups"), exist_ok=True)

    settings = _default_settings()
    settings["pin_hash"] = hash_pin(pin)
    save_profile_settings(safe_name, settings)

    index = _load_index()
    if safe_name not in index["profiles"]:
        index["profiles"].append(safe_name)
        _save_index(index)

    return safe_name


def delete_profile(name):
    """Profili sil. Son kalan profil silinemez."""
    index = _load_index()
    if len(index["profiles"]) <= 1:
        raise ValueError("Son kalan profil silinemez.")
    if name not in index["profiles"]:
        raise ValueError(f"'{name}' profili bulunamadı.")

    profile_dir = os.path.join(_profiles_dir(), name)
    if os.path.isdir(profile_dir):
        shutil.rmtree(profile_dir, ignore_errors=True)

    index["profiles"].remove(name)
    if index["last_active"] == name:
        index["last_active"] = index["profiles"][0] if index["profiles"] else ""
    _save_index(index)


def rename_profile(old_name, new_name):
    """Profili yeniden adlandır."""
    new_name = new_name.strip()
    safe_new = "".join(c for c in new_name if c.isalnum() or c in (' ', '_', '-')).strip()
    if not safe_new:
        raise ValueError("Geçerli bir profil adı girin.")

    index = _load_index()
    if old_name not in index["profiles"]:
        raise ValueError(f"'{old_name}' profili bulunamadı.")
    if safe_new in index["profiles"]:
        raise ValueError(f"'{safe_new}' adında bir profil zaten mevcut.")

    old_dir = os.path.join(_profiles_dir(), old_name)
    new_dir = os.path.join(_profiles_dir(), safe_new)
    if os.path.isdir(old_dir):
        os.rename(old_dir, new_dir)

    idx = index["profiles"].index(old_name)
    index["profiles"][idx] = safe_new
    if index["last_active"] == old_name:
        index["last_active"] = safe_new
    _save_index(index)


def get_profile_db_path(profile_name):
    """Profil veritabanı dosyasının tam yolunu döndür."""
    return os.path.join(_profiles_dir(), profile_name, "urunler.db")


def get_profile_settings_path(profile_name):
    return os.path.join(_profiles_dir(), profile_name, "settings.json")


def load_profile_settings(profile_name):
    """Profil ayarlarını yükle. Dosya yoksa varsayılan döndür."""
    path = get_profile_settings_path(profile_name)
    defaults = _default_settings()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                saved = json.load(f)
            # Eksik anahtarları varsayılanlarla doldur
            for key, val in defaults.items():
                if key not in saved:
                    saved[key] = val
                elif isinstance(val, dict):
                    for subkey, subval in val.items():
                        if subkey not in saved[key]:
                            saved[key][subkey] = subval
            return saved
        except (json.JSONDecodeError, OSError):
            pass
    return defaults


def save_profile_settings(profile_name, settings):
    """Profil ayarlarını kaydet."""
    path = get_profile_settings_path(profile_name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


def get_last_active_profile():
    """Son aktif profil adını döndür."""
    index = _load_index()
    last = index.get("last_active", "")
    if last and last in index.get("profiles", []):
        return last
    profiles = index.get("profiles", [])
    return profiles[0] if profiles else ""


def set_last_active_profile(name):
    """Son aktif profili ayarla."""
    index = _load_index()
    index["last_active"] = name
    _save_index(index)


def migrate_legacy_data():
    """
    Tek seferlik migrasyon: eski data/urunler.db varsa ve
    data/profiles/ yoksa, 'varsayilan' profiline taşı.
    """
    base = get_base_dir()
    old_db = os.path.join(base, "data", "urunler.db")
    profiles_dir = _profiles_dir()

    # Zaten profil sistemi varsa çık
    if os.path.isdir(profiles_dir) and list_profiles():
        return

    # Profil dizinini oluştur
    os.makedirs(profiles_dir, exist_ok=True)

    profile_name = "varsayilan"
    profile_dir = os.path.join(profiles_dir, profile_name)
    os.makedirs(profile_dir, exist_ok=True)
    os.makedirs(os.path.join(profile_dir, "backups"), exist_ok=True)

    # Eski DB'yi taşı
    target_db = os.path.join(profile_dir, "urunler.db")
    if os.path.exists(old_db) and not os.path.exists(target_db):
        shutil.copy2(old_db, target_db)

    # Eski PIN'i ayarlardan al
    settings = _default_settings()
    env_path = os.path.join(base, ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("APP_PIN="):
                        pin_val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if pin_val:
                            settings["pin_hash"] = pin_val if len(pin_val) == 64 else hash_pin(pin_val)
        except OSError:
            pass

    save_profile_settings(profile_name, settings)

    # Index oluştur
    index = {"profiles": [profile_name], "last_active": profile_name}
    _save_index(index)


def _hide_data_directory():
    """Frozen modda data/ dizinini Windows'ta gizle."""
    if not getattr(sys, 'frozen', False):
        return
    try:
        import ctypes
        data_dir = os.path.join(get_base_dir(), "data")
        if os.path.isdir(data_dir):
            FILE_ATTRIBUTE_HIDDEN = 0x02
            ctypes.windll.kernel32.SetFileAttributesW(str(data_dir), FILE_ATTRIBUTE_HIDDEN)
    except Exception:
        pass


def ensure_profiles_exist():
    """En az bir profil olmasını garanti et."""
    migrate_legacy_data()
    if not list_profiles():
        create_profile("varsayilan", "1234")
        set_last_active_profile("varsayilan")
    _hide_data_directory()
