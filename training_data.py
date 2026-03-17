"""
Historische Deal-Daten von Eydura Home Solutions
Zwei abgeschlossene Fix & Flip Deals — Tampa Bay 2025
"""

HISTORICAL_DEALS = [
    {
        "id": "deal_001",
        "address": "4546 Ontario Dr, New Port Richey, FL 34652",
        "county": "pasco",
        "submarket": "New Port Richey",
        "purchase_price": 70000,
        "purchase_date": "2025-02-12",
        "sale_price": 220000,
        "sale_date": "2025-08-07",
        "hold_months": 6,
        "sqft": 1492,
        "beds": 3,
        "baths": 2,
        "year_built": 1977,
        "lot_sqft": 6000,
        "property_type": "SFR",
        "flood_zone": "AE",
        "waterfront": True,
        "subdivision": "Beacon Woods Golf Country",
        "original_list_price": 89900,
        "dom_before_purchase": 24,
        "sale_price_per_sqft": 147,
        "arv": 220000,
        "arv_per_sqft": 147,
        "gross_profit": 150000,
        "renovation_total": None,  # nicht bekannt
        "renovation_items": [],
        "notes": "Waterfront-Lage. Ankauf weit unter Marktwert ($70k bei Taxable Value $112k). Schneller Flip in 6 Monaten. Verkauf an Endkäufer für $220k. Listing ursprünglich $89,900 → Verkauf $70k.",
        "lessons": [
            "Waterfront-Lage in New Port Richey erzielt Premium gegenüber Taxable Value",
            "Ankauf bei $70k möglich wenn Voreigentümer distressed verkauft",
            "6 Monate Hold-Zeit in Pasco County typisch",
            "Flood Zone AE beachten — erhöht Versicherungskosten",
            "ARV $147/sqft für New Port Richey (Pasco) realistisch"
        ]
    },
    {
        "id": "deal_002",
        "address": "6813 Circle Creek Dr, Pinellas Park, FL 33781",
        "county": "pinellas",
        "submarket": "Pinellas Park",
        "purchase_price": 250000,
        "purchase_date": "2025-09-11",
        "sale_price": 445000,
        "sale_date": "2026-01-23",
        "hold_months": 4,
        "sqft": 1506,
        "beds": 4,
        "baths": 2,
        "year_built": 1979,
        "lot_sqft": 9779,
        "property_type": "SFR",
        "flood_zone": "AE",
        "waterfront": False,
        "subdivision": "Bonnie Glynn Ph One-A",
        "original_list_price": 439900,
        "dom_before_purchase": 7,
        "sale_price_per_sqft": 295,
        "arv": 445000,
        "arv_per_sqft": 295,
        "gross_profit": 195000,
        "renovation_total": 68000,
        "net_profit_estimate": 127000,  # 195k - 68k Reno
        "renovation_items": [
            {"name": "Interior Paint", "cost": 2259, "unit": "sqft", "unit_price": 1.50},
            {"name": "Exterior Paint", "cost": 2408, "unit": "sqft", "unit_price": 1.00},
            {"name": "Exterior Paint Trim", "cost": 1204, "unit": "sqft", "unit_price": 0.50},
            {"name": "Drywall Install New", "cost": 2000, "unit": "sheet", "unit_price": 40.00},
            {"name": "LVP/Laminate Flooring", "cost": 7530, "unit": "sqft", "unit_price": 5.00},
            {"name": "Kitchen Cabinets Standard", "cost": 4000, "unit": "linear_ft", "unit_price": 60.00},
            {"name": "Countertops", "cost": 3500, "unit": "linear_ft", "unit_price": 30.00},
            {"name": "Kitchen Sink and Faucets", "cost": 450, "unit": "each", "unit_price": 450.00},
            {"name": "Kitchen Appliance Package", "cost": 4000, "unit": "job", "unit_price": 4000.00},
            {"name": "Bathrooms Custom High End", "cost": 10000, "unit": "job", "unit_price": 5000.00},
            {"name": "Light Fixtures", "cost": 600, "unit": "each", "unit_price": 50.00},
            {"name": "Ceiling Fans", "cost": 600, "unit": "each", "unit_price": 150.00},
            {"name": "Windows Install New", "cost": 4000, "unit": "window", "unit_price": 500.00},
            {"name": "Interior Doors", "cost": 2520, "unit": "each", "unit_price": 210.00},
            {"name": "Misc Electric", "cost": 1000, "unit": "job", "unit_price": 1000.00},
            {"name": "Misc Plumbing", "cost": 1000, "unit": "job", "unit_price": 1000.00},
            {"name": "Front Door", "cost": 300, "unit": "each", "unit_price": 300.00},
            {"name": "Water Heater", "cost": 800, "unit": "each", "unit_price": 550.00},
            {"name": "HVAC Install New 3 Ton", "cost": 500, "unit": "job", "unit_price": 4000.00},
            {"name": "Roof Replace", "cost": 13000, "unit": "bid", "unit_price": 1.00},
            {"name": "Landscaping", "cost": 1000, "unit": "bid", "unit_price": 1.00},
            {"name": "Trashout", "cost": 1000, "unit": "job", "unit_price": 1000.00},
            {"name": "Misc", "cost": 4329, "unit": "each", "unit_price": 1.00},
        ],
        "comps_at_purchase": [
            {"address": "5834 71st St N, St Petersburg", "sale_price": 475000, "sqft": 1495, "sold_date": "2025-04-09", "price_sqft": 318},
            {"address": "7097 Aberfeldy Ave N, St Petersburg", "sale_price": 472500, "sqft": 1420, "sold_date": "2025-03-04", "price_sqft": 333},
            {"address": "6461 67th Ave N, Pinellas Park", "sale_price": 437500, "sqft": 1326, "sold_date": "2025-06-02", "price_sqft": 330},
            {"address": "7853 Sundown Dr, St Petersburg", "sale_price": 428000, "sqft": 1527, "sold_date": "2025-06-18", "price_sqft": 280},
            {"address": "6865 Circle Creek Dr, Pinellas Park", "sale_price": 425000, "sqft": 1416, "sold_date": "2025-08-15", "price_sqft": 300},
        ],
        "comp_avg_price_sqft": 312,
        "notes": "Schneller Flip in nur 4 Monaten. Ankauf $250k, Reno $68k, Verkauf $445k. Bonnie Glynn Subdivision Pinellas Park. Flood Zone AE aber kein direktes Waterfront. DOM nur 7 Tage nach Listing.",
        "lessons": [
            "Pinellas Park ARV $295-333/sqft für renovierte Objekte erzielbar",
            "Vollrenovierung ($68k für 1506 sqft = $45/sqft) erzeugt maximalen Value-Add",
            "Dach ($13k) ist größter Einzelposten — immer einplanen bei Baujahr <1985",
            "Bathrooms ($10k für 2 Bäder = $5k/Bad) bei High-End Ausstattung",
            "4 Monate Hold-Zeit bei Pinellas schnell möglich",
            "NetWorth Realty als Quelle für distressed Ankäufe in Pinellas",
            "Kaufpreis $250k = $166/sqft weit unter Comp-Niveau $295-333/sqft",
            "Interior Paint $1.50/sqft, LVP $5/sqft, Windows $500/Fenster als Benchmarks",
            "Küche komplett: Cabinets + Countertops + Appliances = ~$12k Standard",
        ]
    }
]

