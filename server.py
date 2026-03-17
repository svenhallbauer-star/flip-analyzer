"""
FLIP ANALYZER - Backend Server
Tampa Bay Fix & Flip Tool
Datenquelle: Redfin (kein API-Key nötig)
Läuft lokal auf http://localhost:5000
"""

from flask import Flask, jsonify, request, send_from_directory
from training_data import get_training_context, get_full_training_context, RENOVATION_BENCHMARKS, ARV_BENCHMARKS
from flask_cors import CORS
import requests
import os
import json
import time

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY", "")
RAPIDAPI_KEY   = os.environ.get("RAPIDAPI_KEY", "")

def get_anthropic_key():
    """Liest den API-Key zuerst aus der Env-Variable, dann aus dem globalen Fallback."""
    return os.environ.get("ANTHROPIC_KEY", "") or ANTHROPIC_KEY

COUNTY_CONFIG = {
    "pinellas": {
        "name": "Pinellas County, FL",
        "redfin_region_id": "2480",
        "redfin_region_type": "5",
        "median_sqft": 220,
        "arv_low": 200, "arv_high": 265,
        "median_price": 413000,
        "avg_dom": 62,
        "below_ask": 55,
        "yoy": "+4.6%"
    },
    "hillsborough": {
        "name": "Hillsborough County, FL",
        "redfin_region_id": "464",
        "redfin_region_type": "5",
        "median_sqft": 232,
        "arv_low": 215, "arv_high": 280,
        "median_price": 408000,
        "avg_dom": 61,
        "below_ask": 58,
        "yoy": "+1.9%"
    },
    "pasco": {
        "name": "Pasco County, FL",
        "redfin_region_id": "487",
        "redfin_region_type": "5",
        "median_sqft": 194,
        "arv_low": 175, "arv_high": 225,
        "median_price": 350000,
        "avg_dom": 69,
        "below_ask": 63,
        "yoy": "+2.0%"
    }
}

REDFIN_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.redfin.com/",
    "Origin": "https://www.redfin.com"
}

def _anthropic_post(payload, timeout=55):
    """Anthropic API call mit automatischem Retry bei 429."""
    key = get_anthropic_key()
    headers = {
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    for attempt in range(3):
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload,
            timeout=timeout
        )
        if resp.status_code == 429:
            wait = 20 * (attempt + 1)  # 20s, 40s, 60s
            print(f"Rate limit 429 — warte {wait}s (Versuch {attempt+1}/3)")
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return resp
    resp.raise_for_status()
    return resp


# ── Routen ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("templates", "index.html")

@app.route("/api/config", methods=["GET"])
def get_config():
    return jsonify({
        "anthropic_configured": bool(get_anthropic_key()),
        "data_source": "redfin",
        "counties": list(COUNTY_CONFIG.keys())
    })

@app.route("/api/config", methods=["POST"])
def set_config():
    global ANTHROPIC_KEY
    data = request.json or {}
    if data.get("anthropic_key"):
        ANTHROPIC_KEY = data["anthropic_key"]
        os.environ["ANTHROPIC_KEY"] = ANTHROPIC_KEY
    return jsonify({"ok": True, "anthropic": bool(get_anthropic_key())})


@app.route("/api/search", methods=["POST"])
def search_listings():
    data       = request.json or {}
    county_key = data.get("county", "pinellas")
    min_price  = int(data.get("min_price", 100000))
    max_price  = int(data.get("max_price", 500000))
    min_beds   = int(data.get("min_beds", 3))
    max_dom    = int(data.get("max_dom", 90))
    county     = COUNTY_CONFIG.get(county_key)

    if not county:
        return jsonify({"error": "Unbekannter County"}), 400

    rapidapi_key = os.environ.get("RAPIDAPI_KEY", "")

    if rapidapi_key:
        try:
            listings = _fetch_rapidapi(county, min_price, max_price, min_beds, max_dom, rapidapi_key)
            if listings:
                return jsonify({"source": "zillow_live", "results": listings})
        except Exception as e:
            print(f"RapidAPI Fehler: {e}")

    # Fallback: Redfin
    try:
        listings = _fetch_redfin(county, min_price, max_price, min_beds, max_dom)
        if listings:
            return jsonify({"source": "redfin_live", "results": listings})
    except Exception as e:
        print(f"Redfin Fehler: {e}")

    return jsonify({"source": "demo", "results": _demo_listings(county_key),
                    "warning": "Keine Live-Daten verfügbar — Demo-Modus."})


