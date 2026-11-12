# -*- coding: utf-8 -*-
"""
Alpha Party Window - Quick Installer / Updater (v1.3-alpha)
Author: @chrosticey
Repository: https://github.com/chrosticey/Alpha-party-window
"""

import os
import sys
import shutil
import urllib.request
import json

PLUGIN_FILENAME = "alpha_party_window.py"
RAW_BASE_URL = "https://raw.githubusercontent.com/chrosticey/Alpha-party-window/main"
PLUGIN_URL = f"{RAW_BASE_URL}/{PLUGIN_FILENAME}"
VERSION_URL = f"{RAW_BASE_URL}/version.json"


def find_mods_directories():
    candidates = []
    home = os.path.expanduser("~")

    if sys.platform.startswith("win"):
        local_app = os.environ.get("LOCALAPPDATA", os.path.join(home, "AppData", "Local"))
        appdata = os.environ.get("APPDATA", os.path.join(home, "AppData", "Roaming"))
        candidates.extend([
            os.path.join(local_app, "BombSquad", "mods"),
            os.path.join(appdata, "BombSquad", "mods"),
            os.path.join(home, "BombSquad", "mods"),
        ])
    elif sys.platform == "darwin":
        candidates.extend([
            os.path.join(home, "Library", "Application Support", "BombSquad", "mods"),
            os.path.join(home, "BombSquad", "mods"),
        ])
    else:
        candidates.extend([
            os.path.join(home, ".local", "share", "bombsquad", "mods"),
            os.path.join(home, ".bombsquad", "mods"),
            os.path.join(home, "BombSquad", "mods"),
        ])

    valid = []
    seen = set()
    for p in candidates:
        norm = os.path.normpath(os.path.abspath(p))
        if norm not in seen:
            seen.add(norm)
            valid.append(norm)
    return valid


def fetch_latest_version():
    try:
        req = urllib.request.Request(VERSION_URL, headers={"User-Agent": "APW-Installer/1.3"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("version", "1.3-alpha")
    except Exception:
        return "1.3-alpha"


def download_plugin():
    print(f"[*] Downloading {PLUGIN_FILENAME} from GitHub...")
    req = urllib.request.Request(PLUGIN_URL, headers={"User-Agent": "APW-Installer/1.3"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read()


def main():
    print("=" * 60)
    print("  Alpha Party Window - Glassmorphic Edition Installer")
    print("  Version: 1.3-alpha  |  Author: @chrosticey")
    print("=" * 60)

    ver = fetch_latest_version()
    print(f"[*] Target Release Version: v{ver}")

    mods_dirs = find_mods_directories()
    existing_dirs = [d for d in mods_dirs if os.path.isdir(d)]

    if not existing_dirs:
        target_dir = mods_dirs[0]
        try:
            os.makedirs(target_dir, exist_ok=True)
            chosen_dirs = [target_dir]
            print(f"[+] Created mods directory: {target_dir}")
        except Exception as e:
            print(f"[-] Failed to create mods directory: {e}")
            sys.exit(1)
    else:
        chosen_dirs = existing_dirs

    content = download_plugin()
    if not content or len(content) < 5000:
        print("[-] Downloaded file seems invalid or corrupted.")
        sys.exit(1)

    success_count = 0
    for d in chosen_dirs:
        dest_path = os.path.join(d, PLUGIN_FILENAME)
        bak_path = dest_path + ".bak"

        if os.path.isfile(dest_path):
            try:
                shutil.copy2(dest_path, bak_path)
                print(f"[*] Created backup: {bak_path}")
            except Exception as e:
                print(f"[!] Warning: Could not create backup: {e}")

        try:
            with open(dest_path, "wb") as f:
                f.write(content)
            print(f"[✓] Installed successfully into: {dest_path}")
            success_count += 1
        except Exception as e:
            print(f"[-] Error writing to {dest_path}: {e}")

    if success_count > 0:
        print("=" * 60)
        print("  🎉 Installation complete! Restart BombSquad to enjoy v1.3-alpha!")
        print("=" * 60)
    else:
        print("[-] Installation failed.")


if __name__ == "__main__":
    main()