# Aggregierte Benchmarks aus den Deals
RENOVATION_BENCHMARKS = {
    "pinellas": {
        "interior_paint_per_sqft": 1.50,
        "exterior_paint_per_sqft": 1.00,
        "lvp_flooring_per_sqft": 5.00,
        "kitchen_cabinets_per_linear_ft": 60.00,
        "countertops_per_linear_ft": 30.00,
        "appliance_package": 4000,
        "bathroom_standard": 3500,
        "bathroom_high_end": 5000,
        "window_per_unit": 500,
        "interior_door_per_unit": 210,
        "roof_replace_estimate": 13000,
        "hvac_3ton": 4000,
        "water_heater": 800,
        "trashout": 1000,
        "misc_per_deal": 4000,
        "total_per_sqft_typical": 45,
    },
    "pasco": {
        "total_per_sqft_typical": 35,  # Pasco günstiger als Pinellas
    }
}

# ARV-Benchmarks aus abgeschlossenen Deals
ARV_BENCHMARKS = {
    "pinellas_park_renovated": {"min": 280, "max": 333, "avg": 312},
    "new_port_richey_pasco": {"min": 140, "max": 160, "avg": 147},
    "st_petersburg_renovated": {"min": 295, "max": 333, "avg": 318},
}

def get_training_context():
    """Gibt einen formatierten Trainingskontext für die KI zurück."""
    context = """
=== HISTORISCHE DEALS — EYDURA HOME SOLUTIONS ===

DEAL 1: 4546 Ontario Dr, New Port Richey (Pasco County)
- Ankauf: $70.000 (Feb 2025) | Verkauf: $220.000 (Aug 2025)
- Hold: 6 Monate | Sqft: 1.492 | Baujahr: 1977 | Waterfront
- Bruttogewinn: $150.000 | ARV: $147/sqft
- Lektion: Waterfront NPR erzielt $147/sqft. Ankauf weit unter Marktwert möglich bei distressed Seller.

DEAL 2: 6813 Circle Creek Dr, Pinellas Park (Pinellas County)
- Ankauf: $250.000 (Sep 2025) | Verkauf: $445.000 (Jan 2026)
- Hold: 4 Monate | Sqft: 1.506 | Baujahr: 1979 | Flood Zone AE
- Renovierung: $68.000 ($45/sqft) | Nettogewinn: ~$127.000 | ARV: $295/sqft
- Vollrenovierung: Dach $13k, 2 Bäder $10k, LVP $7,5k, Küche $12k, Fenster $4k

RENOVIERUNGSKOSTEN-BENCHMARKS (aus echten Deals):
- Interior Paint: $1,50/sqft
- LVP Boden: $5,00/sqft  
- Küche komplett: $12.000 (Cabinets + Countertops + Geräte)
- Bad High-End: $5.000/Bad
- Fenster: $500/Stück
- Dach: $13.000 (typisch für 1.500 sqft SFR)
- HVAC 3-Ton: $4.000
- Gesamt typisch Pinellas: $45/sqft für Vollrenovierung

ARV-BENCHMARKS aus Comps (Pinellas Park / St. Pete):
- Renoviert: $280-333/sqft (Durchschnitt $312/sqft)
- Nicht renoviert: $166-200/sqft

ARV-BENCHMARKS Pasco (New Port Richey):
- Renoviert Waterfront: $140-160/sqft
- Standard: $120-145/sqft
"""
    return context

