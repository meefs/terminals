#!/usr/bin/env python3
"""Bake data.json for the terminals report.

Fetches GitHub star counts + last-push dates and npm monthly download counts,
then writes data.json at the repo root. Runs server-side (in a GitHub Action or
locally) so no rate limits or secrets ever reach the published page.

Auth: set GH_TOKEN (or GITHUB_TOKEN). In Actions, the workflow passes the
auto-provided GITHUB_TOKEN. Locally:  GH_TOKEN=$(gh auth token) python3 scripts/refresh.py
"""
import json, os, time, urllib.request, urllib.error

REPOS = [
    "hpjansson/chafa", "dankamongmen/notcurses", "hzeller/timg", "atanunq/viu",
    "posva/catimg", "stefanhaustein/TerminalImageViewer", "TheZoraiz/ascii-image-converter",
    "jstkdng/ueberzugpp", "cacalabs/libcaca", "vadimdemedes/ink", "xtermjs/xterm.js",
    "chjj/blessed", "cronvel/terminal-kit", "sindresorhus/terminal-image",
    "patorjk/figlet.js", "bokub/gradient-string", "dominikwilkowski/cfonts",
    "madbence/node-drawille", "jerch/node-sixel", "charmbracelet/bubbletea",
    "charmbracelet/lipgloss", "ratatui/ratatui", "Textualize/rich", "Textualize/textual",
    "ohmyzsh/ohmyzsh", "romkatv/powerlevel10k", "starship/starship",
    "alacritty/alacritty", "ghostty-org/ghostty", "kovidgoyal/kitty",
    "wezterm/wezterm", "warpdotdev/warp",
]
NPM = ["ink", "@xterm/xterm", "blessed", "terminal-kit", "terminal-image",
       "figlet", "gradient-string", "cfonts", "drawille", "sixel"]

TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")


def fetch(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)


def gh(full):
    h = {"Accept": "application/vnd.github+json", "User-Agent": "terminals-report"}
    if TOKEN:
        h["Authorization"] = "Bearer " + TOKEN
    d = fetch("https://api.github.com/repos/" + full, h)
    return {"stars": d["stargazers_count"], "pushed": d["pushed_at"]}


def npm_downloads(pkg):
    d = fetch("https://api.npmjs.org/downloads/point/last-month/" + pkg)
    return d.get("downloads")


def main():
    repos, npm = {}, {}
    for full in REPOS:
        try:
            repos[full] = gh(full)
            print("  gh   %-34s %s" % (full, repos[full]["stars"]))
        except Exception as e:                       # noqa: BLE001
            print("  gh   FAIL", full, e)
        time.sleep(0.15)
    for p in NPM:
        try:
            npm[p] = {"downloads": npm_downloads(p)}
            print("  npm  %-20s %s" % (p, npm[p]["downloads"]))
        except Exception as e:                       # noqa: BLE001
            print("  npm  FAIL", p, e)
    out = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repos": repos,
        "npm": npm,
    }
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "data.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print("wrote %s — %d repos, %d npm" % (path, len(repos), len(npm)))


if __name__ == "__main__":
    main()
