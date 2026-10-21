#!/usr/bin/env python3
"""Validate generated skyline assets, then add/update their README section.

Called after the 3D contribution action. Never adds links to missing images.
"""
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
START = "<!--SKYLINE:START-->"
END = "<!--SKYLINE:END-->"
BLOCK = '''<!--SKYLINE:START-->
<details>
<summary>Contribution skyline — explore the 3D calendar</summary>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="profile-3d-contrib/night.svg">
  <source media="(prefers-color-scheme: light)" srcset="profile-3d-contrib/day.svg">
  <img src="profile-3d-contrib/night.svg" width="100%" alt="Ashton Ward's contribution calendar rendered as a 3D skyline. Taller blocks represent more contributions on a day; accompanying charts summarize contribution types and languages.">
</picture>

<sub>Generated from GitHub activity; refreshes with the terminal stats every six hours. Built with <a href="https://github.com/yoshi389111/github-profile-3d-contrib">github-profile-3d-contrib</a>.</sub>

</details>
<!--SKYLINE:END-->

'''


def update():
    for name in ("day.svg", "night.svg"):
        path = ROOT / "profile-3d-contrib" / name
        tree = ET.parse(path)
        if tree.getroot().tag != "{http://www.w3.org/2000/svg}svg":
            raise ValueError(f"Not an SVG image: {name}")
    path = ROOT / "README.md"
    readme = path.read_text(encoding="utf-8")
    if START in readme:
        start = readme.index(START)
        end = readme.index(END, start) + len(END)
        readme = readme[:start] + BLOCK.rstrip() + readme[end:]
    else:
        anchor = "## Tools I work with"
        if anchor not in readme:
            raise ValueError("README insertion point is missing")
        readme = readme.replace(anchor, BLOCK + anchor, 1)
    path.write_text(readme, encoding="utf-8")
    print("Skyline images verified and README section updated.")


if __name__ == "__main__":
    update()
