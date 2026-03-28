import urllib.request
import json
import time
from logger import get_logger

_log = get_logger("currency")

_cache = {"rates": None, "timestamp": 0}
CACHE_TTL = 3600  # 1 saat

def get_exchange_rates():
    now = time.time()
    if _cache["rates"] and (now - _cache["timestamp"]) < CACHE_TTL:
        return _cache["rates"]
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            usd_try = data['rates'].get('TRY', 0)

        url_eur = "https://api.exchangerate-api.com/v4/latest/EUR"
        req_eur = urllib.request.Request(url_eur, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req_eur, timeout=5) as response:
            data_eur = json.loads(response.read().decode('utf-8'))
            eur_try = data_eur['rates'].get('TRY', 0)

        result = {"USD": usd_try, "EUR": eur_try}
        _cache["rates"] = result
        _cache["timestamp"] = now
        return result
    except Exception as e:
        _log.debug("Döviz kuru çekme hatası: %s", e)
        if _cache["rates"]:
            return _cache["rates"]
        return {"USD": 0.0, "EUR": 0.0}
