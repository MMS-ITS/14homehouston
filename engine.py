#!/usr/bin/env python3
"""
MMS Consortium — Rental Property Due Diligence engine.
Implements sections 5 (investment analysis), 6 (21-factor scorecard),
7 (red flags) and 10 (recommendation) of the master template.

Every figure produced here is derived from data/properties.json, which carries
the source and date for each input. Nothing is invented: inputs that could not
be verified are flagged and carried through as `provisional`.
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------------
# Section 2 — standard assumptions
# ----------------------------------------------------------------------------
A = dict(
    down_pct=0.20, rate=0.065, years=30, closing_pct=0.03,
    tax_std=0.0298, vacancy=0.05, maint_pct=0.01,
    ins_pct=0.006, mgmt_pct=0.08, other_monthly=0.0,
    appreciation=0.03, selling_costs=0.07,
)

# Reference points for derived geography factors (great-circle, straight line).
AIRPORTS = [
    ("George Bush Intercontinental (IAH)", 29.9902, -95.3368),
    ("William P. Hobby (HOU)", 29.6454, -95.2789),
    ("Dallas/Fort Worth (DFW)", 32.8998, -97.0403),
    ("Dallas Love Field (DAL)", 32.8471, -96.8518),
    ("Austin–Bergstrom (AUS)", 30.1975, -97.6664),
    ("Lafayette Regional (LFT)", 30.2053, -91.9876),
    ("Lake Charles Regional (LCH)", 30.1261, -93.2234),
    ("Easterwood Field, College Station (CLL)", 30.5886, -96.3638),
]
UNIVERSITIES = [
    ("Texas A&M University, College Station", 30.6188, -96.3365),
    ("University of Houston", 29.7199, -95.3422),
    ("UT Dallas", 32.9857, -96.7501),
    ("Texas Christian University, Fort Worth", 32.7097, -97.3626),
    ("Hill College, Cleburne", 32.3470, -97.3860),
    ("Collin College, McKinney", 33.1976, -96.6150),
    ("University of Louisiana at Lafayette", 30.2137, -92.0190),
    ("McNeese State University, Lake Charles", 30.1800, -93.2170),
    ("Lone Star College, Conroe", 30.3000, -95.4800),
    ("Blinn College, Brenham", 30.1669, -96.3977),
    ("Brazosport College, Lake Jackson", 29.0375, -95.4383),
    ("Wharton County Junior College", 29.3116, -96.1027),
    ("San Jacinto College, Houston", 29.6619, -95.1241),
]
# Metro job-market anchors (used for factor 5, flagged provisional).
METRO_JOBS = {
    "Houston": 7, "Houston (Conroe)": 7, "Dallas–Fort Worth": 7,
    "Bryan–College Station": 6, "Lafayette": 5, "Lake Charles": 5,
}
# County population-growth anchors (factor 12, flagged provisional).
COUNTY_GROWTH = {
    "Collin County": 9, "Fort Bend County": 9, "Montgomery County": 9,
    "Liberty County": 8, "Harris County": 6, "Johnson County": 8,
    "Burleson County": 4, "Brazoria County": 7,
    "Lafayette Parish (Carencro)": 4, "Calcasieu Parish": 3,
}
# Regional climate normals, °C (factor 7 narrative).
CLIMATE = {
    "Houston": "summer highs ~35 °C, winter lows ~6 °C",
    "Houston (Conroe)": "summer highs ~35 °C, winter lows ~5 °C",
    "Dallas–Fort Worth": "summer highs ~36 °C, winter lows ~2 °C",
    "Bryan–College Station": "summer highs ~36 °C, winter lows ~5 °C",
    "Lafayette": "summer highs ~33 °C, winter lows ~7 °C",
    "Lake Charles": "summer highs ~33 °C, winter lows ~7 °C",
}
# Zillow/Realtor home-value year-on-year readings gathered 4 Oct 2026 (factor 9).
APPREC_YOY = {
    "Crosby": -0.7, "Conroe": -0.9, "Cut and Shoot": -0.9, "Cleburne": -4.0,
    "Huffman": -2.5, "Needville": 0.5, "Dayton": 2.0, "Farmersville": 1.1,
}
# Local $/sqft benchmarks gathered 4 Oct 2026 (factor 3). None = no benchmark found.
PSF_BENCH = {
    "Huffman": (153, "HAR Huffman market page, average price per square foot, Sep 2026"),
    "Snook": (186, "Realtor.com Snook market page, price per square foot, Oct 2026"),
    "Cleburne": (None, None),
}

WEIGHTS = [15, 10, 7, 7, 7, 6, 5, 5, 5, 4, 4, 4, 4, 3, 3, 3, 2, 2, 2, 1, 1]
FACTOR_NAMES = [
    "Cash flow and returns", "Rental demand and vacancy", "Price against market value",
    "Location and neighbourhood", "Job opportunities", "Schools",
    "Weather and natural hazards", "Workmanship and build quality",
    "Appreciation and resale", "Builder goodwill and warranty",
    "HOA fee and leasing rules", "Population growth", "Crime and safety",
    "Property tax", "Demographics", "Distances to facilities", "Insurance cost",
    "Community amenities", "Airport access", "University or college", "Walk Score",
]


def haversine(a_lat, a_lon, b_lat, b_lon):
    R = 6371.0
    p1, p2 = math.radians(a_lat), math.radians(b_lat)
    dp = p2 - p1
    dl = math.radians(b_lon - a_lon)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def nearest(lat, lon, table):
    best = min(table, key=lambda t: haversine(lat, lon, t[1], t[2]))
    return best[0], haversine(lat, lon, best[1], best[2])


def clamp(v, lo=1.0, hi=10.0):
    return max(lo, min(hi, v))


def pi_payment(loan, rate=A["rate"], years=A["years"]):
    r = rate / 12.0
    n = years * 12
    if r == 0:
        return loan / n
    return loan * r * (1 + r) ** n / ((1 + r) ** n - 1)


def balance_after(loan, months, rate=A["rate"], years=A["years"]):
    r = rate / 12.0
    n = years * 12
    if r == 0:
        return loan * (1 - months / n)
    pmt = pi_payment(loan, rate, years)
    return loan * (1 + r) ** months - pmt * (((1 + r) ** months - 1) / r)


# ----------------------------------------------------------------------------
# Section 5 — investment analysis
# ----------------------------------------------------------------------------
def analyse(p, price=None, rent=None, tax_rate=None, ins_pct=None,
            vacancy=None, maint_pct=None, mgmt_pct=None, hoa_month=None,
            rate=None, other_monthly=None):
    price = float(price if price is not None else p["price"])
    rent = float(rent if rent is not None else p["rent_realistic"])
    tax_rate = float(tax_rate if tax_rate is not None
                     else (p["tax_rate_pct"] / 100.0 if p.get("tax_rate_pct") else A["tax_std"]))
    ins_pct = A["ins_pct"] if ins_pct is None else float(ins_pct)
    vacancy = A["vacancy"] if vacancy is None else float(vacancy)
    maint_pct = A["maint_pct"] if maint_pct is None else float(maint_pct)
    mgmt_pct = A["mgmt_pct"] if mgmt_pct is None else float(mgmt_pct)
    rate = A["rate"] if rate is None else float(rate)
    other_m = A["other_monthly"] if other_monthly is None else float(other_monthly)
    hoa_m = float(hoa_month if hoa_month is not None else (p.get("hoa_month") or 0.0))

    down = price * A["down_pct"]
    loan = price - down
    closing = price * A["closing_pct"]
    makeready = float(p.get("makeready") or 0)
    cash_invested = down + closing + makeready

    pi = pi_payment(loan, rate)
    eff_rent = rent * (1 - vacancy)
    tax_m = price * tax_rate / 12.0
    ins_m = price * ins_pct / 12.0
    maint_m = price * maint_pct / 12.0
    mgmt_m = eff_rent * mgmt_pct
    opex_m = tax_m + ins_m + hoa_m + maint_m + mgmt_m + other_m

    noi_m = eff_rent - opex_m
    cf_m = noi_m - pi

    cap = (noi_m * 12) / price if price else 0
    coc = (cf_m * 12) / cash_invested if cash_invested else 0
    dscr = (noi_m / pi) if pi else 0
    gross_yield = (rent * 12) / price if price else 0
    rent_to_price = rent / price if price else 0

    # Break-even rent: eff*(1-mgmt) must cover fixed costs + debt
    fixed = tax_m + ins_m + hoa_m + maint_m + other_m + pi
    be_rent = fixed / ((1 - mgmt_pct) * (1 - vacancy)) if rent else 0
    be_occ = fixed / ((1 - mgmt_pct) * rent) if rent else 0

    # Max price at $0 cash flow (tax, insurance, maintenance and debt all scale with price)
    k = pi_payment(1.0, rate)  # monthly payment per $1 of loan
    denom = (tax_rate + ins_pct + maint_pct) / 12.0 + (1 - A["down_pct"]) * k
    numer = eff_rent * (1 - mgmt_pct) - hoa_m - other_m
    max_price = numer / denom if denom > 0 else 0

    # 5-year view
    months = 60
    bal = balance_after(loan, months, rate)
    principal_paid = loan - bal
    value5 = price * (1 + A["appreciation"]) ** 5
    net_proceeds = value5 * (1 - A["selling_costs"]) - bal
    cum_cf = cf_m * months
    terminal = cum_cf + net_proceeds
    ann = ((terminal / cash_invested) ** (1 / 5) - 1) if (cash_invested > 0 and terminal > 0) else None

    # Break-even mortgage rate: the rate at which cash flow reaches $0, holding
    # price and rent fixed. If even a 0% loan cannot be covered by NOI, the
    # deal is unreachable through financing alone.
    zero_rate_pi = loan / (A["years"] * 12)
    if noi_m < zero_rate_pi:
        be_rate = None  # not achievable at any interest rate
    else:
        lo, hi = 0.0, 0.25
        for _ in range(80):
            mid = (lo + hi) / 2
            if pi_payment(loan, mid) > noi_m:
                hi = mid
            else:
                lo = mid
        be_rate = (lo + hi) / 2

    return dict(
        be_rate=be_rate, zero_rate_pi=zero_rate_pi,
        rent_needed_1pct=price * 0.01,
        price=price, rent=rent, tax_rate=tax_rate, ins_pct=ins_pct, hoa_month=hoa_m,
        down=down, loan=loan, closing=closing, makeready=makeready,
        cash_invested=cash_invested, pi=pi, eff_rent=eff_rent,
        tax_m=tax_m, ins_m=ins_m, maint_m=maint_m, mgmt_m=mgmt_m, other_m=other_m,
        opex_m=opex_m, noi_m=noi_m, noi_y=noi_m * 12, cf_m=cf_m, cf_y=cf_m * 12,
        cap=cap, coc=coc, dscr=dscr, gross_yield=gross_yield, rent_to_price=rent_to_price,
        be_rent=be_rent, be_occ=be_occ, max_price=max_price,
        psf=price / p["sqft"] if p.get("sqft") else None,
        principal_paid=principal_paid, value5=value5, balance5=bal,
        net_proceeds=net_proceeds, cum_cf=cum_cf, ann_return=ann,
    )


def sensitivity(p):
    base = p["price"]
    out = []
    for delta in (0, -20000, -40000):
        r = analyse(p, price=base + delta)
        out.append(dict(delta=delta, price=base + delta, cf_m=r["cf_m"], coc=r["coc"], dscr=r["dscr"]))
    return out


def stress(p):
    rows = []
    rows.append(("At the standard assumptions", analyse(p)))
    rows.append(("Rent 10% lower", analyse(p, rent=p["rent_realistic"] * 0.9)))
    rows.append(("Vacancy 10%", analyse(p, vacancy=0.10)))
    rows.append(("Maintenance 1.5% of price", analyse(p, maint_pct=0.015)))
    rows.append(("Property tax 10% higher", analyse(
        p, tax_rate=((p["tax_rate_pct"] / 100.0) if p.get("tax_rate_pct") else A["tax_std"]) * 1.10)))
    rows.append(("Insurance 20% higher", analyse(p, ins_pct=A["ins_pct"] * 1.20)))
    rows.append(("All of the above combined", analyse(
        p, rent=p["rent_realistic"] * 0.9, vacancy=0.10, maint_pct=0.015,
        tax_rate=((p["tax_rate_pct"] / 100.0) if p.get("tax_rate_pct") else A["tax_std"]) * 1.10,
        ins_pct=A["ins_pct"] * 1.20)))
    return rows


# ----------------------------------------------------------------------------
# Section 6 — 21-factor scorecard
# ----------------------------------------------------------------------------
def score_property(p, m):
    """Returns list of dicts: score 1-10, basis tag, note/source."""
    S = []

    def add(score, basis, note):
        S.append(dict(score=round(clamp(score), 1), basis=basis, note=note))

    # 1 — Cash flow and returns (weight 15)
    cf = m["cf_m"]
    if cf >= 200: s = 10
    elif cf >= 0: s = 8
    elif cf >= -150: s = 4
    elif cf >= -300: s = 3
    elif cf >= -600: s = 2
    else: s = 1
    if cf < 0:
        s = min(s, 4)  # template: cannot score above 4 if rent does not cover costs
    add(s, "DERIVED",
        f"Cash flow ${cf:,.0f}/mo, cash-on-cash {m['coc']*100:.1f}%, DSCR {m['dscr']:.2f}. "
        f"Benchmark for 7 is cash flow ≥ $0, CoC ≥ 4%, DSCR ≥ 1.20. "
        f"Template rule applied: a home whose rent does not cover costs cannot score above 4.")

    # 2 — Rental demand and vacancy (weight 10)
    s = 6.0
    notes = []
    if p.get("btr_saturation"):
        s -= 2.5; notes.append("competing build-to-rent product advertised in the same town")
    sup = p.get("supply_note", "")
    if "heavy forward supply" in sup.lower() or "very heavy" in sup.lower():
        s -= 1.0; notes.append("heavy forward supply of near-identical new homes")
    srcs = p.get("rent_sources", [])
    spread = (max(x["value"] for x in srcs) - min(x["value"] for x in srcs)) / max(1, m["rent"]) if srcs else 0
    if spread > 0.30:
        s -= 1.0; notes.append(f"rent sources disagree by {spread*100:.0f}% of the underwritten rent")
    add(s, "PROVISIONAL",
        "No property manager has been engaged and no days-on-market evidence for comparable "
        "rentals has been obtained. " + ("Deductions: " + "; ".join(notes) + "." if notes else
        "No specific demand weakness identified from desk research."))

    # 3 — Price against market value (weight 7)
    bench = PSF_BENCH.get(p["city"], (None, None))
    if bench[0] and m["psf"]:
        ratio = m["psf"] / bench[0]
        s = clamp(7 + (1 - ratio) * 20)
        add(s, "PARTLY VERIFIED",
            f"${m['psf']:.0f}/sqft against a local benchmark of ${bench[0]}/sqft "
            f"({ratio*100:.0f}% of benchmark). Source: {bench[1]}. "
            "Benchmark is a market-wide average, not three matched sold comparables.")
    else:
        add(5, "PROVISIONAL",
            f"${m['psf']:.0f}/sqft. Three matched recent sold comparables could not be retrieved "
            "(HAR and Zillow block this environment). Must be run by the listing agent or an appraiser.")

    # 4 — Location and neighbourhood (weight 7)
    add(6, "PROVISIONAL",
        "Exurban commuter location. No site visit, no Street View review and no county GIS check "
        "for industrial sites, landfill, rail, power lines or highway noise has been carried out.")

    # 5 — Job opportunities (weight 7)
    s = METRO_JOBS.get(p["metro"], 5)
    add(s, "PROVISIONAL",
        f"{p['metro']} metro anchor. BLS LAUS unemployment and named large employers within "
        "30 minutes have not been pulled for this location.")

    # 6 — Schools (weight 6)
    add(5, "PROVISIONAL",
        "Zoned elementary, middle and high school ratings have not been verified. "
        "GreatSchools/Niche/state report cards must be checked for the exact attendance zone.")

    # 7 — Weather and natural hazards (weight 5)
    climate = CLIMATE.get(p["metro"], "")
    if p.get("flood_verified") and p.get("flood_zone") == "X":
        s = 7.5
        fnote = f"FEMA Zone X confirmed at the lot. {p['flood_src']}"
    elif p.get("flood_zone") == "Not mapped":
        s = 5.0
        fnote = p["flood_src"]
    elif p.get("flood_sfha") is None:
        s = 3.5
        fnote = "Special Flood Hazard Area polygons are present near this location and the exact lot has not been determined. " + p["flood_src"]
    else:
        s = 6.0
        fnote = p["flood_src"]
    if p["state"] == "LA":
        s -= 2.0
        fnote += " Louisiana Gulf coast: elevated hurricane and wind exposure."
    if p["city"] == "Angleton":
        s -= 1.0
        fnote += " Brazoria County is ~30 km from the coast; hurricane and wind exposure is material."
    add(s, "VERIFIED" if p.get("flood_verified") else "PARTLY VERIFIED",
        fnote + f" Regional climate: {climate}. First Street and NOAA hail/freeze/heat scores not pulled.")

    # 8 — Workmanship and build quality (weight 5)
    if p["construction"].startswith("Resale"):
        add(5, "PROVISIONAL",
            "Two-year-old resale, 'freshly updated'. No independent inspection, sewer scope, "
            "WDI report or CLUE claims history has been obtained.")
    else:
        add(5, "PROVISIONAL",
            "New build. No pre-drywall or final independent inspection has been carried out and "
            "no specification sheet has been reviewed.")

    # 9 — Appreciation and resale (weight 5)
    yoy = APPREC_YOY.get(p["city"])
    s = 5.0
    an = []
    if yoy is not None:
        s = clamp(5 + yoy * 0.8)
        an.append(f"home values {yoy:+.1f}% year-on-year (Zillow/Realtor.com, Oct 2026)")
    if "heavy forward supply" in p.get("supply_note", "").lower() or "very heavy" in p.get("supply_note", "").lower():
        s -= 1.5
        an.append("large unsold new-build pipeline in the same community competes directly on resale")
    if p.get("price_was"):
        s -= 0.5
        an.append(f"the builder has already cut this home from ${p['price_was']:,} to ${p['price']:,}")
    add(s, "PARTLY VERIFIED",
        ("; ".join(an) if an else "No local appreciation series retrieved.") +
        ". Benchmark for 7 is 3%+ a year over 5 years with resales selling inside 45 days.")

    # 10 — Builder goodwill and warranty (weight 4)
    b = (p.get("builder") or "").lower()
    if "not verified" in b:
        add(3, "PROVISIONAL", "The builder has not been identified, so BBB rating, warranty terms and "
                              "defect litigation history cannot be checked. This is itself a gap.")
    elif p["construction"].startswith("Resale"):
        add(5, "PROVISIONAL", "Resale — no builder warranty assumed. Any remaining structural warranty "
                              "from the 2024 build must be identified and its transferability confirmed.")
    else:
        add(6, "PROVISIONAL",
            f"{p['builder']} is a large national builder that publishes a 1-2-10 style warranty. "
            "BBB rating, Google/NewHomeSource review patterns and court records for structural-defect "
            "litigation have not been checked for this division.")

    # 11 — HOA fee and leasing rules (weight 4)
    h = p.get("hoa_month")
    if h is None:
        add(4, "UNVERIFIED",
            "No HOA fee published. Fee, leasing permission, rental cap, owner-occupancy period and "
            "transfer fees are all unknown. Benchmark for 7 is ≤$75/month with 12-month leases allowed.")
    else:
        if h <= 50: s = 8.5
        elif h <= 75: s = 7.0
        elif h <= 110: s = 5.0
        elif h <= 160: s = 3.5
        else: s = 2.5
        add(s, "PARTLY VERIFIED" if p.get("hoa_verified") else "UNVERIFIED",
            f"${h:,.2f}/month (${h*12:,.0f}/year) against a benchmark of ≤$75/month for a score of 7. "
            f"{p['hoa_src']} Leasing permission, rental caps and owner-occupancy rules remain unconfirmed.")

    # 12 — Population growth (weight 4)
    add(COUNTY_GROWTH.get(p["county"], 5), "PROVISIONAL",
        f"{p['county']} anchor. Census QuickFacts 5-year county growth has not been pulled; "
        "benchmark for 7 is 1.5%+ a year.")

    # 13 — Crime and safety (weight 4)
    add(6, "PROVISIONAL",
        "Small-town/exurban setting. CrimeGrade and local police data have not been checked "
        "against the national average.")

    # 14 — Property tax (weight 3)
    rate_pct = (p["tax_rate_pct"] if p.get("tax_rate_pct") else A["tax_std"] * 100)
    s = clamp(7 - (rate_pct - 2.2) * 3.846)
    add(s, "VERIFIED" if p.get("tax_verified") else "UNVERIFIED",
        f"Total rate {rate_pct:.2f}%. Template anchors: 2.2% scores 7, 2.98% scores about 4. "
        f"{p['tax_rate_src']}")

    # 15 — Demographics (weight 3)
    add(5, "PROVISIONAL",
        f"Benchmark is median household income ≥ 3× annual rent (≥ ${m['rent']*12*3:,.0f} here) "
        "and a renter share ≥30%. Census ACS has not been pulled for this tract.")

    # 16 — Distances to facilities (weight 3)
    add(5, "PROVISIONAL",
        "Grocery, hospital, retail and highway drive times have not been measured. "
        "All of these locations are car-dependent exurban or rural settings.")

    # 17 — Insurance cost (weight 2)
    risk = p.get("insurance_risk")
    if risk == "severe":
        add(2, "UNVERIFIED",
            "South-west Louisiana. No DP-3 quote obtained. The template's 0.6% default is almost "
            "certainly far too low here: this market has repriced sharply since the 2020 hurricanes, "
            "and wind and flood cover may be hard to place at any price. This is a material unknown.")
    elif risk == "high":
        add(3, "UNVERIFIED",
            "Louisiana. No DP-3 quote obtained; the 0.6% default is likely too low once wind "
            "and flood cover are included.")
    elif p["city"] == "Angleton":
        add(4, "UNVERIFIED",
            "Brazoria County, ~30 km from the Gulf. No DP-3 quote obtained; windstorm cover in a "
            "coastal county will push the cost above the 0.6% default.")
    else:
        add(6, "UNVERIFIED",
            "Inland Texas. The 0.6% of price per year default has been applied and is labelled an "
            "estimate; two or three broker quotes including wind and hail are still required.")

    # 18 — Community amenities (weight 2)
    if h is not None and h >= 160:
        add(7, "PROVISIONAL",
            "Large Lennar masterplan with pool, trails and parks — the amenity package is real, "
            "but it is what the high monthly assessment is paying for. No site visit.")
    elif h is not None and h <= 110:
        add(4, "PROVISIONAL", "Small community, limited amenity package for the fee. No site visit.")
    else:
        add(4, "PROVISIONAL", "Amenity package not confirmed. No site visit.")

    # 19 — Airport access (weight 2)
    name, dist = nearest(p["lat"], p["lon"], AIRPORTS)
    s = clamp(10 - max(0, dist - 25) / 10.0)
    add(s, "DERIVED",
        f"Nearest commercial airport: {name}, {dist:.0f} km straight-line. "
        "Straight-line distance, not a measured drive time.")

    # 20 — University or college (weight 1)
    uname, udist = nearest(p["lat"], p["lon"], UNIVERSITIES)
    s = clamp(10 - max(0, udist - 20) / 7.0)
    add(s, "DERIVED",
        f"Nearest campus: {uname}, {udist:.0f} km straight-line. "
        "Straight-line distance, not a measured drive time.")

    # 21 — Walk Score (weight 1)
    add(2, "PROVISIONAL",
        "Suburban and rural new-build locations score very low for walkability. "
        "The template sets this weight at 1 deliberately. WalkScore.com not queried.")

    return S


def weighted_total(scores):
    return sum(s["score"] * w / 10.0 for s, w in zip(scores, WEIGHTS))


def verified_weight(scores):
    """Share of the 100 points resting on verified or derived inputs."""
    good = {"VERIFIED", "DERIVED", "PARTLY VERIFIED"}
    return sum(w for s, w in zip(scores, WEIGHTS) if s["basis"] in good)


# ----------------------------------------------------------------------------
# Section 7 — red flags
# ----------------------------------------------------------------------------
def red_flags(p, m):
    out = []
    if p.get("hoa_month") is None or not p.get("hoa_verified"):
        out.append(dict(sev="blocking", flag="HOA leasing rules unconfirmed",
                        detail="The declaration, resale certificate and written confirmation that "
                               "12-month leases are permitted with no rental cap, owner-occupancy "
                               "period or registration fee have not been obtained. The template "
                               "treats this as blocking until resolved."))
    else:
        out.append(dict(sev="blocking", flag="HOA leasing rules unconfirmed",
                        detail="The monthly fee is known but leasing permission, rental caps and "
                               "owner-occupancy periods are not. Must be confirmed in writing "
                               "before the option period ends."))
    if p.get("flood_sfha") is None and p.get("flood_zone") not in ("X",):
        out.append(dict(sev="blocking", flag="Possible Special Flood Hazard Area",
                        detail=f"FEMA shows {p['flood_zone']} polygons at or near this location and no "
                               f"exact-lot determination has been made. {p['flood_src']}"))
    if m["cf_m"] < -300:
        out.append(dict(sev="red", flag="Cash flow worse than −$300 a month",
                        detail=f"Cash flow is ${m['cf_m']:,.0f}/month at the realistic rent. "
                               f"Break-even needs rent of ${m['be_rent']:,.0f} (a "
                               f"{(m['be_rent']/m['rent']-1)*100:.0f}% increase) or a purchase price of "
                               f"${m['max_price']:,.0f} (a {(1-m['max_price']/m['price'])*100:.0f}% discount). "
                               "There is no realistic path to break-even within 3 years at this rent."))
    if p.get("btr_saturation"):
        out.append(dict(sev="red", flag="Build-to-rent competition in the same town",
                        detail=p.get("supply_note", "")))
    if p.get("insurance_risk") in ("high", "severe"):
        out.append(dict(sev="red", flag="Landlord wind and flood cover may be unaffordable",
                        detail="Gulf-coast Louisiana. Affordable landlord wind and flood cover has not "
                               "been demonstrated; the template treats the absence of affordable cover "
                               "as a red flag in its own right."))
    if p.get("excluded_from_ranking"):
        out.append(dict(sev="blocking", flag="Not a purchasable, priced listing",
                        detail=p.get("exclusion_reason", "")))
    if p["construction"].startswith("Resale"):
        out.append(dict(sev="amber", flag="Resale condition unverified",
                        detail="Full inspection, sewer scope, WDI (termite) report, roof/HVAC/water-heater "
                               "ages, Seller's Disclosure and a CLUE claims report are all outstanding."))
    if "not verified" in (p.get("builder") or "").lower():
        out.append(dict(sev="amber", flag="Builder not identified",
                        detail="Without the builder's name, warranty terms, BBB record and "
                               "structural-defect litigation history cannot be checked."))
    if p.get("beds_conflict"):
        out.append(dict(sev="amber", flag="Specification conflict between sources",
                        detail=p["beds_conflict"]))
    return out


# ----------------------------------------------------------------------------
# Section 10 — recommendation
# ----------------------------------------------------------------------------
def recommend(p, m, total, flags):
    blocking = [f for f in flags if f["sev"] == "blocking"]
    if p.get("excluded_from_ranking"):
        return ("Cannot be assessed", "grey",
                p.get("exclusion_reason", "") + " Select a specific homesite and re-run this analysis.")
    disc = (1 - m["max_price"] / m["price"]) * 100 if m["price"] else 0
    if total >= 80: band = "Strong buy candidate"
    elif total >= 70: band = "Buy candidate — negotiate price, rate buydown or closing credit"
    elif total >= 55: band = "Conditional — proceed only if negotiation closes the cash-flow gap"
    else: band = "Pass"
    if m["cf_m"] < 0:
        verdict = f"Buy only at or below ${m['max_price']:,.0f}"
        colour = "red" if total < 55 else "amber"
        detail = (f"At the list price of ${m['price']:,.0f} this home loses ${-m['cf_m']:,.0f} a month. "
                  f"It reaches break-even only at ${m['max_price']:,.0f} — a {disc:.0f}% discount — or "
                  f"with rent of ${m['be_rent']:,.0f}, which is {(m['be_rent']/m['rent']-1)*100:.0f}% "
                  f"above the evidenced market rent. Score {total:.1f}/100: {band}.")
    else:
        verdict = band
        colour = "green" if total >= 70 else "amber"
        detail = (f"Cash flow is positive at ${m['cf_m']:,.0f} a month with DSCR {m['dscr']:.2f}. "
                  f"Score {total:.1f}/100.")
    if blocking:
        detail += (f" {len(blocking)} blocking item(s) must be resolved first: " +
                   "; ".join(f["flag"] for f in blocking) + ".")
    return (verdict, colour, detail)


# ----------------------------------------------------------------------------
def build():
    data = json.load(open(os.path.join(HERE, "data", "properties.json")))
    results = []
    for p in data["properties"]:
        m = analyse(p)
        sc = score_property(p, m)
        total = weighted_total(sc)
        vw = verified_weight(sc)
        flags = red_flags(p, m)
        verdict, colour, detail = recommend(p, m, total, flags)
        results.append(dict(
            p=p, m=m, scores=sc, total=total, verified_weight=vw, flags=flags,
            verdict=verdict, colour=colour, detail=detail,
            sens=sensitivity(p), stress=stress(p),
            airport=nearest(p["lat"], p["lon"], AIRPORTS),
            university=nearest(p["lat"], p["lon"], UNIVERSITIES),
        ))
    return data, results


if __name__ == "__main__":
    data, res = build()
    res_sorted = sorted(res, key=lambda r: (r["p"].get("excluded_from_ranking", False), -r["total"]))
    print(f"{'ID':4} {'Address':34} {'Price':>9} {'Rent':>6} {'CF/mo':>8} {'DSCR':>5} "
          f"{'Cap':>6} {'CoC':>7} {'MaxPx':>9} {'Score':>6} {'Vw%':>4}  Verdict")
    print("-" * 150)
    for r in res_sorted:
        p, m = r["p"], r["m"]
        print(f"{p['id']:4} {(p['address']+', '+p['city'])[:34]:34} {m['price']:>9,.0f} "
              f"{m['rent']:>6,.0f} {m['cf_m']:>8,.0f} {m['dscr']:>5.2f} {m['cap']*100:>5.2f}% "
              f"{m['coc']*100:>6.1f}% {m['max_price']:>9,.0f} {r['total']:>6.1f} {r['verified_weight']:>4.0f}  {r['verdict']}")
