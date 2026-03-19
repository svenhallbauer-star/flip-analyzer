"""
FLIP ANALYZER - Backend Server
Tampa Bay Fix & Flip Tool
Datenquelle: Redfin (kein API-Key nötig)
Läuft lokal auf http://localhost:5000
"""

from flask import Flask, jsonify, request, send_from_directory, session, redirect, url_for, render_template_string
from training_data import get_training_context, get_full_training_context, RENOVATION_BENCHMARKS, ARV_BENCHMARKS
from flask_cors import CORS
from functools import wraps
import requests
import os
import json
import time
import hashlib
import secrets

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)
app.secret_key = os.environ.get("SECRET_KEY", "flip-analyzer-default-key-change-me")

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY", "")
RAPIDAPI_KEY  = os.environ.get("RAPIDAPI_KEY", "")

# ── Benutzer (aus Env-Variablen oder Defaults) ─────────────────────────────────
def load_users():
    """Lädt Benutzer aus USERS Env-Variable (JSON) oder nutzt Defaults."""
    users_json = os.environ.get("USERS", "")
    if users_json:
        try:
            return json.loads(users_json)
        except:
            pass
    # Default: admin / flip2024
    return {
        "admin": {
            "password_hash": hashlib.sha256("flip2024".encode()).hexdigest(),
            "name": "Admin",
            "role": "admin"
        }
    }

def check_password(username, password):
    users = load_users()
    user = users.get(username)
    if not user:
        return False
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    return pw_hash == user.get("password_hash", "")

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            if request.is_json:
                return jsonify({"error": "Nicht eingeloggt"}), 401
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated

