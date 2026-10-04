#!/usr/bin/env python3
"""
Builds the two deliverables required by section 11 of the master template:
  1. index.html  — interactive artifact with a live calculator
  2. MMS-Rental-Due-Diligence.pdf — A4 portrait, "Page X of Y" on every page
"""
import json, os, html, datetime
import engine

HERE = os.path.dirname(os.path.abspath(__file__))
TODAY = "4 October 2026"

# Front-elevation image shipped in this repository, and what it actually is.
IMAGES = {
    "P1":  ("assets/elev/P1.jpg",  "IMG_3489.jpg", "render", "Builder rendering of the Holden plan, not a photograph of this house"),
    "P2":  ("assets/elev/P2.jpg",  "IMG_3490.jpg", "photo",  "Daylight photograph of the completed front elevation"),
    "P3":  ("assets/elev/P3.jpg",  "IMG_3491.jpg", "photo",  "Daylight photograph of the completed front elevation"),
    "P4":  ("assets/elev/P4.jpg",  "IMG_3492.jpg", "render", "Builder rendering of the Ruth plan, not a photograph of this house"),
    "P5":  ("assets/elev/P5.jpg",  "IMG_3493.jpg", "dusk",   "Photograph taken at dusk, not daylight"),
    "P6":  ("assets/elev/P6.jpg",  "IMG_3494.jpg", "photo",  "Daylight photograph of the completed front elevation"),
    "P7":  ("assets/elev/P7.jpg",  "IMG_3496.jpg", "render", "Builder rendering, not a photograph of this house"),
    "P8":  ("assets/elev/P8.jpg",  "IMG_3499.jpg", "render", "Builder rendering of a plan in this community"),
    "P9":  ("assets/elev/P9.jpg",  "IMG_3501.jpg", "photo",  "Daylight photograph of the completed front elevation"),
    "P10": ("assets/elev/P10.jpg", "IMG_3502.jpg", "render", "Builder rendering of the Canon plan, not a photograph of this house"),
    "P11": ("assets/elev/P11.jpg", "IMG_3504.jpg", "render", "Builder rendering of a plan in this community"),
    "P12": ("assets/elev/P12.jpg", "IMG_3505.jpg", "render", "Builder rendering of the Ruth plan, not a photograph of this house"),
}

# Contacts. Only what is actually published to this environment, with its source.
CONTACTS = {
    "P1": dict(
        agent=dict(name="Listing agent for NTREIS MLS 21337061", co="Not published to this environment",
                   email=None, phone=None,
                   how="Use the contact form on the Redfin or Zillow listing page, or call Trophy Signature Homes' Lakehaven sales office. The agent of record is named on the MLS sheet, which the brokerage will send on request."),
        builder=dict(name="Trophy Signature Homes — Lakehaven sales office", co="Trophy Signature Homes",
                     email=None, phone=None,
                     how="Trophy Signature Homes publishes a community enquiry form at trophysignaturehomes.com. The sales office address and direct line are given on the community page; neither was retrievable here."),
        hoa=dict(name="Lakehaven HOA management company", co="Not identified",
                 email=None, phone=None,
                 how="Ask the builder for the management company name, or obtain the management certificate recorded with Collin County.")),
    "P2": dict(
        agent=dict(name="Century Communities listing agent", co="Century Communities (builder lists its own inventory)",
                   email=None, phone=None,
                   how="Enquire through the lot page at centurycommunities.com/find-your-new-home/texas/houston-metro/angleton/bayou-bend/lots/010211---59352c19/"),
        builder=dict(name="Bayou Bend sales office", co="Century Communities",
                     email=None, phone=None,
                     how="Century Communities publishes a sales-office phone number and hours on the Bayou Bend community page; it was not retrievable here. Realtor.com lists the sales office as 'Visit Elm Estates or By Appt'."),
        hoa=dict(name="Bayou Bend HOA management company", co="Not identified",
                 email=None, phone=None,
                 how="Request from the builder, or obtain the management certificate recorded with Brazoria County.")),
    "P3": dict(
        agent=dict(name="Listing agent, HARMLS 87266577", co="Not published to this environment",
                   email=None, phone="281-780-4815",
                   phone_src="HAR.com listing flyer for 214 Cross Gable Ln (agent reference 'DPETERS'), retrieved 4 Oct 2026",
                   how="The email address is not published. Request it on the call, or use the HAR listing contact form."),
        builder=dict(name="DRB Homes — River Ranch sales office", co="DRB Homes",
                     email=None, phone=None,
                     how="Enquire through drbhomes.com River Ranch community page. DRB publishes an online appointment form rather than a direct office line."),
        hoa=dict(name="River Ranch HOA management company", co="Not identified",
                 email=None, phone=None,
                 how="Request from DRB Homes, or obtain the management certificate recorded with Liberty County.")),
    "P4": dict(
        agent=dict(name="Lennar New Home Consultant", co="Lennar Homes / Village Builders",
                   email=None, phone="888-671-8175",
                   phone_src="Consultant line published on lennar.com community pages, retrieved 4 Oct 2026",
                   how="Lennar does not publish individual consultant email addresses. Request the named consultant's address on the call."),
        builder=dict(name="Synova sales office", co="Lennar",
                     email=None, phone="888-671-8175",
                     phone_src="lennar.com, 4 Oct 2026",
                     address="1707 Dahlia Cove Court, Crosby, TX 77532",
                     how="Office address from the Lennar community record. Hours shown as 10:00–19:00."),
        hoa=dict(name="Synova HOA management company", co="Not identified",
                 email=None, phone=None,
                 how="Request from the Lennar consultant, or obtain the management certificate recorded with Harris County.")),
    "P5": dict(
        agent=dict(name="Listing agent, NTREIS MLS 21366281", co="Not published to this environment",
                   email=None, phone=None,
                   how="Use the Redfin or Zillow listing contact form, or request the MLS sheet from the listing brokerage."),
        builder=dict(name="Not applicable — resale", co="Seller is a private owner",
                     email=None, phone=None,
                     how="There is no builder. Direct the construction and warranty questions to the seller through the listing agent."),
        hoa=dict(name="Sugartree HOA management company", co="Not identified",
                 email=None, phone=None,
                 how="The seller must provide the resale certificate; ask the listing agent for the management company's details.")),
    "P6": dict(
        agent=dict(name="Listing agent, HARMLS 14976851", co="Not published to this environment",
                   email=None, phone="248-346-6322",
                   phone_src="HAR.com listing flyer for 5646 Shelford Birch Dr, retrieved 4 Oct 2026",
                   how="Email address not published. Request it on the call."),
        builder=dict(name="Avalon Ridge sales office", co="Builder not identified",
                     email=None, phone=None,
                     how="The builder of Avalon Ridge could not be confirmed from any source reachable here. Ask the listing agent to name the builder and provide the sales office details before anything else."),
        hoa=dict(name="Avalon Ridge HOA management company", co="Not identified",
                 email=None, phone=None,
                 how="Request from the listing agent, or obtain the management certificate recorded with Montgomery County.")),
    "P7": dict(
        agent=dict(name="Lennar New Home Consultant", co="Lennar Homes",
                   email=None, phone="888-671-8175",
                   phone_src="lennar.com, 4 Oct 2026",
                   how="Ask first whether 173 Cotton Cv is still available — it is absent from Lennar's published inventory."),
        builder=dict(name="Grand Lake sales office", co="Lennar",
                     email=None, phone="888-671-8175",
                     phone_src="lennar.com, 4 Oct 2026",
                     address="112 Combine Road, Snook, TX 77878",
                     how="Office address from the Lennar community record."),
        hoa=dict(name="Grand Lake HOA management company", co="Not identified",
                 email=None, phone=None,
                 how="Request from the Lennar consultant, or obtain the management certificate recorded with Burleson County.")),
    "P8": dict(
        agent=dict(name="D.R. Horton sales representative", co="D.R. Horton",
                   email=None, phone=None,
                   how="Enquire through drhorton.com/louisiana/lake-charles-lafayette/lafayette/stable-view. A specific homesite must be selected before any of this is meaningful."),
        builder=dict(name="Stable View sales office", co="D.R. Horton",
                     email=None, phone=None,
                     how="D.R. Horton publishes a community enquiry form; the direct office line was not retrievable here."),
        hoa=dict(name="Stable View HOA management company", co="Not identified",
                 email=None, phone=None,
                 how="Request from D.R. Horton, or obtain the recorded declaration from Lafayette Parish.")),
    "P9": dict(
        agent=dict(name="Listing agent, HARMLS 16181578", co="Not published to this environment",
                   email=None, phone="281-772-6793",
                   phone_src="HAR.com listing flyer for 6515 Little Yellow Ct, retrieved 4 Oct 2026",
                   how="Ask first whether the home is still available — it is absent from Lennar's published inventory."),
        builder=dict(name="Monarch Landing sales office", co="Lennar",
                     email=None, phone="888-671-8175",
                     phone_src="lennar.com, 4 Oct 2026",
                     address="6638 Painted Lady Dr, Needville, TX 77461",
                     how="Office address from the Lennar community record."),
        hoa=dict(name="Monarch Landing HOA management company", co="Not identified",
                 email=None, phone=None,
                 how="Request from the Lennar consultant, or obtain the management certificate recorded with Fort Bend County.")),
    "P10": dict(
        agent=dict(name="Lennar New Home Consultant", co="Lennar Homes",
                   email=None, phone="888-671-8175",
                   phone_src="lennar.com, 4 Oct 2026",
                   how="Lennar does not publish individual consultant email addresses."),
        builder=dict(name="Sila sales office", co="Lennar",
                     email=None, phone="888-671-8175",
                     phone_src="lennar.com, 4 Oct 2026",
                     address="810 Prunella Lane, Huffman, TX 77336",
                     how="Office address from the Lennar community record."),
        hoa=dict(name="Sila HOA management company", co="Not identified",
                 email=None, phone=None,
                 how="Request from the Lennar consultant, or obtain the management certificate recorded with Harris County.")),
    "P11": dict(
        agent=dict(name="Sales representative", co="D.R. Horton — but DSLD Homes also markets a 'Crest at Morganfield'",
                   email=None, phone=None,
                   how="Establish which builder owns the home you are being shown before anything else. D.R. Horton: drhorton.com/louisiana/lake-charles-lafayette/lake-charles/crest-at-morganfield. DSLD: dsldhomes.com/communities/louisiana/lake-charles/the-crest-at-morganfield."),
        builder=dict(name="Crest at Morganfield sales office", co="D.R. Horton and/or DSLD Homes",
                     email=None, phone=None,
                     how="Realtor.com gives the D.R. Horton sales office as 3106 Ravenwood Drive, Lake Charles, LA 70607, with hours Sun 12:00–18:00, Mon–Tue 10:00–18:00, Wed by appointment, Thu–Sat 10:00–18:00. No direct line was retrievable."),
        hoa=dict(name="Crest at Morganfield HOA", co="Not identified",
                 email=None, phone=None,
                 how="Request from the builder, or obtain the recorded declaration from Calcasieu Parish.")),
    "P12": dict(
        agent=dict(name="Lennar New Home Consultant", co="Lennar Homes",
                   email=None, phone="888-671-8175",
                   phone_src="lennar.com, 4 Oct 2026",
                   how="Lennar does not publish individual consultant email addresses."),
        builder=dict(name="Whitetail Run sales office", co="Lennar",
                     email=None, phone="888-671-8175",
                     phone_src="lennar.com, 4 Oct 2026",
                     address="102 Credeur Avenue, Caldwell, TX 77836",
                     how="Office address from the Lennar community record."),
        hoa=dict(name="Whitetail Run HOA management company", co="Not identified",
                 email=None, phone=None,
                 how="Request from the Lennar consultant, or obtain the management certificate recorded with Burleson County.")),
}

