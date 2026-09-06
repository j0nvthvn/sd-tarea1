import time, os
from urllib.parse import urlparse
from collections import Counter
from playwright.sync_api import sync_playwright

URL = "https://cl.soccerway.com/chile/liga-de-primera/#/f1w5g1qT/clasificacion/general/"
os.makedirs("/app/data", exist_ok=True)
urls = []

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox"])
    pg = b.new_page()
    pg.on("response", lambda r: urls.append(r.url))
    pg.goto(URL, wait_until="networkidle", timeout=60000)
    time.sleep(3)
    try:
        pg.click('text=/Tabla de posici/i', timeout=4000); print("click tabla OK")
    except Exception as e:
        print("no click:", e)
    time.sleep(10)
    open("/app/data/pagina_tabla.html", "w", encoding="utf-8").write(pg.content())
    pg.screenshot(path="/app/data/pagina_tabla.png", full_page=True)
    b.close()

c = Counter(urlparse(u).netloc for u in urls)
print("=== hosts contactados ===")
for h, n in c.most_common():
    print(n, h)
open("/app/data/urls.txt", "w").write("\n".join(urls))
print("total urls:", len(urls))