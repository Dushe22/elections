#!/usr/bin/env python3
"""Recopila titulares sobre las elecciones de medios de EE.UU. (RSS) y escribe news.json."""
import json, re, datetime, urllib.request, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

FEEDS = [
    ("NYT", "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml"),
    ("Washington Post", "https://feeds.washingtonpost.com/rss/politics"),
    ("CNN", "http://rss.cnn.com/rss/cnn_allpolitics.rss"),
    ("Fox News", "https://moxie.foxnews.com/google-publisher/politics.xml"),
    ("NPR", "https://feeds.npr.org/1014/rss.xml"),
    ("Politico", "https://rss.politico.com/politics-news.xml"),
    ("CBS News", "https://www.cbsnews.com/latest/rss/politics"),
    ("ABC News", "https://abcnews.go.com/abcnews/politicsheadlines"),
    ("NBC News", "https://feeds.nbcnews.com/nbcnews/public/politics"),
    ("The Hill", "https://thehill.com/homenews/campaign/feed/"),
    ("Axios", "https://api.axios.com/feed/"),
    ("Google News", "https://news.google.com/rss/search?q=midterm+elections+2026+when:2d&hl=en-US&gl=US&ceid=US:en"),
]
KEEP = re.compile(r"\b(midterms?|elections?|electoral|ballots?|voters?|voting|vote[sd]?|polls?|polling|campaign|candidates?|"
                  r"senate (race|seat|control|majority)|house (race|control|majority)|governor'?s? race|gubernatorial|"
                  r"early vote|turnout|swing (state|district)|battleground|recount|concede[sd]?|projected|race call)\b", re.I)

def text(el, *names):
    for n in names:
        x = el.find(n)
        if x is not None:
            return (x.text or x.get("href") or "").strip()
    return ""

def parse_date(s):
    if not s:
        return None
    try:
        return parsedate_to_datetime(s).astimezone(datetime.timezone.utc)
    except Exception:
        try:
            return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(datetime.timezone.utc)
        except Exception:
            return None

def fetch(src, url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (elections dashboard; RSS reader)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        root = ET.fromstring(r.read())
    atom = "{http://www.w3.org/2005/Atom}"
    nodes = root.findall(".//item") or root.findall(f".//{atom}entry")
    out = []
    for it in nodes:
        title = text(it, "title", f"{atom}title")
        link = text(it, "link", f"{atom}link")
        if not link:
            l = it.find(f"{atom}link")
            link = l.get("href") if l is not None else ""
        desc = re.sub("<[^>]+>", " ", text(it, "description", f"{atom}summary"))
        date = parse_date(text(it, "pubDate", f"{atom}updated", f"{atom}published"))
        name = src
        if src == "Google News":  # "Titular - Medio"
            m = re.match(r"(.*) - ([^-]+)$", title)
            if m:
                title, name = m.group(1).strip(), m.group(2).strip()
        if title and link and KEEP.search(title + " " + desc):
            out.append({"src": name, "title": title, "link": link,
                        "date": date.isoformat() if date else None})
    return out

def main():
    items, status = [], {}
    for src, url in FEEDS:
        try:
            got = fetch(src, url)
            items += got
            status[src] = len(got)
        except Exception as e:
            status[src] = "error: " + str(e)[:80]
    seen, uniq = set(), []
    for i in sorted(items, key=lambda x: x["date"] or "", reverse=True):
        k = re.sub(r"\W+", "", i["title"].lower())[:70]
        if k not in seen:
            seen.add(k)
            uniq.append(i)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with open("news.json", "w") as f:
        json.dump({"updated": now, "status": status, "items": uniq[:120]}, f, ensure_ascii=False)
    print(json.dumps(status, indent=1))

if __name__ == "__main__":
    main()