LOGIN_HTML = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Flip Analyzer — Login</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@400;500&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0f1117;color:#e8e4dc;font-family:'DM Mono',monospace;min-height:100vh;display:flex;align-items:center;justify-content:center}
.login-box{background:#181c25;border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:40px;width:100%;max-width:400px}
h1{font-family:'Syne',sans-serif;font-size:22px;font-weight:800;color:#f0c040;margin-bottom:6px}
.sub{font-size:11px;color:#7a7f8e;margin-bottom:28px}
.field{display:flex;flex-direction:column;gap:5px;margin-bottom:14px}
label{font-size:10px;color:#7a7f8e;text-transform:uppercase;letter-spacing:.5px}
input{background:#1e2330;border:1px solid rgba(255,255,255,0.08);border-radius:6px;color:#e8e4dc;font-family:'DM Mono',monospace;font-size:13px;padding:10px 12px}
input:focus{outline:none;border-color:rgba(240,192,64,.4)}
.btn{width:100%;padding:13px;background:#f0c040;color:#0f1117;font-family:'Syne',sans-serif;font-size:14px;font-weight:800;border:none;border-radius:6px;cursor:pointer;margin-top:8px}
.btn:hover{background:#f5d060}
.err{background:rgba(240,80,80,.1);border:1px solid rgba(240,80,80,.2);color:#f05050;border-radius:6px;padding:10px;font-size:12px;margin-bottom:14px;display:{% if error %}block{% else %}none{% endif %}}
</style>
</head>
<body>
<div class="login-box">
  <h1>FLIP ANALYZER</h1>
  <div class="sub">Tampa Bay Pro — Bitte einloggen</div>
  <div class="err">{{ error }}</div>
  <form method="POST" action="/login">
    <div class="field">
      <label>Benutzername</label>
      <input type="text" name="username" placeholder="username" autocomplete="username" required>
    </div>
    <div class="field">
      <label>Passwort</label>
      <input type="password" name="password" placeholder="••••••••" autocomplete="current-password" required>
    </div>
    <button type="submit" class="btn">EINLOGGEN →</button>
  </form>
</div>
</body>
</html>"""

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


# ── Auth Routen ────────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if check_password(username, password):
            session["logged_in"] = True
            session["username"]  = username
            users = load_users()
            session["role"] = users.get(username, {}).get("role", "user")
            session["name"] = users.get(username, {}).get("name", username)
            return redirect("/")
        return render_template_string(LOGIN_HTML, error="Benutzername oder Passwort falsch.")
    if session.get("logged_in"):
        return redirect("/")
    return render_template_string(LOGIN_HTML, error="")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/api/me")
@login_required
def me():
    return jsonify({
        "username": session.get("username"),
        "name":     session.get("name"),
        "role":     session.get("role")
    })

@app.route("/api/users", methods=["GET"])
@login_required
def list_users():
    if session.get("role") != "admin":
        return jsonify({"error": "Kein Zugriff"}), 403
    users = load_users()
    return jsonify([{"username": k, "name": v.get("name",""), "role": v.get("role","user")} for k,v in users.items()])

@app.route("/api/users", methods=["POST"])
@login_required
def add_user():
    if session.get("role") != "admin":
        return jsonify({"error": "Kein Zugriff"}), 403
    data     = request.json or {}
    username = data.get("username","").strip()
    password = data.get("password","").strip()
    name     = data.get("name", username)
    role     = data.get("role", "user")
    if not username or not password:
        return jsonify({"error": "Benutzername und Passwort erforderlich"}), 400
    users_json = os.environ.get("USERS", "")
    users = json.loads(users_json) if users_json else load_users()
    users[username] = {
        "password_hash": hashlib.sha256(password.encode()).hexdigest(),
        "name": name,
        "role": role
    }
    os.environ["USERS"] = json.dumps(users)
    return jsonify({"ok": True})

@app.route("/api/users/<username>", methods=["DELETE"])
@login_required
def delete_user(username):
    if session.get("role") != "admin":
        return jsonify({"error": "Kein Zugriff"}), 403
    if username == session.get("username"):
        return jsonify({"error": "Eigenen Account nicht löschbar"}), 400
    users_json = os.environ.get("USERS", "")
    users = json.loads(users_json) if users_json else load_users()
    users.pop(username, None)
    os.environ["USERS"] = json.dumps(users)
    return jsonify({"ok": True})

# ── Routen ─────────────────────────────────────────────────────────────────────

@app.route("/")
@login_required
def index():
    return send_from_directory("templates", "index.html")

@app.route("/api/config", methods=["GET"])
@login_required
def get_config():
    return jsonify({
        "anthropic_configured": bool(get_anthropic_key()),
        "data_source": "redfin",
        "counties": list(COUNTY_CONFIG.keys())
    })

@app.route("/api/config", methods=["POST"])
@login_required
def set_config():
    global ANTHROPIC_KEY
    data = request.json or {}
    if data.get("anthropic_key"):
        ANTHROPIC_KEY = data["anthropic_key"]
        os.environ["ANTHROPIC_KEY"] = ANTHROPIC_KEY
    return jsonify({"ok": True, "anthropic": bool(get_anthropic_key())})


@app.route("/api/search", methods=["POST"])
@login_required
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
        "home_type":    "HOUSES"
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

            # Extract photo URLs from RapidAPI response
            photos = []
            raw_photos = h.get("imgSrc", h.get("carouselPhotos", h.get("photos", [])))
            if isinstance(raw_photos, str):
                photos = [raw_photos]
            elif isinstance(raw_photos, list):
                for p in raw_photos[:8]:
                    if isinstance(p, str):
                        photos.append(p)
                    elif isinstance(p, dict):
                        url = p.get("url", p.get("src", p.get("mixedSources", {}).get("jpeg", [{}])[0].get("url", "")))
                        if url:
                            photos.append(url)

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
                "photos":     photos[:25],
                "zpid":       str(h.get("zpid", h.get("listingId", ""))),
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
@login_required
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
@login_required
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
@login_required
def scan_imap():
    data       = request.json or {}
    host       = data.get("host", "imap.gmail.com")
    port       = int(data.get("port", 993))
    user       = data.get("user", "")
    password   = data.get("password", "")
    query      = data.get("query", "redfin.com OR zillow.com")
    county_key = data.get("county_key", "pinellas")

    # Falls leer, aus DB laden
    if not user or not password:
        _ensure_settings_table()
        saved = _load_user_settings(session.get("username", "default")).get("imap", {})
        if not user:
            user = saved.get("user", "")
        if not password:
            password = saved.get("password", "")
        if not host or host == "imap.gmail.com":
            host = saved.get("host", "imap.gmail.com")
        if not query:
            query = saved.get("query", "")

    if not user or not password:
        return jsonify({"error": "Email und Passwort erforderlich."}), 400

    # Zugangsdaten persistent speichern
    _ensure_settings_table()
    username = session.get("username", "default")
    settings = _load_user_settings(username)
    settings["imap"] = {"host": host, "port": port, "user": user, "password": password, "query": query}
    _save_user_settings(username, settings)

    try:
        mail = imaplib.IMAP4_SSL(host, port)
        mail.login(user, password)
        mail.select("INBOX")

        # Search all emails since Jan 2026 - no keyword filter at IMAP level
        _, msg_ids = mail.search(None, 'SINCE "01-Jan-2026"')
        all_ids = msg_ids[0].split()
        # Take last 50 emails
        ids = all_ids[-50:]

        email_texts = []
        keywords = [q.strip().lower() for q in query.replace(" OR ", "|").split("|")]

        for mid in ids:
            try:
                _, msg_data = mail.fetch(mid, "(RFC822)")
                msg = email_lib.message_from_bytes(msg_data[0][1])

                # Decode subject safely
                raw_subject = msg.get("Subject", "") or ""
                try:
                    subject_parts = decode_header(raw_subject)
                    subject = ""
                    for part, enc in subject_parts:
                        if isinstance(part, bytes):
                            subject += part.decode(enc or "utf-8", errors="ignore")
                        else:
                            subject += str(part)
                except:
                    subject = raw_subject

                sender = msg.get("From", "") or ""

                # Filter by keywords in subject OR sender OR body snippet
                combined = (subject + sender).lower()

                # Also check body for keywords
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        ct = part.get_content_type()
                        if ct == "text/plain":
                            try:
                                body = part.get_payload(decode=True).decode(errors="ignore")[:500]
                            except:
                                pass
                            break
                        elif ct == "text/html" and not body:
                            try:
                                body = part.get_payload(decode=True).decode(errors="ignore")[:200]
                            except:
                                pass
                else:
                    try:
                        body = msg.get_payload(decode=True).decode(errors="ignore")[:500]
                    except:
                        pass

                combined_full = (combined + body.lower())

                # Match if ANY keyword found, or if query is empty/wildcard
                if query.strip() == "*" or not keywords or any(kw in combined_full for kw in keywords):
                    # Get full body
                    full_body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                try:
                                    full_body = part.get_payload(decode=True).decode(errors="ignore")[:3000]
                                except:
                                    pass
                                break
                    else:
                        try:
                            full_body = msg.get_payload(decode=True).decode(errors="ignore")[:3000]
                        except:
                            pass

                    # PDF-Anhaenge extrahieren
                    pdf_texts = []
                    for part in msg.walk():
                        if part.get_content_type() == "application/pdf" or                            (part.get_filename() and part.get_filename().lower().endswith(".pdf")):
                            try:
                                pdf_data = part.get_payload(decode=True)
                                if pdf_data:
                                    pdf_b64 = base64.b64encode(pdf_data).decode("utf-8")
                                    # PDF via Claude analysieren
                                    pdf_resp = _anthropic_post({
                                        "model": "claude-sonnet-4-5",
                                        "max_tokens": 800,
                                        "messages": [{"role": "user", "content": [
                                            {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_b64}},
                                            {"type": "text", "text": "Extrahiere alle Immobiliendaten aus diesem Dokument: Adresse, Preis, Groesse, Zimmer, Baujahr, Zustand, Besonderheiten. Antworte auf Deutsch."}
                                        ]}]
                                    })
                                    pdf_text = pdf_resp.json()["content"][0]["text"]
                                    pdf_texts.append(f"[PDF-Anhang: {part.get_filename()}]\n{pdf_text}")
                                    print(f"  PDF-Anhang analysiert: {part.get_filename()}")
                            except Exception as pe:
                                print(f"  PDF-Fehler: {pe}")

                    combined_content = f"Von: {sender}\nBetreff: {subject}\n\n{full_body}"
                    if pdf_texts:
                        combined_content += "\n\n" + "\n\n".join(pdf_texts)

                    email_texts.append(combined_content)
                    print(f"  Email gefunden: {subject[:60]}")
            except Exception as e:
                print(f"  Email-Fehler: {e}")
                continue

        mail.logout()

        if not email_texts:
            return jsonify({"listings": [], "message": "Keine passenden Emails gefunden."})

        # Analyze combined email content directly (no localhost call)
        combined_text = "\n\n---\n\n".join(email_texts[:5])
        county = COUNTY_CONFIG.get(county_key, COUNTY_CONFIG["pinellas"])

        prompt = f"""Analysiere diesen Email-Text von einem Makler oder einer Immobilien-Plattform.
Extrahiere alle Immobilien-Listings die du findest.

Markt: {county['name']} (ARV ${county['arv_low']}-${county['arv_high']}/sqft)

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
      "price_sqft": 0,
      "county": "{county_key}",
      "listing_url": "<URL falls vorhanden>",
      "source": "email",
      "notes": "<Zusatzinfos>",
      "zestimate": 0
    }}
  ]
}}

Email-Text:
{combined_text[:4000]}"""

        resp = _anthropic_post({
            "model": "claude-sonnet-4-5",
            "max_tokens": 1500,
            "system": "Du bist Immobilien-Daten-Extraktor. Antworte NUR mit validem JSON.",
            "messages": [{"role": "user", "content": prompt}]
        })
        raw = resp.json()["content"][0]["text"].replace("```json","").replace("```","").strip()
        return jsonify(json.loads(raw))

    except imaplib.IMAP4.error as e:
        return jsonify({"error": f"IMAP-Fehler: {e}. Bitte App-Passwort prüfen."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/api/analyze", methods=["POST"])
@login_required
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


# ── IMAP Credentials (persistent in Postgres) ─────────────────────────────────

def _get_db_conn():
    """Datenbankverbindung holen."""
    import psycopg2
    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url:
        return None
    return psycopg2.connect(db_url)

def _ensure_settings_table():
    """Erstellt Settings-Tabelle falls nicht vorhanden."""
    try:
        conn = _get_db_conn()
        if not conn:
            return
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    username    TEXT PRIMARY KEY,
                    settings    JSONB NOT NULL DEFAULT '{}',
                    updated_at  TIMESTAMP DEFAULT NOW()
                )
            """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Settings table error: {e}")

def _load_user_settings(username):
    """Laedt User-Settings aus DB."""
    try:
        conn = _get_db_conn()
        if not conn:
            return {}
        with conn.cursor() as cur:
            cur.execute("SELECT settings FROM user_settings WHERE username = %s", (username,))
            row = cur.fetchone()
        conn.close()
        return row[0] if row else {}
    except Exception as e:
        print(f"Load settings error: {e}")
        return {}

def _save_user_settings(username, settings):
    """Speichert User-Settings in DB."""
    try:
        conn = _get_db_conn()
        if not conn:
            return False
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO user_settings (username, settings, updated_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT (username) DO UPDATE
                SET settings = %s, updated_at = NOW()
            """, (username, json.dumps(settings), json.dumps(settings)))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Save settings error: {e}")
        return False


@app.route("/api/imap-credentials", methods=["GET"])
@login_required
def get_imap_credentials():
    """Gibt gespeicherte IMAP-Zugangsdaten zurueck."""
    _ensure_settings_table()
    username = session.get("username", "default")
    settings = _load_user_settings(username)
    creds = settings.get("imap", {})
    if creds:
        return jsonify({
            "host":     creds.get("host", "imap.gmail.com"),
            "port":     creds.get("port", 993),
            "user":     creds.get("user", ""),
            "password": creds.get("password", ""),
            "query":    creds.get("query", "zillow.com OR redfin.com OR new listing"),
            "saved":    True
        })
    return jsonify({"saved": False})

@app.route("/api/imap-credentials", methods=["POST"])
@login_required
def save_imap_credentials():
    """Speichert IMAP-Zugangsdaten persistent in Postgres."""
    _ensure_settings_table()
    data = request.json or {}
    username = session.get("username", "default")
    settings = _load_user_settings(username)
    settings["imap"] = {
        "host":     data.get("host", "imap.gmail.com"),
        "port":     int(data.get("port", 993)),
        "user":     data.get("user", ""),
        "password": data.get("password", ""),
        "query":    data.get("query", "")
    }
    _save_user_settings(username, settings)
    return jsonify({"ok": True})

@app.route("/api/imap-credentials", methods=["DELETE"])
@login_required
def delete_imap_credentials():
    """Loescht gespeicherte IMAP-Zugangsdaten."""
    _ensure_settings_table()
    username = session.get("username", "default")
    settings = _load_user_settings(username)
    settings.pop("imap", None)
    _save_user_settings(username, settings)
    return jsonify({"ok": True})


# ── Zillow Foto-Analyse ────────────────────────────────────────────────────────

@app.route("/api/analyze-listing-photos", methods=["POST"])
@login_required
def analyze_listing_photos():
    """Laedt Zillow-Fotos und analysiert sie mit RAG."""
    import psycopg2

    data       = request.json or {}
    listing    = data.get("listing", {})
    county_key = data.get("county_key", "pinellas")
    photos     = listing.get("photos", [])

    if not get_anthropic_key():
        return jsonify({"error": "Anthropic API-Key nicht konfiguriert."}), 400

    # Lade ALLE Fotos via Property Details API
    rapidapi_key = os.environ.get("RAPIDAPI_KEY", "")
    zpid = listing.get("zpid", "")
    address = listing.get("address", "")

    if rapidapi_key:
        # Versuch 1: Property Details via zpid
        if zpid:
            try:
                r = requests.get(
                    "https://real-time-real-estate-data.p.rapidapi.com/property-details",
                    headers={"x-rapidapi-host": "real-time-real-estate-data.p.rapidapi.com",
                             "x-rapidapi-key": rapidapi_key},
                    params={"zpid": zpid},
                    timeout=20
                )
                print(f"Property details (zpid): {r.status_code}")
                if r.ok:
                    prop = r.json().get("data", r.json())
                    for field in ["carouselPhotos", "responsivePhotos", "photos", "images"]:
                        raw = prop.get(field, [])
                        if raw:
                            for p in raw:
                                url = p.get("url", p.get("src", "")) if isinstance(p, dict) else str(p)
                                if url and url.startswith("http"):
                                    photos.append(url)
                            print(f"  Got {len(photos)} photos from {field}")
                            if photos:
                                break
            except Exception as e:
                print(f"zpid lookup error: {e}")

        # Versuch 2: Property by Address
        if not photos and address:
            try:
                r = requests.get(
                    "https://real-time-real-estate-data.p.rapidapi.com/property-by-address",
                    headers={"x-rapidapi-host": "real-time-real-estate-data.p.rapidapi.com",
                             "x-rapidapi-key": rapidapi_key},
                    params={"address": address},
                    timeout=20
                )
                print(f"Property by address: {r.status_code}")
                if r.ok:
                    prop = r.json().get("data", r.json())
                    for field in ["carouselPhotos", "responsivePhotos", "photos"]:
                        raw = prop.get(field, [])
                        if raw:
                            for p in raw:
                                url = p.get("url", p.get("src", "")) if isinstance(p, dict) else str(p)
                                if url and url.startswith("http"):
                                    photos.append(url)
                            if photos:
                                break
            except Exception as e:
                print(f"Address lookup error: {e}")

    print(f"Total photos to analyze: {len(photos)}")

    if not photos:
        return jsonify({"error": "Keine Fotos fuer dieses Listing verfuegbar. Bitte Bilder manuell im Import-Tab hochladen.", "no_photos": True}), 404

    # Fotos herunterladen und als base64 kodieren
    photo_results = []
    for photo_url in photos:
        try:
            r = requests.get(photo_url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            })
            if r.ok and r.headers.get("content-type","").startswith("image"):
                img_b64 = base64.b64encode(r.content).decode("utf-8")
                photo_results.append((img_b64, photo_url))
        except Exception as e:
            print(f"Photo download error: {e}")
            continue

    if not photo_results:
        return jsonify({"error": "Fotos konnten nicht geladen werden. Bitte Bilder manuell hochladen.", "no_photos": True}), 404

    # Jedes Foto durch RAG-Analyse schicken
    db_url = os.environ.get("DATABASE_URL", "")
    analyses = []

    for img_b64, photo_url in photo_results:
        # Schnelle Beschreibung
        try:
            desc_resp = _anthropic_post({
                "model": "claude-sonnet-4-5",
                "max_tokens": 200,
                "messages": [{"role": "user", "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img_b64}},
                    {"type": "text", "text": 'Describe this real estate photo in JSON: {"room_type":"<room>","damage_types":["<damage>"],"severity":<1-5>,"description":"<text>"}'}
                ]}]
            })
            raw = desc_resp.json()["content"][0]["text"].replace("```json","").replace("```","").strip()
            desc = json.loads(raw)
        except:
            continue

        # RAG Suche
        similar = []
        if db_url:
            try:
                embed_text = f"Room: {desc.get('room_type','')} Damage: {', '.join(desc.get('damage_types',[]))} Severity: {desc.get('severity',3)}"
                words = embed_text.lower().split()[:100]
                embedding = []
                for i in range(1536):
                    val = 0.0
                    for j, word in enumerate(words):
                        h = int(__import__('hashlib').md5(f"{word}{i}{j}".encode()).hexdigest(), 16)
                        val += (h % 1000 - 500) / 500.0
                    embedding.append(val / max(len(words), 1))
                magnitude = sum(x**2 for x in embedding) ** 0.5
                if magnitude > 0:
                    embedding = [x / magnitude for x in embedding]
                conn = psycopg2.connect(db_url)
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT deal_name, room_type, severity, reno_cost,
                               1-(embedding <=> %s::vector) as sim
                        FROM deal_images ORDER BY embedding <=> %s::vector LIMIT 3
                    """, (embedding, embedding))
                    for row in cur.fetchall():
                        similar.append({"deal": row[0], "room": row[1], "severity": row[2],
                                        "cost": float(row[3]) if row[3] else 0, "sim": round(float(row[4])*100,1)})
                conn.close()
            except Exception as e:
                print(f"RAG error: {e}")

        analyses.append({
            "room_type":   desc.get("room_type",""),
            "damage_types": desc.get("damage_types",[]),
            "severity":    desc.get("severity", 3),
            "description": desc.get("description",""),
            "similar":     similar,
            "est_cost":    similar[0]["cost"] if similar else 0,
            "photo_url":   photo_url
        })

    # Zusammenfassung
    total_cost = sum(a["est_cost"] for a in analyses)
    worst = sorted(analyses, key=lambda x: x["severity"], reverse=True)

    return jsonify({
        "photos_analyzed": len(analyses),
        "analyses":        analyses,
        "total_est_cost":  total_cost,
        "worst_room":      worst[0] if worst else None,
        "rag_enabled":     bool(db_url),
        "address":         listing.get("address","")
    })


# ── RAG Bildanalyse ────────────────────────────────────────────────────────────

@app.route("/api/analyze-image-rag", methods=["POST"])
@login_required
def analyze_image_rag():
    """Analysiert ein Bild mit RAG -- sucht aehnliche Bilder aus echten Deals."""
    import psycopg2

    data       = request.json or {}
    img_b64    = data.get("image", "")
    county_key = data.get("county_key", "pinellas")
    room_hint  = data.get("room_hint", "")

    if not get_anthropic_key():
        return jsonify({"error": "Anthropic API-Key nicht konfiguriert."}), 400
    if not img_b64:
        return jsonify({"error": "Kein Bild erhalten."}), 400

    db_url = os.environ.get("DATABASE_URL", "")

    # Schritt 1: Bild beschriften
    describe_prompt = """Describe this real estate image briefly for renovation analysis.
Respond ONLY with valid JSON:
{
  "room_type": "<Kitchen|Bathroom|Living Room|Bedroom|Basement|Exterior|Roof|Garage|Hallway>",
  "damage_types": ["<Mold|Water Damage|Structural|Outdated|OK>"],
  "severity": <1-5>,
  "description": "<brief description>"
}"""

    try:
        desc_resp = _anthropic_post({
            "model": "claude-sonnet-4-5",
            "max_tokens": 300,
            "messages": [{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img_b64}},
                {"type": "text", "text": describe_prompt}
            ]}]
        })
        raw = desc_resp.json()["content"][0]["text"].replace("```json","").replace("```","").strip()
        img_desc = json.loads(raw)
    except Exception as e:
        img_desc = {"room_type": room_hint or "Unknown", "damage_types": [], "severity": 3, "description": ""}

    # Schritt 2: Aehnliche Faelle suchen
    similar_cases = []
    if db_url:
        try:
            embed_text = f"Room: {img_desc.get('room_type','')} Damage: {', '.join(img_desc.get('damage_types',[]))} Severity: {img_desc.get('severity',3)}"
            words = embed_text.lower().split()[:100]
            embedding = []
            for i in range(1536):
                val = 0.0
                for j, word in enumerate(words):
                    h = int(__import__('hashlib').md5(f"{word}{i}{j}".encode()).hexdigest(), 16)
                    val += (h % 1000 - 500) / 500.0
                embedding.append(val / max(len(words), 1))
            magnitude = sum(x**2 for x in embedding) ** 0.5
            if magnitude > 0:
                embedding = [x / magnitude for x in embedding]

            conn = psycopg2.connect(db_url)
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT deal_name, phase, filename, room_type, damage_type,
                           severity, description, reno_cost, deal_data,
                           1 - (embedding <=> %s::vector) as similarity
                    FROM deal_images
                    ORDER BY embedding <=> %s::vector
                    LIMIT 5
                """, (embedding, embedding))
                for row in cur.fetchall():
                    similar_cases.append({
                        "deal": row[0], "phase": row[1], "filename": row[2],
                        "room_type": row[3], "damage_type": row[4], "severity": row[5],
                        "description": row[6], "reno_cost": float(row[7]) if row[7] else 0,
                        "deal_data": row[8], "similarity": round(float(row[9]) * 100, 1)
                    })
            conn.close()
        except Exception as e:
            print(f"DB-Fehler RAG: {e}")

    # Schritt 3: Vollanalyse mit RAG-Kontext
    county = COUNTY_CONFIG.get(county_key, COUNTY_CONFIG["pinellas"])
    rag_context = ""
    if similar_cases:
        rag_context = "\n\nSIMILAR CASES FROM REAL DEALS (use for cost estimation):\n"
        for i, case in enumerate(similar_cases[:3], 1):
            deal_data = case.get("deal_data", {})
            reno = deal_data.get("renovation_costs", {}) if isinstance(deal_data, dict) else {}
            rag_context += f"""
