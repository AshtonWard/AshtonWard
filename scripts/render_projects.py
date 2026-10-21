#!/usr/bin/env python3
"""Render the README project cards. Run from any directory; no dependencies.

Edit PROJECTS below, then run python scripts/render_projects.py.
The generated SVGs are committed and need no external rendering service.
"""
from html import escape
from pathlib import Path
from textwrap import wrap

ROOT = Path(__file__).resolve().parents[1]
THEMES = {
    "dark": dict(bg="#10171d", border="#31404b", text="#e3eaf0", muted="#a0aeb9", green="#8bc9a2", amber="#e2bb79", link="#8ebad9"),
    "light": dict(bg="#f8fafb", border="#d0d7de", text="#243540", muted="#526674", green="#2e7049", amber="#886018", link="#315f83"),
}
PROJECTS = [
    dict(slug="ansible", title="Infrastructure automation", icon="terminal", width=430, height=300,
         status=["PUBLIC EXAMPLES IN PROGRESS"],
         description="Turning repetitive VM provisioning and Linux configuration into repeatable workflows.",
         tools=["Ansible · Proxmox VE · GitHub Actions"], link="Explore Ansible →"),
    dict(slug="homelab", title="Homelab engineering", icon="server", width=430, height=300,
         status=["PUBLIC DOCUMENTATION", "IN PREPARATION"],
         description="Hands-on work in virtualization, segmented networking, secure remote access, and recovery.",
         tools=["Linux · OPNsense · Docker · Wazuh"], link="Explore the homelab →"),
    dict(slug="putler", title="Putler / Homelab assistant", icon="bot", width=880, height=250,
         status=["IN DEVELOPMENT · INCIDENT WORKFLOWS PLANNED"],
         description="A Hermes-based assistant for investigation, documentation, and guided learning. Designing bounded investigations with human approval for consequential changes.",
         tools=["Hermes · Alert-driven investigation · Evidence-based reporting"], link="Read the dispatcher design →"),
]


def render(project, theme):
    c = THEMES[theme]
    w, h = project["width"], project["height"]
    content = []

    def text(x, y, value, color="text", size=16, mono=False):
        family = "'DejaVu Sans Mono',Consolas,monospace" if mono else "'DejaVu Sans',Arial,sans-serif"
        content.append(f'<text x="{x}" y="{y}" fill="{c[color]}" font-family="{family}" font-size="{size}">{escape(value)}</text>')

    icons = {
        "terminal": '<rect x="25" y="25" width="21" height="18" rx="3"/><path d="m29 30 4 4-4 4m8 0h5"/>',
        "server": '<rect x="25" y="25" width="21" height="8" rx="2"/><rect x="25" y="36" width="21" height="8" rx="2"/><path d="M29 29h1m-1 11h1"/>',
        "bot": '<rect x="25" y="28" width="21" height="16" rx="4"/><path d="M35.5 28v-5m-13 10v6m26-6v6m-19-5h2m7 0h2m-9 5h7"/>',
    }
    content.append(f'<g fill="none" stroke="{c["green"]}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{icons[project["icon"]]}</g>')
    text(58, 40, project["title"], size=19)
    for i, line in enumerate(project["status"]):
        text(25, 75 + 18 * i, line, "amber", 12, True)
    # Same baseline for both compact cards, with room for two-line status labels.
    top = 130 if w == 430 else 112
    for i, line in enumerate(wrap(project["description"], width=42 if w == 430 else 95)):
        text(25, top + i * 25, line, size=16)
    for i, line in enumerate(project["tools"]):
        text(25, h - 66 + i * 18, line, "muted", 12, True)
    text(25, h - 27, project["link"], "link", 15)
    desc = f"{project['title']}. {' '.join(project['status'])}. {project['description']} {' '.join(project['tools'])}. {project['link']}"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">
<title id="title">{escape(project['title'])}</title>
<desc id="desc">{escape(desc)}</desc>
<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="10" fill="{c['bg']}" stroke="{c['border']}"/>
{chr(10).join(content)}
</svg>
'''


if __name__ == "__main__":
    (ROOT / "assets").mkdir(exist_ok=True)
    for project in PROJECTS:
        for theme in THEMES:
            path = ROOT / "assets" / f"project-{project['slug']}-{theme}.svg"
            path.write_text(render(project, theme), encoding="utf-8")
    print("Generated six project card assets.")
