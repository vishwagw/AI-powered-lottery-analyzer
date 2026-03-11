"""
Sri Lanka Lottery Results Scraper — Selenium Version
======================================================
Scrapes winning lottery numbers from:
  - NLB (National Lottery Board): https://www.nlb.lk/
  - DLB (Development Lotteries Board): https://www.dlb.lk/

Works with JavaScript-rendered pages that the requests version cannot handle.

Requirements:
    pip install selenium webdriver-manager pandas

    Chrome browser must be installed on your machine.
    Download from: https://www.google.com/chrome/

Usage:
    python lottery_scraper_selenium.py

Output:
    nlb_lottery_results.csv
    dlb_lottery_results.csv
    (saved in the same directory as this script)
"""

import re
import os
import sys
import time
import pandas as pd
from datetime import datetime, timedelta

# ── Selenium imports ───────────────────────────────────────────────────────────
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait, Select
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import (
        TimeoutException, NoSuchElementException,
        StaleElementReferenceException, ElementClickInterceptedException
    )
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError as e:
    print(f"\n[ERROR] Missing package: {e}")
    print("  Run: pip install selenium webdriver-manager pandas\n")
    sys.exit(1)


# ─── CONFIG ────────────────────────────────────────────────────────────────────
MONTHS_BACK  = 3
PAGE_TIMEOUT = 20       # seconds to wait for elements
DELAY        = 2.0      # polite pause between actions
OUTPUT_DIR   = os.path.dirname(os.path.abspath(__file__))

END_DATE     = datetime.today()
START_DATE   = END_DATE - timedelta(days=MONTHS_BACK * 30)

NLB_BASE     = "https://www.nlb.lk"
DLB_BASE     = "https://www.dlb.lk"

print(f"\n{'='*62}")
print("  Sri Lanka Lottery Scraper  —  Selenium Edition")
print(f"  Period : {START_DATE.strftime('%Y-%m-%d')}  →  {END_DATE.strftime('%Y-%m-%d')}")
print(f"{'='*62}\n")


# ─── DRIVER SETUP ──────────────────────────────────────────────────────────────

def build_driver(headless: bool = True) -> webdriver.Chrome:
    """Create a Chrome WebDriver (auto-downloads chromedriver if needed)."""
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    try:
        service = Service(ChromeDriverManager().install())
        driver  = webdriver.Chrome(service=service, options=opts)
    except Exception as e:
        print(f"  [!] ChromeDriver auto-install failed: {e}")
        print("      Trying system ChromeDriver …")
        driver = webdriver.Chrome(options=opts)   # falls back to PATH

    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"}
    )
    return driver


def wait_for(driver, by, selector, timeout=PAGE_TIMEOUT):
    """Wait for an element and return it, or None on timeout."""
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
    except TimeoutException:
        return None


