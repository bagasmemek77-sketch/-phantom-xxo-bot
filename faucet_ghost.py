#!/usr/bin/env python3
"""
PHANTOM XXO BOT - Perfect Stealth Faucet Claimer
Berjalan di GitHub Actions, laptop mati pun tetap hidup.
Cukup set secrets, dan bot akan klaim recehan tiap jam.

Features:
- Anti-Detection: Free proxy rotation + random User-Agent
- Dynamic faucet loader dari URL eksternal
- Validasi BTC address (P2PKH, P2SH, bech32)
- Persistent failure tracking di JSON
- Claim history logging ke CSV
- Dry-run mode untuk testing
- Auto-disable faucet yang gagal 3x berturut-turut
- Retry otomatis untuk POST method
- Session/cookie management
"""
import os
import json
import time
import random
import requests
import re
import csv
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from urllib.parse import urlencode


def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

# ========== AMBIL KONFIGURASI DARI SECRETS & ENV ==========
BTC_ADDRESS = os.environ.get("CAKE_BTC_ADDR", "").strip()
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
DYNAMIC_FAUCET_URL = os.environ.get("DYNAMIC_FAUCET_URL", "").strip()
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"

# Path faucet_list.json (otomatis menyesuaikan)
WORKSPACE = os.environ.get("GITHUB_WORKSPACE", "/workspaces/-phantom-xxo-bot")
FAUCET_LIST_PATH = os.path.join(WORKSPACE, "faucet_list.json")
FAILURE_STATE_PATH = os.path.join(WORKSPACE, "faucet_failure_state.json")
CLAIM_HISTORY_PATH = os.path.join(WORKSPACE, "claim_history.csv")

# ========== ANTI-DETECTION: USER-AGENTS ==========
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/123.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 OPR/108.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (Android 14; Mobile; rv:122.0) Gecko/122.0 Firefox/122.0",
    "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Vivaldi/6.6.3281.65",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (iPad; CPU OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 EdgHTML/123.0.2420.97",
]

# ========== ANTI-DETECTION: FREE PROXY FETCHER ==========
def fetch_free_proxies() -> List[str]:
    """Fetch free proxy list dari GitHub repo atau fallback."""
    proxy_sources = [
        "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-by-protocol.txt",
        "https://raw.githubusercontent.com/hezhao/proxylist/master/proxy-list.txt",
    ]

    proxies = []
    for source in proxy_sources:
        try:
            log(f"🌐 Fetching proxies dari {source}...")
            resp = requests.get(source, timeout=10)
            if resp.status_code == 200:
                lines = resp.text.split('\n')
                for line in lines:
                    line = line.strip()
                    # Parse "ip:port" format
                    if line and ':' in line and not line.startswith('#'):
                        try:
                            parts = line.split(':')
                            if len(parts) >= 2:
                                ip, port = parts[0], parts[1]
                                if ip and port.isdigit():
                                    proxies.append(f"http://{ip}:{port}")
                        except:
                            pass

                if proxies:
                    log(f"✅ Loaded {len(proxies)} free proxies")
                    return proxies
        except Exception as e:
            log(f"⚠️ Proxy source failed: {e}")

    log("⚠️ Tidak bisa load proxy, lanjut tanpa proxy...")
    return []

# ========== SESSION & COOKIES ==========
class SessionManager:
    """Manage sessions dan cookies untuk realism."""
    def __init__(self):
        self.sessions: Dict[str, requests.Session] = {}
        self.proxies = fetch_free_proxies()

    def get_session(self, faucet_name: str) -> requests.Session:
        """Get atau create session untuk faucet."""
        if faucet_name not in self.sessions:
            session = requests.Session()
            session.headers.update({"User-Agent": random.choice(USER_AGENTS)})

            # Pakai random proxy (jika available)
            if self.proxies:
                proxy = random.choice(self.proxies)
                session.proxies = {
                    "http": proxy,
                    "https": proxy,
                }

            self.sessions[faucet_name] = session

        # Random User-Agent setiap request
        self.sessions[faucet_name].headers.update(
            {"User-Agent": random.choice(USER_AGENTS)}
        )
        return self.sessions[faucet_name]

    def clear_session(self, faucet_name: str):
        """Clear session untuk faucet."""
        if faucet_name in self.sessions:
            self.sessions[faucet_name].close()
            del self.sessions[faucet_name]

