import requests
from bs4 import BeautifulSoup
import urllib.parse

def trendyol_arama(kelime):
    query = urllib.parse.quote(kelime)
    url = f"https://public.trendyol.com/discovery-web-searchgw-service/v2/api/infinite-scroll/sr?q={query}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    sonuclar = []
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            products = data.get("result", {}).get("products", [])
            for p in products[:20]: # İlk 20
                baslik = p.get("name", "")
                fiyat = float(p.get("price", {}).get("sellingPrice", 0))
                link = "https://www.trendyol.com" + p.get("url", "")
                if baslik and fiyat > 0:
                    sonuclar.append({
                        "platform": "Trendyol",
                        "baslik": baslik,
                        "fiyat": fiyat,
                        "link": link
                    })
    except Exception:
        pass
    return sonuclar

def n11_arama(kelime):
    query = urllib.parse.quote(kelime.replace(" ", "+"))
    url = f"https://www.n11.com/arama?q={query}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    sonuclar = []
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            soup = BeautifulSoup(r.content, "html.parser")
            products = soup.find_all("li", class_="column", limit=20)
            for p in products:
                title_tag = p.find("h3", class_="productName")
                price_tag = p.find("ins") or p.find("a", class_="newPrice") or p.find("span", class_="newPrice")
                link_tag = p.find("a", class_="plink")
                
                if title_tag and price_tag and link_tag:
                    baslik = title_tag.text.strip()
                    fiyat_metin = price_tag.text.replace("TL", "").replace(".", "").replace(",", ".").strip()
                    try:
                        fiyat = float(fiyat_metin)
                        link = link_tag.get("href", "")
                        sonuclar.append({
                            "platform": "N11",
                            "baslik": baslik,
                            "fiyat": fiyat,
                            "link": link
                        })
                    except ValueError:
                        pass
    except Exception:
        pass
    return sonuclar

def amazon_arama_selenium(kelime):
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.common.by import By
    except ImportError:
        raise Exception("Eksik Kütüphane! Lütfen terminale şunu yazıp kurun:\npip install selenium webdriver-manager\nArdından uygulamayı yeniden başlatın.")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    sonuclar = []
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(15)
        
        query = urllib.parse.quote(kelime)
        driver.get(f"https://www.amazon.com.tr/s?k={query}")
        
        items = driver.find_elements(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
        for item in items[:15]:
            try:
                title_elem = item.find_element(By.CSS_SELECTOR, "h2 a span")
                baslik = title_elem.text.strip()
                
                price_elem = item.find_element(By.CSS_SELECTOR, "span.a-price-whole")
                fiyat_metin = price_elem.text.replace(".", "").replace(",", ".").strip()
                fiyat = float(fiyat_metin)
                
                link_elem = item.find_element(By.CSS_SELECTOR, "h2 a")
                link = link_elem.get_attribute("href")
                
                if baslik and fiyat > 0:
                    sonuclar.append({
                        "platform": "Amazon",
                        "baslik": baslik,
                        "fiyat": fiyat,
                        "link": link
                    })
            except Exception:
                continue
    except Exception as e:
        raise Exception(f"Tarayıcı Hatası veya Amazon Bot Koruma Engeli.\nÇözüm: Google Chrome güncelleyin veya tekrar deneyin.\nDetay: {str(e)[:80]}")
    finally:
        if driver:
            driver.quit()
    return sonuclar

def urun_ara(kelime, mode="hizli"):
    tum_sonuclar = []
    if mode == "kapsamli":
        amz_res = amazon_arama_selenium(kelime)
        tum_sonuclar.extend(amz_res)
    else:
        t_res = trendyol_arama(kelime)
        n_res = n11_arama(kelime)
        tum_sonuclar.extend(t_res)
        tum_sonuclar.extend(n_res)
        
    tum_sonuclar = sorted(tum_sonuclar, key=lambda x: x['fiyat'])
    return tum_sonuclar
