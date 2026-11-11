# -*- coding: utf-8 -*-
# ba_meta require api 9
'''
Alpha Party Window - Glassmorphic Edition
by @chrosticey

Upgraded with Clear Glass UI, Interactive Tabs,
Quick Icons Popup, Universal Translate, and v1.8+ Clean Moderation.

Version : 1.2-alpha
API     : 9
'''

import traceback
import ast
import codecs
import json
import random
import re
import zlib
import sys
import shutil
import copy
import urllib
import urllib.request
import urllib.parse
import os
import socket
import threading
import weakref
import base64
import datetime
import ssl
import math
import time
from typing import List, Sequence, Optional, Dict, Any, Union, cast
from _thread import start_new_thread

import babase
import bauiv1 as bui
import bascenev1 as bs
import _babase
import bauiv1lib.party as bascenev1lib_party
from bauiv1lib.popup import PopupMenuWindow, PopupWindow
from babase._general import CallPartial, CallStrict

version_str = "1.2-alpha"

APW_REPO_URL     = "https://github.com/chrosticey/Alpha-party-window"
APW_GITHUB_RAW   = "https://raw.githubusercontent.com/chrosticey/Alpha-party-window/main"
APW_VERSION_URL  = APW_GITHUB_RAW + "/version.json"
APW_PLUGIN_URL   = APW_GITHUB_RAW + "/alpha_party_window.py"
APW_UPDATE_CHECK = True
APW_PREVIEW_UPDATE = True

_apw_update_state: Dict[str, Any] = {
    "checking": False,
    "checked": True if APW_PREVIEW_UPDATE else False,
    "available": True if APW_PREVIEW_UPDATE else False,
    "remote_version": "1.2-alpha" if APW_PREVIEW_UPDATE else "",
    "min_api": 9,
    "changelog": "Preview notification — tap Update to install from GitHub, GitHub to inspect source, or X to hide until next launch." if APW_PREVIEW_UPDATE else "",
    "added": [
        "Chat strip animations (Scanner, Equalizer, Wave, Prism)",
        "Update banner notification & Updates details menu",
        "Help & Feature Guide menu",
    ] if APW_PREVIEW_UPDATE else [],
    "changed": [
        "Fixed duplicate chats when unmuting players",
        "Outline color sync toggle & custom Cyber Color Picker",
        "First Favourite icon syncs to Quick Icons button",
    ] if APW_PREVIEW_UPDATE else [],
    "download_url": APW_PLUGIN_URL,
    "error": "",
    "dismissed_this_boot": False,
    "installing": False,
    "installed_pending_restart": False,
}


def _apw_get_plugin_path() -> str:
    return os.path.join(_babase.env()["python_directory_user"], "alpha_party_window.py")


def _apw_version_tuple(v: str):
    nums = re.findall(r'\d+', v)
    return tuple(int(x) for x in nums)


def _apw_download_update(reason: str = "update", url_override: Optional[str] = None) -> bool:
    try:
        src_url = (url_override or _apw_update_state.get("download_url") or APW_PLUGIN_URL).strip()
        req = urllib.request.Request(
            src_url,
            headers={"User-Agent": "BombSquad-APW-Updater"})
        data = urllib.request.urlopen(req, timeout=20).read()
        ast.parse(data.decode("utf-8"))
        dest = _apw_get_plugin_path()
        backup = dest + ".bak"
        try:
            if os.path.exists(dest):
                shutil.copy2(dest, backup)
        except Exception:
            pass
        with open(dest, "wb") as f:
            f.write(data)
        print(f"[APW] ✅ {reason.capitalize()} successful. Restart BombSquad to apply.")
        return True
    except Exception as e:
        print(f"[APW] ❌ Download failed ({reason}):", e)
        return False


def _apw_restore_backup():
    dest   = _apw_get_plugin_path()
    backup = dest + ".bak"
    if os.path.exists(backup):
        try:
            shutil.copy2(backup, dest)
            print("[APW] 🔄 Restored backup file.")
            return True
        except Exception as e:
            print("[APW] ❌ Backup restore failed:", e)
    return False


def _apw_check_and_update(on_checked=None):
    if not APW_UPDATE_CHECK:
        return
    if APW_PREVIEW_UPDATE:
        _apw_update_state["checking"] = False
        _apw_update_state["checked"] = True
        if not _apw_update_state.get("installed_pending_restart"):
            _apw_update_state["available"] = True
        if callable(on_checked):
            try:
                _babase.pushcall(on_checked, from_other_thread=True)
            except Exception:
                pass
        return
    _apw_update_state["checking"] = True
    _apw_update_state["error"] = ""
    try:
        req = urllib.request.Request(
            APW_VERSION_URL,
            headers={"User-Agent": "BombSquad-APW-Updater"})
        raw  = urllib.request.urlopen(req, timeout=10).read()
        info = json.loads(raw.decode("utf-8"))
        remote_version = str(info.get("version", "0.0")).strip()
        cl_raw = info.get("changelog", "")
        if isinstance(cl_raw, list):
            cl_txt = "\n".join(f"• {x}" for x in cl_raw if str(x).strip())
        else:
            cl_txt = str(cl_raw or "").strip()
        added_raw = info.get("added", [])
        changed_raw = info.get("changed", [])
        is_newer = _apw_version_tuple(remote_version) > _apw_version_tuple(version_str)
        _apw_update_state.update({
            "checking": False,
            "checked": True,
            "available": is_newer and not _apw_update_state.get("installed_pending_restart", False),
            "remote_version": remote_version,
            "min_api": info.get("min_api", 9),
            "changelog": cl_txt,
            "added": list(added_raw) if isinstance(added_raw, list) else [],
            "changed": list(changed_raw) if isinstance(changed_raw, list) else [],
            "download_url": str(info.get("download_url") or APW_PLUGIN_URL).strip(),
            "error": "",
        })
        if is_newer:
            print(f"[APW] 🔔 New version available: {remote_version} (current: {version_str})")
        else:
            print(f"[APW] ✔ Up to date ({version_str}).")
    except Exception as e:
        _apw_update_state["checking"] = False
        _apw_update_state["checked"] = True
        _apw_update_state["error"] = str(e)
        print("[APW] ⚠ Update check failed:", e)

    def _ui_refresh():
        try:
            inst = _apw_active_window_ref() if _apw_active_window_ref is not None else None
            if inst is not None and hasattr(inst, '_refresh_header_players'):
                inst._refresh_header_players(force=True)
            if callable(on_checked):
                on_checked()
        except Exception:
            pass
    try:
        _babase.pushcall(_ui_refresh, from_other_thread=True)
    except Exception:
        pass


def _apw_install_update_async(on_done=None) -> None:
    if _apw_update_state.get("installing"):
        return
    _apw_update_state["installing"] = True
    target_ver = _apw_update_state.get("remote_version") or "latest"

    def _worker():
        ok = _apw_download_update("manual-update")
        _apw_update_state["installing"] = False
        if ok:
            _apw_update_state["available"] = False
            _apw_update_state["installed_pending_restart"] = True

        def _finish():
            try:
                if ok:
                    babase.screenmessage(
                        f"Updated to {target_ver}! Restart BombSquad to apply.",
                        color=(0.25, 1.0, 0.45))
                else:
                    babase.screenmessage("Update download failed. Check console/GitHub.", color=(1.0, 0.35, 0.35))
                inst = _apw_active_window_ref() if _apw_active_window_ref is not None else None
                if inst is not None and hasattr(inst, '_refresh_header_players'):
                    inst._refresh_header_players(force=True)
                if callable(on_done):
                    on_done(ok)
            except Exception:
                pass
        try:
            _babase.pushcall(_finish, from_other_thread=True)
        except Exception:
            pass

    start_new_thread(_worker, ())


cache_chat = []
draft_chat_text = ''
connect = bs.connect_to_party
disconnect = bs.disconnect_from_host
unmuted_names = []
muted_chat_names = set()
chatlogger = False
screenmsg = True
ip_add = "127.0.0.1"
p_port = 43210
current_ping = 0.0
ssl._create_default_https_context = ssl._create_unverified_context


def newconnect_to_party(address, port=43210, print_progress=False):
    global ip_add, p_port
    try:
        dd = bs.get_connection_to_host_info_2()
        title = getattr(dd, 'name', '') if dd else ''
        if dd and title:
            bs.chatmessage("Left: " + str(title))
        ip_add = address
        p_port = port
        bs.chatmessage(f"Connecting to IP {address} PORT {port}")
        if bool(dd):
            bs.disconnect_from_host()
        connect(address, port, print_progress)
    except Exception as e:
        bui.screenmessage("Connection failed: " + str(e), color=(1, 0.3, 0.3))


class PingThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)

    def run(self) -> None:
        global current_ping
        while True:
            sock: Optional[socket.socket] = None
            try:
                from babase._net import get_ip_address_type
                socket_type = get_ip_address_type(ip_add)
                sock = socket.socket(socket_type, socket.SOCK_DGRAM)
                sock.settimeout(1.0)
                sock.connect((ip_add, p_port))
                starttime = time.time()
                for _ in range(2):
                    sock.send(b'\x0b')
                    try:
                        result = sock.recv(10)
                        if result == b'\x0c':
                            ping = (time.time() - starttime) * 1000.0
                            current_ping = round(ping, 2)
                            break
                    except Exception:
                        pass
                    time.sleep(0.5)
            except Exception:
                pass
            finally:
                if sock is not None:
                    try:
                        sock.close()
                    except Exception:
                        pass
            time.sleep(3.5)


RecordFilesDir = os.path.join(_babase.env()["python_directory_user"], "Configs" + os.sep)
if not os.path.exists(RecordFilesDir):
    try:
        os.makedirs(RecordFilesDir)
    except Exception:
        pass

Current_Lang = None
SystemEncode = sys.getfilesystemencoding()
if not isinstance(SystemEncode, str):
    SystemEncode = "utf-8"

PingThread().start()


_apw_chatlog_state: Dict[str, Any] = {
    "server_key": "",
    "file_path": "",
    "last_msg": None,
}


def _apw_get_chatlogs_dir() -> str:
    d = os.path.join(RecordFilesDir, "ChatLogs")
    try:
        os.makedirs(d, exist_ok=True)
    except Exception:
        pass
    return d


def _apw_is_chatlogger_enabled() -> bool:
    return bool(babase.app.config.get('APW_ChatLogger_Enabled', False))


def _apw_set_chatlogger_enabled(enabled: bool) -> None:
    global chatlogger
    chatlogger = bool(enabled)
    babase.app.config['APW_ChatLogger_Enabled'] = chatlogger
    babase.app.config.commit()


def _apw_sync_chatlogger_cfg() -> None:
    global chatlogger
    chatlogger = _apw_is_chatlogger_enabled()


def _apw_chatlog_tick() -> None:
    try:
        if not _apw_is_chatlogger_enabled():
            _apw_chatlog_state["server_key"] = ""
            _apw_chatlog_state["file_path"] = ""
            _apw_chatlog_state["last_msg"] = None
            return

        roster = bs.get_game_roster() or []
        msgs = bs.get_chat_messages() or []
        info = bs.get_connection_to_host_info_2()
        if isinstance(info, dict):
            sname = str(info.get('name', '') or '').strip()
            saddr = str(info.get('address', '') or '').strip()
        else:
            sname = str(getattr(info, 'name', '') or '').strip() if info else ''
            saddr = str(getattr(info, 'address', '') or '').strip() if info else ''

        if not roster and not sname:
            _apw_chatlog_state["server_key"] = ""
            _apw_chatlog_state["file_path"] = ""
            _apw_chatlog_state["last_msg"] = None
            return

        server_key = f"{sname}|{saddr}"
        now_dt = datetime.datetime.now()
        date_str = now_dt.strftime("%Y-%m-%d %H:%M")
        safe_srv = re.sub(r'[^A-Za-z0-9 _-]+', '', sname or 'Party').strip()[:32] or 'Party'

        if server_key != _apw_chatlog_state["server_key"] or not _apw_chatlog_state["file_path"]:
            fname = f"log_{now_dt.strftime('%Y%m%d_%H%M%S')}_{safe_srv.replace(' ', '_')}.json"
            fpath = os.path.join(_apw_get_chatlogs_dir(), fname)
            _apw_chatlog_state["server_key"] = server_key
            _apw_chatlog_state["file_path"] = fpath
            _apw_chatlog_state["last_msg"] = None
            seed_lines = [f"[{now_dt.strftime('%H:%M:%S')}] {m}" for m in msgs]
            if msgs:
                _apw_chatlog_state["last_msg"] = msgs[-1]
            payload = {
                "title": f"{date_str} - {sname or 'Party'}",
                "date": now_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "server": sname or "Party",
                "addr": f"{ip_add}:{p_port}",
                "messages": seed_lines,
            }
            if seed_lines:
                with open(fpath, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False, indent=2)
            return

        if not msgs:
            return

        last_seen = _apw_chatlog_state["last_msg"]
        if last_seen is None:
            new_msgs = list(msgs)
        elif last_seen in msgs:
            idx = len(msgs) - 1 - msgs[::-1].index(last_seen)
            new_msgs = msgs[idx + 1:]
        else:
            new_msgs = msgs[-5:]

        if not new_msgs:
            return

        _apw_chatlog_state["last_msg"] = msgs[-1]
        fpath = _apw_chatlog_state["file_path"]
        data = {
            "title": f"{date_str} - {sname or 'Party'}",
            "date": now_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "server": sname or "Party",
            "addr": f"{ip_add}:{p_port}",
            "messages": [],
        }
        if os.path.isfile(fpath):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    data.update(loaded)
            except Exception:
                pass
        stamp = now_dt.strftime("%H:%M:%S")
        for m in new_msgs:
            data.setdefault("messages", []).append(f"[{stamp}] {m}")
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _apw_list_chatlogs() -> List[Dict[str, Any]]:
    logs_dir = _apw_get_chatlogs_dir()
    items = []
    try:
        for fn in sorted(os.listdir(logs_dir), reverse=True):
            if not fn.endswith(".json"):
                continue
            fpath = os.path.join(logs_dir, fn)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    data["_path"] = fpath
                    data.setdefault("title", fn[:-5])
                    data.setdefault("date", "")
                    data.setdefault("server", "Party")
                    data.setdefault("addr", "")
                    if not isinstance(data.get("messages"), list):
                        data["messages"] = []
                    items.append(data)
            except Exception:
                pass
    except Exception:
        pass
    return items


def _apw_rename_chatlog(fpath: str, new_title: str) -> bool:
    try:
        if not os.path.isfile(fpath):
            return False
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return False
        data["title"] = new_title.strip()[:60]
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def _apw_delete_chatlog(fpath: str) -> bool:
    try:
        if os.path.isfile(fpath):
            os.remove(fpath)
            return True
    except Exception:
        pass
    return False


class chatloggThread:
    def run(self) -> None:
        _apw_set_chatlogger_enabled(True)


class mututalServerThread:
    def run(self):
        self.timer = babase.AppTimer(10, self.checkPlayers, repeat=True)

    def checkPlayers(self):
        if bool(bs.get_connection_to_host_info_2()):
            info = bs.get_connection_to_host_info_2()
            server_name = info.get("name", "Unnamed Server") if isinstance(info, dict) else getattr(info, "name", "Unnamed Server")
            players = [ros["display_string"] for ros in bs.get_game_roster()]
            start_new_thread(dump_mutual_servers, (players, server_name,))