def scroll_to_bottom(driver, pauses=3):
    """Scroll page to trigger lazy-loading."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(pauses):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


# ─── DATE HELPERS ──────────────────────────────────────────────────────────────

DATE_FORMATS = [
    "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y",
    "%d %B %Y", "%B %d, %Y", "%d %b %Y",
    "%Y/%m/%d", "%m/%d/%Y",
]

def parse_date(text: str):
    text = text.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    # Try extracting date from longer text
    patterns = [
        r"\d{4}[-/]\d{1,2}[-/]\d{1,2}",
        r"\d{1,2}[-/]\d{1,2}[-/]\d{4}",
        r"\d{1,2}\s+\w+\s+\d{4}",
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            return parse_date(m.group())
    return None


def in_range(dt):
    return dt and START_DATE <= dt <= END_DATE


# ─── GENERIC PAGE PARSER ───────────────────────────────────────────────────────

def parse_tables_from_driver(driver, source_label="") -> list[dict]:
    """Extract all lottery result rows from any table on the current page."""
    records = []
    try:
        tables = driver.find_elements(By.TAG_NAME, "table")
    except Exception:
        return records

    for table in tables:
        try:
            headers = [
                th.text.strip().lower()
                for th in table.find_elements(By.TAG_NAME, "th")
            ]
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                cells = [td.text.strip() for td in row.find_elements(By.TAG_NAME, "td")]
                if not cells:
                    continue
                rec = extract_record(headers, cells, source_label)
                if rec:
                    records.append(rec)
        except StaleElementReferenceException:
            continue
    return records


def parse_cards_from_driver(driver, source_label="") -> list[dict]:
    """Extract results from card/div-based layouts."""
    records = []
    card_selectors = [
        "[class*='result']", "[class*='draw']",
        "[class*='lottery']", "[class*='winning']",
        "[class*='card']", "[class*='item']",
    ]
    seen_texts = set()

    for sel in card_selectors:
        try:
            cards = driver.find_elements(By.CSS_SELECTOR, sel)
            for card in cards:
                text = card.text.strip()
                if not text or text in seen_texts or len(text) < 15:
                    continue
                seen_texts.add(text)

                dt = None
                for line in text.split("\n"):
                    dt = parse_date(line)
                    if dt:
                        break

                if not in_range(dt):
                    continue

                num_match = re.search(r"\b(\d{1,2}(?:\s+\d{1,2}){2,})\b", text)
                draw_match = re.search(r"(?:draw|no\.?|#)\s*[:\-]?\s*(\d+)", text, re.I)
                name_match = re.search(r"^([A-Za-z][A-Za-z\s]+)", text)

                records.append({
                    "date": dt.strftime("%Y-%m-%d"),
                    "lottery_name": name_match.group(1).strip() if name_match else "",
                    "draw_no": draw_match.group(1) if draw_match else "",
                    "winning_numbers": num_match.group(1).strip() if num_match else "",
                    "source": source_label,
                })
        except Exception:
            continue

    return records


def extract_record(headers: list, cells: list, source: str) -> dict | None:
    """Map a table row to a result record using header hints."""
    if len(cells) < 2:
        return None

    # Find date cell
    dt = None
    for cell in cells:
        dt = parse_date(cell)
        if dt:
            break
    if not in_range(dt):
        return None

    rec = {"date": dt.strftime("%Y-%m-%d"), "source": source}

    col = dict(zip(headers, cells)) if headers else {}

    def pick(*keys):
        for k in keys:
            for h, v in col.items():
                if k in h:
                    return v
        return ""

    rec["lottery_name"]    = pick("name", "lottery", "game", "type")
    rec["draw_no"]         = pick("draw no", "draw#", "no.", "draw_no", "draw")
    rec["winning_numbers"] = pick("winning", "number", "result", "ball")
    rec["supplementary"]   = pick("bonus", "supplem", "power", "extra")
    rec["jackpot"]         = pick("jackpot", "prize", "amount")

    # Fallback: find any cell that looks like lottery numbers
    if not rec["winning_numbers"]:
        for cell in cells:
            if re.search(r"\b\d{1,2}(?:\s+\d{1,2}){2,}\b", cell):
                rec["winning_numbers"] = cell
                break

    return rec if rec.get("winning_numbers") else None


# ─── NLB SCRAPER ───────────────────────────────────────────────────────────────

def scrape_nlb(driver: webdriver.Chrome) -> list[dict]:
    print("[ NLB ] Opening website …")
    records = []

    # ── 1. Try main results page ───────────────────────────────────────────────
    for path in ["/results", "/en/results", "/lottery-results", "/"]:
        try:
            driver.get(NLB_BASE + path)
            time.sleep(DELAY)
            if wait_for(driver, By.TAG_NAME, "body"):
                break
        except Exception:
            continue

    scroll_to_bottom(driver)
    print(f"  Page title: {driver.title}")

    # ── 2. Collect internal result links ──────────────────────────────────────
    links = _collect_links(driver, NLB_BASE, r"result|draw|lottery")
    print(f"  Found {len(links)} sub-page(s) to visit.")

    # Parse current page first
    records += parse_tables_from_driver(driver, "NLB main")
    records += parse_cards_from_driver(driver,  "NLB main")

    # ── 3. Visit each sub-link ─────────────────────────────────────────────────
    for url in links[:25]:
        try:
            driver.get(url)
            time.sleep(DELAY)
            scroll_to_bottom(driver)
            records += parse_tables_from_driver(driver, url)
            records += parse_cards_from_driver(driver,  url)
        except Exception as e:
            print(f"  [!] Error visiting {url}: {e}")

    # ── 4. Try date-based filtering if the page has a date picker ─────────────
    if len(records) < 5:
        print("  Trying date filter …")
        records += _try_date_filter(driver, NLB_BASE, "NLB")

    # ── 5. Try selecting lottery type from dropdown ────────────────────────────
    if len(records) < 5:
        print("  Trying lottery type dropdowns …")
        records += _try_dropdown_scrape(driver, NLB_BASE, "NLB")

    records = dedupe(records)
    print(f"  [ NLB ] Records collected: {len(records)}")
    return records


# ─── DLB SCRAPER ───────────────────────────────────────────────────────────────

def scrape_dlb(driver: webdriver.Chrome) -> list[dict]:
    print("\n[ DLB ] Opening website …")
    records = []

    for path in ["/results", "/en/results", "/lottery-results", "/"]:
        try:
            driver.get(DLB_BASE + path)
            time.sleep(DELAY)
            if wait_for(driver, By.TAG_NAME, "body"):
                break
        except Exception:
            continue

    scroll_to_bottom(driver)
    print(f"  Page title: {driver.title}")

    links = _collect_links(driver, DLB_BASE, r"result|draw|lottery")
    print(f"  Found {len(links)} sub-page(s) to visit.")

    records += parse_tables_from_driver(driver, "DLB main")
    records += parse_cards_from_driver(driver,  "DLB main")

    for url in links[:25]:
        try:
            driver.get(url)
            time.sleep(DELAY)
            scroll_to_bottom(driver)
            records += parse_tables_from_driver(driver, url)
            records += parse_cards_from_driver(driver,  url)
        except Exception as e:
            print(f"  [!] Error visiting {url}: {e}")

    if len(records) < 5:
        print("  Trying date filter …")
        records += _try_date_filter(driver, DLB_BASE, "DLB")

    if len(records) < 5:
        print("  Trying lottery type dropdowns …")
        records += _try_dropdown_scrape(driver, DLB_BASE, "DLB")

    records = dedupe(records)
    print(f"  [ DLB ] Records collected: {len(records)}")
    return records


# ─── SHARED HELPER STRATEGIES ──────────────────────────────────────────────────

def _collect_links(driver, base_url, pattern) -> list[str]:
    """Find all anchor hrefs matching pattern on the current page."""
    links = []
    try:
        anchors = driver.find_elements(By.TAG_NAME, "a")
        for a in anchors:
            href = a.get_attribute("href") or ""
            if re.search(pattern, href, re.I) and base_url in href:
                if href not in links:
                    links.append(href)
    except Exception:
        pass
    return links


def _try_date_filter(driver, base_url, label) -> list[dict]:
    """
    Attempt to find a date-range input or calendar picker and
    scrape results for each month in our range.
    """
    records = []
    date_input_selectors = [
        "input[type='date']",
        "input[name*='date']",
        "input[id*='date']",
        "input[placeholder*='date']",
        "input[placeholder*='Date']",
    ]

    current = datetime(START_DATE.year, START_DATE.month, 1)
    while current <= END_DATE:
        month_str = current.strftime("%Y-%m")
        for path in [f"/results?month={month_str}", f"/results/{month_str}", f"/results?date={month_str}"]:
            try:
                driver.get(base_url + path)
                time.sleep(DELAY)
                scroll_to_bottom(driver)
                new = parse_tables_from_driver(driver, f"{label} {month_str}")
                new += parse_cards_from_driver(driver,  f"{label} {month_str}")
                if new:
                    records += new
                    break
            except Exception:
                continue

        # Try filling date input fields
        for sel in date_input_selectors:
            try:
                inputs = driver.find_elements(By.CSS_SELECTOR, sel)
                if inputs:
                    inputs[0].clear()
                    inputs[0].send_keys(current.strftime("%Y-%m-%d"))
                    # Look for a search/submit button
                    for btn_sel in ["button[type='submit']", "input[type='submit']",
                                    "[class*='search']", "[class*='filter']"]:
                        btns = driver.find_elements(By.CSS_SELECTOR, btn_sel)
                        if btns:
                            try:
                                btns[0].click()
                                time.sleep(DELAY)
                            except ElementClickInterceptedException:
                                pass
                    records += parse_tables_from_driver(driver, f"{label} date-input")
                    records += parse_cards_from_driver(driver,  f"{label} date-input")
                    break
            except Exception:
                continue

        # Advance one month
        if current.month == 12:
            current = datetime(current.year + 1, 1, 1)
        else:
            current = datetime(current.year, current.month + 1, 1)

    return records


def _try_dropdown_scrape(driver, base_url, label) -> list[dict]:
    """
    If the page has a <select> dropdown for lottery type, iterate each option.
    """
    records = []
    try:
        driver.get(base_url + "/results")
        time.sleep(DELAY)
        selects = driver.find_elements(By.TAG_NAME, "select")
        if not selects:
            return records

        for sel_el in selects[:3]:   # try up to 3 dropdowns
            sel = Select(sel_el)
            options = sel.options
            print(f"    Dropdown has {len(options)} option(s).")
            for i in range(len(options)):
                try:
                    sel = Select(driver.find_elements(By.TAG_NAME, "select")[0])
                    option_text = sel.options[i].text.strip()
                    if not option_text or option_text.lower() in ("select", "all", "---", ""):
                        continue
                    sel.select_by_index(i)
                    time.sleep(DELAY)
                    scroll_to_bottom(driver)
                    new = parse_tables_from_driver(driver, f"{label} › {option_text}")
                    new += parse_cards_from_driver(driver,  f"{label} › {option_text}")
                    for r in new:
                        r.setdefault("lottery_name", option_text)
                    records += new
                    print(f"    '{option_text}' → {len(new)} record(s)")
                except Exception as e:
                    print(f"    [!] Dropdown option {i} error: {e}")
                    continue
    except Exception as e:
        print(f"  [!] Dropdown scrape error: {e}")

    return records


# ─── DEDUP & SAVE ──────────────────────────────────────────────────────────────

def dedupe(records: list[dict]) -> list[dict]:
    seen = set()
    out  = []
    for r in records:
        key = (r.get("date",""), r.get("draw_no",""), r.get("winning_numbers",""))
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


def save_csv(records: list[dict], filename: str, label: str):
    if not records:
        print(f"\n  ⚠  No data for {label}. CSV not written.")
        print("     The site may use a login wall, CAPTCHA, or unusual JS framework.")
        return None

    df = pd.DataFrame(records)
    priority = ["date", "lottery_name", "draw_no", "winning_numbers", "supplementary", "jackpot"]
    cols = [c for c in priority if c in df.columns] + \
           [c for c in df.columns if c not in priority]
    df = df[cols].sort_values("date", ascending=False).reset_index(drop=True)

    path = os.path.join(OUTPUT_DIR, filename)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"\n  ✓  Saved {len(df)} rows  →  {path}")
    return df


# ─── MAIN ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    # Ask user about headless mode
    headless = True
    if len(sys.argv) > 1 and sys.argv[1].lower() in ("--show", "--visible", "--no-headless"):
        headless = False
        print("  Running in VISIBLE browser mode (--show flag detected)\n")
    else:
        print("  Running in HEADLESS mode. To watch the browser, run:")
        print("  python lottery_scraper_selenium.py --show\n")

    driver = None
    try:
        print("  Starting ChromeDriver …")
        driver = build_driver(headless=headless)
        print("  ChromeDriver ready.\n")

        # ── NLB ──────────────────────────────────────────────────────────────
        nlb_records = scrape_nlb(driver)
        save_csv(nlb_records, "nlb_lottery_results.csv", "NLB")

        # ── DLB ──────────────────────────────────────────────────────────────
        dlb_records = scrape_dlb(driver)
        save_csv(dlb_records, "dlb_lottery_results.csv", "DLB")

    except KeyboardInterrupt:
        print("\n  [!] Interrupted by user.")
    except Exception as e:
        print(f"\n  [!] Unexpected error: {e}")
        import traceback; traceback.print_exc()
    finally:
        if driver:
            driver.quit()
            print("\n  Browser closed.")

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*62}")
    print(f"  NLB records : {len(nlb_records) if 'nlb_records' in dir() else 0}")
    print(f"  DLB records : {len(dlb_records) if 'dlb_records' in dir() else 0}")
    print(f"  Output dir  : {OUTPUT_DIR}")
    print(f"{'='*62}\n")