SIG = ("Mohsin Chowdhury\nMMS Consortium\nMobile: +1 702 582 5724\nEmail: mms221@gmail.com")
REPLY_BY = "9 October 2026"


def money(v, dp=0):
    if v is None:
        return "—"
    if v < 0:
        return f"\u2212${abs(v):,.{dp}f}"
    return f"${v:,.{dp}f}"


def pct(v, dp=1):
    if v is None:
        return "—"
    x = v * 100
    if x < 0:
        return f"\u2212{abs(x):.{dp}f}%"
    return f"{x:.{dp}f}%"


def esc(s):
    return html.escape(str(s if s is not None else ""))


# ---------------------------------------------------------------------------
# Section 9 — three emails per property, adapted to what each listing already answers
# ---------------------------------------------------------------------------
def emails_for(r):
    p, m = r["p"], r["m"]
    addr = f"{p['address']}, {p['city']}, {p['state']} {p['zip']}"
    short = p["address"]
    unavailable = p.get("excluded_from_ranking")
    community_only = "community" in p["address"].lower()

    # ---- Email 1: listing agent
    q = []
    if unavailable and not community_only:
        q.append("Status: Is this home still for sale? It no longer appears in the builder's published "
                 "inventory. If it is under contract, when does the option period end and will the seller "
                 "take a backup offer?")
    else:
        q.append("Status: Confirm the home is available and unsold, and that no backup offer is ahead of me.")
    if p.get("price_was"):
        q.append(f"Price: It is listed at {money(p['price'])}, down from {money(p['price_was'])}. "
                 f"What is the lowest price the seller will accept today, and which concessions "
                 f"(price cut, closing credit, rate buydown) can be combined?")
    else:
        q.append(f"Price: It is listed at {money(p['price'])}. What is the lowest price the seller will "
                 f"accept, and which concessions can be combined?")
    if p.get("tax_verified"):
        q.append(f"Tax: The builder publishes {p['tax_rate_pct']:.2f}%. Confirm the rate by entity, "
                 f"including any MUD or PID, and the first full-year bill with no homestead exemption.")
    else:
        q.append("Tax: Give the total tax rate by entity, including any MUD or PID, and the annual bill "
                 "with no homestead exemption. My model currently assumes 2.98% because nothing is published.")
    if p.get("hoa_month"):
        q.append(f"HOA: Confirm the assessment is {money(p['hoa_month'], 2)} a month, what it covers, "
                 f"and give me the manager's contact details and written confirmation that 12-month "
                 f"leases are allowed with no rental cap and no owner-occupancy period.")
    else:
        q.append("HOA: Give the assessment, what it covers, the manager's contact details, and written "
                 "confirmation that 12-month leases are allowed with no rental cap or owner-occupancy period.")
    if p.get("flood_verified") and p.get("flood_zone") == "X":
        q.append("Flood and insurance: I have the lot in FEMA Zone X. Confirm that, and disclose any "
                 "past flood or insurance claim. I also need a landlord DP-3 quote including wind.")
    else:
        q.append(f"Flood and insurance: FEMA shows {p['flood_zone']} at or near this lot and I have no "
                 f"exact-lot determination. Provide the flood zone for this specific lot, an elevation "
                 f"certificate, and any past flood or insurance claim.")
    if p["construction"].startswith("Resale"):
        q.append("Condition: Send the Seller's Disclosure Notice, all inspection reports and repair "
                 "receipts, the ages of roof, HVAC and water heater, the survey with a T-47 affidavit, "
                 "and any current lease and deposit.")
    else:
        q.append("Condition: Confirm the completion date, send the warranty document, and confirm my "
                 "independent inspector may inspect before closing.")
    q.append(f"Rent: My underwriting uses {money(m['rent'])} a month, from {len(p['rent_sources'])} "
             f"market sources. Name two property managers active in this community and tell me what "
             f"they are actually achieving and how long their homes sit vacant.")
    q.append("Closing: The earliest closing date, and any extension or rollover fee.")

    e1 = dict(
        to=CONTACTS[p["id"]]["agent"],
        subject=f"{short}: written answers needed before my offer (by {REPLY_BY})",
        body=(f"Dear {CONTACTS[p['id']]['agent']['name']},\n\n"
              f"I intend to buy {addr} as a long-term rental, with 20% down and financing arranged. "
              f"Before I submit an offer I need written answers to the points below by {REPLY_BY}.\n\n"
              + "\n".join(f"{i+1}. {t}" for i, t in enumerate(q)) +
              f"\n\nI will submit a written offer within 48 hours of receiving complete answers.\n\n"
              f"Regards,\n\n{SIG}"))

    # ---- Email 2: builder sales office
    qb = []
    if community_only:
        qb.append("Which specific homesites are available, at what price, with what plan, square footage "
                  "and completion date? I cannot underwrite a community — I need an address.")
    qb.append(f"Best net price: your lowest price today on {short} and the full incentive in dollars. "
              f"If I use my own lender, can the incentive be taken as a price reduction instead?")
    qb.append("Investor eligibility: written confirmation that the incentive applies to a "
              "non-owner-occupied purchase and will be stated in the contract, so it cannot be "
              "withheld at closing.")
    qb.append("Financing: your preferred lender's investor rate, points and APR for 20% down on a "
              "30-year fixed loan, with a Loan Estimate. Note that advertised buydown rates appear to "
              "be owner-occupier FHA/VA/RD products; I need the investor equivalent.")
    qb.append("Taxes: the total rate by entity (county, school district, MUD, PID) and the first "
              "full-year tax on the completed value at the non-homestead rate.")
    if p.get("appliances_included"):
        qb.append("Inclusions: confirm in writing that the refrigerator, washer, dryer, blinds, fence "
                  "and irrigation are included in this specific home, as the community marketing states.")
    else:
        qb.append("Inclusions: refrigerator, washer and dryer, blinds, fence and irrigation — included "
                  "or not? I have budgeted " + money(p["makeready"]) + " to make this rent-ready.")
    qb.append("Inspection and warranty: access for my independent inspector before closing, the warranty "
              "document with its claim process, and whether it transfers to a later buyer.")
    qb.append("Lot and flood: the plot plan or survey, the FEMA flood zone for this exact lot, an "
              "elevation certificate and the drainage plan.")
    if p.get("supply_note"):
        qb.append("Rental competition and supply: how many homes in this community are investor-owned or "
                  "listed for rent, how many remain unsold, and what future phases are planned. Please "
                  "also give me the HOA manager's contact details.")
    qb.append("Closing terms: a firm closing date, and confirmation that no rollover, extension or "
              "rate-lock fee applies if a delay is on your side.")

    e2 = dict(
        to=CONTACTS[p["id"]]["builder"],
        subject=f"{short}: investor purchase, best net terms in writing by {REPLY_BY}",
        body=(f"Dear {CONTACTS[p['id']]['builder']['name']},\n\n"
              f"I am ready to buy {addr}"
              + (f" ({p['plan']}, {p['community']})" if p.get("plan") else "")
              + f" as a long-term rental with 20% down, and I am choosing between this home and others "
                f"on net terms. My decision rests on written answers to these points by {REPLY_BY}:\n\n"
              + "\n".join(f"{i+1}. {t}" for i, t in enumerate(qb)) +
              f"\n\nWith satisfactory written terms I will sign the purchase agreement promptly.\n\n"
              f"Regards,\n\n{SIG}"))

    # ---- Email 3: HOA manager
    qh = [
        "Leasing: are 12-month leases allowed? Is there a minimum lease term, rental cap, "
        "owner-occupancy period, tenant registration, approval requirement or fee?",
        "Suite: if the home has a separate-entry suite, may it be leased on its own?",
    ]
    if p.get("hoa_month"):
        qh.append(f"Dues: confirm the current assessment — I have {money(p['hoa_month'], 2)} a month "
                  f"({money(p['hoa_month']*12)} a year) — what it covers, and any approved or proposed "
                  f"increase or special assessment.")
    else:
        qh.append("Dues: the current assessment, what it covers, and any approved or proposed increase "
                  "or special assessment. Nothing is published, so I am underwriting blind.")
    qh += [
        "Finances and disputes: the current budget, the reserve study or reserve balance, and any "
        "litigation involving the association.",
        "Tenant violations: the fine schedule, and whether the owner is notified before a tenant is fined.",
        "Closing costs: the resale certificate fee, transfer fee and any capital contribution due at closing.",
        "Documents: the declaration (CC&Rs), bylaws, rules and the current resale certificate.",
    ]
    e3 = dict(
        to=CONTACTS[p["id"]]["hoa"],
        subject=f"{short}, {p['community']}: leasing rules and assessments (reply by {REPLY_BY})",
        body=(f"Dear {CONTACTS[p['id']]['hoa']['name']},\n\n"
              f"I am buying {addr} in {p['community']} to lease it long-term. Please confirm the "
              f"following in writing by {REPLY_BY}:\n\n"
              + "\n".join(f"{i+1}. {t}" for i, t in enumerate(qh)) +
              f"\n\nA prompt reply will let me complete my purchase review.\n\n"
              f"Regards,\n\n{SIG}"))

    return [("Listing agent", e1), ("Builder sales office", e2), ("HOA manager", e3)]


