"""
email_enrichment.py  —  Flip Analyzer · Email-Link-Enrichment
================================================================
Dieses Modul neben server.py ablegen.
In server.py oben einfügen:  from email_enrichment import enrich_email

Funktionsweise:
  1. Extrahiert alle relevanten Links aus dem HTML/Text einer Email
  2. Fetcht jede Seite (inkl. Google Drive Ordner)
  3. Lädt bis zu 3 Bilder als base64 herunter
  4. Gibt einen Enrichment-Dict zurück der in die KI-Analyse einfließt
"""

import re
import base64
import requests
from urllib.parse import urljoin, urlparse

try:
    from bs4 import BeautifulSoup
    BS4_OK = True
except ImportError:
    BS4_OK = False


# ---------------------------------------------------------------------------
# Filter-Regexes
# ---------------------------------------------------------------------------
_NOISE = re.compile(r"""
    list-manage\.com | mailchimp\.com | unsubscribe | track/open | track/click |
    facebook\.com    | instagram\.com | linkedin\.com | twitter\.com | youtube\.com |
    schemas\.microsoft\.com | w3\.org | cdn-images\. | mcusercontent\.com |
    googletagmanager | google-analytics | mailto: | tel: | ^\#
""", re.VERBOSE | re.IGNORECASE)

_LISTING = re.compile(r"""
    drive\.google\.com | dropbox\.com | zillow\.com | redfin\.com |
    realtor\.com | mitchelldean | eydura | property | listing | photos |
    flip | deal | mls | homes | realty
""", re.VERBOSE | re.IGNORECASE)

# ---------------------------------------------------------------------------
# Schritt 1: Links extrahieren
# ---------------------------------------------------------------------------

def _extract_links(html: str, text: str) -> list:
    links, seen = [], set()

    # Aus HTML
    if html and BS4_OK:
        try:
            soup = BeautifulSoup(html, "lxml")
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                href = re.sub(r'=\r?\n', '', href).replace('=3D', '=')
                if href.startswith("http"):
                    links.append(href)
        except Exception:
            pass

    # Aus Plaintext (Fallback)
    for u in re.findall(r'https?://[^\s<>"\'\\)>]+', text or ""):
        links.append(u.rstrip('>').strip())

    boosted, rest = [], []
    for url in links:
        url = re.sub(r'=\r?\n', '', url).strip()
        key = url[:120]
        if key in seen or not url.startswith("http"):
            continue
        seen.add(key)
        if _NOISE.search(url):
            continue
        (boosted if _LISTING.search(url) else rest).append(url)

    return (boosted + rest)[:5]


# ---------------------------------------------------------------------------
# Schritt 2: Seite fetchen
# ---------------------------------------------------------------------------

_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.9",
    "Accept-Language": "en-US,en;q=0.9",
}


def _gdrive_folder_images(url: str) -> list:
    """Extrahiert downloadbare Bild-URLs aus einem öffentlichen Google Drive Ordner."""
    try:
        r = requests.get(url, headers=_BROWSER_HEADERS, timeout=15, allow_redirects=True)
        if r.status_code != 200:
            return []
        ids, seen_ids, out = re.findall(r'"([a-zA-Z0-9_-]{25,33})"', r.text), set(), []
        for fid in ids:
            if fid not in seen_ids:
                seen_ids.add(fid)
                out.append(f"https://drive.google.com/uc?id={fid}&export=download")
                if len(out) >= 5:
                    break
        return out
    except Exception as e:
        print(f"  GDrive folder: {e}")
        return []