if __name__ == "__main__":
    print(get_training_context())
    print(f"\n{len(HISTORICAL_DEALS)} Deals geladen")
    print(f"Deal 2 Renovierung: ${sum(i['cost'] for i in HISTORICAL_DEALS[1]['renovation_items']):,}")


# Visuelle Zustandsanalyse Deal 1 beim Ankauf
DEAL_1_CONDITION_AT_PURCHASE = {
    "address": "4546 Ontario Dr, New Port Richey, FL 34652",
    "purchase_price": 70000,
    "condition_grade": "D+",  # sehr schlechter Zustand
    
    "exterior": {
        "grade": "D",
        "issues": [
            "Fassade komplett verwittert, Farbe abgeplatzt überall",
            "Holzverkleidung (T1-11 Siding) stark beschädigt und vermodert",
            "Steinverkleidung an Fassade verwittert",
            "Dachzustand: Composition Shingles — äußerlich relativ OK (neueres Dach sichtbar)",
            "Grundstück verwildert, kein Rasen, Gestrüpp",
            "Überwucherter Backyard mit Bananenstauden und Wildwuchs direkt am Waterfront",
            "Außenwände mit Schimmelflecken",
            "Gutters beschädigt",
        ],
        "renovation_needed": ["Komplett-Außenverkleidung ersetzen oder Stucco", "Neuer Außenanstrich", "Landscaping komplett neu"]
    },
    
    "living_areas": {
        "grade": "D",
        "issues": [
            "Decke in Wohnzimmer: Wasserflecken und durchhängende Teile — Wasserschaden von oben",
            "Popcorn-Decken überall — Asbestalarm bei Baujahr 1977",
            "Böden: alte Linoleum/Vinylkacheln in schlechtem Zustand",
            "Wände: Flecken, Schäden, teilweise komplett abgeplatzt",
            "Holzbalken-Raumteiler (70er-Style) muss entfernt werden",
            "Steinwand im Wohnbereich — optisch veraltet, Entfernung aufwändig",
        ],
        "renovation_needed": ["Decke reparieren/erneuern", "Böden komplett neu (LVP)", "Wände spachteln und streichen", "Raumteiler entfernen"]
    },
    
    "kitchen": {
        "grade": "D-",
        "issues": [
            "Küche komplett original aus den 70ern",
            "Schimmelflecken an Unterschränken sichtbar",
            "Küchenfronten stark verschmutzt und beschädigt",
            "Fliesen-Backsplash veraltet",
            "Keine funktionsfähigen Geräte",
            "Bodenfliesen stark verschmutzt/beschädigt",
        ],
        "renovation_needed": ["Küche komplett neu: Cabinets, Countertops, Geräte, Backsplash, Boden"]
    },
    
    "bathrooms": {
        "grade": "D",
        "issues": [
            "Bad 1: Fliesen original 70er, Schimmel an Wand-/Deckenübergängen",
            "Bad 2: Massiver Schimmelbefall an Wänden (dunkelblau + Schimmel)",
            "Beide Bäder komplett veraltet",
            "Schimmel hinter Vanity sichtbar",
        ],
        "renovation_needed": ["Beide Bäder komplett neu"]
    },
    
    "bedrooms": {
        "grade": "D-",
        "critical_finding": "MASSIVER SCHIMMELBEFALL",
        "issues": [
            "Schlafzimmer 1: Schimmel bodennah auf blauer Wand, Floorboden nackt (Teppich entfernt)",
            "Schlafzimmer 2: EXTREMER Schimmelbefall — alle Wände bis 60cm Höhe schwarz",
            "Masterbedroom: Schimmel an Wänden, Wasserstand sichtbar (Flutmarke)",
            "Schlafzimmer 3: Schimmel in Ecken und bodennah",
            "FLUTMARKE auf Wänden deutlich sichtbar — Haus war überflutet (Flood Zone AE!)",
            "Alle Böden nackt (Teppich bereits entfernt vor Listing)",
        ],
        "renovation_needed": ["Professionelle Schimmelentfernung/Remediation MUSS", "Komplette Wandsanierung", "Neue Böden"]
    },
    
    "enclosed_porch_florida_room": {
        "grade": "F",
        "issues": [
            "Florida Room / enclosed porch: massivster Schimmelbefall im gesamten Objekt",
            "Alle Wände vollflächig mit Schimmel bedeckt",
            "Betonboden — Wasser stand hier",
            "Decke komplett verschimmelt",
            "Kamin aus Backstein — strukturell OK aber Raum drumherum komplett beschädigt",
            "Holzvertäfelung und Wandpaneele komplett durchfeuchtet",
        ],
        "renovation_needed": ["Komplette Entkernung des Florida Rooms", "Professionelle Schimmelremediation", "Neubau des Florida Rooms oder Konvertierung"]
    },
    
    "utility_laundry": {
        "grade": "D",
        "issues": [
            "Waschküche: Schimmel auf Wänden",
            "Elektrische Leitungen sichtbar und unsachgemäß verlegt",
            "HVAC-Schlauch auf Boden — HVAC funktionslos oder entfernt",
        ],
        "renovation_needed": ["Neue elektrische Installation", "Neuer HVAC", "Schimmelentfernung"]
    },
    
    "structural_electrical": {
        "grade": "D",
        "issues": [
            "Elektrisches Panel sichtbar im Wohnbereich — veraltetes System",
            "Freiliegende Leitungen in mehreren Räumen",
            "Wasserschaden-Spuren an Decken — mögliche strukturelle Schäden",
            "Dachüberstand mit Schimmel außen",
        ],
        "renovation_needed": ["Elektrische Überholung", "Wasserschaden-Assessment", "Strukturprüfung"]
    },
    
    "waterfront_backyard": {
        "grade": "C-",
        "notes": "Direkter Wasserzugang zum Teich/See sichtbar — das ist der VALUE des Objekts. Trotz komplett verwildertem Garten ist der Wasserblick klar erkennbar. Dies rechtfertigt den Premium-Verkaufspreis von $220k trotz des desaströsen Zustands."
    },
    
    "key_insight": """
    LERNEFFEKT FÜR KI-TRAINING:
    Dieses Objekt wurde für $70k gekauft und für $220k verkauft trotz:
    - Massivem Schimmelbefall in fast allen Räumen (Flutschäden aus Flood Zone AE)
    - Komplett verrotteter Außenverkleidung
    - Nicht funktionsfähiger Küche, beider Bäder, HVAC
    - Totalrenovierung notwendig
    
    Der Schlüssel war: WATERFRONT-LAGE in Pasco County.
    Der Schimmel/Flutschaden war eingepreist im $70k Kaufpreis.
    Nach Remediation + Vollrenovierung: $220k erzielbar.
    
    Renovierungskosten-Schätzung für dieses Objekt (1.492 sqft, massiver Schimmel):
    - Schimmelremediation: $8.000-15.000 (professionell, mehrere Räume)
    - Außenverkleidung/Stucco: $8.000-12.000
    - Küche komplett: $10.000-15.000
    - Bäder (2x): $8.000-10.000
    - Böden LVP: $7.000-9.000
    - HVAC neu: $4.000-5.000
    - Elektrik: $3.000-5.000
    - Malen innen+außen: $5.000-7.000
    - Florida Room Sanierung: $5.000-10.000
    - Landscaping: $2.000-3.000
    - Diverses/Misc: $5.000
    GESCHÄTZTER GESAMTAUFWAND: $65.000-$96.000
    TATSÄCHLICHER GEWINN nach Reno: ~$80.000-$85.000 netto (bei $65-85k Reno)
    """,
    
    "condition_red_flags": [
        "FLUTSCHÄDEN sichtbar — Flood Zone AE, Hurrican-Überflutung",
        "Schimmelbefall in 80%+ aller Räume — professionelle Remediation zwingend",
        "Komplette Außenverkleidung defekt",
        "HVAC nicht vorhanden/funktionslos",
        "Elektrische Anlage veraltet und unsicher",
        "Alle Böden und Böden in Florida Room beschädigt"
    ],
    
    "why_it_worked": [
        "Waterfront-Lage rechtfertigt Premium-ARV in Pasco County",
        "$70k Ankauf war Spottpreis — Schimmel hatte alle anderen Käufer abgeschreckt",
        "Schimmelremediation ist teuer aber kalkulierbar",
        "Nach Remediation und Reno: normales Haus mit Wasserblick = $220k"
    ]
}