DOC_CHECKLIST = [
    ("Financing", [
        "Investor (non-owner-occupied) loan quote in writing: rate, points, APR, lock period",
        "Builder's lender compared with an outside lender on total cost",
        "Lender's written acceptance of foreign-sourced funds and its source-of-funds document list",
        "Loan Estimate checked against the 3% closing-cost assumption",
    ]),
    ("Title, tax and HOA", [
        "Title commitment — easements, liens, MUD/PID notices",
        "Tax by entity on the completed, non-homestead value",
        "HOA declaration (CC&Rs), bylaws, budget, reserve study and resale certificate",
        "Leasing permission in writing — no rental cap, no owner-occupancy period",
        "Planned special assessments or fee increases",
    ]),
    ("Condition and warranty", [
        "New build: independent pre-drywall and final inspections",
        "New build: 11-month warranty inspection booked; 1-2-10 warranty and claim process",
        "Resale: full inspection, sewer scope, termite (WDI) report",
        "Resale: roof, HVAC and water-heater ages; Seller's Disclosure; CLUE claims report",
        "Both: survey or plot plan showing setbacks, easements, drainage and lot grade",
    ]),
    ("Risk and insurance", [
        "Written FEMA zone confirmation for the exact lot",
        "Elevation certificate where the lot is near a flood zone",
        "Landlord (DP-3) quotes including wind and flood, with deductibles stated",
    ]),
    ("Rental readiness", [
        "Property manager's agreement — management, leasing and renewal fees",
        "City or county rental registration rules",
        "Appliances and blinds included or budgeted",
        "Utility providers and MUD water and sewer rates",
    ]),
]


CSS = """
:root{
  --ink:#14171c; --muted:#5b6572; --line:#dfe4ea; --bg:#f6f7f9; --card:#fff;
  --red:#b3261e; --amber:#8a5a00; --green:#1b5e20; --grey:#5b6572;
  --redbg:#fdecea; --amberbg:#fff6e0; --greenbg:#e9f5ea; --greybg:#eef0f3;
  --accent:#17365d;
}
*{box-sizing:border-box}
body{margin:0;font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  color:var(--ink);background:var(--bg)}
.wrap{max-width:1180px;margin:0 auto;padding:28px 20px 80px}
h1{font-size:30px;line-height:1.2;margin:0 0 6px}
h2{font-size:21px;margin:38px 0 12px;padding-bottom:7px;border-bottom:2px solid var(--accent);color:var(--accent)}
h3{font-size:17px;margin:22px 0 8px}
h4{font-size:15px;margin:16px 0 6px}
p{margin:0 0 10px}
small,.small{font-size:12.5px;color:var(--muted)}
.lede{font-size:16.5px;color:#2b3340;max-width:88ch}
header.doc{background:var(--accent);color:#fff;padding:26px 20px;margin:-28px -20px 24px}
header.doc .wrap2{max-width:1140px;margin:0 auto}
header.doc h1{color:#fff}
header.doc .meta{color:#c6d4e8;font-size:13px;margin-top:8px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:18px 20px;margin:0 0 16px}
.callout{border-left:4px solid var(--accent);background:#fff;padding:14px 18px;margin:0 0 16px;border-radius:0 8px 8px 0;
  border-top:1px solid var(--line);border-right:1px solid var(--line);border-bottom:1px solid var(--line)}
.callout.red{border-left-color:var(--red);background:var(--redbg)}
.callout.amber{border-left-color:var(--amber);background:var(--amberbg)}
.callout.green{border-left-color:var(--green);background:var(--greenbg)}
table{width:100%;border-collapse:collapse;font-size:13.5px;background:#fff}
th,td{padding:7px 9px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{background:#eef1f5;font-weight:600;font-size:12.5px;text-transform:uppercase;letter-spacing:.3px;color:#3a4553}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
tr:hover td{background:#fafbfc}
.scroll{overflow-x:auto;border:1px solid var(--line);border-radius:10px}
table.cmp{font-size:12.5px;min-width:1150px}
table.cmp td:nth-child(2){min-width:190px}
table.cmp td:nth-child(2) small{white-space:nowrap}
table.cmp td,table.cmp th{padding:6px 8px}
table.rec{min-width:900px}
table.rec td:nth-child(1){width:170px}
table.rec td:nth-child(4){min-width:420px}
.neg{color:var(--red);font-weight:600}
.pos{color:var(--green);font-weight:600}
.pill{display:inline-block;padding:2px 9px;border-radius:999px;font-size:11.5px;font-weight:700;
  text-transform:uppercase;letter-spacing:.4px;white-space:nowrap}
.pill.red{background:var(--redbg);color:var(--red)}
.pill.amber{background:var(--amberbg);color:var(--amber)}
.pill.green{background:var(--greenbg);color:var(--green)}
.pill.grey{background:var(--greybg);color:var(--grey)}
.tag{display:inline-block;padding:1px 7px;border-radius:4px;font-size:10.5px;font-weight:700;letter-spacing:.3px}
.tag.VERIFIED{background:#e9f5ea;color:#1b5e20}
.tag.DERIVED{background:#e8eef7;color:#17365d}
.tag[class*="PARTLY"]{background:#fff6e0;color:#8a5a00}
.tag.PROVISIONAL{background:#eef0f3;color:#5b6572}
.tag.UNVERIFIED{background:#fdecea;color:#b3261e}
.grid{display:grid;gap:16px}
.g2{grid-template-columns:repeat(auto-fit,minmax(330px,1fr))}
.g3{grid-template-columns:repeat(auto-fit,minmax(230px,1fr))}
.kv{display:flex;justify-content:space-between;gap:12px;padding:4px 0;border-bottom:1px dotted var(--line);font-size:13.5px}
.kv:last-child{border-bottom:0}
.kv b{font-variant-numeric:tabular-nums;white-space:nowrap}
.photo{width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;border:1px solid var(--line);background:#eee}
.imgnote{font-size:11.5px;color:var(--muted);margin-top:5px}
.prop{background:#fff;border:1px solid var(--line);border-radius:12px;padding:0;margin:0 0 22px;overflow:hidden}
.prop > .head{padding:16px 20px;border-bottom:1px solid var(--line);background:#fbfcfd;
  display:flex;justify-content:space-between;align-items:flex-start;gap:16px;flex-wrap:wrap}
.prop > .body{padding:18px 20px}
.head h3{margin:0 0 3px;font-size:18px}
.calc{background:#f0f4f9;border:1px solid #cfdbe9;border-radius:10px;padding:14px 16px;margin:0 0 14px}
.calc .row{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}
.calc label{display:block;font-size:11.5px;font-weight:700;color:#3a4553;text-transform:uppercase;letter-spacing:.3px;margin-bottom:3px}
.calc input{width:100%;padding:6px 8px;border:1px solid #b9c7d8;border-radius:6px;font:inherit;font-size:13.5px;
  font-variant-numeric:tabular-nums;background:#fff}
.calc .out{display:grid;grid-template-columns:repeat(auto-fit,minmax(118px,1fr));gap:8px;margin-top:12px}
.calc .out div{background:#fff;border:1px solid #cfdbe9;border-radius:7px;padding:7px 9px}
.calc .out span{display:block;font-size:10.5px;color:var(--muted);text-transform:uppercase;letter-spacing:.3px}
.calc .out b{font-size:16px;font-variant-numeric:tabular-nums}
.email{border:1px solid var(--line);border-radius:9px;margin:0 0 12px;background:#fff}
.email .eh{padding:9px 13px;background:#eef1f5;border-bottom:1px solid var(--line);border-radius:8px 8px 0 0;
  display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap}
.email .eh b{font-size:13.5px}
.email pre{margin:0;padding:13px;white-space:pre-wrap;font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
button.copy{border:1px solid #b9c7d8;background:#fff;border-radius:6px;padding:4px 11px;font-size:12px;cursor:pointer;font-weight:600}
button.copy:hover{background:#f0f4f9}
button.copy.done{background:var(--greenbg);border-color:#9fc9a4;color:var(--green)}
ul.tight{margin:4px 0 10px;padding-left:20px}
ul.tight li{margin:2px 0}
.chk{list-style:none;padding-left:0;margin:4px 0 10px}
.chk li{padding-left:22px;position:relative;margin:3px 0;font-size:13.5px}
.chk li:before{content:"☐";position:absolute;left:0;font-size:15px;color:var(--accent)}
nav.toc{background:#fff;border:1px solid var(--line);border-radius:10px;padding:14px 18px;margin:0 0 22px}
nav.toc a{color:var(--accent);text-decoration:none;font-size:13.5px}
nav.toc a:hover{text-decoration:underline}
nav.toc ol{margin:6px 0 0;padding-left:20px}
.src{font-size:11.5px;color:var(--muted);font-style:italic}
.printonly{display:none}
.flagrow{display:flex;gap:10px;align-items:flex-start;padding:7px 0;border-bottom:1px dotted var(--line)}
.flagrow:last-child{border-bottom:0}
.flagrow .ftxt{flex:1}
.flagrow b{font-size:13.5px}
footer.doc{margin-top:46px;padding-top:16px;border-top:1px solid var(--line);font-size:12.5px;color:var(--muted)}
@media print{body{background:#fff}.wrap{max-width:none}}
"""

