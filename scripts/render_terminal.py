#!/usr/bin/env python3
"""Generate the profile terminal assets using cached GitHub activity.

Run: python scripts/render_terminal.py
Check generated files: python scripts/render_terminal.py --check
Refresh data: GITHUB_TOKEN=... python scripts/render_terminal.py --refresh
The scheduled workflow refreshes public activity every six hours. Normal renders
use the committed cache, require no network/token, and are deterministic.
"""
import argparse
import json
import os
import urllib.request
from datetime import date, datetime, timedelta, timezone
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEMES = {
    "dark": dict(bg="#10171d", bar="#19232b", border="#31404b", text="#e3eaf0", muted="#a0aeb9", green="#8bc9a2", amber="#e2bb79", blue="#8ebad9"),
    "light": dict(bg="#f8fafb", bar="#edf1f4", border="#c7d1d9", text="#243540", muted="#526674", green="#2e7049", amber="#886018", blue="#315f83"),
}
# kind, text, color, reveal time (seconds)
ROWS = [
    ("cmd", "whoami", "text", 0.15),
    ("out", "Ashton Ward / SubnetPhantom", "text", 0.8),
    ("out", "QA Engineer | Network Specialist | Homelab Builder", "muted", 0.95),
    ("cmd", "cat mission.txt", "text", 1.3),
    ("out", "Build reliable infrastructure.", "text", 2.15),
    ("out", "Automate the repeatable work.", "text", 2.3),
    ("out", "Understand what happens underneath.", "text", 2.45),
    ("cmd", "ls projects/", "text", 2.8),
    ("out", "ansible-automation/   homelab/   putler/", "blue", 3.55),
    ("cmd", "cat focus.txt", "text", 3.9),
    ("out", "infrastructure  /  automation  /  observability", "amber", 4.65),
]


def request(url, token, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
        "User-Agent": "AshtonWard-profile", "X-GitHub-Api-Version": "2022-11-28",
    })
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def streaks(days, today):
    """Missing dates break a streak; an unfinished empty today does not."""
    counts = {date.fromisoformat(day["date"]): day["contributionCount"] for day in days
              if date.fromisoformat(day["date"]) <= today}
    if not counts:
        return 0, 0
    first = min(counts)
    longest = run = 0
    day = first
    while day <= today:
        run = run + 1 if counts.get(day, 0) > 0 else 0
        longest = max(longest, run)
        day += timedelta(days=1)
    day = today if counts.get(today, 0) else today - timedelta(days=1)
    current = 0
    while day >= first and counts.get(day, 0) > 0:
        current += 1
        day -= timedelta(days=1)
    return current, longest


def refresh_stats():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN is required for --refresh")
    now = datetime.now(timezone.utc).replace(microsecond=0)
    start = now - timedelta(days=365)
    query = '''query($login: String!, $start: DateTime!, $year: DateTime!, $end: DateTime!) {
      user(login: $login) {
        rolling: contributionsCollection(from: $start, to: $end) {
          contributionCalendar { weeks { contributionDays { date contributionCount } } }
        }
        ytd: contributionsCollection(from: $year, to: $end) {
          contributionCalendar { totalContributions }
        }
      }
    }'''
    result = request("https://api.github.com/graphql", token, {"query": query, "variables": {
        "login": "AshtonWard", "start": start.isoformat(),
        "year": f"{now.year}-01-01T00:00:00Z", "end": now.isoformat(),
    }})
    if result.get("errors") or not result.get("data", {}).get("user"):
        raise SystemExit("GitHub contribution query failed; retaining the previous assets.")
    user = result["data"]["user"]
    days = [day for week in user["rolling"]["contributionCalendar"]["weeks"]
            for day in week["contributionDays"]]
    current, longest = streaks(days, now.date())
    # This public-only endpoint cannot expose private repository names.
    events = request("https://api.github.com/users/AshtonWard/events/public?per_page=100", token)
    pushes = [event for event in events if event["type"] == "PushEvent" and event.get("public") is True]
    latest = max(pushes, key=lambda event: event["created_at"], default=None)
    return {"updated_at": now.isoformat(), "year": now.year, "current": current,
            "longest": longest, "year_total": user["ytd"]["contributionCalendar"]["totalContributions"],
            "last_push": {"repo": latest["repo"]["name"], "date": latest["created_at"][:10]} if latest else None}