def _fetch_rapidapi(county, min_price, max_price, min_beds, max_dom, api_key):
    """Ruft Listings über RapidAPI Real-Time Real-Estate Data ab."""

    # Determine city/state from county
    location_map = {
        "pinellas":     "Pinellas County, FL",
        "hillsborough": "Hillsborough County, FL",
        "pasco":        "Pasco County, FL"
    }
    county_key = [k for k, v in COUNTY_CONFIG.items() if v == county][0]
    location   = location_map.get(county_key, "Pinellas County, FL")

    url = "https://real-time-real-estate-data.p.rapidapi.com/search"
    params = {
        "location":     location,
        "home_status":  "FOR_SALE",
        "listing_type": "BY_AGENT",
        "sort":         "DEFAULT",
        "min_price":    str(min_price),
        "max_price":    str(max_price),
        "beds_min":     str(min_beds),
        "home_type":    "SINGLE_FAMILY"
    }
    headers = {
        "x-rapidapi-host": "real-time-real-estate-data.p.rapidapi.com",
        "x-rapidapi-key":  api_key
    }

    resp = requests.get(url, headers=headers, params=params, timeout=20)
    print(f"RapidAPI Status: {resp.status_code}")
    print(f"RapidAPI Response: {resp.text[:500]}")
    resp.raise_for_status()
    data = resp.json()

    # Try different response structures
    homes = []
    if isinstance(data, list):
        homes = data
    elif isinstance(data, dict):
        for key in ["data", "results", "properties", "homes", "listings"]:
            val = data.get(key)
            if val and isinstance(val, list):
                homes = val
                break
            elif val and isinstance(val, dict):
                for k2 in ["results", "properties", "homes"]:
                    if val.get(k2):
                        homes = val[k2]
                        break

    listings = []
    for h in homes:
        try:
            price    = h.get("price", h.get("listPrice", 0))
            sqft     = h.get("livingArea", h.get("sqft", h.get("square_feet", 0)))
            beds     = h.get("bedrooms", h.get("beds", 0))
            baths    = h.get("bathrooms", h.get("baths", 0))
            year     = h.get("yearBuilt", h.get("year_built", 0))
            dom      = h.get("daysOnZillow", h.get("days_on_market", h.get("dom", 0)))
            street   = h.get("streetAddress", h.get("address", ""))
            city     = h.get("city", "")
            state    = h.get("state", "FL")
            zipcode  = h.get("zipcode", h.get("zip_code", ""))
            address  = f"{street}, {city}, {state} {zipcode}".strip(", ")
            url_prop = h.get("url", h.get("property_url", ""))
            if url_prop and not url_prop.startswith("http"):
                url_prop = "https://www.zillow.com" + url_prop

            price = int(price) if price else 0
            sqft  = int(sqft)  if sqft  else 0
            if not price or not sqft:
                continue
            if dom and int(dom) > max_dom:
                continue

            listings.append({
                "address":    address or "Adresse nicht verfügbar",
                "price":      price,
                "beds":       int(beds)   if beds  else 0,
                "baths":      float(baths) if baths else 0,
                "sqft":       sqft,
                "year_built": int(year) if year else 0,
                "dom":        int(dom)  if dom  else 0,
                "zestimate":  0,
                "price_sqft": round(price / sqft) if sqft else 0,
                "county":     county_key,
                "listing_url": url_prop,
                "source":     "zillow"
            })
        except Exception as e:
            print(f"RapidAPI Parse-Fehler: {e}")
            continue

    return listings[:12]