JS = """
const DATA = __DATA__;
function pi(loan,rate,years){const r=rate/12,n=years*12;
  return r===0? loan/n : loan*r*Math.pow(1+r,n)/(Math.pow(1+r,n)-1);}
function fm(v){return (v<0?"\u2212$":"$")+Math.abs(Math.round(v)).toLocaleString();}
function fp(v,d){const x=v*100,n=Math.abs(x).toFixed(d===undefined?1:d);return (x<0?"\u2212":"")+n+"%";}
function recalc(id){
  const d=DATA[id], g=k=>parseFloat(document.getElementById(id+"_"+k).value)||0;
  const price=g("price"), rent=g("rent"), taxr=g("tax")/100, ins=g("ins")/100,
        vac=g("vac")/100, maint=g("maint")/100, mgmt=g("mgmt")/100,
        hoa=g("hoa"), rate=g("rate")/100, other=g("other"), mk=g("mk");
  const down=price*0.20, loan=price-down, closing=price*0.03;
  const cash=down+closing+mk;
  const P=pi(loan,rate,30);
  const eff=rent*(1-vac);
  const tm=price*taxr/12, im=price*ins/12, mm=price*maint/12, gm=eff*mgmt;
  const opex=tm+im+mm+gm+hoa+other;
  const noi=eff-opex, cf=noi-P;
  const cap=price?noi*12/price:0, coc=cash?cf*12/cash:0, dscr=P?noi/P:0;
  const fixed=tm+im+mm+hoa+other+P;
  const beRent=fixed/((1-mgmt)*(1-vac));
  const beOcc=rent?fixed/((1-mgmt)*rent):0;
  const k=pi(1,rate,30);
  const denom=(taxr+ins+maint)/12+0.80*k;
  const maxPx=denom>0?(eff*(1-mgmt)-hoa-other)/denom:0;
  const set=(k2,v,cls)=>{const e=document.getElementById(id+"_o_"+k2); if(!e)return;
    e.textContent=v; e.className = cls||"";};
  set("cf",fm(cf),cf>=0?"pos":"neg");
  set("noi",fm(noi));
  set("pi",fm(P));
  set("cap",fp(cap,2));
  set("coc",fp(coc),cf>=0?"pos":"neg");
  set("dscr",dscr.toFixed(2),dscr>=1?"pos":"neg");
  set("cash",fm(cash));
  set("gy",fp(rent*12/price,2));
  set("rtp",fp(rent/price,3));
  set("berent",fm(beRent));
  set("beocc",fp(beOcc,0));
  set("maxpx",fm(maxPx));
  set("gap",fm(maxPx-price));
}
function copyEmail(btn,pre){
  const t=document.getElementById(pre).innerText;
  navigator.clipboard.writeText(t).then(()=>{
    const o=btn.textContent; btn.textContent="Copied"; btn.classList.add("done");
    setTimeout(()=>{btn.textContent=o;btn.classList.remove("done");},1600);
  });
}
document.addEventListener("DOMContentLoaded",()=>{
  Object.keys(DATA).forEach(id=>{
    ["price","rent","tax","ins","vac","maint","mgmt","hoa","rate","other","mk"].forEach(k=>{
      const e=document.getElementById(id+"_"+k);
      if(e) e.addEventListener("input",()=>recalc(id));
    });
    recalc(id);
  });
});
"""


# ---------------------------------------------------------------------------
def contact_block(role, c):
    bits = [f"<b>{esc(c['name'])}</b>"]
    if c.get("co"):
        bits.append(esc(c["co"]))
    if c.get("address"):
        bits.append(esc(c["address"]))
    bits.append("Email: " + (esc(c["email"]) if c.get("email")
                else "<i>not published to this environment</i>"))
    bits.append("Phone: " + (esc(c["phone"]) if c.get("phone")
                else "<i>not published to this environment</i>"))
    if c.get("phone_src"):
        bits.append(f"<span class='src'>Phone source: {esc(c['phone_src'])}</span>")
    bits.append(f"<span class='src'>How to obtain what is missing: {esc(c['how'])}</span>")
    return ("<div class='kv' style='display:block;background:#fbfcfd'>"
            + "<br>".join(bits) + "</div>")


def summary_table(res):
    rows = []
    for r in sorted(res, key=lambda x: (x["p"].get("excluded_from_ranking", False), -x["total"])):
        p, m = r["p"], r["m"]
        cf = m["cf_m"]
        ber = "—" if m["be_rate"] is None else f"{m['be_rate']*100:.2f}%"
        nflags = len([f for f in r["flags"] if f["sev"] in ("blocking", "red")])
        rows.append(f"""<tr>
<td><b>{esc(p['id'])}</b></td>
<td>{esc(p['address'])}<br><small>{esc(p['city'])}, {esc(p['state'])} {esc(p['zip'])}</small></td>
<td class="n">{money(m['price'])}</td>
<td class="n">{money(m['rent'])}</td>
<td class="n">{money(m['cash_invested'])}</td>
<td class="n {'pos' if cf>=0 else 'neg'}">{money(cf)}</td>
<td class="n">{pct(m['cap'],2)}</td>
<td class="n {'pos' if m['coc']>=0 else 'neg'}">{pct(m['coc'])}</td>
<td class="n {'pos' if m['dscr']>=1 else 'neg'}">{m['dscr']:.2f}</td>
<td class="n">{money(m['be_rent'])}</td>
<td class="n">{money(m['max_price'])}</td>
<td class="n">{ber}</td>
<td class="n">{r['total']:.1f}</td>
<td class="n">{nflags}</td>
<td><span class="pill {r['colour']}">{esc(r['verdict'])}</span></td>
</tr>""")
    return f"""<div class="scroll"><table class="cmp">
<thead><tr>
<th>ID</th><th>Property</th><th class="n">List price</th><th class="n">Realistic rent</th>
<th class="n">Cash in</th><th class="n">Cash flow /mo</th><th class="n">Cap</th>
<th class="n">Cash-on-cash</th><th class="n">DSCR</th><th class="n">Break-even rent</th>
<th class="n">Max price $0 CF</th><th class="n">Break-even rate</th><th class="n">Score</th>
<th class="n">Flags</th><th>Recommendation</th>
</tr></thead><tbody>{''.join(rows)}</tbody></table></div>"""


