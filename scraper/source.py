import os
from playwright.sync_api import sync_playwright

BASE = "https://cl.soccerway.com/chile/liga-de-primera/#/f1w5g1qT/clasificacion/general/"
SNAPSHOT = "/app/data/pagina_tabla.html"

def obtener_html(url: str = BASE) -> str:
    # Modo experimento/demo: leer del snapshot (rápido, determinista, sin red)
    if os.getenv("USAR_SNAPSHOT") == "1" and os.path.exists(SNAPSHOT):
        return open(SNAPSHOT, encoding="utf-8").read()
    # Modo real: renderizar con Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        try:
            page.click('text=/Tabla de posici/i', timeout=5000)
        except Exception:
            pass
        page.wait_for_selector(".ui-table__row", timeout=20000)  # esperar la tabla real
        html = page.content()
        browser.close()
        return html