def _fetch_redfin(county, min_price, max_price, min_beds, max_dom):
    """Ruft aktuelle Listings von Redfin ab."""

    # Schritt 1: Region-ID für Redfin-Suche bestimmen
    region_id   = county["redfin_region_id"]
    region_type = county["redfin_region_type"]

    # Schritt 2: Redfin Stingray API (inoffizielle JSON-API)
    url = "https://www.redfin.com/stingray/api/gis"
    params = {
        "al": "1",
        "has_deal": "false",
        "has_dishwasher": "false",
        "has_laundry_facility": "false",
        "has_laundry_hookups": "false",
        "has_parking": "false",
        "has_pool": "false",
        "has_short_term_lease": "false",
        "include_pending_homes": "false",
        "isRentals": "false",
        "is_furnished": "false",
        "is_income_restricted": "false",
        "is_senior_living": "false",
        "market": "florida",
        "max_price": str(max_price),
        "min_beds": str(min_beds),
        "min_price": str(min_price),
        "num_beds": str(min_beds),
        "num_homes": "50",
        "ord": "days-on-redfin-asc",
        "page_number": "1",
        "property_type": "1",   # 1 = Single Family
        "region_id": region_id,
        "region_type": region_type,
        "sf": "1,2,3,5,6,7",
        "start": "0",
        "status": "9",          # For Sale
        "uipt": "1",
        "v": "8"
    }

    resp = requests.get(url, headers=REDFIN_HEADERS, params=params, timeout=20)
    resp.raise_for_status()

    # Redfin gibt "{}&&" vor dem JSON zurück — bereinigen
    raw_text = resp.text
    if raw_text.startswith("{}&&"):
        raw_text = raw_text[4:]

    raw = json.loads(raw_text)
    homes = raw.get("payload", {}).get("homes", [])

    listings = []
    for h in homes:
        try:
            hd = h.get("homeData", h)

            price_info  = hd.get("priceInfo", {})
            size_info   = hd.get("sqFtInfo", {})
            beds_info   = hd.get("beds", 0)
            baths_info  = hd.get("baths", 0)
            year_info   = hd.get("yearBuilt", {})
            dom_info    = hd.get("dom", {})
            address     = hd.get("addressInfo", {})

            price = price_info.get("amount", 0) if isinstance(price_info, dict) else price_info
            sqft  = size_info.get("value", 0)   if isinstance(size_info, dict)  else size_info
            year  = year_info.get("value", 0)   if isinstance(year_info, dict)  else year_info
            dom   = dom_info.get("value", 0)    if isinstance(dom_info, dict)   else dom_info
            beds  = beds_info if isinstance(beds_info, (int,float)) else beds_info.get("value", 0) if isinstance(beds_info, dict) else 0
            baths = baths_info if isinstance(baths_info, (int,float)) else baths_info.get("value", 0) if isinstance(baths_info, dict) else 0

            street  = address.get("streetLine", {}).get("value", "") if isinstance(address, dict) else ""
            city    = address.get("city", "")    if isinstance(address, dict) else ""
            state   = address.get("state", "FL") if isinstance(address, dict) else "FL"
            zipcode = address.get("zip", "")     if isinstance(address, dict) else ""
            full_addr = f"{street}, {city}, {state} {zipcode}".strip(", ")

            url_path = hd.get("url", "")
            zillow_url = f"https://www.redfin.com{url_path}" if url_path else ""

            if not price or not sqft:
                continue
            if dom > max_dom:
                continue

            listings.append({
                "address":      full_addr or "Adresse nicht verfügbar",
                "price":        int(price),
                "beds":         int(beds),
                "baths":        float(baths),
                "sqft":         int(sqft),
                "year_built":   int(year) if year else 0,
                "dom":          int(dom),
                "zestimate":    0,
                "price_sqft":   round(price / sqft) if sqft else 0,
                "county":       list(COUNTY_CONFIG.keys())[[c["redfin_region_id"] for c in COUNTY_CONFIG.values()].index(region_id)],
                "listing_url":  zillow_url,
                "source":       "redfin"
            })
        except Exception as e:
            print(f"Parse-Fehler bei Listing: {e}")
            continue

    return listings[:12]


import base64
import imaplib
import email as email_lib
from email.header import decode_header


