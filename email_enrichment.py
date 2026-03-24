"""
email_enrichment.py  —  Flip Analyzer · Email-Link-Enrichment v2
=================================================================
Neben server.py ablegen.
In server.py oben: from email_enrichment import enrich_email

NEU in v2 (gegenueber v1):
  - Mailchimp track/click Links werden als Property-CTAs erkannt
    (anhand Anchor-Text wie "Click here to view 4112 W Wallace Ave")
  - 2-Level-Crawl: Email -> Property Page -> Sub-Links (Fotos, PDFs, Sub-Pages)
  - PDF-Links werden heruntergeladen und als base64 an Claude uebergeben
  - campaign-archive.com (Web-Version der Email) wird ausgelesen
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
# Konstanten & Regex-Filter
# ---------------------------------------------------------------------------

_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.9",
    "Accept-Language": "en-US,en;q=0.9",
}

# Anchor-Texte die einen Mailchimp-Tracking-Link als Property-CTA markieren
_CTA_TEXT = re.compile(
    r'view|click here|property|deal|listing|home|house|address|photo|'
    r'mehr infos|details|angebot|objekt|see more|\d{3,5}\s+\w',
    re.IGNORECASE
)

# Harter Noise-Filter (diese URLs niemals fetchen)
_NOISE = re.compile(r"""
    unsubscribe | track/open | vcard\? | profile\? |
    facebook\.com | instagram\.com | linkedin\.com | twitter\.com | youtube\.com |
    schemas\.microsoft\.com | w3\.org | cdn-images\. |
    googletagmanager | google-analytics | mailto: | tel: | ^\#
""", re.VERBOSE | re.IGNORECASE)

# Domains/Muster mit hoher Wahrscheinlichkeit fuer Listing-Inhalt
_LISTING = re.compile(r"""
    drive\.google\.com | dropbox\.com | zillow\.com | redfin\.com |
    realtor\.com | mitchelldean | eydura | networthrealty | networth |
    property | listing | photos | flip | deal | mls | homes | realty |
    campaign-archive\.com
""", re.VERBOSE | re.IGNORECASE)

# Sub-Links auf Property-Pages die sich lohnen zu folgen
_SUBLINK_WORTH = re.compile(r"""
    photo | image | img | gallery | picture | pic | media |
    document | doc | pdf | flyer | brochure | attachment |
    property | listing | detail | view | deal |
    \.pdf$ | \.jpg$ | \.jpeg$ | \.png$ | \.webp$
""", re.VERBOSE | re.IGNORECASE)

_SUBLINK_NOISE = re.compile(r"""
    facebook | instagram | linkedin | twitter | youtube |
    unsubscribe | login | signin | register | mailto | tel:
""", re.VERBOSE | re.IGNORECASE)


# ---------------------------------------------------------------------------
# Schritt 1: Links aus Email extrahieren
# ---------------------------------------------------------------------------

def _extract_links(html: str, text: str) -> list:
    """
    Extrahiert relevante Listing-Links aus Email-HTML und Plaintext.

    Besonderheit v2: Mailchimp track/click Links werden anhand des
    Anchor-Texts als Property-CTAs erkannt und behalten.
    """
    raw_links = []  # [(url, anchor_text), ...]

    if html and BS4_OK:
        try:
            soup = BeautifulSoup(html, "lxml")
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                href = re.sub(r'=\r?\n', '', href).replace('=3D', '=').replace('&amp;', '&')
                anchor = a.get_text(strip=True)[:120]
                if href.startswith("http"):
                    raw_links.append((href, anchor))
        except Exception:
            pass
    elif html:
        for href in re.findall(r'href="(https?://[^"]+)"', html):
            href = re.sub(r'=\r?\n', '', href).replace('=3D', '=').replace('&amp;', '&')
            raw_links.append((href, ""))

    # Aus Plaintext (Fallback oder Ergaenzung)
    for u in re.findall(r'https?://[^\s<>"\'\\)>]+', text or ""):
        raw_links.append((u.rstrip('>').strip(), ""))

    boosted, mid, rest = [], [], []
    seen = set()

    for url, anchor in raw_links:
        url = re.sub(r'=\r?\n', '', url).strip().replace('&amp;', '&')
        key = url[:150]
        if key in seen or not url.startswith("http"):
            continue
        seen.add(key)

        # Harter Noise-Filter
        if _NOISE.search(url):
            continue

        # Mailchimp track/click: nur behalten wenn Anchor-Text Property-CTA
        if "list-manage.com/track/click" in url or "mailchi.mp" in url:
            if _CTA_TEXT.search(anchor):
                boosted.append(url)
            # ohne passenden Anchor-Text weglassen
            continue

        # campaign-archive = Web-Version der Email
        if "campaign-archive.com" in url:
            mid.append(url)
            continue

        # Google Drive, Dropbox, Zillow etc.
        if _LISTING.search(url):
            boosted.append(url)
        else:
            rest.append(url)

    return (boosted + mid + rest)[:6]


# ---------------------------------------------------------------------------
# Schritt 2a: Google Drive Ordner-Bilder extrahieren
# ---------------------------------------------------------------------------

def _gdrive_folder_images(url: str) -> list:
    try:
        r = requests.get(url, headers=_BROWSER_HEADERS, timeout=15, allow_redirects=True)
        if r.status_code != 200:
            return []
        ids, seen_ids, out = re.findall(r'"([a-zA-Z0-9_-]{25,33})"', r.text), set(), []
        for fid in ids:
            if fid not in seen_ids:
                seen_ids.add(fid)
                out.append(f"https://drive.google.com/uc?id={fid}&export=download")
                if len(out) >= 6:
                    break
        return out
    except Exception as e:
        print(f"  GDrive folder: {e}")
        return []


# ---------------------------------------------------------------------------
# Schritt 2b: Sub-Links einer Property-Page extrahieren
# ---------------------------------------------------------------------------

def _extract_sublinks(html: str, base_url: str) -> dict:
    """
    Extrahiert aus dem HTML einer Property-Page:
      image_urls: direkte Bild-URLs
      pdf_urls:   PDF-Links
      page_urls:  weitere HTML-Seiten die nach Property-Inhalt klingen
    """
    result = {"image_urls": [], "pdf_urls": [], "page_urls": []}
    if not BS4_OK or not html:
        return result

    try:
        soup = BeautifulSoup(html, "lxml")
        parsed_base = urlparse(base_url)
        base = f"{parsed_base.scheme}://{parsed_base.netloc}"
        seen = set()

        # <img> Tags
        for img in soup.find_all("img", src=True):
            src = img["src"].strip()
            if src.startswith("data:"):
                continue
            full = urljoin(base, src)
            if any(x in full.lower() for x in ["logo", "icon", "avatar", "social",
                                                 "pixel", "track", "blank", "spacer", "arrow"]):
                continue
            try:
                w = img.get("width", "")
                if w and int(w) < 100:
                    continue
            except (ValueError, TypeError):
                pass
            if full not in seen:
                seen.add(full)
                result["image_urls"].append(full)

        # <a> Tags
        for a in soup.find_all("a", href=True):
            href = a["href"].strip().replace('&amp;', '&')
            if not href.startswith("http"):
                href = urljoin(base, href)
            if not href.startswith("http") or href in seen:
                continue
            if _SUBLINK_NOISE.search(href):
                continue
            seen.add(href)
            anchor = a.get_text(strip=True).lower()

            if href.lower().endswith(".pdf") or "pdf" in anchor or "document" in anchor or "flyer" in anchor:
                result["pdf_urls"].append(href)
            elif any(href.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]):
                result["image_urls"].append(href)
            elif _SUBLINK_WORTH.search(href) or _SUBLINK_WORTH.search(anchor):
                href_host = urlparse(href).netloc
                if href_host == parsed_base.netloc or _LISTING.search(href):
                    result["page_urls"].append(href)

        result["image_urls"] = result["image_urls"][:8]
        result["pdf_urls"]   = result["pdf_urls"][:3]
        result["page_urls"]  = result["page_urls"][:3]

    except Exception as e:
        print(f"  Sublink-Extraktion Fehler: {e}")

    return result


# ---------------------------------------------------------------------------
# Schritt 2c: Eine URL fetchen
# ---------------------------------------------------------------------------

def _fetch_page(url: str, follow_sublinks: bool = False) -> dict:
    """
    Fetcht eine URL mit Redirect-Folgen.

    follow_sublinks=True: analysiert die Seite zusaetzlich auf
    Sub-Links (Fotos, PDFs, weitere Property-Seiten).

    Rueckgabe:
    {
      "text":       str,
      "image_urls": list[str],
      "pdf_urls":   list[str],
      "page_urls":  list[str],
      "final_url":  str,
      "error":      str|None,
    }
    """
    result = {
        "text": "", "image_urls": [], "pdf_urls": [],
        "page_urls": [], "final_url": url, "error": None,
    }

    # Google Drive Ordner
    if "drive.google.com/folder" in url or "drive.google.com/drive/folder" in url:
        imgs = _gdrive_folder_images(url)
        result["text"] = f"[Google Drive Ordner - {len(imgs)} Bilder gefunden]"
        result["image_urls"] = imgs
        return result

    # Google Drive Direktdownload
    if "drive.google.com/uc" in url:
        result["image_urls"] = [url]
        result["text"] = "[Google Drive direktes Bild]"
        return result

    try:
        r = requests.get(url, headers=_BROWSER_HEADERS, timeout=18, allow_redirects=True)
        r.raise_for_status()
        result["final_url"] = r.url
        ct = r.headers.get("Content-Type", "")

        # Direktes Bild
        if any(t in ct for t in ["image/jpeg", "image/png", "image/webp", "image/gif"]):
            result["image_urls"] = [r.url]
            result["text"] = "[Direktes Bild]"
            return result

        # Direktes PDF
        if "application/pdf" in ct or r.url.lower().endswith(".pdf"):
            result["pdf_urls"] = [r.url]
            result["text"] = "[Direktes PDF]"
            return result

        # HTML verarbeiten
        html = r.text

        if BS4_OK:
            soup = BeautifulSoup(html, "lxml")
            for tag in soup(["nav", "footer", "script", "style", "header", "aside"]):
                tag.decompose()
            raw = soup.get_text(" ", strip=True)
            result["text"] = re.sub(r'\s+', ' ', raw).strip()[:3000]

            base = f"{urlparse(r.url).scheme}://{urlparse(r.url).netloc}"
            imgs = []
            for img in soup.find_all("img", src=True):
                src = img["src"].strip()
                if src.startswith("data:"):
                    continue
                full = urljoin(base, src)
                if any(x in full.lower() for x in ["logo", "icon", "avatar", "social",
                                                     "pixel", "track", "blank", "spacer"]):
                    continue
                try:
                    w = img.get("width", "")
                    if w and int(w) < 100:
                        continue
                except (ValueError, TypeError):
                    pass
                imgs.append(full)
                if len(imgs) >= 6:
                    break
            result["image_urls"] = imgs
        else:
            clean = re.sub(r'<[^>]+>', ' ', html)
            result["text"] = re.sub(r'\s+', ' ', clean).strip()[:3000]

        # Sub-Links extrahieren (Level 2)
        if follow_sublinks and BS4_OK:
            subs = _extract_sublinks(html, r.url)
            for u in subs["image_urls"]:
                if u not in result["image_urls"]:
                    result["image_urls"].append(u)
            result["pdf_urls"]  = subs["pdf_urls"]
            result["page_urls"] = subs["page_urls"]

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

def _download_images(image_urls: list, max_images: int = 4) -> list:
    """Rückgabe: [{"b64": str, "media_type": str, "url": str}]"""
    results = []
    headers = {**_BROWSER_HEADERS, "Accept": "image/*,*/*;q=0.8"}
    for url in image_urls[:max_images * 3]:
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
                if len(data) > 2 * 1024 * 1024:
                    break
            if len(data) < 5000:
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
# Schritt 4: PDFs als base64 laden
# ---------------------------------------------------------------------------

def _download_pdfs(pdf_urls: list, max_pdfs: int = 2) -> list:
    """Rückgabe: [{"b64": str, "url": str}]"""
    results = []
    for url in pdf_urls[:max_pdfs]:
        try:
            r = requests.get(url, headers=_BROWSER_HEADERS, timeout=20, stream=True)
            r.raise_for_status()
            ct = r.headers.get("Content-Type", "")
            if "pdf" not in ct.lower() and not url.lower().endswith(".pdf"):
                continue
            data = b""
            for chunk in r.iter_content(65536):
                data += chunk
                if len(data) > 10 * 1024 * 1024:
                    break
            if len(data) < 1000:
                continue
            results.append({"b64": base64.b64encode(data).decode(), "url": url})
            print(f"  PDF geladen: {url[:55]}... ({len(data)//1024} KB)")
        except Exception as e:
            print(f"  PDF-Fehler {url[:45]}: {e}")
    return results


# ---------------------------------------------------------------------------
# Haupt-API
# ---------------------------------------------------------------------------

def enrich_email(html: str = "", text: str = "", county_key: str = "pinellas") -> dict:
    """
    Verarbeitet eine Makler-Email vollstaendig (2-Level-Crawl).

    Ablauf:
      Level 1 - Relevante Links aus Email fetchen (Mailchimp-CTA-Redirects folgen)
      Level 2 - Sub-Links der Property-Pages folgen (Fotos, PDFs, weitere Seiten)

    Unterstuetzte Makler-Muster:
      - Mitchell Dean Realty: Google Drive Ordner mit Fotos
      - NetWorth Realty: Mailchimp track/click -> cash3.networthrealtyusa.net
      - Generisch: Alle Makler-Seiten mit Immobilien-Listings

    Rueckgabe:
    {
      "extra_text":    str,          # kombinierter Text aller Seiten
      "images":        list[dict],   # [{"b64", "media_type", "url"}]
      "pdfs":          list[dict],   # [{"b64", "url"}]
      "links_found":   list[str],
      "links_fetched": list[str],
    }
    """
    # ── Level 1: Email-Links identifizieren und fetchen ─────────────────────
    links = _extract_links(html, text)
    print(f"  [enrich v2] {len(links)} Listing-Links gefunden")
    for l in links:
        print(f"    -> {l[:90]}")

    all_img_urls, all_pdf_urls, page_texts, fetched = [], [], [], []

    for url in links:
        print(f"  [L1] fetche: {url[:70]}...")
        page = _fetch_page(url, follow_sublinks=True)

        if page["error"]:
            print(f"    x {page['error']}")
            continue

        fetched.append(url)
        final_url = page["final_url"]
        if final_url != url:
            print(f"    -> Redirect zu: {final_url[:70]}")

        if page["text"]:
            label = final_url[:55] if final_url != url else url[:55]
            page_texts.append(f"[Von {label}]:\n{page['text'][:1000]}")

        all_img_urls.extend(page["image_urls"])
        all_pdf_urls.extend(page["pdf_urls"])

        # ── Level 2: Sub-Pages der Property-Page ────────────────────────────
        for sub_url in page.get("page_urls", []):
            print(f"  [L2] fetche sub-page: {sub_url[:70]}...")
            sub = _fetch_page(sub_url, follow_sublinks=False)
            if sub["error"]:
                print(f"    x {sub['error']}")
                continue
            if sub["text"]:
                page_texts.append(f"[Sub-Seite {sub_url[:45]}]:\n{sub['text'][:600]}")
            all_img_urls.extend(sub["image_urls"])
            all_pdf_urls.extend(sub["pdf_urls"])

    # Deduplizieren
    all_img_urls = list(dict.fromkeys(all_img_urls))
    all_pdf_urls = list(dict.fromkeys(all_pdf_urls))

    # Bilder + PDFs herunterladen
    images = _download_images(all_img_urls, max_images=4)
    pdfs   = _download_pdfs(all_pdf_urls,   max_pdfs=2)

    print(f"  [enrich v2] Fertig: {len(fetched)} Seiten, "
          f"{len(images)} Bilder, {len(pdfs)} PDFs")

    return {
        "extra_text":    "\n\n".join(page_texts),
        "images":        images,
        "pdfs":          pdfs,
        "links_found":   links,
        "links_fetched": fetched,
    }