Case {i} (Similarity: {case['similarity']}%):
- Deal: {case['deal']} | Phase: {case['phase']}
- Room: {case['room_type']} | Damage: {case['damage_type']} | Severity: {case['severity']}
- Description: {case['description']}
- Estimated cost for this room: ${case['reno_cost']:,.0f}
- Total renovation cost of deal: ${reno.get('total', 0):,.0f}
"""

    analysis_prompt = f"""Analyze this real estate image for Fix-and-Flip in {county['name']}.
{rag_context}

MARKET {county['name']}:
- ARV: ${county['arv_low']}-${county['arv_high']}/sqft
- Median: ${county['median_price']:,}

Based on the image AND similar reference cases -- respond ONLY with valid JSON:
{{
  "room_type": "{img_desc.get('room_type', '')}",
  "damage_types": {json.dumps(img_desc.get('damage_types', []))},
  "severity": {img_desc.get('severity', 3)},
  "description": "<detailed description of what you see>",
  "priority": "<MUST|SHOULD|OPTIONAL>",
  "estimated_reno_cost": <cost estimate in USD based on reference cases>,
  "cost_reasoning": "<explanation referencing similar cases>",
  "similar_cases_used": {json.dumps([c['deal'] + ' (' + str(c['similarity']) + '%)' for c in similar_cases[:3]])},
  "action_items": ["<action 1>", "<action 2>", "<action 3>"]
}}"""

    try:
        resp = _anthropic_post({
            "model": "claude-sonnet-4-5",
            "max_tokens": 800,
            "messages": [{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img_b64}},
                {"type": "text", "text": analysis_prompt}
            ]}]
        })
        raw = resp.json()["content"][0]["text"].replace("```json","").replace("```","").strip()
        result = json.loads(raw)
        result["similar_cases"] = similar_cases[:3]
        result["rag_enabled"] = len(similar_cases) > 0
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