@app.route("/api/analyze-pdf", methods=["POST"])
def analyze_pdf():
    data       = request.json or {}
    pdf_b64    = data.get("data", "")
    filename   = data.get("filename", "dokument.pdf")
    county_key = data.get("county_key", "pinellas")
    county     = COUNTY_CONFIG.get(county_key, COUNTY_CONFIG["pinellas"])

    if not get_anthropic_key():
        return jsonify({"error": "Anthropic API-Key nicht konfiguriert."}), 400
    if not pdf_b64:
        return jsonify({"error": "Keine PDF-Daten erhalten."}), 400

    prompt = f"""Analysiere dieses Immobilien-Dokument (Exposé / MLS-Sheet) für {county['name']}.

Extrahiere alle verfügbaren Immobiliendaten und gib sie als JSON zurück.
Wenn Daten fehlen, schätze vernünftige Werte basierend auf dem Markt.

Antworte NUR mit validem JSON (kein Markdown):
{{
  "address": "<Straße, Stadt, State ZIP>",
  "price": <Listenpreis als Zahl>,
  "beds": <Schlafzimmer>,
  "baths": <Bäder>,
  "sqft": <Wohnfläche>,
  "year_built": <Baujahr>,
  "dom": <Days on Market oder 0>,
  "price_sqft": <Preis pro sqft>,
  "county": "{county_key}",
  "listing_url": "<URL falls vorhanden, sonst leer>",
  "source": "pdf",
  "notes": "<wichtige Infos aus dem Dokument: Zustand, Besonderheiten, Flood Zone, etc.>",
  "zestimate": 0
}}"""

    try:
        resp = _anthropic_post({
                "model": "claude-sonnet-4-5",
                "max_tokens": 1000,
                "messages": [{
                    "role": "user",
                    "content": [
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": pdf_b64
                            }
                        },
                        {"type": "text", "text": prompt}
                    ]
                }]
            })
        resp.raise_for_status()
        raw = resp.json()["content"][0]["text"]
        raw = raw.replace("```json", "").replace("```", "").strip()
        listing = json.loads(raw)
        return jsonify({"listing": listing})
    except Exception as e:
        return jsonify({"error": f"PDF-Analyse fehlgeschlagen: {e}"}), 500