def summary_table_print(res):
    """Same content as summary_table, split into two narrower tables so it is
    legible on A4 portrait. Shown only in the PDF."""
    ordered = sorted(res, key=lambda x: (x["p"].get("excluded_from_ranking", False), -x["total"]))
    a, b = [], []
    for r in ordered:
        p, m = r["p"], r["m"]
        cf = m["cf_m"]
        a.append(f"""<tr><td><b>{esc(p['id'])}</b></td>
<td>{esc(p['address'])}<br><small>{esc(p['city'])}, {esc(p['state'])}</small></td>
<td class="n">{money(m['price'])}</td><td class="n">{money(m['rent'])}</td>
<td class="n">{money(m['cash_invested'])}</td>
<td class="n {'pos' if cf>=0 else 'neg'}">{money(cf)}</td>
<td class="n">{pct(m['cap'],2)}</td>
<td class="n {'pos' if m['coc']>=0 else 'neg'}">{pct(m['coc'])}</td>
<td class="n {'pos' if m['dscr']>=1 else 'neg'}">{m['dscr']:.2f}</td></tr>""")
        ber = "—" if m["be_rate"] is None else f"{m['be_rate']*100:.2f}%"
        nflags = len([f for f in r["flags"] if f["sev"] in ("blocking", "red")])
        short = r["verdict"]
        if short.startswith("Buy only at or below"):
            short = "Buy below max price"
        b.append(f"""<tr><td><b>{esc(p['id'])}</b></td>
<td>{esc(p['address'])}<br><small>{esc(p['city'])}, {esc(p['state'])}</small></td>
<td class="n">{money(m['be_rent'])}</td><td class="n">{pct(m['be_occ'],0)}</td>
<td class="n">{money(m['max_price'])}</td><td class="n">{ber}</td>
<td class="n">{r['total']:.1f}</td><td class="n">{r['verified_weight']:.0f}</td>
<td class="n">{nflags}</td><td>{esc(short)}</td></tr>""")
    return f"""<div class="printonly">
<h4>3a · Price, rent and returns</h4>
<table class="cmp2"><thead><tr><th>ID</th><th>Property</th><th class="n">List price</th>
<th class="n">Rent</th><th class="n">Cash in</th><th class="n">Cash flow /mo</th>
<th class="n">Cap</th><th class="n">Cash-on-cash</th><th class="n">DSCR</th>
</tr></thead><tbody>{''.join(a)}</tbody></table>
<h4>3b · Break-even, score and verdict</h4>
<p class="small">BE = break-even. "Ver. pts" is how many of the 100 scorecard points rest on verified or derived inputs. A dash under BE rate means no mortgage rate achieves break-even.</p>
<table class="cmp2 cmp2b"><thead><tr><th>ID</th><th>Property</th><th class="n">BE rent</th>
<th class="n">BE occ.</th><th class="n">Max price</th><th class="n">BE rate</th>
<th class="n">Score</th><th class="n">Ver. pts</th><th class="n">Flags</th><th>Verdict</th>
</tr></thead><tbody>{''.join(b)}</tbody></table></div>"""


def scorecard_table(r):
    rows = []
    for i, (name, w, s) in enumerate(zip(engine.FACTOR_NAMES, engine.WEIGHTS, r["scores"]), 1):
        wp = s["score"] * w / 10.0
        bar = int(round(s["score"]))
        rows.append(f"""<tr>
<td class="n">{i}</td><td>{esc(name)}</td><td class="n">{w}</td>
<td class="n"><b>{s['score']:.1f}</b></td><td class="n">{wp:.1f}</td>
<td><span class="tag {esc(s['basis'].split()[0])}">{esc(s['basis'])}</span></td>
<td><small>{esc(s['note'])}</small></td></tr>""")
    return f"""<div class="scroll"><table class="scorecard">
<thead><tr><th class="n">#</th><th>Factor</th><th class="n">Weight</th><th class="n">Score</th>
<th class="n">Points</th><th>Basis</th><th>Source and reasoning</th></tr></thead>
<tbody>{''.join(rows)}
<tr><th colspan="4">Weighted total</th><th class="n">{r['total']:.1f} / 100</th>
<th colspan="2">{r['verified_weight']:.0f} of 100 points rest on verified or derived inputs</th></tr>
</tbody></table></div>"""


def calculator(r):
    p, m = r["p"], r["m"]
    i = p["id"]
    tax_pct = p["tax_rate_pct"] if p.get("tax_rate_pct") else 2.98
    def fld(k, label, val, step="1"):
        return (f"<div><label for='{i}_{k}'>{esc(label)}</label>"
                f"<input id='{i}_{k}' type='number' step='{step}' value='{val}'></div>")
    def out(k, label):
        return f"<div><span>{esc(label)}</span><b id='{i}_o_{k}'>—</b></div>"
    return f"""<div class="calc">
<div class="small" style="margin-bottom:9px"><b>Editable calculator.</b> Change any input and every
metric below recalculates. Down payment is fixed at 20% and closing costs at 3% per the template.</div>
<div class="row">
{fld('price','Price ($)', int(m['price']), '500')}
{fld('rent','Monthly rent ($)', int(m['rent']), '25')}
{fld('rate','Mortgage rate (%)', 6.5, '0.05')}
{fld('tax','Property tax (%/yr)', tax_pct, '0.01')}
{fld('ins','Insurance (%/yr)', 0.6, '0.05')}
{fld('hoa','HOA ($/mo)', round(m['hoa_month'],2), '1')}
{fld('vac','Vacancy (%)', 5, '0.5')}
{fld('maint','Maintenance (%/yr)', 1, '0.1')}
{fld('mgmt','Management (% of rent)', 8, '0.5')}
{fld('mk','Make-ready ($)', int(m['makeready']), '100')}
{fld('other','Other costs ($/mo)', 0, '10')}
</div>
<div class="out">
{out('cf','Cash flow /mo')}{out('noi','NOI /mo')}{out('pi','P&I /mo')}
{out('cap','Cap rate')}{out('coc','Cash-on-cash')}{out('dscr','DSCR')}
{out('cash','Cash invested')}{out('gy','Gross yield')}{out('rtp','Rent/price /mo')}
{out('berent','Break-even rent')}{out('beocc','Break-even occupancy')}
{out('maxpx','Max price $0 CF')}{out('gap','Gap to list price')}
</div></div>"""


def stress_table(r):
    rows = []
    for label, s in r["stress"]:
        rows.append(f"""<tr><td>{esc(label)}</td>
<td class="n {'pos' if s['cf_m']>=0 else 'neg'}">{money(s['cf_m'])}</td>
<td class="n">{pct(s['cap'],2)}</td>
<td class="n">{s['dscr']:.2f}</td>
<td class="n {'pos' if s['coc']>=0 else 'neg'}">{pct(s['coc'])}</td></tr>""")
    return ("<table><thead><tr><th>Stress test</th><th class='n'>Cash flow /mo</th>"
            "<th class='n'>Cap rate</th><th class='n'>DSCR</th><th class='n'>Cash-on-cash</th>"
            f"</tr></thead><tbody>{''.join(rows)}</tbody></table>")


def sens_table(r):
    rows = []
    for s in r["sens"]:
        lab = "List price" if s["delta"] == 0 else f"{money(s['delta'])} on list"
        rows.append(f"""<tr><td>{esc(lab)}</td><td class="n">{money(s['price'])}</td>
<td class="n {'pos' if s['cf_m']>=0 else 'neg'}">{money(s['cf_m'])}</td>
<td class="n {'pos' if s['coc']>=0 else 'neg'}">{pct(s['coc'])}</td>
<td class="n">{s['dscr']:.2f}</td></tr>""")
    return ("<table><thead><tr><th>Scenario</th><th class='n'>Price</th><th class='n'>Cash flow /mo</th>"
            f"<th class='n'>Cash-on-cash</th><th class='n'>DSCR</th></tr></thead><tbody>{''.join(rows)}</tbody></table>")


def flags_block(r):
    if not r["flags"]:
        return "<p class='small'>No red flags identified from the data gathered.</p>"
    out = []
    for f in r["flags"]:
        colour = {"blocking": "red", "red": "red", "amber": "amber"}[f["sev"]]
        lab = {"blocking": "Blocking", "red": "Red flag", "amber": "Amber"}[f["sev"]]
        out.append(f"""<div class="flagrow"><span class="pill {colour}">{lab}</span>
<div class="ftxt"><b>{esc(f['flag'])}</b><br><small>{esc(f['detail'])}</small></div></div>""")
    return "".join(out)


def snapshot(r):
    p, m = r["p"], r["m"]
    img, origimg, kind, imgnote = IMAGES[p["id"]]
    ap, apd = r["airport"]
    un, und = r["university"]
    rents = "".join(
        f"<div class='kv'><span>{esc(s['src'])} <span class='src'>({esc(s['date'])})</span></span>"
        f"<b>{money(s['value'])}</b></div>" for s in p["rent_sources"])
    return f"""<div class="grid g2">
<div>
  <img class="photo" src="{esc(img)}" alt="Front elevation, {esc(p['address'])}">
  <div class="imgnote"><b>Image check:</b> {esc(imgnote)}. Source file <code>{esc(origimg)}</code> in this
  repository — a WhatsApp screenshot, not an original listing photograph. The template asks for a
  daylight photograph of the full front elevation; {'this meets that test' if kind=='photo' else 'this does not meet that test and must be replaced with a site photograph'}.</div>
</div>
<div>
  <div class="kv"><span>Listing status</span><b>{esc(p['status'])}</b></div>
  <div class="kv"><span>Builder / seller</span><b>{esc(p['builder'])}</b></div>
  <div class="kv"><span>Community / plan</span><b>{esc(p['community'])}{(' — ' + esc(p['plan'])) if p.get('plan') else ''}</b></div>
  <div class="kv"><span>Construction</span><b>{esc(p['construction'])}, {esc(p['year_built'])}</b></div>
  <div class="kv"><span>Beds / baths / garage</span><b>{esc(p['beds'])} / {esc(p['baths'])} / {esc(p['garage'])}</b></div>
  <div class="kv"><span>Living area</span><b>{p['sqft']:,} sqft</b></div>
  <div class="kv"><span>List price</span><b>{money(m['price'])}{(' (was ' + money(p['price_was']) + ')') if p.get('price_was') else ''}</b></div>
  <div class="kv"><span>Price per sqft</span><b>{money(m['psf'])}</b></div>
  <div class="kv"><span>HOA</span><b>{(money(m['hoa_month'],2) + ' /mo') if m['hoa_month'] else 'Not published'}</b></div>
  <div class="kv"><span>Total tax rate</span><b>{(f"{p['tax_rate_pct']:.2f}%" + (' (verified)' if p.get('tax_verified') else '')) if p.get('tax_rate_pct') else '2.98% assumed — not verified'}</b></div>
  <div class="kv"><span>FEMA flood zone</span><b>{esc(p['flood_zone'])}{' (verified)' if p.get('flood_verified') else ' — unresolved'}</b></div>
  <div class="kv"><span>Nearest airport</span><b>{esc(ap)}, {apd:.0f} km</b></div>
  <div class="kv"><span>Nearest campus</span><b>{esc(un)}, {und:.0f} km</b></div>
  <div class="kv"><span>Zillow link</span><b><a href="{esc(p['zillow_url'])}">zpid {esc(p['zpid'])}</a></b></div>
</div></div>

<h4>Where each figure comes from</h4>
<ul class="tight small">
<li><b>Price:</b> {esc(p['price_src'])}</li>
<li><b>Status:</b> {esc(p['status_src'])}</li>
<li><b>HOA:</b> {esc(p['hoa_src'])}</li>
<li><b>Tax:</b> {esc(p['tax_rate_src'])}</li>
<li><b>Flood:</b> {esc(p['flood_src'])}</li>
<li><b>Coordinates:</b> {p['lat']:.6f}, {p['lon']:.6f} — {esc(p['geo_precision'])}</li>
<li><b>Appliances:</b> {esc(p['appliances_note'])}</li>
{'<li><b>Specification conflict:</b> ' + esc(p['beds_conflict']) + '</li>' if p.get('beds_conflict') else ''}
</ul>

<h4>Realistic rent — section 4</h4>
{rents}
<p class="small" style="margin-top:7px"><b>Conservative {money(p['rent_conservative'])} · Underwritten {money(p['rent_realistic'])}.</b>
{esc(p['rent_basis'])}</p>
<p class="small"><b>Supply and competition:</b> {esc(p['supply_note'])}</p>
<p class="small"><b>Not done:</b> no Rent Zestimate or Rentometer report was obtainable (both block this
environment), no three-to-five matched rental comparables within 1 mile with their days-on-market were
retrieved, and no property manager has given an achievable rent. Until a manager confirms this figure in
writing, the rent above is an <b>estimate</b> and every number derived from it inherits that uncertainty.</p>"""