# Visuelle Zustandsanalyse Deal 1 NACH Renovierung (Verkaufszustand Mai 2025)
DEAL_1_CONDITION_AFTER_RENOVATION = {
    "address": "4546 Ontario Dr, New Port Richey, FL 34652",
    "sale_price": 220000,
    "renovation_date_complete": "2025-05",
    
    "exterior_after": {
        "grade": "B+",
        "what_was_done": [
            "Komplette Stucco-Verkleidung neu — altes T1-11 Holzsiding komplett ersetzt",
            "Farbe: leuchtendes Blau — charakteristisch, hebt sich ab",
            "Neue weiße Fensterrahmen überall — frisches Erscheinungsbild",
            "Dach: bestehendes Komposit-Schindeldach behalten (war noch OK)",
            "Mini-Split HVAC außen installiert sichtbar (Daikin/Fujitsu-Type)",
            "Neuer schwarzer Holzzaun links installiert",
            "Grundstück: Rasen gemäht, Grundreinigung — kein vollständiges Landscaping",
            "Neue weiße Dachuntersicht (Soffit/Fascia) erneuert",
        ],
        "cost_insight": "Stucco-Vollverkleidung statt Neubeplankung — kostengünstiger und langlebiger in Florida"
    },
    
    "florida_room_after": {
        "grade": "B",
        "what_was_done": [
            "Florida Room komplett saniert — war vorher der schlimmste Bereich",
            "Kamin aus Backstein: weiß gestrichen/gekalkt — modernes Erscheinungsbild",
            "Wände: blau gestrichen (Holzpaneele behalten aber gestrichen)",
            "Boden: grauer Epoxidboden/Betonfarbe — günstig und funktional",
            "Neue Decke weiß verputzt",
            "Neue Screens/Fliegengitter-Elemente",
            "Neue Beleuchtung (Deckenleuchte)",
            "Schiebetüren zu Haus hin erneuert",
        ],
        "key_learning": "Florida Room NICHT abgerissen sondern günstig saniert — Stucco+Farbe+Epoxy statt Neubau. Kosteneinsparung ca. $8.000-12.000 vs. Abriss und Neubau",
        "waterfront_view": "DIREKTER WASSERBLICK aus Florida Room auf den Teich/See — DAS ist der Verkaufshebel. Käufer sehen sofort den Mehrwert."
    },
    
    "hvac_solution": {
        "type": "Mini-Split (Ductless)",
        "brand_visible": "FREX oder ähnlich — günstige Mini-Split-Einheit",
        "cost_estimate": "$2.500-4.000 für Mini-Split vs. $6.000-8.000 für Central HVAC",
        "key_learning": "Bei Flutobjekten ohne Ductwork: Mini-Split günstiger als zentrales HVAC-System. Spart $3.000-4.000 Installationskosten. Für Pasco County / Einfachobjekte akzeptabel."
    },
    
    "renovation_strategy_insight": {
        "approach": "Kostenminimierung bei maximaler Präsentation",
        "key_decisions": [
            "Stucco über altes Siding statt komplettem Abriss — spart $3.000-5.000",
            "Mini-Split statt Central HVAC — spart $3.000-4.000",
            "Florida Room saniert statt abgerissen — spart $8.000-12.000",
            "Kamin weiß gestrichen statt entfernt — kostet $200 statt $2.000",
            "Betonboden mit Epoxy statt LVP im Florida Room — spart $2.000",
            "Dach wurde NICHT ersetzt (war noch OK) — spart $10.000-15.000",
            "Landscaping minimal (nur gemäht) — spart $2.000-3.000",
        ],
        "total_estimated_savings_vs_premium_reno": "$31.000-43.000",
        "result": "Verkauf für $220k trotz sparsamem Renovierungsansatz dank Waterfront-Lage"
    },
    
    "before_after_transformation": {
        "exterior": "Von: verwitterte weiße Holzverkleidung, komplett abgeplätzt → Zu: frischer blauer Stucco, neue Fensterrahmen",
        "florida_room": "Von: vollflächig schwarz-verschimmelter Schandfleck, Betonboden nackt → Zu: gemütlicher Wohnraum mit Wasserblick, weißer Kamin, grauer Epoxiboden",
        "hvac": "Von: kein HVAC vorhanden → Zu: Mini-Split außen montiert, funktionsfähig",
        "overall": "Von: Schrottobjekt das jeden abschreckt → Zu: bewohnbares Haus mit besonderem Merkmal (Waterfront-Florida-Room)"
    },
    
    "lessons_for_ai": """
KRITISCHE LERNPUNKTE AUS DEAL 1 VORHER/NACHHER:

1. STUCCO ÜBER SIDING: In Florida Standard-Praxis. Günstiger als Abriss. 
   Kosten: $6-8/sqft für Außenfläche = ca. $6.000-10.000 für typisches SFR.
   
2. MINI-SPLIT HVAC: Bei Flutobjekten ohne Ductwork = beste Lösung.
   Kosten: $2.500-4.000 installiert. Funktioniert für Pasco-Objekte bis 1.500 sqft.
   
3. FLORIDA ROOM STRATEGIE: Nicht abreißen wenn strukturell OK.
   Sanierung mit Farbe + Epoxiboden + neue Screens = $3.000-5.000.
   vs. Abriss + Neubau = $15.000-25.000.
   
4. WASSERBLICK ALS VERKAUFSARGUMENT: Käufer kaufen das Gefühl.
   Der Florida Room gibt direkten Wasserblick — das rechtfertigt Premium.
   Ohne Waterfront wäre ARV $140-150/sqft gewesen.
   Mit Waterfront + renoviertem Florida Room: $147/sqft erzielt.
   
5. MINIMALRENOVIERUNG BEI NIEDRIGPREISSEGMENT:
   Pasco County $70k-$220k Segment: Käufer erwarten kein High-End.
   Sauber, funktional, besonderes Merkmal reicht.
   Im Vergleich: Pinellas Park $250k-$445k: High-End Vollrenovierung nötig.
   
6. DACH ASSESSMENT: Wenn Dach noch 5+ Jahre hält — nicht austauschen.
   Spart $10.000-15.000 = bedeutendste Einzelentscheidung im Projekt.
"""
}