def _fetch_page(url: str) -> dict:
    """
    Fetcht eine URL.
    Rückgabe: {"text": str, "image_urls": list, "error": str|None}
    """
    result = {"text": "", "image_urls": [], "error": None}

    # Google Drive Ordner
    if "drive.google.com/folder" in url or "drive.google.com/drive/folder" in url:
        imgs = _gdrive_folder_images(url)
        result["text"] = f"[Google Drive Ordner – {len(imgs)} Bilder gefunden]"
        result["image_urls"] = imgs
        return result

    # Google Drive direkt-Download
    if "drive.google.com/uc" in url:
        result["image_urls"] = [url]
        result["text"] = "[Google Drive direktes Bild]"
        return result

    try:
        r = requests.get(url, headers=_BROWSER_HEADERS, timeout=15, allow_redirects=True)
        r.raise_for_status()
        ct = r.headers.get("Content-Type", "")

        # Direktes Bild
        if any(t in ct for t in ["image/jpeg", "image/png", "image/webp", "image/gif"]):
            result["image_urls"] = [url]
            result["text"] = "[Direktes Bild]"
            return result

        # HTML parsen
        if BS4_OK:
            soup = BeautifulSoup(r.text, "lxml")
            for tag in soup(["nav", "footer", "script", "style", "header", "aside"]):
                tag.decompose()
            raw = soup.get_text(" ", strip=True)
            result["text"] = re.sub(r'\s+', ' ', raw).strip()[:3000]

            base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
            imgs = []
            for img in soup.find_all("img", src=True):
                src = img["src"].strip()
                if src.startswith("data:"):
                    continue
                full = urljoin(base, src)
                if any(x in full.lower() for x in ["logo", "icon", "avatar", "social", "pixel", "track"]):
                    continue
                try:
                    w = img.get("width", "")
                    if w and int(w) < 100:
                        continue
                except (ValueError, TypeError):
                    pass
                imgs.append(full)
                if len(imgs) >= 5:
                    break
            result["image_urls"] = imgs
        else:
            # Fallback ohne BS4
            clean = re.sub(r'<[^>]+>', ' ', r.text)
            result["text"] = re.sub(r'\s+', ' ', clean).strip()[:3000]

    except requests.exceptions.Timeout:
        result["error"] = f"Timeout: {url[:60]}"
    except requests.exceptions.RequestException as e:
        result["error"] = f"Request-Fehler: {e}"
    except Exception as e:
        result["error"] = f"Fehler: {e}"

    return result


# ---------------------------------------------------------------------------
# Schritt 3: Bilder als base64 laden
# ---------------------------------------------------------------------------

def _download_images(image_urls: list, max_images: int = 3) -> list:
    """
    Lädt Bilder herunter.
    Rückgabe: [{"b64": str, "media_type": str, "url": str}]
    """
    results = []
    headers = {**_BROWSER_HEADERS, "Accept": "image/*,*/*;q=0.8"}
    for url in image_urls[:max_images * 2]:  # etwas mehr versuchen wegen Fehlern
        if len(results) >= max_images:
            break
        try:
            r = requests.get(url, headers=headers, timeout=12, stream=True)
            r.raise_for_status()
            ct = r.headers.get("Content-Type", "image/jpeg")
            if not any(t in ct for t in ["image/jpeg", "image/png", "image/webp", "image/gif"]):
                continue
            data = b""
            for chunk in r.iter_content(65536):
                data += chunk
                if len(data) > 2 * 1024 * 1024:  # max 2MB
                    break
            if len(data) < 5000:  # zu klein = kein echtes Foto
                continue
            mt = ct.split(";")[0].strip()
            if mt not in ["image/jpeg", "image/png", "image/webp", "image/gif"]:
                mt = "image/jpeg"
            results.append({"b64": base64.b64encode(data).decode(), "media_type": mt, "url": url})
            print(f"  Bild geladen: {url[:55]}... ({len(data)//1024} KB)")
        except Exception as e:
            print(f"  Bild-Fehler {url[:45]}: {e}")
    return results


# ---------------------------------------------------------------------------
# Haupt-API
# ---------------------------------------------------------------------------

def enrich_email(html: str = "", text: str = "", county_key: str = "pinellas") -> dict:
    """
    Verarbeitet eine Makler-Email vollständig:
      - Links extrahieren & filtern
      - Seiten fetchen (Text + Bild-URLs)
      - Bilder als base64 laden
    
    Rückgabe:
    {
      "extra_text":    str,         # kombinierter Text aller Seiten
      "images":        list[dict],  # [{"b64", "media_type", "url"}]
      "links_found":   list[str],
      "links_fetched": list[str],
    }
    """
    links = _extract_links(html, text)
    print(f"  [enrich] {len(links)} Listing-Links gefunden")
    for l in links:
        print(f"    → {l[:80]}")

    all_img_urls, page_texts, fetched = [], [], []

    for url in links:
        print(f"  [enrich] fetche: {url[:65]}...")
        page = _fetch_page(url)
        if page["error"]:
            print(f"    ✗ {page['error']}")
            continue
        if page["text"]:
            page_texts.append(f"[Von {url[:50]}]:\n{page['text'][:800]}")
        all_img_urls.extend(page["image_urls"])
        fetched.append(url)

    images = _download_images(all_img_urls, max_images=3)

    return {
        "extra_text":    "\n\n".join(page_texts),
        "images":        images,
        "links_found":   links,
        "links_fetched": fetched,
    }
