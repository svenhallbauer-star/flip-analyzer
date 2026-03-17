# FLIP ANALYZER — Tampa Bay
## Fix & Flip Bewertungstool für Pinellas, Hillsborough & Pasco County

---

## SCHNELLSTART (3 Schritte)

### 1. Python-Pakete installieren
Öffnen Sie ein Terminal im Ordner `flip_analyzer` und führen Sie aus:
```
pip install -r requirements.txt
```

### 2. API-Keys eintragen (optional aber empfohlen)
Öffnen Sie `server.py` und tragen Sie Ihre Keys direkt ein:
```python
RAPIDAPI_KEY = "IHR_RAPIDAPI_KEY_HIER"
ANTHROPIC_KEY = "sk-ant-IHR_KEY_HIER"
```

**Oder** starten Sie den Server ohne Keys — dann läuft die App im **Demo-Modus** mit realistischen Beispieldaten.

### 3. Server starten
```
python server.py
```

Dann im Browser öffnen: **http://localhost:5000**

---

## API-Keys beschaffen

### RapidAPI (Zillow-Daten)
1. Kostenlos registrieren: https://rapidapi.com
2. API abonnieren: https://rapidapi.com/s.mahmoud97/api/zillow56
3. Kostenlosen Plan wählen (50 Calls/Monat gratis)
4. API-Key kopieren aus dem Dashboard

### Anthropic (KI-Analyse)
1. Account erstellen: https://console.anthropic.com
2. API-Key erstellen unter "API Keys"
3. Guthaben aufladen (ca. $5 reichen für ~500 Analysen)

---

## FUNKTIONEN

### Zillow-Suche
- Automatische Suche in Pinellas, Hillsborough oder Pasco County
- Filterbar nach Preis, Zimmeranzahl, Days on Market
- Submarket-Filter (z.B. nur Wesley Chapel oder South Tampa)
- Schnell-Score und ARV-Vorschau pro Listing

### KI-Vollanalyse
- After Repair Value (ARV) nach county-spezifischen Comps
- Max. Kaufpreis nach 70%-Regel
- Renovierungsplan mit MUSS/SOLL/KANN-Priorisierung
- ROI-Kalkulation inkl. Halte- und Closingkosten
- 3 Vergleichsobjekte aus der Region
- Go/No-Go Empfehlung mit Deal-Score 0–100

---

## COUNTY-MARKTDATEN (Q1 2026)

| County       | Median Preis | Median $/sqft | ARV-Spanne    | Ø DOM  |
|--------------|-------------|--------------|---------------|--------|
| Pinellas     | $381,000    | $220         | $200–265/sqft | 16 Tage|
| Hillsborough | $408,000    | $232         | $215–280/sqft | 52 Tage|
| Pasco        | $350,000    | $194         | $175–225/sqft | 69 Tage|

---

## NÄCHSTE AUSBAUSTUFEN

- [ ] Email-Monitoring: Maklerangebote automatisch aus Posteingang verarbeiten
- [ ] PDF-Upload: Direkte Analyse von Makler-PDFs mit Bildanalyse
- [ ] County Property Appraiser API: Echte historische Verkaufsdaten (kostenlos, öffentlich)
- [ ] Täglicher Deal-Report per Email
- [ ] Historische Deal-Datenbank zum KI-Training

---

Quellen: Redfin, Zillow ZHVI, Barrett Henry Market Report Feb 2026