# Zusätzliche Innenraumfotos Deal 1 nach Renovierung
DEAL_1_INTERIOR_AFTER = {
    "hvac_solution_detail": {
        "brand": "GREE / Trane / ähnlich — Mini-Split Wandeinheit",
        "installation": "Inneneinheit an der Wand, Außeneinheit außen — keine Ductwork nötig",
        "pro_room_units": True,
        "key_finding": "MEHRERE Mini-Split Einheiten installiert — mindestens 2 sichtbar (Bild 4 + Bild 5). Jedes Zimmer hat eigene Einheit. Kostenschätzung: $1.500-2.500 pro Einheit installiert.",
        "total_cost_estimate": "$5.000-8.000 für Multi-Zone Mini-Split System",
        "vs_central": "Zentrales Ductsystem in einem Fluthaus: $8.000-15.000. Mini-Split spart $3.000-7.000."
    },

    "flooring_detail": {
        "type": "LVP — dunkles Holzdekor, grau-braun Ton",
        "style": "Plank-Format, zeitgemäß",
        "quality": "Mittleres Segment — funktional und ansprechend",
        "cost_per_sqft": 4.50,
        "key_finding": "Gleiches LVP in allen Zimmern durchgängig — günstiger bei Großeinkauf und einfacher Installation. Dunkler Ton kaschiert Mängel besser als hell.",
        "note": "Bodenfliesen im Florida Room (grauer Epoxy) bleiben — nur Hauptwohnbereich mit LVP"
    },

    "bedroom_transformation": {
        "before": "Massiver Schimmel bis 60cm Höhe an allen Wänden, nackte Betonböden",
        "after": "Wände komplett weiß/hellgrau gestrichen, neue Baseboard, LVP Boden, neue Türen schwarz, Mini-Split",
        "key_process": [
            "1. Schimmelremediation: Befallene Wandbereiche herausschneiden",
            "2. Drywall-Ersatz in befallenen Bereichen",
            "3. Anti-Schimmel Grundierung auf alle Wände",
            "4. Wände glatt spachteln und streichen (hellgrau)",
            "5. Neues LVP verlegen",
            "6. Neue weiße Baseboards",
            "7. Neue Zimmertüren (weiß, schwarze Beschläge)",
            "8. Mini-Split montieren"
        ],
        "cost_per_bedroom_estimate": "$3.500-5.000 inkl. anteilige Remediation"
    },

    "door_hardware": {
        "style": "Weiße Türen + schwarze Beschläge/Griffe",
        "cost": "$150-210 pro Tür komplett",
        "design_note": "Schwarz/Weiß Kontrast = moderner Look, günstig umsetzbar. Hebt Qualitätseindruck."
    },

    "final_renovation_breakdown_deal1": {
        "estimated_actual_costs": {
            "schimmelremediation_professional": 10000,
            "stucco_aussen_komplett": 9000,
            "mini_split_system_multizone": 7000,
            "lvp_boden_alle_zimmer": 6000,
            "wände_spachteln_streichen_innen": 4000,
            "küche_komplett": 12000,
            "bäder_2x": 8000,
            "florida_room_sanierung": 4000,
            "türen_und_beschläge": 2500,
            "elektrik_misc": 3000,
            "baseboards_trim": 1500,
            "landscaping_minimal": 1000,
            "trashout_dumpster": 1000,
            "misc_permit_misc": 3000,
        },
        "total_estimated": 72000,
        "gross_profit": 150000,
        "net_profit_estimated": 78000,
        "roi_estimated": "111% auf investiertes Kapital ($70k Kauf + $72k Reno = $142k)",
        "hold_time_months": 6
    }
}