def property_section(r):
    p, m = r["p"], r["m"]
    ber = ("<b>not achievable at any interest rate</b> — even an interest-free 30-year loan "
           f"({money(m['zero_rate_pi'])} a month of pure principal) exceeds the "
           f"{money(m['noi_m'])} this home produces after costs"
           ) if m["be_rate"] is None else f"<b>{m['be_rate']*100:.2f}%</b>"
    ems = "".join(
        f"""<div class="email">
<div class="eh"><b>{esc(role)}</b>
<button class="copy" onclick="copyEmail(this,'{p['id']}_em{n}')">Copy email</button></div>
{contact_block(role, e['to'])}
<pre id="{p['id']}_em{n}">Subject: {esc(e['subject'])}

{esc(e['body'])}</pre></div>"""
        for n, (role, e) in enumerate(emails_for(r)))

    return f"""<div class="prop" id="{p['id']}">
<div class="head">
  <div><h3>{esc(p['id'])} · {esc(p['address'])}</h3>
  <small>{esc(p['city'])}, {esc(p['state'])} {esc(p['zip'])} · {esc(p['county'])} · {esc(p['metro'])} metro</small></div>
  <div style="text-align:right">
    <span class="pill {r['colour']}">{esc(r['verdict'])}</span><br>
    <small>Score <b>{r['total']:.1f}</b>/100 · {r['verified_weight']:.0f} pts verified or derived</small>
  </div>
</div>
<div class="body">
<div class="callout {r['colour']}"><b>Recommendation.</b> {esc(r['detail'])}</div>

<h4>Property snapshot — section 3</h4>
{snapshot(r)}

<h4>Investment analysis — section 5</h4>
{calculator(r)}
<div class="grid g2">
<div>
<div class="kv"><span>Cash invested (20% down + 3% closing + make-ready)</span><b>{money(m['cash_invested'])}</b></div>
<div class="kv"><span>Loan at 80% of price</span><b>{money(m['loan'])}</b></div>
<div class="kv"><span>Principal and interest, 6.5% / 30 years</span><b>{money(m['pi'])}</b></div>
<div class="kv"><span>Effective rent after 5% vacancy</span><b>{money(m['eff_rent'])}</b></div>
<div class="kv"><span>Property tax</span><b>{money(m['tax_m'])}</b></div>
<div class="kv"><span>Insurance (0.6% estimate)</span><b>{money(m['ins_m'])}</b></div>
<div class="kv"><span>HOA</span><b>{money(m['hoa_month'],2)}</b></div>
<div class="kv"><span>Maintenance (1% of price)</span><b>{money(m['maint_m'])}</b></div>
<div class="kv"><span>Management (8% of rent collected)</span><b>{money(m['mgmt_m'])}</b></div>
<div class="kv"><span><b>Operating costs, total</b></span><b>{money(m['opex_m'])}</b></div>
</div>
<div>
<div class="kv"><span>Net operating income, monthly</span><b>{money(m['noi_m'])}</b></div>
<div class="kv"><span>Net operating income, annual</span><b>{money(m['noi_y'])}</b></div>
<div class="kv"><span><b>Cash flow, monthly</b></span><b class="{'pos' if m['cf_m']>=0 else 'neg'}">{money(m['cf_m'])}</b></div>
<div class="kv"><span>Cash flow, annual</span><b class="{'pos' if m['cf_y']>=0 else 'neg'}">{money(m['cf_y'])}</b></div>
<div class="kv"><span>Cap rate</span><b>{pct(m['cap'],2)}</b></div>
<div class="kv"><span>Cash-on-cash return</span><b class="{'pos' if m['coc']>=0 else 'neg'}">{pct(m['coc'])}</b></div>
<div class="kv"><span>Debt service coverage (DSCR)</span><b class="{'pos' if m['dscr']>=1 else 'neg'}">{m['dscr']:.2f}</b></div>
<div class="kv"><span>Gross yield · rent-to-price monthly</span><b>{pct(m['gross_yield'],2)} · {pct(m['rent_to_price'],3)}</b></div>
<div class="kv"><span>Break-even rent · occupancy</span><b>{money(m['be_rent'])} · {pct(m['be_occ'],0)}</b></div>
<div class="kv"><span>Rent needed on the 1%-of-price rule</span><b>{money(m['rent_needed_1pct'])}</b></div>
<div class="kv"><span>Max price for $0 cash flow</span><b>{money(m['max_price'])} ({pct(1-m['max_price']/m['price'],0)} discount)</b></div>
</div></div>

<p class="small" style="margin-top:10px"><b>Break-even mortgage rate:</b> {ber}.</p>

<div class="grid g2" style="margin-top:12px">
<div><h4>Price sensitivity</h4>{sens_table(r)}</div>
<div><h4>Stress tests</h4>{stress_table(r)}</div>
</div>

<h4>Five-year view</h4>
<div class="grid g3">
<div class="card" style="margin:0"><div class="kv"><span>Cumulative cash flow, 5 years</span>
  <b class="{'pos' if m['cum_cf']>=0 else 'neg'}">{money(m['cum_cf'])}</b></div>
  <div class="kv"><span>Principal paid down</span><b>{money(m['principal_paid'])}</b></div></div>
<div class="card" style="margin:0"><div class="kv"><span>Value at 3% a year</span><b>{money(m['value5'])}</b></div>
  <div class="kv"><span>Loan balance at month 60</span><b>{money(m['balance5'])}</b></div></div>
<div class="card" style="margin:0"><div class="kv"><span>Net sale proceeds after 7% costs</span><b>{money(m['net_proceeds'])}</b></div>
  <div class="kv"><span>Annualised return on cash invested</span>
  <b class="{'pos' if (m['ann_return'] or 0)>0 else 'neg'}">{pct(m['ann_return']) if m['ann_return'] is not None else 'negative'}</b></div></div>
</div>
<p class="small">Assumes the rent, costs and 3% appreciation hold flat for five years and the home is sold
at month 60. Appreciation is an assumption, not a forecast.</p>

<h4>Scorecard — section 6</h4>
{scorecard_table(r)}

<h4>Red flags — section 7</h4>
{flags_block(r)}

<h4>Emails — section 9</h4>
<p class="small">Reply date set to {esc(REPLY_BY)}, three business days from {esc(TODAY)}. No contact
email address was published to this environment for any of the 36 parties below; each block states how to
obtain the missing detail, as the template requires. No address has been invented.</p>
{ems}
</div></div>"""


