#!/usr/bin/env python3
"""Generate the profile terminal assets. Standard library only; no network or tokens.

Run: python scripts/render_terminal.py
Check generated files: python scripts/render_terminal.py --check
Edit ROWS below to change the terminal. Assets are committed so the profile has
no dependency on a scheduled workflow or third-party badge service.
"""
import argparse
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
    ("end", "", "text", 4.9),
]


def render(theme):
    c = THEMES[theme]
    items = []
    y = 91
    for i, (kind, value, color, delay) in enumerate(ROWS):
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
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" width="880" height="474" viewBox="0 0 880 474" role="img" aria-labelledby="title desc">
<title id="title">Ashton Ward — engineering profile</title>
<desc id="desc">Terminal introduction: QA Engineer, Network Specialist, Homelab Builder. Build reliable infrastructure. Automate the repeatable work. Understand what happens underneath. Projects: Ansible automation, homelab, Putler.</desc>
<!-- A small source-only capture: flag{{understand_automate_verify}} -->
<style>
text{{font-family:'DejaVu Sans Mono','Liberation Mono',Consolas,monospace;font-size:15px;white-space:pre}}
@keyframes reveal{{from{{clip-path:inset(0 100% 0 0)}}to{{clip-path:inset(0 0 0 0)}}}}
@keyframes cursor{{0%,100%{{opacity:1}}50%{{opacity:0}}}}
@media(prefers-reduced-motion:reduce){{text,rect{{animation:none!important}}}}
</style>
<rect x=".5" y=".5" width="879" height="473" rx="12" fill="{c['bg']}" stroke="{c['border']}"/>
<path d="M1 45V13Q1 1 13 1H867Q879 1 879 13V45Z" fill="{c['bar']}"/>
<path d="M1 45H879" stroke="{c['border']}"/>
<circle cx="25" cy="23" r="5" fill="{c['green']}"/>
<circle cx="44" cy="23" r="5" fill="{c['amber']}"/>
<circle cx="63" cy="23" r="5" fill="{c['blue']}"/>
<text x="440" y="28" text-anchor="middle" fill="{c['muted']}" style="font-size:12px;letter-spacing:1px">ASHTON WARD / ENGINEERING LOG</text>
{chr(10).join(items)}
<text x="852" y="454" text-anchor="end" fill="{c['muted']}" style="font-size:10px;letter-spacing:1px">BUILD / UNDERSTAND / IMPROVE</text>
</svg>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
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