def dump_mutual_servers(players, server_name):
    filePath = os.path.join(RecordFilesDir, "players.json")
    data = {}
    if os.path.isfile(filePath):
        try:
            with open(filePath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    for player in players:
        if player in data:
            if server_name not in data[player]:
                data[player].insert(0, server_name)
                data[player] = data[player][:3]
        else:
            data[player] = [server_name]
    try:
        with open(filePath, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass


mututalServerThread().run()


class customchatThread:
    def __init__(self):
        global cache_chat
        self.saved_msg = []
        try:
            for msg in bs.get_chat_messages():
                cache_chat.append(msg)
        except Exception:
            pass

    def run(self) -> None:
        self.timerr = babase.AppTimer(5.0, self.chatcheck, repeat=True)

    def chatcheck(self):
        global unmuted_names, cache_chat
        try:
            chats = bs.get_chat_messages()
        except Exception:
            chats = []
        try:
            temp_muted = babase.app.config.get('TempMuted', {})
            if isinstance(temp_muted, dict):
                now = time.time()
                expired = [k for k, v in temp_muted.items() if v <= now]
                if expired:
                    for k in expired:
                        del temp_muted[k]
                    babase.app.config['TempMuted'] = temp_muted
                    babase.app.config.commit()
        except Exception:
            temp_muted = {}
        for msg in chats:
            if msg not in cache_chat:
                sender = msg.split(":")[0]
                is_temp_muted = isinstance(temp_muted, dict) and sender in temp_muted
                is_chat_muted = sender in muted_chat_names
                if not is_temp_muted and not is_chat_muted:
                    if sender in unmuted_names:
                        bs.broadcastmessage(msg, color=(0.6, 0.9, 0.6))
                cache_chat.append(msg)
                if len(self.saved_msg) > 45:
                    cache_chat.pop(0)
            if not babase.app.config.resolve('Chat Muted'):
                self.timerr = None


def chatloggerstatus():
    return "Turn off Chat Logger" if chatlogger else "Turn on chat logger"


def _getTransText(text, isBaLstr=False, same_fb=False):
    global Current_Lang, Language_Texts
    if Current_Lang != 'English':
        Current_Lang = 'English'
        Language_Texts = {
            "Chinese": {},
            "English": {
                "Add_a_Quick_Reply": "Add a Quick Reply",
                "Admin_Command_Kick_Confirm": "Are you sure to use admin command to kick %s?",
                "Ban_For_%d_Seconds": "Ban for %d second(s).",
                "Ban_Time_Post": "Enter the time you want to ban(Seconds).",
                "Credits_for_This": "Credits & About",
                "Custom_Action": "Custom Action",
                "Debug_for_Host_Info": "Host Info Debug",
                "Kick_ID": "Kick ID:%d",
                "Mention_this_guy": "Mention this guy",
                "Modify_Main_Color": "Modify Main Color",
                "No_valid_player_found": "Can't find a valid player.",
                "No_valid_player_id_found": "Can't find a valid player ID.",
                "Normal_kick_confirm": "Are you sure to kick %s?",
                "Remove_a_Quick_Reply": "Remove a Quick Reply",
                "Send_%d_times": "Send for %d times",
                "Something_is_added": "'%s' is added.",
                "Something_is_removed": "'%s' is removed.",
                "Times": "Times",
                "Translator": "Translator",
                "chatloggeroff": "Turn off Chat Logger",
                "chatloggeron": "Turn on Chat Logger",
                "screenmsgoff": "Hide ScreenMessage",
                "screenmsgon": "Show ScreenMessage",
                "unmutethisguy": "unmute this guy",
                "mutethisguy": "mute this guy",
                "muteall": "Mute all",
                "unmuteall": "Unmute all",
                "copymsg": "Copy message",
                "reply": "Reply",
                "banthisguy": "Ban this guy",
                "mutethisguytemp": "Mute (temp)",
                "ban_duration_title": "Select Ban Duration",
                "mute_duration_title": "Select Mute Duration",
                "Ban_For_%d_Minutes": "Ban for %d minute(s).",
                "Mute_For_%d_Minutes": "Mute for %d minute(s).",
                "complaint": "Complaint",
                "complaint_window_title": "File a Complaint",
                "complaint_select_offender": "Select Offender",
                "complaint_description_hint": "Describe the offense...",
                "complaint_copy": "Copy Complaint",
                "complaint_copied": "Complaint copied!",
                "change_color": "Change Window Color",
                "mute_success": "Player muted for %d min(s).",
                "ban_success": "Player banned for %d min(s)."
            }
        }
        Language_Texts = Language_Texts.get(Current_Lang, {})
        try:
            from Language_Packs import ModifiedPartyWindow_LanguagePack as ext_lan_pack
            if isinstance(ext_lan_pack, dict) and isinstance(ext_lan_pack.get(Current_Lang), dict):
                for key, item in ext_lan_pack.get(Current_Lang).items():
                    Language_Texts[key] = item
        except Exception:
            pass

    res = Language_Texts.get(text, "#Unknown Text#" if not same_fb else text)
    return babase.Lstr(resource="??Unknown??", fallback_value=res) if isBaLstr else res


def _get_popup_window_scale() -> float:
    uiscale = bui.app.ui_v1.uiscale
    return (2.2 if uiscale is babase.UIScale.SMALL else 1.55 if uiscale is babase.UIScale.MEDIUM else 1.2)


def _creat_Lstr_list(string_list: list = []) -> list:
    return [babase.Lstr(resource="??Unknown??", fallback_value=item) for item in string_list]


customchatThread().run()


EMOJI_SCALES = {
    '\ue047': 1.08,
    '\ue046': 0.90,
    '\ue049': 0.62,
    '\ue02a': 0.72,
    '\ue048': 0.72,
    '\ue04f': 0.72,
    '\ue043': 0.76,
    '\ue027': 0.76,
    '\ue067': 0.76,
    '\ue01e': 0.80,
    '\ue01f': 0.80,
    '\ue028': 0.78,
    '\ue044': 0.78,
    '\ue045': 0.80,
    '\ue04a': 0.78,
    '\ue04d': 0.78,
    '\ue064': 0.80,
    '\ue065': 0.80,
}


def _sc_str(sc) -> str:
    """Resolve SpecialChar enum member to unicode character across API 9 & v1.8+."""
    try:
        if isinstance(sc.value, str):
            return sc.value
        return bui.charstr(sc)
    except Exception:
        return ''


def _get_categorized_special_chars() -> Dict[str, List[tuple]]:
    """Return all available BombSquad SpecialChars grouped into browsable categories."""
    all_items = []
    emblems = []
    flags = []
    gamepad = []

    flag_keywords = ('FLAG_',)
    gamepad_keywords = (
        'ARROW', 'BUTTON', 'DICE', 'DPAD', 'PLAY_', 'PAUSE', 'REWIND',
        'FAST_FORWARD', 'OUYA', 'PLAY_STATION', 'STEAM', 'DISCORD',
        'OCULUS', 'NVIDIA', 'GOOGLE_PLAY', 'GAME_CENTER', 'GAME_CIRCLE',
        'DELETE', 'SHIFT', 'BACK', 'POPUP_ICON',
    )
    skip_names = {'CLOSE'}

    seen_chars = set()
    try:
        members = list(bui.SpecialChar)
    except Exception:
        members = []

    for sc in members:
        name = getattr(sc, 'name', '')
        if name in skip_names:
            continue
        ch = _sc_str(sc)
        if not ch or ch in seen_chars:
            continue
        seen_chars.add(ch)
        label = name.replace('FLAG_', '').replace('_FULL', ' ★').replace('_', ' ').title()
        item = (ch, label, name)
        all_items.append(item)

        if any(k in name for k in flag_keywords):
            flags.append(item)
        elif any(k in name for k in gamepad_keywords):
            gamepad.append(item)
        else:
            emblems.append(item)

    return {
        'All': all_items,
        'Emblems': emblems,
        'Flags': flags,
        'Gamepad': gamepad,
    }


def get_emoji_scale(char: str) -> float:
    if char in EMOJI_SCALES:
        return EMOJI_SCALES[char]
    try:
        code = ord(char[0])
        if 0xE06B <= code <= 0xE0AA:
            return 0.72
        if 0xE02A <= code <= 0xE02F:
            return 0.70
        if (0xE032 <= code <= 0xE040) or (0xE050 <= code <= 0xE061):
            return 0.84
        if 0xE001 <= code <= 0xE01C:
            return 0.76
    except Exception:
        pass
    return 0.80


def _apw_compute_outline_color(color) -> tuple:
    """Compute cyber-glass neon outline color, optionally harmonized with party window color."""
    if not bool(babase.app.config.get('APW_Sync_Outline', True)):
        return (0.40, 1.00, 0.55)
    try:
        r, g, b = [max(0.0, min(1.0, float(v))) for v in color[:3]]
    except Exception:
        return (0.40, 1.00, 0.55)
    mx = max(r, g, b, 0.01)
    nr, ng, nb = r / mx, g / mx, b / mx
    return (
        min(1.0, nr * 0.62 + 0.34),
        min(1.0, ng * 0.62 + 0.34),
        min(1.0, nb * 0.62 + 0.34),
    )


def _apw_get_theme_colors():
    """Return (bg_color, dark_frame_color, neon_outline_color) from current theme config."""
    base = babase.app.config.get("PartyWindow_Main_Color", (0.25, 0.45, 0.35))
    if not isinstance(base, (list, tuple)) or len(base) != 3:
        base = (0.25, 0.45, 0.35)
    r, g, b = float(base[0]), float(base[1]), float(base[2])
    dark = (r * 0.14 + 0.03, g * 0.14 + 0.04, b * 0.14 + 0.06)
    ol = _apw_compute_outline_color(base)
    return base, dark, ol


def _draw_panel_bg(parent, x, y, w, h, color=(0.05, 0.07, 0.11), opacity=0.90):
    """Draw a full-bleed dark frosted backing panel that meets neon borders with zero edge gap."""
    return bui.imagewidget(
        parent=parent,
        size=(w, h),
        position=(x, y),
        texture=bui.gettexture('white'),
        opacity=opacity,
        color=color)


_apw_aid_cache: Dict[Any, str] = {}


def _apw_resolve_aid(client_id=None, v2_id=None, is_self=False) -> Optional[str]:
    """Resolve a player's verified BombSquad Account ID (a-... or pb-...) if exposed locally."""
    if is_self:
        try:
            plus = babase.app.plus
            if plus is not None and hasattr(plus, 'accounts') and getattr(plus.accounts, 'primary', None) is not None:
                aid = getattr(plus.accounts.primary, 'accountid', None)
                if aid:
                    return aid
        except Exception:
            pass
        try:
            classic = bui.app.classic
            if classic is not None and hasattr(classic, 'host_ui'):
                aid = classic.host_ui.get_client_account_id(-1)
                if aid:
                    return aid
        except Exception:
            pass

    if client_id is not None and client_id in _apw_aid_cache:
        return _apw_aid_cache[client_id]
    if v2_id and v2_id in _apw_aid_cache:
        return _apw_aid_cache[v2_id]

    try:
        classic = bui.app.classic
        if client_id is not None and classic is not None and hasattr(classic, 'host_ui'):
            aid = classic.host_ui.get_client_account_id(client_id)
            if aid:
                return aid
    except Exception:
        pass

    try:
        for entry in (bs.get_game_roster() or []):
            cid_match = (client_id is not None and entry.get('client_id') == client_id)
            tag_match = (v2_id is not None and entry.get('display_string') == v2_id)
            if cid_match or tag_match:
                aid = entry.get('account_id')
                if isinstance(aid, str) and (aid.startswith('a-') or aid.startswith('pb-')):
                    return aid
                spec_raw = entry.get('spec_string')
                if spec_raw:
                    try:
                        spec = json.loads(spec_raw)
                        sa = spec.get('a') or spec.get('account_id')
                        if isinstance(sa, str) and (sa.startswith('a-') or sa.startswith('pb-')):
                            return sa
                    except Exception:
                        pass
    except Exception:
        pass
    return None


_apw_docui_hooked = False
_apw_active_window_ref: Optional[weakref.ref] = None
_apw_session_chat_history: List[str] = []
_apw_last_bs_snapshot: List[str] = []


def _apw_sync_session_history(extra_msg: Optional[str] = None) -> List[str]:
    global _apw_last_bs_snapshot
    try:
        bs_msgs = list(bs.get_chat_messages() or [])
    except Exception:
        bs_msgs = []

    prev = _apw_last_bs_snapshot
    if bs_msgs != prev:
        if not prev:
            new_items = bs_msgs
        else:
            overlap = 0
            max_k = min(len(prev), len(bs_msgs))
            for k in range(max_k, 0, -1):
                if prev[-k:] == bs_msgs[:k]:
                    overlap = k
                    break
            new_items = bs_msgs[overlap:] if overlap > 0 else bs_msgs
        for m in new_items:
            if m:
                _apw_session_chat_history.append(m)
        _apw_last_bs_snapshot = bs_msgs

    if extra_msg and (not bs_msgs or bs_msgs[-1] != extra_msg):
        if not _apw_session_chat_history or _apw_session_chat_history[-1] != extra_msg:
            _apw_session_chat_history.append(extra_msg)

    if len(_apw_session_chat_history) > 250:
        del _apw_session_chat_history[:-250]
    return list(_apw_session_chat_history)


_APW_CHAT_ANIM_MODES = [
    ("scanner",  "⚡ Neon Scanner"),
    ("equalizer","🎵 Synth Equalizer"),
    ("wave",     "🌊 Pulse Wave"),
    ("spectrum", "🌈 Cyber Prism"),
    ("off",      "⬜ Off (Static)"),
]


def _apw_get_chat_anim_style() -> str:
    val = str(babase.app.config.get('APW_Chat_Anim_Style', 'scanner') or 'scanner')
    valid = {k for k, _ in _APW_CHAT_ANIM_MODES}
    return val if val in valid else 'scanner'


def _apw_should_show_update_banner() -> bool:
    return bool(
        _apw_update_state.get("available")
        and not _apw_update_state.get("dismissed_this_boot")
        and not _apw_update_state.get("installed_pending_restart")
    )


def _apw_show_header_players() -> bool:
    return bool(babase.app.config.get('APW_Show_Header_Players', False))


def _install_docui_and_account_theme():
    """Keep BombSquad DocUIWindow and AccountViewerWindow 100% native while
    passively sniffing Host DocUI ShowAccount AIDs when exposed."""
    global _apw_docui_hooked
    if _apw_docui_hooked:
        return
    _apw_docui_hooked = True

    try:
        import bauiv1lib.hostdocui as _hostdocui_mod
        from bacommon.docui.walk import page_actions
        _HostCtrl = _hostdocui_mod.HostDocUIController
        if not getattr(_HostCtrl, '_apw_aid_hooked', False):
            _orig_fulfill = _HostCtrl.fulfill_request

            def _sniffer_fulfill(self, request):
                resp = _orig_fulfill(self, request)
                try:
                    req_args = getattr(request, 'args', None)
                    if isinstance(req_args, dict) and hasattr(resp, 'page'):
                        cid = None
                        for k in ('id', 'client_id', 'clientid'):
                            if isinstance(req_args.get(k), int):
                                cid = req_args[k]
                                break
                        if cid is None:
                            for v in req_args.values():
                                if isinstance(v, int):
                                    cid = v
                                    break
                        if cid is not None:
                            for act in page_actions(resp.page):
                                if getattr(act, 'name', None) == 'show_account':
                                    args_d = getattr(act, 'args', None) or {}
                                    aid = args_d.get('a') or args_d.get('account_id')
                                    if isinstance(aid, str) and aid.startswith('a-'):
                                        _apw_aid_cache[cid] = aid
                                        break
                except Exception:
                    pass
                return resp

            _HostCtrl.fulfill_request = _sniffer_fulfill
            _HostCtrl._apw_aid_hooked = True
    except Exception:
        pass


def _draw_border(parent, x, y, w, h, color=(0.4, 1.0, 0.5), opacity=0.70, thickness=1.5, draw_controller=None):
    """Draws 4 edge lines forming a laser-sharp neon border outline."""
    t = thickness
    edges = [
        (x,         y + h - t, w,     t),
        (x,         y,         w,     t),
        (x,         y,         t,     h),
        (x + w - t, y,         t,     h),
    ]
    lines = []
    for rx, ry, rw, rh in edges:
        kw = {
            "parent": parent,
            "size": (rw, rh),
            "position": (rx, ry),
            "texture": bui.gettexture('white'),
            "opacity": opacity,
            "color": color,
        }
        if draw_controller is not None:
            kw["draw_controller"] = draw_controller
        lines.append(bui.imagewidget(**kw))
    return lines


def _draw_glass_textbox(parent, x, y, w, h, ol=(0.4, 1.0, 0.5),
                        text='', max_chars=120, description='',
                        opacity=0.78, border_opacity=0.60, border_thickness=1.1,
                        autoselect=True):
    """Draws a full-size Cyber-Glass editable textbox whose input rect matches its outline."""
    _draw_panel_bg(parent, x, y, w, h, color=(0.02, 0.04, 0.07), opacity=opacity)
    field = bui.textwidget(
        parent=parent,
        position=(x, y),
        size=(w, h),
        text=text,
        editable=True,
        autoselect=autoselect,
        max_chars=max_chars,
        maxwidth=max(20, w - 16),
        h_align='left',
        v_align='center',
        padding=4,
        flatness=1.0,
        shadow=0.3,
        scale=1.0,
        description=description)
    _draw_border(parent, x, y, w, h, color=ol, opacity=border_opacity, thickness=border_thickness)
    return field


def get_emoji_y_offset(char: str) -> float:
    """Pull superscript SpecialChar glyphs downward slightly so they sit vertically centered in tall boxes."""
    try:
        code = ord(char[0])
        if 0xE01D <= code <= 0xE06A:
            return -4.5
        if 0xE06B <= code <= 0xE0AA:
            return -1.0
    except Exception:
        pass
    return -1.5


class GlassButton:
    """A sleek translucent glass button with depth, subtle beveling,
    neon border framing, and full outline-sized click hitbox."""

    def __init__(self, parent, position, size, label='',
                 bg_color=(0.12, 0.16, 0.24), opacity=0.25,
                 text_color=(0.90, 0.95, 1.0), text_scale=0.7,
                 text_y_offset=0.0,
                 border=False, border_color=(0.4, 1.0, 0.5), border_opacity=0.70,
                 border_thickness=1.5,
                 on_activate_call=None):
        self.default_bg = bg_color
        self.default_opacity = opacity
        self.default_text_color = text_color
        self.position = position
        self.size = size
        self.border_lines = []
        self.border_thickness = border_thickness
        self.text_y_offset = text_y_offset

        w, h = size
        x, y = position

        is_col = False
        try:
            is_col = 'column' in str(type(parent)).lower()
        except Exception:
            pass

        if is_col:
            self._holder = bui.containerwidget(parent=parent, size=size, background=False)
            actual_parent = self._holder
            actual_pos = (0, 0)
        else:
            self._holder = None
            actual_parent = parent
            actual_pos = position

        ax, ay = actual_pos

        self.widget = bui.buttonwidget(
            parent=actual_parent,
            position=actual_pos,
            size=size,
            texture=bui.gettexture('empty'),
            label='',
            color=(1, 1, 1),
            autoselect=True,
            extra_touch_border_scale=0.0,
            on_activate_call=on_activate_call)

        self.shadow = bui.imagewidget(
            parent=actual_parent,
            size=(w, h),
            position=(ax, ay - 1),
            texture=bui.gettexture('softRect'),
            opacity=0.35,
            color=(0.0, 0.0, 0.0))

        self.bg = bui.imagewidget(
            parent=actual_parent,
            size=size,
            position=actual_pos,
            texture=bui.gettexture('softRect'),
            opacity=opacity,
            color=bg_color,
            draw_controller=self.widget)

        if border:
            self.border_lines = _draw_border(
                actual_parent, ax, ay, w, h,
                color=border_color, opacity=border_opacity, thickness=border_thickness,
                draw_controller=self.widget)

        safe_lbl = babase.Lstr(value=label) if (isinstance(label, str) and label.lstrip().startswith('{')) else label
        self.label_widget = bui.textwidget(
            parent=actual_parent,
            size=(0, 0),
            position=(ax + w * 0.5, ay + h * 0.5 + text_y_offset),
            text=safe_lbl,
            scale=text_scale,
            color=text_color,
            h_align='center',
            v_align='center',
            maxwidth=max(8, w - 6),
            draw_controller=self.widget)

    def set_color(self, bg_color=None, text_color=None, opacity=None):
        if bg_color is not None:
            self.default_bg = bg_color
            bui.imagewidget(edit=self.bg, color=bg_color)
        if opacity is not None:
            self.default_opacity = opacity
            bui.imagewidget(edit=self.bg, opacity=opacity)
        if text_color is not None:
            self.default_text_color = text_color
            bui.textwidget(edit=self.label_widget, color=text_color)

    def set_border_color(self, color=None, opacity=None):
        for line in self.border_lines:
            try:
                if color is not None:
                    bui.imagewidget(edit=line, color=color)
                if opacity is not None:
                    bui.imagewidget(edit=line, opacity=opacity)
            except Exception:
                pass

    def set_text(self, text):
        safe_txt = babase.Lstr(value=text) if (isinstance(text, str) and text.lstrip().startswith('{')) else text
        bui.textwidget(edit=self.label_widget, text=safe_txt)

    def set_on_activate(self, on_activate_call):
        bui.buttonwidget(edit=self.widget, on_activate_call=on_activate_call)

    def set_position(self, x, y):
        if self._holder is not None:
            return
        w, h = self.size
        t = self.border_thickness
        self.position = (x, y)
        bui.buttonwidget(edit=self.widget, position=(x, y))
        bui.imagewidget(edit=self.shadow, position=(x, y - 1))
        bui.imagewidget(edit=self.bg, position=(x, y))
        bui.textwidget(edit=self.label_widget, position=(x + w * 0.5, y + h * 0.5 + self.text_y_offset))
        if len(self.border_lines) == 4:
            bui.imagewidget(edit=self.border_lines[0], position=(x, y + h - t))
            bui.imagewidget(edit=self.border_lines[1], position=(x, y))
            bui.imagewidget(edit=self.border_lines[2], position=(x, y))
            bui.imagewidget(edit=self.border_lines[3], position=(x + w - t, y))

    def delete(self):
        if self._holder is not None:
            try:
                self._holder.delete()
                return
            except Exception:
                pass
        for line in self.border_lines:
            try:
                line.delete()
            except Exception:
                pass
        for w in (self.shadow, self.bg, self.label_widget, self.widget):
            try:
                w.delete()
            except Exception:
                pass


_APW_SORRY_WORDS = [
    "Sryyy", "Sorryy", "Sry", "Sowwy", "Forgive me",
]
_APW_SORRY_CONFESSIONS = [
    "My bad", "My fault", "My mistake", "My apologies", "Shouldn't have done that",
]
_APW_SORRY_ARGUMENTS = [
    "%, It's on me",
    "Ah! %!",
    "Ah, I slipped, %...",
    "Ah, % about that!",
    "Ah, $, %!",
    "A- I did that, $!",
    "$! Wasn't my intention!",
    "$, Forgive the error...!",
    "$!",
    "%, didn't mean to mess up!",
    "%, Totally $!",
    "Didn't mean to trouble, %",
]
_APW_SORRY_DELAY = 5.0
_apw_sorry_ready_at = 0.0


def _apw_random_sorry() -> str:
    return (
        random.choice(_APW_SORRY_ARGUMENTS)
        .replace('%', random.choice(_APW_SORRY_WORDS))
        .replace('$', random.choice(_APW_SORRY_CONFESSIONS))
    )


def _apw_get_muted_registry() -> Dict[str, Dict[str, str]]:
    raw = babase.app.config.get('APW_Chat_Muted', None)
    if isinstance(raw, dict):
        out: Dict[str, Dict[str, str]] = {}
        for k, v in raw.items():
            if isinstance(v, dict):
                out[str(k)] = {"v2": str(v.get("v2", k)), "aid": str(v.get("aid", ""))}
            else:
                out[str(k)] = {"v2": str(v or k), "aid": ""}
        return out
    return {}


def _apw_sync_muted_set_from_cfg() -> None:
    try:
        reg = _apw_get_muted_registry()
        for k, info in reg.items():
            v2 = info.get("v2") or k
            if v2:
                muted_chat_names.add(v2)
    except Exception:
        pass


def _apw_set_chat_muted(acc: str, muted: bool, client_id: Optional[int] = None) -> None:
    reg = _apw_get_muted_registry()
    clean_key = _apw_clean_name(acc) or acc
    if muted:
        muted_chat_names.add(acc)
        aid = ""
        try:
            aid = str(_apw_resolve_aid(client_id=client_id, v2_id=acc) or "")
        except Exception:
            aid = ""
        reg[clean_key] = {"v2": acc, "aid": aid}
    else:
        for item in list(muted_chat_names):
            if item == acc or _apw_clean_name(item) == clean_key:
                muted_chat_names.discard(item)
        reg.pop(clean_key, None)
        reg.pop(acc, None)
    cfg = babase.app.config
    cfg['APW_Chat_Muted'] = reg
    cfg.commit()


_APW_GREET_TRIGGERS = (
    "hi", "hii", "hiii", "hey", "heyy", "heya", "hai", "hoi",
    "hlo", "hei", "hello", "helo", "halo", "hallo", "hemlo",
    "hmlo", "ello", "hewwo", "hewo", "yo", "yow", "yoo",
    "wsp", "wsg", "sup", "greeting", "pagi", "siang", "sore", "malam",
)
_APW_GREET_REPLIES = [
    "Hoi", "Ello", "Hi There", "Heyy", "Hii", "Hello", "Yow", "Heya", "Hiee", "Hloo",
]
_APW_GREET_RE = re.compile(r'\b(' + '|'.join(_APW_GREET_TRIGGERS) + r')\b', re.IGNORECASE)

_apw_greet_state: Dict[str, Any] = {
    "server_key": "",
    "known_accounts": set(),
    "greeted_accounts": set(),
    "seeded": False,
    "last_msg": None,
    "reply_cooldown": {},
}


def _apw_clean_name(s: str) -> str:
    return re.sub(r'[\ue000-\uf8ff]', '', str(s or '')).strip()


def _apw_format_reply_prefix(raw_msg: str) -> str:
    parts = str(raw_msg or '').split(":", 1)
    sender = _apw_clean_name(parts[0]).strip(" '\"")
    if not sender:
        return ""
    body = _apw_clean_name(parts[1]).strip() if len(parts) > 1 else ""
    words = body.split()
    if not words:
        return f"@{sender} "
    snippet = " ".join(words[:4]) + ("...." if len(words) > 4 else "")
    return f'@{sender} "{snippet}" '


_APW_CHAT_PALETTE = [
    (0.45, 0.95, 1.00),
    (1.00, 0.85, 0.38),
    (0.55, 1.00, 0.62),
    (1.00, 0.58, 0.68),
    (0.76, 0.65, 1.00),
    (0.48, 0.78, 1.00),
    (1.00, 0.72, 0.44),
    (0.75, 1.00, 0.42),
    (1.00, 0.62, 0.92),
    (0.42, 1.00, 0.86),
    (0.98, 0.96, 0.52),
    (0.65, 0.72, 1.00),
]


def _apw_is_colorful_chat() -> bool:
    return bool(babase.app.config.get('APW_Colorful_Chat', False))


def _apw_get_chat_sender_color(msg: str, default_col=(0.90, 0.95, 1.00)) -> tuple:
    if ':' not in msg:
        return default_col
    sender_raw = msg.split(':', 1)[0]
    key = _apw_clean_name(sender_raw).strip(" '\"").lower()
    if not key:
        return default_col
    seed = int(babase.app.config.get('APW_Chat_Color_Seed', 1337) or 1337)
    idx = (zlib.crc32(key.encode('utf-8', 'ignore')) ^ seed) % len(_APW_CHAT_PALETTE)
    return _APW_CHAT_PALETTE[idx]


def _apw_get_roster_colors() -> tuple:
    cfg = babase.app.config
    p_col = cfg.get('APW_Roster_PlayerColor', (0.95, 0.97, 1.00))
    n_col = cfg.get('APW_Roster_NickColor', (0.40, 1.00, 0.80))
    if not (isinstance(p_col, (list, tuple)) and len(p_col) == 3):
        p_col = (0.95, 0.97, 1.00)
    if not (isinstance(n_col, (list, tuple)) and len(n_col) == 3):
        n_col = (0.40, 1.00, 0.80)
    return (tuple(p_col), tuple(n_col))


_APW_TRANSLATE_LANGS = [
    ("English", "en"),
    ("Arabic (العربية)", "ar"),
    ("Russian (Русский)", "ru"),
    ("Hindi (हिन्दी)", "hi"),
    ("Spanish (Español)", "es"),
    ("Indonesian (ID)", "id"),
    ("Urdu (اردو)", "ur"),
    ("Persian (فارسی)", "fa"),
    ("Bengali (বাংলা)", "bn"),
    ("French (Français)", "fr"),
    ("German (Deutsch)", "de"),
    ("Portuguese (PT)", "pt"),
    ("Turkish (Türkçe)", "tr"),
    ("Japanese (日本語)", "ja"),
    ("Korean (한국어)", "ko"),
    ("Chinese Simp (中文)", "zh-CN"),
    ("Chinese Trad (繁體)", "zh-TW"),
    ("Ukrainian (Українська)", "uk"),
    ("Italian (Italiano)", "it"),
    ("Vietnamese (Tiếng Việt)", "vi"),
    ("Thai (ไทย)", "th"),
    ("Polish (Polski)", "pl"),
    ("Dutch (Nederlands)", "nl"),
    ("Greek (Ελληνικά)", "el"),
    ("Hebrew (עברית)", "iw"),
    ("Tamil (தமிழ்)", "ta"),
    ("Telugu (తెలుగు)", "te"),
    ("Marathi (मराठी)", "mr"),
    ("Gujarati (ગુજરાતી)", "gu"),
    ("Punjabi (ਪੰਜਾਬੀ)", "pa"),
    ("Malayalam (മലയാളം)", "ml"),
    ("Kannada (ಕನ್ನಡ)", "kn"),
    ("Nepali (नेपाली)", "ne"),
    ("Sinhala (සිංහල)", "si"),
    ("Malay (Melayu)", "ms"),
    ("Filipino (Tagalog)", "tl"),
    ("Swahili (Kiswahili)", "sw"),
    ("Czech (Čeština)", "cs"),
    ("Romanian (Română)", "ro"),
    ("Hungarian (Magyar)", "hu"),
    ("Swedish (Svenska)", "sv"),
    ("Finnish (Suomi)", "fi"),
    ("Danish (Dansk)", "da"),
    ("Norwegian (Norsk)", "no"),
    ("Kazakh (Қазақша)", "kk"),
    ("Uzbek (Oʻzbek)", "uz"),
]

_APW_ROMANIZED_ITC_BY_LANG = {
    "hi": "hi-t-i0-und",
    "ar": "ar-t-i0-und",
    "ru": "ru-t-i0-und",
    "fa": "fa-t-i0-und",
    "ja": "ja-t-i0-und",
    "zh-CN": "zh-t-i0-pinyin",
    "zh": "zh-t-i0-pinyin",
    "bn": "bn-t-i0-und",
    "ur": "ur-t-i0-und",
    "ta": "ta-t-i0-und",
    "te": "te-t-i0-und",
    "mr": "mr-t-i0-und",
    "gu": "gu-t-i0-und",
    "pa": "pa-t-i0-und",
    "ml": "ml-t-i0-und",
    "kn": "kn-t-i0-und",
    "ne": "ne-t-i0-und",
    "or": "or-t-i0-und",
    "si": "si-t-i0-und",
    "th": "th-t-i0-und",
    "iw": "he-t-i0-und",
    "he": "he-t-i0-und",
    "el": "el-t-i0-und",
    "uk": "uk-t-i0-und",
    "sr": "sr-t-i0-und",
    "bg": "bg-t-i0-und",
    "be": "be-t-i0-und",
    "am": "am-t-i0-und",
}

_APW_ROMANIZED_PROFILES = [
    ("gu", "gu-t-i0-und", {
        "kem", "cho", "chho", "che", "chhe", "chu", "chhu", "su", "shu", "maja", "majama",
        "tame", "tamne", "mane", "tane", "hu", "hun", "ame", "apde", "aapde", "nathi",
        "avjo", "aavjo", "aavu", "aavo", "ramu", "ramye", "ramiye", "khabar", "saras",
        "saru", "ketla", "kyare", "kyan", "bahu", "bou", "thodu", "vadhu", "pachhi", "pachi",
        "bhaila", "bhaibandh", "karsu", "karu", "kare", "karyu", "hatu", "hati", "hata",
        "hoy", "thayu", "jaiye", "malye", "maliye", "chalse", "chaalse", "etle", "badhu",
        "kain", "kashu", "aaje", "kaale", "kale", "kemcho", "kemche", "ghare", "bol", "bolo",
        "chalo", "aave", "thay", "pan", "ane", "mate", "gando", "gandi", "dikra",
    }),
    ("ar", "ar-t-i0-und", {
        "salam", "salamo", "alaikom", "3alikom", "3aleikom", "ahlan", "ahla", "marhaba",
        "mar7aba", "kifak", "keefak", "kefak", "kifek", "keefek", "izzayak", "ezayak",
        "ezayyak", "3amel", "3amla", "eih", "shlonak", "shlonek", "shaku", "maku",
        "tamam", "kwayes", "kwayyes", "kwais", "zein", "zain", "helw", "7elw", "helwa",
        "7elwa", "habibi", "7abibi", "habibti", "7abibti", "habib", "akhi", "ya5i",
        "o5ti", "sa7bi", "sahbi", "shukran", "shokran", "yalla", "yala", "inshallah",
        "inshalla", "nshallah", "mashallah", "mashalla", "alhamdulillah", "al7amdulillah",
        "hamdullah", "subhanallah", "khalas", "mabsut", "mabsoot", "ana", "inta", "enti",
        "enta", "e7na", "ehna", "nahna", "howa", "heya", "homa", "lesh", "leish", "laish",
        "leh", "leih", "wein", "fein", "feen", "fen", "wen", "fain", "sabah", "sabaho",
        "masa", "masaa", "aywa", "aiwa", "mamnoon", "kalam", "tayeb", "tayyib", "wallah",
        "wallahi", "yaani", "ya3ni", "yani", "mish", "mesh", "mush", "mafish", "mafeesh",
        "mafesh", "mafi", "moshkela", "moshkila", "mushkila", "mumtaz", "kbeer", "sagheer",
        "shabab", "khoya", "keda", "kida", "hek", "haik", "heik", "dilwa2ti", "delwa2ti",
        "hassa", "hala2", "ba3den", "ba3dain", "bukra", "bokra", "sawa", "ta3al", "ta3ala",
        "emshi", "imshi", "ro7", "roo7", "estanna", "stanna", "shoof", "shouf", "shuf",
        "nel3ab", "al3ab", "la3ba", "le3ba", "faiz", "fayez", "khaser", "khasran",
        "kheer", "kheir", "kher", "kteer", "ktir", "ketir", "awi", "2awi", "shway",
        "shwaya", "shweya", "biddi", "badi", "3ayez", "3ayza", "ayez", "lazem", "laazem",
        "momken", "mumkin", "akeed", "akid", "tab3an", "gamed", "jamil", "gamil",
        "2albi", "albi", "galbi", "ro7i", "sa7", "ghalat", "mabrook", "mabruk", "shu", "sho",
    }),
    ("hi", "hi-t-i0-und", {
        "hai", "hain", "kya", "kaise", "kaisa", "kaisi", "bhai", "yaar", "nahi", "nhi",
        "haan", "hn", "aaja", "aao", "jao", "karo", "karna", "raha", "rahi", "rahe",
        "mera", "tera", "meri", "teri", "humko", "tumko", "aap", "tum", "hum", "kuch", "sabko",
        "bhi", "toh", "mat", "abhi", "jaldi", "ruk", "khel", "khelna", "khele", "khelte",
        "jeet", "haar", "pata", "samajh", "bol", "baat", "accha", "acha", "theek",
        "thik", "badiya", "mast", "bekar", "pagal", "saale", "kahan", "kidhar", "idhar",
        "udhar", "kyun", "kyu", "kab", "kaun", "kitna", "bahut", "bohot", "thoda", "zyada",
        "gaya", "gayi", "gaye", "diya", "liya", "hua", "hui", "hoga", "hogi", "honge",
        "chahiye", "sakta", "dekh", "dekho", "sun", "suno", "maar", "maaro", "bhag",
        "bhago", "nikal", "band", "chalu", "shuru", "khatam", "bilkul", "sach", "jhooth",
        "mazak", "abe", "oye", "yr", "wala", "wali", "wale", "lagta", "chup",
    }),
    ("ur", "ur-t-i0-und", {
        "shukriya", "meherbani", "khuda", "hafiz", "khudahafiz", "assalamualaikum",
        "walekum", "waqt", "waqai", "zindagi", "duniya", "mohabbat", "madad", "huzoor",
        "janaab", "janab", "jazakallah", "khairiyat", "mizaj", "tashreef", "farmaiye",
    }),
    ("mr", "mr-t-i0-und", {
        "kasa", "kashi", "kay", "aahe", "aahes", "aahet", "mala", "tula", "amhi",
        "tumhi", "kheluya", "chala", "jhala", "jhale", "bhava", "bhau", "mitra",
        "kuthe", "kevha", "bara", "chan", "chhan", "nako", "houde", "sang", "sanga",
    }),
    ("pa", "pa-t-i0-und", {
        "haiga", "haige", "haigi", "veere", "veer", "paaji", "paji", "pajji",
        "satsriakal", "changa", "vadiya", "wadhiya", "tussi", "tusi", "assi",
        "mainu", "tenu", "kiddan", "kida", "kidda", "ohnu", "chakk", "khedna", "khed",
    }),
    ("te", "te-t-i0-und", {
        "unnav", "unnaru", "unnavu", "unna", "bagunnava", "bagunna", "enti", "cheppu",
        "randi", "velli", "manchidi", "nenu", "nuvvu", "meeru", "ekkadiki", "ekkada",
        "annaya", "thammudu", "ela", "emi", "aadudam", "bavundi",
    }),
    ("ml", "ml-t-i0-und", {
        "sukhamano", "sukham", "enthu", "vishesham", "evide", "njan", "nee", "ningal",
        "chetta", "chechi", "aliyan", "machane", "mwone", "mone", "adipoli", "pwoli",
        "kollam", "kollaam", "ariyilla", "nanni", "entha", "enthaanu", "poyi", "varu",
        "kalikkam", "enda", "machan", "sugham",
    }),
    ("kn", "kn-t-i0-und", {
        "hegiddiya", "hegiddira", "chennagide", "chennagiddini", "naanu", "neenu", "yelli",
        "elli", "macha", "magane", "gottilla", "baro", "banni", "hogo", "hogona",
        "aadu", "aadona", "yenu", "enu", "dhanyavada", "sakkath", "chindi", "maga",
    }),
    ("ne", "ne-t-i0-und", {
        "kasto", "chha", "chhau", "chhu", "sanchai", "thikai", "tapai", "timi", "hami",
        "kaha", "kahan", "kati", "kina", "khelne", "khelau", "daju", "sathi", "ramro",
        "dhanyabad", "thahachaina", "huncha", "hoina", "gardai", "namaste",
    }),
    ("bn", "bn-t-i0-und", {
        "kemon", "acho", "achi", "bhalo", "valobashi", "nomoshkar", "dhonnobad",
        "kothay", "tumi", "korcho", "bhaijan", "khub", "sundor", "khelbo", "cholo",
    }),
    ("ta", "ta-t-i0-und", {
        "vanakkam", "eppadi", "irukkeenga", "irukka", "nandri", "nalla", "machan",
        "machi", "thambi", "enna", "pannura", "vaanga", "ponga", "sollu", "theriyala",
    }),
    ("si", "si-t-i0-und", {
        "ayubowan", "kohomada", "sthuthi", "istuti", "hondai", "machan", "yaluwa",
        "mokada", "koheda", "ennako", "palayan", "sellam", "karamu",
    }),
    ("or", "or-t-i0-und", {
        "namaskar", "kemiti", "achanti", "acha", "bhala", "bhal", "dhanyabad",
        "kouthi", "kaha", "kheliba", "bhaina",
    }),
    ("th", "th-t-i0-und", {
        "sawadee", "sawasdee", "khap", "khrap", "krup", "kha", "sabai", "sabaidee",
        "khop", "khun", "khob", "chai", "mai", "jing", "len", "aroi", "sanuk",
    }),
    ("iw", "he-t-i0-und", {
        "shalom", "nishma", "toda", "raba", "sababa", "yofi", "achla", "ken",
        "boker", "tov", "erev", "laila", "slicha", "chaver", "achi", "efo",
    }),
    ("el", "el-t-i0-und", {
        "kalimera", "kalispera", "kalinichta", "geia", "efharisto", "efxaristo",
        "parakalo", "kaneis", "kanis", "kala", "eimai", "pame", "file", "aderfe",
        "ochi", "tipota", "oraia", "wraia", "malaka",
    }),
    ("ru", "ru-t-i0-und", {
        "privet", "kak", "dela", "spasibo", "brat", "bratan", "chto", "delaesh", "horosho",
        "khorosho", "davai", "davay", "pochemu", "poka", "zdravstvuy", "ponyal", "ladno",
        "kruto", "zachem", "kuda", "kogda", "tebya", "menya", "ochen", "bystro", "igra",
        "igrat", "pobeda", "pozhaluysta", "izvini", "drug", "molodets", "konechno", "nikak",
    }),
    ("uk", "uk-t-i0-und", {
        "pryvit", "yak", "spravy", "dyakuyu", "dobre", "budlaska", "tse", "shcho",
        "chomu", "kudy", "koli", "mene", "tebe", "druze", "brate", "hrayemo",
        "hraty", "peremoha", "garazd", "harazd",
    }),
    ("sr", "sr-t-i0-und", {
        "zdravo", "kako", "brate", "hvala", "dobro", "izvini", "hajde", "igraj",
        "pobeda", "gde", "zasto", "super", "druze", "molim", "nema", "problema",
    }),
    ("bg", "bg-t-i0-und", {
        "zdravei", "zdravey", "kak", "si", "blagodarya", "mersi", "dobre", "bratle",
        "priyatel", "hajde", "igraem", "pobeda", "kade", "zashto",
    }),
    ("be", "be-t-i0-und", {
        "pryvit", "pryvitannie", "dzyakuy", "dobra", "kali", "laska", "syabra", "gulnya",
    }),
    ("fa", "fa-t-i0-und", {
        "chetori", "khobi", "khoobi", "dadash", "khodahafez", "chera",
        "koja", "hastam", "hasti", "kheili", "khosh", "befarma", "farda", "emrooz",
        "raftam", "oomadam", "azizam", "khaste", "chetor", "kojaei", "mersi",
    }),
    ("am", "am-t-i0-und", {
        "selam", "endemin", "indemin", "dehna", "ameseginalehu", "wendime", "wendim",
        "betam", "konjo", "eshi", "ishi", "yene", "aydelem",
    }),
    ("ja", "ja-t-i0-und", {
        "ohayou", "konnichiwa", "konbanwa", "arigatou", "arigato", "sumimasen", "gomen",
        "gomenasai", "genki", "desu", "nani", "sugoi", "kawaii", "sayonara",
        "onegaishimasu", "wakarimasen", "yatta", "daijoubu", "tomodachi", "yoroshiku",
    }),
    ("zh-CN", "zh-t-i0-pinyin", {
        "nihao", "xiexie", "zaijian", "shenme", "weishenme", "duibuqi", "meiguanxi",
        "jiayou", "pengyou", "laoshi", "xihuan", "zenme", "bukeqi",
    }),
]
_APW_GU_CASUAL_MAP = {
    "cho": "chho",
    "che": "chhe",
    "chu": "chhu",
    "su": "shu",
    "pachi": "pachhi",
    "kemcho": "kem chho",
    "kemche": "kem chhe",
    "majama": "maja ma",
}
_APW_ARABIZI_IGNORE = {"v2", "2d", "3d", "4k", "h2o", "b2b", "ps3", "ps4", "ps5", "mp3", "mp4", "m4a"}
_apw_translate_cache: Dict[tuple, str] = {}


def _apw_get_translate_cfg() -> Dict[str, Any]:
    cfg = babase.app.config
    tl = str(cfg.get('APW_Translate_Lang', 'en') or 'en').strip() or 'en'
    sl = str(cfg.get('APW_Translate_Source', 'auto') or 'auto').strip() or 'auto'
    return {
        "enabled": bool(cfg.get('APW_AutoTranslate_Chat', False)),
        "tl": tl,
        "sl": sl,
        "romanized": bool(cfg.get('APW_Translate_Romanized', cfg.get('APW_Translate_Hinglish', True))),
    }


def _apw_get_lang_label(code: str) -> str:
    if code == 'auto':
        return 'Auto-Detect (All)'
    for lname, lcode in _APW_TRANSLATE_LANGS:
        if lcode.lower() == code.lower():
            return f"{lname} [{lcode}]"
    return f"Custom [{code}]"


def _apw_prepare_romanized_text(text: str, lang_code: str) -> str:
    """Normalize casual phonetic Romanized spellings before Google Input Tools."""
    if lang_code != "gu":
        return text
    out = []
    for tok in re.split(r"(\s+)", text):
        if tok.isspace() or not tok:
            out.append(tok)
        else:
            m = re.match(r"^([^a-zA-Z0-9]*)([a-zA-Z0-9]+)([^a-zA-Z0-9]*)$", tok)
            if m and m.group(2).lower() in _APW_GU_CASUAL_MAP:
                out.append(f"{m.group(1)}{_APW_GU_CASUAL_MAP[m.group(2).lower()]}{m.group(3)}")
            else:
                out.append(tok)
    return "".join(out)


def _apw_score_romanized_profiles(text: str, exclude_lang: Optional[str] = None) -> List[tuple]:
    tokens = re.findall(r"[0-9a-zA-Z]+", text.lower())
    if not tokens:
        return []
    arabizi_digits = sum(
        1 for w in tokens
        if w not in _APW_ARABIZI_IGNORE
        and re.search(r"(?:^[235789][a-z]{2,}|[a-z]+[235789][a-z]+|[a-z]{2,}[2357]$)", w)
    )
    scored = []
    for lang_code, itc, vocab in _APW_ROMANIZED_PROFILES:
        if exclude_lang and lang_code == exclude_lang:
            continue
        hits = sum(1 for w in tokens if w in vocab)
        if lang_code == "ar":
            hits += arabizi_digits
        if hits > 0:
            scored.append((hits, lang_code, itc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored


def _apw_detect_romanized_profile(text: str) -> Optional[tuple]:
    """Detect non-Latin languages written in English letters (Gujarati, Arabizi, Hinglish, RU Translit, etc.)."""
    tokens = re.findall(r"[0-9a-zA-Z]+", text.lower())
    scored = _apw_score_romanized_profiles(text)
    if not scored:
        return None
    best_hits, lang_code, itc = scored[0]
    if best_hits >= 2 or (best_hits == 1 and len(tokens) <= 4):
        return (lang_code, itc)
    return None


def _apw_gtrans_raw(text: str, sl: str, tl: str) -> tuple:
    url = 'https://translate.googleapis.com/translate_a/single?' + urllib.parse.urlencode({
        'client': 'gtx', 'sl': sl, 'tl': tl, 'dt': 't', 'q': text,
    })
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    out = ''.join(seg[0] for seg in (data[0] or []) if seg and seg[0])
    src = data[2] if len(data) > 2 else sl
    return out.strip(), str(src or sl)


def _apw_translit_itc(text: str, itc: str) -> str:
    url = 'https://inputtools.google.com/request?' + urllib.parse.urlencode({
        'text': text, 'itc': itc, 'num': 1, 'cp': 0, 'cs': 1,
        'ie': 'utf-8', 'oe': 'utf-8', 'app': 'demopage',
    })
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    if isinstance(data, list) and len(data) > 1 and data[0] == 'SUCCESS':
        parts = [item[1][0] for item in data[1] if isinstance(item, list) and len(item) > 1 and item[1]]
        if parts:
            return ' '.join(parts)
    return text


def _apw_translit_and_translate(clean: str, src_lang: str, tl: str) -> Optional[str]:
    itc = _APW_ROMANIZED_ITC_BY_LANG.get(src_lang)
    if not itc:
        return None
    prep_txt = _apw_prepare_romanized_text(clean, src_lang)
    native_txt = _apw_translit_itc(prep_txt, itc)
    if tl == src_lang:
        return native_txt
    tr_lang = "iw" if src_lang == "he" else src_lang
    tr_txt, _ = _apw_gtrans_raw(native_txt, tr_lang, tl)
    return tr_txt or None


def _apw_translate_sync(text: str, tl: str, sl: str = 'auto', romanized: bool = True) -> str:
    clean = _apw_clean_name(text).strip()
    if not clean:
        return text
    key = (clean, sl, tl, romanized)
    if key in _apw_translate_cache:
        return _apw_translate_cache[key]

    try:
        if sl != 'auto' and romanized and clean.isascii() and sl in _APW_ROMANIZED_ITC_BY_LANG:
            tr_forced = _apw_translit_and_translate(clean, sl, tl)
            if tr_forced:
                _apw_translate_cache[key] = tr_forced
                return tr_forced

        if sl == 'auto' and romanized and clean.isascii():
            prof = _apw_detect_romanized_profile(clean)
            if prof is not None:
                p_lang, _ = prof
                tr_rom = _apw_translit_and_translate(clean, p_lang, tl)
                if tr_rom:
                    _apw_translate_cache[key] = tr_rom
                    return tr_rom

        translated, detected_src = _apw_gtrans_raw(clean, sl, tl)

        if sl == 'auto' and romanized and clean.isascii():
            c_toks = re.findall(r"[a-zA-Z0-9]+", clean.lower())
            t_toks = set(re.findall(r"[a-zA-Z0-9]+", (translated or "").lower()))
            unchanged_ratio = (sum(1 for w in c_toks if w in t_toks) / len(c_toks)) if c_toks else 1.0

            if unchanged_ratio >= 0.45 or detected_src == tl:
                if detected_src and detected_src != tl and detected_src in _APW_ROMANIZED_ITC_BY_LANG:
                    tr_det = _apw_translit_and_translate(clean, detected_src, tl)
                    if tr_det and tr_det.lower() != clean.lower():
                        translated = tr_det
                        t_toks = set(re.findall(r"[a-zA-Z0-9]+", translated.lower()))
                        unchanged_ratio = (sum(1 for w in c_toks if w in t_toks) / len(c_toks)) if c_toks else 1.0

                if unchanged_ratio >= 0.55 or translated.lower() == clean.lower():
                    scored = _apw_score_romanized_profiles(clean, exclude_lang=tl)
                    if scored:
                        _, p_lang, _ = scored[0]
                        tr2 = _apw_translit_and_translate(clean, p_lang, tl)
                        if tr2 and tr2.lower() != clean.lower():
                            translated = tr2

        result = translated or text
        _apw_translate_cache[key] = result
        return result
    except Exception:
        return text


def _apw_translate_async(text: str, callback) -> None:
    tcfg = _apw_get_translate_cfg()
    tl = tcfg["tl"]
    sl = tcfg["sl"]
    romanized = tcfg["romanized"]
    clean = _apw_clean_name(text).strip()
    if not clean:
        return
    cached = _apw_translate_cache.get((clean, sl, tl, romanized))
    if cached is not None:
        callback(cached)
        return

    def _worker():
        res = _apw_translate_sync(clean, tl, sl=sl, romanized=romanized)
        try:
            _babase.pushcall(babase.CallPartial(callback, res), from_other_thread=True)
        except Exception:
            pass

    start_new_thread(_worker, ())


def _apw_get_autogreet_players() -> Dict[str, Dict[str, str]]:
    """Return {aid_or_key: {'v2': v2_tag, 'aid': aid_str}} for auto-greeted players."""
    raw = babase.app.config.get('APW_AutoGreet_Players', None)
    if not isinstance(raw, dict):
        return {}
    out: Dict[str, Dict[str, str]] = {}
    for k, v in raw.items():
        if isinstance(v, dict):
            v2 = str(v.get("v2") or k).strip()
            aid = str(v.get("aid") or k).strip()
            out[str(k)] = {"v2": v2, "aid": aid}
        elif v:
            out[str(k)] = {"v2": str(v), "aid": str(k)}
    return out


def _apw_save_autogreet_players(players_map: Dict[str, Dict[str, str]]) -> None:
    cfg = babase.app.config
    cfg['APW_AutoGreet_Players'] = dict(players_map)
    cfg.commit()


def _apw_find_autogreet_key(aid: str, v2_tag: str, ag_map: Dict[str, Dict[str, str]]) -> Optional[str]:
    if aid and aid in ag_map:
        return aid
    if v2_tag and v2_tag in ag_map:
        return v2_tag
    v2_clean = _apw_clean_name(v2_tag).lower()
    for k, info in ag_map.items():
        if v2_tag and info.get("v2") == v2_tag:
            return k
        if aid and info.get("aid") == aid:
            return k
        if v2_clean and _apw_clean_name(info.get("v2", "")).lower() == v2_clean:
            return k
    return None


def _apw_get_autogreet_cfg() -> Dict[str, Any]:
    cfg = babase.app.config
    join_mode = str(cfg.get('APW_AutoGreet_JoinMode', 'list')).lower()
    if join_mode == 'friends':
        join_mode = 'list'
    if join_mode not in ('list', 'all', 'off'):
        join_mode = 'list'
    return {
        "enabled": bool(cfg.get('APW_AutoGreet_Enabled', True)),
        "chat_reply": bool(cfg.get('APW_AutoGreet_Chat', True)),
        "join_mode": join_mode,
        "join_msg": str(cfg.get('APW_AutoGreet_Message', 'Hey {name}, welcome!') or 'Hey {name}, welcome!'),
        "reply_msg": str(cfg.get('APW_AutoGreet_Reply', 'Hey {name}!') or 'Hey {name}!'),
        "nicks": str(cfg.get('APW_AutoGreet_Nicks', '') or ''),
    }


def _apw_format_greet_msg(template: str, disp_name: str, v2_tag: str) -> str:
    t = (template or '').strip()
    if not t:
        t = f"{random.choice(_APW_GREET_REPLIES)} {{name}}!"
    return t.replace('{name}', disp_name).replace('$name', disp_name).replace('{acc}', v2_tag).replace('$acc', v2_tag)


def _apw_get_my_account() -> str:
    try:
        if babase.app.plus is not None:
            return str(babase.app.plus.get_v1_account_display_string() or '').strip()
    except Exception:
        pass
    return ''


def _apw_send_delayed_greet(msg_text: str, acc_key: str, expected_server: str) -> None:
    try:
        if _apw_greet_state.get("server_key") != expected_server:
            return
        roster = bs.get_game_roster() or []
        if not roster:
            return
        bs.chatmessage(msg_text)
        if acc_key:
            _apw_greet_state["greeted_accounts"].add(acc_key)
        bui.screenmessage(f"Auto Greeted: {acc_key}", color=(0.45, 0.95, 0.72))
    except Exception:
        pass


def _apw_autogreet_tick() -> None:
    try:
        roster = bs.get_game_roster() or []
        msgs = bs.get_chat_messages() or []
        info = bs.get_connection_to_host_info_2()
        if isinstance(info, dict):
            sname = str(info.get('name', '') or '')
            saddr = str(info.get('address', '') or '')
        else:
            sname = str(getattr(info, 'name', '') or '') if info else ''
            saddr = str(getattr(info, 'address', '') or '') if info else ''
        server_key = f"{sname}|{saddr}" if (roster or sname) else ""

        if not roster or server_key != _apw_greet_state["server_key"]:
            if server_key != _apw_greet_state["server_key"]:
                _apw_session_chat_history.clear()
                _apw_last_bs_snapshot.clear()
            _apw_greet_state["server_key"] = server_key
            _apw_greet_state["known_accounts"].clear()
            _apw_greet_state["greeted_accounts"].clear()
            _apw_greet_state["reply_cooldown"].clear()
            _apw_greet_state["seeded"] = False
            _apw_greet_state["last_msg"] = msgs[-1] if msgs else None
            _apw_sync_session_history()
            return

        _apw_sync_session_history()
        cfg = _apw_get_autogreet_cfg()
        if not cfg["enabled"]:
            _apw_greet_state["last_msg"] = msgs[-1] if msgs else _apw_greet_state["last_msg"]
            for r in roster:
                acc = str(r.get("display_string") or "").strip()
                if acc:
                    _apw_greet_state["known_accounts"].add(acc)
            return

        my_acc = _apw_get_my_account()
        my_clean = _apw_clean_name(my_acc).lower()

        ag_players = _apw_get_autogreet_players()
        ag_updated = False

        join_mode = cfg["join_mode"]
        if join_mode in ('list', 'all'):
            greet_queue = []
            first_scan = not _apw_greet_state["seeded"]
            for r in roster:
                acc = str(r.get("display_string") or "").strip()
                if not acc:
                    continue
                cid = r.get("client_id", -1)
                aid = ""
                try:
                    aid = str(_apw_resolve_aid(client_id=cid, v2_id=acc, is_self=(cid == -1)) or "").strip()
                except Exception:
                    aid = ""

                matched_key = _apw_find_autogreet_key(aid, acc, ag_players)
                if matched_key is not None and acc and ag_players[matched_key].get("v2") != acc:
                    ag_players[matched_key]["v2"] = acc
                    ag_updated = True

                is_new = acc not in _apw_greet_state["known_accounts"]
                _apw_greet_state["known_accounts"].add(acc)

                if not is_new:
                    continue
                if acc == my_acc or _apw_clean_name(acc).lower() == my_clean:
                    continue
                if acc in muted_chat_names or acc in _apw_greet_state["greeted_accounts"]:
                    continue

                is_listed = matched_key is not None
                if first_scan:
                    if join_mode == 'list' and is_listed and len(greet_queue) < 2:
                        greet_queue.append((r, acc))
                else:
                    if join_mode == 'all' or is_listed:
                        greet_queue.append((r, acc))

            if ag_updated:
                _apw_save_autogreet_players(ag_players)

            _apw_greet_state["seeded"] = True
            for i, (r_entry, acc) in enumerate(greet_queue):
                players = r_entry.get("players") or []
                pname = ""
                if players and isinstance(players, list):
                    pname = str(players[0].get("name_full") or players[0].get("name") or "").strip()
                disp = _apw_clean_name(pname or acc) or acc
                _apw_greet_state["greeted_accounts"].add(acc)
                msg_out = _apw_format_greet_msg(cfg["join_msg"], disp, acc)
                babase.apptimer(
                    1.6 + i * 1.1 + random.uniform(0.0, 0.4),
                    babase.CallPartial(_apw_send_delayed_greet, msg_out, acc, server_key),
                )
        else:
            for r in roster:
                acc = str(r.get("display_string") or "").strip()
                if acc:
                    _apw_greet_state["known_accounts"].add(acc)
            _apw_greet_state["seeded"] = True

        if cfg["chat_reply"] and msgs:
            last_seen = _apw_greet_state["last_msg"]
            if last_seen is None:
                _apw_greet_state["last_msg"] = msgs[-1]
                return

            new_msgs = []
            if last_seen in msgs:
                idx = len(msgs) - 1 - msgs[::-1].index(last_seen)
                new_msgs = msgs[idx + 1:]
            else:
                new_msgs = msgs[-2:]
            _apw_greet_state["last_msg"] = msgs[-1]

            my_triggers = set()
            if my_clean:
                my_triggers.add(my_clean)
                first_tok = my_clean.split()[0]
                if len(first_tok) >= 3:
                    my_triggers.add(first_tok)
            for r in roster:
                acc = str(r.get("display_string") or "").strip()
                if acc == my_acc:
                    for p in (r.get("players") or []):
                        pn = _apw_clean_name(p.get("name_full") or p.get("name") or "").lower()
                        if len(pn) >= 3:
                            my_triggers.add(pn)
            for tok in cfg["nicks"].split(','):
                tk = tok.strip().lower()
                if len(tk) >= 2:
                    my_triggers.add(tk)

            now = time.monotonic()
            for raw_m in new_msgs[-3:]:
                if ':' not in raw_m:
                    continue
                sender_raw, body_raw = raw_m.split(':', 1)
                sender_clean = _apw_clean_name(sender_raw).strip(" '\"")
                sender_key = sender_clean.lower()
                if not sender_key or sender_key == my_clean:
                    continue
                if any(_apw_clean_name(m).lower() == sender_key for m in muted_chat_names):
                    continue
                if now < _apw_greet_state["reply_cooldown"].get(sender_key, 0.0):
                    continue

                body_clean = _apw_clean_name(body_raw).lower()
                if not _APW_GREET_RE.search(body_clean):
                    continue
                if not any(re.search(r'\b' + re.escape(tr) + r'\b', body_clean) for tr in my_triggers):
                    continue

                _apw_greet_state["reply_cooldown"][sender_key] = now + 15.0
                reply_out = _apw_format_greet_msg(cfg["reply_msg"], sender_clean, sender_clean)
                babase.apptimer(
                    1.2 + random.uniform(0.1, 0.6),
                    babase.CallPartial(_apw_send_delayed_greet, reply_out, sender_clean, server_key),
                )
    except Exception:
        pass


def _apw_bg_daemon_tick() -> None:
    _apw_autogreet_tick()
    _apw_chatlog_tick()


class AlphaPopupMenu:
    def __init__(self, position=(0.0, 0.0), choices=None, choices_display=None, current_choice='', delegate=None, scale=None):
        uiscale = bui.app.ui_v1.uiscale
        if scale is None:
            scale = _get_popup_window_scale()

        choices = choices or []
        choices_display = choices_display or []
        self._delegate_ref = weakref.ref(delegate) if delegate is not None else None

        item_h   = 34
        visible  = 6
        pad      = 8

        eval_labels = [
            disp.evaluate() if isinstance(disp, babase.Lstr) else str(disp if disp else ch)
            for ch, disp in zip(choices, choices_display)
        ]
        max_lbl_w = 0.0
        for lbl in eval_labels:
            try:
                w_px = float(bui.get_string_width(lbl, suppress_warning=True)) * 0.68 if lbl.isascii() else len(lbl) * 9.8
            except Exception:
                w_px = len(lbl) * 9.8
            if w_px > max_lbl_w:
                max_lbl_w = w_px

        c_width  = min(420, max(250, int(max_lbl_w) + 52))
        list_h   = min(len(choices), visible) * item_h
        c_height = list_h + pad * 2

        self.root_widget = cnt = bui.containerwidget(
            scale=scale, size=(0, 0), transition='in_scale',
            background=False,
            color=(0, 0, 0), parent=bui.get_special_widget('overlay_stack'))

        _draw_panel_bg(
            parent=cnt,
            x=-c_width * 0.5, y=-c_height * 0.5,
            w=c_width, h=c_height,
            color=(0.05, 0.07, 0.11), opacity=0.94)

        _, _, _ol = _apw_get_theme_colors()
        _draw_border(
            parent=cnt,
            x=-c_width * 0.5, y=-c_height * 0.5,
            w=c_width, h=c_height,
            color=_ol, opacity=0.80, thickness=1.5)

        scroll = bui.scrollwidget(
            parent=cnt, size=(c_width - 8, list_h),
            position=(4 - c_width * 0.5, pad - c_height * 0.5),
            color=(0, 0, 0), simple_culling_v=10)

        col = bui.columnwidget(parent=scroll, border=0, margin=0)

        def _make_cb(ch):
            def _cb():
                bui.containerwidget(edit=cnt, transition='out_scale')
                dlg = self._delegate_ref() if self._delegate_ref is not None else None
                if dlg is not None:
                    dlg.popup_menu_selected_choice(self, ch)
            return _cb

        for ch, label in zip(choices, eval_labels):
            is_curr = (ch == current_choice)
            row = bui.containerwidget(parent=col, size=(c_width - 12, item_h), background=False)
            bui.imagewidget(
                parent=row, size=(c_width - 12, item_h - 2), position=(0, 1),
                texture=bui.gettexture('softRect'),
                opacity=0.35 if is_curr else 0.14,
                color=(0.20, 0.45, 0.70) if is_curr else (0.10, 0.12, 0.16))
            bui.textwidget(
                parent=row, size=(c_width - 12, item_h - 2), position=(0, 1),
                text=babase.Lstr(value=label), scale=0.66, maxwidth=c_width - 28,
                color=(1.0, 0.95, 0.4) if is_curr else (0.9, 0.95, 1.0),
                h_align='center', v_align='center',
                selectable=True, autoselect=True, click_activate=True,
                on_activate_call=_make_cb(ch))

        bui.containerwidget(edit=cnt, on_outside_click_call=babase.CallPartial(bui.containerwidget, edit=cnt, transition='out_scale'))


class AlphaPartyWindow(bui.Window):
    def __init__(self, *, origin: Sequence[float] = (0, 0)):
        global _apw_active_window_ref
        self._uiopenstate = bui.UIOpenState('classicparty')
        self._r = 'partyWindow'
        self.msg_user_selected = ''
        self._popup_type: Optional[str] = None
        self._popup_party_member_client_id: Optional[int] = None
        self._popup_party_member_is_host: Optional[bool] = None
        self._complaint_cnt = None
        self._width = 520

        uiscale = bui.app.ui_v1.uiscale
        self._height = (390 if uiscale is babase.UIScale.SMALL else
                        500 if uiscale is babase.UIScale.MEDIUM else 620)

        self._bg_color = babase.app.config.get("PartyWindow_Main_Color", (0.25, 0.45, 0.35))
        if not isinstance(self._bg_color, (list, tuple)) or len(self._bg_color) != 3:
            self._bg_color = (0.25, 0.45, 0.35)

        _W = self._width
        _H = self._height
        _hw = _W * 0.5
        _hh = _H * 0.5

        bui.Window.__init__(self, root_widget=bui.containerwidget(
            size=(0.0, 0.0),
            transition='in_scale',
            background=False,
            color=self._bg_color,
            parent=bui.get_special_widget('overlay_stack'),
            on_outside_click_call=self.close_with_sound,
            scale_origin_stack_offset=origin,
            scale=(1.95 if uiscale is babase.UIScale.SMALL else
                   1.35 if uiscale is babase.UIScale.MEDIUM else 1.0),
            stack_offset=(0, -10) if uiscale is babase.UIScale.SMALL else (
                240, 0) if uiscale is babase.UIScale.MEDIUM else (330, 20)))

        _r, _g, _b = self._bg_color
        _OL = _apw_compute_outline_color(self._bg_color)
        _OA = 0.75
        self._outline_color = _OL

        self._bg_image = _draw_panel_bg(
            parent=self._root_widget,
            x=-_hw, y=-_hh, w=_W, h=_H,
            color=(_r * 0.14 + 0.03, _g * 0.14 + 0.04, _b * 0.14 + 0.06),
            opacity=0.88)
        self._bg_footer = self._bg_image

        self._window_borders = _draw_border(
            parent=self._root_widget,
            x=-_hw, y=-_hh, w=_W, h=_H,
            color=_OL, opacity=_OA, thickness=2)

        PAD = 5
        self._content_w = CONTENT_W = _W - PAD * 2
        self._left_x = LEFT_X = -_hw + PAD
        self._right_x = RIGHT_X = _hw - PAD

        HEADER_Y = _hh - 46
        BTN_SZ   = 36

        self._header_track = _draw_panel_bg(
            parent=self._root_widget,
            x=LEFT_X, y=HEADER_Y - 4, w=CONTENT_W, h=BTN_SZ + 8,
            color=(0.03, 0.05, 0.09), opacity=0.55)

        self._header_borders = _draw_border(
            parent=self._root_widget,
            x=LEFT_X, y=HEADER_Y - 4,
            w=CONTENT_W, h=BTN_SZ + 8,
            color=_OL, opacity=0.60, thickness=1.5)

        SORRY_W = 58
        self._header_dividers = [
            bui.imagewidget(
                parent=self._root_widget,
                size=(1.5, BTN_SZ),
                position=(LEFT_X + BTN_SZ + 9, HEADER_Y),
                texture=bui.gettexture('white'),
                opacity=0.40,
                color=_OL),
            bui.imagewidget(
                parent=self._root_widget,
                size=(1.5, BTN_SZ),
                position=(RIGHT_X - BTN_SZ - 15 - SORRY_W, HEADER_Y),
                texture=bui.gettexture('white'),
                opacity=0.40,
                color=_OL),
            bui.imagewidget(
                parent=self._root_widget,
                size=(1.5, BTN_SZ),
                position=(RIGHT_X - BTN_SZ - 10, HEADER_Y),
                texture=bui.gettexture('white'),
                opacity=0.40,
                color=_OL),
        ]

        self._close_button_gb = GlassButton(
            parent=self._root_widget,
            position=(LEFT_X + 4, HEADER_Y),
            size=(BTN_SZ, BTN_SZ),
            label='✕', text_scale=0.85,
            bg_color=(0.18, 0.08, 0.09),
            opacity=0.35,
            text_color=(1.0, 0.55, 0.55),
            border=True,
            border_color=(1.0, 0.40, 0.45),
            border_opacity=0.85,
            border_thickness=1.5,
            on_activate_call=self.close)
        self._close_button = self._close_button_gb.widget

        self._cancel_button = bui.buttonwidget(
            parent=self._root_widget,
            position=(-9000, -9000),
            size=(1, 1),
            label='',
            on_activate_call=self.close)
        bui.containerwidget(edit=self._root_widget, cancel_button=self._cancel_button)

        self._sorry_button_gb = GlassButton(
            parent=self._root_widget,
            position=(RIGHT_X - 4 - BTN_SZ - 10 - SORRY_W, HEADER_Y),
            size=(SORRY_W, BTN_SZ),
            label='Sorry!', text_scale=0.58,
            bg_color=(0.24, 0.16, 0.10),
            opacity=0.38,
            text_color=(1.0, 0.88, 0.60),
            border=True,
            border_color=_OL,
            border_opacity=0.75,
            border_thickness=1.5,
            on_activate_call=self._on_sorry_press)

        self._menu_button_gb = GlassButton(
            parent=self._root_widget,
            position=(RIGHT_X - 4 - BTN_SZ, HEADER_Y),
            size=(BTN_SZ, BTN_SZ),
            label='⚙', text_scale=0.85,
            bg_color=(0.10, 0.13, 0.18),
            opacity=0.35,
            text_color=(0.85, 0.95, 0.90),
            border=True,
            border_color=_OL,
            border_opacity=0.85,
            border_thickness=1.5,
            on_activate_call=self._on_menu_button_press)
        self._menu_button = self._menu_button_gb.widget

        info = bs.get_connection_to_host_info_2()
        title = info.get("name", "Party") if isinstance(info, dict) else (getattr(info, "name", "Party") if info else "Party")

        self._header_y = HEADER_Y
        self._left_x = LEFT_X
        self._right_x = RIGHT_X
        self._content_w = CONTENT_W
        self._header_max_w = CONTENT_W - BTN_SZ * 2 - SORRY_W - 44
        self._title_text = bui.textwidget(
            parent=self._root_widget,
            scale=1.12,
            color=(0.98, 1.0, 0.65),
            text=title,
            size=(0, 0),
            position=(-32, HEADER_Y + 15),
            selectable=False,
            maxwidth=self._header_max_w,
            h_align='center', v_align='center')

        self._header_players_box_bg: Optional[bui.Widget] = None
        self._header_players_box_borders: List[bui.Widget] = []
        self._header_players_widgets: List[bui.Widget] = []
        self._header_players_rows: int = -1

        self.ping_widget = None
        _babase.ping_widget = None
        self._refresh_sorry_btn()

        self._base_tab_y = TAB_Y = HEADER_Y - 36
        self._tab_track_h = TAB_TRACK_H = 30
        self._tab_h = TAB_H = 26
        self._tab_gap = TAB_GAP = 3
        self._tab_w = TAB_W = (CONTENT_W - 6 - 2 * TAB_GAP) / 3
        self.active_tab = "chat"

        self._tab_track = _draw_panel_bg(
            parent=self._root_widget,
            x=LEFT_X, y=TAB_Y - 2, w=CONTENT_W, h=TAB_TRACK_H,
            color=(0.01, 0.02, 0.04), opacity=0.55)

        self._tab_track_borders = _draw_border(
            parent=self._root_widget,
            x=LEFT_X, y=TAB_Y - 2, w=CONTENT_W, h=TAB_TRACK_H,
            color=_OL, opacity=0.55, thickness=1.5)

        self._tab_chat = GlassButton(
            parent=self._root_widget,
            position=(LEFT_X + 3, TAB_Y),
            size=(TAB_W, TAB_H),
            label='💬 Chat', text_scale=0.68,
            bg_color=(0.14, 0.34, 0.25),
            opacity=0.55,
            text_color=(1, 1, 1),
            border=True,
            border_color=_OL,
            border_opacity=0.90,
            border_thickness=1.5,
            on_activate_call=babase.CallPartial(self._switch_tab, "chat"))

        self._tab_players = GlassButton(
            parent=self._root_widget,
            position=(LEFT_X + 3 + TAB_W + TAB_GAP, TAB_Y),
            size=(TAB_W, TAB_H),
            label='👥 Roster', text_scale=0.68,
            bg_color=(0.08, 0.11, 0.16),
            opacity=0.30,
            text_color=(0.72, 0.82, 0.92),
            border=True,
            border_color=_OL,
            border_opacity=0.35,
            border_thickness=1.5,
            on_activate_call=babase.CallPartial(self._switch_tab, "players"))

        self._tab_servers = GlassButton(
            parent=self._root_widget,
            position=(LEFT_X + 3 + (TAB_W + TAB_GAP) * 2, TAB_Y),
            size=(TAB_W, TAB_H),
            label='⭐ Servers', text_scale=0.68,
            bg_color=(0.08, 0.11, 0.16),
            opacity=0.30,
            text_color=(0.72, 0.82, 0.92),
            border=True,
            border_color=_OL,
            border_opacity=0.35,
            border_thickness=1.5,
            on_activate_call=babase.CallPartial(self._switch_tab, "servers"))

        INP_Y = -_hh + 7
        QUICK_W = 70
        ICON_BTN_W = 44
        SEND_W = 70
        BTN_H = 38
        GAP = 4

        self._bottom_dock = _draw_panel_bg(
            parent=self._root_widget,
            x=LEFT_X, y=INP_Y - 2, w=CONTENT_W, h=BTN_H + 4,
            color=(0.01, 0.02, 0.04), opacity=0.55)

        self._bottom_borders = _draw_border(
            parent=self._root_widget,
            x=LEFT_X, y=INP_Y - 2, w=CONTENT_W, h=BTN_H + 4,
            color=_OL, opacity=0.55, thickness=1.5)

        self._quick_button = GlassButton(
            parent=self._root_widget,
            position=(LEFT_X + 2, INP_Y),
            size=(QUICK_W, BTN_H),
            label='Quick', text_scale=0.66,
            bg_color=(0.12, 0.18, 0.26),
            opacity=0.38,
            text_color=(0.88, 0.94, 1.0),
            border=True,
            border_color=_OL,
            border_opacity=0.80,
            border_thickness=1.5,
            on_activate_call=self._on_quick_button_click)

        _q_icon_cfg = babase.app.config.get('APW_Quick_Emojis')
        _q_icon = _q_icon_cfg[0] if (isinstance(_q_icon_cfg, list) and _q_icon_cfg) else '\ue048'
        self._emoji_popup_btn = GlassButton(
            parent=self._root_widget,
            position=(LEFT_X + 2 + QUICK_W + GAP, INP_Y),
            size=(ICON_BTN_W, BTN_H),
            label=_q_icon, text_scale=get_emoji_scale(_q_icon),
            text_y_offset=get_emoji_y_offset(_q_icon),
            bg_color=(0.12, 0.18, 0.28),
            opacity=0.40,
            text_color=(1.0, 0.92, 0.55),
            border=True,
            border_color=_OL,
            border_opacity=0.80,
            border_thickness=1.5,
            on_activate_call=self._open_emoji_insert_popup)

        field_x = LEFT_X + 2 + QUICK_W + GAP + ICON_BTN_W + GAP
        send_x = RIGHT_X - SEND_W - 2
        field_box_w = send_x - GAP - field_x

        self._text_bg = _draw_panel_bg(
            parent=self._root_widget,
            x=field_x, y=INP_Y, w=field_box_w, h=BTN_H,
            color=(0.02, 0.04, 0.07), opacity=0.65)

        self._text_field = bui.textwidget(
            parent=self._root_widget,
            editable=True,
            size=(field_box_w - 8, BTN_H),
            position=(field_x + 4, INP_Y),
            text=draft_chat_text,
            maxwidth=field_box_w - 18,
            shadow=0.3,
            flatness=1.0,
            description=babase.Lstr(resource=self._r + '.chatMessageText'),
            autoselect=True,
            v_align='center')

        self._empty_ping_hint = bui.textwidget(
            parent=self._root_widget,
            size=(0, 0),
            position=(field_x + field_box_w * 0.5, INP_Y + BTN_H * 0.5),
            h_align='center', v_align='center',
            scale=0.60,
            selectable=False,
            flatness=1.0,
            shadow=0.2,
            color=(0.55, 0.90, 0.72),
            maxwidth=field_box_w - 20,
            text=f"{current_ping:.2f}ms" if not draft_chat_text else "")

        self._text_borders = _draw_border(
            parent=self._root_widget,
            x=field_x, y=INP_Y,
            w=field_box_w, h=BTN_H,
            color=_OL, opacity=0.70, thickness=1.5)

        self._send_button = GlassButton(
            parent=self._root_widget,
            position=(send_x, INP_Y),
            size=(SEND_W, BTN_H),
            label='Send', text_scale=0.72,
            bg_color=(0.10, 0.30, 0.20),
            opacity=0.45,
            text_color=(0.85, 1.0, 0.88),
            border=True,
            border_color=_OL,
            border_opacity=0.85,
            border_thickness=1.5,
            on_activate_call=self._send_chat_message)

        self._emoji_buttons: List[GlassButton] = []
        self._emoji_borders = []

        self._full_scroll_bottom = INP_Y + BTN_H + 6
        self._chat_nav_scroll_bottom = self._full_scroll_bottom + 31
        self._scroll_top = TAB_Y - 5
        self._scroll_width = CONTENT_W

        self._chat_nav_widgets: List[Any] = []
        self._chat_nav_label: Optional[bui.Widget] = None

        _scroll_h = self._scroll_top - self._full_scroll_bottom

        self._scroll_bg = _draw_panel_bg(
            parent=self._root_widget,
            x=LEFT_X, y=self._full_scroll_bottom, w=CONTENT_W, h=_scroll_h,
            color=(_r * 0.08 + 0.02, _g * 0.08 + 0.03, _b * 0.08 + 0.05),
            opacity=0.68)

        self._scroll_borders = _draw_border(
            parent=self._root_widget,
            x=LEFT_X, y=self._full_scroll_bottom, w=CONTENT_W, h=_scroll_h,
            color=_OL, opacity=0.65, thickness=1.5)
        self._scrollwidget = bui.scrollwidget(
            parent=self._root_widget,
            size=(self._scroll_width, max(60, self._scroll_top - self._chat_nav_scroll_bottom)),
            position=(LEFT_X, self._chat_nav_scroll_bottom),
            color=(0.04, 0.05, 0.08))

        self._columnwidget = bui.columnwidget(parent=self._scrollwidget, border=0, margin=0)

        bui.textwidget(edit=self._text_field, on_return_press_call=self._send_chat_message)
        bui.containerwidget(edit=self._root_widget, selected_child=self._text_field)

        self._chat_texts: List[bui.Widget] = []
        self._chat_texts_haxx: List[bui.Widget] = []
        self._chat_items: List[Dict[str, Any]] = []
        self._selected_chat_idx: int = -1
        self._chat_empty_holder: Optional[bui.Widget] = None
        self._roster_widgets: List[bui.Widget] = []
        self._roster: Optional[List[Dict[str, Any]]] = None

        self._build_chat_nav_bar()

        _apw_active_window_ref = weakref.ref(self)
        msgs = _apw_sync_session_history()
        visible_msgs = [m for m in msgs if not self._is_msg_muted(m)]
        if visible_msgs:
            for msg in visible_msgs[-50:]:
                self._add_msg(msg, ignore_mute=True)
        else:
            self._render_empty_chat_banner()

        self._update_timer = babase.AppTimer(1.0, babase.WeakCallStrict(self._update), repeat=True)
        self._ping_hint_timer = babase.AppTimer(0.15, babase.WeakCallStrict(self._refresh_input_ping_hint), repeat=True)
        self._refresh_header_players(force=True)
        self._update()

    def _destroy_chat_nav_bar(self) -> None:
        self._anim_timer = None
        for item in getattr(self, '_chat_nav_widgets', []):
            try:
                item.delete()
            except Exception:
                pass
        for item in getattr(self, '_anim_widgets', []):
            try:
                item.delete()
            except Exception:
                pass
        self._chat_nav_widgets = []
        self._anim_widgets = []
        self._anim_bars = []
        self._anim_track_borders = []
        self._chat_nav_label = None

    def _step_chat_anim(self) -> None:
        bars = getattr(self, '_anim_bars', None)
        if not bars or self.active_tab != "chat" or not getattr(self, '_root_widget', None):
            return
        mode = _apw_get_chat_anim_style()
        if mode == 'off':
            return
        t = getattr(self, '_anim_phase', 0.0) + 0.28
        self._anim_phase = t
        ol = getattr(self, '_outline_color', (0.4, 1.0, 0.5))
        n = len(bars)
        base_y = getattr(self, '_anim_base_y', 0.0)
        bar_w = getattr(self, '_anim_bar_w', 8.0)
        max_h = 18.0
        try:
            if mode == 'scanner':
                pos = (math.sin(t * 0.72) * 0.5 + 0.5) * (n - 1)
                for i, bw in enumerate(bars):
                    dist = abs(i - pos)
                    intensity = max(0.0, 1.0 - dist / 2.6)
                    h = 4.0 + intensity * (max_h - 4.0)
                    cy = base_y + (max_h - h) * 0.5
                    col = (
                        min(1.0, ol[0] * (0.4 + 0.65 * intensity)),
                        min(1.0, ol[1] * (0.4 + 0.65 * intensity)),
                        min(1.0, ol[2] * (0.4 + 0.65 * intensity)),
                    )
                    bui.imagewidget(
                        edit=bw, size=(bar_w, h),
                        position=(getattr(self, '_anim_xs', [])[i], cy),
                        color=col, opacity=0.20 + 0.75 * intensity)
            elif mode == 'equalizer':
                for i, bw in enumerate(bars):
                    v = 0.5 + 0.5 * math.sin(t * 1.35 + i * 0.85) * math.cos(t * 0.6 + i * 0.4)
                    h = 3.5 + max(0.0, min(1.0, v)) * (max_h - 3.5)
                    col = (
                        min(1.0, ol[0] * 0.55 + 0.25 * (1.0 - i / max(1, n - 1))),
                        min(1.0, ol[1] * 0.75 + 0.25 * v),
                        min(1.0, ol[2] * 0.75 + 0.30 * (i / max(1, n - 1))),
                    )
                    bui.imagewidget(
                        edit=bw, size=(bar_w, h),
                        position=(getattr(self, '_anim_xs', [])[i], base_y),
                        color=col, opacity=0.35 + 0.58 * v)
            elif mode == 'wave':
                for i, bw in enumerate(bars):
                    w_val = 0.5 + 0.5 * math.sin(t * 1.15 - i * 0.55)
                    h = 4.0 + w_val * 10.0
                    cy = base_y + 4.0 + math.sin(t * 1.15 - i * 0.55) * 4.0
                    cy = max(base_y, min(base_y + max_h - h, cy))
                    col = (
                        min(1.0, 0.25 + 0.70 * w_val * ol[0]),
                        min(1.0, 0.45 + 0.55 * w_val),
                        min(1.0, 0.60 + 0.40 * (1.0 - w_val)),
                    )
                    bui.imagewidget(
                        edit=bw, size=(bar_w, h),
                        position=(getattr(self, '_anim_xs', [])[i], cy),
                        color=col, opacity=0.30 + 0.62 * w_val)
            elif mode == 'spectrum':
                for i, bw in enumerate(bars):
                    hue = (t * 0.08 + i / max(1, n)) % 1.0
                    r = 0.5 + 0.5 * math.sin(hue * 6.283)
                    g = 0.5 + 0.5 * math.sin((hue + 0.333) * 6.283)
                    b = 0.5 + 0.5 * math.sin((hue + 0.666) * 6.283)
                    pulse = 0.5 + 0.5 * math.sin(t * 0.9 - i * 0.45)
                    h = 6.0 + pulse * (max_h - 6.0)
                    cy = base_y + (max_h - h) * 0.5
                    bui.imagewidget(
                        edit=bw, size=(bar_w, h),
                        position=(getattr(self, '_anim_xs', [])[i], cy),
                        color=(r, g, b), opacity=0.55 + 0.35 * pulse)
        except Exception:
            pass

    def _build_chat_nav_bar(self) -> None:
        self._destroy_chat_nav_bar()
        if self.active_tab != "chat":
            return
        ol = getattr(self, '_outline_color', (0.4, 1.0, 0.5))
        t_on = _apw_get_translate_cfg()["enabled"]
        nw = 194
        nh = 26
        nx = self._right_x - nw - 6
        ny = self._full_scroll_bottom + 4

        ax = self._left_x + 6
        aw = max(40, (nx - 6) - ax)
        anim_mode = _apw_get_chat_anim_style()
        abg = _draw_panel_bg(self._root_widget, ax, ny, aw, nh, color=(0.02, 0.04, 0.07), opacity=0.65)
        abdrs = _draw_border(self._root_widget, ax, ny, aw, nh, color=ol, opacity=0.38 if anim_mode != 'off' else 0.22, thickness=1.0)
        self._anim_widgets.append(abg)
        self._anim_widgets.extend(abdrs)
        self._anim_track_borders = list(abdrs)
        self._anim_bars = []
        self._anim_xs = []
        if anim_mode != 'off' and aw >= 60:
            cnt_bars = 14
            pad_x = 8.0
            gap_x = 4.0
            bar_w = max(4.0, (aw - pad_x * 2 - (cnt_bars - 1) * gap_x) / cnt_bars)
            self._anim_bar_w = bar_w
            self._anim_base_y = ny + 4.0
            self._anim_phase = getattr(self, '_anim_phase', 0.0)
            for i in range(cnt_bars):
                bx = ax + pad_x + i * (bar_w + gap_x)
                self._anim_xs.append(bx)
                img = bui.imagewidget(
                    parent=self._root_widget,
                    position=(bx, ny + 4.0),
                    size=(bar_w, 10.0),
                    texture=bui.gettexture('softRect'),
                    color=ol,
                    opacity=0.45)
                self._anim_bars.append(img)
                self._anim_widgets.append(img)
            self._step_chat_anim()
            self._anim_timer = babase.AppTimer(0.09, babase.WeakCallStrict(self._step_chat_anim), repeat=True)

        bg = _draw_panel_bg(self._root_widget, nx, ny, nw, nh, color=(0.02, 0.04, 0.07), opacity=0.84)
        bdrs = _draw_border(self._root_widget, nx, ny, nw, nh, color=ol, opacity=0.65, thickness=1.1)
        self._chat_nav_widgets.append(bg)
        self._chat_nav_widgets.extend(bdrs)

        btn_h = nh - 4
        btn_y = ny + 2

        up_gb = GlassButton(
            parent=self._root_widget, position=(nx + 3, btn_y), size=(26, btn_h),
            label='▲', text_scale=0.52, bg_color=(0.10, 0.16, 0.24), opacity=0.55,
            text_color=(0.75, 0.92, 1.0), border=True, border_color=ol, border_opacity=0.60, border_thickness=1.0,
            on_activate_call=babase.CallPartial(self._nav_chat_msg, -1))
        dn_gb = GlassButton(
            parent=self._root_widget, position=(nx + 32, btn_y), size=(26, btn_h),
            label='▼', text_scale=0.52, bg_color=(0.10, 0.16, 0.24), opacity=0.55,
            text_color=(0.75, 0.92, 1.0), border=True, border_color=ol, border_opacity=0.60, border_thickness=1.0,
            on_activate_call=babase.CallPartial(self._nav_chat_msg, 1))
        tr_gb = GlassButton(
            parent=self._root_widget, position=(nx + 61, btn_y), size=(30, btn_h),
            label='🌐', text_scale=0.54,
            bg_color=(0.12, 0.38, 0.24) if t_on else (0.10, 0.14, 0.20),
            opacity=0.72 if t_on else 0.48,
            text_color=(0.70, 1.0, 0.80) if t_on else (0.72, 0.82, 0.92),
            border=True, border_color=ol if t_on else (0.45, 0.65, 0.85),
            border_opacity=0.85 if t_on else 0.50, border_thickness=1.0,
            on_activate_call=self._toggle_whole_chat_translate)
        cp_gb = GlassButton(
            parent=self._root_widget, position=(nx + 94, btn_y), size=(46, btn_h),
            label='Copy', text_scale=0.50, bg_color=(0.12, 0.24, 0.36), opacity=0.55,
            text_color=(0.85, 0.95, 1.0), border=True, border_color=(0.45, 0.80, 1.0), border_opacity=0.70, border_thickness=1.0,
            on_activate_call=self._copy_selected_chat_msg)
        rp_gb = GlassButton(
            parent=self._root_widget, position=(nx + 143, btn_y), size=(48, btn_h),
            label='Reply', text_scale=0.50, bg_color=(0.12, 0.32, 0.22), opacity=0.55,
            text_color=(0.85, 1.0, 0.88), border=True, border_color=ol, border_opacity=0.75, border_thickness=1.0,
            on_activate_call=self._reply_selected_chat_msg)

        self._chat_nav_widgets.extend([up_gb, dn_gb, tr_gb, cp_gb, rp_gb])
        self._chat_auto_trans_gb = tr_gb
        self._chat_nav_label = None

    def _set_scroll_bottom(self, bottom_y: float) -> None:
        try:
            lx = getattr(self, '_left_x', -self._width * 0.5 + 8)
            h = max(60, self._scroll_top - bottom_y)
            bui.scrollwidget(edit=self._scrollwidget, position=(lx, bottom_y), size=(self._scroll_width, h))
        except Exception:
            pass

    def _update_chat_nav_label(self) -> None:
        pass

    def _apply_chat_row_text(self, idx: int) -> None:
        if not (0 <= idx < len(self._chat_items)):
            return
        it = self._chat_items[idx]
        disp = it.get("translated") or it["msg"]
        if idx == self._selected_chat_idx:
            disp = f">> {disp}"
            col = (0.45, 1.0, 0.75)
        elif it.get("translated"):
            col = (0.60, 0.95, 1.0) if not _apw_is_colorful_chat() else it["base_color"]
        else:
            col = it["base_color"]
        try:
            bui.textwidget(edit=it["widget"], text=babase.Lstr(value=disp), color=col)
        except Exception:
            pass

    def _translate_item_async(self, item_ref: Dict[str, Any]) -> None:
        raw_msg = item_ref.get("msg", "")
        if not raw_msg:
            return
        if ':' in raw_msg:
            sender_p, body_p = raw_msg.split(':', 1)
            prefix = f"{sender_p}: "
            body = body_p.strip()
        else:
            prefix = ""
            body = raw_msg.strip()
        if not body:
            return
        w_self = weakref.ref(self)

        def _on_done(tr_body: str):
            inst = w_self()
            if inst is None or item_ref not in inst._chat_items:
                return
            if tr_body and tr_body.strip():
                item_ref["translated"] = f"{prefix}{tr_body}"
                try:
                    idx = inst._chat_items.index(item_ref)
                    inst._apply_chat_row_text(idx)
                except Exception:
                    pass

        _apw_translate_async(body, _on_done)

    def _toggle_whole_chat_translate(self) -> None:
        cur = _apw_get_translate_cfg()["enabled"]
        nxt = not cur
        babase.app.config['APW_AutoTranslate_Chat'] = nxt
        babase.app.config.commit()
        tr_gb = getattr(self, '_chat_auto_trans_gb', None)
        ol = getattr(self, '_outline_color', (0.4, 1.0, 0.5))
        if tr_gb is not None:
            tr_gb.set_color(
                bg_color=(0.12, 0.38, 0.24) if nxt else (0.10, 0.14, 0.20),
                opacity=0.72 if nxt else 0.48,
                text_color=(0.70, 1.0, 0.80) if nxt else (0.72, 0.82, 0.92))
            tr_gb.set_border_color(color=ol if nxt else (0.45, 0.65, 0.85), opacity=0.85 if nxt else 0.50)
        bui.screenmessage(
            f"Auto-Translate Whole Chat: {'ON' if nxt else 'OFF'}",
            color=(0.45, 1.0, 0.70) if nxt else (0.85, 0.85, 0.90))
        self._refresh_all_chat_translations()

    def _refresh_all_chat_translations(self) -> None:
        t_on = _apw_get_translate_cfg()["enabled"]
        for idx, it in enumerate(self._chat_items):
            if t_on:
                self._translate_item_async(it)
            else:
                it["translated"] = None
                self._apply_chat_row_text(idx)

    def _translate_selected_chat_msg(self) -> None:
        idx = self._selected_chat_idx
        if not (0 <= idx < len(self._chat_items)):
            return
        it = self._chat_items[idx]
        if it.get("translated"):
            it["translated"] = None
            self._apply_chat_row_text(idx)
            bui.screenmessage("Restored original message", color=(0.80, 0.88, 0.96))
        else:
            bui.screenmessage("Translating message...", color=(0.55, 0.92, 1.0))
            self._translate_item_async(it)

    def _recolor_chat_items(self) -> None:
        colorful = _apw_is_colorful_chat()
        try:
            my_name = babase.app.plus.get_v1_account_display_string() if babase.app.plus else ''
        except Exception:
            my_name = ''
        for idx, it in enumerate(self._chat_items):
            msg = it["msg"]
            is_mention = bool(my_name and f"@{my_name}".lower() in msg.lower())
            if is_mention:
                col = (1.0, 0.82, 0.35)
            elif colorful:
                col = _apw_get_chat_sender_color(msg)
            else:
                col = (0.90, 0.95, 1.00)
            it["base_color"] = col
            self._apply_chat_row_text(idx)

    def _select_chat_index(self, new_idx: int) -> None:
        items = self._chat_items
        if not items:
            self._selected_chat_idx = -1
            return
        old_idx = self._selected_chat_idx
        self._selected_chat_idx = -1
        if 0 <= old_idx < len(items):
            self._apply_chat_row_text(old_idx)

        if new_idx < 0 or new_idx >= len(items):
            self._selected_chat_idx = -1
            self.msg_user_selected = ""
            return

        self._selected_chat_idx = new_idx
        it = items[new_idx]
        self.msg_user_selected = it["msg"]
        self._apply_chat_row_text(new_idx)
        try:
            bui.containerwidget(edit=self._columnwidget, visible_child=it.get("row", it["widget"]))
        except Exception:
            pass

    def _nav_chat_msg(self, delta: int) -> None:
        items = self._chat_items
        if not items:
            bui.screenmessage("No chat messages yet!", color=(1.0, 0.75, 0.35))
            return
        idx = self._selected_chat_idx
        if idx < 0 or idx >= len(items):
            target = len(items) - 1 if delta < 0 else 0
        else:
            target = max(0, min(len(items) - 1, idx + delta))
        self._select_chat_index(target)

    def _copy_selected_chat_msg(self) -> None:
        if not (0 <= self._selected_chat_idx < len(self._chat_items)):
            if not self._chat_items:
                bui.screenmessage("No chat message to copy!", color=(1.0, 0.55, 0.35))
                return
            self._select_chat_index(len(self._chat_items) - 1)
        msg = self._chat_items[self._selected_chat_idx]["msg"]
        if bui.clipboard_is_supported():
            bui.clipboard_set_text(msg)
            bui.screenmessage("Copied message!", color=(0.3, 1.0, 0.5))

    def _reply_selected_chat_msg(self) -> None:
        if not (0 <= self._selected_chat_idx < len(self._chat_items)):
            if not self._chat_items:
                bui.screenmessage("No chat message to reply to!", color=(1.0, 0.55, 0.35))
                return
            self._select_chat_index(len(self._chat_items) - 1)
        msg = self._chat_items[self._selected_chat_idx]["msg"]
        rep_txt = _apw_format_reply_prefix(msg)
        if rep_txt:
            bui.textwidget(edit=self._text_field, text=rep_txt)
            self._refresh_input_ping_hint()
            sender = _apw_clean_name(msg.split(":", 1)[0]).strip(" '\"")
            bui.screenmessage(f"Replying to {sender}", color=(0.45, 0.90, 1.0))

    def on_chat_message(self, msg: str) -> None:
        """Called by BombSquad when a new chat message arrives."""
        _apw_sync_session_history(extra_msg=msg)
        if not self._is_msg_muted(msg):
            self._add_msg(msg)

    def _rebuild_chat_after_unmute(self) -> None:
        """Re-populate visible chat chronologically so previously muted player chats appear on unmute."""
        if self.active_tab != "chat":
            return
        try:
            for child in self._columnwidget.get_children():
                child.delete()
            self._chat_texts.clear()
            self._chat_texts_haxx.clear()
            self._chat_items.clear()
            self._selected_chat_idx = -1
            self._chat_empty_holder = None
            msgs = _apw_sync_session_history()
            visible_msgs = [m for m in msgs if not self._is_msg_muted(m)]
            if visible_msgs:
                for msg in visible_msgs[-50:]:
                    self._add_msg(msg, ignore_mute=True)
            else:
                self._render_empty_chat_banner()
        except Exception:
            pass

    def _render_empty_chat_banner(self) -> None:
        if self.active_tab != "chat":
            return
        try:
            if getattr(self, '_chat_empty_holder', None) is not None:
                return
            ol = getattr(self, '_outline_color', (0.4, 1.0, 0.5))
            box_w = self._scroll_width - 16
            holder = bui.containerwidget(parent=self._columnwidget, size=(box_w, 120), background=False)
            bui.imagewidget(
                parent=holder, size=(box_w - 24, 84), position=(12, 18),
                texture=bui.gettexture('softRect'), opacity=0.22,
                color=(0.08, 0.14, 0.22))
            _draw_border(holder, 12, 18, box_w - 24, 84, color=ol, opacity=0.35, thickness=1.0)
            bui.textwidget(
                parent=holder, position=(box_w * 0.5, 72), size=(0, 0),
                h_align='center', v_align='center',
                text='💬 Party Chat Ready',
                scale=0.78, color=(0.88, 0.96, 1.0))
            bui.textwidget(
                parent=holder, position=(box_w * 0.5, 44), size=(0, 0),
                h_align='center', v_align='center',
                text='Type a message below or tap Quick / Icons next to it',
                scale=0.50, color=(0.60, 0.74, 0.88))
            self._chat_empty_holder = holder
        except Exception:
            pass

    def _switch_tab(self, tab: str):
        self.active_tab = tab
        c_act_bg   = (0.14, 0.34, 0.25)
        c_inact_bg = (0.08, 0.11, 0.16)
        ol = getattr(self, '_outline_color', (0.4, 1.0, 0.5))

        self._tab_chat.set_color(bg_color=c_act_bg if tab == "chat" else c_inact_bg,
                                 opacity=0.52 if tab == "chat" else 0.28,
                                 text_color=(1, 1, 1) if tab == "chat" else (0.72, 0.82, 0.92))
        self._tab_chat.set_border_color(color=ol, opacity=0.90 if tab == "chat" else 0.35)

        self._tab_players.set_color(bg_color=c_act_bg if tab == "players" else c_inact_bg,
                                   opacity=0.52 if tab == "players" else 0.28,
                                   text_color=(1, 1, 1) if tab == "players" else (0.72, 0.82, 0.92))
        self._tab_players.set_border_color(color=ol, opacity=0.90 if tab == "players" else 0.35)

        self._tab_servers.set_color(bg_color=c_act_bg if tab == "servers" else c_inact_bg,
                                   opacity=0.52 if tab == "servers" else 0.28,
                                   text_color=(1, 1, 1) if tab == "servers" else (0.72, 0.82, 0.92))
        self._tab_servers.set_border_color(color=ol, opacity=0.90 if tab == "servers" else 0.35)

        for child in self._columnwidget.get_children():
            child.delete()
        self._chat_texts.clear()
        self._chat_texts_haxx.clear()
        self._chat_items.clear()
        self._selected_chat_idx = -1
        self._chat_empty_holder = None
        self._roster_widgets.clear()

        if tab == "chat":
            self._set_scroll_bottom(self._chat_nav_scroll_bottom)
            self._build_chat_nav_bar()
            msgs = _apw_sync_session_history()
            visible_msgs = [m for m in msgs if not self._is_msg_muted(m)]
            if visible_msgs:
                for msg in visible_msgs[-50:]:
                    self._add_msg(msg, ignore_mute=True)
            else:
                self._render_empty_chat_banner()
        elif tab == "players":
            self._destroy_chat_nav_bar()
            self._set_scroll_bottom(self._full_scroll_bottom)
            self._render_players_tab()
        elif tab == "servers":
            self._destroy_chat_nav_bar()
            self._set_scroll_bottom(self._full_scroll_bottom)
            self._render_servers_tab()

    def _insert_emoji(self, code: str):
        curr = bui.textwidget(query=self._text_field)
        bui.textwidget(edit=self._text_field, text=curr + code + " ")
        self._refresh_input_ping_hint()

    def _refresh_emoji_popup_btn(self) -> None:
        btn = getattr(self, '_emoji_popup_btn', None)
        if btn is None:
            return
        try:
            cfg = babase.app.config.get('APW_Quick_Emojis')
            ic = cfg[0] if (isinstance(cfg, list) and cfg) else '\ue048'
            btn.text_y_offset = get_emoji_y_offset(ic)
            ax, ay = btn.position
            w, h = btn.size
            bui.textwidget(
                edit=btn.label_widget,
                text=ic,
                scale=get_emoji_scale(ic),
                position=(ax + w * 0.5, ay + h * 0.5 + btn.text_y_offset))
        except Exception:
            pass

    def _open_emoji_insert_popup(self) -> None:
        """Compact Cyber-Glass Quick Icons Popup with Favourites block first, then Emblems, Others & All."""
        c_width, c_height = 500, 415
        ol = getattr(self, '_outline_color', (0.4, 1.0, 0.5))
        uiscale = bui.app.ui_v1.uiscale
        weak_self = weakref.ref(self)

        cnt = bui.containerwidget(
            size=(c_width, c_height),
            scale=(1.46 if uiscale is babase.UIScale.SMALL else
                   1.16 if uiscale is babase.UIScale.MEDIUM else 1.0),
            transition='in_scale',
            background=False,
            parent=bui.get_special_widget('overlay_stack'))

        _draw_panel_bg(cnt, 0, 0, c_width, c_height, color=(0.05, 0.07, 0.11), opacity=0.96)
        _draw_border(cnt, 0, 0, c_width, c_height, color=ol, opacity=0.84, thickness=1.5)

        bui.textwidget(
            parent=cnt, position=(c_width * 0.5, c_height - 19), size=(0, 0),
            h_align='center', v_align='center',
            text='Quick Icons & Favourites', scale=0.80, color=(1.0, 0.88, 0.35))

        default_favs = ['\ue048', '\ue043', '\ue046', '\ue04f', '\ue044', '\ue047', '\ue04d', '\ue02a']
        cfg_favs = babase.app.config.get('APW_Quick_Emojis')
        fav_icons = list(cfg_favs) if (isinstance(cfg_favs, list) and len(cfg_favs) == 8) else list(default_favs)
        pin_state = {"editing": False, "slot": 0}

        bui.textwidget(
            parent=cnt, position=(14, c_height - 43), size=(0, 0),
            h_align='left', v_align='center',
            text='⭐ Favourites:', scale=0.52, color=(1.0, 0.88, 0.38))

        pin_btn = GlassButton(
            parent=cnt, position=(c_width - 178, c_height - 54), size=(94, 22),
            label='Pin Fav: OFF', text_scale=0.42,
            bg_color=(0.12, 0.16, 0.24), opacity=0.45,
            border=True, border_color=ol, border_opacity=0.55, border_thickness=1.0)
        reset_fav_btn = GlassButton(
            parent=cnt, position=(c_width - 78, c_height - 54), size=(64, 22),
            label='Reset', text_scale=0.42,
            bg_color=(0.24, 0.14, 0.16), opacity=0.45,
            border=True, border_color=(1.0, 0.45, 0.48), border_opacity=0.60, border_thickness=1.0)

        fav_w, fav_h, fav_gap = 55, 34, 5
        fav_start_x = (c_width - (8 * fav_w + 7 * fav_gap)) * 0.5
        fav_y = c_height - 94
        fav_bgs: List[bui.Widget] = []
        fav_borders: List[List[bui.Widget]] = []
        fav_texts: List[bui.Widget] = []

        def _refresh_favs_ui():
            ed = pin_state["editing"]
            pin_btn.set_text('Pin Fav: ON' if ed else 'Pin Fav: OFF')
            pin_btn.set_color(
                bg_color=(0.16, 0.40, 0.24) if ed else (0.12, 0.16, 0.24),
                opacity=0.65 if ed else 0.45)
            for idx in range(8):
                is_sel = ed and (idx == pin_state["slot"])
                bui.imagewidget(
                    edit=fav_bgs[idx],
                    color=(0.18, 0.45, 0.62) if is_sel else (0.09, 0.13, 0.20),
                    opacity=0.68 if is_sel else 0.38)
                for line in fav_borders[idx]:
                    bui.imagewidget(
                        edit=line,
                        color=(0.45, 1.0, 0.80) if is_sel else ol,
                        opacity=0.95 if is_sel else 0.42)
                code = fav_icons[idx]
                fx_i = fav_start_x + idx * (fav_w + fav_gap)
                bui.textwidget(
                    edit=fav_texts[idx],
                    text=code,
                    position=(fx_i, fav_y + get_emoji_y_offset(code)),
                    scale=get_emoji_scale(code))

        def _toggle_pin():
            pin_state["editing"] = not pin_state["editing"]
            _refresh_favs_ui()

        def _reset_favs():
            fav_icons[:] = list(default_favs)
            babase.app.config['APW_Quick_Emojis'] = list(fav_icons)
            babase._appconfig.commit_app_config()
            _refresh_favs_ui()
            inst = weak_self()
            if inst is not None:
                inst._refresh_emoji_popup_btn()

        pin_btn.set_on_activate(_toggle_pin)
        reset_fav_btn.set_on_activate(_reset_favs)

        def _on_fav_tap(slot_idx: int):
            if pin_state["editing"]:
                pin_state["slot"] = slot_idx
                _refresh_favs_ui()
            else:
                inst = weak_self()
                if inst is not None:
                    inst._insert_emoji(fav_icons[slot_idx])
                try:
                    bui.getsound('click01').play()
                except Exception:
                    pass

        for idx in range(8):
            fx = fav_start_x + idx * (fav_w + fav_gap)
            f_bg = _draw_panel_bg(cnt, fx, fav_y, fav_w, fav_h, color=(0.09, 0.13, 0.20), opacity=0.38)
            fav_bgs.append(f_bg)
            fav_borders.append(_draw_border(cnt, fx, fav_y, fav_w, fav_h, color=ol, opacity=0.42, thickness=1.1))
            f_txt = bui.textwidget(
                parent=cnt, size=(fav_w, fav_h),
                position=(fx, fav_y + get_emoji_y_offset(fav_icons[idx])),
                text=fav_icons[idx], scale=get_emoji_scale(fav_icons[idx]),
                h_align='center', v_align='center',
                selectable=True, click_activate=True,
                on_activate_call=babase.CallPartial(_on_fav_tap, idx))
            fav_texts.append(f_txt)

        cats = _get_categorized_special_chars()
        emblems_list = list(cats.get('Emblems', []))
        emblem_codes = {it[0] for it in emblems_list}
        others_list = [it for it in cats.get('All', []) if it[0] not in emblem_codes]
        all_list = list(cats.get('All', []))
        tab_data = {
            'Emblems': emblems_list,
            'Others': others_list,
            'All': all_list,
        }
        cat_keys = [
            ('Emblems', f"Emblems ({len(emblems_list)})"),
            ('Others', f"Others ({len(others_list)})"),
            ('All', f"All ({len(all_list)})"),
        ]

        cat_y = fav_y - 34
        cat_h = 26
        cat_gap = 6
        cat_w = (c_width - 16 - cat_gap * 2) / 3
        cat_btns: Dict[str, GlassButton] = {}

        scroll_x, scroll_y, scroll_w, scroll_h = 8, 52, c_width - 16, cat_y - 58
        _draw_panel_bg(cnt, scroll_x, scroll_y, scroll_w, scroll_h, color=(0.02, 0.04, 0.07), opacity=0.72)
        _draw_border(cnt, scroll_x, scroll_y, scroll_w, scroll_h, color=ol, opacity=0.50, thickness=1.2)
        p_scroll = bui.scrollwidget(
            parent=cnt, size=(scroll_w - 4, scroll_h - 4), position=(scroll_x + 2, scroll_y + 2),
            highlight=False, border_opacity=0.0)
        p_col = bui.columnwidget(parent=p_scroll, border=0, margin=0)

        def _insert_one(icon_code: str):
            if pin_state["editing"]:
                s_idx = pin_state["slot"]
                fav_icons[s_idx] = icon_code
                pin_state["slot"] = (s_idx + 1) % 8
                babase.app.config['APW_Quick_Emojis'] = list(fav_icons)
                babase._appconfig.commit_app_config()
                _refresh_favs_ui()
                inst = weak_self()
                if inst is not None:
                    inst._refresh_emoji_popup_btn()
                try:
                    bui.getsound('click01').play()
                except Exception:
                    pass
                return
            inst = weak_self()
            if inst is not None:
                inst._insert_emoji(icon_code)
            try:
                bui.getsound('click01').play()
            except Exception:
                pass

        def _populate_category(cat_key: str):
            for k, gbtn in cat_btns.items():
                is_act = (k == cat_key)
                gbtn.set_color(
                    bg_color=(0.14, 0.36, 0.28) if is_act else (0.08, 0.11, 0.16),
                    opacity=0.55 if is_act else 0.28,
                    text_color=(1, 1, 1) if is_act else (0.72, 0.82, 0.92))
                gbtn.set_border_color(color=ol, opacity=0.90 if is_act else 0.30)

            for child in p_col.get_children():
                child.delete()

            items = tab_data.get(cat_key, [])
            if not items:
                bui.textwidget(
                    parent=p_col, size=(scroll_w - 16, 60),
                    h_align='center', v_align='center',
                    text='No icons available', color=(0.6, 0.6, 0.6), scale=0.65)
                return

            p_cols = 9
            cell_w, cell_h, cell_gap = 48, 36, 4
            row_pad_x = max(4, (scroll_w - 18 - (p_cols * cell_w + (p_cols - 1) * cell_gap)) * 0.5)

            for r_start in range(0, len(items), p_cols):
                row_items = items[r_start:r_start + p_cols]
                row_cnt = bui.containerwidget(parent=p_col, size=(scroll_w - 18, cell_h + 4), background=False)
                for c_idx, (icon_code, _lbl, _name) in enumerate(row_items):
                    px = row_pad_x + c_idx * (cell_w + cell_gap)
                    py = 2
                    bui.imagewidget(
                        parent=row_cnt, size=(cell_w, cell_h), position=(px, py),
                        texture=bui.gettexture('softRect'), opacity=0.28, color=(0.10, 0.15, 0.22))
                    _draw_border(row_cnt, px, py, cell_w, cell_h, color=ol, opacity=0.24, thickness=1.0)
                    bui.textwidget(
                        parent=row_cnt, size=(cell_w, cell_h),
                        position=(px, py + get_emoji_y_offset(icon_code)),
                        text=icon_code, scale=get_emoji_scale(icon_code),
                        h_align='center', v_align='center',
                        selectable=True, click_activate=True,
                        on_activate_call=babase.CallPartial(_insert_one, icon_code))

        for c_i, (ck, clabel) in enumerate(cat_keys):
            cx = 8 + c_i * (cat_w + cat_gap)
            cat_btns[ck] = GlassButton(
                parent=cnt, position=(cx, cat_y), size=(cat_w, cat_h),
                label=clabel, text_scale=0.52,
                bg_color=(0.14, 0.36, 0.28) if ck == 'Emblems' else (0.08, 0.11, 0.16),
                opacity=0.55 if ck == 'Emblems' else 0.28,
                text_color=(1, 1, 1) if ck == 'Emblems' else (0.72, 0.82, 0.92),
                border=True, border_color=ol, border_opacity=0.90 if ck == 'Emblems' else 0.30, border_thickness=1.2,
                on_activate_call=babase.CallPartial(_populate_category, ck))

        _refresh_favs_ui()
        _populate_category('Emblems')

        def _close():
            try:
                bui.getsound('swish').play()
            except Exception:
                pass
            bui.containerwidget(edit=cnt, transition='out_scale')

        ghost_cancel = bui.buttonwidget(parent=cnt, position=(-9000, -9000), size=(1, 1), label='', on_activate_call=_close)
        bui.containerwidget(edit=cnt, cancel_button=ghost_cancel)

        GlassButton(
            parent=cnt, position=(c_width - 36, c_height - 34), size=(26, 26),
            label='✕', text_scale=0.8, bg_color=(0.18, 0.08, 0.09), opacity=0.35,
            text_color=(0.95, 0.50, 0.50), border=True, border_color=(1.0, 0.40, 0.45),
            border_opacity=0.75, border_thickness=1.2, on_activate_call=_close)
        GlassButton(
            parent=cnt, position=(c_width - 134, 10), size=(122, 34),
            label='Done', text_scale=0.66,
            bg_color=(0.14, 0.34, 0.24), opacity=0.55,
            border=True, border_color=ol, border_opacity=0.85, border_thickness=1.2,
            on_activate_call=_close)

    def close_with_sound(self) -> None:
        if not self._root_widget or getattr(self._root_widget, 'transitioning_out', False):
            return
        bui.getsound('swish').play()
        self.close()

    def close(self) -> None:
        global draft_chat_text
        if self._text_field:
            try:
                draft_chat_text = bui.textwidget(query=self._text_field)
            except Exception:
                pass
        self._update_timer = None
        self._ping_hint_timer = None
        self._anim_timer = None
        if not self._root_widget or getattr(self._root_widget, 'transitioning_out', False):
            return
        try:
            bui.containerwidget(edit=self._root_widget, transition='out_scale')
        except Exception:
            pass

    def _refresh_input_ping_hint(self) -> None:
        hint = getattr(self, '_empty_ping_hint', None)
        tf = getattr(self, '_text_field', None)
        if not hint or not tf:
            return
        try:
            txt = bui.textwidget(query=tf) or ""
            if txt:
                bui.textwidget(edit=hint, text="")
            else:
                if current_ping <= 70:
                    col = (0.50, 0.95, 0.68)
                elif current_ping <= 150:
                    col = (1.0, 0.88, 0.42)
                else:
                    col = (1.0, 0.48, 0.48)
                bui.textwidget(edit=hint, text=f"{current_ping:.2f}ms", color=col)
        except Exception:
            pass

    def _dismiss_update_banner(self) -> None:
        _apw_update_state["dismissed_this_boot"] = True
        self._refresh_header_players(force=True)

    def _start_manual_update_install(self) -> None:
        bui.screenmessage("Downloading update from GitHub...", color=(0.55, 0.92, 1.0))
        _apw_install_update_async()

    def _open_github_repo(self) -> None:
        try:
            bui.open_url(APW_REPO_URL)
        except Exception:
            bui.screenmessage(APW_REPO_URL, color=(0.65, 0.90, 1.0))

    def _refresh_header_players(self, force: bool = False) -> None:
        hy = getattr(self, '_header_y', None)
        base_tab_y = getattr(self, '_base_tab_y', None)
        if hy is None or base_tab_y is None:
            return
        try:
            show_p = _apw_show_header_players()
            show_upd = _apw_should_show_update_banner()
            roster = (bs.get_game_roster() or []) if show_p else []
            sig = (
                show_p,
                show_upd,
                _apw_update_state.get("remote_version", ""),
                tuple(
                    (
                        e.get('client_id'),
                        e.get('display_string'),
                        tuple((p.get('name_full') or p.get('name') or '') for p in (e.get('players') or [])),
                    )
                    for e in roster
                ),
            )
            if not force and getattr(self, '_header_players_sig', None) == sig:
                return
            self._header_players_sig = sig

            for w in getattr(self, '_header_players_widgets', []):
                try:
                    w.delete()
                except Exception:
                    pass
            self._header_players_widgets = []
            for w in getattr(self, '_header_players_box_borders', []):
                try:
                    w.delete()
                except Exception:
                    pass
            self._header_players_box_borders = []
            if getattr(self, '_header_players_box_bg', None) is not None:
                try:
                    self._header_players_box_bg.delete()
                except Exception:
                    pass
                self._header_players_box_bg = None
            for w in getattr(self, '_update_banner_widgets', []):
                try:
                    w.delete()
                except Exception:
                    pass
            self._update_banner_widgets = []
            self._update_banner_borders = []

            ol = getattr(self, '_outline_color', (0.4, 1.0, 0.5))
            lx = self._left_x
            cw = self._content_w
            p_col, _ = _apw_get_roster_colors()
            extra_h = 0

            if show_p:
                n = len(roster)
                cols = 1 if n <= 1 else (2 if n == 2 else 3)
                rows = max(1, math.ceil(n / cols)) if n > 0 else 1
                row_h = 20
                box_h = rows * row_h + 6
                top_y = hy - 4
                box_y = top_y - box_h
                extra_h = box_h + 4

                self._header_players_box_bg = _draw_panel_bg(
                    parent=self._root_widget,
                    x=lx, y=box_y, w=cw, h=box_h,
                    color=(0.01, 0.02, 0.05), opacity=0.52)
                self._header_players_box_borders = _draw_border(
                    parent=self._root_widget,
                    x=lx, y=box_y, w=cw, h=box_h,
                    color=ol, opacity=0.45, thickness=1.2)

                if n == 0:
                    nw = bui.textwidget(
                        parent=self._root_widget,
                        position=(lx + cw * 0.5, box_y + box_h * 0.5), size=(0, 0),
                        h_align='center', v_align='center',
                        text='No players connected', scale=0.45, color=(0.62, 0.72, 0.84))
                    self._header_players_widgets.append(nw)
                else:
                    cell_w = (cw - 10) / cols
                    for idx, entry in enumerate(roster):
                        cid = entry.get('client_id', -1)
                        v2_id = entry.get('display_string', 'Unknown')
                        ps = entry.get('players') or []
                        if ps:
                            pn = ", ".join(str(p.get('name_full') or p.get('name') or '').strip() for p in ps if (p.get('name_full') or p.get('name')))
                            pname = pn or v2_id
                        else:
                            pname = v2_id
                        is_host = (cid == -1)
                        r_i = idx // cols
                        c_i = idx % cols
                        bx = lx + 5 + c_i * cell_w + 2
                        by = (top_y - 3) - (r_i + 1) * row_h
                        disp = f"\ue027 {pname}" if is_host else pname
                        nw = bui.textwidget(
                            parent=self._root_widget,
                            position=(bx, by), size=(cell_w - 4, row_h),
                            h_align='center', v_align='center',
                            text=babase.Lstr(value=disp),
                            scale=0.52,
                            color=(1.0, 0.90, 0.42) if is_host else p_col,
                            maxwidth=max(20, cell_w - 8),
                            selectable=True, click_activate=True)
                        bui.textwidget(
                            edit=nw,
                            on_activate_call=babase.CallPartial(self._on_header_player_press, cid, is_host, nw))
                        self._header_players_widgets.append(nw)

            tab_y = base_tab_y - extra_h
            track_h = self._tab_track_h
            t = 1.5
            bui.imagewidget(edit=self._tab_track, position=(lx, tab_y - 2))
            tb = getattr(self, '_tab_track_borders', [])
            if len(tb) == 4:
                bui.imagewidget(edit=tb[0], position=(lx, tab_y - 2 + track_h - t))
                bui.imagewidget(edit=tb[1], position=(lx, tab_y - 2))
                bui.imagewidget(edit=tb[2], position=(lx, tab_y - 2))
                bui.imagewidget(edit=tb[3], position=(lx + cw - t, tab_y - 2))

            self._tab_chat.set_position(lx + 3, tab_y)
            self._tab_players.set_position(lx + 3 + self._tab_w + self._tab_gap, tab_y)
            self._tab_servers.set_position(lx + 3 + (self._tab_w + self._tab_gap) * 2, tab_y)

            upd_extra = 0
            if show_upd:
                upd_h = 28
                upd_y = tab_y - 3 - upd_h
                upd_extra = upd_h + 4
                ubg = _draw_panel_bg(
                    parent=self._root_widget,
                    x=lx, y=upd_y, w=cw, h=upd_h,
                    color=(0.06, 0.14, 0.22), opacity=0.88)
                ubdrs = _draw_border(
                    parent=self._root_widget,
                    x=lx, y=upd_y, w=cw, h=upd_h,
                    color=(0.35, 0.92, 1.0), opacity=0.78, thickness=1.2)
                self._update_banner_widgets.append(ubg)
                self._update_banner_widgets.extend(ubdrs)
                self._update_banner_borders = list(ubdrs)

                rver = _apw_update_state.get("remote_version") or "New"
                utxt = bui.textwidget(
                    parent=self._root_widget,
                    position=(lx + 10, upd_y + upd_h * 0.5), size=(0, 0),
                    h_align='left', v_align='center',
                    text=f"🔔 Update v{rver} available!",
                    scale=0.50, color=(1.0, 0.90, 0.42), maxwidth=cw - 178)
                u_cls = GlassButton(
                    parent=self._root_widget, position=(lx + cw - 28, upd_y + 3), size=(24, upd_h - 6),
                    label='✕', text_scale=0.55,
                    bg_color=(0.24, 0.10, 0.12), opacity=0.60,
                    text_color=(1.0, 0.55, 0.55),
                    border=True, border_color=(1.0, 0.42, 0.45), border_opacity=0.80, border_thickness=1.0,
                    on_activate_call=self._dismiss_update_banner)
                u_gh = GlassButton(
                    parent=self._root_widget, position=(lx + cw - 92, upd_y + 3), size=(60, upd_h - 6),
                    label='GitHub', text_scale=0.45,
                    bg_color=(0.12, 0.24, 0.40), opacity=0.62,
                    text_color=(0.82, 0.94, 1.0),
                    border=True, border_color=(0.45, 0.80, 1.0), border_opacity=0.78, border_thickness=1.0,
                    on_activate_call=self._open_github_repo)
                u_up = GlassButton(
                    parent=self._root_widget, position=(lx + cw - 160, upd_y + 3), size=(64, upd_h - 6),
                    label='Update', text_scale=0.46,
                    bg_color=(0.12, 0.38, 0.22), opacity=0.68,
                    text_color=(0.86, 1.0, 0.88),
                    border=True, border_color=ol, border_opacity=0.88, border_thickness=1.0,
                    on_activate_call=self._start_manual_update_install)
                self._update_banner_widgets.extend([utxt, u_cls, u_gh, u_up])

            self._scroll_top = tab_y - 5 - upd_extra
            sb = self._full_scroll_bottom
            sh = max(80, self._scroll_top - sb)
            bui.imagewidget(edit=self._scroll_bg, position=(lx, sb), size=(cw, sh))
            scb = getattr(self, '_scroll_borders', [])
            if len(scb) == 4:
                bui.imagewidget(edit=scb[0], position=(lx, sb + sh - t), size=(cw, t))
                bui.imagewidget(edit=scb[1], position=(lx, sb), size=(cw, t))
                bui.imagewidget(edit=scb[2], position=(lx, sb), size=(t, sh))
                bui.imagewidget(edit=scb[3], position=(lx + cw - t, sb), size=(t, sh))
            bui.scrollwidget(
                edit=self._scrollwidget,
                position=(lx, self._chat_nav_scroll_bottom if self.active_tab == "chat" else sb),
                size=(self._scroll_width, max(60, self._scroll_top - (self._chat_nav_scroll_bottom if self.active_tab == "chat" else sb))))
        except Exception:
            pass

    def _update(self) -> None:
        self._refresh_input_ping_hint()
        new_roster = bs.get_game_roster()
        if new_roster != self._roster:
            self._roster = new_roster
            self._refresh_header_players()
            if self.active_tab == "players":
                self._render_players_tab()
        elif _apw_show_header_players():
            self._refresh_header_players()

    def _render_players_tab(self):
        for child in self._columnwidget.get_children():
            child.delete()
        self._roster_widgets.clear()

        roster = bs.get_game_roster() or []
        self._tab_players.set_text(f"👥 Roster ({len(roster)})")
        ol = getattr(self, '_outline_color', (0.4, 1.0, 0.5))

        if not roster:
            bui.textwidget(
                parent=self._columnwidget, size=(self._scroll_width, 60),
                h_align='center', v_align='center',
                text='No players connected', color=(0.6, 0.6, 0.6), scale=0.75)
            return

        for entry in roster:
            cid = entry.get('client_id', -1)
            v2_id = entry.get('display_string', 'Unknown')
            players = entry.get('players', [])
            if players:
                p_names = [str(p.get('name_full') or p.get('name') or '').strip() for p in players]
                p_names = [x for x in p_names if x]
                name = ", ".join(p_names) if p_names else v2_id
            else:
                name = v2_id
            is_host = (cid == -1)

            nick = self._get_nick(v2_id)
            display_title = f"{name} ({nick})" if nick != "add nick" else name

            row_h = 54
            row_w = self._scroll_width - 8
            row = bui.containerwidget(parent=self._columnwidget, size=(row_w, row_h), background=False)

            bui.imagewidget(
                parent=row, size=(row_w, row_h - 4), position=(0, 2),
                texture=bui.gettexture('softRect'), opacity=0.28 if is_host else 0.22,
                color=(0.10, 0.45, 0.28) if is_host else (0.14, 0.22, 0.34))
            _draw_border(
                row, 0, 2, row_w, row_h - 4,
                color=(0.45, 1.0, 0.55) if is_host else ol,
                opacity=0.45 if is_host else 0.22, thickness=1.0)

            prefix = '\ue027 ' if is_host else ''
            player_col, nick_col = _apw_get_roster_colors()
            name_str = f"{prefix}{name}"
            has_nick = bool(nick and nick != "add nick")
            avail_w = row_w - 186

            if has_nick:
                name_max_w = max(80, avail_w - 75)
                bui.textwidget(
                    parent=row, position=(12, 34), size=(0, 0),
                    h_align='left', v_align='center',
                    text=babase.Lstr(value=name_str),
                    color=(1.0, 0.9, 0.4) if is_host else player_col,
                    scale=0.68, maxwidth=name_max_w)
                try:
                    raw_w = float(bui.get_string_width(name_str, suppress_warning=True)) * 0.68
                except Exception:
                    raw_w = len(name_str) * 8.5
                drawn_name_w = min(float(name_max_w), raw_w)
                nick_x = 12 + drawn_name_w + 6
                nick_max_w = max(32, avail_w - drawn_name_w - 6)
                bui.textwidget(
                    parent=row, position=(nick_x, 34), size=(0, 0),
                    h_align='left', v_align='center',
                    text=babase.Lstr(value=f"({nick})"),
                    color=nick_col,
                    scale=0.62, maxwidth=nick_max_w)
            else:
                bui.textwidget(
                    parent=row, position=(12, 34), size=(0, 0),
                    h_align='left', v_align='center',
                    text=babase.Lstr(value=name_str),
                    color=(1.0, 0.9, 0.4) if is_host else player_col,
                    scale=0.68, maxwidth=avail_w)

            cid_tag = "HOST" if is_host else f"CID: {cid}"
            bui.textwidget(
                parent=row, position=(12, 15), size=(0, 0),
                h_align='left', v_align='center',
                text=f"ID: {v2_id} • {cid_tag}", color=(0.62, 0.78, 0.94),
                scale=0.46, maxwidth=row_w - 186)

            GlassButton(
                parent=row, position=(row_w - 174, (row_h - 28) // 2),
                size=(34, 28), label='🛠️', text_scale=0.58,
                bg_color=(0.18, 0.24, 0.36), opacity=0.45,
                text_color=(1.0, 0.90, 0.55),
                border=True, border_color=(0.85, 0.75, 0.35), border_opacity=0.70, border_thickness=1.1,
                on_activate_call=babase.CallPartial(self._on_party_member_commands_press, cid, is_host, row))

            info_gb = GlassButton(
                parent=row, position=(row_w - 134, (row_h - 28) // 2),
                size=(50, 28), label='Info', text_scale=0.58,
                bg_color=(0.10, 0.32, 0.46), opacity=0.42,
                text_color=(0.75, 0.96, 1.0),
                border=True, border_color=(0.35, 0.85, 1.0), border_opacity=0.75, border_thickness=1.2)
            info_gb.set_on_activate(
                babase.CallPartial(self._on_player_info_press, cid, info_gb.widget))

            GlassButton(
                parent=row, position=(row_w - 78, (row_h - 28) // 2),
                size=(70, 28), label='Actions', text_scale=0.58,
                bg_color=(0.18, 0.32, 0.48), opacity=0.42,
                text_color=(0.90, 0.95, 1.0),
                border=True, border_color=ol, border_opacity=0.70, border_thickness=1.2,
                on_activate_call=babase.CallPartial(self._on_party_member_press, cid, is_host, row))

    def _on_header_player_press(self, client_id: int, is_host: bool, widget: Optional[bui.Widget] = None) -> None:
        """Click handler for names under Party Name: opens native Host DocUI if offered, else Actions."""
        try:
            classic = bui.app.classic
            if classic is not None and hasattr(classic, 'host_ui'):
                browse = classic.host_ui.get_client_page_browse(client_id)
                if browse is None and hasattr(classic.host_ui, 'get_client_page'):
                    browse = classic.host_ui.get_client_page(client_id)
                if browse is not None:
                    from bauiv1lib.hostdocui import show_host_docui_page
                    show_host_docui_page(browse, origin_widget=widget)
                    self.close()
                    return
        except Exception:
            babase.print_exception("[APW] Header player DocUI open failed")
        self._on_party_member_press(client_id, is_host, widget if widget is not None else self._root_widget)

    def _on_player_info_press(self, client_id: int, widget: Optional[bui.Widget] = None) -> None:
        """Open BombSquad 1.8+ Host DocUI Player Page directly; fall back cleanly on older hosts."""
        origin = widget if widget is not None else self._root_widget

        try:
            classic = bui.app.classic
            if classic is not None and hasattr(classic, 'host_ui'):
                browse = classic.host_ui.get_client_page_browse(client_id)
                if browse is None and hasattr(classic.host_ui, 'get_client_page'):
                    browse = classic.host_ui.get_client_page(client_id)
                if browse is not None:
                    from bauiv1lib.hostdocui import show_host_docui_page
                    show_host_docui_page(browse, origin_widget=origin)
                    self.close()
                    return
        except Exception:
            babase.print_exception("[APW] Host DocUI open failed")

        entry = None
        for r in (bs.get_game_roster() or []):
            if r.get('client_id') == client_id:
                entry = r
                break
        if entry is None:
            bui.screenmessage('Player no longer in party.', color=(1, 0.5, 0.3))
            return
        self._open_alpha_player_info_modal(entry)

    def _open_alpha_player_info_modal(self, entry: Dict[str, Any]) -> None:
        """Sleek Cyber-Glass Player Info Inspector with live BombSquad account lookup."""
        cid = entry.get('client_id', -1)
        v2_id = entry.get('display_string', 'Unknown')
        players = entry.get('players', [])
        name = players[0].get('name_full', v2_id) if players else v2_id
        is_host = (cid == -1)
        nick = self._get_nick(v2_id)

        account_id = _apw_resolve_aid(client_id=cid, v2_id=v2_id, is_self=is_host)

        mutual_count = 0
        try:
            if os.path.isfile(MutualServerFile):
                with open(MutualServerFile, 'r', encoding='utf-8') as f:
                    mdata = json.loads(f.read() or '{}')
                if v2_id in mdata and isinstance(mdata[v2_id], list):
                    mutual_count = len(mdata[v2_id])
        except Exception:
            pass

        c_width, c_height = 420, 355
        ol = getattr(self, '_outline_color', (0.4, 1.0, 0.5))
        uiscale = bui.app.ui_v1.uiscale

        cnt = bui.containerwidget(
            size=(c_width, c_height),
            scale=(1.6 if uiscale is babase.UIScale.SMALL else
                   1.25 if uiscale is babase.UIScale.MEDIUM else 1.0),
            transition='in_scale',
            background=False,
            parent=bui.get_special_widget('overlay_stack'))

        _draw_panel_bg(cnt, 0, 0, c_width, c_height, color=(0.05, 0.07, 0.11), opacity=0.95)
        _draw_border(cnt, 0, 0, c_width, c_height, color=ol, opacity=0.85, thickness=1.5)

        def _close():
            try:
                bui.getsound('swish').play()
            except Exception:
                pass
            bui.containerwidget(edit=cnt, transition='out_scale')

        ghost_cancel = bui.buttonwidget(
            parent=cnt, position=(-9000, -9000), size=(1, 1), label='', on_activate_call=_close)
        bui.containerwidget(edit=cnt, cancel_button=ghost_cancel)

        role_txt = "👑 HOST" if is_host else f"👤 CLIENT #{cid}"
        bui.textwidget(
            parent=cnt, position=(c_width * 0.5, c_height - 20), size=(0, 0),
            h_align='center', v_align='center',
            text=f"ℹ️ Player Info • {name}", scale=0.80, maxwidth=c_width - 80,
            color=(0.98, 1.0, 0.65))

        GlassButton(
            parent=cnt, position=(c_width - 34, c_height - 34), size=(26, 26),
            label='✕', text_scale=0.8, bg_color=(0.18, 0.08, 0.09), opacity=0.35,
            text_color=(1.0, 0.50, 0.50), border=True, border_color=(1.0, 0.40, 0.45),
            border_opacity=0.80, border_thickness=1.2, on_activate_call=_close)

        card_x, card_y, card_w, card_h = 8, c_height - 138, c_width - 16, 94
        _draw_panel_bg(cnt, card_x, card_y, card_w, card_h, color=(0.08, 0.12, 0.18), opacity=0.55)
        _draw_border(cnt, card_x, card_y, card_w, card_h, color=ol, opacity=0.45, thickness=1.0)

        nick_disp = nick if nick != "add nick" else "None set"
        info_lines = [
            (f"Role: {role_txt}   |   Mutual Servers: {mutual_count}", (0.45, 0.95, 0.65)),
            (f"Display / V2 Tag: {v2_id}", (0.85, 0.94, 1.0)),
            (f"Account ID: {account_id or 'Local / Unavailable'}", (0.68, 0.82, 0.98)),
            (f"Custom Nickname: {nick_disp}", (1.0, 0.85, 0.45)),
        ]
        for idx_l, (ltxt, lcol) in enumerate(info_lines):
            bui.textwidget(
                parent=cnt, position=(card_x + 10, card_y + card_h - 16 - idx_l * 21),
                size=(0, 0), h_align='left', v_align='center',
                text=ltxt, scale=0.54, color=lcol, maxwidth=card_w - 20)

        stats_x, stats_y, stats_w, stats_h = 8, 50, c_width - 16, card_y - 56
        _draw_panel_bg(cnt, stats_x, stats_y, stats_w, stats_h, color=(0.04, 0.06, 0.10), opacity=0.55)
        _draw_border(cnt, stats_x, stats_y, stats_w, stats_h, color=ol, opacity=0.40, thickness=1.0)

        fallback_txt = (
            "Host DocUI page not offered by this server (1.7 / custom protocol)."
            if not account_id else
            f"Resolved Account ID: {account_id}\nHost DocUI page not offered by this server."
        )
        bui.textwidget(
            parent=cnt, position=(c_width * 0.5, stats_y + stats_h * 0.5),
            size=(0, 0), h_align='center', v_align='center',
            text=fallback_txt,
            scale=0.50, color=(0.68, 0.80, 0.92), maxwidth=stats_w - 20)

        btn_y = 8
        btn_h = 34
        bw = (c_width - 28) / 3
        weak_self = weakref.ref(self)

        def _copy_id():
            target_copy = str(account_id or v2_id)
            if bui.clipboard_is_supported():
                bui.clipboard_set_text(target_copy)
                bui.screenmessage(f'Copied ID: {target_copy}', color=(0.4, 1.0, 0.4))

        def _mention():
            inst = weak_self()
            if inst is not None:
                try:
                    curr = bui.textwidget(query=inst._text_field)
                    bui.textwidget(edit=inst._text_field, text=f"{curr}@{v2_id} ")
                    inst._refresh_input_ping_hint()
                except Exception:
                    pass
            _close()

        def _open_official():
            inst = weak_self()
            try:
                _close()
                if bui.app.classic is not None and hasattr(bui.app.classic, 'host_ui'):
                    browse = bui.app.classic.host_ui.get_client_page_browse(cid)
                    if browse is not None:
                        from bauiv1lib.hostdocui import show_host_docui_page
                        show_host_docui_page(browse)
                        if inst is not None:
                            inst.close()
                        return
                from bauiv1lib.account.viewer import AccountViewerWindow
                if account_id and account_id.startswith('pb-'):
                    AccountViewerWindow(account_id=account_id)
                else:
                    bui.screenmessage('Original Host DocUI is unavailable on this 1.7 server.', color=(1, 0.65, 0.35))
            except Exception as e:
                bui.screenmessage(f'Unavailable: {e}', color=(1, 0.4, 0.4))

        GlassButton(
            parent=cnt, position=(8, btn_y), size=(bw, btn_h),
            label='📋 Copy ID', text_scale=0.58,
            bg_color=(0.12, 0.22, 0.34), opacity=0.45,
            border=True, border_color=ol, border_opacity=0.70, border_thickness=1.2,
            on_activate_call=_copy_id)

        GlassButton(
            parent=cnt, position=(14 + bw, btn_y), size=(bw, btn_h),
            label='@ Mention', text_scale=0.58,
            bg_color=(0.12, 0.32, 0.22), opacity=0.45,
            border=True, border_color=ol, border_opacity=0.70, border_thickness=1.2,
            on_activate_call=_mention)

        GlassButton(
            parent=cnt, position=(20 + bw * 2, btn_y), size=(bw, btn_h),
            label='🌐 Full Profile', text_scale=0.58,
            bg_color=(0.18, 0.22, 0.42), opacity=0.45,
            border=True, border_color=(0.45, 0.80, 1.0), border_opacity=0.75, border_thickness=1.2,
            on_activate_call=_open_official)

    def _render_servers_tab(self):
        for child in self._columnwidget.get_children():
            child.delete()

        servers = self._get_saved_servers()
        ol = getattr(self, '_outline_color', (0.4, 1.0, 0.5))

        top_row = bui.containerwidget(parent=self._columnwidget, size=(self._scroll_width - 8, 38), background=False)
        GlassButton(
            parent=top_row, position=(4, 3),
            size=((self._scroll_width - 24) // 2, 32),
            label='⭐ Save This Server', text_scale=0.65,
            bg_color=(0.14, 0.42, 0.25), opacity=0.48,
            border=True, border_color=ol, border_opacity=0.75, border_thickness=1.2,
            on_activate_call=self._save_current_server_direct)

        GlassButton(
            parent=top_row,
            position=(12 + (self._scroll_width - 24) // 2, 3),
            size=((self._scroll_width - 24) // 2, 32),
            label='➕ Add Server', text_scale=0.65,
            bg_color=(0.14, 0.32, 0.52), opacity=0.45,
            border=True, border_color=ol, border_opacity=0.75, border_thickness=1.2,
            on_activate_call=self._open_add_server_window)

        if not servers:
            bui.textwidget(
                parent=self._columnwidget, size=(self._scroll_width, 80),
                h_align='center', v_align='center',
                text='No saved servers yet.\nClick above to bookmark your current game!',
                color=(0.6, 0.6, 0.6), scale=0.7)
            return

        for idx, srv in enumerate(servers):
            srv_name = srv.get('name', 'Server')
            srv_addr = srv.get('addr', '?')
            srv_port = srv.get('port', 43210)

            s_row = bui.containerwidget(parent=self._columnwidget, size=(self._scroll_width - 8, 50), background=False)
            bui.imagewidget(
                parent=s_row, size=(self._scroll_width - 8, 46), position=(0, 2),
                texture=bui.gettexture('softRect'), opacity=0.22,
                color=(0.10, 0.16, 0.24))
            _draw_border(s_row, 0, 2, self._scroll_width - 8, 46, color=ol, opacity=0.25, thickness=1.0)

            bui.textwidget(
                parent=s_row, position=(12, 33), size=(0, 0),
                h_align='left', v_align='center',
                text=srv_name, color=(1, 1, 0.8), scale=0.72,
                maxwidth=self._scroll_width - 160)

            bui.textwidget(
                parent=s_row, position=(12, 15), size=(0, 0),
                h_align='left', v_align='center',
                text=f"{srv_addr}:{srv_port}", color=(0.6, 0.78, 0.94), scale=0.52)

            GlassButton(
                parent=s_row, position=(self._scroll_width - 146, 11),
                size=(60, 28), label='Join', text_scale=0.6,
                bg_color=(0.14, 0.45, 0.25), opacity=0.48,
                border=True, border_color=(0.35, 1.0, 0.55), border_opacity=0.75, border_thickness=1.2,
                on_activate_call=babase.CallPartial(self._direct_connect, srv_addr, srv_port))

            GlassButton(
                parent=s_row, position=(self._scroll_width - 78, 11),
                size=(60, 28), label='Delete', text_scale=0.6,
                bg_color=(0.45, 0.14, 0.16), opacity=0.48,
                border=True, border_color=(1.0, 0.40, 0.45), border_opacity=0.75, border_thickness=1.2,
                on_activate_call=babase.CallPartial(self._delete_saved_server, idx))

    def _direct_connect(self, addr, port):
        self.close()
        newconnect_to_party(addr, int(port))

    def _delete_saved_server(self, idx):
        svrs = self._get_saved_servers()
        if 0 <= idx < len(svrs):
            svrs.pop(idx)
            self._write_saved_servers(svrs)
            self._render_servers_tab()

    def _save_current_server_direct(self):
        info = bs.get_connection_to_host_info_2()
        if not info:
            bui.screenmessage('Not connected to any server!', color=(1, 0.3, 0.3))
            return
        srv_name = info.get('name', 'Server') if isinstance(info, dict) else getattr(info, 'name', 'Server')
        svrs = self._get_saved_servers()
        for s in svrs:
            if s.get('addr') == ip_add and s.get('port') == p_port:
                bui.screenmessage('Server already saved!', color=(1, 0.8, 0.2))
                return
        svrs.append({'name': srv_name, 'addr': ip_add, 'port': int(p_port)})
        self._write_saved_servers(svrs)
        bui.getsound('gunCocking').play()
        bui.screenmessage(f"Saved '{srv_name}'!", color=(0.2, 1, 0.4))
        self._render_servers_tab()

    def _is_msg_muted(self, msg: str) -> bool:
        if not muted_chat_names:
            return False
        sender = msg.split(':', 1)[0].strip()
        sender_clean = re.sub(r'[\ue000-\uf8ff]', '', sender).strip().strip("'")
        for muted in muted_chat_names:
            if sender_clean == re.sub(r'[\ue000-\uf8ff]', '', muted).strip().strip("'"):
                return True
        return False

    def _add_msg(self, msg: str, ignore_mute: bool = False) -> None:
        if self.active_tab != "chat":
            return
        if not ignore_mute and self._is_msg_muted(msg):
            return
        try:
            if getattr(self, '_chat_empty_holder', None) is not None:
                try:
                    self._chat_empty_holder.delete()
                except Exception:
                    pass
                self._chat_empty_holder = None

            my_name = babase.app.plus.get_v1_account_display_string() if babase.app.plus else ''
            is_mention = (my_name and f"@{my_name}".lower() in msg.lower())
            if is_mention:
                base_col = (1.0, 0.82, 0.35)
            elif _apw_is_colorful_chat():
                base_col = _apw_get_chat_sender_color(msg)
            else:
                base_col = (0.90, 0.95, 1.00)

            row_w = self._scroll_width - 10
            row = bui.containerwidget(parent=self._columnwidget, size=(row_w, 22), background=False)
            hit = bui.buttonwidget(
                parent=row, position=(0, 0), size=(row_w, 22),
                texture=bui.gettexture('empty'), label='', color=(1, 1, 1),
                autoselect=True, extra_touch_border_scale=0.0)
            txt = bui.textwidget(
                parent=row,
                text=babase.Lstr(value=msg),
                position=(8, 11),
                h_align='left', v_align='center',
                size=(0, 0),
                scale=0.62,
                color=base_col,
                maxwidth=row_w - 18,
                shadow=0.3, flatness=1.0,
                draw_controller=hit)

            bui.buttonwidget(edit=hit, on_activate_call=babase.CallPartial(self._on_chat_press, msg, row))
            item_obj = {"row": row, "widget": txt, "msg": msg, "base_color": base_col, "translated": None}
            self._chat_items.append(item_obj)
            if _apw_get_translate_cfg()["enabled"]:
                self._translate_item_async(item_obj)
            self._chat_texts_haxx.append(row)
            if len(self._chat_texts_haxx) > 50:
                first = self._chat_texts_haxx.pop(0)
                if self._chat_items and self._chat_items[0].get("row") == first:
                    self._chat_items.pop(0)
                    if self._selected_chat_idx > 0:
                        self._selected_chat_idx -= 1
                    elif self._selected_chat_idx == 0:
                        self._selected_chat_idx = -1
                try:
                    first.delete()
                except Exception:
                    pass
            bui.containerwidget(edit=self._columnwidget, visible_child=row)
        except Exception:
            pass

    def _on_chat_press(self, msg, widget):
        clicked_idx = -1
        for i, it in enumerate(self._chat_items):
            if it.get("row") == widget or it["widget"] == widget:
                clicked_idx = i
                break
        if clicked_idx != -1:
            if clicked_idx == self._selected_chat_idx:
                self._select_chat_index(-1)
                return
            self._select_chat_index(clicked_idx)
            is_translated = bool(self._chat_items[clicked_idx].get("translated"))
        else:
            self.msg_user_selected = msg
            is_translated = False
        self._popup_type = "chatmessagepress"
        tr_label = '🔄 Revert Translation' if is_translated else '🌐 Translate Msg'
        AlphaPopupMenu(
            position=widget.get_screen_space_center(),
            choices=['translate', 'copy', 'reply'],
            choices_display=[tr_label, '📋 Copy Message', '↩ Reply'],
            current_choice='translate', delegate=self)

    def _on_quick_button_click(self):
        replies = self._get_quick_responds()
        choices = ["__manage_quick__"] + list(replies)
        choices_display = ["➕ Add / Manage Quick Replies..."] + list(replies)
        self._popup_type = "QuickMessageSelect"
        AlphaPopupMenu(
            position=self._quick_button.widget.get_screen_space_center(),
            choices=choices, choices_display=choices_display,
            current_choice=replies[0] if replies else "__manage_quick__", delegate=self)

    def _send_chat_message(self) -> None:
        global draft_chat_text
        text = bui.textwidget(query=self._text_field).strip()
        if not text:
            return

        if text == ".ip":
            bs.chatmessage(f"IP {ip_add} PORT {p_port}")
            bui.textwidget(edit=self._text_field, text="")
            return
        elif text == ".info":
            info = bs.get_connection_to_host_info_2()
            s_build = info.get('build_number', 0) if isinstance(info, dict) else (getattr(info, 'build_number', 0) if info else 0)
            bs.chatmessage(f"Script version: {version_str} - build: {s_build}")
            bui.textwidget(edit=self._text_field, text="")
            return
        elif text == ".ping":
            bs.chatmessage(f"My ping: {current_ping} ms")
            bui.textwidget(edit=self._text_field, text="")
            return
        elif text == ".save":
            self._save_current_server_direct()
            bui.textwidget(edit=self._text_field, text="")
            return

        replacements = {
            '\\d': '\ue048', '\\c': '\ue043', '\\h': '\ue049',
            '\\s': '\ue046', '\\n': '\ue04b', '\\f': '\ue04f',
            '\\g': '\ue027', '\\i': '\ue03a', '\\m': '\ue04d',
            '\\t': '\ue01f', '\\bs': '\ue01e', '\\j': '\ue010',
            '\\e': '\ue045', '\\l': '\ue047', '\\a': '\ue020',
            '\\b': '\ue00c'
        }
        for k, v in replacements.items():
            text = text.replace(k, v)

        words = text.split(" ")
        if len(words) > 12:
            mid = len(words) // 2
            bs.chatmessage(" ".join(words[:mid]))
            bs.chatmessage(" ".join(words[mid:]))
        else:
            bs.chatmessage(text)

        bui.textwidget(edit=self._text_field, text="")
        draft_chat_text = ''

    def _on_party_member_commands_press(self, client_id: int, is_host: bool, widget: bui.Widget) -> None:
        self._popup_party_member_client_id = client_id
        self._popup_party_member_is_host = is_host
        self._popup_type = "partyMemberCommands"

        choices = []
        choices_display = []
        for idx, cmd_entry in enumerate(self._get_custom_commands()):
            lbl = (cmd_entry.get("label") or cmd_entry.get("cmd") or f"Cmd {idx + 1}").strip()
            choices.append(f"cmd:{idx}")
            choices_display.append(babase.Lstr(value=lbl))

        choices.append("open_cmd_maker")
        choices_display.append(babase.Lstr(value="Command Maker..."))

        AlphaPopupMenu(
            position=widget.get_screen_space_center(),
            choices=choices, choices_display=choices_display,
            current_choice=choices[0] if choices else "open_cmd_maker", delegate=self)

    def _on_party_member_press(self, client_id: int, is_host: bool, widget: bui.Widget) -> None:
        self._popup_party_member_client_id = client_id
        self._popup_party_member_is_host = is_host
        self._popup_type = "partyMemberPress"

        account = self._getObjectByID("account", client_id) or ""
        _is_chat_muted = any(
            m == account or _apw_clean_name(m) == _apw_clean_name(account)
            for m in muted_chat_names
        ) if account else False

        aid = ""
        try:
            aid = str(_apw_resolve_aid(client_id=client_id, v2_id=account, is_self=is_host) or "")
        except Exception:
            aid = ""
        ag_map = _apw_get_autogreet_players()
        in_ag = _apw_find_autogreet_key(aid, account, ag_map) is not None

        choices = ["@ this guy", "mute_chat", "set_nick", "toggle_autogreet", "complaint"]
        choices_display = [
            _getTransText("Mention_this_guy", isBaLstr=True),
            babase.Lstr(value="🔊 Unmute Chat" if _is_chat_muted else "🔇 Mute Chat"),
            babase.Lstr(value="🏷️ Set Nick"),
            babase.Lstr(value="👋 Remove Auto Greet" if in_ag else "👋 Add Auto Greet"),
            _getTransText("complaint", isBaLstr=True),
        ]

        AlphaPopupMenu(
            position=widget.get_screen_space_center(),
            choices=choices, choices_display=choices_display,
            current_choice="@ this guy", delegate=self)

    def _open_complaint_window(self, preselected_client_id=None) -> None:
        roster = bs.get_game_roster() or []
        player_list = []
        for entry in roster:
            cid = entry.get('client_id', -1)
            v2_id = entry.get('display_string', 'Unknown')
            players = entry.get('players', [])
            current_name = players[0].get('name_full', v2_id) if players else v2_id
            player_list.append({'client_id': cid, 'v2_id': v2_id, 'current_name': current_name})

        if preselected_client_id is not None:
            match = next((p for p in player_list if p['client_id'] == preselected_client_id), None)
            if match:
                self._show_complaint_form(match)
                return

        uiscale = bui.app.ui_v1.uiscale
        ol = getattr(self, '_outline_color', (0.4, 1.0, 0.5))
        c_width = 410
        list_h = max(60, min(len(player_list) * 44, 280))
        c_height = list_h + 96

        cnt = bui.containerwidget(
            scale=(1.8 if uiscale is babase.UIScale.SMALL else 1.35 if uiscale is babase.UIScale.MEDIUM else 1.0),
            size=(c_width, c_height), transition='in_scale', background=False,
            parent=bui.get_special_widget('overlay_stack'))

        _draw_panel_bg(cnt, 0, 0, c_width, c_height, color=(0.05, 0.07, 0.11), opacity=0.95)
        _draw_border(cnt, 0, 0, c_width, c_height, color=ol, opacity=0.85, thickness=1.5)

        bui.textwidget(parent=cnt, position=(c_width * 0.5, c_height - 22), size=(0, 0),
                       h_align='center', v_align='center',
                       text=_getTransText("complaint_select_offender", same_fb=True),
                       color=(1, 1, 0), scale=0.82)

        _draw_panel_bg(cnt, 8, 50, c_width - 16, list_h, color=(0.02, 0.04, 0.07), opacity=0.65)
        _draw_border(cnt, 8, 50, c_width - 16, list_h, color=ol, opacity=0.45, thickness=1.0)
        scroll = bui.scrollwidget(parent=cnt, size=(c_width - 16, list_h), position=(8, 50), color=(0.04, 0.06, 0.10))
        col = bui.columnwidget(parent=scroll, border=2, margin=0)

        for p in player_list:
            btn_label = f"{p['current_name']}  ({p['v2_id']})"
            def _on_select(player=p, c=cnt):
                bui.containerwidget(edit=c, transition='out_scale')
                self._show_complaint_form(player)

            GlassButton(parent=col, position=(0, 0), size=(c_width - 28, 38),
                        label=btn_label, text_scale=0.66, bg_color=(0.12, 0.18, 0.28),
                        opacity=0.38, border=True, border_color=ol, border_opacity=0.45, border_thickness=1.0,
                        on_activate_call=_on_select)

        GlassButton(
            parent=cnt, size=(120, 34), position=(c_width * 0.5 - 60, 8),
            label=babase.Lstr(resource='backText', fallback_value='Back'),
            bg_color=(0.35, 0.14, 0.16), opacity=0.45,
            border=True, border_color=(1.0, 0.45, 0.48), border_opacity=0.75, border_thickness=1.2,
            on_activate_call=babase.CallStrict(lambda: bui.containerwidget(edit=cnt, transition='out_scale')))
        ghost_cancel = bui.buttonwidget(
            parent=cnt, position=(-9000, -9000), size=(1, 1), label='',
            on_activate_call=babase.CallStrict(lambda: bui.containerwidget(edit=cnt, transition='out_scale')))
        bui.containerwidget(edit=cnt, cancel_button=ghost_cancel)

    def _show_complaint_form(self, offender_info: dict) -> None:
        uiscale = bui.app.ui_v1.uiscale
        ol = getattr(self, '_outline_color', (0.4, 1.0, 0.5))
        host_info = bs.get_connection_to_host_info_2()
        server_name = (host_info.get('name', 'Unknown Server') if isinstance(host_info, dict) else getattr(host_info, 'name', 'Unknown Server')) if host_info else 'Unknown Server'

        try:
            my_v2_id = babase.app.plus.get_v1_account_display_string() if babase.app.plus else 'Unknown'
        except Exception:
            my_v2_id = 'Unknown'
        my_current_name = my_v2_id
        my_cid = None
        for entry in (bs.get_game_roster() or []):
            if entry.get('display_string') == my_v2_id:
                my_cid = entry.get('client_id')
                ps = entry.get('players', [])
                if ps:
                    my_current_name = ps[0].get('name_full', my_v2_id)
                break

        off_cid = offender_info.get('client_id')
        off_v2_id = offender_info.get('v2_id', 'Unknown')
        off_current_name = offender_info.get('current_name', 'Unknown')

        my_aid = _apw_resolve_aid(client_id=my_cid, v2_id=my_v2_id, is_self=True)
        off_aid = _apw_resolve_aid(client_id=off_cid, v2_id=off_v2_id, is_self=(off_cid == -1))

        my_bracket = f"{my_v2_id}, {my_aid}" if (my_aid and my_aid != my_v2_id) else my_v2_id
        off_bracket = f"{off_v2_id}, {off_aid}" if (off_aid and off_aid != off_v2_id) else off_v2_id

        c_width = 430
        c_height = 334

        cnt = bui.containerwidget(
            scale=(1.45 if uiscale is babase.UIScale.SMALL else 1.15 if uiscale is babase.UIScale.MEDIUM else 1.0),
            size=(c_width, c_height), transition='in_scale', background=False,
            parent=bui.get_special_widget('overlay_stack'))

        _draw_panel_bg(cnt, 0, 0, c_width, c_height, color=(0.05, 0.07, 0.11), opacity=0.95)
        _draw_border(cnt, 0, 0, c_width, c_height, color=ol, opacity=0.85, thickness=1.5)

        bui.textwidget(parent=cnt, position=(c_width * 0.5, c_height - 20), size=(0, 0),
                       h_align='center', v_align='center', text=_getTransText("complaint_window_title", same_fb=True),
                       color=(1, 0.9, 0.2), scale=0.85)

        card_x, card_y, card_w, card_h = 10, c_height - 114, c_width - 20, 74
        _draw_panel_bg(cnt, card_x, card_y, card_w, card_h, color=(0.08, 0.11, 0.17), opacity=0.55)
        _draw_border(cnt, card_x, card_y, card_w, card_h, color=ol, opacity=0.40, thickness=1.0)

        lbls = [
            ("Server Name:", server_name),
            ("Complainer:", f"{my_current_name} ({my_bracket})"),
            ("Offender:", f"{off_current_name} ({off_bracket})")
        ]
        y = card_y + card_h - 14
        for l, v in lbls:
            bui.textwidget(parent=cnt, position=(card_x + 10, y), size=(0, 0), h_align='left', v_align='center',
                           text=l, color=(0.7, 0.85, 1.0), scale=0.56)
            bui.textwidget(parent=cnt, position=(card_x + 108, y), size=(0, 0), h_align='left', v_align='center',
                           text=v, color=(1, 1, 1), scale=0.55, maxwidth=card_w - 118)
            y -= 22

        bui.textwidget(parent=cnt, position=(12, card_y - 14), size=(0, 0), h_align='left', v_align='center',
                       text="Reason:", color=(0.7, 0.85, 1.0), scale=0.56)
        y = card_y - 54

        TAG_ROW1 = ['Abuse', 'Rejoin', 'Betraying']
        TAG_ROW2 = ['Parental Abuse', 'Spamming']
        desc_ref = [None]

        def _make_tag_cb(t):
            def _cb():
                if desc_ref[0] is not None:
                    curr = bui.textwidget(query=desc_ref[0]) or ''
                    sep = ', ' if curr.strip() else ''
                    bui.textwidget(edit=desc_ref[0], text=f"{curr}{sep}{t}")
            return _cb

        btn_w = (c_width - 20 - 12) // 3
        for i, tag in enumerate(TAG_ROW1):
            GlassButton(parent=cnt, size=(btn_w, 26), position=(10 + i * (btn_w + 6), y),
                        label=tag, text_scale=0.54, bg_color=(0.14, 0.24, 0.38), opacity=0.45,
                        border=True, border_color=ol, border_opacity=0.55, border_thickness=1.0,
                        on_activate_call=_make_tag_cb(tag))
        y -= 32
        btn_w2 = (c_width - 20 - 6) // 2
        for i, tag in enumerate(TAG_ROW2):
            GlassButton(parent=cnt, size=(btn_w2, 26), position=(10 + i * (btn_w2 + 6), y),
                        label=tag, text_scale=0.54, bg_color=(0.14, 0.24, 0.38), opacity=0.45,
                        border=True, border_color=ol, border_opacity=0.55, border_thickness=1.0,
                        on_activate_call=_make_tag_cb(tag))

        bui.textwidget(parent=cnt, position=(12, y - 14), size=(0, 0), h_align='left', v_align='center',
                       text="Details:", color=(0.7, 0.85, 1.0), scale=0.54)
        desc_y = 58
        desc_field = _draw_glass_textbox(
            cnt, 10, desc_y, c_width - 20, 42, ol=ol,
            max_chars=300, opacity=0.70, border_opacity=0.65, border_thickness=1.2,
            description=_getTransText("complaint_description_hint", same_fb=True))
        desc_ref[0] = desc_field

        def _close():
            bui.containerwidget(edit=cnt, transition='out_scale')

        ghost_cancel = bui.buttonwidget(parent=cnt, position=(-9000, -9000), size=(1, 1), label='', on_activate_call=_close)
        bui.containerwidget(edit=cnt, cancel_button=ghost_cancel)

        def _copy():
            desc = bui.textwidget(query=desc_field)
            txt = (f"--- Complaint ---\nServer: {server_name}\nComplainer: {my_current_name} ({my_bracket})\n"
                   f"Offender: {off_current_name} ({off_bracket})\nDescription: {desc if desc else '(None)'}\n-----------------")
            if bui.clipboard_is_supported():
                bui.clipboard_set_text(txt)
                bui.screenmessage(_getTransText("complaint_copied", same_fb=True), color=(0, 1, 0))

        GlassButton(parent=cnt, size=(160, 34), position=(10, 12), label='Back',
                    bg_color=(0.35, 0.16, 0.18), opacity=0.45,
                    border=True, border_color=(1.0, 0.45, 0.48), border_opacity=0.75, border_thickness=1.2,
                    on_activate_call=_close)
        GlassButton(parent=cnt, size=(160, 34), position=(c_width - 170, 12), label='Copy Complaint',
                    bg_color=(0.14, 0.42, 0.24), opacity=0.50,
                    border=True, border_color=ol, border_opacity=0.85, border_thickness=1.2,
                    on_activate_call=_copy)

    def _get_saved_servers(self) -> list:
        servers = babase.app.config.get('APW_Saved_Servers', [])
        return servers if isinstance(servers, list) else []

    def _write_saved_servers(self, servers: list) -> None:
        babase.app.config['APW_Saved_Servers'] = servers
        babase.app.config.commit()

    def _open_add_server_window(self) -> None:
        uiscale = bui.app.ui_v1.uiscale
        ol = getattr(self, '_outline_color', (0.4, 1.0, 0.5))
        c_width, c_height = 400, 246
        cnt = bui.containerwidget(
            scale=(1.7 if uiscale is babase.UIScale.SMALL else 1.25 if uiscale is babase.UIScale.MEDIUM else 1.0),
            size=(c_width, c_height), transition='in_scale', background=False,
            parent=bui.get_special_widget('overlay_stack'))

        _draw_panel_bg(cnt, 0, 0, c_width, c_height, color=(0.05, 0.07, 0.11), opacity=0.95)
        _draw_border(cnt, 0, 0, c_width, c_height, color=ol, opacity=0.85, thickness=1.5)

        bui.textwidget(parent=cnt, position=(c_width * 0.5, c_height - 20), size=(0, 0),
                       h_align='center', v_align='center', text='Add Saved Server', color=(1, 0.85, 0.2), scale=0.82)

        bui.textwidget(parent=cnt, position=(12, c_height - 52), size=(0, 0), text='Server Name:', color=(0.7, 0.85, 1.0), scale=0.58)
        n_field = _draw_glass_textbox(cnt, 12, c_height - 88, c_width - 24, 30, ol=ol, max_chars=40, opacity=0.70, border_opacity=0.55, border_thickness=1.0)

        bui.textwidget(parent=cnt, position=(12, c_height - 108), size=(0, 0), text='IP Address:', color=(0.7, 0.85, 1.0), scale=0.58)
        ip_f = _draw_glass_textbox(cnt, 12, c_height - 144, c_width - 24, 30, ol=ol, max_chars=64, opacity=0.70, border_opacity=0.55, border_thickness=1.0)

        bui.textwidget(parent=cnt, position=(12, c_height - 174), size=(0, 0), text='Port:', color=(0.7, 0.85, 1.0), scale=0.58)
        p_f = _draw_glass_textbox(cnt, 68, c_height - 188, 120, 30, ol=ol, text='43210', max_chars=6, opacity=0.70, border_opacity=0.55, border_thickness=1.0)

        weak_self = weakref.ref(self)

        def _save():
            s_name = bui.textwidget(query=n_field).strip()
            s_ip = bui.textwidget(query=ip_f).strip()
            s_p = bui.textwidget(query=p_f).strip()
            if not s_ip:
                bui.screenmessage('IP cannot be empty!', color=(1, 0.3, 0.3))
                return
            try:
                port = int(s_p)
            except Exception:
                port = 43210
            inst = weak_self()
            if inst is not None:
                svrs = inst._get_saved_servers()
                svrs.append({'name': s_name or f"{s_ip}:{port}", 'addr': s_ip, 'port': port})
                inst._write_saved_servers(svrs)
                if inst.active_tab == "servers":
                    inst._render_servers_tab()
            bui.containerwidget(edit=cnt, transition='out_scale')

        def _close():
            bui.containerwidget(edit=cnt, transition='out_scale')

        ghost_cancel = bui.buttonwidget(parent=cnt, position=(-9000, -9000), size=(1, 1), label='', on_activate_call=_close)
        bui.containerwidget(edit=cnt, cancel_button=ghost_cancel)

        GlassButton(parent=cnt, size=(120, 34), position=(12, 10), label='Cancel',
                    bg_color=(0.35, 0.16, 0.18), opacity=0.45,
                    border=True, border_color=(1.0, 0.45, 0.48), border_opacity=0.75, border_thickness=1.2,
                    on_activate_call=_close)
        GlassButton(parent=cnt, size=(120, 34), position=(c_width - 132, 10), label='Save',
                    bg_color=(0.14, 0.42, 0.24), opacity=0.50,
                    border=True, border_color=ol, border_opacity=0.85, border_thickness=1.2,
                    on_activate_call=_save)

    def _get_nick(self, acc_id: str) -> str:
        nicks = babase.app.config.get('players nick', {})
        return nicks.get(acc_id, "add nick") if isinstance(nicks, dict) else "add nick"

    def _open_set_nick_window(self, account_id: str) -> None:
        ol = getattr(self, '_outline_color', (0.4, 1.0, 0.5))
        c_width, c_height = 380, 152
        cnt = bui.containerwidget(size=(c_width, c_height), transition='in_scale', background=False, parent=bui.get_special_widget('overlay_stack'))
        _draw_panel_bg(cnt, 0, 0, c_width, c_height, color=(0.05, 0.07, 0.11), opacity=0.95)
        _draw_border(cnt, 0, 0, c_width, c_height, color=ol, opacity=0.85, thickness=1.5)
        bui.textwidget(parent=cnt, position=(c_width * 0.5, c_height - 22), size=(0, 0), h_align='center', v_align='center',
                       text=f'Set Nickname for {account_id}', scale=0.72, color=(1, 0.9, 0.3), maxwidth=c_width - 24)

        curr = self._get_nick(account_id)
        field = _draw_glass_textbox(
            cnt, 12, c_height - 84, c_width - 24, 34, ol=ol,
            text='' if curr == 'add nick' else curr, max_chars=30,
            opacity=0.70, border_opacity=0.60, border_thickness=1.2)

        weak_self = weakref.ref(self)

        def _save():
            new_n = bui.textwidget(query=field).strip()
            cfg = babase.app.config
            if not isinstance(cfg.get('players nick'), dict):
                cfg['players nick'] = {}
            if new_n:
                cfg['players nick'][account_id] = new_n
            else:
                cfg['players nick'].pop(account_id, None)
            cfg.commit()
            bui.containerwidget(edit=cnt, transition='out_scale')
            inst = weak_self()
            if inst is not None and inst.active_tab == "players":
                inst._render_players_tab()

        def _close():
            bui.containerwidget(edit=cnt, transition='out_scale')

        ghost_cancel = bui.buttonwidget(parent=cnt, position=(-9000, -9000), size=(1, 1), label='', on_activate_call=_close)
        bui.containerwidget(edit=cnt, cancel_button=ghost_cancel)

        GlassButton(parent=cnt, size=(120, 34), position=(12, 10), label='Cancel',
                    bg_color=(0.35, 0.16, 0.18), opacity=0.45,
                    border=True, border_color=(1.0, 0.45, 0.48), border_opacity=0.75, border_thickness=1.2,
                    on_activate_call=_close)
        GlassButton(parent=cnt, size=(120, 34), position=(c_width - 132, 10), label='Save',
                    bg_color=(0.14, 0.42, 0.24), opacity=0.50,
                    border=True, border_color=ol, border_opacity=0.85, border_thickness=1.2,
                    on_activate_call=_save)

    def _getCustomSets(self):
        try:
            filePath = os.path.join(RecordFilesDir, "Settings.json")
            if os.path.isfile(filePath):
                with open(filePath, "r", encoding="utf-8") as Reader:
                    return json.loads(Reader.read()).get("Custom_PartyWindow_Sets", {})
        except Exception:
            pass
        return {}

    def _getObjectByID(self, obj_type="account", client_id=None):
        for roster in (bs.get_game_roster() or []):
            if roster.get("client_id") == client_id:
                if obj_type.lower() in ("account", "displaystring"):
                    return roster.get("display_string")
                elif obj_type.lower() in ("players", "playernamefull"):
                    return roster.get("players", [])
        return None

    def _get_quick_responds(self):
        filePath = os.path.join(RecordFilesDir, "Quickmessage.txt")
        if not os.path.isfile(filePath):
            return ["GG!", "Nice shot!", "Watch out!", "That was awesome!"]
        try:
            with open(filePath, "r", encoding="utf-8") as r:
                raw = r.read().replace("\\n", "\n")
                return [line.strip() for line in raw.splitlines() if line.strip()]
        except Exception:
            return ["GG!", "Nice shot!"]

    def _write_quick_responds(self, data):
        try:
            os.makedirs(RecordFilesDir, exist_ok=True)
            with open(os.path.join(RecordFilesDir, "Quickmessage.txt"), "w", encoding="utf-8") as writer:
                writer.write("\n".join(str(x).strip() for x in data if str(x).strip()))
        except Exception:
            pass

    def _open_quick_replies_window(self, prefill: str = "") -> None:
        ol = getattr(self, '_outline_color', (0.4, 1.0, 0.5))
        c_width, c_height = 460, 365
        uiscale = bui.app.ui_v1.uiscale
        weak_self = weakref.ref(self)

        cnt = bui.containerwidget(
            size=(c_width, c_height),
            scale=(1.45 if uiscale is babase.UIScale.SMALL else
                   1.16 if uiscale is babase.UIScale.MEDIUM else 1.0),
            transition='in_scale',
            background=False,
            parent=bui.get_special_widget('overlay_stack'))

        _draw_panel_bg(cnt, 0, 0, c_width, c_height, color=(0.05, 0.07, 0.11), opacity=0.96)
        _draw_border(cnt, 0, 0, c_width, c_height, color=ol, opacity=0.85, thickness=1.5)

        bui.textwidget(
            parent=cnt, position=(c_width * 0.5, c_height - 20), size=(0, 0),
            h_align='center', v_align='center',
            text='⚡ Quick Replies Manager', scale=0.80, color=(1.0, 0.88, 0.35))

        list_x, list_y, list_w, list_h = 12, 98, c_width - 24, c_height - 144
        _draw_panel_bg(cnt, list_x, list_y, list_w, list_h, color=(0.02, 0.04, 0.07), opacity=0.76)
        _draw_border(cnt, list_x, list_y, list_w, list_h, color=ol, opacity=0.48, thickness=1.1)
        scroll = bui.scrollwidget(
            parent=cnt, position=(list_x + 4, list_y + 4), size=(list_w - 8, list_h - 8),
            highlight=False, border_opacity=0.0)
        list_col = bui.columnwidget(parent=scroll, border=0, margin=3)

        replies = list(self._get_quick_responds())

        def _persist():
            inst = weak_self()
            if inst is not None:
                inst._write_quick_responds(replies)
            else:
                try:
                    os.makedirs(RecordFilesDir, exist_ok=True)
                    with open(os.path.join(RecordFilesDir, "Quickmessage.txt"), "w", encoding="utf-8") as w:
                        w.write("\n".join(replies))
                except Exception:
                    pass

        def _populate():
            for ch in list_col.get_children():
                ch.delete()
            row_w = list_w - 24
            if not replies:
                bui.textwidget(
                    parent=list_col, size=(row_w, 80),
                    h_align='center', v_align='center',
                    text='No quick replies saved. Add one below!',
                    scale=0.55, color=(0.65, 0.72, 0.82))
                return
            for idx, msg_s in enumerate(replies):
                rc = bui.containerwidget(parent=list_col, size=(row_w, 34), background=False)
                _draw_panel_bg(rc, 0, 2, row_w, 30, color=(0.09, 0.13, 0.20), opacity=0.62)
                _draw_border(rc, 0, 2, row_w, 30, color=ol, opacity=0.30, thickness=1.0)
                bui.textwidget(
                    parent=rc, position=(10, 17), size=(0, 0),
                    h_align='left', v_align='center',
                    text=babase.Lstr(value=msg_s), scale=0.54, color=(0.90, 0.96, 1.0),
                    maxwidth=row_w - 58)

                def _del_at(del_i=idx):
                    if 0 <= del_i < len(replies):
                        replies.pop(del_i)
                        _persist()
                        _populate()

                GlassButton(
                    parent=rc, position=(row_w - 34, 4), size=(28, 26),
                    label='✕', text_scale=0.52,
                    bg_color=(0.35, 0.14, 0.16), opacity=0.55,
                    text_color=(1.0, 0.65, 0.65),
                    border=True, border_color=(1.0, 0.42, 0.45), border_opacity=0.70, border_thickness=1.0,
                    on_activate_call=_del_at)

        _populate()

        add_field = _draw_glass_textbox(
            cnt, 12, 54, c_width - 108, 32, ol=ol,
            text=prefill, max_chars=120, opacity=0.78, border_opacity=0.65, border_thickness=1.1,
            description='New quick reply text...')

        def _add_reply():
            val = (bui.textwidget(query=add_field) or "").strip()
            if not val:
                bui.screenmessage("Enter a quick reply first!", color=(1.0, 0.45, 0.35))
                return
            if val not in replies:
                replies.append(val)
                _persist()
                _populate()
            bui.textwidget(edit=add_field, text="")
            bui.screenmessage("Quick reply added!", color=(0.4, 1.0, 0.5))

        def _reset_replies():
            replies[:] = ["GG!", "Nice shot!", "Watch out!", "That was awesome!"]
            _persist()
            _populate()
            bui.screenmessage("Restored default quick replies", color=(1.0, 0.85, 0.35))

        GlassButton(
            parent=cnt, position=(c_width - 88, 54), size=(76, 32),
            label='Add', text_scale=0.56,
            bg_color=(0.14, 0.38, 0.24), opacity=0.60,
            border=True, border_color=ol, border_opacity=0.85, border_thickness=1.1,
            on_activate_call=_add_reply)

        def _close():
            bui.containerwidget(edit=cnt, transition='out_scale')

        ghost_cancel = bui.buttonwidget(parent=cnt, position=(-9000, -9000), size=(1, 1), label='', on_activate_call=_close)
        bui.containerwidget(edit=cnt, cancel_button=ghost_cancel)

        GlassButton(
            parent=cnt, position=(12, 12), size=(136, 32),
            label='Reset Defaults', text_scale=0.50,
            bg_color=(0.30, 0.20, 0.12), opacity=0.50,
            border=True, border_color=(1.0, 0.75, 0.30), border_opacity=0.70, border_thickness=1.1,
            on_activate_call=_reset_replies)
        GlassButton(
            parent=cnt, position=(c_width - 132, 12), size=(120, 32),
            label='Done', text_scale=0.60,
            bg_color=(0.16, 0.24, 0.34), opacity=0.55,
            border=True, border_color=ol, border_opacity=0.85, border_thickness=1.2,
            on_activate_call=_close)

    _DEFAULT_CUSTOM_COMMANDS = [
        {"label": "Kick", "cmd": "/kick {cid}", "direct": True, "confirm": True},
    ]

    def _get_custom_commands(self) -> list:
        raw = babase.app.config.get('APW_Custom_Commands', None)
        if not isinstance(raw, list):
            return [dict(item) for item in self._DEFAULT_CUSTOM_COMMANDS]
        cleaned = []
        for item in raw:
            if isinstance(item, dict):
                cmd_s = str(item.get("cmd", "")).strip()
                lbl_s = str(item.get("label", "")).strip() or cmd_s
                if cmd_s:
                    cleaned.append({
                        "label": lbl_s[:28],
                        "cmd": cmd_s,
                        "direct": bool(item.get("direct", True)),
                        "confirm": bool(item.get("confirm", False)),
                    })
        return cleaned

    @staticmethod
    def _save_custom_commands(cmds: list) -> None:
        cfg = babase.app.config
        cfg['APW_Custom_Commands'] = [
            {
                "label": str(c.get("label", "")).strip()[:28],
                "cmd": str(c.get("cmd", "")).strip(),
                "direct": bool(c.get("direct", True)),
                "confirm": bool(c.get("confirm", False)),
            }
            for c in cmds if str(c.get("cmd", "")).strip()
        ]
        cfg.commit()

    def _resolve_command_template(self, template: str, client_id: int, duration: Optional[str] = None) -> str:
        acc = str(self._getObjectByID("account", client_id) or "").strip()
        players = self._getObjectByID("players", client_id) or []
        p_name = ""
        if players and isinstance(players, list):
            p_name = str(players[0].get("name_full") or players[0].get("name") or "").strip()
        if not p_name:
            p_name = acc or f"Client {client_id}"
        nick = self._get_nick(acc) if acc else "add nick"
        if not nick or nick == "add nick":
            nick = p_name
        try:
            aid = str(_apw_resolve_aid(client_id=client_id) or acc or "").strip()
        except Exception:
            aid = acc
        try:
            me = str(babase.app.plus.get_v1_account_display_string() or "Host").strip()
        except Exception:
            me = "Host"
        dur_str = str(duration if duration is not None else "1").strip()

        replacements = {
            "{cid}": str(client_id),
            "{acc}": acc or str(client_id),
            "{name}": p_name,
            "{nick}": nick,
            "{aid}": aid or str(client_id),
            "{me}": me,
            "{dur}": dur_str,
            "$cid": str(client_id),
            "$acc": acc or str(client_id),
            "$name": p_name,
            "$nick": nick,
            "$aid": aid or str(client_id),
            "$me": me,
            "$dur": dur_str,
        }
        out = template
        for k, v in replacements.items():
            out = out.replace(k, v)
        return out

    def _execute_custom_command(self, cmd_entry: dict, client_id: int, duration: Optional[str] = None) -> None:
        raw_cmd = str(cmd_entry.get("cmd", "") or "").strip()
        if not raw_cmd:
            return
        if duration is None and ("{dur}" in raw_cmd or "$dur" in raw_cmd):
            target = str(self._getObjectByID("account", client_id) or f"CID {client_id}")
            self._open_duration_picker_modal(dict(cmd_entry), client_id, target)
            return

        resolved = self._resolve_command_template(raw_cmd, client_id, duration=duration).strip()
        if not resolved:
            return
        if not cmd_entry.get("direct", True):
            try:
                bui.textwidget(edit=self._text_field, text=resolved + " ")
            except Exception:
                bui.textwidget(edit=self._text_field, text=resolved)
            bui.screenmessage(f"Drafted: {resolved}", color=(0.45, 0.85, 1.0))
            return
        if cmd_entry.get("confirm", False):
            target = str(self._getObjectByID("account", client_id) or f"CID {client_id}")
            self._open_confirm_command_modal(
                title_lbl=cmd_entry.get("label", "Run Command"),
                resolved_cmd=resolved,
                target_label=target,
            )
            return
        bs.chatmessage(resolved)
        bui.screenmessage(f"Sent: {resolved}", color=(0.4, 1.0, 0.5))

    def _open_duration_picker_modal(self, cmd_entry: dict, client_id: int, target_label: str) -> None:
        """Select a duration value for commands using {dur} / $dur."""
        ol = getattr(self, '_outline_color', (0.4, 1.0, 0.5))
        weak_self = weakref.ref(self)
        c_width, c_height = 410, 250
        uiscale = bui.app.ui_v1.uiscale
        cnt = bui.containerwidget(
            size=(c_width, c_height),
            scale=(1.48 if uiscale is babase.UIScale.SMALL else
                   1.18 if uiscale is babase.UIScale.MEDIUM else 1.0),
            transition='in_scale',
            background=False,
            parent=bui.get_special_widget('overlay_stack'))
        _draw_panel_bg(cnt, 0, 0, c_width, c_height, color=(0.05, 0.07, 0.11), opacity=0.96)
        _draw_border(cnt, 0, 0, c_width, c_height, color=ol, opacity=0.85, thickness=1.5)

        bui.textwidget(
            parent=cnt, position=(c_width * 0.5, c_height - 22), size=(0, 0),
            h_align='center', v_align='center',
            text=f"Duration: {cmd_entry.get('label', 'Command')}", scale=0.78, color=(1.0, 0.85, 0.35), maxwidth=c_width - 28)
        bui.textwidget(
            parent=cnt, position=(c_width * 0.5, c_height - 44), size=(0, 0),
            h_align='center', v_align='center',
            text=f"Target: {target_label}", scale=0.54, color=(0.72, 0.84, 0.96), maxwidth=c_width - 28)

        def _close():
            bui.containerwidget(edit=cnt, transition='out_scale')

        def _pick(sec_val: str):
            val = str(sec_val or '').strip()
            if not val:
                bui.screenmessage("Enter duration value!", color=(1.0, 0.35, 0.35))
                return
            _close()
            inst = weak_self()
            if inst is not None:
                inst._execute_custom_command(cmd_entry, client_id, duration=val)

        presets_r1 = [("1 Day", "1"), ("3 Days", "3"), ("7 Days", "7")]
        bw1 = (c_width - 36) / 3
        for idx, (lbl, sec) in enumerate(presets_r1):
            GlassButton(
                parent=cnt, position=(12 + idx * (bw1 + 6), c_height - 102), size=(bw1, 32),
                label=lbl, text_scale=0.58,
                bg_color=(0.12, 0.24, 0.36), opacity=0.50,
                border=True, border_color=ol, border_opacity=0.65, border_thickness=1.1,
                on_activate_call=babase.CallPartial(_pick, sec))

        presets_r2 = [("14 Days", "14"), ("30 Days", "30"), ("Permanent (0)", "0")]
        for idx, (lbl, sec) in enumerate(presets_r2):
            GlassButton(
                parent=cnt, position=(12 + idx * (bw1 + 6), c_height - 140), size=(bw1, 32),
                label=lbl, text_scale=0.55,
                bg_color=(0.18, 0.20, 0.32), opacity=0.50,
                border=True, border_color=(0.45, 0.80, 1.0), border_opacity=0.65, border_thickness=1.1,
                on_activate_call=babase.CallPartial(_pick, sec))

        bui.textwidget(
            parent=cnt, position=(14, 72), size=(0, 0),
            h_align='left', v_align='center',
            text='Custom (days):', scale=0.52, color=(0.75, 0.85, 0.96))
        custom_dur_f = _draw_glass_textbox(
            cnt, 126, 56, 162, 32, ol=ol,
            text='1', max_chars=12, opacity=0.78, border_opacity=0.55, border_thickness=1.1,
            description='Duration in days')
        GlassButton(
            parent=cnt, position=(296, 56), size=(102, 32),
            label='Apply', text_scale=0.58,
            bg_color=(0.14, 0.42, 0.24), opacity=0.55,
            border=True, border_color=ol, border_opacity=0.85, border_thickness=1.2,
            on_activate_call=lambda: _pick(bui.textwidget(query=custom_dur_f)))

        ghost_cancel = bui.buttonwidget(parent=cnt, position=(-9000, -9000), size=(1, 1), label='', on_activate_call=_close)
        bui.containerwidget(edit=cnt, cancel_button=ghost_cancel)

        GlassButton(
            parent=cnt, size=(120, 32), position=(c_width * 0.5 - 60, 12), label='Cancel',
            bg_color=(0.35, 0.16, 0.18), opacity=0.45,
            border=True, border_color=(1.0, 0.45, 0.48), border_opacity=0.75, border_thickness=1.2,
            on_activate_call=_close)

    def _open_confirm_command_modal(self, title_lbl: str, resolved_cmd: str, target_label: str) -> None:
        ol = getattr(self, '_outline_color', (0.4, 1.0, 0.5))
        c_width, c_height = 420, 185
        uiscale = bui.app.ui_v1.uiscale
        cnt = bui.containerwidget(
            size=(c_width, c_height),
            scale=(1.50 if uiscale is babase.UIScale.SMALL else
                   1.20 if uiscale is babase.UIScale.MEDIUM else 1.0),
            transition='in_scale',
            background=False,
            parent=bui.get_special_widget('overlay_stack'))
        _draw_panel_bg(cnt, 0, 0, c_width, c_height, color=(0.05, 0.07, 0.11), opacity=0.96)
        _draw_border(cnt, 0, 0, c_width, c_height, color=(1.0, 0.65, 0.25), opacity=0.85, thickness=1.5)

        bui.textwidget(
            parent=cnt, position=(c_width * 0.5, c_height - 24), size=(0, 0),
            h_align='center', v_align='center',
            text=f"Confirm: {title_lbl}", scale=0.78, color=(1.0, 0.85, 0.35), maxwidth=c_width - 28)
        bui.textwidget(
            parent=cnt, position=(c_width * 0.5, c_height - 52), size=(0, 0),
            h_align='center', v_align='center',
            text=f"Target: {target_label}", scale=0.58, color=(0.75, 0.85, 0.96), maxwidth=c_width - 28)

        _draw_panel_bg(cnt, 16, c_height - 122, c_width - 32, 46, color=(0.02, 0.04, 0.07), opacity=0.80)
        _draw_border(cnt, 16, c_height - 122, c_width - 32, 46, color=ol, opacity=0.50, thickness=1.0)
        bui.textwidget(
            parent=cnt, position=(c_width * 0.5, c_height - 99), size=(0, 0),
            h_align='center', v_align='center',
            text=babase.Lstr(value=resolved_cmd), scale=0.68, color=(0.55, 1.0, 0.72), maxwidth=c_width - 48)

        def _close():
            bui.containerwidget(edit=cnt, transition='out_scale')

        def _send_now():
            bs.chatmessage(resolved_cmd)
            bui.screenmessage(f"Sent: {resolved_cmd}", color=(0.4, 1.0, 0.5))
            _close()

        ghost_cancel = bui.buttonwidget(parent=cnt, position=(-9000, -9000), size=(1, 1), label='', on_activate_call=_close)
        bui.containerwidget(edit=cnt, cancel_button=ghost_cancel)

        GlassButton(
            parent=cnt, size=(120, 34), position=(16, 12), label='Cancel',
            bg_color=(0.35, 0.16, 0.18), opacity=0.45,
            border=True, border_color=(1.0, 0.45, 0.48), border_opacity=0.75, border_thickness=1.2,
            on_activate_call=_close)
        GlassButton(
            parent=cnt, size=(145, 34), position=(c_width - 161, 12), label='Send Now',
            bg_color=(0.14, 0.42, 0.24), opacity=0.55,
            border=True, border_color=ol, border_opacity=0.90, border_thickness=1.3,
            on_activate_call=_send_now)

    def _open_cmd_vars_help_modal(self, ol=(0.4, 1.0, 0.5)) -> None:
        """Shows what every Command Maker placeholder variable does with examples."""
        c_width, c_height = 520, 392
        uiscale = bui.app.ui_v1.uiscale
        cnt = bui.containerwidget(
            size=(c_width, c_height),
            scale=(1.35 if uiscale is babase.UIScale.SMALL else
                   1.12 if uiscale is babase.UIScale.MEDIUM else 1.0),
            transition='in_scale',
            background=False,
            parent=bui.get_special_widget('overlay_stack'))

        _draw_panel_bg(cnt, 0, 0, c_width, c_height, color=(0.05, 0.07, 0.11), opacity=0.97)
        _draw_border(cnt, 0, 0, c_width, c_height, color=ol, opacity=0.88, thickness=1.5)

        bui.textwidget(
            parent=cnt, position=(c_width * 0.5, c_height - 22), size=(0, 0),
            h_align='center', v_align='center',
            text='Command Variables & Examples', scale=0.78, color=(1.0, 0.88, 0.35))
        bui.textwidget(
            parent=cnt, position=(c_width * 0.5, c_height - 42), size=(0, 0),
            h_align='center', v_align='center',
            text='Tap any {var} chip in Command Maker to insert it automatically',
            scale=0.47, color=(0.68, 0.78, 0.90))

        entries = [
            ("{cid}  / $cid", "Target player's Client ID number", "/kick {cid}  ->  /kick 4"),
            ("{acc}  / $acc", "Target account display string", "/give {acc} 100  ->  /give Normiii 100"),
            ("{name} / $name", "Current in-game character profile name", "Hi {name}!  ->  Hi Spaz!"),
            ("{nick} / $nick", "Saved local nickname (or falls back to name)", "/pm {nick} gg  ->  /pm Bro gg"),
            ("{aid}  / $aid", "Resolved Ballistica V2 Account ID", "/info {aid}  ->  /info a-1A2B3C..."),
            ("{me}   / $me", "Your own BombSquad account name", "/msg {cid} from {me}"),
            ("{dur}  / $dur", "Prompts duration picker in days", "/ban {cid} {dur}  ->  /ban 4 7"),
        ]

        y = c_height - 62
        row_h = 37
        for var_lbl, desc, ex in entries:
            _draw_panel_bg(cnt, 12, y - row_h, c_width - 24, row_h, color=(0.07, 0.10, 0.16), opacity=0.72)
            _draw_border(cnt, 12, y - row_h, c_width - 24, row_h, color=ol, opacity=0.35, thickness=1.0)
            bui.textwidget(
                parent=cnt, position=(20, y - 12), size=(0, 0),
                h_align='left', v_align='center',
                text=babase.Lstr(value=var_lbl), scale=0.52, color=(0.50, 0.95, 1.0), maxwidth=125)
            bui.textwidget(
                parent=cnt, position=(145, y - 12), size=(0, 0),
                h_align='left', v_align='center',
                text=desc, scale=0.48, color=(0.92, 0.96, 1.0), maxwidth=c_width - 165)
            bui.textwidget(
                parent=cnt, position=(145, y - 27), size=(0, 0),
                h_align='left', v_align='center',
                text=babase.Lstr(value=f"Ex: {ex}"), scale=0.44, color=(0.55, 0.90, 0.70), maxwidth=c_width - 165)
            y -= (row_h + 4)

        def _close():
            bui.containerwidget(edit=cnt, transition='out_scale')

        ghost_cancel = bui.buttonwidget(parent=cnt, position=(-9000, -9000), size=(1, 1), label='', on_activate_call=_close)
        bui.containerwidget(edit=cnt, cancel_button=ghost_cancel)

        GlassButton(
            parent=cnt, position=(c_width - 132, 10), size=(120, 34),
            label='Got It', text_scale=0.66,
            bg_color=(0.14, 0.36, 0.28), opacity=0.55,
            border=True, border_color=ol, border_opacity=0.85, border_thickness=1.2,
            on_activate_call=_close)

    def _open_command_maker_window(self) -> None:
        """Cyber-Glass Custom Command Maker: build, edit, reorder & configure commands."""
        c_width, c_height = 540, 460
        ol = getattr(self, '_outline_color', (0.4, 1.0, 0.5))
        uiscale = bui.app.ui_v1.uiscale

        cnt = bui.containerwidget(
            size=(c_width, c_height),
            scale=(1.42 if uiscale is babase.UIScale.SMALL else
                   1.15 if uiscale is babase.UIScale.MEDIUM else 1.0),
            transition='in_scale',
            background=False,
            parent=bui.get_special_widget('overlay_stack'))

        _draw_panel_bg(cnt, 0, 0, c_width, c_height, color=(0.05, 0.07, 0.11), opacity=0.96)
        _draw_border(cnt, 0, 0, c_width, c_height, color=ol, opacity=0.82, thickness=1.5)

        bui.textwidget(
            parent=cnt, position=(c_width * 0.5, c_height - 20), size=(0, 0),
            h_align='center', v_align='center',
            text='Custom Command Maker', scale=0.82, color=(1.0, 0.88, 0.35), maxwidth=c_width - 96)
        bui.textwidget(
            parent=cnt, position=(c_width * 0.5, c_height - 38), size=(0, 0),
            h_align='center', v_align='center',
            text='Commands appear in Roster -> Commands button (tools icon)',
            scale=0.49, color=(0.68, 0.78, 0.90), maxwidth=c_width - 96)

        GlassButton(
            parent=cnt, position=(c_width - 42, c_height - 38), size=(28, 28),
            label='ⓘ', text_scale=0.68,
            bg_color=(0.12, 0.24, 0.38), opacity=0.55,
            text_color=(0.60, 0.92, 1.0),
            border=True, border_color=(0.40, 0.82, 1.0), border_opacity=0.80, border_thickness=1.2,
            on_activate_call=babase.CallPartial(self._open_cmd_vars_help_modal, ol))

        cmds = self._get_custom_commands()
        state = {"edit_idx": None, "direct": True, "confirm": True}

        list_x, list_y, list_w, list_h = 12, 228, c_width - 24, 180
        _draw_panel_bg(cnt, list_x, list_y, list_w, list_h, color=(0.03, 0.05, 0.08), opacity=0.78)
        _draw_border(cnt, list_x, list_y, list_w, list_h, color=ol, opacity=0.45, thickness=1.0)
        scroll = bui.scrollwidget(
            parent=cnt, position=(list_x + 4, list_y + 4), size=(list_w - 8, list_h - 8),
            highlight=False, border_opacity=0.0)
        list_col = bui.columnwidget(parent=scroll, border=0, margin=3)

        ed_x, ed_y, ed_w, ed_h = 12, 52, c_width - 24, 166
        _draw_panel_bg(cnt, ed_x, ed_y, ed_w, ed_h, color=(0.06, 0.09, 0.14), opacity=0.88)
        _draw_border(cnt, ed_x, ed_y, ed_w, ed_h, color=ol, opacity=0.58, thickness=1.2)

        mode_hdr = bui.textwidget(
            parent=cnt, position=(22, 203), size=(0, 0),
            h_align='left', v_align='center',
            text='Create New Command', scale=0.56, color=(0.55, 0.92, 1.0))

        bui.textwidget(
            parent=cnt, position=(22, 178), size=(0, 0),
            h_align='left', v_align='center',
            text='Label:', scale=0.54, color=(0.78, 0.85, 0.95))
        label_field = _draw_glass_textbox(
            cnt, 66, 162, 130, 32, ol=ol,
            max_chars=28, opacity=0.78, border_opacity=0.55, border_thickness=1.1,
            description='Command label')

        bui.textwidget(
            parent=cnt, position=(204, 178), size=(0, 0),
            h_align='left', v_align='center',
            text='Cmd:', scale=0.54, color=(0.78, 0.85, 0.95))
        cmd_field = _draw_glass_textbox(
            cnt, 242, 162, 276, 32, ol=ol,
            max_chars=140, opacity=0.78, border_opacity=0.55, border_thickness=1.1,
            description='Command template, e.g. /ban {cid} {dur}')

        bui.textwidget(
            parent=cnt, position=(22, 139), size=(0, 0),
            h_align='left', v_align='center',
            text='Vars:', scale=0.50, color=(0.68, 0.78, 0.90))

        def _insert_var(tok: str) -> None:
            cur = bui.textwidget(query=cmd_field) or ""
            sep = "" if (not cur or cur.endswith((" ", "/", ":"))) else " "
            bui.textwidget(edit=cmd_field, text=cur + sep + tok)

        var_tokens = ["{cid}", "{acc}", "{name}", "{nick}", "{aid}", "{me}", "{dur}"]
        for v_i, v_tok in enumerate(var_tokens):
            vx = 66 + v_i * 65
            GlassButton(
                parent=cnt, position=(vx, 126), size=(61, 25),
                label=v_tok, text_scale=0.47,
                bg_color=(0.10, 0.16, 0.26), opacity=0.45,
                text_color=(0.55, 0.92, 1.0),
                border=True, border_color=(0.35, 0.78, 1.0), border_opacity=0.55, border_thickness=1.0,
                on_activate_call=babase.CallPartial(_insert_var, v_tok))

        mode_btn = GlassButton(
            parent=cnt, position=(22, 92), size=(242, 26),
            label='Mode: Instant Send', text_scale=0.52,
            bg_color=(0.12, 0.30, 0.20), opacity=0.50,
            border=True, border_color=ol, border_opacity=0.70, border_thickness=1.1)

        confirm_btn = GlassButton(
            parent=cnt, position=(272, 92), size=(246, 26),
            label='Guard: Ask Confirm', text_scale=0.52,
            bg_color=(0.28, 0.22, 0.10), opacity=0.50,
            border=True, border_color=(1.0, 0.75, 0.30), border_opacity=0.70, border_thickness=1.1)

        save_btn = GlassButton(
            parent=cnt, position=(22, 58), size=(220, 28),
            label='Add Command', text_scale=0.58,
            bg_color=(0.14, 0.42, 0.24), opacity=0.55,
            border=True, border_color=ol, border_opacity=0.85, border_thickness=1.2)

        def _sync_editor_controls():
            is_ed = (state["edit_idx"] is not None)
            if is_ed:
                bui.textwidget(edit=mode_hdr, text=f"Editing Command #{state['edit_idx'] + 1}", color=(1.0, 0.85, 0.35))
                save_btn.set_text('Update Command')
            else:
                bui.textwidget(edit=mode_hdr, text='Create New Command', color=(0.55, 0.92, 1.0))
                save_btn.set_text('Add Command')

            if state["direct"]:
                mode_btn.set_text('Mode: Instant Send')
                mode_btn.set_color(bg_color=(0.12, 0.30, 0.20), opacity=0.50, text_color=(0.85, 1.0, 0.88))
                mode_btn.set_border_color(color=ol, opacity=0.75)
                if state["confirm"]:
                    confirm_btn.set_text('Guard: Ask Confirm')
                    confirm_btn.set_color(bg_color=(0.28, 0.22, 0.10), opacity=0.52, text_color=(1.0, 0.90, 0.65))
                    confirm_btn.set_border_color(color=(1.0, 0.75, 0.30), opacity=0.75)
                else:
                    confirm_btn.set_text('Guard: Direct Send')
                    confirm_btn.set_color(bg_color=(0.30, 0.12, 0.14), opacity=0.52, text_color=(1.0, 0.72, 0.72))
                    confirm_btn.set_border_color(color=(1.0, 0.42, 0.45), opacity=0.75)
            else:
                mode_btn.set_text('Mode: Fill Chat Draft')
                mode_btn.set_color(bg_color=(0.12, 0.22, 0.36), opacity=0.52, text_color=(0.70, 0.90, 1.0))
                mode_btn.set_border_color(color=(0.40, 0.78, 1.0), opacity=0.75)
                confirm_btn.set_text('Draft (Edit Before Send)')
                confirm_btn.set_color(bg_color=(0.10, 0.13, 0.18), opacity=0.35, text_color=(0.65, 0.72, 0.82))
                confirm_btn.set_border_color(color=(0.45, 0.55, 0.68), opacity=0.40)

        def _toggle_mode():
            state["direct"] = not state["direct"]
            _sync_editor_controls()

        def _toggle_confirm():
            if not state["direct"]:
                bui.screenmessage("Draft mode always opens in chat box first!", color=(0.55, 0.85, 1.0))
                return
            state["confirm"] = not state["confirm"]
            _sync_editor_controls()

        mode_btn.set_on_activate(_toggle_mode)
        confirm_btn.set_on_activate(_toggle_confirm)

        def _clear_editor():
            state["edit_idx"] = None
            state["direct"] = True
            state["confirm"] = True
            bui.textwidget(edit=label_field, text='')
            bui.textwidget(edit=cmd_field, text='')
            _sync_editor_controls()
            _rebuild_list()

        def _load_for_edit(idx: int):
            if 0 <= idx < len(cmds):
                item = cmds[idx]
                state["edit_idx"] = idx
                state["direct"] = bool(item.get("direct", True))
                state["confirm"] = bool(item.get("confirm", False))
                bui.textwidget(edit=label_field, text=item.get("label", ""))
                bui.textwidget(edit=cmd_field, text=item.get("cmd", ""))
                _sync_editor_controls()
                _rebuild_list()

        def _move_cmd(idx: int, delta: int):
            ni = idx + delta
            if 0 <= idx < len(cmds) and 0 <= ni < len(cmds):
                cmds[idx], cmds[ni] = cmds[ni], cmds[idx]
                if state["edit_idx"] == idx:
                    state["edit_idx"] = ni
                elif state["edit_idx"] == ni:
                    state["edit_idx"] = idx
                AlphaPartyWindow._save_custom_commands(cmds)
                _sync_editor_controls()
                _rebuild_list()

        def _delete_cmd(idx: int):
            if 0 <= idx < len(cmds):
                cmds.pop(idx)
                if state["edit_idx"] == idx:
                    state["edit_idx"] = None
                    bui.textwidget(edit=label_field, text='')
                    bui.textwidget(edit=cmd_field, text='')
                elif state["edit_idx"] is not None and state["edit_idx"] > idx:
                    state["edit_idx"] -= 1
                AlphaPartyWindow._save_custom_commands(cmds)
                _sync_editor_controls()
                _rebuild_list()

        def _save_or_add():
            new_cmd = (bui.textwidget(query=cmd_field) or "").strip()
            new_lbl = (bui.textwidget(query=label_field) or "").strip() or new_cmd[:24]
            if not new_cmd:
                bui.screenmessage("Command template cannot be empty!", color=(1.0, 0.35, 0.35))
                return
            entry = {
                "label": new_lbl[:28],
                "cmd": new_cmd,
                "direct": bool(state["direct"]),
                "confirm": bool(state["confirm"]) if state["direct"] else False,
            }
            if state["edit_idx"] is not None and 0 <= state["edit_idx"] < len(cmds):
                cmds[state["edit_idx"]] = entry
                bui.screenmessage(f"Updated '{entry['label']}'", color=(0.4, 1.0, 0.5))
            else:
                cmds.append(entry)
                bui.screenmessage(f"Added '{entry['label']}'", color=(0.4, 1.0, 0.5))
            AlphaPartyWindow._save_custom_commands(cmds)
            _clear_editor()

        def _reset_defaults():
            cmds[:] = [dict(x) for x in AlphaPartyWindow._DEFAULT_CUSTOM_COMMANDS]
            AlphaPartyWindow._save_custom_commands(cmds)
            bui.screenmessage("Restored default commands", color=(1.0, 0.85, 0.35))
            _clear_editor()

        save_btn.set_on_activate(_save_or_add)

        GlassButton(
            parent=cnt, position=(250, 58), size=(125, 28),
            label='New / Clear', text_scale=0.54,
            bg_color=(0.14, 0.18, 0.26), opacity=0.45,
            border=True, border_color=(0.55, 0.72, 0.90), border_opacity=0.60, border_thickness=1.1,
            on_activate_call=_clear_editor)
        GlassButton(
            parent=cnt, position=(383, 58), size=(135, 28),
            label='Reset Defaults', text_scale=0.52,
            bg_color=(0.30, 0.22, 0.12), opacity=0.45,
            border=True, border_color=(1.0, 0.75, 0.30), border_opacity=0.65, border_thickness=1.1,
            on_activate_call=_reset_defaults)

        def _rebuild_list():
            for child in list_col.get_children():
                child.delete()
            row_w = list_w - 28
            row_h = 44
            if not cmds:
                bui.textwidget(
                    parent=list_col, size=(row_w, 90),
                    h_align='center', v_align='center',
                    text='No custom commands yet — build one below!',
                    scale=0.62, color=(0.65, 0.72, 0.82))
                return

            for idx, entry in enumerate(cmds):
                is_sel = (state["edit_idx"] == idx)
                rc = bui.containerwidget(parent=list_col, size=(row_w, row_h), background=False)
                _draw_panel_bg(
                    rc, 0, 0, row_w, row_h,
                    color=(0.14, 0.26, 0.36) if is_sel else (0.09, 0.12, 0.18),
                    opacity=0.65 if is_sel else 0.48)
                _draw_border(
                    rc, 0, 0, row_w, row_h,
                    color=(0.45, 0.92, 1.0) if is_sel else ol,
                    opacity=0.88 if is_sel else 0.32, thickness=1.1)

                badge = "[Draft]" if not entry.get("direct", True) else ("[Confirm]" if entry.get("confirm", False) else "[Direct]")
                bui.textwidget(
                    parent=rc, position=(10, 30), size=(0, 0),
                    h_align='left', v_align='center',
                    text=f"{entry.get('label', '')}  {badge}",
                    scale=0.56, color=(1.0, 0.92, 0.55) if is_sel else (0.94, 0.96, 1.0),
                    maxwidth=row_w - 170)
                bui.textwidget(
                    parent=rc, position=(10, 12), size=(0, 0),
                    h_align='left', v_align='center',
                    text=babase.Lstr(value=entry.get('cmd', '')),
                    scale=0.49, color=(0.55, 0.90, 0.78),
                    maxwidth=row_w - 170)

                bx = row_w - 154
                GlassButton(
                    parent=rc, position=(bx, 8), size=(42, 28),
                    label='Edit', text_scale=0.50,
                    bg_color=(0.12, 0.24, 0.38), opacity=0.50,
                    border=True, border_color=(0.45, 0.80, 1.0), border_opacity=0.65, border_thickness=1.0,
                    on_activate_call=babase.CallPartial(_load_for_edit, idx))
                GlassButton(
                    parent=rc, position=(bx + 46, 8), size=(28, 28),
                    label='Up', text_scale=0.44,
                    bg_color=(0.12, 0.16, 0.22), opacity=0.45,
                    border=True, border_color=ol, border_opacity=0.45, border_thickness=1.0,
                    on_activate_call=babase.CallPartial(_move_cmd, idx, -1))
                GlassButton(
                    parent=rc, position=(bx + 78, 8), size=(28, 28),
                    label='Dn', text_scale=0.44,
                    bg_color=(0.12, 0.16, 0.22), opacity=0.45,
                    border=True, border_color=ol, border_opacity=0.45, border_thickness=1.0,
                    on_activate_call=babase.CallPartial(_move_cmd, idx, 1))
                GlassButton(
                    parent=rc, position=(bx + 110, 8), size=(36, 28),
                    label='Del', text_scale=0.48,
                    bg_color=(0.38, 0.14, 0.16), opacity=0.55,
                    border=True, border_color=(1.0, 0.42, 0.45), border_opacity=0.70, border_thickness=1.0,
                    on_activate_call=babase.CallPartial(_delete_cmd, idx))

        _sync_editor_controls()
        _rebuild_list()

        def _close():
            bui.containerwidget(edit=cnt, transition='out_scale')

        ghost_cancel = bui.buttonwidget(parent=cnt, position=(-9000, -9000), size=(1, 1), label='', on_activate_call=_close)
        bui.containerwidget(edit=cnt, cancel_button=ghost_cancel)

        bui.textwidget(
            parent=cnt, position=(16, 26), size=(0, 0),
            h_align='left', v_align='center',
            text='Placeholders also accept $cid / $acc / $name / $nick / $aid / $dur',
            scale=0.44, color=(0.55, 0.65, 0.78), maxwidth=c_width - 165)

        GlassButton(
            parent=cnt, position=(c_width - 134, 10), size=(122, 34),
            label='Done', text_scale=0.68,
            bg_color=(0.16, 0.24, 0.34), opacity=0.55,
            border=True, border_color=ol, border_opacity=0.85, border_thickness=1.2,
            on_activate_call=_close)

    def popup_menu_selected_choice(self, popup_window, choice: str) -> None:
        if self._popup_type == "QuickMessageSelect":
            if choice == "__manage_quick__":
                try:
                    cur_txt = (bui.textwidget(query=self._text_field) or "").strip()
                except Exception:
                    cur_txt = ""
                self._open_quick_replies_window(prefill=cur_txt)
            else:
                bui.textwidget(edit=self._text_field, text=choice)
                self._refresh_input_ping_hint()
        elif self._popup_type == "chatmessagepress":
            if choice == "translate":
                self._translate_selected_chat_msg()
            elif choice == "copy":
                if bui.clipboard_is_supported():
                    bui.clipboard_set_text(self.msg_user_selected)
                    bui.screenmessage("Copied message!", color=(0, 1, 0))
            elif choice == "reply":
                rep_txt = _apw_format_reply_prefix(self.msg_user_selected)
                if rep_txt:
                    bui.textwidget(edit=self._text_field, text=rep_txt)
                    self._refresh_input_ping_hint()
        elif self._popup_type == "partyMemberCommands":
            cid = self._popup_party_member_client_id
            if choice.startswith("cmd:"):
                try:
                    c_idx = int(choice.split(":", 1)[1])
                    cmds = self._get_custom_commands()
                    if 0 <= c_idx < len(cmds):
                        self._execute_custom_command(cmds[c_idx], cid)
                except Exception:
                    pass
            elif choice == "open_cmd_maker":
                self._open_command_maker_window()
        elif self._popup_type == "partyMemberPress":
            cid = self._popup_party_member_client_id
            if choice == "info":
                self._on_player_info_press(cid, widget=popup_window.root_widget)
            elif choice == "@ this guy":
                acc = self._getObjectByID("account", cid)
                if acc:
                    bui.textwidget(edit=self._text_field, text=f"@{acc} ")
                    self._refresh_input_ping_hint()
            elif choice == "set_nick":
                acc = self._getObjectByID("account", cid)
                if acc:
                    self._open_set_nick_window(acc)
            elif choice == "mute_chat":
                acc = self._getObjectByID("account", cid)
                if acc:
                    is_m = any(m == acc or _apw_clean_name(m) == _apw_clean_name(acc) for m in muted_chat_names)
                    if is_m:
                        _apw_set_chat_muted(acc, False, client_id=cid)
                        bs.broadcastmessage(f"Unmuted {acc}", color=(0.4, 1, 0.4))
                        self._rebuild_chat_after_unmute()
                    else:
                        _apw_set_chat_muted(acc, True, client_id=cid)
                        bs.broadcastmessage(f"Muted {acc}", color=(1, 0.7, 0.3))
            elif choice == "toggle_autogreet":
                acc = self._getObjectByID("account", cid) or ""
                if acc:
                    aid = ""
                    try:
                        aid = str(_apw_resolve_aid(client_id=cid, v2_id=acc, is_self=(cid == -1)) or "").strip()
                    except Exception:
                        aid = ""
                    ag_map = _apw_get_autogreet_players()
                    existing_key = _apw_find_autogreet_key(aid, acc, ag_map)
                    if existing_key is not None:
                        ag_map.pop(existing_key, None)
                        _apw_save_autogreet_players(ag_map)
                        bui.screenmessage(f"Removed {acc} from Auto Greet", color=(1.0, 0.75, 0.35))
                    else:
                        store_key = aid or acc
                        ag_map[store_key] = {"v2": acc, "aid": aid or acc}
                        _apw_save_autogreet_players(ag_map)
                        bui.screenmessage(f"Added {acc} to Auto Greet", color=(0.4, 1.0, 0.5))
            elif choice == "complaint":
                self._open_complaint_window(cid)
        elif self._popup_type == "menu":
            is_muted = babase.app.config.resolve('Chat Muted')
            global screenmsg
            if choice == "mute":
                cfg = babase.app.config
                cfg['Chat Muted'] = not is_muted
                cfg.apply_and_commit()
            elif choice == "color":
                self._open_colors_window()
            elif choice == "chat_logs":
                self._open_chat_logs_window()
            elif choice == "translate":
                self._open_translate_settings_window()
            elif choice == "screenmsg":
                screenmsg = not screenmsg
                if screenmsg:
                    self.restore_screen_msg()
                else:
                    self.hide_screen_msg()
            elif choice == "cmd_maker":
                self._open_command_maker_window()
            elif choice == "autogreet":
                self._open_autogreet_window()
            elif choice == "player_lists":
                self._open_player_lists_window("muted")
            elif choice == "header_players":
                cur = _apw_show_header_players()
                babase.app.config['APW_Show_Header_Players'] = not cur
                babase.app.config.commit()
                self._refresh_header_players(force=True)
                if self.active_tab == "players":
                    self._render_players_tab()
                bui.screenmessage(
                    f"Players Under Party Name: {'ON' if not cur else 'OFF'}",
                    color=(0.4, 1.0, 0.5))
            elif choice == "chat_anim":
                cur_anim = _apw_get_chat_anim_style()
                self._popup_type = "chatAnimSelect"
                AlphaPopupMenu(
                    position=popup_window.root_widget.get_screen_space_center() if popup_window else self._menu_button.get_screen_space_center(),
                    choices=[k for k, _ in _APW_CHAT_ANIM_MODES],
                    choices_display=[lbl for _, lbl in _APW_CHAT_ANIM_MODES],
                    current_choice=cur_anim,
                    delegate=self)
            elif choice == "updates":
                self._open_updates_window()
            elif choice == "help":
                self._open_help_window()
            elif choice == "credits":
                self._open_credits_window()
        elif self._popup_type == "chatAnimSelect":
            babase.app.config['APW_Chat_Anim_Style'] = choice
            babase.app.config.commit()
            if self.active_tab == "chat":
                self._build_chat_nav_bar()
            lbl = dict(_APW_CHAT_ANIM_MODES).get(choice, choice)
            bui.screenmessage(f"Chat Bar Animation: {lbl}", color=(0.55, 0.95, 1.0))

    def _on_sorry_press(self) -> None:
        global _apw_sorry_ready_at
        now = time.monotonic()
        rem = _apw_sorry_ready_at - now
        if rem > 0.05:
            bui.screenmessage(f"Too fast! Wait {rem:.1f}s", color=(1.0, 0.78, 0.35))
            return
        _apw_sorry_ready_at = now + _APW_SORRY_DELAY
        bs.chatmessage(_apw_random_sorry())
        self._refresh_sorry_btn()

    def _refresh_sorry_btn(self) -> None:
        gb = getattr(self, '_sorry_button_gb', None)
        if gb is None or not getattr(self, '_root_widget', None):
            return
        try:
            rem = _apw_sorry_ready_at - time.monotonic()
            if rem > 0.05:
                gb.set_text(f"{rem:.1f}s")
                gb.set_color(bg_color=(0.14, 0.12, 0.10), opacity=0.35, text_color=(0.75, 0.75, 0.78))
                babase.apptimer(0.2, babase.WeakCallStrict(self._refresh_sorry_btn))
            else:
                gb.set_text('Sorry!')
                gb.set_color(bg_color=(0.24, 0.16, 0.10), opacity=0.38, text_color=(1.0, 0.88, 0.60))
        except Exception:
            pass

    def _open_autogreet_window(self) -> None:
        """Simple, clear Cyber-Glass Auto Greet Setup modal."""
        c_width, c_height = 430, 290
        ol = getattr(self, '_outline_color', (0.4, 1.0, 0.5))
        uiscale = bui.app.ui_v1.uiscale
        weak_self = weakref.ref(self)

        cnt = bui.containerwidget(
            size=(c_width, c_height),
            scale=(1.48 if uiscale is babase.UIScale.SMALL else
                   1.18 if uiscale is babase.UIScale.MEDIUM else 1.0),
            transition='in_scale',
            background=False,
            parent=bui.get_special_widget('overlay_stack'))

        _draw_panel_bg(cnt, 0, 0, c_width, c_height, color=(0.05, 0.07, 0.11), opacity=0.96)
        _draw_border(cnt, 0, 0, c_width, c_height, color=ol, opacity=0.84, thickness=1.5)

        bui.textwidget(
            parent=cnt, position=(c_width * 0.5, c_height - 20), size=(0, 0),
            h_align='center', v_align='center',
            text='👋 Auto Greet Setup', scale=0.82, color=(1.0, 0.88, 0.35))
        bui.textwidget(
            parent=cnt, position=(c_width * 0.5, c_height - 39), size=(0, 0),
            h_align='center', v_align='center',
            text='Automatically greet friends on join or reply when greeted',
            scale=0.47, color=(0.68, 0.78, 0.90), maxwidth=c_width - 28)

        st = _apw_get_autogreet_cfg()

        en_btn = GlassButton(
            parent=cnt, position=(14, c_height - 88), size=(c_width - 28, 30),
            label='', text_scale=0.58,
            border=True, border_color=ol, border_opacity=0.75, border_thickness=1.2)
        jm_btn = GlassButton(
            parent=cnt, position=(14, c_height - 124), size=(c_width - 28, 30),
            label='', text_scale=0.55,
            border=True, border_color=ol, border_opacity=0.75, border_thickness=1.2)
        cr_btn = GlassButton(
            parent=cnt, position=(14, c_height - 160), size=(c_width - 28, 30),
            label='', text_scale=0.55,
            border=True, border_color=ol, border_opacity=0.75, border_thickness=1.2)

        bui.textwidget(
            parent=cnt, position=(16, c_height - 180), size=(0, 0),
            h_align='left', v_align='center',
            text='Greet Message ({name} = player, {acc} = V2 tag):',
            scale=0.47, color=(0.72, 0.84, 0.96), maxwidth=c_width - 32)
        join_msg_field = _draw_glass_textbox(
            cnt, 14, c_height - 222, c_width - 28, 32, ol=ol,
            text=st["join_msg"], max_chars=120,
            opacity=0.78, border_opacity=0.60, border_thickness=1.1,
            description='Custom greeting message')

        def _sync():
            if st["enabled"]:
                en_btn.set_text('Auto Greet: ON')
                en_btn.set_color(bg_color=(0.12, 0.34, 0.22), opacity=0.55, text_color=(0.85, 1.0, 0.88))
                en_btn.set_border_color(color=ol, opacity=0.85)
            else:
                en_btn.set_text('Auto Greet: OFF')
                en_btn.set_color(bg_color=(0.24, 0.14, 0.16), opacity=0.45, text_color=(1.0, 0.78, 0.78))
                en_btn.set_border_color(color=(1.0, 0.45, 0.48), opacity=0.75)

            jm_labels = {
                'list': f"On Join: Saved List ({len(_apw_get_autogreet_players())})",
                'all': 'On Join: Everyone',
                'off': 'On Join: Off',
            }
            jm_btn.set_text(jm_labels.get(st["join_mode"], jm_labels['list']))
            jm_active = st["join_mode"] != 'off'
            jm_btn.set_color(
                bg_color=(0.12, 0.24, 0.36) if jm_active else (0.12, 0.14, 0.18),
                opacity=0.50 if jm_active else 0.35,
                text_color=(0.85, 0.95, 1.0) if jm_active else (0.68, 0.74, 0.82))

            if st["chat_reply"]:
                cr_btn.set_text('Reply When Greeted ("Hi"): ON')
                cr_btn.set_color(bg_color=(0.12, 0.28, 0.30), opacity=0.50, text_color=(0.85, 0.98, 0.95))
            else:
                cr_btn.set_text('Reply When Greeted ("Hi"): OFF')
                cr_btn.set_color(bg_color=(0.12, 0.14, 0.18), opacity=0.35, text_color=(0.68, 0.74, 0.82))

        def _toggle_en():
            st["enabled"] = not st["enabled"]
            _sync()

        def _cycle_jm():
            order = ['list', 'all', 'off']
            cur = st["join_mode"] if st["join_mode"] in order else 'list'
            st["join_mode"] = order[(order.index(cur) + 1) % len(order)]
            _sync()

        def _toggle_cr():
            st["chat_reply"] = not st["chat_reply"]
            _sync()

        en_btn.set_on_activate(_toggle_en)
        jm_btn.set_on_activate(_cycle_jm)
        cr_btn.set_on_activate(_toggle_cr)
        _sync()

        def _close():
            bui.containerwidget(edit=cnt, transition='out_scale')

        def _open_list():
            _close()
            inst = weak_self()
            if inst is not None:
                inst._open_player_lists_window("autogreet")

        def _save():
            msg_val = (bui.textwidget(query=join_msg_field) or '').strip() or 'Hey {name}, welcome!'
            cfg = babase.app.config
            cfg['APW_AutoGreet_Enabled'] = bool(st["enabled"])
            cfg['APW_AutoGreet_JoinMode'] = st["join_mode"]
            cfg['APW_AutoGreet_Chat'] = bool(st["chat_reply"])
            cfg['APW_AutoGreet_Message'] = msg_val
            cfg['APW_AutoGreet_Reply'] = msg_val
            cfg.commit()
            bui.screenmessage(
                f"Auto Greet {'Enabled' if st['enabled'] else 'Disabled'}",
                color=(0.4, 1.0, 0.5) if st["enabled"] else (1.0, 0.75, 0.35))
            _close()

        ghost_cancel = bui.buttonwidget(parent=cnt, position=(-9000, -9000), size=(1, 1), label='', on_activate_call=_close)
        bui.containerwidget(edit=cnt, cancel_button=ghost_cancel)

        GlassButton(
            parent=cnt, size=(96, 34), position=(14, 12), label='Cancel',
            bg_color=(0.35, 0.16, 0.18), opacity=0.45,
            border=True, border_color=(1.0, 0.45, 0.48), border_opacity=0.75, border_thickness=1.2,
            on_activate_call=_close)
        GlassButton(
            parent=cnt, size=(176, 34), position=(c_width * 0.5 - 88, 12), label='📋 Greet List (V2/AID)', text_scale=0.52,
            bg_color=(0.12, 0.24, 0.38), opacity=0.52,
            border=True, border_color=(0.45, 0.80, 1.0), border_opacity=0.75, border_thickness=1.2,
            on_activate_call=_open_list)
        GlassButton(
            parent=cnt, size=(96, 34), position=(c_width - 110, 12), label='Save',
            bg_color=(0.14, 0.42, 0.24), opacity=0.52,
            border=True, border_color=ol, border_opacity=0.85, border_thickness=1.2,
            on_activate_call=_save)

    def _open_player_lists_window(self, initial_tab: str = "muted") -> None:
        """Unified Cyber-Glass Registry Page: Chat Muted, Settled Nicks & Auto Greet (V2 + AID)."""
        c_width, c_height = 530, 440
        ol = getattr(self, '_outline_color', (0.4, 1.0, 0.5))
        uiscale = bui.app.ui_v1.uiscale
        weak_self = weakref.ref(self)

        cnt = bui.containerwidget(
            size=(c_width, c_height),
            scale=(1.42 if uiscale is babase.UIScale.SMALL else
                   1.14 if uiscale is babase.UIScale.MEDIUM else 1.0),
            transition='in_scale',
            background=False,
            parent=bui.get_special_widget('overlay_stack'))

        _draw_panel_bg(cnt, 0, 0, c_width, c_height, color=(0.05, 0.07, 0.11), opacity=0.96)
        _draw_border(cnt, 0, 0, c_width, c_height, color=ol, opacity=0.84, thickness=1.5)

        bui.textwidget(
            parent=cnt, position=(c_width * 0.5, c_height - 20), size=(0, 0),
            h_align='center', v_align='center',
            text='Player Lists Registry', scale=0.82, color=(1.0, 0.88, 0.35))
        bui.textwidget(
            parent=cnt, position=(c_width * 0.5, c_height - 39), size=(0, 0),
            h_align='center', v_align='center',
            text='Manage Chat Muted, Settled Nicks & Auto Greet AID players',
            scale=0.47, color=(0.68, 0.78, 0.90), maxwidth=c_width - 28)

        active_tab = [initial_tab if initial_tab in ("muted", "nicks", "autogreet") else "muted"]

        tab_y = c_height - 80
        tab_w = (c_width - 36) / 3
        tab_btns: Dict[str, GlassButton] = {}

        list_x, list_y, list_w, list_h = 12, 54, c_width - 24, c_height - 144
        _draw_panel_bg(cnt, list_x, list_y, list_w, list_h, color=(0.03, 0.05, 0.08), opacity=0.78)
        _draw_border(cnt, list_x, list_y, list_w, list_h, color=ol, opacity=0.48, thickness=1.1)
        scroll = bui.scrollwidget(
            parent=cnt, position=(list_x + 4, list_y + 4), size=(list_w - 8, list_h - 8),
            highlight=False, border_opacity=0.0)
        list_col = bui.columnwidget(parent=scroll, border=0, margin=3)

        def _populate():
            cur = active_tab[0]
            for tk, tb in tab_btns.items():
                is_act = (tk == cur)
                tb.set_color(
                    bg_color=(0.14, 0.34, 0.25) if is_act else (0.08, 0.11, 0.16),
                    opacity=0.55 if is_act else 0.32,
                    text_color=(1, 1, 1) if is_act else (0.70, 0.80, 0.90))
                tb.set_border_color(color=ol, opacity=0.90 if is_act else 0.35)

            for ch in list_col.get_children():
                ch.delete()

            row_w = list_w - 28
            row_h = 46

            if cur == "muted":
                reg = _apw_get_muted_registry()
                for m in list(muted_chat_names):
                    mk = _apw_clean_name(m) or m
                    if mk not in reg:
                        reg[mk] = {"v2": m, "aid": ""}
                if not reg:
                    bui.textwidget(
                        parent=list_col, size=(row_w, 120),
                        h_align='center', v_align='center',
                        text='No players muted from Party Window yet.',
                        scale=0.60, color=(0.62, 0.70, 0.80))
                    return
                for mk, info in list(reg.items()):
                    v2_disp = info.get("v2") or mk
                    aid_disp = info.get("aid") or "Unknown AID"
                    rc = bui.containerwidget(parent=list_col, size=(row_w, row_h), background=False)
                    _draw_panel_bg(rc, 0, 0, row_w, row_h, color=(0.10, 0.13, 0.19), opacity=0.55)
                    _draw_border(rc, 0, 0, row_w, row_h, color=ol, opacity=0.30, thickness=1.0)
                    bui.textwidget(
                        parent=rc, position=(10, 31), size=(0, 0),
                        h_align='left', v_align='center',
                        text=f"V2: {v2_disp}", scale=0.58, color=(1.0, 0.92, 0.72), maxwidth=row_w - 110)
                    bui.textwidget(
                        parent=rc, position=(10, 13), size=(0, 0),
                        h_align='left', v_align='center',
                        text=f"AID: {aid_disp}", scale=0.45, color=(0.60, 0.78, 0.95), maxwidth=row_w - 110)

                    def _unmute(target_v2=v2_disp):
                        _apw_set_chat_muted(target_v2, False)
                        bui.screenmessage(f"Unmuted {target_v2}", color=(0.4, 1.0, 0.5))
                        _populate()
                        inst = _apw_active_window_ref() if _apw_active_window_ref is not None else None
                        if inst is not None:
                            inst._rebuild_chat_after_unmute()

                    GlassButton(
                        parent=rc, position=(row_w - 94, 9), size=(86, 28),
                        label='Unmute', text_scale=0.52,
                        bg_color=(0.14, 0.36, 0.24), opacity=0.52,
                        border=True, border_color=ol, border_opacity=0.75, border_thickness=1.0,
                        on_activate_call=_unmute)

            elif cur == "nicks":
                nicks = babase.app.config.get('players nick', {})
                if not isinstance(nicks, dict) or not nicks:
                    bui.textwidget(
                        parent=list_col, size=(row_w, 120),
                        h_align='center', v_align='center',
                        text='No custom nicknames settled yet.\nUse Roster -> Actions -> Set Nick.',
                        scale=0.58, color=(0.62, 0.70, 0.80))
                    return
                for acc_k, nick_val in list(nicks.items()):
                    rc = bui.containerwidget(parent=list_col, size=(row_w, row_h), background=False)
                    _draw_panel_bg(rc, 0, 0, row_w, row_h, color=(0.10, 0.13, 0.19), opacity=0.55)
                    _draw_border(rc, 0, 0, row_w, row_h, color=ol, opacity=0.30, thickness=1.0)
                    bui.textwidget(
                        parent=rc, position=(10, 31), size=(0, 0),
                        h_align='left', v_align='center',
                        text=f"Nick: {nick_val}", scale=0.58, color=(0.55, 1.0, 0.75), maxwidth=row_w - 135)
                    bui.textwidget(
                        parent=rc, position=(10, 13), size=(0, 0),
                        h_align='left', v_align='center',
                        text=f"V2 Tag: {acc_k}", scale=0.45, color=(0.72, 0.84, 0.96), maxwidth=row_w - 135)

                    def _edit_n(ak=acc_k):
                        bui.containerwidget(edit=cnt, transition='out_scale')
                        inst = weak_self()
                        if inst is not None:
                            inst._open_set_nick_window(ak)

                    def _del_n(ak=acc_k):
                        cfg = babase.app.config
                        if isinstance(cfg.get('players nick'), dict):
                            cfg['players nick'].pop(ak, None)
                            cfg.commit()
                        inst = weak_self()
                        if inst is not None and inst.active_tab == "players":
                            inst._render_players_tab()
                        _populate()

                    GlassButton(
                        parent=rc, position=(row_w - 122, 9), size=(54, 28),
                        label='Edit', text_scale=0.50,
                        bg_color=(0.12, 0.24, 0.38), opacity=0.50,
                        border=True, border_color=(0.45, 0.80, 1.0), border_opacity=0.65, border_thickness=1.0,
                        on_activate_call=_edit_n)
                    GlassButton(
                        parent=rc, position=(row_w - 64, 9), size=(56, 28),
                        label='Del', text_scale=0.50,
                        bg_color=(0.38, 0.14, 0.16), opacity=0.55,
                        border=True, border_color=(1.0, 0.42, 0.45), border_opacity=0.70, border_thickness=1.0,
                        on_activate_call=_del_n)

            elif cur == "autogreet":
                ag_map = _apw_get_autogreet_players()
                my_acc = _apw_get_my_account()
                online_candidates = []
                for r in (bs.get_game_roster() or []):
                    r_acc = str(r.get("display_string") or "").strip()
                    r_cid = r.get("client_id", -1)
                    if not r_acc or r_acc == my_acc:
                        continue
                    try:
                        r_aid = str(_apw_resolve_aid(client_id=r_cid, v2_id=r_acc, is_self=(r_cid == -1)) or "").strip()
                    except Exception:
                        r_aid = ""
                    if _apw_find_autogreet_key(r_aid, r_acc, ag_map) is None:
                        online_candidates.append((r_acc, r_aid or r_acc))

                if online_candidates:
                    hdr_c = bui.containerwidget(parent=list_col, size=(row_w, 34), background=False)
                    bui.textwidget(
                        parent=hdr_c, position=(6, 17), size=(0, 0),
                        h_align='left', v_align='center',
                        text='Add from lobby:', scale=0.48, color=(0.65, 0.85, 1.0))
                    px = 110
                    for c_acc, c_aid in online_candidates[:3]:
                        bw = min(122, (row_w - 115) // min(len(online_candidates), 3) - 4)
                        if bw < 60:
                            break
                        def _add_onl(va=c_acc, vd=c_aid):
                            m2 = _apw_get_autogreet_players()
                            m2[vd] = {"v2": va, "aid": vd}
                            _apw_save_autogreet_players(m2)
                            bui.screenmessage(f"Added {va} to Auto Greet", color=(0.4, 1.0, 0.5))
                            _populate()
                        GlassButton(
                            parent=hdr_c, position=(px, 4), size=(bw, 26),
                            label=f"+ {c_acc[:12]}", text_scale=0.45,
                            bg_color=(0.14, 0.34, 0.24), opacity=0.52,
                            border=True, border_color=ol, border_opacity=0.65, border_thickness=1.0,
                            on_activate_call=_add_onl)
                        px += bw + 4

                if not ag_map:
                    bui.textwidget(
                        parent=list_col, size=(row_w, 100),
                        h_align='center', v_align='center',
                        text='No Auto Greet players saved yet.\nUse Roster -> Actions -> Add Auto Greet or click above.',
                        scale=0.56, color=(0.62, 0.70, 0.80))
                    return

                for ag_key, info in list(ag_map.items()):
                    v2_tag = info.get("v2") or ag_key
                    aid_str = info.get("aid") or ag_key
                    rc = bui.containerwidget(parent=list_col, size=(row_w, row_h), background=False)
                    _draw_panel_bg(rc, 0, 0, row_w, row_h, color=(0.10, 0.14, 0.20), opacity=0.55)
                    _draw_border(rc, 0, 0, row_w, row_h, color=ol, opacity=0.35, thickness=1.0)
                    bui.textwidget(
                        parent=rc, position=(10, 31), size=(0, 0),
                        h_align='left', v_align='center',
                        text=f"V2 Tag: {v2_tag}", scale=0.58, color=(0.55, 1.0, 0.78), maxwidth=row_w - 102)
                    bui.textwidget(
                        parent=rc, position=(10, 13), size=(0, 0),
                        h_align='left', v_align='center',
                        text=f"AID: {aid_str}", scale=0.45, color=(0.65, 0.80, 0.96), maxwidth=row_w - 102)

                    def _rem_ag(gk=ag_key):
                        m2 = _apw_get_autogreet_players()
                        m2.pop(gk, None)
                        _apw_save_autogreet_players(m2)
                        _populate()

                    GlassButton(
                        parent=rc, position=(row_w - 86, 9), size=(78, 28),
                        label='Remove', text_scale=0.50,
                        bg_color=(0.38, 0.14, 0.16), opacity=0.55,
                        border=True, border_color=(1.0, 0.42, 0.45), border_opacity=0.70, border_thickness=1.0,
                        on_activate_call=_rem_ag)

        def _switch(tk: str):
            active_tab[0] = tk
            _populate()

        for idx, (tk, tlbl) in enumerate([("muted", "Chat Muted"), ("nicks", "Settled Nicks"), ("autogreet", "Auto Greet")]):
            tx = 12 + idx * (tab_w + 6)
            tab_btns[tk] = GlassButton(
                parent=cnt, position=(tx, tab_y), size=(tab_w, 28),
                label=tlbl, text_scale=0.55,
                bg_color=(0.08, 0.11, 0.16), opacity=0.32,
                border=True, border_color=ol, border_opacity=0.40, border_thickness=1.1,
                on_activate_call=babase.CallPartial(_switch, tk))

        _populate()

        def _close():
            bui.containerwidget(edit=cnt, transition='out_scale')

        ghost_cancel = bui.buttonwidget(parent=cnt, position=(-9000, -9000), size=(1, 1), label='', on_activate_call=_close)
        bui.containerwidget(edit=cnt, cancel_button=ghost_cancel)

        GlassButton(
            parent=cnt, position=(c_width * 0.5 - 65, 10), size=(130, 34),
            label='Done', text_scale=0.66,
            bg_color=(0.16, 0.24, 0.34), opacity=0.55,
            border=True, border_color=ol, border_opacity=0.85, border_thickness=1.2,
            on_activate_call=_close)

    def _open_cyber_color_picker(self, tag_name: str, initial_color: tuple, title: str = "🎨 Custom Color Picker") -> None:
        """Pure Cyber-Glass RGB/Hex/Swatch color picker (replaces BombSquad clay ColorPickerExact)."""
        c_width, c_height = 440, 355
        ol = getattr(self, '_outline_color', (0.4, 1.0, 0.5))
        uiscale = bui.app.ui_v1.uiscale
        weak_self = weakref.ref(self)

        try:
            r0, g0, b0 = [max(0.0, min(1.0, float(v))) for v in initial_color[:3]]
        except Exception:
            r0, g0, b0 = (0.25, 0.45, 0.35)
        rgb = [r0, g0, b0]

        cnt = bui.containerwidget(
            size=(c_width, c_height),
            scale=(1.45 if uiscale is babase.UIScale.SMALL else
                   1.16 if uiscale is babase.UIScale.MEDIUM else 1.0),
            transition='in_scale',
            background=False,
            parent=bui.get_special_widget('overlay_stack'))

        _draw_panel_bg(cnt, 0, 0, c_width, c_height, color=(0.05, 0.07, 0.11), opacity=0.97)
        _draw_border(cnt, 0, 0, c_width, c_height, color=ol, opacity=0.88, thickness=1.5)

        bui.textwidget(
            parent=cnt, position=(c_width * 0.5, c_height - 20), size=(0, 0),
            h_align='center', v_align='center',
            text=title, scale=0.80, color=(1.0, 0.88, 0.35))

        prev_bg = _draw_panel_bg(cnt, 14, c_height - 82, 118, 42, color=tuple(rgb), opacity=0.95)
        _draw_border(cnt, 14, c_height - 82, 118, 42, color=ol, opacity=0.80, thickness=1.2)
        rgb_txt = bui.textwidget(
            parent=cnt, position=(144, c_height - 52), size=(0, 0),
            h_align='left', v_align='center',
            text='', scale=0.48, color=(0.80, 0.90, 1.0))

        def _rgb_to_hex(col_vals):
            return "#{:02X}{:02X}{:02X}".format(
                int(round(col_vals[0] * 255)),
                int(round(col_vals[1] * 255)),
                int(round(col_vals[2] * 255)))

        hex_field = _draw_glass_textbox(
            cnt, 144, c_height - 84, 154, 28, ol=ol,
            text=_rgb_to_hex(rgb), max_chars=9,
            opacity=0.78, border_opacity=0.60, border_thickness=1.1,
            description='#RRGGBB')

        bar_fills: List[bui.Widget] = []
        bar_labels: List[bui.Widget] = []
        bar_w = 152

        def _sync_ui(update_hex: bool = True):
            cur_t = tuple(rgb)
            bui.imagewidget(edit=prev_bg, color=cur_t)
            bui.textwidget(
                edit=rgb_txt,
                text=f"RGB: ({int(rgb[0]*255)}, {int(rgb[1]*255)}, {int(rgb[2]*255)})")
            if update_hex:
                bui.textwidget(edit=hex_field, text=_rgb_to_hex(rgb))
            for ch_i in range(3):
                val = rgb[ch_i]
                bui.imagewidget(edit=bar_fills[ch_i], size=(max(2, bar_w * val), 14))
                bui.textwidget(edit=bar_labels[ch_i], text=f"{int(round(val * 100))}%")
            inst = weak_self()
            if inst is not None:
                inst.color_picker_selected_color(None, cur_t, tag_override=tag_name)

        def _apply_hex():
            raw = (bui.textwidget(query=hex_field) or "").strip().lstrip('#')
            if len(raw) == 6:
                try:
                    rgb[0] = max(0.0, min(1.0, int(raw[0:2], 16) / 255.0))
                    rgb[1] = max(0.0, min(1.0, int(raw[2:4], 16) / 255.0))
                    rgb[2] = max(0.0, min(1.0, int(raw[4:6], 16) / 255.0))
                    _sync_ui(update_hex=False)
                    return
                except Exception:
                    pass
            bui.screenmessage("Enter valid 6-digit hex like #2E8B57", color=(1.0, 0.55, 0.35))

        GlassButton(
            parent=cnt, position=(304, c_height - 84), size=(122, 28),
            label='Apply Hex', text_scale=0.50,
            bg_color=(0.14, 0.34, 0.24), opacity=0.55,
            border=True, border_color=ol, border_opacity=0.80, border_thickness=1.1,
            on_activate_call=_apply_hex)

        swatches = [
            (0.25, 0.55, 0.40), (0.15, 0.50, 0.68), (0.18, 0.34, 0.72), (0.44, 0.22, 0.68),
            (0.66, 0.18, 0.28), (0.72, 0.46, 0.14), (0.18, 0.24, 0.32), (0.95, 0.97, 1.00),
            (0.40, 1.00, 0.85), (1.00, 0.88, 0.36),
        ]
        sw_s = 36
        for idx_s, scol in enumerate(swatches):
            def _pick_sw(c=scol):
                rgb[0], rgb[1], rgb[2] = c
                _sync_ui()

            GlassButton(
                parent=cnt, position=(14 + idx_s * (sw_s + 5), c_height - 126), size=(sw_s, 26),
                label='', bg_color=scol, opacity=0.92,
                border=True, border_color=(1, 1, 1), border_opacity=0.65, border_thickness=1.0,
                on_activate_call=_pick_sw)

        ch_specs = [
            ("R", (1.0, 0.38, 0.42)),
            ("G", (0.38, 1.0, 0.52)),
            ("B", (0.42, 0.72, 1.0)),
        ]

        def _nudge(ci: int, delta: float):
            rgb[ci] = max(0.0, min(1.0, round(rgb[ci] + delta, 3)))
            _sync_ui()

        for ci, (cname, ccol) in enumerate(ch_specs):
            ry = c_height - 172 - ci * 44
            bui.textwidget(
                parent=cnt, position=(18, ry + 13), size=(0, 0),
                h_align='left', v_align='center', text=cname, scale=0.60, color=ccol)
            _draw_panel_bg(cnt, 42, ry + 6, bar_w, 14, color=(0.02, 0.04, 0.07), opacity=0.85)
            _draw_border(cnt, 42, ry + 6, bar_w, 14, color=ccol, opacity=0.45, thickness=1.0)
            fill = bui.imagewidget(
                parent=cnt, position=(42, ry + 6), size=(max(2, bar_w * rgb[ci]), 14),
                texture=bui.gettexture('white'), color=ccol, opacity=0.85)
            bar_fills.append(fill)
            pct = bui.textwidget(
                parent=cnt, position=(42 + bar_w + 22, ry + 13), size=(0, 0),
                h_align='center', v_align='center', text=f"{int(round(rgb[ci]*100))}%",
                scale=0.45, color=(0.88, 0.94, 1.0))
            bar_labels.append(pct)

            steps = [("-10", -0.10), ("-2", -0.02), ("+2", 0.02), ("+10", 0.10)]
            for si, (slbl, sdelta) in enumerate(steps):
                GlassButton(
                    parent=cnt, position=(238 + si * 48, ry), size=(44, 26),
                    label=slbl, text_scale=0.45,
                    bg_color=(0.10, 0.16, 0.24), opacity=0.52,
                    border=True, border_color=ccol, border_opacity=0.60, border_thickness=1.0,
                    on_activate_call=babase.CallPartial(_nudge, ci, sdelta))

        _sync_ui()

        def _done():
            inst = weak_self()
            if inst is not None:
                inst.color_picker_selected_color(None, tuple(rgb), tag_override=tag_name)
            babase._appconfig.commit_app_config()
            bui.containerwidget(edit=cnt, transition='out_scale')

        def _cancel():
            inst = weak_self()
            if inst is not None:
                inst.color_picker_selected_color(None, (r0, g0, b0), tag_override=tag_name)
            bui.containerwidget(edit=cnt, transition='out_scale')

        ghost_cancel = bui.buttonwidget(parent=cnt, position=(-9000, -9000), size=(1, 1), label='', on_activate_call=_cancel)
        bui.containerwidget(edit=cnt, cancel_button=ghost_cancel)

        GlassButton(
            parent=cnt, position=(14, 12), size=(120, 32),
            label='Cancel', text_scale=0.58,
            bg_color=(0.35, 0.16, 0.18), opacity=0.48,
            border=True, border_color=(1.0, 0.45, 0.48), border_opacity=0.75, border_thickness=1.1,
            on_activate_call=_cancel)
        GlassButton(
            parent=cnt, position=(c_width - 144, 12), size=(130, 32),
            label='Apply Color', text_scale=0.58,
            bg_color=(0.14, 0.38, 0.24), opacity=0.58,
            border=True, border_color=ol, border_opacity=0.88, border_thickness=1.2,
            on_activate_call=_done)

    def _open_colors_window(self) -> None:
        """Compact Cyber-Glass Color Manager: Roster Player/Nick Colors, Window Presets & Custom Picker."""
        c_width, c_height = 460, 360
        ol = getattr(self, '_outline_color', (0.4, 1.0, 0.5))
        uiscale = bui.app.ui_v1.uiscale
        weak_self = weakref.ref(self)

        cnt = bui.containerwidget(
            size=(c_width, c_height),
            scale=(1.45 if uiscale is babase.UIScale.SMALL else
                   1.16 if uiscale is babase.UIScale.MEDIUM else 1.0),
            transition='in_scale',
            background=False,
            parent=bui.get_special_widget('overlay_stack'))

        _draw_panel_bg(cnt, 0, 0, c_width, c_height, color=(0.05, 0.07, 0.11), opacity=0.96)
        _draw_border(cnt, 0, 0, c_width, c_height, color=ol, opacity=0.85, thickness=1.5)

        bui.textwidget(
            parent=cnt, position=(c_width * 0.5, c_height - 20), size=(0, 0),
            h_align='center', v_align='center',
            text='🎨 Colors & Theme', scale=0.82, color=(1.0, 0.88, 0.35))

        swatches = [
            ("White", (0.95, 0.97, 1.00)),
            ("Cyan",  (0.40, 1.00, 0.85)),
            ("Sky",   (0.48, 0.82, 1.00)),
            ("Gold",  (1.00, 0.88, 0.36)),
            ("Lime",  (0.55, 1.00, 0.45)),
            ("Pink",  (1.00, 0.60, 0.88)),
        ]
        win_presets = [
            ("Emerald",  (0.25, 0.45, 0.35)),
            ("Cyan",     (0.14, 0.48, 0.66)),
            ("Cobalt",   (0.18, 0.32, 0.68)),
            ("Violet",   (0.42, 0.22, 0.66)),
            ("Crimson",  (0.62, 0.16, 0.24)),
            ("Obsidian", (0.16, 0.20, 0.26)),
        ]

        def _set_roster_color(cfg_key: str, col: tuple, label_name: str):
            babase.app.config[cfg_key] = tuple(col)
            babase.app.config.commit()
            inst = weak_self()
            if inst is not None and inst.active_tab == "players":
                inst._render_players_tab()
            bui.screenmessage(f"{label_name} color updated!", color=col)

        def _set_window_preset(col: tuple, label_name: str):
            inst = weak_self()
            if inst is not None:
                inst.color_picker_selected_color(None, col, tag_override='')
                babase._appconfig.commit_app_config()
            bui.screenmessage(f"Window theme: {label_name}", color=col)

        def _open_picker(tag_name: str, init_col: tuple, p_title: str = "🎨 Custom Color Picker"):
            bui.containerwidget(edit=cnt, transition='out_scale')
            inst = weak_self()
            if inst is not None:
                inst._open_cyber_color_picker(tag_name, init_col, title=p_title)

        p_col, n_col = _apw_get_roster_colors()
        cur_win_col = getattr(self, '_bg_color', (0.25, 0.45, 0.35))

        bui.textwidget(
            parent=cnt, position=(14, c_height - 50), size=(0, 0),
            h_align='left', v_align='center',
            text='Window Color Suggestions:', scale=0.52, color=(0.80, 0.88, 0.98))
        sw_w = 50
        for i, (wname, wcol) in enumerate(win_presets):
            GlassButton(
                parent=cnt, position=(14 + i * (sw_w + 4), c_height - 90), size=(sw_w, 28),
                label=wname, text_scale=0.41,
                bg_color=(wcol[0] * 0.60, wcol[1] * 0.60, wcol[2] * 0.60), opacity=0.75,
                text_color=(0.95, 0.98, 1.0),
                border=True, border_color=(min(1.0, wcol[0] * 0.4 + 0.35), min(1.0, wcol[1] * 0.4 + 0.70), min(1.0, wcol[2] * 0.4 + 0.45)),
                border_opacity=0.85, border_thickness=1.1,
                on_activate_call=babase.CallPartial(_set_window_preset, wcol, wname))
        GlassButton(
            parent=cnt, position=(c_width - 108, c_height - 90), size=(94, 28),
            label='Custom...', text_scale=0.48,
            bg_color=(0.14, 0.22, 0.34), opacity=0.55,
            border=True, border_color=ol, border_opacity=0.75, border_thickness=1.1,
            on_activate_call=babase.CallPartial(_open_picker, '', cur_win_col, '🎨 Custom Window Color'))

        bui.textwidget(
            parent=cnt, position=(14, c_height - 116), size=(0, 0),
            h_align='left', v_align='center',
            text='Roster Player Names Color:', scale=0.52, color=(0.80, 0.88, 0.98))
        for i, (sname, scol) in enumerate(swatches):
            GlassButton(
                parent=cnt, position=(14 + i * (sw_w + 4), c_height - 156), size=(sw_w, 28),
                label=sname, text_scale=0.45,
                bg_color=(scol[0] * 0.30, scol[1] * 0.30, scol[2] * 0.30), opacity=0.65,
                text_color=scol,
                border=True, border_color=scol, border_opacity=0.80, border_thickness=1.1,
                on_activate_call=babase.CallPartial(_set_roster_color, 'APW_Roster_PlayerColor', scol, 'Player Name'))
        GlassButton(
            parent=cnt, position=(c_width - 108, c_height - 156), size=(94, 28),
            label='Custom...', text_scale=0.48,
            bg_color=(0.14, 0.22, 0.34), opacity=0.55,
            border=True, border_color=ol, border_opacity=0.70, border_thickness=1.1,
            on_activate_call=babase.CallPartial(_open_picker, 'roster_player', p_col, '🎨 Player Name Color'))

        bui.textwidget(
            parent=cnt, position=(14, c_height - 182), size=(0, 0),
            h_align='left', v_align='center',
            text='Roster Nicknames Color:', scale=0.52, color=(0.80, 0.88, 0.98))
        for i, (sname, scol) in enumerate(swatches):
            GlassButton(
                parent=cnt, position=(14 + i * (sw_w + 4), c_height - 222), size=(sw_w, 28),
                label=sname, text_scale=0.45,
                bg_color=(scol[0] * 0.30, scol[1] * 0.30, scol[2] * 0.30), opacity=0.65,
                text_color=scol,
                border=True, border_color=scol, border_opacity=0.80, border_thickness=1.1,
                on_activate_call=babase.CallPartial(_set_roster_color, 'APW_Roster_NickColor', scol, 'Nickname'))
        GlassButton(
            parent=cnt, position=(c_width - 108, c_height - 222), size=(94, 28),
            label='Custom...', text_scale=0.48,
            bg_color=(0.14, 0.22, 0.34), opacity=0.55,
            border=True, border_color=ol, border_opacity=0.70, border_thickness=1.1,
            on_activate_call=babase.CallPartial(_open_picker, 'roster_nick', n_col, '🎨 Nickname Color'))

        cc_btn = GlassButton(
            parent=cnt, position=(14, c_height - 274), size=(210, 32),
            label=f"✨ Colorful Chat: {'ON' if _apw_is_colorful_chat() else 'OFF'}", text_scale=0.52,
            bg_color=(0.14, 0.32, 0.26) if _apw_is_colorful_chat() else (0.14, 0.16, 0.22), opacity=0.52,
            border=True, border_color=ol, border_opacity=0.75, border_thickness=1.1)

        def _toggle_cc():
            cur = _apw_is_colorful_chat()
            babase.app.config['APW_Colorful_Chat'] = not cur
            babase.app.config.commit()
            cc_btn.set_text(f"✨ Colorful Chat: {'ON' if not cur else 'OFF'}")
            cc_btn.set_color(
                bg_color=(0.14, 0.32, 0.26) if not cur else (0.14, 0.16, 0.22),
                opacity=0.52)
            inst = weak_self()
            if inst is not None:
                inst._recolor_chat_items()

        def _rand_cc():
            babase.app.config['APW_Colorful_Chat'] = True
            babase.app.config['APW_Chat_Color_Seed'] = random.randint(1, 999999)
            babase.app.config.commit()
            cc_btn.set_text("✨ Colorful Chat: ON")
            cc_btn.set_color(bg_color=(0.14, 0.32, 0.26), opacity=0.52)
            inst = weak_self()
            if inst is not None:
                inst._recolor_chat_items()
            bui.screenmessage("Randomized chat colors!", color=(0.55, 0.95, 1.0))

        cc_btn.set_on_activate(_toggle_cc)

        GlassButton(
            parent=cnt, position=(232, c_height - 274), size=(214, 32),
            label='🎲 Randomize Chat Colors', text_scale=0.52,
            bg_color=(0.18, 0.22, 0.38), opacity=0.52,
            border=True, border_color=(0.55, 0.85, 1.0), border_opacity=0.75, border_thickness=1.1,
            on_activate_call=_rand_cc)

        sync_ol_on = bool(babase.app.config.get('APW_Sync_Outline', True))
        sync_ol_btn = GlassButton(
            parent=cnt, position=(14, 12), size=(210, 34),
            label=f"Sync Outlines: {'ON' if sync_ol_on else 'OFF'}", text_scale=0.52,
            bg_color=(0.12, 0.34, 0.24) if sync_ol_on else (0.14, 0.16, 0.22),
            opacity=0.55 if sync_ol_on else 0.45,
            border=True, border_color=ol, border_opacity=0.80, border_thickness=1.1)

        def _toggle_sync_outline():
            cur = bool(babase.app.config.get('APW_Sync_Outline', True))
            nxt = not cur
            babase.app.config['APW_Sync_Outline'] = nxt
            babase.app.config.commit()
            sync_ol_btn.set_text(f"Sync Outlines: {'ON' if nxt else 'OFF'}")
            sync_ol_btn.set_color(
                bg_color=(0.12, 0.34, 0.24) if nxt else (0.14, 0.16, 0.22),
                opacity=0.55 if nxt else 0.45)
            inst = weak_self()
            if inst is not None:
                cur_c = getattr(inst, '_bg_color', (0.25, 0.45, 0.35))
                inst.color_picker_selected_color(None, cur_c, tag_override='')
                babase._appconfig.commit_app_config()
                new_ol = getattr(inst, '_outline_color', ol)
                sync_ol_btn.set_border_color(color=new_ol, opacity=0.85)
            bui.screenmessage(
                f"Sync Outlines with Window Color: {'ON' if nxt else 'OFF'}",
                color=(0.55, 0.95, 1.0))

        sync_ol_btn.set_on_activate(_toggle_sync_outline)

        def _close():
            bui.containerwidget(edit=cnt, transition='out_scale')

        ghost_cancel = bui.buttonwidget(parent=cnt, position=(-9000, -9000), size=(1, 1), label='', on_activate_call=_close)
        bui.containerwidget(edit=cnt, cancel_button=ghost_cancel)

        GlassButton(
            parent=cnt, position=(c_width - 134, 12), size=(120, 34),
            label='Done', text_scale=0.66,
            bg_color=(0.16, 0.24, 0.34), opacity=0.55,
            border=True, border_color=ol, border_opacity=0.85, border_thickness=1.2,
            on_activate_call=_close)

    def _open_translate_settings_window(self) -> None:
        """Universal Cyber-Glass Translate Settings: All World Languages, Romanized Mode & Custom Code."""
        c_width, c_height = 520, 445
        ol = getattr(self, '_outline_color', (0.4, 1.0, 0.5))
        uiscale = bui.app.ui_v1.uiscale
        weak_self = weakref.ref(self)

        cnt = bui.containerwidget(
            size=(c_width, c_height),
            scale=(1.40 if uiscale is babase.UIScale.SMALL else
                   1.14 if uiscale is babase.UIScale.MEDIUM else 1.0),
            transition='in_scale',
            background=False,
            parent=bui.get_special_widget('overlay_stack'))

        _draw_panel_bg(cnt, 0, 0, c_width, c_height, color=(0.05, 0.07, 0.11), opacity=0.96)
        _draw_border(cnt, 0, 0, c_width, c_height, color=ol, opacity=0.85, thickness=1.5)

        bui.textwidget(
            parent=cnt, position=(c_width * 0.5, c_height - 20), size=(0, 0),
            h_align='center', v_align='center',
            text='🌐 Universal Translate Settings', scale=0.80, color=(1.0, 0.88, 0.35))

        tcfg = _apw_get_translate_cfg()
        active_tab = ["target"]

        rom_btn = GlassButton(
            parent=cnt, position=(12, c_height - 68), size=(c_width - 24, 28),
            label='', text_scale=0.49,
            border=True, border_color=ol, border_opacity=0.75, border_thickness=1.1)

        tab_y = c_height - 104
        tab_w = (c_width - 30) / 2
        tab_source_gb = GlassButton(
            parent=cnt, position=(12, tab_y), size=(tab_w, 28),
            label='', text_scale=0.48,
            border=True, border_color=ol, border_opacity=0.60, border_thickness=1.1)
        tab_target_gb = GlassButton(
            parent=cnt, position=(18 + tab_w, tab_y), size=(tab_w, 28),
            label='', text_scale=0.48,
            border=True, border_color=ol, border_opacity=0.60, border_thickness=1.1)

        bui.textwidget(
            parent=cnt, position=(14, c_height - 126), size=(0, 0),
            h_align='left', v_align='center',
            text='Search or Custom ISO Code:', scale=0.46, color=(0.72, 0.84, 0.96))
        query_field = _draw_glass_textbox(
            cnt, 196, c_height - 142, 166, 30, ol=ol,
            text='', max_chars=24, opacity=0.78, border_opacity=0.60, border_thickness=1.1,
            description='Filter languages or enter ISO code')

        filter_btn = GlassButton(
            parent=cnt, position=(368, c_height - 142), size=(64, 30),
            label='Filter', text_scale=0.50,
            bg_color=(0.12, 0.24, 0.38), opacity=0.52,
            border=True, border_color=(0.45, 0.80, 1.0), border_opacity=0.70, border_thickness=1.0)
        set_code_btn = GlassButton(
            parent=cnt, position=(436, c_height - 142), size=(72, 30),
            label='Set Code', text_scale=0.48,
            bg_color=(0.14, 0.38, 0.24), opacity=0.55,
            border=True, border_color=ol, border_opacity=0.80, border_thickness=1.0)

        list_x, list_y, list_w, list_h = 12, 54, c_width - 24, c_height - 204
        _draw_panel_bg(cnt, list_x, list_y, list_w, list_h, color=(0.03, 0.05, 0.08), opacity=0.78)
        _draw_border(cnt, list_x, list_y, list_w, list_h, color=ol, opacity=0.48, thickness=1.1)
        scroll = bui.scrollwidget(
            parent=cnt, position=(list_x + 4, list_y + 4), size=(list_w - 8, list_h - 8),
            highlight=False, border_opacity=0.0)
        list_col = bui.columnwidget(parent=scroll, border=0, margin=3)

        def _apply_selection(code_val: str):
            code = code_val.strip()
            if not code:
                return
            if active_tab[0] == "target":
                if code.lower() == "auto":
                    bui.screenmessage("Target must be a specific language code!", color=(1.0, 0.5, 0.3))
                    return
                tcfg["tl"] = code
                babase.app.config['APW_Translate_Lang'] = code
            else:
                tcfg["sl"] = code
                babase.app.config['APW_Translate_Source'] = code
            babase.app.config.commit()
            _sync_header()
            _populate_langs()
            inst = weak_self()
            if inst is not None and _apw_get_translate_cfg()["enabled"]:
                inst._refresh_all_chat_translations()

        def _sync_header():
            r_on = tcfg["romanized"]
            rom_btn.set_text(f"🗣️ Romanized Text Mode (Hinglish, Arabizi, RU Translit, etc.): {'ON' if r_on else 'OFF'}")
            rom_btn.set_color(
                bg_color=(0.12, 0.34, 0.24) if r_on else (0.24, 0.14, 0.16),
                opacity=0.55 if r_on else 0.45,
                text_color=(0.85, 1.0, 0.88) if r_on else (1.0, 0.78, 0.78))

            is_tgt = (active_tab[0] == "target")
            tab_target_gb.set_text(f"Into: {_apw_get_lang_label(tcfg['tl'])}")
            tab_target_gb.set_color(
                bg_color=(0.14, 0.34, 0.25) if is_tgt else (0.08, 0.11, 0.16),
                opacity=0.58 if is_tgt else 0.35,
                text_color=(1, 1, 1) if is_tgt else (0.70, 0.80, 0.90))
            tab_target_gb.set_border_color(color=ol, opacity=0.90 if is_tgt else 0.35)

            tab_source_gb.set_text(f"From: {_apw_get_lang_label(tcfg['sl'])}")
            tab_source_gb.set_color(
                bg_color=(0.14, 0.34, 0.25) if not is_tgt else (0.08, 0.11, 0.16),
                opacity=0.58 if not is_tgt else 0.35,
                text_color=(1, 1, 1) if not is_tgt else (0.70, 0.80, 0.90))
            tab_source_gb.set_border_color(color=ol, opacity=0.90 if not is_tgt else 0.35)

        def _populate_langs():
            for ch in list_col.get_children():
                ch.delete()
            q = (bui.textwidget(query=query_field) or '').strip().lower()
            items = []
            if active_tab[0] == "source":
                items.append(("Auto-Detect (All + Romanized)", "auto"))
            items.extend(_APW_TRANSLATE_LANGS)
            if q:
                items = [(n, c) for n, c in items if q in n.lower() or q in c.lower()]

            cur_code = tcfg["tl"] if active_tab[0] == "target" else tcfg["sl"]
            row_w = list_w - 28
            if not items:
                bui.textwidget(
                    parent=list_col, size=(row_w, 80),
                    h_align='center', v_align='center',
                    text="No preset match — press 'Set Code' to use your custom ISO code!",
                    scale=0.52, color=(0.68, 0.78, 0.88))
                return

            cols = 2
            cw = (row_w - 6) / cols
            for i in range(0, len(items), cols):
                rc = bui.containerwidget(parent=list_col, size=(row_w, 34), background=False)
                for j in range(cols):
                    if i + j >= len(items):
                        break
                    lname, lcode = items[i + j]
                    is_sel = (lcode.lower() == cur_code.lower())
                    GlassButton(
                        parent=rc, position=(j * (cw + 6), 2), size=(cw, 30),
                        label=f"{lname} [{lcode}]", text_scale=0.46,
                        bg_color=(0.14, 0.38, 0.26) if is_sel else (0.10, 0.14, 0.20),
                        opacity=0.62 if is_sel else 0.42,
                        text_color=(1.0, 0.95, 0.55) if is_sel else (0.88, 0.94, 1.0),
                        border=True, border_color=ol, border_opacity=0.90 if is_sel else 0.38, border_thickness=1.0,
                        on_activate_call=babase.CallPartial(_apply_selection, lcode))

        def _toggle_rom():
            tcfg["romanized"] = not tcfg["romanized"]
            babase.app.config['APW_Translate_Romanized'] = tcfg["romanized"]
            babase.app.config.commit()
            _sync_header()
            inst = weak_self()
            if inst is not None and _apw_get_translate_cfg()["enabled"]:
                inst._refresh_all_chat_translations()

        def _switch_tab(tab_name: str):
            active_tab[0] = tab_name
            _sync_header()
            _populate_langs()

        def _apply_custom_code():
            raw_c = (bui.textwidget(query=query_field) or '').strip()
            if not raw_c:
                bui.screenmessage("Type any ISO code (e.g. ja, ko, ar, ru, es, auto)", color=(1.0, 0.78, 0.35))
                return
            _apply_selection(raw_c)
            bui.screenmessage(f"Language set to: {raw_c}", color=(0.45, 1.0, 0.65))

        rom_btn.set_on_activate(_toggle_rom)
        tab_target_gb.set_on_activate(babase.CallPartial(_switch_tab, "target"))
        tab_source_gb.set_on_activate(babase.CallPartial(_switch_tab, "source"))
        filter_btn.set_on_activate(_populate_langs)
        set_code_btn.set_on_activate(_apply_custom_code)

        _sync_header()
        _populate_langs()

        def _close():
            bui.containerwidget(edit=cnt, transition='out_scale')

        ghost_cancel = bui.buttonwidget(parent=cnt, position=(-9000, -9000), size=(1, 1), label='', on_activate_call=_close)
        bui.containerwidget(edit=cnt, cancel_button=ghost_cancel)

        GlassButton(
            parent=cnt, position=(c_width - 134, 10), size=(122, 34),
            label='Done', text_scale=0.66,
            bg_color=(0.16, 0.24, 0.34), opacity=0.55,
            border=True, border_color=ol, border_opacity=0.85, border_thickness=1.2,
            on_activate_call=_close)

    def _open_chat_logs_window(self) -> None:
        """Cyber-Glass Chat Logs Manager: Logger ON/OFF + Dated Session Logs (View / Rename / Delete)."""
        c_width, c_height = 530, 440
        ol = getattr(self, '_outline_color', (0.4, 1.0, 0.5))
        uiscale = bui.app.ui_v1.uiscale

        cnt = bui.containerwidget(
            size=(c_width, c_height),
            scale=(1.40 if uiscale is babase.UIScale.SMALL else
                   1.14 if uiscale is babase.UIScale.MEDIUM else 1.0),
            transition='in_scale',
            background=False,
            parent=bui.get_special_widget('overlay_stack'))

        _draw_panel_bg(cnt, 0, 0, c_width, c_height, color=(0.05, 0.07, 0.11), opacity=0.96)
        _draw_border(cnt, 0, 0, c_width, c_height, color=ol, opacity=0.85, thickness=1.5)

        bui.textwidget(
            parent=cnt, position=(c_width * 0.5, c_height - 20), size=(0, 0),
            h_align='center', v_align='center',
            text='📜 Saved Chat Logs', scale=0.82, color=(1.0, 0.88, 0.35))

        log_btn = GlassButton(
            parent=cnt, position=(12, c_height - 66), size=(c_width - 24, 30),
            label='', text_scale=0.56,
            border=True, border_color=ol, border_opacity=0.75, border_thickness=1.2)

        def _sync_log_btn():
            on = _apw_is_chatlogger_enabled()
            log_btn.set_text(f"📝 Session Chat Logger: {'ON (Auto-Saving)' if on else 'OFF'}")
            log_btn.set_color(
                bg_color=(0.12, 0.34, 0.22) if on else (0.24, 0.14, 0.16),
                opacity=0.55 if on else 0.45,
                text_color=(0.85, 1.0, 0.88) if on else (1.0, 0.78, 0.78))
            log_btn.set_border_color(color=ol if on else (1.0, 0.45, 0.48), opacity=0.85)

        def _toggle_logger():
            nxt = not _apw_is_chatlogger_enabled()
            _apw_set_chatlogger_enabled(nxt)
            _sync_log_btn()
            if nxt:
                _apw_chatlog_tick()
                _populate_logs()

        log_btn.set_on_activate(_toggle_logger)
        _sync_log_btn()

        list_x, list_y, list_w, list_h = 12, 54, c_width - 24, c_height - 130
        _draw_panel_bg(cnt, list_x, list_y, list_w, list_h, color=(0.03, 0.05, 0.08), opacity=0.78)
        _draw_border(cnt, list_x, list_y, list_w, list_h, color=ol, opacity=0.48, thickness=1.1)
        scroll = bui.scrollwidget(
            parent=cnt, position=(list_x + 4, list_y + 4), size=(list_w - 8, list_h - 8),
            highlight=False, border_opacity=0.0)
        list_col = bui.columnwidget(parent=scroll, border=0, margin=3)

        def _open_viewer(log_data: Dict[str, Any]):
            vw, vh = 500, 410
            vcnt = bui.containerwidget(
                size=(vw, vh),
                scale=(1.42 if uiscale is babase.UIScale.SMALL else
                       1.14 if uiscale is babase.UIScale.MEDIUM else 1.0),
                transition='in_scale', background=False,
                parent=bui.get_special_widget('overlay_stack'))
            _draw_panel_bg(vcnt, 0, 0, vw, vh, color=(0.05, 0.07, 0.11), opacity=0.97)
            _draw_border(vcnt, 0, 0, vw, vh, color=ol, opacity=0.88, thickness=1.5)
            bui.textwidget(
                parent=vcnt, position=(vw * 0.5, vh - 20), size=(0, 0),
                h_align='center', v_align='center',
                text=babase.Lstr(value=str(log_data.get("title", "Chat Log"))),
                scale=0.74, color=(1.0, 0.88, 0.35), maxwidth=vw - 32)
            bui.textwidget(
                parent=vcnt, position=(vw * 0.5, vh - 38), size=(0, 0),
                h_align='center', v_align='center',
                text=f"{log_data.get('date', '')} • {log_data.get('addr', '')}",
                scale=0.46, color=(0.68, 0.78, 0.90), maxwidth=vw - 32)

            sx, sy, sw, sh = 12, 54, vw - 24, vh - 104
            _draw_panel_bg(vcnt, sx, sy, sw, sh, color=(0.02, 0.04, 0.07), opacity=0.80)
            _draw_border(vcnt, sx, sy, sw, sh, color=ol, opacity=0.45, thickness=1.0)
            vscroll = bui.scrollwidget(parent=vcnt, position=(sx + 4, sy + 4), size=(sw - 8, sh - 8), highlight=False)
            vcol = bui.columnwidget(parent=vscroll, border=0, margin=1)
            lines = log_data.get("messages", [])
            if not lines:
                bui.textwidget(parent=vcol, size=(sw - 20, 80), h_align='center', v_align='center',
                               text='(Empty log)', scale=0.60, color=(0.65, 0.72, 0.82))
            else:
                for line in lines:
                    lrow = bui.containerwidget(parent=vcol, size=(sw - 20, 20), background=False)
                    bui.textwidget(
                        parent=lrow, position=(6, 10), size=(0, 0),
                        h_align='left', v_align='center',
                        text=babase.Lstr(value=str(line)), scale=0.54,
                        color=(0.90, 0.95, 1.0), maxwidth=sw - 32)

            def _vclose():
                bui.containerwidget(edit=vcnt, transition='out_scale')

            def _copy_all():
                if bui.clipboard_is_supported():
                    bui.clipboard_set_text('\n'.join(str(x) for x in lines))
                    bui.screenmessage("Copied chat log!", color=(0.4, 1.0, 0.5))

            gc = bui.buttonwidget(parent=vcnt, position=(-9000, -9000), size=(1, 1), label='', on_activate_call=_vclose)
            bui.containerwidget(edit=vcnt, cancel_button=gc)
            GlassButton(parent=vcnt, position=(12, 10), size=(140, 34), label='Copy All', text_scale=0.58,
                        bg_color=(0.12, 0.24, 0.36), opacity=0.52,
                        border=True, border_color=(0.45, 0.80, 1.0), border_opacity=0.75, border_thickness=1.2,
                        on_activate_call=_copy_all)
            GlassButton(parent=vcnt, position=(vw - 134, 10), size=(122, 34), label='Back', text_scale=0.62,
                        bg_color=(0.35, 0.16, 0.18), opacity=0.48,
                        border=True, border_color=(1.0, 0.45, 0.48), border_opacity=0.75, border_thickness=1.2,
                        on_activate_call=_vclose)

        def _open_rename(log_data: Dict[str, Any]):
            rw, rh = 390, 154
            rcnt = bui.containerwidget(
                size=(rw, rh),
                scale=(1.45 if uiscale is babase.UIScale.SMALL else
                       1.18 if uiscale is babase.UIScale.MEDIUM else 1.0),
                transition='in_scale', background=False,
                parent=bui.get_special_widget('overlay_stack'))
            _draw_panel_bg(rcnt, 0, 0, rw, rh, color=(0.05, 0.07, 0.11), opacity=0.97)
            _draw_border(rcnt, 0, 0, rw, rh, color=ol, opacity=0.88, thickness=1.5)
            bui.textwidget(
                parent=rcnt, position=(rw * 0.5, rh - 22), size=(0, 0),
                h_align='center', v_align='center',
                text='Rename Chat Log', scale=0.74, color=(1.0, 0.88, 0.35))
            tf = _draw_glass_textbox(
                rcnt, 14, rh - 86, rw - 28, 34, ol=ol,
                text=str(log_data.get("title", "")), max_chars=60,
                opacity=0.78, border_opacity=0.65, border_thickness=1.1,
                description='New log title')

            def _rclose():
                bui.containerwidget(edit=rcnt, transition='out_scale')

            def _rsave():
                new_t = (bui.textwidget(query=tf) or "").strip()
                if not new_t:
                    bui.screenmessage("Title cannot be empty!", color=(1.0, 0.35, 0.35))
                    return
                if _apw_rename_chatlog(log_data.get("_path", ""), new_t):
                    bui.screenmessage("Renamed chat log!", color=(0.4, 1.0, 0.5))
                _rclose()
                _populate_logs()

            gc = bui.buttonwidget(parent=rcnt, position=(-9000, -9000), size=(1, 1), label='', on_activate_call=_rclose)
            bui.containerwidget(edit=rcnt, cancel_button=gc)
            GlassButton(parent=rcnt, position=(14, 12), size=(120, 34), label='Cancel',
                        bg_color=(0.35, 0.16, 0.18), opacity=0.45,
                        border=True, border_color=(1.0, 0.45, 0.48), border_opacity=0.75, border_thickness=1.2,
                        on_activate_call=_rclose)
            GlassButton(parent=rcnt, position=(rw - 134, 12), size=(120, 34), label='Save',
                        bg_color=(0.14, 0.42, 0.24), opacity=0.52,
                        border=True, border_color=ol, border_opacity=0.85, border_thickness=1.2,
                        on_activate_call=_rsave)

        def _populate_logs():
            for ch in list_col.get_children():
                ch.delete()
            logs = _apw_list_chatlogs()
            row_w = list_w - 28
            row_h = 48
            if not logs:
                bui.textwidget(
                    parent=list_col, size=(row_w, 120),
                    h_align='center', v_align='center',
                    text='No saved chat logs yet.\nTurn on Chat Logger above to record server sessions.',
                    scale=0.58, color=(0.62, 0.70, 0.80))
                return

            for ld in logs:
                rc = bui.containerwidget(parent=list_col, size=(row_w, row_h), background=False)
                _draw_panel_bg(rc, 0, 0, row_w, row_h, color=(0.10, 0.13, 0.19), opacity=0.55)
                _draw_border(rc, 0, 0, row_w, row_h, color=ol, opacity=0.32, thickness=1.0)
                bui.textwidget(
                    parent=rc, position=(10, 32), size=(0, 0),
                    h_align='left', v_align='center',
                    text=babase.Lstr(value=str(ld.get("title", "Log"))),
                    scale=0.56, color=(1.0, 0.92, 0.65), maxwidth=row_w - 178)
                sub = f"{ld.get('date', '')[:16]}  •  {len(ld.get('messages', []))} msgs"
                bui.textwidget(
                    parent=rc, position=(10, 14), size=(0, 0),
                    h_align='left', v_align='center',
                    text=sub, scale=0.44, color=(0.65, 0.80, 0.96), maxwidth=row_w - 178)

                bx = row_w - 164
                GlassButton(
                    parent=rc, position=(bx, 10), size=(50, 28),
                    label='View', text_scale=0.50,
                    bg_color=(0.12, 0.30, 0.24), opacity=0.52,
                    border=True, border_color=ol, border_opacity=0.70, border_thickness=1.0,
                    on_activate_call=babase.CallPartial(_open_viewer, ld))
                GlassButton(
                    parent=rc, position=(bx + 54, 10), size=(60, 28),
                    label='Rename', text_scale=0.46,
                    bg_color=(0.12, 0.24, 0.38), opacity=0.50,
                    border=True, border_color=(0.45, 0.80, 1.0), border_opacity=0.65, border_thickness=1.0,
                    on_activate_call=babase.CallPartial(_open_rename, ld))

                def _del_log(fp=ld.get("_path", "")):
                    _apw_delete_chatlog(fp)
                    _populate_logs()

                GlassButton(
                    parent=rc, position=(bx + 118, 10), size=(40, 28),
                    label='Del', text_scale=0.48,
                    bg_color=(0.38, 0.14, 0.16), opacity=0.55,
                    border=True, border_color=(1.0, 0.42, 0.45), border_opacity=0.70, border_thickness=1.0,
                    on_activate_call=_del_log)

        _populate_logs()

        def _close():
            bui.containerwidget(edit=cnt, transition='out_scale')

        ghost_cancel = bui.buttonwidget(parent=cnt, position=(-9000, -9000), size=(1, 1), label='', on_activate_call=_close)
        bui.containerwidget(edit=cnt, cancel_button=ghost_cancel)

        GlassButton(
            parent=cnt, position=(c_width - 134, 10), size=(122, 34),
            label='Done', text_scale=0.66,
            bg_color=(0.16, 0.24, 0.34), opacity=0.55,
            border=True, border_color=ol, border_opacity=0.85, border_thickness=1.2,
            on_activate_call=_close)

    def _on_menu_button_press(self):
        is_muted = babase.app.config.resolve('Chat Muted')
        ag_on = bool(babase.app.config.get('APW_AutoGreet_Enabled', True))
        hp_on = _apw_show_header_players()
        anim_lbl = dict(_APW_CHAT_ANIM_MODES).get(_apw_get_chat_anim_style(), 'Scanner')
        upd_avail = bool(_apw_update_state.get("available"))
        upd_tag = f"🔔 Updates (v{_apw_update_state.get('remote_version', 'New')})" if upd_avail else "🚀 Updates"
        choices = [
            "mute", "screenmsg", "translate", "chat_logs",
            "autogreet", "cmd_maker", "player_lists",
            "header_players", "chat_anim", "color",
            "updates", "help", "credits",
        ]
        choices_display = [
            "🔊 Unmute Chat" if is_muted else "🔇 Mute Chat",
            "👁️ Toggle Screen Messages",
            "🌐 Translate Settings",
            "📜 Chat Logs & Logger",
            f"👋 Auto Greet Setup ({'ON' if ag_on else 'OFF'})",
            "🛠️ Custom Command Maker",
            "📋 Player Lists",
            f"👥 Players Under Name ({'ON' if hp_on else 'OFF'})",
            f"✨ Chat Bar Anim: {anim_lbl}",
            "🎨 Colors & Chat Style",
            upd_tag,
            "❓ Help & Feature Guide",
            "ℹ️ Credits & About",
        ]
        self._popup_type = "menu"
        AlphaPopupMenu(
            position=self._menu_button.get_screen_space_center(),
            choices=choices, choices_display=choices_display,
            current_choice="translate", delegate=self)

    def color_picker_selected_color(self, picker, color, tag_override: Optional[str] = None) -> None:
        tag = tag_override if tag_override is not None else ''
        if not tag and picker is not None:
            try:
                if hasattr(picker, 'get_tag'):
                    tag = picker.get_tag() or ''
            except Exception:
                tag = ''
        if tag == 'roster_player':
            babase.app.config['APW_Roster_PlayerColor'] = tuple(color)
            babase.app.config.commit()
            if self.active_tab == "players":
                self._render_players_tab()
            return
        if tag == 'roster_nick':
            babase.app.config['APW_Roster_NickColor'] = tuple(color)
            babase.app.config.commit()
            if self.active_tab == "players":
                self._render_players_tab()
            return

        self._bg_color = color
        babase.app.config["PartyWindow_Main_Color"] = color
        r, g, b = color
        try:
            bui.imagewidget(edit=self._bg_image, color=(r * 0.14 + 0.03, g * 0.14 + 0.04, b * 0.14 + 0.06))
        except Exception:
            pass
        try:
            bui.imagewidget(edit=self._scroll_bg, color=(r * 0.08 + 0.02, g * 0.08 + 0.03, b * 0.08 + 0.05))
        except Exception:
            pass

        ol = _apw_compute_outline_color(color)
        self._outline_color = ol

        for blist in (getattr(self, '_window_borders', []),
                      getattr(self, '_header_borders', []),
                      getattr(self, '_header_dividers', []),
                      getattr(self, '_header_players_box_borders', []),
                      getattr(self, '_tab_track_borders', []),
                      getattr(self, '_scroll_borders', []),
                      getattr(self, '_anim_track_borders', []),
                      getattr(self, '_emoji_borders', []),
                      getattr(self, '_bottom_borders', []),
                      getattr(self, '_text_borders', [])):
            for line in blist:
                try:
                    bui.imagewidget(edit=line, color=ol)
                except Exception:
                    pass

        for btn in (getattr(self, '_menu_button_gb', None),
                    getattr(self, '_sorry_button_gb', None),
                    getattr(self, '_tab_chat', None),
                    getattr(self, '_tab_players', None),
                    getattr(self, '_tab_servers', None),
                    getattr(self, '_quick_button', None),
                    getattr(self, '_emoji_popup_btn', None),
                    getattr(self, '_send_button', None)):
            if btn is not None:
                btn.set_border_color(color=ol)

    def color_picker_closing(self, picker) -> None:
        babase._appconfig.commit_app_config()

    def hide_screen_msg(self):
        try:
            with open('ba_data/data/languages/english.json', encoding='utf-8') as file:
                eng = json.loads(file.read())
            keys = ['playerJoinedPartyText', 'playerLeftPartyText', 'chatBlockedText',
                    'kickVoteStartedText', 'kickWithChatText', 'kickOccurredText',
                    'kickVoteFailedText', 'votesNeededText', 'playerDelayedJoinText', 'playerLeftText']
            for k in keys:
                if k in eng:
                    eng[k] = ''
                if 'internal' in eng and k in eng['internal']:
                    eng['internal'][k] = ''
            with open('ba_data/data/languages/english.json', 'w', encoding='utf-8') as file:
                json.dump(eng, file)
        except Exception:
            pass
        bui.apptimer(0.5, lambda: bs.app.lang.setlanguage(babase.app.config.get('Lang', 'English') or 'English'))

    def restore_screen_msg(self):
        try:
            with open('ba_data/data/languages/english.json', encoding='utf-8') as file:
                eng = json.loads(file.read())
            eng['internal']['playerJoinedPartyText'] = "${NAME} joined the pawri!"
            eng['internal']['playerLeftPartyText'] = "${NAME} left the pawri."
            with open('ba_data/data/languages/english.json', 'w', encoding='utf-8') as file:
                json.dump(eng, file)
        except Exception:
            pass
        bui.apptimer(0.5, lambda: bs.app.lang.setlanguage(babase.app.config.get('Lang', 'English') or 'English'))

    def _open_updates_window(self) -> None:
        """Updates Center showing version status, changelog details, GitHub link & manual Update button."""
        ol = getattr(self, '_outline_color', (0.4, 1.0, 0.5))
        c_w, c_h = 490, 380
        uiscale = bui.app.ui_v1.uiscale
        cnt = bui.containerwidget(
            size=(c_w, c_h),
            scale=(1.42 if uiscale is babase.UIScale.SMALL else
                   1.15 if uiscale is babase.UIScale.MEDIUM else 1.0),
            transition='in_scale',
            background=False,
            parent=bui.get_special_widget('overlay_stack'))

        _draw_panel_bg(cnt, 0, 0, c_w, c_h, color=(0.05, 0.07, 0.11), opacity=0.97)
        _draw_border(cnt, 0, 0, c_w, c_h, color=ol, opacity=0.86, thickness=1.5)

        bui.textwidget(
            parent=cnt, position=(c_w * 0.5, c_h - 20), size=(0, 0),
            h_align='center', v_align='center',
            text='🚀 Plugin Updates', scale=0.82, color=(1.0, 0.88, 0.35))

        status_card_y = c_h - 94
        _draw_panel_bg(cnt, 12, status_card_y, c_w - 24, 54, color=(0.08, 0.12, 0.18), opacity=0.72)
        _draw_border(cnt, 12, status_card_y, c_w - 24, 54, color=ol, opacity=0.45, thickness=1.1)

        cur_lbl = bui.textwidget(
            parent=cnt, position=(22, status_card_y + 38), size=(0, 0),
            h_align='left', v_align='center',
            text=f"Installed Version: v{version_str}", scale=0.52, color=(0.82, 0.92, 1.0))
        remote_lbl = bui.textwidget(
            parent=cnt, position=(22, status_card_y + 16), size=(0, 0),
            h_align='left', v_align='center',
            text="", scale=0.50, color=(0.65, 0.95, 0.72), maxwidth=c_w - 150)

        scroll_x, scroll_y, scroll_w, scroll_h = 12, 56, c_w - 24, status_card_y - 64
        _draw_panel_bg(cnt, scroll_x, scroll_y, scroll_w, scroll_h, color=(0.02, 0.04, 0.07), opacity=0.76)
        _draw_border(cnt, scroll_x, scroll_y, scroll_w, scroll_h, color=ol, opacity=0.48, thickness=1.1)
        scroll = bui.scrollwidget(
            parent=cnt, position=(scroll_x + 4, scroll_y + 4), size=(scroll_w - 8, scroll_h - 8),
            highlight=False, border_opacity=0.0)
        cl_col = bui.columnwidget(parent=scroll, border=0, margin=4)

        upd_btn = GlassButton(
            parent=cnt, position=(c_w - 142, 12), size=(130, 34),
            label='Update Now', text_scale=0.56,
            bg_color=(0.14, 0.40, 0.24), opacity=0.60,
            border=True, border_color=ol, border_opacity=0.88, border_thickness=1.2)

        def _render_state():
            try:
                if not cnt:
                    return
            except Exception:
                return
            st = _apw_update_state
            if st.get("installed_pending_restart"):
                st_txt = f"Updated to v{st.get('remote_version', '?')} — Restart BombSquad to apply!"
                st_col = (0.42, 1.0, 0.55)
            elif st.get("checking"):
                st_txt = "Checking GitHub version.json..."
                st_col = (0.65, 0.88, 1.0)
            elif st.get("error"):
                st_txt = f"Check failed: {st['error'][:48]}"
                st_col = (1.0, 0.55, 0.45)
            elif st.get("available"):
                st_txt = f"New Update Ready: v{st.get('remote_version')}  (Press Update Now to install)"
                st_col = (1.0, 0.88, 0.35)
            elif st.get("checked"):
                rv = st.get("remote_version") or version_str
                st_txt = f"Latest on GitHub: v{rv}  (You are up to date)"
                st_col = (0.55, 0.95, 0.72)
            else:
                st_txt = "Press Check to query GitHub for updates."
                st_col = (0.72, 0.82, 0.92)
            bui.textwidget(edit=remote_lbl, text=st_txt, color=st_col)

            if st.get("installing"):
                upd_btn.set_text("Installing...")
                upd_btn.set_color(bg_color=(0.18, 0.28, 0.36), opacity=0.45)
            elif st.get("installed_pending_restart"):
                upd_btn.set_text("Restart Game")
                upd_btn.set_color(bg_color=(0.18, 0.38, 0.26), opacity=0.55)
            elif st.get("available"):
                upd_btn.set_text("Update Now")
                upd_btn.set_color(bg_color=(0.14, 0.44, 0.24), opacity=0.68)
            else:
                upd_btn.set_text("Reinstall")
                upd_btn.set_color(bg_color=(0.14, 0.22, 0.32), opacity=0.48)

            for ch in cl_col.get_children():
                ch.delete()

            blocks = []
            added_list = st.get("added") or []
            changed_list = st.get("changed") or []
            cl_str = (st.get("changelog") or "").strip()
            if added_list:
                blocks.append(("✨ Added", [str(x) for x in added_list if str(x).strip()], (0.52, 1.0, 0.68)))
            if changed_list:
                blocks.append(("🔧 Changed / Fixed", [str(x) for x in changed_list if str(x).strip()], (0.55, 0.90, 1.0)))
            if cl_str:
                blocks.append(("📝 Release Notes", [ln.strip() for ln in cl_str.splitlines() if ln.strip()], (0.92, 0.95, 1.0)))
            if not blocks:
                blocks.append(("📋 Update Info", [
                    f"Repository: {APW_REPO_URL}",
                    "Updates are strictly manual — files are downloaded only when you press Update.",
                ], (0.78, 0.86, 0.96)))

            row_w = scroll_w - 22
            for hdr_t, lines_l, hcol in blocks:
                bh = 26 + len(lines_l) * 17
                rc = bui.containerwidget(parent=cl_col, size=(row_w, bh), background=False)
                _draw_panel_bg(rc, 0, 2, row_w, bh - 4, color=(0.08, 0.12, 0.18), opacity=0.65)
                _draw_border(rc, 0, 2, row_w, bh - 4, color=ol, opacity=0.32, thickness=1.0)
                bui.textwidget(
                    parent=rc, position=(10, bh - 14), size=(0, 0),
                    h_align='left', v_align='center',
                    text=hdr_t, scale=0.54, color=hcol, maxwidth=row_w - 20)
                yl = bh - 32
                for line_t in lines_l:
                    bui.textwidget(
                        parent=rc, position=(14, yl), size=(0, 0),
                        h_align='left', v_align='center',
                        text=line_t, scale=0.44, color=(0.86, 0.92, 0.98), maxwidth=row_w - 26)
                    yl -= 16

        def _recheck():
            _apw_update_state["checking"] = True
            _render_state()
            start_new_thread(_apw_check_and_update, (_render_state,))

        def _do_update():
            if _apw_update_state.get("installed_pending_restart"):
                bui.screenmessage("Please restart BombSquad to apply the installed update.", color=(0.4, 1.0, 0.55))
                return
            _apw_install_update_async(lambda _ok: _render_state())
            _render_state()

        upd_btn.set_on_activate(_do_update)

        GlassButton(
            parent=cnt, position=(c_w - 114, status_card_y + 13), size=(90, 28),
            label='↻ Check', text_scale=0.48,
            bg_color=(0.14, 0.24, 0.38), opacity=0.58,
            border=True, border_color=(0.45, 0.80, 1.0), border_opacity=0.75, border_thickness=1.0,
            on_activate_call=_recheck)

        def _close():
            bui.containerwidget(edit=cnt, transition='out_scale')

        ghost_cancel = bui.buttonwidget(parent=cnt, position=(-9000, -9000), size=(1, 1), label='', on_activate_call=_close)
        bui.containerwidget(edit=cnt, cancel_button=ghost_cancel)

        GlassButton(
            parent=cnt, position=(c_w - 34, c_h - 34), size=(26, 26),
            label='✕', text_scale=0.8, bg_color=(0.18, 0.08, 0.09), opacity=0.35,
            text_color=(0.95, 0.50, 0.50), border=True, border_color=(1.0, 0.40, 0.45),
            border_opacity=0.80, border_thickness=1.2, on_activate_call=_close)
        GlassButton(
            parent=cnt, position=(12, 12), size=(110, 34),
            label='Close', text_scale=0.58,
            bg_color=(0.32, 0.16, 0.18), opacity=0.48,
            border=True, border_color=(1.0, 0.45, 0.48), border_opacity=0.75, border_thickness=1.1,
            on_activate_call=_close)
        GlassButton(
            parent=cnt, position=(130, 12), size=(134, 34),
            label='View GitHub', text_scale=0.56,
            bg_color=(0.12, 0.24, 0.40), opacity=0.58,
            border=True, border_color=(0.45, 0.80, 1.0), border_opacity=0.80, border_thickness=1.1,
            on_activate_call=lambda: bui.open_url(APW_REPO_URL))

        _render_state()
        if not _apw_update_state.get("checked") and not _apw_update_state.get("checking"):
            _recheck()

    def _open_help_window(self) -> None:
        """Clean, user-friendly scrollable guide covering all Party Window features."""
        ol = getattr(self, '_outline_color', (0.4, 1.0, 0.5))
        c_w, c_h = 510, 425
        uiscale = bui.app.ui_v1.uiscale
        cnt = bui.containerwidget(
            size=(c_w, c_h),
            scale=(1.40 if uiscale is babase.UIScale.SMALL else
                   1.14 if uiscale is babase.UIScale.MEDIUM else 1.0),
            transition='in_scale',
            background=False,
            parent=bui.get_special_widget('overlay_stack'))

        _draw_panel_bg(cnt, 0, 0, c_w, c_h, color=(0.05, 0.07, 0.11), opacity=0.97)
        _draw_border(cnt, 0, 0, c_w, c_h, color=ol, opacity=0.86, thickness=1.5)

        bui.textwidget(
            parent=cnt, position=(c_w * 0.5, c_h - 20), size=(0, 0),
            h_align='center', v_align='center',
            text='❓ Party Window — Help & Guide', scale=0.80, color=(1.0, 0.88, 0.35))
        bui.textwidget(
            parent=cnt, position=(c_w * 0.5, c_h - 40), size=(0, 0),
            h_align='center', v_align='center',
            text='Quick reference for every button, tab & customization option',
            scale=0.47, color=(0.68, 0.78, 0.90))

        scroll_x, scroll_y, scroll_w, scroll_h = 10, 52, c_w - 20, c_h - 104
        _draw_panel_bg(cnt, scroll_x, scroll_y, scroll_w, scroll_h, color=(0.02, 0.04, 0.07), opacity=0.72)
        _draw_border(cnt, scroll_x, scroll_y, scroll_w, scroll_h, color=ol, opacity=0.48, thickness=1.1)
        scroll = bui.scrollwidget(
            parent=cnt, position=(scroll_x + 4, scroll_y + 4), size=(scroll_w - 8, scroll_h - 8),
            highlight=False, border_opacity=0.0)
        col = bui.columnwidget(parent=scroll, border=0, margin=4)

        sections = [
            ("💬 Chat, Selection & 4-Word Reply",
             "Tap any message to Translate / Revert, Copy, or Reply (quotes first 4 words).\n"
             "Tap a selected chat again to deselect it, or use ▲ / ▼ / Copy / Reply at bottom-right."),
            ("⚡ Quick Replies, Icons & ⭐ Favourites",
             "Tap Quick for phrases or ➕ Add / Manage Quick Replies to add, delete & reset replies.\n"
             "Tap the Icon button beside Quick for ⭐ Favourites (Slot #1 sets the button icon)."),
            ("🌐 Universal & Romanized Translate",
             "Tap 🌐 next to Reply to toggle whole-chat translation, or translate one chat via tap.\n"
             "Settings -> Translate sets From (left) & Into (right), including Romanized chat."),
            ("✨ Chat Bar Animations & Colors",
             "Settings -> Chat Bar Anim picks Neon Scanner, Synth Equalizer, Pulse Wave, Prism or Off.\n"
             "Settings -> Colors sets Window presets, Sync Outlines toggle, Roster/Nick colors & Colorful Chat."),
            ("👥 Roster Controls & Header Names",
             "🛠️ runs custom commands; Info opens BombSquad's DocUI popup when offered by host;\n"
             "Actions has @ Mention, Mute Chat (unmuting restores hidden chats!), Nick & Complaint.\n"
             "Settings -> Players Under Name shows clickable 3-per-row names below the Party title."),
            ("🛠️ Custom Command Maker ({var})",
             "Create Instant or Draft commands with {cid}, {acc}, {name}, {nick}, {aid}, {me}, {dur} (days).\n"
             "Tap ⓘ inside Command Maker for examples. Reset Defaults restores /kick {cid}."),
            ("👋 Auto Greet, Lists & 📜 Chat Logs",
             "Auto Greet welcomes saved V2/AID friends or replies to greetings. Player Lists manages\n"
             "Muted, Nicks & Greet players. Chat Logs saves dated logs you can view or rename."),
            ("🚀 Updates & Dot Commands",
             "Updates are manual: tap Update in the banner or Settings -> Updates to install.\n"
             "GitHub opens the repo to inspect code. Chat shortcuts: .ip  •  .ping  •  .info  •  .save"),
        ]

        card_w = scroll_w - 24
        for title_s, body_s in sections:
            lines = body_s.split('\n')
            card_h = 30 + len(lines) * 16
            rc = bui.containerwidget(parent=col, size=(card_w, card_h), background=False)
            _draw_panel_bg(rc, 0, 2, card_w, card_h - 4, color=(0.08, 0.12, 0.18), opacity=0.68)
            _draw_border(rc, 0, 2, card_w, card_h - 4, color=ol, opacity=0.35, thickness=1.0)
            bui.textwidget(
                parent=rc, position=(10, card_h - 14), size=(0, 0),
                h_align='left', v_align='center',
                text=title_s, scale=0.56, color=(0.55, 0.96, 1.0), maxwidth=card_w - 20)
            y_ln = card_h - 32
            for ln in lines:
                bui.textwidget(
                    parent=rc, position=(12, y_ln), size=(0, 0),
                    h_align='left', v_align='center',
                    text=ln, scale=0.45, color=(0.86, 0.92, 0.98), maxwidth=card_w - 24)
                y_ln -= 15

        def _close():
            try:
                bui.getsound('swish').play()
            except Exception:
                pass
            bui.containerwidget(edit=cnt, transition='out_scale')

        ghost_cancel = bui.buttonwidget(parent=cnt, position=(-9000, -9000), size=(1, 1), label='', on_activate_call=_close)
        bui.containerwidget(edit=cnt, cancel_button=ghost_cancel)

        GlassButton(
            parent=cnt, position=(c_w - 34, c_h - 34), size=(26, 26),
            label='✕', text_scale=0.8, bg_color=(0.18, 0.08, 0.09), opacity=0.35,
            text_color=(0.95, 0.50, 0.50), border=True, border_color=(1.0, 0.40, 0.45),
            border_opacity=0.80, border_thickness=1.2, on_activate_call=_close)
        GlassButton(
            parent=cnt, position=(c_w * 0.5 - 65, 10), size=(130, 34),
            label='Got It', text_scale=0.66,
            bg_color=(0.14, 0.36, 0.28), opacity=0.55,
            border=True, border_color=ol, border_opacity=0.85, border_thickness=1.2,
            on_activate_call=_close)

    def _open_credits_window(self):
        ol = getattr(self, '_outline_color', (0.4, 1.0, 0.5))
        c_w, c_h = 390, 212
        cnt = bui.containerwidget(
            size=(c_w, c_h),
            transition='in_scale',
            background=False,
            parent=bui.get_special_widget('overlay_stack'))

        _draw_panel_bg(cnt, 0, 0, c_w, c_h, color=(0.05, 0.07, 0.11), opacity=0.95)
        _draw_border(cnt, 0, 0, c_w, c_h, color=ol, opacity=0.85, thickness=1.5)

        bui.textwidget(
            parent=cnt,
            position=(c_w * 0.5, c_h - 32),
            size=(0, 0),
            h_align='center', v_align='center',
            text='Alpha Party Window v1.2',
            scale=0.88,
            color=(1.0, 0.85, 0.30))

        bui.textwidget(
            parent=cnt,
            position=(c_w * 0.5, c_h - 62),
            size=(0, 0),
            h_align='center', v_align='center',
            text='by @chrosticey',
            scale=0.66,
            color=(0.75, 0.90, 1.0))

        _draw_panel_bg(cnt, 18, 58, c_w - 36, 68, color=(0.08, 0.11, 0.16), opacity=0.45)
        _draw_border(cnt, 18, 58, c_w - 36, 68, color=ol, opacity=0.25, thickness=1.0)
        bui.textwidget(
            parent=cnt,
            position=(c_w * 0.5, 102),
            size=(0, 0),
            h_align='center', v_align='center',
            text='Made for late-night lobbies, clean chats,\nand smooth vibes between friends.',
            scale=0.48,
            color=(0.56, 0.62, 0.72),
            maxwidth=c_w - 56)
        bui.textwidget(
            parent=cnt,
            position=(c_w * 0.5, 71),
            size=(0, 0),
            h_align='center', v_align='center',
            text='- chrosticey',
            scale=0.46,
            color=(0.48, 0.54, 0.64))

        def _close():
            bui.getsound('swish').play()
            bui.containerwidget(edit=cnt, transition='out_scale')

        ghost_cancel = bui.buttonwidget(
            parent=cnt, position=(-9000, -9000), size=(1, 1), label='',
            on_activate_call=babase.CallStrict(_close))
        bui.containerwidget(edit=cnt, cancel_button=ghost_cancel)

        GlassButton(
            parent=cnt,
            position=(c_w - 34, c_h - 34),
            size=(26, 26),
            label='✕',
            text_scale=0.8,
            bg_color=(0.18, 0.08, 0.09),
            opacity=0.35,
            text_color=(0.95, 0.50, 0.50),
            border=True,
            border_color=(1.0, 0.40, 0.45),
            border_opacity=0.80,
            border_thickness=1.2,
            on_activate_call=_close)

        GlassButton(
            parent=cnt,
            size=(140, 34),
            position=(c_w * 0.5 - 70, 12),
            label='Back',
            text_scale=0.68,
            bg_color=(0.35, 0.16, 0.18),
            opacity=0.45,
            text_color=(1.0, 0.72, 0.72),
            border=True,
            border_color=(1.0, 0.45, 0.48),
            border_opacity=0.75,
            border_thickness=1.2,
            on_activate_call=_close)


# ba_meta export babase.Plugin
class AlphaPartyWindowPlugin(babase.Plugin):
    def __init__(self):
        try:
            bs.connect_to_party = newconnect_to_party
            bascenev1lib_party.PartyWindow = AlphaPartyWindow
            _install_docui_and_account_theme()
            _apw_sync_muted_set_from_cfg()
            _apw_sync_chatlogger_cfg()
            self._autogreet_timer = babase.AppTimer(2.0, _apw_bg_daemon_tick, repeat=True)
            babase.apptimer(8.0, self._start_update_check)
        except Exception:
            babase.print_exception("[APW] Failed to initialize Alpha Party Window")
            self._self_repair()

    def _start_update_check(self):
        start_new_thread(_apw_check_and_update, ())

    def _self_repair(self):
        if _apw_restore_backup():
            try:
                babase.screenmessage("Alpha Party Window: crash detected, restored backup.", color=(1, 0.8, 0.2))
            except Exception:
                pass
            return

        def _repair_thread():
            ok = _apw_download_update("crash-repair")
            def _notify():
                try:
                    if ok:
                        babase.screenmessage("Alpha Party Window: repaired from GitHub! Restart to apply.", color=(0.2, 1, 0.4))
                    else:
                        babase.screenmessage("Alpha Party Window: repair failed. Check console.", color=(1, 0.3, 0.3))
                except Exception:
                    pass
            try:
                _babase.pushcall(_notify, from_other_thread=True)
            except Exception:
                pass

        start_new_thread(_repair_thread, ())