def headline(res):
    live = [r for r in res if not r["p"].get("excluded_from_ranking")]
    excl = [r for r in res if r["p"].get("excluded_from_ranking")]
    unreachable = [r for r in res if r["m"]["be_rate"] is None]
    best = max(res, key=lambda r: r["m"]["cf_m"])
    worst = min(res, key=lambda r: r["m"]["cf_m"])
    best_score = max(res, key=lambda r: r["total"])
    return f"""
<div class="callout red">
<h3 style="margin-top:0">The finding, in one paragraph</h3>
<p>Not one of the twelve listings covers its own costs as a long-term rental at the standard
assumptions. Cash flow ranges from <b>{money(worst['m']['cf_m'])}</b> to <b>{money(best['m']['cf_m'])}</b>
a month. Cap rates run {pct(min(r['m']['cap'] for r in res),2)} to {pct(max(r['m']['cap'] for r in res),2)}
against debt costing 6.5%, so every property is negatively levered. The highest score in the set is
<b>{best_score['total']:.1f} out of 100</b>, which is below the template's own pass mark of 55, so the
decision rule in section 6 returns <b>Pass</b> for all twelve.</p>
<p><b>{len(unreachable)} of the 12 cannot reach break-even at any mortgage interest rate.</b> For those
properties, net operating income after tax, insurance, HOA, vacancy, maintenance and management is less
than the principal repayment alone on an interest-free 30-year loan. A rate buydown cannot rescue them;
only a materially lower purchase price or materially higher rent can.</p>
</div>

<h3>Why the economics fail</h3>
<p class="lede">Three costs do the damage, and two of them are specific to the communities chosen.</p>
<div class="grid g3">
<div class="card"><b>Property tax</b><p class="small">Five of the twelve sit in Texas MUD districts where
the builder's own published rate is 3.00% to 3.55% of value a year — above the 2.98% the template already
treats as a score of 4 out of 10. On a $280,000 home a 3.37% rate is <b>$786 a month</b> before a single
repair.</p></div>
<div class="card"><b>HOA assessments</b><p class="small">The Lennar masterplans charge
$183.33 to $191.66 a month — $2,200 to $2,300 a year, against the template's benchmark of $75 a month
for a passing score. That is roughly 10% of gross rent going to the association.</p></div>
<div class="card"><b>Rent-to-price</b><p class="small">The template notes a home usually needs monthly rent
near 1% of price to break even. The best in this set reaches
{pct(max(r['m']['rent_to_price'] for r in res),3)} and the worst
{pct(min(r['m']['rent_to_price'] for r in res),3)}. These are $250,000–$360,000 houses in towns whose
evidenced market rents are $1,400 to $2,400.</p></div>
</div>

<h3>What is wrong with the list itself</h3>
<div class="callout amber">
<ul class="tight">
<li><b>The 14 screenshots contain 12 unique properties.</b> IMG_3503 duplicates IMG_3490
(117 Bayou Bend Ct, Angleton), and IMG_3506 is a front-elevation render with no link attached.</li>
<li><b>Two of the twelve are not homes.</b> Stable View (Lafayette, LA) and Crest at Morganfield
(Lake Charles, LA) are builder <i>community</i> pages covering price ranges of $230,500–$323,500 and
$233,500–$324,500. There is no address, lot, plan or price to underwrite. Both are shown below for
completeness using the midpoint of the advertised range, clearly marked as an estimate.</li>
<li><b>Two more appear already gone.</b> 173 Cotton Cv (Snook) and 6515 Little Yellow Ct (Needville) are
absent from their builders' current published inventories as at {TODAY}, although marketing flyers for
both still exist. Confirm status before spending anything further.</li>
<li><b>So {len(live)} of the 12 are actually live, priced, specific homes</b> that can be analysed as the
template intends.</li>
<li><b>Only 3 of the 12 images are daylight photographs of the completed front elevation.</b> Seven are
builder renderings and one was taken at dusk. Section 3 requires a daylight photograph of the full front
elevation, so eight need replacing with site photographs.</li>
<li><b>The brief is headed "14homehouston", but four of the twelve are not in the Houston market</b> —
Farmersville and Cleburne are Dallas–Fort Worth, Snook and Caldwell are Bryan–College Station, and two
are in Louisiana.</li>
</ul>
</div>

<h3>Where the data came from, and what is still missing</h3>
<p class="lede">Zillow returns HTTP 403 to this environment, as do Trulia, HAR and NewHomeSource. Listing
facts were therefore verified against the builders' own websites and Redfin, and flood zones were queried
directly from FEMA. That makes the price, specification, HOA, tax and flood data stronger than a Zillow
scrape would have been — but it leaves real gaps, and those gaps are named rather than filled with guesses.</p>
<div class="grid g2">
<div class="card"><b>Verified, with source and date</b>
<ul class="tight small">
<li>Price, plan, square footage, bed/bath count and sale status — from lennar.com,
centurycommunities.com, drhorton.com and redfin.com, all retrieved {TODAY}</li>
<li>HOA monthly fee for 6 properties — Lennar community records, cross-checked against a Redfin
listing in the same masterplan showing "$192/mo"</li>
<li>Total property tax rate for 5 properties — the builders' own published community estimates</li>
<li>FEMA flood zone for 6 properties — FEMA National Flood Hazard Layer point queries against the
exact lot coordinates, with the FIRM panel recorded</li>
<li>Airport and campus distances — great-circle distance computed from verified coordinates</li>
</ul></div>
<div class="card"><b>Not verified — and therefore not scored as fact</b>
<ul class="tight small">
<li><b>Rent.</b> No Rent Zestimate, no Rentometer report, no matched 1-mile comparables with
days-on-market, and no property manager opinion. Rents here are medians of three market-level
sources and are labelled estimates throughout.</li>
<li><b>HOA leasing rules.</b> Not one declaration, resale certificate or written leasing permission has
been seen. The template makes this a blocking red flag for all twelve.</li>
<li><b>Insurance.</b> No DP-3 quote. The 0.6% default is applied for comparability, which flatters the
two Louisiana entries and the coastal Angleton home.</li>
<li><b>Schools, crime, demographics, job data, builder BBB records, workmanship.</b> Not pulled.
These carry provisional scores, clearly tagged, and together account for most of the
{100 - int(min(r['verified_weight'] for r in res))} points that are <i>not</i> resting on verified data
in the weakest case.</li>
<li><b>Contact details.</b> No email address was published for any of the 36 parties. Four direct
phone numbers were recovered from HAR flyers and Lennar's consultant line. Nothing has been invented.</li>
</ul></div>
</div>
<p class="small"><b>Read the scores accordingly.</b> Each property shows how many of its 100 points rest on
verified or derived inputs — between {min(r['verified_weight'] for r in res):.0f} and
{max(r['verified_weight'] for r in res):.0f}. The cash-flow conclusion is robust because it depends on
price, tax, HOA and rent, which are the best-evidenced inputs. The overall scores are indicative only
until the field work in section 8 is done.</p>
"""


def recommendation_detail(res):
    rows = []
    for r in sorted(res, key=lambda x: (x["p"].get("excluded_from_ranking", False), -x["total"])):
        p, m = r["p"], r["m"]
        if p.get("excluded_from_ranking"):
            verdict_price = "n/a"
        else:
            verdict_price = money(m["max_price"])
        psf_note = ""
        if p["city"] in engine.PSF_BENCH and engine.PSF_BENCH[p["city"]][0]:
            b = engine.PSF_BENCH[p["city"]][0]
            rel = m["psf"] / b
            psf_note = (f" At {money(m['psf'])}/sqft against a local benchmark of ${b}/sqft it is "
                        f"{'below market' if rel < 0.95 else ('fair' if rel <= 1.05 else 'above market')}.")
        short = r['verdict']
        if short.startswith("Buy only at or below"):
            short = "Buy below max price"
        rows.append(f"""<tr>
<td><b>{esc(p['id'])}</b><br><small>{esc(p['address'])}, {esc(p['city'])}</small></td>
<td><span class="pill {r['colour']}">{esc(short)}</span></td>
<td class="n">{verdict_price}</td>
<td><small>{esc(r['detail'])}{psf_note}</small></td>
</tr>""")
    return ("<div class='scroll'><table class='rec'><thead><tr><th>Property</th><th>Verdict</th>"
            "<th class='n'>Max price</th><th>Reasoning</th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table></div>")


