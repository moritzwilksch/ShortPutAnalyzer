from rich.console import Console
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json

c = Console()
from rich import print

COLNAMES = [
    "no",
    "ticker",
    "company",
    "sector",
    "industry",
    "country",
    "marketcap",
    "pe",
    "price",
    "change",
    "volume",
]

BASE_URL = "https://finviz.com/screener.ashx?v=111&f=cap_largeover,fa_div_o1,fa_opermargin_pos,fa_payoutratio_u100,fa_pe_u40,fa_pfcf_u30,sh_opt_option"


def get_items_from_page_html(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    rows = soup.find_all("tr", {"class": "table-light-row-cp"}) + soup.find_all(
        "tr", {"class": "table-dark-row-cp"}
    )

    items = []
    for row in rows:
        current_item = dict()
        for name, col in zip(COLNAMES, row.find_all("td")):
            current_item[name] = col.text.strip()
        items.append(current_item)
    items.sort(key=lambda x: int(x["no"]))
    return items


all_items = []
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(BASE_URL)
    n_total_pages = int(page.query_selector_all("a.screener-pages")[-1].inner_text())

    print(f"[green][INFO][/] Total: {n_total_pages} pages")
    for pagenum in range(1, n_total_pages):
        print(f"[green][INFO][/] Fetching page {pagenum}...")
        url = f"{BASE_URL}&r={(pagenum-1)*20 + 1}"
        page.goto(url)
        page.wait_for_selector("tr.screener-tabs-top-row", timeout=10_000)
        html = page.inner_html("html")
        all_items.extend(get_items_from_page_html(html))
        page.wait_for_timeout(2_000)
    browser.close()


print(all_items)
with open("watchlist.json", "w") as f:
    json.dump(all_items, f, indent=2)

print(":white_check_mark: Done.")