session_manager = None  # Will be initialized in main()

# ========== VALIDASI ==========
def validate_btc_address(addr: str) -> bool:
    """Validasi format alamat BTC (P2PKH, P2SH, bech32)."""
    if not addr or len(addr) < 26:
        return False
    # Pattern untuk BTC address
    patterns = [
        r"^1[a-zA-Z0-9]{25,34}$",     # P2PKH (1...)
        r"^3[a-zA-Z0-9]{25,34}$",     # P2SH (3...)
        r"^bc1[a-z0-9]{39,59}$",      # bech32 (bc1...)
    ]
    return any(re.match(pattern, addr) for pattern in patterns)

# ========== FUNGSI PEMBANTU ==========
def log_claim(faucet_name: str, method: str, status: str, error_msg: str = ""):
    """Log claim attempt ke CSV."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        btc_hint = BTC_ADDRESS[:10] + "..." if BTC_ADDRESS else "UNKNOWN"

        # Append ke CSV
        with open(CLAIM_HISTORY_PATH, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, faucet_name, method, status, error_msg, btc_hint])

        log(f"  📝 Logged: {faucet_name} → {status}")
    except Exception as e:
        log(f"  ⚠️ CSV logging error: {e}")

def load_failure_state() -> Dict[str, int]:
    """Load persistent failure state dari JSON."""
    try:
        if os.path.exists(FAILURE_STATE_PATH):
            with open(FAILURE_STATE_PATH, "r") as f:
                data = json.load(f)
                return data.get("failure_tracking", {})
    except Exception as e:
        log(f"⚠️ Load failure state error: {e}")
    return {}

def save_failure_state(failures: Dict[str, int]):
    """Save persistent failure state ke JSON."""
    try:
        state = {
            "failure_tracking": failures,
            "last_updated": datetime.now().isoformat() + "Z",
            "version": 1
        }
        with open(FAILURE_STATE_PATH, "w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        log(f"⚠️ Save failure state error: {e}")

def send_telegram(msg: str):
    """Kirim laporan ke Telegram jika token tersedia."""
    if not (TELEGRAM_TOKEN and TELEGRAM_CHAT_ID):
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"},
            timeout=10
        )
    except Exception as e:
        log(f"⚠️ Gagal kirim Telegram: {e}")

def load_faucet_list() -> Tuple[List[Dict], List[Dict]]:
    """Muat faucet_list.json, kembalikan (semua_faucet, faucet_enabled)."""
    try:
        if not os.path.exists(FAUCET_LIST_PATH):
            log("❌ faucet_list.json tidak ditemukan!")
            fallback = [{
                "name": "FreeBitco.in (fallback)",
                "method": "post",
                "url": "https://freebitco.in/cgi-bin/freebitco.pl",
                "data": {"op": "r", "addr": "___ADDR___"},
                "enabled": True
            }]
            return fallback, fallback

        with open(FAUCET_LIST_PATH, "r") as f:
            faucets = json.load(f)

        for f in faucets:
            if not all(k in f for k in ["name", "method", "url", "data"]):
                log(f"⚠️ Faucet '{f.get('name', 'Unknown')}' struktur tidak valid, disable.")
                f["enabled"] = False

        enabled = [f for f in faucets if f.get("enabled", True)]
        log(f"📋 {len(enabled)}/{len(faucets)} faucet(s) dimuat.")
        return faucets, enabled

    except json.JSONDecodeError as e:
        log(f"❌ JSON parsing error: {e}")
        return [], []
    except Exception as e:
        log(f"❌ Error load faucet list: {e}")
        return [], []

def fetch_dynamic_faucets() -> Optional[List[Dict]]:
    """Fetch daftar faucet terbaru dari URL eksternal."""
    if not DYNAMIC_FAUCET_URL:
        return None

    try:
        log(f"🌐 Fetch dynamic faucets dari external URL...")
        resp = requests.get(DYNAMIC_FAUCET_URL, timeout=15)
        resp.raise_for_status()
        faucets = resp.json()

        if not isinstance(faucets, list):
            log("⚠️ Dynamic faucet URL harus mengembalikan array JSON!")
            return None

        log(f"✅ Loaded {len(faucets)} faucets dari external URL")
        return faucets

    except Exception as e:
        log(f"⚠️ Gagal fetch dynamic faucets: {e}")
        return None

def merge_faucets(local_faucets: List[Dict], dynamic_faucets: List[Dict]) -> List[Dict]:
    """Merge local faucets dengan dynamic faucets, deduplicate by URL."""
    faucet_map = {f["url"]: f for f in local_faucets}

    for f in dynamic_faucets:
        if "url" not in f:
            continue
        if f["url"] not in faucet_map:
            f["enabled"] = f.get("enabled", True)
            faucet_map[f["url"]] = f
            log(f"  ✨ Faucet baru: {f.get('name', 'Unknown')}")

    merged = list(faucet_map.values())
    log(f"📊 Total faucets setelah merge: {len(merged)}")
    return merged

def save_faucet_list(faucets: List[Dict]):
    """Simpan faucet list ke file JSON."""
    try:
        with open(FAUCET_LIST_PATH, "w") as f:
            json.dump(faucets, f, indent=2)
        log(f"💾 Faucet list disimpan ({len(faucets)} items)")
    except Exception as e:
        log(f"❌ Gagal simpan faucet list: {e}")

def record_faucet_failure(failure_state: Dict[str, int], faucet_name: str) -> bool:
    """Catat kegagalan faucet. Return True jika perlu di-disable (3x gagal)."""
    if faucet_name not in failure_state:
        failure_state[faucet_name] = 0
    failure_state[faucet_name] += 1

    if failure_state[faucet_name] >= 3:
        log(f"⚠️ {faucet_name} gagal 3x, marking untuk auto-disable.")
        return True
    return False

def reset_faucet_failure(failure_state: Dict[str, int], faucet_name: str):
    """Reset failure counter jika faucet berhasil."""
    if faucet_name in failure_state:
        failure_state[faucet_name] = 0

def validate_btc_address(addr: str) -> bool:
    """Validasi format alamat BTC (P2PKH, P2SH, bech32)."""
    if not addr or len(addr) < 26:
        return False
    patterns = [
        r"^1[a-zA-Z0-9]{25,34}$",     # P2PKH (1...)
        r"^3[a-zA-Z0-9]{25,34}$",     # P2SH (3...)
        r"^bc1[a-z0-9]{39,59}$",      # bech32 (bc1...)
    ]
    return any(re.match(pattern, addr) for pattern in patterns)

def claim_via_post(faucet: Dict, retry: int = 0) -> Tuple[bool, str]:
    """Klaim faucet metode POST dengan retry otomatis + anti-detection."""
    max_retries = 1

    if DRY_RUN:
        log(f"  🏃 DRY-RUN: Simulasi POST ke {faucet['url']}")
        return True, ""

    try:
        url = faucet["url"]
        data = {}

        # Replace placeholder dengan alamat BTC
        for key, value in faucet["data"].items():
            if value == "___ADDR___":
                data[key] = BTC_ADDRESS
            else:
                data[key] = value

        # Get sesion dengan proxy & random UA
        session = session_manager.get_session(faucet["name"])

        log(f"  🌐 POST ke {url[:50]}...")
        resp = session.post(url, data=data, timeout=15)

        if resp.status_code == 200:
            text = resp.text.lower()
            # Check success keywords
            if any(k in text for k in ["success", "congratulations", "reward", "you have", "claimed", "sent", "confirmed"]):
                return True, ""

        # Retry jika belum berhasil & belum exceed max retries
        if retry < max_retries:
            delay = random.randint(5, 10)
            log(f"  🔄 Retry #{retry + 1} dalam {delay}s...")
            time.sleep(delay)
            return claim_via_post(faucet, retry + 1)

        return False, f"No success in response"

    except Exception as e:
        error_msg = str(e)
        log(f"  ⚠️ POST error: {error_msg}")
        if retry < max_retries:
            delay = random.randint(5, 10)
            log(f"  🔄 Retry #{retry + 1} dalam {delay}s...")
            time.sleep(delay)
            return claim_via_post(faucet, retry + 1)
        return False, error_msg

def claim_via_browser(faucet: Dict) -> Tuple[bool, str]:
    """Klaim faucet yang butuh browser headless dengan Playwright + anti-detection."""
    if DRY_RUN:
        log(f"  🏃 DRY-RUN: Simulasi browser ke {faucet['url']}")
        return True, ""

    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

        with sync_playwright() as p:
            # Launch dengan args untuk anti-detection
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-gpu",
                    "--disable-web-resources",
                    "--disable-dev-shm-usage"
                ]
            )
            page = browser.new_page(
                user_agent=random.choice(USER_AGENTS),
                viewport={"width": random.randint(1024, 1920), "height": random.randint(768, 1080)},
            )

            try:
                log(f"  🌐 Navigate ke {faucet['url'][:50]}...")
                page.goto(faucet["url"], timeout=20000, wait_until="domcontentloaded")

                # Isi alamat dengan berbagai selector
                address_selectors = [
                    'input[name="addr"]',
                    'input[name="address"]',
                    'input[name="btc_address"]',
                    'input[name="wallet"]',
                    'input[type="text"]'
                ]

                for selector in address_selectors:
                    try:
                        page.fill(selector, BTC_ADDRESS)
                        log(f"  ✍️ Address filled via: {selector}")
                        break
                    except:
                        pass

                # Klik tombol klaim dengan berbagai variasi
                button_patterns = [
                    'button:has-text("Roll")',
                    'button:has-text("Claim")',
                    'button:has-text("Get")',
                    'button:has-text("Submit")',
                    'button:has-text("Collect")',
                    'button:has-text("OK")',
                    '[role="button"]:has-text("Roll")',
                    'input[type="submit"]'
                ]

                clicked = False
                for pattern in button_patterns:
                    try:
                        page.click(pattern, timeout=5000)
                        log(f"  🖱️ Button clicked: {pattern}")
                        clicked = True
                        break
                    except:
                        pass

                if clicked:
                    page.wait_for_timeout(5000)
                    return True, ""
                else:
                    return False, "Cannot find claim button"

            except PlaywrightTimeout:
                return False, "Browser timeout"
            finally:
                browser.close()

    except ImportError:
        return False, "Playwright not installed"
    except Exception as e:
        return False, str(e)

# ========== EKSEKUSI UTAMA ==========
def main():
    global session_manager
    session_manager = SessionManager()
    
    log("💀 Phantom XXO Ghost - START")

    if DRY_RUN:
        log("🏃 DRY-RUN MODE - Tidak akan klaim sebenarnya!")

    # 1. Validasi BTC Address
    if not validate_btc_address(BTC_ADDRESS):
        msg = f"❌ *ERROR*: BTC Address format tidak valid!\nAlamat: {BTC_ADDRESS[:15]}... (tidak sesuai P2PKH/P2SH/bech32)"
        log(msg)
        send_telegram(msg)
        return

    log(f"✅ BTC Address valid: {BTC_ADDRESS[:10]}...")
    log(f"🔧 Proxy enabled: {len(session_manager.proxies)} proxies loaded")

    # 2. Load persistent failure state
    failure_state = load_failure_state()
    log(f"📊 Loaded failure state: {len(failure_state)} tracked faucets")

    # 3. Load faucet list
    all_faucets, enabled_faucets = load_faucet_list()

    if not all_faucets:
        log("❌ Tidak ada faucet ditemukan.")
        send_telegram("❌ Tidak ada faucet tersedia di faucet_list.json")
        return

    # 4. Fetch dynamic faucets dan merge
    if DYNAMIC_FAUCET_URL:
        dynamic = fetch_dynamic_faucets()
        if dynamic:
            all_faucets = merge_faucets(all_faucets, dynamic)
            enabled_faucets = [f for f in all_faucets if f.get("enabled", True)]
            save_faucet_list(all_faucets)

    if not enabled_faucets:
        log("❌ Semua faucet disabled.")
        send_telegram("⚠️ Semua faucet sudah disabled. Mungkin terlalu banyak gagal?")
        return

    success = 0
    fail = 0
    dry_run_count = 0
    report = []

    for idx, faucet in enumerate(enabled_faucets, 1):
        log(f"\n[{idx}/{len(enabled_faucets)}] Mencoba {faucet['name']}...")

        try:
            method = faucet.get("method", "post")
            result, error_msg = claim_via_browser(faucet) if method == "browser" else claim_via_post(faucet)

            status = "SUCCESS" if result else "FAIL"
            if DRY_RUN:
                status = "DRY_RUN"
                dry_run_count += 1

            log_claim(faucet['name'], method, status, error_msg)

            if result:
                log("  ✅ SUKSES")
                success += 1
                report.append(f"✅ {faucet['name']}")
                reset_faucet_failure(failure_state, faucet['name'])
            else:
                log(f"  ❌ GAGAL: {error_msg}")
                fail += 1
                report.append(f"❌ {faucet['name']}")

                # Check if need to disable (3x gagal)
                should_disable = record_faucet_failure(failure_state, faucet['name'])
                if should_disable:
                    faucet["enabled"] = False
                    log(f"  🔴 Auto-disabled: {faucet['name']}")
                    report.append(f"🔴 {faucet['name']} (disabled)")

                # Save failure state
                save_failure_state(failure_state)
                save_faucet_list(all_faucets)

        except Exception as e:
            error_msg = str(e)
            log(f"  ❌ ERROR: {error_msg}")
            log_claim(faucet['name'], method, "ERROR", error_msg)
            fail += 1
            report.append(f"❌ {faucet['name']} (error)")

        # Jeda acak 30-120 detik antar faucet (ANTI-DETECTION)
        if idx < len(enabled_faucets):
            sleep_time = random.randint(30, 120)
            log(f"⏳ Tunggu {sleep_time}s sebelum faucet berikutnya... (anti-detection)")
            time.sleep(sleep_time)

    # 5. Simpan final state dan generate report
    save_failure_state(failure_state)

    # 6. Ringkasan & Laporan
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    success_rate = f"{(success / len(enabled_faucets) * 100):.0f}%" if enabled_faucets else "N/A"

    mode_info = "🏃 [DRY-RUN]" if DRY_RUN else "⚙️ [LIVE]"
    summary = f"""🤖 *LAPORAN PHANTOM XXO* {mode_info}
🕐 {now}
📊 Total Faucet: {len(enabled_faucets)} (enabled)
✅ Sukses: {success}
❌ Gagal: {fail}
🏃 Dry-run: {dry_run_count}
📈 Success Rate: {success_rate}
📝 CSV Log: {CLAIM_HISTORY_PATH}
💾 Failure State: saved
━━━━━━━━━━━━━━━━━━━━━━
🔹 {' | '.join(report[:5])}{'...' if len(report) > 5 else ''}"""

    log(summary)
    send_telegram(summary)
    log(f"🎭 Selesai, failure state disimpan, CSV updated...\n")

if __name__ == "__main__":
    main()