def get_full_training_context():
    """Vollständiger Trainingskontext inkl. aller Deal-Details für KI-Analyse."""
    from training_data import get_training_context
    base = get_training_context()

    full = base + """
INNENRAUM-RENOVIERUNGSDETAILS DEAL 1 (aus Vorher/Nachher-Fotos):

HVAC-LÖSUNG: Zentrales HVAC + zusätzliche Mini-Split Zonen
- Zentrales System erneuert: $5.000-8.000
- Zusätzliche Mini-Split Wandeinheiten in Schlafzimmern: $1.500-2.500/Zone

BÖDEN-STANDARD DEAL 1:
- LVP grau-braun Holzdekor, Plankformat, ca. $4.50/sqft
- Durchgängig in allen Schlafzimmern und Wohnbereichen
- Florida Room: grauer Epoxy-Beton ($0.80-1.20/sqft)

KÜCHEN-BENCHMARK DEAL 1 (Pasco $220k):
- RTA White Shaker Cabinets + schwarze Bar-Griffe: $4.500
- Granit Countertops (nicht Quartz): $2.500
- Frigidaire Edelstahl-Paket komplett: $3.500
- Hexagon Backsplash grau: $600
- Schwarzes Farmhouse-Spülbecken + Hahn: $400
- Island: $800
- TOTAL KÜCHE: ~$13.500

BAD-BENCHMARK DEAL 1:
- Walk-in Dusche mit schwarzem Glasrahmen: $900-1.200
- Marmor-Look Porzellanfliesen (12x24): $800-1.200
- Weißer Vanity + schwarze Griffe: $400-600
- Rahmenloser Spiegel + schwarze Wandleuchte: $200-300
- TOTAL MASTERBAD: ~$4.500-6.000

DESIGN-SYSTEM PASCO (Deal 1): Weiß/Grau Wände + Grau LVP + Schwarz Akzente + Blauer Stucco
DESIGN-SYSTEM PINELLAS (Deal 2): Weißer Stucco + Dunkelgraues Dach + Grüne Akzenttür + High-End Bäder

KORREKTE DEAL 1 ABRECHNUNG:
Ankauf $70k + Renovation ~$94k = $164k investiert → Verkauf $220k → Nettogewinn ~$43k (26% ROI)

DEAL 2 ABRECHNUNG (Pinellas Park):
Ankauf $250k + Renovation $68k = $318k investiert → Verkauf $445k → Nettogewinn ~$102k (32% ROI)

VERGLEICH BEIDE DEALS:
- Deal 2 (Pinellas) profitabler: $102k vs $43k Nettogewinn
- Deal 2 schneller: 4 Monate vs 6 Monate Hold
- Deal 2 niedrigere Renovierungskosten: $68k vs $94k (trotz höherem Verkaufspreis!)
- Schlüssel: Pinellas höherer ARV/sqft ($295) + niedrigere Reno nötig (kein Schimmel/Flut)
- Empfehlung: Pinellas deals bei $200-300k Ankauf bevorzugen wenn verfügbar
"""
    return full


