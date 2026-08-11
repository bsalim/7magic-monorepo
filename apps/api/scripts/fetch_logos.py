"""Fetch hotel partner logos from Wikimedia Commons.

Commons is used deliberately over logo-aggregator sites: every file carries
machine-readable licence metadata, so we can record provenance per logo instead
of hoping a scraped PNG was legitimate.

Writes: raw/<slug>.png plus sources.json (title, licence, artist, file page).
"""

import json
import os
import re
import urllib.parse
import urllib.request

UA = "7magic-partner-logos/1.0 (https://7magicwedding.com; hello@7magic.id)"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logos")
RAW = os.path.join(OUT, "raw")

# (slug, display name, Commons query, must-match tokens in the filename)
BRANDS = [
    ("ritz-carlton", "The Ritz-Carlton", "Ritz-Carlton logo", ["ritz"]),
    ("jw-marriott", "JW Marriott", "JW Marriott logo hotel", ["marriott"]),
    ("aloft", "Aloft Hotels", "Aloft Hotels logo", ["aloft"]),
    ("westin", "The Westin", "Westin Hotels logo", ["westin"]),
    ("kempinski", "Kempinski", "Kempinski Hotels Resorts Logo", ["kempinski"]),
    ("grand-hyatt", "Grand Hyatt", "Grand Hyatt logo", ["hyatt"]),
    ("st-regis", "St. Regis", "St. Regis Hotels Resorts logo", ["regis"]),
    ("pullman", "Pullman", "Pullman hotel logo 2013", ["pullman"]),
    ("tentrem", "Hotel Tentrem", "Hotel Tentrem Yogyakarta logo", ["tentrem"]),
    ("vivere", "Vivere Hotel", "Vivere Hotel logo", ["vivere"]),
    ("shangri-la", "Shangri-La", "Shangri-La Hotels and Resorts logo", ["shangri"]),
    ("conrad", "Conrad", "Conrad Hotels Resorts logo", ["conrad"]),
    ("four-points", "Four Points by Sheraton", "Four Points by Sheraton logo", ["four", "point"]),
    ("mercure", "Mercure", "Mercure Hotels Logo", ["mercure"]),
    ("grand-mercure", "Grand Mercure", "Grand Mercure logo", ["mercure"]),
    ("novotel", "Novotel", "Novotel logo", ["novotel"]),
    ("artotel", "Artotel", "Artotel Group logo Indonesia", ["artotel"]),
    ("ibis-styles", "ibis Styles", "ibis Styles logo", ["ibis"]),
    ("js-luwansa", "JS Luwansa", "JS Luwansa Hotel Jakarta logo", ["luwansa"]),
    ("lumire", "Lumire Hotel", "Lumire Hotel Jakarta logo", ["lumire"]),
    ("vertu", "Vertu Hotel", "Vertu Harmoni Jakarta hotel logo", ["vertu"]),
    ("harris", "HARRIS Hotels", "Harris Hotels Indonesia logo", ["harris"]),
    ("ascott", "Ascott", "Ascott Limited logo", ["ascott"]),
    ("visesa-ubud", "Visesa Ubud", "Visesa Ubud resort logo", ["visesa"]),
    ("titik-dua-ubud", "Titik Dua Ubud", "Titik Dua Ubud hotel logo", ["titik"]),
    ("oberoi-bali", "The Oberoi", "Oberoi Hotels Resorts logo", ["oberoi"]),
    ("hilton-bali", "Hilton", "Hilton Hotels Resorts logo", ["hilton"]),
    ("trembesi", "Trembesi", "Trembesi hotel Indonesia logo", ["trembesi"]),
    ("atria", "Atria Hotel", "Atria Hotel Indonesia logo", ["atria"]),
]


def api(params):
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return json.load(urllib.request.urlopen(req, timeout=30))


def score(title, tokens):
    """Prefer a clean brand wordmark over a photo of a building or a sub-property."""
    t = title.lower()
    if not all(tok in t for tok in tokens):
        return -1
    s = 0
    if "logo" in t:
        s += 10
    if t.endswith(".svg"):
        s += 6  # vector renders cleanly at any size
    if t.endswith(".png"):
        s += 3
    # Photographs of signage / buildings, not the mark itself.
    for bad in ("hotel ", "building", "night", "exterior", "tower", "sign", "boxes",
                "label", ".jpg", "jpeg", "street", "view", "entrance"):
        if bad in t:
            s -= 5
    return s


def find(brand):
    slug, name, query, tokens = brand
    try:
        d = api({
            "action": "query", "format": "json", "generator": "search",
            "gsrsearch": f"{query} filetype:bitmap|drawing", "gsrnamespace": "6",
            "gsrlimit": "12", "prop": "imageinfo",
            "iiprop": "url|mime|extmetadata", "iiurlwidth": "800",
        })
    except Exception as e:
        return None, f"search failed: {e}"

    pages = (d.get("query", {}).get("pages") or {}).values()
    best, best_s = None, 0
    for p in pages:
        title = p["title"][5:]
        s = score(title, tokens)
        if s > best_s:
            ii = (p.get("imageinfo") or [{}])[0]
            meta = ii.get("extmetadata", {})
            best, best_s = {
                "title": title,
                "thumb": ii.get("thumburl") or ii.get("url"),
                "mime": ii.get("mime"),
                "licence": (meta.get("LicenseShortName") or {}).get("value", "?"),
                "artist": re.sub("<[^>]+>", "", (meta.get("Artist") or {}).get("value", "") or ""),
                "page": ii.get("descriptionurl"),
                "score": s,
            }, s
    if not best:
        return None, "no confident match on Commons"
    return best, None


def main():
    os.makedirs(RAW, exist_ok=True)
    sources, missing = {}, []
    for brand in BRANDS:
        slug, name = brand[0], brand[1]
        hit, err = find(brand)
        if not hit:
            missing.append((slug, name, err))
            print(f"MISS  {slug:16s} {err}")
            continue
        try:
            req = urllib.request.Request(hit["thumb"], headers={"User-Agent": UA})
            data = urllib.request.urlopen(req, timeout=45).read()
            with open(os.path.join(RAW, f"{slug}.png"), "wb") as f:
                f.write(data)
            hit["name"] = name
            sources[slug] = hit
            print(f"OK    {slug:16s} {hit['title'][:52]:54s} {hit['licence']}")
        except Exception as e:
            missing.append((slug, name, f"download failed: {e}"))
            print(f"FAIL  {slug:16s} {e}")

    with open(os.path.join(OUT, "sources.json"), "w") as f:
        json.dump({"found": sources, "missing": missing}, f, indent=2, ensure_ascii=False)
    print(f"\n{len(sources)} downloaded, {len(missing)} missing")


if __name__ == "__main__":
    main()
