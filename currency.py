import urllib.request
import json

def get_exchange_rates():
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
            
        return {"USD": usd_try, "EUR": eur_try}
    except Exception:
        return {"USD": 0.0, "EUR": 0.0}
