#!/usr/bin/env python3
"""Descarga cotizaciones públicas de Kalshi (Senado, gobernadores, control) y escribe kalshi.json.
API pública de datos de mercado, sin clave. Si un evento no existe se omite."""
import json, re, time, datetime, urllib.request

BASES = ["https://api.elections.kalshi.com/trade-api/v2", "https://external-api.kalshi.com/trade-api/v2"]
EVENTS = ["CONTROLS-2026", "CONTROLH-2026", "SENATEAL-26", "SENATEAK-26", "SENATEAR-26", "SENATECO-26", "SENATEDE-26", "SENATEFLS-26", "SENATEGA-26", "SENATEID-26", "SENATEIL-26", "SENATEIA-26", "SENATEKS-26", "SENATEKY-26", "SENATELA-26", "SENATEME-26", "SENATEMA-26", "SENATEMI-26", "SENATEMN-26", "SENATEMS-26", "SENATEMT-26", "SENATENE-26", "SENATENH-26", "SENATENJ-26", "SENATENM-26", "SENATENC-26", "SENATEOHS-26", "SENATEOK-26", "SENATEOR-26", "SENATERI-26", "SENATESC-26", "SENATESD-26", "SENATETN-26", "SENATETX-26", "SENATEVA-26", "SENATEWV-26", "SENATEWY-26", "GOVPARTYOR-26", "GOVPARTYNV-26", "GOVPARTYGA-26", "GOVPARTYOH-26", "GOVPARTYWI-26", "GOVPARTYTX-26", "GOVPARTYKS-26", "GOVPARTYVT-26", "GOVPARTYFL-26", "GOVPARTYAK-26", "GOVPARTYNM-26", "GOVPARTYMI-26", "GOVPARTYAZ-26", "GOVPARTYIA-26", "GOVPARTYNE-26", "GOVPARTYME-26", "GOVPARTYOK-26", "GOVPARTYNH-26", "GOVPARTYTN-26", "GOVPARTYMN-26", "GOVPARTYSC-26", "GOVPARTYAL-26", "GOVPARTYNY-26", "GOVPARTYRI-26", "GOVPARTYCT-26", "GOVPARTYSD-26", "GOVPARTYIL-26", "GOVPARTYID-26", "GOVPARTYAR-26", "GOVPARTYCO-26", "GOVPARTYCA-26", "GOVPARTYPA-26", "GOVPARTYMA-26", "GOVPARTYMD-26", "GOVPARTYHI-26", "GOVPARTYWY-26"]
SLUG = {"CONTROLS-2026": "controls/senate-winner/controls-2026", "CONTROLH-2026": "controlh/house-winner/controlh-2026"}

def get(path):
    last = None
    for b in BASES:
        try:
            req = urllib.request.Request(b + path, headers={"Accept": "application/json", "User-Agent": "elections-dashboard"})
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.load(r)
        except Exception as e:
            last = e
    raise last

def num(m, *keys):
    for k in keys:
        v = m.get(k)
        if v in (None, ""):
            continue
        try:
            v = float(v)
        except ValueError:
            continue
        return v / 100 if not k.endswith("_dollars") and v > 1 else v
    return None

def party(m):
    t = (m.get("ticker") or "").upper()
    s = " ".join(str(m.get(k) or "") for k in ("yes_sub_title", "subtitle", "title")).lower()
    if re.search(r"-D$|-DEM", t) or "democrat" in s: return "D"
    if re.search(r"-R$|-REP|-GOP", t) or "republican" in s: return "R"
    if re.search(r"-I$|-IND", t) or "independent" in s: return "I"
    return None

def main():
    out, status = {}, {}
    for ev in EVENTS:
        try:
            j = get(f"/events/{ev}?with_nested_markets=true")
            mk = j.get("markets") or (j.get("event") or {}).get("markets") or []
            if not mk:
                mk = get(f"/markets?event_ticker={ev}&limit=50").get("markets", [])
            ms = []
            for m in mk:
                p = party(m)
                bid, ask = num(m, "yes_bid_dollars", "yes_bid"), num(m, "yes_ask_dollars", "yes_ask")
                last = num(m, "last_price_dollars", "last_price")
                price = (bid + ask) / 2 if bid is not None and ask is not None and ask > 0 else last
                if p and price is not None:
                    ms.append({"party": p, "p": round(price, 3), "ticker": m.get("ticker"), "vol": m.get("volume") or m.get("volume_fp")})
            series = ev.split("-")[0].lower()
            out[ev] = {"url": "https://kalshi.com/markets/" + SLUG.get(ev, f"{series}/-/{ev.lower()}"), "markets": ms}
            status[ev] = len(ms)
        except Exception as e:
            status[ev] = "error: " + str(e)[:60]
        time.sleep(0.15)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with open("kalshi.json", "w") as f:
        json.dump({"updated": now, "status": status, "events": out}, f)
    print(json.dumps(status, indent=1))

if __name__ == "__main__":
    main()