def activity_rows(stats):
    rows = [("cmd", "./streak --status", "text", 4.9)]
    if not stats.get("updated_at"):
        rows.append(("out", "Activity stats awaiting their first GitHub refresh.", "muted", 5.65))
    else:
        current = stats["current"]
        status, color = (("dormant", "muted") if current == 0 else
                         ("beaconing", "amber") if current < 7 else
                         ("persistent", "green") if current < 30 else ("resident", "blue"))
        latest = stats["last_push"]
        push = f"{latest['repo']} @ {latest['date']}" if latest else "none in recent public events"
        # Keep text in the fixed terminal width, including unusually long repo names.
        if len(push) > 65:
            push = push[:48] + "... @ " + latest["date"]
        lines = [
            (f"[+] current streak          {current} day{'s' if current != 1 else ''}", "green"),
            (f"[+] longest streak (1y)     {stats['longest']} days", "text"),
            (f"[+] contributions ({stats['year']})    {stats['year_total']:,}", "text"),
            ("[+] last public push", "muted"),
            (f"    {push}", "blue"),
            (f"[*] status                  {status}", color),
        ]
        rows += [("out", text, color, 5.65 + i * .1) for i, (text, color) in enumerate(lines)]
    rows.append(("end", "", "text", 6.35))
    return rows


def render(theme):
    c = THEMES[theme]
    stats = json.loads((ROOT / "assets" / "stats.json").read_text(encoding="utf-8"))
    rows = ROWS + activity_rows(stats)
    height = 91 + len(rows) * 25 + sum(13 for i, row in enumerate(rows) if i and row[0] in ("cmd", "end")) + 31
    items = []
    y = 91
    for i, (kind, value, color, delay) in enumerate(rows):
        if kind in ("cmd", "end") and i:
            y += 13
        if kind in ("cmd", "end"):
            prompt = '<tspan fill="{green}">ashton@subnetphantom</tspan><tspan fill="{muted}">:</tspan><tspan fill="{blue}">~</tspan><tspan fill="{text}">$ </tspan>'.format(**c)
            text = prompt + escape(value)
        else:
            text = escape(value)
        duration = 0.55 if kind == "cmd" else 0.12
        # clip-path reveals a line once. Without CSS support the final text stays visible.
        style = f"animation:reveal {duration}s steps({max(len(value), 1)},end) {delay}s both"
        items.append(f'<text x="28" y="{y}" fill="{c[color]}" style="{style}">{text}</text>')
        if kind == "end":
            items.append(f'<rect x="242" y="{y-13}" width="8" height="16" rx="1" fill="{c["green"]}" style="animation:cursor 1s step-end {delay}s 3 both"/>')
        y += 25
    refreshed = stats.get("updated_at")
    footer = f"STATS / {refreshed[:16].replace('T', ' ')} UTC" if refreshed else "STATS / PENDING FIRST REFRESH"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" width="880" height="{height}" viewBox="0 0 880 {height}" role="img" aria-labelledby="title desc">
<title id="title">Ashton Ward — engineering profile</title>
<desc id="desc">Terminal introduction: QA Engineer, Network Specialist, Homelab Builder. Build reliable infrastructure. Automate the repeatable work. Understand what happens underneath. Projects: Ansible automation, homelab, Putler.</desc>
<!-- A small source-only capture: flag{{understand_automate_verify}} -->
<style>
text{{font-family:'DejaVu Sans Mono','Liberation Mono',Consolas,monospace;font-size:15px;white-space:pre}}
@keyframes reveal{{from{{clip-path:inset(0 100% 0 0)}}to{{clip-path:inset(0 0 0 0)}}}}
@keyframes cursor{{0%,100%{{opacity:1}}50%{{opacity:0}}}}
@media(prefers-reduced-motion:reduce){{text,rect{{animation:none!important}}}}
</style>
<rect x=".5" y=".5" width="879" height="{height-1}" rx="12" fill="{c['bg']}" stroke="{c['border']}"/>
<path d="M1 45V13Q1 1 13 1H867Q879 1 879 13V45Z" fill="{c['bar']}"/>
<path d="M1 45H879" stroke="{c['border']}"/>
<circle cx="25" cy="23" r="5" fill="{c['green']}"/>
<circle cx="44" cy="23" r="5" fill="{c['amber']}"/>
<circle cx="63" cy="23" r="5" fill="{c['blue']}"/>
<text x="440" y="28" text-anchor="middle" fill="{c['muted']}" style="font-size:12px;letter-spacing:1px">ASHTON WARD / ENGINEERING LOG</text>
{chr(10).join(items)}
<text x="852" y="{height-18}" text-anchor="end" fill="{c['muted']}" style="font-size:10px;letter-spacing:1px">{footer}</text>
</svg>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    if args.refresh and args.check:
        parser.error("Use --refresh and --check separately")
    if args.refresh:
        stats = refresh_stats()
        (ROOT / "assets" / "stats.json").write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    for theme in THEMES:
        path = ROOT / "assets" / f"terminal-{theme}.svg"
        content = render(theme)
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                raise SystemExit(f"Out-of-date asset: {path.name}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    print("Terminal assets verified." if args.check else "Terminal assets generated.")


if __name__ == "__main__":
    main()