@app.route("/api/analyze-email", methods=["POST"])
def analyze_email():
    data       = request.json or {}
    email_text = data.get("email_text", "")
    county_key = data.get("county_key", "pinellas")
    county     = COUNTY_CONFIG.get(county_key, COUNTY_CONFIG["pinellas"])

    if not get_anthropic_key():
        return jsonify({"error": "Anthropic API-Key nicht konfiguriert."}), 400

    prompt = f"""Analysiere diesen Email-Text von einem Makler oder einer Immobilien-Plattform.
Extrahiere alle Immobilien-Listings die du findest.

Markt: {county['name']} (ARV ${county['arv_low']}–${county['arv_high']}/sqft)

Antworte NUR mit validem JSON (kein Markdown):
{{
  "listings": [
    {{
      "address": "<Adresse>",
      "price": <Preis>,
      "beds": <Beds>,
      "baths": <Baths>,
      "sqft": <sqft oder 0>,
      "year_built": <Jahr oder 0>,
      "dom": 0,
      "price_sqft": <oder 0>,
      "county": "{county_key}",
      "listing_url": "<URL falls vorhanden>",
      "source": "email",
      "notes": "<Zusatzinfos>",
      "zestimate": 0
    }}
  ]
}}

Email-Text:
{email_text[:4000]}"""

    try:
        resp = _anthropic_post({
                "model": "claude-sonnet-4-5",
                "max_tokens": 1500,
                "system": "Du bist Immobilien-Daten-Extraktor. Antworte NUR mit validem JSON.",
                "messages": [{"role": "user", "content": prompt}]
            })
        resp.raise_for_status()
        raw = resp.json()["content"][0]["text"]
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/scan-imap", methods=["POST"])
def scan_imap():
    data       = request.json or {}
    host       = data.get("host", "imap.gmail.com")
    port       = int(data.get("port", 993))
    user       = data.get("user", "")
    password   = data.get("password", "")
    query      = data.get("query", "redfin.com OR zillow.com")
    county_key = data.get("county_key", "pinellas")

    if not user or not password:
        return jsonify({"error": "Email und Passwort erforderlich."}), 400

    try:
        mail = imaplib.IMAP4_SSL(host, port)
        mail.login(user, password)
        mail.select("INBOX")

        # Search last 30 days for real estate emails
        _, msg_ids = mail.search(None, 'SINCE "01-Jan-2026"')
        ids = msg_ids[0].split()[-20:]  # last 20 matching emails

        email_texts = []
        for mid in ids:
            _, msg_data = mail.fetch(mid, "(RFC822)")
            msg = email_lib.message_from_bytes(msg_data[0][1])
            subject = decode_header(msg["Subject"] or "")[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode(errors="ignore")
            sender  = msg.get("From", "")

            # Filter by query keywords
            keywords = [q.strip().lower() for q in query.replace(" OR ", "|").split("|")]
            combined = (subject + sender).lower()
            if not any(kw in combined for kw in keywords):
                continue

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors="ignore")[:2000]
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors="ignore")[:2000]

            email_texts.append(f"Von: {sender}\nBetreff: {subject}\n\n{body}")

        mail.logout()

        if not email_texts:
            return jsonify({"listings": [], "message": "Keine passenden Emails gefunden."})

        # Analyze combined email content
        combined_text = "\n\n---\n\n".join(email_texts[:5])
        inner_resp = requests.post(
            f"http://localhost:{os.environ.get('PORT', 5000)}/api/analyze-email",
            json={"email_text": combined_text, "county_key": county_key},
            timeout=55
        )
        return inner_resp.json()

    except imaplib.IMAP4.error as e:
        return jsonify({"error": f"IMAP-Fehler: {e}. Bitte App-Passwort prüfen."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/api/analyze", methods=["POST"])
def analyze_listing():
    data       = request.json or {}
    listing    = data.get("listing", {})
    county_key = data.get("county_key", "pinellas")
    county     = COUNTY_CONFIG.get(county_key, COUNTY_CONFIG["pinellas"])

    if not get_anthropic_key():
        return jsonify({"error": "Anthropic API-Key nicht konfiguriert. Bitte oben eintragen."}), 400

    from training_data import DEAL_1_CONDITION_AT_PURCHASE
    training_ctx = get_full_training_context()
    
    # Erweiterte Lernkontext aus Bildanalyse Deal 1
    visual_insights = f"""
VISUELLE LERNMUSTER AUS DEAL 1 (Ontario Dr — Schimmel/Fluthaus → 20k Verkauf):
- Massiver Schimmelbefall (Flutmarken sichtbar) + Flood Zone AE = Ankauf für 0k möglich
- Schimmelremediation kalkulierbar: .000-15.000 professionell
- Waterfront-Lage rechtfertigt trotzdem 47/sqft ARV in Pasco
- Außenverkleidung komplett defekt (T1-11 Holzsiding) → Stucco/Neubeplankung -12k
- Florida Room mit Vollschimmel → Entkernung + Neubau -10k
- Alle Böden entfernt, nackte Betonplatten = typisch nach Flut → LVP /sqft
- HVAC nicht vorhanden = immer -5k einplanen bei Flutobjekten
- Elektrische Anlage veraltet = -5k Misc Electric

KONDITIONS-SCORING SYSTEM (aus echten Deals gelernt):
- Schimmel bodennah (<30cm): MUSS Remediation, +.000-5.000 auf Reno
- Schimmel flächig (>50% einer Wand): MUSS Remediation, +.000-15.000
- Flutmarken sichtbar: Strukturprüfung + Remediation zwingend
- Decke durchhängend/Wasserflecken: Dachkontrolle + Reparatur
- Böden entfernt/nackt: Vorarbeit bereits gemacht, spart Entsorgung
- Küche 70er-Original: Komplettaustausch 0.000-15.000
- Bad Original (>1990): .500-5.000 pro Bad
"""
    training_ctx = training_ctx + visual_insights
    prompt = f"""Analysiere dieses Fix-and-Flip Objekt für {county['name']} (Q1 2026):

{training_ctx}
=== NEUE ANALYSE ===

MARKTDATEN {county['name']}:
- Median Preis: ${county['median_price']:,}
- Median $/sqft: ${county['median_sqft']}
- ARV-Spanne: ${county['arv_low']}–${county['arv_high']}/sqft
- Ø Days on Market: {county['avg_dom']} Tage
- {county['below_ask']}% verkaufen unter Listenpreis
- YoY: {county['yoy']}

OBJEKT:
- Adresse: {listing.get('address', 'unbekannt')}
- Angebotspreis: ${listing.get('price', 0):,}
- Wohnfläche: {listing.get('sqft', 0)} sqft
- Baujahr: {listing.get('year_built', 'unbekannt')}
- {listing.get('beds', 0)}bd / {listing.get('baths', 0)}ba
- Days on Market: {listing.get('dom', 0)}
{f"- Notizen: {listing.get('notes', '')}" if listing.get('notes') else ""}

Antworte NUR mit validem JSON (kein Markdown, kein Text außerhalb):
{{
  "deal_score": <0-100>,
  "verdict": "GO|NO-GO|MAYBE",
  "verdict_reason": "<2 Sätze auf Deutsch>",
  "arv": <Zahl>,
  "arv_per_sqft": <Zahl>,
  "max_purchase_price": <ARV mal 0.70 minus Renovierungskosten>,
  "price_delta": <Angebotspreis minus max_purchase_price>,
  "renovation_total": <Zahl>,
  "estimated_profit": <Zahl>,
  "roi_percent": <Zahl>,
  "holding_costs": <Zahl>,
  "closing_costs": <Zahl>,
  "renovation_items": [
    {{"name": "Küche", "cost": <Zahl>, "priority": "MUSS", "condition": "schlecht"}},
    {{"name": "Bäder", "cost": <Zahl>, "priority": "MUSS", "condition": "mittel"}},
    {{"name": "Dach", "cost": <Zahl>, "priority": "MUSS", "condition": "mittel"}},
    {{"name": "HVAC", "cost": <Zahl>, "priority": "MUSS", "condition": "unklar"}},
    {{"name": "Böden", "cost": <Zahl>, "priority": "SOLL", "condition": "mittel"}},
    {{"name": "Außen / Curb Appeal", "cost": <Zahl>, "priority": "KANN", "condition": "mittel"}}
  ],
  "comps": [
    {{"address": "<echte Straße in {county['name']}>", "sale_price": <Zahl>, "sqft": <Zahl>, "days_ago": <1-90>, "beds_baths": "3/2"}},
    {{"address": "<echte Straße>", "sale_price": <Zahl>, "sqft": <Zahl>, "days_ago": <1-90>, "beds_baths": "3/2"}},
    {{"address": "<echte Straße>", "sale_price": <Zahl>, "sqft": <Zahl>, "days_ago": <1-90>, "beds_baths": "3/2"}}
  ],
  "market_insights": "<2-3 Sätze auf Deutsch zum aktuellen Markt in {county['name']}>",
  "risk_flags": ["<Risiko auf Deutsch>", "<Risiko auf Deutsch>"],
  "opportunities": ["<Chance auf Deutsch>", "<Chance auf Deutsch>"]
}}"""

    try:
        resp = _anthropic_post({
                "model": "claude-sonnet-4-5",
                "max_tokens": 2000,
                "system": "Du bist Fix-and-Flip Analyst Tampa Bay Florida. Antworte NUR mit validem JSON.",
                "messages": [{"role": "user", "content": prompt}]
            })
        resp.raise_for_status()
        raw = resp.json()["content"][0]["text"]
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Demo-Daten ─────────────────────────────────────────────────────────────────
def _demo_listings(county_key):
    demos = {
        "pinellas": [
            {"address": "4821 Burlington Ave N, St. Petersburg, FL 33713", "price": 285000, "beds": 3, "baths": 1, "sqft": 1240, "year_built": 1956, "dom": 47, "zestimate": 0, "price_sqft": 230, "county": "pinellas", "listing_url": "https://www.redfin.com/county/488/FL/Pinellas-County", "source": "demo"},
            {"address": "1633 44th St S, St. Petersburg, FL 33711",        "price": 219000, "beds": 3, "baths": 1, "sqft": 1050, "year_built": 1952, "dom": 72, "zestimate": 0, "price_sqft": 209, "county": "pinellas", "listing_url": "", "source": "demo"},
            {"address": "2218 Sunset Dr, Clearwater, FL 33765",            "price": 349000, "beds": 4, "baths": 2, "sqft": 1620, "year_built": 1968, "dom": 33, "zestimate": 0, "price_sqft": 215, "county": "pinellas", "listing_url": "", "source": "demo"},
            {"address": "919 Harold Ave NE, Largo, FL 33771",              "price": 265000, "beds": 3, "baths": 2, "sqft": 1380, "year_built": 1972, "dom": 58, "zestimate": 0, "price_sqft": 192, "county": "pinellas", "listing_url": "", "source": "demo"},
        ],
        "hillsborough": [
            {"address": "3412 W Estrella St, Tampa, FL 33629",  "price": 385000, "beds": 3, "baths": 2, "sqft": 1540, "year_built": 1963, "dom": 41, "zestimate": 0, "price_sqft": 250, "county": "hillsborough", "listing_url": "", "source": "demo"},
            {"address": "8204 Causeway Blvd, Tampa, FL 33619",  "price": 229000, "beds": 3, "baths": 1, "sqft": 1180, "year_built": 1958, "dom": 88, "zestimate": 0, "price_sqft": 194, "county": "hillsborough", "listing_url": "", "source": "demo"},
            {"address": "1019 Elm Dr, Brandon, FL 33511",       "price": 298000, "beds": 4, "baths": 2, "sqft": 1720, "year_built": 1978, "dom": 55, "zestimate": 0, "price_sqft": 173, "county": "hillsborough", "listing_url": "", "source": "demo"},
            {"address": "5517 Linebaugh Ave, Tampa, FL 33624",  "price": 312000, "beds": 3, "baths": 2, "sqft": 1460, "year_built": 1981, "dom": 29, "zestimate": 0, "price_sqft": 214, "county": "hillsborough", "listing_url": "", "source": "demo"},
        ],
        "pasco": [
            {"address": "6215 Drexel Rd, New Port Richey, FL 34653",        "price": 198000, "beds": 3, "baths": 2, "sqft": 1320, "year_built": 1975, "dom": 91, "zestimate": 0, "price_sqft": 150, "county": "pasco", "listing_url": "", "source": "demo"},
            {"address": "22847 Settlers Trail, Land O Lakes, FL 34639",     "price": 315000, "beds": 4, "baths": 2, "sqft": 1890, "year_built": 1988, "dom": 44, "zestimate": 0, "price_sqft": 167, "county": "pasco", "listing_url": "", "source": "demo"},
            {"address": "3308 Hidden Lake Dr, Wesley Chapel, FL 33544",     "price": 378000, "beds": 4, "baths": 3, "sqft": 2100, "year_built": 1999, "dom": 29, "zestimate": 0, "price_sqft": 180, "county": "pasco", "listing_url": "", "source": "demo"},
            {"address": "7741 Honeymoon Lake Dr, New Port Richey, FL 34655","price": 225000, "beds": 3, "baths": 2, "sqft": 1410, "year_built": 1979, "dom": 67, "zestimate": 0, "price_sqft": 160, "county": "pasco", "listing_url": "", "source": "demo"},
        ]
    }
    return demos.get(county_key, demos["pinellas"])


if __name__ == "__main__":
    print("\n" + "="*55)
    print("  FLIP ANALYZER — Tampa Bay")
    print("  Datenquelle: Redfin (kein API-Key nötig)")
    print("  Server läuft auf: http://localhost:5000")
    print("="*55)
    print(f"  Anthropic Key: {'✓ konfiguriert' if ANTHROPIC_KEY else '✗ fehlt (in App eintragen)'}")
    print("="*55 + "\n")
    app.run(debug=True, port=5000)