# Deal 2 — Innenraum-Details nach Renovierung (professionelle MLS-Fotos)
DEAL_2_INTERIOR_STAGING = {

    "masterbedroom_after": {
        "flooring": {
            "type": "Helles LVP — warmer Eichenholzton, sehr hell",
            "color": "Natural Oak / Blond — komplett anders als Deal 1 dunkelgrau",
            "key_learning": "Deal 1 Pasco: DUNKLES Grau LVP. Deal 2 Pinellas Premium: HELLES Oak LVP. Helles LVP lässt Räume größer wirken = bessere Fotos = höherer Verkaufspreis. Kosten ähnlich: $3.50-5/sqft."
        },
        "ceiling_fan": {
            "style": "Moderner Holzoptik-Deckenventilator mit integriertem Licht — Bronze/Messing-Finish",
            "cost": "$80-150 bei Home Depot",
            "note": "Bewusst warmer Ton statt schwarz — passt zur hellen, warmen Palette von Deal 2"
        },
        "walls": "Reines Weiß — keine Grautöne wie Deal 1. Hellstes Weiß maximiert Lichtreflexion",
        "windows": "Neue Doppelflügelfenster, weiße Rahmen ohne schwarze Profile (anders als Deal 1)",
        "baseboards": "Hohe weiße Baseboards — professionell, sauber",
        "staging": {
            "used": True,
            "style": "Modernes Coastal/Skandinavisch — Beige, Creme, Naturholz, Gold-Akzente",
            "key_learning": "HOME STAGING wurde für Deal 2 eingesetzt — nicht für Deal 1. Professionelles Staging erhöht Verkaufspreis um $10.000-20.000 bei Pinellas Premium-Objekten.",
            "staging_cost": "$2.000-4.000 für 4-6 Wochen professionelles Staging",
            "roi_staging": "Investment ~$3.000 → zusätzliche $10.000-15.000 im Verkaufspreis = sehr lohnenswert"
        }
    },

    "deal2_design_system_complete": {
        "palette": "Reines Weiß Wände + Helles Oak LVP + Bronze/Messing Akzente + Weiße Fensterrahmen",
        "vs_deal1": "Deal 1: Grau Wände + Dunkel Grau LVP + Schwarz Akzente. Deal 2: Weiß Wände + Hell LVP + Warm Bronze.",
        "principle": "Pinellas Premium $400k+: HELL, WARM, LUFTIG. Pasco Budget $200k: MODERN, KÜHL, KONTRAST.",
        "photography": "Professionelle Immobilienfotografie für Deal 2 (helle, gesättigte Bilder). Deal 1: DJI Drohnen-Eigenfotos.",
        "photography_cost": "$200-500 für professionelle Immobilienfotografie",
        "photography_roi": "Professionelle Fotos → mehr Clicks → mehr Besichtigungen → schnellerer Verkauf"
    },

    "deal2_complete_strategy_summary": {
        "segment": "Pinellas Park $400k-500k — Mittleres bis gehobenes Segment",
        "buyer_profile": "Familien, Suburban, wollen fertig renoviertes Objekt, bezahlen Premium für Qualität",
        "renovation_approach": "Vollrenovierung High-End (Bad-Marmorfliesen, Granite, professionelles Staging)",
        "exterior": "Weiß Stucco + Dunkelgraues Dach + Grüne Akzenttür = maximale Curb Appeal",
        "interior_floors": "Helles Oak LVP = Räume wirken größer + wärmer + premium",
        "marketing": "Professionelle Fotos + Home Staging = maximaler Online-Eindruck",
        "result": "DOM nur 7 Tage — eines der schnellsten Verkäufe im County",
        "net_profit": "$102.000 in 4 Monaten"
    },

    "ai_training_comparison_final": """
FINALER VERGLEICH BEIDE EYDURA DEALS — KI-LERNPROFIL:

╔══════════════════════════════════════════════════════════╗
║ DEAL 1: Ontario Dr, New Port Richey (PASCO)              ║
║ Ankauf: $70k → Verkauf: $220k → Nettogewinn: ~$43k       ║
║ Reno: $94k (Flut/Schimmel) | Hold: 6 Monate | ROI: 26%  ║
║ Exterior: Blauer Stucco | Interior: Dunkel LVP + Schwarz ║
║ HVAC: Zentral + Mini-Split | Fotos: Eigenfotos DJI       ║
╚══════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════╗
║ DEAL 2: Circle Creek Dr, Pinellas Park (PINELLAS)        ║
║ Ankauf: $250k → Verkauf: $445k → Nettogewinn: ~$102k     ║
║ Reno: $68k (Standard) | Hold: 4 Monate | ROI: 32%        ║
║ Exterior: Weiß Stucco + Grüne Tür | Interior: Hell LVP  ║
║ HVAC: Zentral | Staging: Professionell | Fotos: Pro      ║
╚══════════════════════════════════════════════════════════╝

EMPFEHLUNG FÜR NEUE DEALS:
→ Pinellas Objekte $200-300k Ankauf ohne Flutschäden = BEVORZUGTE STRATEGIE
→ Pasco Objekte mit Flutschäden nur bei sehr niedrigem Ankauf (<$100k) und Wasserfront
→ Home Staging + Pro-Fotos bei Pinellas $350k+ immer einsetzen
→ Helles Oak LVP für Pinellas, Dunkles Grau LVP für Pasco
→ Weißer Stucco für Premium, Farbiger Stucco für Budget-Segment
"""
}
