#!/usr/bin/env python3
"""
Alpha Party Window - One-Click Installer
Installs or updates alpha_party_window.py into your BombSquad user mods directory.
Repo: https://github.com/chrosticey/Alpha-party-window
"""

import os
import sys
import platform
import urllib.request

RAW_URL = "https://raw.githubusercontent.com/chrosticey/Alpha-party-window/main/alpha_party_window.py"
FILE_NAME = "alpha_party_window.py"


def get_mods_dir() -> str:
    system = platform.system()
    home = os.path.expanduser("~")

    # 1. Windows
    if system == "Windows":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            return os.path.join(local_app_data, "BombSquad", "mods")
        return os.path.join(home, "AppData", "Local", "BombSquad", "mods")

    # 2. macOS
    if system == "Darwin":
        return os.path.join(home, "Library", "Application Support", "BombSquad", "mods")

    # 3. Android (Termux / Pydroid / generic terminal)
    android_candidates = [
        "/storage/emulated/0/BombSquad/mods",
        "/sdcard/BombSquad/mods",
        os.path.join(home, "storage", "shared", "BombSquad", "mods"),
    ]
    for p in android_candidates:
        if os.path.isdir(os.path.dirname(p)):
            return p

    # 4. Linux fallback
    return os.path.join(home, ".bombsquad", "mods")


def main() -> None:
    print("=" * 60)
    print("  🚀 Alpha Party Window v1.31-alpha Installer")
    print("=" * 60)

    target_dir = get_mods_dir()
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, FILE_NAME)

    print(f"[*] Target Directory: {target_dir}")
    print(f"[*] Downloading from: {RAW_URL}")

    try:
        req = urllib.request.Request(
            RAW_URL,
            headers={"User-Agent": "Mozilla/5.0 (AlphaPartyWindowInstaller/1.31-alpha)"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()

        if len(content) < 1000:
            raise RuntimeError("Downloaded file is too small or incomplete.")

        with open(target_path, "wb") as f:
            f.write(content)

        print("\n" + "=" * 60)
        print("  ✅ Installation Successful!")
        print(f"  Saved to: {target_path}")
        print("  Restart BombSquad to enjoy Alpha Party Window v1.31-alpha!")
        print("=" * 60)
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"  ❌ Installation failed: {e}")
        print(f"  Please download manually from: {RAW_URL}")
        print(f"  and place it inside: {target_dir}")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
