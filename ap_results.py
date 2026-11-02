#!/usr/bin/env python3
"""Baja resultados de la AP Elections API y escribe results.json (lo lee index.html).

SIN PROBAR: escrito sin clave ni acceso a la API. Contrasta los nombres de campos con una
respuesta real (developer.ap.org/ap-elections-api) y prueba antes del martes con
AP_API_KEY=... python3 ap_results.py && head results.json
"""
import json, os, sys, urllib.request, datetime

KEY = os.environ.get("AP_API_KEY")
DATE = "2026-11-03"
BASE = "https://api.ap.org/v3/elections/" + DATE

def get(office):
    url = f"{BASE}?officeID={office}&format=json"
    req = urllib.request.Request(url, headers={"x-api-key": KEY})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def main():
    if not KEY:
        sys.exit("Falta AP_API_KEY")
    out = []
    for kind in ("S", "G"):
        for race in get(kind).get("races", []):
            for ru in race.get("reportingUnits", []):
                if ru.get("level") != "state":
                    continue
                v = {"Dem": 0, "GOP": 0, "other": 0}
                called = ""
                for c in ru.get("candidates", []):
                    p = c.get("party")
                    v[p if p in v else "other"] += c.get("voteCount", 0)
                    if c.get("winner") == "X":
                        called = {"Dem": "D", "GOP": "R"}.get(p, "I")
                pct = ru.get("precinctsReportingPct") or (100 if called else 0)
                # "D" = candidato de la izquierda de la tabla (si es independiente, ver NOTA en README)
                out.append({"id": f"{kind}-{ru.get('statePostal')}", "counted": round(pct, 1),
                            "D": v["Dem"], "R": v["GOP"], "I": v["other"], "called": called})
    doc = {"updated": datetime.datetime.now(datetime.timezone.utc).isoformat(), "races": out}
    with open("results.json", "w") as f:
        json.dump(doc, f)
    print(len(out), "carreras")

if __name__ == "__main__":
    main()