def checklist_html():
    out = []
    for group, items in DOC_CHECKLIST:
        out.append(f"<div class='card' style='margin:0'><b>{esc(group)}</b><ul class='chk'>"
                   + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul></div>")
    return "<div class='grid g2'>" + "".join(out) + "</div>"


def build_html(data, res):
    order = sorted(res, key=lambda x: (x["p"].get("excluded_from_ranking", False), -x["total"]))
    calc_data = {r["p"]["id"]: {} for r in res}
    toc = "".join(
        f"<li><a href='#{r['p']['id']}'>{esc(r['p']['id'])} — {esc(r['p']['address'])}, "
        f"{esc(r['p']['city'])}</a> <span class='pill {r['colour']}'>{esc(r['verdict'])}</span></li>"
        for r in order)
    props = "".join(property_section(r) for r in order)
    js = JS.replace("__DATA__", json.dumps(calc_data))
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rental Property Due Diligence — 12 listings — MMS Consortium</title>
<style>{CSS}</style></head><body>
<header class="doc"><div class="wrap2">
<h1>Rental Property Due Diligence</h1>
<div>12 listings assessed as long-term rentals · 20% down · 30-year loan at 6.5%</div>
<div class="meta">MMS Consortium · Master Template version 1.0 · Analysis dated {TODAY} ·
Prepared for M. Mohsin Chowdhury · All amounts in US dollars · Temperatures in °C</div>
</div></header>
<div class="wrap">

<h2>1 · Summary and recommendation</h2>
{headline(res)}

<h2>2 · Recommendation for each property</h2>
{recommendation_detail(res)}

<h2>3 · Side-by-side comparison</h2>
<p class="small">Sorted by weighted score. All figures at the standard assumptions in section 2 of the
template, using the underwritten rent from section 4. "Break-even rate" is the mortgage rate at which
cash flow would reach zero holding price and rent fixed; a dash means no rate achieves it.</p>
<div class="screenonly">{summary_table(res)}</div>
{summary_table_print(res)}

<h2>4 · Contents</h2>
<nav class="toc"><ol>{toc}</ol></nav>

<h2>5 · Property by property</h2>
{props}

<h2>6 · Documents and inspections — section 8</h2>
<p class="small">To be obtained before the option period ends and the earnest money becomes
non-refundable. None of these has been obtained for any property in this set.</p>
{checklist_html()}

<h2>7 · Method and limitations</h2>
<div class="card">
<h4>How every number was produced</h4>
<p class="small">Inputs live in <code>data/properties.json</code>, each with its source and retrieval
date. <code>engine.py</code> implements sections 5, 6, 7 and 10 of the template and
<code>generate.py</code> renders this page and the PDF. Re-running <code>python3 generate.py</code>
reproduces both deliverables exactly. The calculator on this page uses the same formulas in JavaScript,
so the figures you see when you change an input are computed the same way as the printed ones.</p>
<h4>Formulas, as specified in section 5</h4>
<ul class="tight small">
<li>Principal and interest = L · r(1+r)<sup>360</sup> ÷ [(1+r)<sup>360</sup> − 1], L = 80% of price, r = 6.5% ÷ 12</li>
<li>Effective rent = rent × (1 − vacancy); management = 8% of rent collected, i.e. of effective rent</li>
<li>NOI = effective rent − (tax + insurance + HOA + maintenance + management + other); NOI excludes the mortgage</li>
<li>Cash flow = NOI − P&amp;I · Cap rate = annual NOI ÷ price · Cash-on-cash = annual cash flow ÷ cash invested · DSCR = NOI ÷ P&amp;I</li>
<li>Break-even rent = fixed costs ÷ [(1 − management) × (1 − vacancy)]</li>
<li>Maximum price at $0 cash flow solves for price with tax, insurance, maintenance and debt all scaling with price</li>
</ul>
<h4>Limitations you should hold against this document</h4>
<ul class="tight small">
<li>Rents are market-level medians, not matched comparables, and no property manager has confirmed them.</li>
<li>Seven of 21 scored factors are provisional for every property; the per-property scorecard tags each one.</li>
<li>Insurance at 0.6% of price is a template default, not a quote, and is materially optimistic for the
two Louisiana entries and for Angleton.</li>
<li>Tax rates for 7 of 12 properties are the template's 2.98% assumption, not a verified rate. Where a
MUD or PID exists the true rate will be higher, which makes those seven look better than they are.</li>
<li>No site visit, inspection, title search or HOA document review has been carried out.</li>
<li>Flood zones for 6 of 12 rest on community or city coordinates rather than the exact lot. Four
locations have Special Flood Hazard Area polygons nearby and need a determination for the specific lot.</li>
</ul>
</div>

<footer class="doc">
Prepared by MMS Consortium, {TODAY}, applying the Rental Property Due Diligence Master Template
version 1.0. Listing facts retrieved {TODAY} from lennar.com, centurycommunities.com, drhorton.com,
redfin.com, realtor.com, trulia.com market pages, HAR listing flyers and RentCafe; flood data from the
FEMA National Flood Hazard Layer; coordinates from the US Census geocoder, OpenStreetMap Nominatim and
the builders' own records. Figures labelled as estimates are estimates. Nothing in this document is
financial, legal or tax advice.
</footer>
</div>
<script>{js}</script></body></html>"""


# ---------------------------------------------------------------------------
# PDF — A4 portrait, "Page X of Y" on every page
# ---------------------------------------------------------------------------
PRINT_CSS = """
@page {
  size: A4 portrait;
  margin: 17mm 14mm 18mm 14mm;
  @top-right { content: "MMS Consortium · Rental Property Due Diligence · 4 October 2026";
               font-size: 7.5pt; color: #6b7280; }
  @bottom-center { content: "Page " counter(page) " of " counter(pages);
                   font-size: 8pt; color: #374151; }
}
@page :first { @top-right { content: ""; } }
html { font-size: 9.2pt; }
body { background:#fff; font-family: "DejaVu Sans", sans-serif; color:#14171c; }
.wrap { max-width:none; padding:0; }
header.doc { background:#17365d; color:#fff; padding:16mm 10mm; margin:0 0 8mm;
             border-radius:0; page-break-after:always; }
header.doc h1 { font-size:26pt; color:#fff; }
h1 { font-size:22pt; }
h2 { font-size:13pt; margin:7mm 0 3mm; page-break-after:avoid; border-bottom:1.5pt solid #17365d; }
h3 { font-size:11pt; margin:5mm 0 2mm; page-break-after:avoid; }
h4 { font-size:9.6pt; margin:4mm 0 1.5mm; page-break-after:avoid; }
p, li { font-size:8.6pt; }
small, .small, .src { font-size:7.6pt; }
table { font-size:7.2pt; page-break-inside:auto; }
thead { display:table-header-group; }
tr { page-break-inside:avoid; }
th, td { padding:2.2pt 3pt; }
th { font-size:6.8pt; }
.scroll { overflow:visible; border:none; border-radius:0; }
table.cmp { min-width:0; width:100%; font-size:5.6pt; table-layout:fixed; }
table.cmp td, table.cmp th { padding:1.3pt 1.6pt; word-wrap:break-word; }
table.cmp td:nth-child(2) small { white-space:normal; }
table.cmp th:nth-child(1), table.cmp td:nth-child(1){ width:3.2%; }
table.cmp th:nth-child(2), table.cmp td:nth-child(2){ width:14%; }
table.cmp th:nth-child(15), table.cmp td:nth-child(15){ width:13%; }
table.rec { min-width:0; width:100%; font-size:6.8pt; table-layout:fixed; }
table.rec td, table.rec th { padding:1.6pt 2.4pt; word-wrap:break-word; }
table.rec th:nth-child(1), table.rec td:nth-child(1){ width:15%; }
table.rec th:nth-child(2), table.rec td:nth-child(2){ width:18%; }
table.rec th:nth-child(3), table.rec td:nth-child(3){ width:12%; }
table.rec th:nth-child(4), table.rec td:nth-child(4){ width:53%; }
table.rec tr { page-break-inside:auto; }
.printonly { display:block !important; }
.screenonly { display:none !important; }
table.cmp2 { width:100%; font-size:6.4pt; table-layout:fixed; }
table.cmp2 th, table.cmp2 td { padding:1.6pt 2pt; white-space:normal !important; word-wrap:break-word; }
table.cmp2 th:nth-child(1), table.cmp2 td:nth-child(1) { width:7%; white-space:nowrap !important; }
table.cmp2 th:nth-child(2), table.cmp2 td:nth-child(2) { width:22%; }
table.cmp2 td.n { white-space:nowrap !important; }
table.cmp2b th:nth-child(2), table.cmp2b td:nth-child(2) { width:19%; }
table.cmp2b th:nth-child(10), table.cmp2b td:nth-child(10) { width:14%; }
table.cmp2b { font-size:6.1pt; }
table.rec th, table.rec td, table.cmp th, table.cmp td { white-space:normal !important; overflow:hidden; }
table.rec th:nth-child(3), table.rec td:nth-child(3) { white-space:nowrap !important; }
table.rec .pill { display:inline; background:none !important; border:0; padding:0; font-size:6.6pt; font-weight:700; white-space:normal !important; }
.pill { white-space:normal; display:inline-block; max-width:100%; overflow-wrap:anywhere; padding:0.5pt 2pt; }
.prop { page-break-before:always; border:none; margin:0; }
.prop > .head { background:#eef1f5; border-bottom:1.5pt solid #17365d; padding:3mm 4mm; }
.prop > .body { padding:3mm 0 0; }
.calc { page-break-inside:avoid; }
.kv { padding:1.3pt 0; font-size:8.1pt; align-items:flex-start; }
.kv b { white-space:normal !important; text-align:right; max-width:62%; }
.scorecard td small { font-size:6.5pt; line-height:1.3; }
.email pre { font-size:6.9pt; line-height:1.42; }
ul.tight li, .chk li { font-size:8.1pt; }
.calc .row, .calc input { display:none; }
.calc:before { content:"The editable calculator is available in the HTML version of this report.";
               font-size:7.6pt; font-style:italic; color:#5b6572; }
.calc .out { margin-top:3mm; }
.photo { aspect-ratio:auto; height:44mm; object-fit:cover; }
.grid { display:block; }
.grid > div { margin-bottom:3mm; }
.g2 > div, .g3 > div { width:100%; }
.email { page-break-inside:avoid; }
.email pre { font-size:7.2pt; }
button.copy { display:none; }
nav.toc a { color:#17365d; }
.pill, .tag { border:0.4pt solid rgba(0,0,0,.12); }
footer.doc { page-break-before:avoid; font-size:7.4pt; }
"""


def build_pdf(html_str, out_path):
    from weasyprint import HTML, CSS as WCSS
    HTML(string=html_str, base_url=HERE).write_pdf(
        out_path, stylesheets=[WCSS(string=PRINT_CSS)],
        optimize_images=True, jpeg_quality=70, dpi=150, full_fonts=False)


if __name__ == "__main__":
    data, res = engine.build()
    page = build_html(data, res)
    out_html = os.path.join(HERE, "index.html")
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"wrote {out_html} ({len(page):,} bytes)")
    pdf = os.path.join(HERE, "MMS-Rental-Due-Diligence.pdf")
    build_pdf(page, pdf)
    print(f"wrote {pdf} ({os.path.getsize(pdf):,} bytes)")
