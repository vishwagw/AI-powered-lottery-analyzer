"""
Sri Lanka Lottery Results Scraper
==================================
Scrapes winning lottery numbers from:
  - NLB (National Lottery Board): https://www.nlb.lk/
  - DLB (Development Lotteries Board): https://www.dlb.lk/

Output: Two CSV files saved in the same directory as this script.

Requirements:
    pip install requests beautifulsoup4 lxml pandas

Usage:
    python lottery_scraper.py
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import re
import sys
import os

# ─── CONFIG ────────────────────────────────────────────────────────────────────
MONTHS_BACK = 3          # How far back to fetch results
DELAY = 1.5              # Seconds between requests (be polite to servers)
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Date range
END_DATE   = datetime.today()
START_DATE = END_DATE - timedelta(days=MONTHS_BACK * 30)

print(f"\n{'='*60}")
print("  Sri Lanka Lottery Results Scraper")
print(f"  Period: {START_DATE.strftime('%Y-%m-%d')} → {END_DATE.strftime('%Y-%m-%d')}")
print(f"{'='*60}\n")


# ─── HELPERS ───────────────────────────────────────────────────────────────────

def get_session():
    s = requests.Session()
    s.headers.update(HEADERS)
    return s


def safe_get(session, url, params=None, retries=3):
    """GET with retries and friendly error messages."""
    for attempt in range(1, retries + 1):
        try:
            resp = session.get(url, params=params, timeout=20)
            resp.raise_for_status()
            return resp
        except requests.exceptions.HTTPError as e:
            print(f"  [!] HTTP error {e.response.status_code} on {url}")
        except requests.exceptions.ConnectionError:
            print(f"  [!] Connection failed on attempt {attempt}/{retries}: {url}")
        except requests.exceptions.Timeout:
            print(f"  [!] Timeout on attempt {attempt}/{retries}: {url}")
        if attempt < retries:
            time.sleep(DELAY * attempt)
    return None


def save_csv(records, filename, label):
    if not records:
        print(f"  [!] No data collected for {label}. CSV not saved.")
        return
    df = pd.DataFrame(records)
    # Normalise column order
    priority = ["date", "lottery_name", "draw_no", "winning_numbers", "supplementary", "jackpot"]
    cols = [c for c in priority if c in df.columns] + \
           [c for c in df.columns if c not in priority]
    df = df[cols].sort_values("date", ascending=False).reset_index(drop=True)
    path = os.path.join(OUTPUT_DIR, filename)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"\n  ✓ Saved {len(df)} records → {path}")
    return df


# ─── NLB SCRAPER ───────────────────────────────────────────────────────────────

def scrape_nlb():
    """
    Scrapes NLB results from https://www.nlb.lk/results
    NLB typically lists results per lottery type with draw date and number.
    """
    print("[ NLB ] Starting scrape …")
    BASE = "https://www.nlb.lk"
    session = get_session()
    records = []

    # ── Step 1: collect all lottery result page links ──────────────────────────
    resp = safe_get(session, f"{BASE}/results")
    if resp is None:
        resp = safe_get(session, f"{BASE}/en/results")
    if resp is None:
        print("  [!] Could not reach NLB results page. Check your internet connection.")
        return records

    soup = BeautifulSoup(resp.text, "lxml")

    # Find lottery type links (common patterns on NLB site)
    lottery_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if re.search(r"(result|lottery|draw)", href, re.I):
            full = href if href.startswith("http") else BASE + "/" + href.lstrip("/")
            if full not in lottery_links:
                lottery_links.append(full)

    # If no sub-links found, treat the current page itself
    if not lottery_links:
        lottery_links = [f"{BASE}/results"]

    print(f"  Found {len(lottery_links)} lottery page(s) to check.")

    # ── Step 2: parse each page for draw results ───────────────────────────────
    for url in lottery_links[:30]:   # cap to avoid runaway scraping
        time.sleep(DELAY)
        r = safe_get(session, url)
        if r is None:
            continue
        s = BeautifulSoup(r.text, "lxml")
        records += _parse_nlb_page(s, url)

    # ── Step 3: if results still empty, try the AJAX / search endpoint ─────────
    if not records:
        print("  Trying NLB search/API endpoint …")
        records += _try_nlb_ajax(session, BASE)

    print(f"  [ NLB ] Total records collected: {len(records)}")
    return records


def _parse_nlb_page(soup, source_url=""):
    """
    Extracts rows from an NLB results page.
    Handles multiple common HTML layouts used by nlb.lk
    """
    rows = []

    # Layout A – standard <table>
    for table in soup.find_all("table"):
        headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
        for tr in table.find_all("tr"):
            cells = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
            if not cells:
                continue
            row = _map_nlb_row(headers, cells, source_url)
            if row:
                rows.append(row)

    # Layout B – card / div-based results
    if not rows:
        for card in soup.find_all(class_=re.compile(r"result|draw|lottery", re.I)):
            text = card.get_text(" ", strip=True)
            date_match = re.search(r"\d{4}[-/]\d{1,2}[-/]\d{1,2}", text)
            num_match  = re.search(r"(\d[\d\s\-]+\d)", text)
            if date_match and num_match:
                try:
                    date = datetime.strptime(date_match.group(), "%Y-%m-%d")
                except ValueError:
                    continue
                if START_DATE <= date <= END_DATE:
                    rows.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "lottery_name": _extract_lottery_name(card),
                        "draw_no": _extract_draw_no(text),
                        "winning_numbers": num_match.group().strip(),
                        "source": source_url,
                    })
    return rows


def _map_nlb_row(headers, cells, source_url):
    """Map table cells to a dict using header hints."""
    if len(cells) < 2:
        return None

    # Try to find a date in the cells
    date_str = None
    for cell in cells:
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d %B %Y", "%B %d, %Y"):
            try:
                dt = datetime.strptime(cell.strip(), fmt)
                if START_DATE <= dt <= END_DATE:
                    date_str = dt.strftime("%Y-%m-%d")
                break
            except ValueError:
                continue
        if date_str:
            break

    if not date_str:
        return None

    row = {"date": date_str, "source": source_url}

    for i, h in enumerate(headers):
        if i >= len(cells):
            break
        if "draw" in h or "no" in h:
            row["draw_no"] = cells[i]
        elif "name" in h or "lottery" in h:
            row["lottery_name"] = cells[i]
        elif "number" in h or "winning" in h or "result" in h:
            row["winning_numbers"] = cells[i]
        elif "super" in h or "supplem" in h or "bonus" in h:
            row["supplementary"] = cells[i]
        elif "jackpot" in h or "prize" in h:
            row["jackpot"] = cells[i]

    if not row.get("winning_numbers"):
        # Fall back: take the longest numeric-looking cell
        numeric_cells = [c for c in cells if re.search(r"\d{1,2}[\s\-]\d{1,2}", c)]
        if numeric_cells:
            row["winning_numbers"] = max(numeric_cells, key=len)

    return row if row.get("winning_numbers") else None


def _try_nlb_ajax(session, base):
    """Try known NLB API / search paths."""
    records = []
    endpoints = [
        "/api/results",
        "/results/search",
        "/en/results",
        "/results/latest",
    ]
    for ep in endpoints:
        r = safe_get(session, base + ep)
        if r is None:
            continue
        try:
            data = r.json()
            # parse JSON if it looks like a list of results
            if isinstance(data, list):
                for item in data:
                    date_val = item.get("date") or item.get("draw_date") or ""
                    records.append({
                        "date": date_val,
                        "lottery_name": item.get("name") or item.get("lottery"),
                        "draw_no": item.get("draw_no") or item.get("draw"),
                        "winning_numbers": item.get("numbers") or item.get("winning_numbers"),
                        "source": base + ep,
                    })
        except Exception:
            soup = BeautifulSoup(r.text, "lxml")
            records += _parse_nlb_page(soup, base + ep)
        if records:
            break
        time.sleep(DELAY)
    return records


# ─── DLB SCRAPER ───────────────────────────────────────────────────────────────

def scrape_dlb():
    """
    Scrapes DLB results from https://www.dlb.lk/results
    DLB typically has a results page filtered by lottery name and date.
    """
    print("\n[ DLB ] Starting scrape …")
    BASE = "https://www.dlb.lk"
    session = get_session()
    records = []

    # ── Step 1: load main results page ────────────────────────────────────────
    for path in ["/results", "/en/results", "/lottery-results", "/"]:
        resp = safe_get(session, BASE + path)
        if resp:
            break
    if resp is None:
        print("  [!] Could not reach DLB results page. Check your internet connection.")
        return records

    soup = BeautifulSoup(resp.text, "lxml")

    # ── Step 2: find individual lottery links ──────────────────────────────────
    lottery_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if re.search(r"(result|draw|lottery)", href, re.I) and "dlb" in href or href.startswith("/"):
            full = href if href.startswith("http") else BASE + "/" + href.lstrip("/")
            if full not in lottery_links and "dlb.lk" in full:
                lottery_links.append(full)

    if not lottery_links:
        lottery_links = [BASE + "/results"]

    print(f"  Found {len(lottery_links)} lottery page(s) to check.")

    for url in lottery_links[:30]:
        time.sleep(DELAY)
        r = safe_get(session, url)
        if r is None:
            continue
        s = BeautifulSoup(r.text, "lxml")
        records += _parse_dlb_page(s, url)

    # ── Step 3: paginate if results seem sparse ────────────────────────────────
    if len(records) < 10:
        print("  Trying paginated DLB results …")
        records += _paginate_dlb(session, BASE)

    print(f"  [ DLB ] Total records collected: {len(records)}")
    return records


def _parse_dlb_page(soup, source_url=""):
    rows = []

    # Table-based layout
    for table in soup.find_all("table"):
        headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
        for tr in table.find_all("tr"):
            cells = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
            if not cells:
                continue
            row = _map_dlb_row(headers, cells, source_url)
            if row:
                rows.append(row)

    # Card / div layout
    if not rows:
        for card in soup.find_all(class_=re.compile(r"result|draw|winning|lottery", re.I)):
            text = card.get_text(" ", strip=True)
            date_match = re.search(
                r"(\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{4})", text
            )
            if date_match:
                raw = date_match.group()
                for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%d-%m-%Y"):
                    try:
                        dt = datetime.strptime(raw, fmt)
                        break
                    except ValueError:
                        dt = None
                if dt and START_DATE <= dt <= END_DATE:
                    num_match = re.search(r"(\d{1,2}(?:[\s\-]+\d{1,2}){2,})", text)
                    rows.append({
                        "date": dt.strftime("%Y-%m-%d"),
                        "lottery_name": _extract_lottery_name(card),
                        "draw_no": _extract_draw_no(text),
                        "winning_numbers": num_match.group().strip() if num_match else "",
                        "source": source_url,
                    })
    return rows


def _map_dlb_row(headers, cells, source_url):
    if len(cells) < 2:
        return None

    date_str = None
    for cell in cells:
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d %B %Y", "%B %d, %Y"):
            try:
                dt = datetime.strptime(cell.strip(), fmt)
                if START_DATE <= dt <= END_DATE:
                    date_str = dt.strftime("%Y-%m-%d")
                break
            except ValueError:
                continue
        if date_str:
            break

    if not date_str:
        return None

    row = {"date": date_str, "source": source_url}
    for i, h in enumerate(headers):
        if i >= len(cells):
            break
        if "draw" in h and ("no" in h or "#" in h):
            row["draw_no"] = cells[i]
        elif "name" in h or "lottery" in h or "game" in h:
            row["lottery_name"] = cells[i]
        elif "number" in h or "winning" in h or "ball" in h:
            row["winning_numbers"] = cells[i]
        elif "bonus" in h or "supplem" in h or "power" in h:
            row["supplementary"] = cells[i]
        elif "jackpot" in h or "prize" in h:
            row["jackpot"] = cells[i]

    if not row.get("winning_numbers"):
        numeric_cells = [c for c in cells if re.search(r"\d{1,2}[\s\-]\d{1,2}", c)]
        if numeric_cells:
            row["winning_numbers"] = max(numeric_cells, key=len)

    return row if row.get("winning_numbers") else None


def _paginate_dlb(session, base):
    records = []
    page = 1
    while page <= 10:
        urls_to_try = [
            f"{base}/results?page={page}",
            f"{base}/results/page/{page}",
            f"{base}/en/results?page={page}",
        ]
        for url in urls_to_try:
            r = safe_get(session, url)
            if r is None:
                continue
            s = BeautifulSoup(r.text, "lxml")
            new = _parse_dlb_page(s, url)
            if new:
                records += new
                break
        else:
            break   # no more pages
        page += 1
        time.sleep(DELAY)
    return records


# ─── UTILITY ───────────────────────────────────────────────────────────────────

def _extract_lottery_name(tag):
    for cls in (tag.get("class") or []):
        clean = re.sub(r"[-_]", " ", cls).strip()
        if len(clean) > 3:
            return clean.title()
    heading = tag.find(re.compile(r"h[1-6]|strong|b"))
    return heading.get_text(strip=True) if heading else ""


def _extract_draw_no(text):
    m = re.search(r"(?:draw|no\.?|#)\s*[:\-]?\s*(\d+)", text, re.I)
    return m.group(1) if m else ""


# ─── MAIN ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Check dependencies
    missing = []
    for pkg in ["requests", "bs4", "lxml", "pandas"]:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"[ERROR] Missing packages: {', '.join(missing)}")
        print(f"        Run: pip install {' '.join(missing)}")
        sys.exit(1)

    # ── NLB ──
    nlb_data = scrape_nlb()
    nlb_df = save_csv(nlb_data, "nlb_lottery_results.csv", "NLB")

    # ── DLB ──
    dlb_data = scrape_dlb()
    dlb_df = save_csv(dlb_data, "dlb_lottery_results.csv", "DLB")

    # ── Summary ──
    print(f"\n{'='*60}")
    print("  Done!")
    print(f"  NLB records: {len(nlb_data)}")
    print(f"  DLB records: {len(dlb_data)}")
    print(f"  Files saved to: {OUTPUT_DIR}")
    print(f"{'='*60}\n")

    if not nlb_data and not dlb_data:
        print("  ⚠  No data was scraped. Possible reasons:")
        print("     • The website structure may have changed.")
        print("     • Your IP may be rate-limited.")
        print("     • The sites may require JavaScript (try a Selenium version).")
        print("\n  Would you like a Selenium-based version? Ask Claude!")
