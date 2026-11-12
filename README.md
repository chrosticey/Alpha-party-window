<div align="center">

# ⚡ Alpha Party Window
### *A sleek, Cyber-Glass Party Window overhaul for BombSquad — fast, expressive, and crafted for players.*

![Version](https://img.shields.io/badge/version-1.3--alpha-00e5ff?style=for-the-badge)
![API](https://img.shields.io/badge/BombSquad%20API-9-ff9100?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-00e676?style=for-the-badge)
![Platform](https://img.shields.io/badge/platform-Android%20%7C%20PC%20%7C%20Mac-9e9e9e?style=for-the-badge)

[📦 Releases](../../releases) • [🐛 Report a Bug](../../issues) • [📖 Quick Usage](#-how-to-use)

</div>

---

## ✨ Features

| ✨ Feature | 📝 Description |
|------------|----------------|
| 🪟 **Cyber-Glass Tabbed UI** | Smooth **Chat**, **Roster**, and **Servers** tabs with custom themes, presets, RGB/Hex picker & synced neon outlines |
| 🌐 **Universal & Romanized Translate** | Translate individual chats or the entire feed — supports native scripts plus Romanized chat (*Hinglish, Arabizi, RU Translit, etc.*) |
| 💬 **Smart Chat & 4-Word Reply** | Tap any message to **Translate / Revert**, **Copy**, or **Reply** *(quotes up to 4 words)*; navigate with `▲` / `▼` and view live `ms` ping inside the empty input box |
| ⚡ **Quick Replies Manager** | Tap `Quick` → **`➕ Add / Manage Quick Replies...`** to add, delete, or reset phrases in one place |
| 🐉 **Quick Icons & ⭐ Favourites** | Clean icon popup organized into **Favourites**, **Emblems**, **Others**, and **All** (`Slot #1` sets your toolbar button icon) |
| 🌈 **Animated Chat Strip** | Customizable animated bar next to chat controls (`Neon Scanner`, `Synth Equalizer`, `Pulse Wave`, `Cyber Prism`, or `Off`) |
| 🔇 **Per-Player Mute + Restore** | Silence noisy players cleanly — **unmuting restores** the session chats you missed while muted |
| 🛠️ **Custom Command Maker** | Build Instant or Draft commands with live placeholders `{cid}`, `{acc}`, `{name}`, `{nick}`, `{aid}`, `{me}`, `{dur}` |
| 👋 **Auto Greet & 📋 Player Lists** | Greet V2/AID friends on join or reply to greetings; manage **Muted**, **Nicknames**, and **Auto Greet** lists in one window |
| ⭐ **Saved Servers & 🚨 Complaint** | One-tap server saving/joining and formatted complaint builder with Account ID detection |
| 📜 **Session Chat Logs** | Automatically logs dated chat sessions with built-in **View**, **Rename**, and **Delete** controls |
| 🔔 **Manual Update Notifications** | Checks GitHub on boot without touching your files — notifies you with **Update**, **GitHub**, and **✕**, installing **only** when you click Update |
| 🛡️ **Crash Recovery** | Creates a `.bak` backup before every update and recovers automatically on load errors |

> 🧑‍💻 **Created by** `@chrosticey`

---

## 📦 Installation

Pick whichever method suits you best:

### Method 1 — In-Game Console One-Liner ⚡ *(Easiest)*

> Works on **all platforms** — no file manager required.

1. Open **BombSquad** → **Settings** → **Advanced** → **Dev Tools** → enable **Show Developer Console**
2. Go back to the main menu and tap the **`Dev`** button
3. Paste this line and press **Enter**:

```python
import urllib.request,os,ssl,babase,_babase; exec(urllib.request.urlopen("https://raw.githubusercontent.com/chrosticey/Alpha-party-window/main/install.py",context=ssl._create_unverified_context()).read().decode())
```

4. Wait for **"Installed! Please restart."**, then **restart BombSquad** ✅

---

### Method 2 — Ballistica Workspace Sync 🌐 *(No file manager needed)*

> Requires a free **V2 / Ballistica account** at [ballistica.net](https://ballistica.net).

1. Sign in to [ballistica.net](https://ballistica.net) and in BombSquad under **Settings → Account**
2. Open **Workspace** on [ballistica.net](https://ballistica.net) and create/select a workspace
3. Click **Add Files / Folders → Upload file** and upload [`alpha_party_window.py`](alpha_party_window.py)
4. In BombSquad go to **Settings → Account → Workspace** → **Sync Now** → **Restart BombSquad** ✅

---

### Method 3 — Manual File Copy 🗂️

| 🖥️ Platform | 📂 Mods Folder Path |
|-------------|---------------------|
| 🤖 **Android** | `Android/data/net.froemling.bombsquad/files/mods/` |
| 🍎 **Mac** | `~/Library/Application Support/BombSquad/mods/` |
| 🪟 **Windows** | `%APPDATA%\BombSquad\mods\` |
| 🐧 **Linux** | `~/.bombsquad/mods/` |
| 🔎 **Any** | **Settings → Advanced → Show Mods Folder** |

1. Download [`alpha_party_window.py`](../../releases/latest)
2. Drop it into your mods folder and restart BombSquad ✅

---

## 📖 How to Use

| 🎯 Goal | 🖱️ Steps |
|---------|----------|
| **Reply / Copy / Translate a message** | Tap any chat row, or use `▲`, `▼`, `🌐`, `Copy`, `Reply` at the bottom-right |
| **Add or edit Quick Replies** | Tap **`Quick`** → **`➕ Add / Manage Quick Replies...`** → type & click **Add** |
| **Customize your Icon button** | Tap the Icon button beside `Quick` → enable **Pin Fav: ON** → set **Slot #1** |
| **Set Translation languages** | Menu (`⚙`) → **Translate Settings** → **From** *(left)* / **Into** *(right)* |
| **Change Chat Bar animation** | Menu (`⚙`) → **Chat Bar Anim** → pick Scanner, Equalizer, Wave, Prism, or Off |
| **Customize Colors & Outlines** | Menu (`⚙`) → **Colors & Chat Style** → pick presets, RGB/Hex custom color, or **Sync Outlines** |
| **Run or build commands** | **Roster** → `🛠️` to run commands, or Menu (`⚙`) → **Custom Command Maker** |
| **Mute / Unmute someone** | **Roster** → **Actions** → **Mute Chat** *(unmuting brings back missed chats)* |
| **Use dot commands in chat** | Send `.ip`, `.ping`, `.info`, or `.save` in the input box |
| **Full in-game guide** | Menu (`⚙`) → **Help & Feature Guide** |

---

## 🔔 Manual Update System

```text
Game Launch ──(8s)──▶ Check version.json on GitHub (read-only)
                          │
        New version? ─────┴──▶ Show Update Banner + Updates Menu
                                  ├── [Update] ──▶ Backup .bak + Download + Validate + Prompt Restart
                                  ├── [GitHub] ──▶ Open repo to inspect code
                                  └── [✕]      ──▶ Hide until next game launch
```

- **Strict opt-in updates**: the plugin **never** modifies itself until you explicitly tap **Update**
- **Syntax verified**: downloads are checked with Python `ast.parse` and backed up to `.bak` before saving
- Prefer no version check at all? Set `APW_UPDATE_CHECK = False` near line `53` of `alpha_party_window.py`

---

## 🗑️ Uninstall

Paste into the BombSquad console:

```python
import os,_babase; os.remove(os.path.join(_babase.env()["python_directory_user"],"alpha_party_window.py")); print("Removed. Restart BombSquad.")
```

Or delete `alpha_party_window.py` from your mods folder manually.

---

## 📁 Repository Structure

```text
Alpha-party-window/
├── alpha_party_window.py   # Main Cyber-Glass party window plugin
├── install.py              # One-liner BombSquad console installer
├── version.json            # Version & changelog metadata for update checks
├── README.md               # Documentation
├── LICENSE                 # MIT License
└── .gitignore
```

---

## 🙌 Credits & Inspiration

<div align="center">

**Massive thanks and huge inspiration from ✨ *Fluffy Party Window* ✨ and *Advanced Party Window* — thank you for shaping the ideas and features behind this project.**

*MIT License • Made for the BombSquad community by `@chrosticey`*

</div>
