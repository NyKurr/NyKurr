"""Dependency-free, public-only GitHub profile instrument."""
import argparse
from datetime import date, datetime, timedelta, timezone
from html import escape
import json
import math
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REPO = "NyKurr/NyKurEdge"
API = "https://api.github.com"


def get_json(path):
    # Deliberately unauthenticated: private account data cannot enter this pipeline.
    request = Request(API + path, headers={"Accept": "application/vnd.github+json",
                                          "User-Agent": "NyKurr-public-profile"})
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def snapshot(today=None, fetch=get_json):
    today = today or datetime.now(timezone.utc).date()
    start = today - timedelta(days=today.weekday() + 77)
    meta = fetch(f"/repos/{REPO}")
    if meta.get("private") is not False or meta.get("full_name") != REPO:
        raise ValueError("Selected repository must be explicitly public")
    counts = [0] * 12
    seen = set()
    for page in range(1, 21):
        commits = fetch(f"/repos/{REPO}/commits?since={start}T00:00:00Z&per_page=100&page={page}")
        if not isinstance(commits, list):
            raise ValueError("Invalid commit response")
        for commit in commits:
            if commit["sha"] in seen:
                continue
            seen.add(commit["sha"])
            day = datetime.fromisoformat(commit["commit"]["committer"]["date"].replace("Z", "+00:00")).astimezone(timezone.utc).date()
            if start <= day <= today:
                counts[(day - start).days // 7] += 1
        if len(commits) < 100:
            break
    else:
        raise ValueError("Pagination limit reached; refusing a truncated snapshot")
    return {"repository": REPO, "as_of": str(today), "week_starts":
            [str(start + timedelta(weeks=i)) for i in range(12)], "counts": counts}


def validate(data):
    if set(data) != {"repository", "as_of", "week_starts", "counts"} or data["repository"] != REPO:
        raise ValueError("Unexpected snapshot fields")
    day = date.fromisoformat(data["as_of"])
    start = day - timedelta(days=day.weekday() + 77)
    if data["week_starts"] != [str(start + timedelta(weeks=i)) for i in range(12)]:
        raise ValueError("Invalid week boundaries")
    if len(data["counts"]) != 12 or any(type(n) is not int or n < 0 for n in data["counts"]):
        raise ValueError("Invalid counts")


def svg_open(height, title, desc):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="{height}" viewBox="0 0 960 {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>
<style>text{{font-family:Consolas,'Liberation Mono',monospace}} .quiet{{fill:#9bac9f}} .bright{{fill:#a3ff70}}</style>
<rect width="960" height="{height}" rx="12" fill="#080e0c"/>
<rect x=".5" y=".5" width="959" height="{height-1}" rx="12" fill="none" stroke="#26392d"/>
'''


def identity():
    out = svg_open(440, "NyKurr / Field terminal", "Worlds to explore. Systems to use. Game development, native software, tools and automation. Original green contour artwork.")
    out += '''<defs><clipPath id="terrain"><rect x="580" y="56" width="354" height="326"/></clipPath>
<linearGradient id="fade"><stop stop-color="#51c987" stop-opacity=".12"/><stop offset="1" stop-color="#a3ff70" stop-opacity=".85"/></linearGradient></defs>
<style>@keyframes breathe{0%,100%{opacity:.65}50%{opacity:1}} .terrain{animation:breathe 12s ease-in-out infinite}@media(prefers-reduced-motion:reduce){.terrain{animation:none}}</style>
<path d="M32 56H928 M32 382H928" stroke="#26392d"/>
<circle cx="38" cy="30" r="4" fill="#a3ff70"/>
<text x="52" y="36" font-size="15" letter-spacing="3" fill="#b9cabe">NYKURR / FIELD TERMINAL</text>
<text x="928" y="36" text-anchor="end" font-size="13" class="quiet">PERSONAL BUILD SPACE</text>
<g class="terrain" clip-path="url(#terrain)" fill="none" stroke="url(#fade)" stroke-width="1.2">'''
    for i in range(31):
        pts = []
        for j in range(85):
            t = j / 84 * math.tau
            r = 30 + i * 6.1
            warp = 1 + .13 * math.sin(t * 3 + i * .11) + .065 * math.cos(t * 5 - i * .07)
            x = 786 + math.cos(t) * r * warp * .88
            y = 226 + math.sin(t) * r * warp * .78
            pts.append(f"{x:.1f},{y:.1f}")
        out += '<path d="M' + ' L'.join(pts) + 'Z"/>'
    out += '''</g><path d="M758 242V205L802 247V210 M817 199V253" stroke="#a3ff70" stroke-width="5" fill="none"/>
<path d="M602 86h16m-8-8v16 M902 350h16m-8-8v16" stroke="#51c987"/>
<text x="38" y="105" font-size="14" letter-spacing="3" class="bright">WORLDS / INTERFACES / SYSTEMS</text>
<text x="30" y="205" font-size="96" font-weight="700" letter-spacing="-7" fill="#edf7ef">NyKurr<tspan fill="#a3ff70">_</tspan></text>
<text x="38" y="272" font-family="sans-serif" font-size="31" fill="#edf7ef">Worlds to explore.</text>
<text x="38" y="315" font-family="sans-serif" font-size="31" fill="#edf7ef">Systems to use.</text>
<text x="38" y="355" font-size="15" class="quiet">GAME DEV · NATIVE SOFTWARE · AUTOMATION</text>
<text x="38" y="414" font-size="14" class="quiet">01 / EXPLORE THE WORK BELOW</text>
<text x="922" y="414" text-anchor="end" font-size="14" class="bright">SOURCE IS THE SIGNAL ↘</text></svg>'''
    return out


def signal(data):
    validate(data)
    counts = data["counts"]
    total = sum(counts)
    out = svg_open(300, "NyKurEdge / public signal history", f"Snapshot {data['as_of']}. {total} commits across twelve UTC weeks, all authors. Weekly counts: {', '.join(map(str, counts))}.")
    out += f'''<text x="32" y="38" font-size="16" letter-spacing="2" class="bright">PUBLIC SIGNAL / NyKurEdge</text>
<text x="928" y="38" text-anchor="end" font-size="14" class="quiet">12 WEEKS · UTC</text>
<path d="M32 58H928" stroke="#26392d"/>
<text x="32" y="127" font-size="54" fill="#edf7ef">{total:02d}</text>
<text x="34" y="156" font-size="14" class="quiet">COMMITS</text>
<text x="34" y="180" font-size="13" class="quiet">ALL AUTHORS</text>
<path d="M192 82V218" stroke="#26392d"/>
'''
    for y in (110, 155, 200):
        out += f'<path d="M222 {y}H926" stroke="#17271d"/>'
    peak = max(max(counts), 1)
    for i, n in enumerate(counts):
        x = 230 + i * 58
        h = max(3, n / peak * 104)
        out += f'<rect x="{x}" y="{210-h}" width="34" height="{h}" rx="3" fill="{"#a3ff70" if n else "#26392d"}"/>'
        if n:
            out += f'<text x="{x+17}" y="{200-h}" text-anchor="middle" font-size="14" fill="#edf7ef">{n}</text>'
    out += f'''<text x="230" y="237" font-size="13" class="quiet">{data['week_starts'][0]}</text>
<text x="902" y="237" text-anchor="end" font-size="13" class="quiet">CURRENT WEEK*</text>
<path d="M32 254H928" stroke="#26392d"/>
<text x="32" y="281" font-size="13" class="quiet">SNAPSHOT {data['as_of']} / *PARTIAL WEEK</text>
<text x="928" y="281" text-anchor="end" font-size="13" class="bright">OPEN COMMIT HISTORY ↗</text></svg>'''
    return out


def write(data):
    validate(data)
    files = {"assets/identity.svg": identity(), "assets/signal.svg": signal(data),
             "data/signal.json": json.dumps(data, indent=2) + "\n"}
    for name, content in files.items():
        path = ROOT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cached", action="store_true")
    args = parser.parse_args()
    data = json.loads((ROOT / "data/signal.json").read_text()) if args.cached else snapshot()
    write(data)
    print("Rendered public snapshot", data["as_of"])
