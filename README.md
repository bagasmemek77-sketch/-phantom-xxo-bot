# -phantom-xxo-bot 👻

**Phantom XXO Ghost Bot** — Crypto Faucet Claimer Otomatis yang jalan di GitHub Actions 24/7 dengan **Anti-Detection & Persistent Tracking**

## 🚀 Fitur Utama

### ⚙️ **Core Features**
✅ **Otomatis setiap jam** - Cron schedule `0 * * * *` (tiap jam)  
✅ **Bekerja di GitHub Actions** - Laptop mati pun tetap jalan  
✅ **Multi-method support** - POST requests & headless browser (Playwright)  
✅ **Dynamic Faucet Loader** - Fetch daftar faucet dari URL eksternal  

### 🛡️ **Anti-Detection System** (NEW!)
✅ **Free Proxy Rotation** - Fetch & rotate from GitHub proxy lists (no paid proxies)  
✅ **Random User-Agent** - 20+ browser fingerprints (Chrome, Firefox, Edge, Safari)  
✅ **Smart Delays** - Random 30-120s antar faucet (bukan fixed 30-90s)  
✅ **Session Management** - Cookies & session persistence per faucet  
✅ **Browser Fingerprinting** - Random viewport size & anti-bot evasion  

### 📊 **Persistent Tracking** (NEW!)
✅ **Failure State JSON** - `faucet_failure_state.json` menyimpan failure count antar runs  
✅ **Claim History CSV** - `claim_history.csv` track semua klaim dengan timestamp  
✅ **Auto-disable Logic** - Faucet gagal 3x → auto-disable dan persistent di JSON  
✅ **Auto Git Commit** - CSV & failure state di-push otomatis ke repo  

### 🧪 **Developer Features** (NEW!)
✅ **DRY-RUN Mode** - Test tanpa klaim sebenarnya, lalu lihat di CSV  
✅ **CSV Analytics** - Export claim history untuk analysis & debugging  
✅ **Smart Validation** - BTC address format validation (P2PKH, P2SH, bech32)  
✅ **Comprehensive Logging** - Semua event dengan timestamp & emoji  

### 🔄 **Reliability**
✅ **Retry Logic** - POST gagal → coba 2x (max) dengan jeda random  
✅ **Error Handling** - Try-catch di setiap fungsi + error logging  
✅ **Telegram Reports** - Laporan sukses/fail dikirim via Bot Telegram  
✅ **JSON Fallback** - Jika file tidak ada, punya default data  

---

## 🛠️ Setup

### 1. GitHub Secrets (Required)
Set di repository settings → Secrets and variables → Actions:

- **`CAKE_BTC_ADDR`** → Alamat wallet BTC (format: 1xyz..., 3xyz..., atau bc1xyz...)
- **`TELEGRAM_BOT_TOKEN`** → Token dari @BotFather di Telegram *(optional)*
- **`TELEGRAM_CHAT_ID`** → Chat ID untuk laporan Telegram *(optional)*

### 2. GitHub Secrets (Optional - Untuk Advanced Features)

- **`DYNAMIC_FAUCET_URL`** → URL ke JSON array daftar faucet eksternal (auto-fetch & merge)
- **`DRY_RUN`** → Set ke `true` untuk test mode (tidak klaim sebenarnya)

Contoh nilai:

- `DRY_RUN`: `true` atau `false` (string). Contoh: `true`
- `DYNAMIC_FAUCET_URL`: `https://example.com/faucets.json` (harus mengembalikan array JSON dengan format yang sama seperti `faucet_list.json`)

### 3. File Struktur
```
.
├── faucet_ghost.py              (Bot utama - 580 lines)
├── faucet_list.json             (11 faucets - expanding dynamically)
├── claim_history.csv            (Track semua klaim - auto-populated)
├── faucet_failure_state.json    (Persistent failure count - auto-synced)
├── README.md                    (Dokumentasi)
└── .github/workflows/
    └── bot-runner.yml           (Workflow - jalankan tiap jam)
```

---

## 📋 Format faucet_list.json

```json
[
  {
    "name": "FreeBitco.in",
    "method": "post",
    "url": "https://freebitco.in/cgi-bin/freebitco.pl",
    "data": {
      "op": "r",
      "addr": "___ADDR___"
    },
    "enabled": true
  },
  {
    "name": "Moon Bitcoin",
    "method": "browser",
    "url": "https://moonbitcoin.org",
    "data": {},
    "enabled": true
  }
]
```

**Field yang dimaksud:**
- `name` - Nama faucet (untuk laporan & CSV)
- `method` - `"post"` (HTTP POST) atau `"browser"` (Playwright headless)
- `url` - URL faucet
- `data` - Form data untuk POST (gunakan `___ADDR___` sebagai placeholder BTC address)
- `enabled` - `true`/`false` (auto-disable jika gagal 3x, di-save ke JSON)

---

## 🔐 Anti-Detection System

**Bagaimana bot menghindari detection & blocking:**

### 1. **Free Proxy Rotation** 🌐
```python
- Fetch dari GitHub repo publik (gratis, no paid API required)
- Random proxy setiap session per faucet
- Fallback ke direct connection jika proxy gagal
```

### 2. **User-Agent Spoofing** 🖥️
```python
- 20+ realistic User-Agent strings
- Random browser setiap request (Chrome, Firefox, Edge, Safari)
- Desktop & mobile variants
```

### 3. **Smart Delays** ⏱️
```python
- Random 30-120 detik antar faucet (bukan fixed timing yg suspicious)
- Jeda random 5-10s pada retry
- Prevent rate-limiting
```

### 4. **Session Management** 🍪
```python
- Per-faucet sessions dengan cookies
- Random viewport size (1024-1920 x 768-1080)
- Browser fingerprinting evasion
```

---

## 📊 Persistent Failure Tracking

**Bagaimana bot track & persist failure counts:**

### 1. **faucet_failure_state.json**
```json
{
  "failure_tracking": {
    "FreeBitco.in": 1,
    "FreeDoge.co.in": 0,
    "CoinFaucet.io": 3
  },
  "last_updated": "2026-05-08T14:30:00Z",
  "version": 1
}
```

### 2. **Auto-disable Logic**
- Faucet gagal 1x → Catat di JSON
- Faucet gagal 2x → Masih dicoba
- **Faucet gagal 3x → Auto-disable** (set `"enabled": false` di `faucet_list.json`)
- Faucet sukses → Reset counter ke 0

### 3 **Auto Git Commit**
Setelah bot selesai, workflow otomatis:
```
1. Update claim_history.csv
2. Update faucet_failure_state.json
3. Update faucet_list.json (jika ada auto-disable)
4. Git commit & push ke main
```

---

## 📝 Claim History CSV

**File: `claim_history.csv`**

Struktur:
```
timestamp,faucet_name,method,status,error_message,wallet_address_hint
2026-05-08 14:30:00,FreeBitco.in,post,SUCCESS,,1abc...xyz
2026-05-08 14:31:30,FreeDoge.co.in,post,FAIL,No success in response,1abc...xyz
2026-05-08 14:33:00,CoinFaucet.io,browser,SUCCESS,,1abc...xyz
2026-05-08 14:35:00,FreeBitco.in,post,DRY_RUN,,1abc...xyz
```

**Kolom:**
- `timestamp` - Waktu claim attempt
- `faucet_name` - Nama faucet
- `method` - POST atau browser
- `status` - SUCCESS, FAIL, ERROR, atau DRY_RUN
- `error_message` - Detail error (jika gagal)
- `wallet_address_hint` - First 10 chars BTC address (untuk tracking)

**Gunakan untuk:**
- Track total earnings per faucet
- Hitung success rate
- Debug issues
- Analytics & reporting

---

## 🧪 DRY-RUN Mode

**Test bot tanpa klaim sebenarnya:**

### Setup
Set secret `DRY_RUN` ke `true`:
```
CAKE_BTC_ADDR: 1A1z7agoat...
DRY_RUN: true
```

### Behavior
- Bot akan:
  ✅ Load faucet list
  ✅ Validate BTC address
  ✅ Simulate POST/browser tanpa beneran kirim
  ✅ Log "DRY_RUN" ke CSV
  ✅ Send Telegram report dengan [DRY-RUN] label

### Output di CSV
```
2026-05-08 14:30:00,FreeBitco.in,post,DRY_RUN,,1abc...xyz
```

---

## 🔄 Dynamic Faucet Loader

**Bot bisa fetch daftar faucet dari URL eksternal & auto-merge:**

### Setup
1. Siapkan URL yang return JSON array (format sama seperti `faucet_list.json`)
2. Set secret `DYNAMIC_FAUCET_URL`:
   ```
   DYNAMIC_FAUCET_URL: https://yourserver.com/faucets.json
   ```

### Behavior
Bot akan:
1. Fetch dari URL tersebut
2. Merge dengan `faucet_list.json` (deduplicate by URL)
3. Auto-enable faucet baru
4. Simpan perubahan ke repo

### Contoh External JSON
```json
[
  {
    "name": "NewFaucet.io",
    "method": "post",
    "url": "https://newfaucet.io/claim",
    "data": {"wallet": "___ADDR___"},
    "enabled": true
  }
]
```

---

## ⚙️ Validasi BTC Address

Bot hanya berjalan jika BTC address format valid:

- ✅ **P2PKH**: `1` + 25-34 karakter (e.g. `1A1z7agoat...`)
- ✅ **P2SH**: `3` + 25-34 karakter (e.g. `3J98t1WpE...`)
- ✅ **bech32**: `bc1` + 39-59 lowercase alphanumeric (e.g. `bc1qw508d6...`)

---

## 📊 Laporan Telegram

Jika `TELEGRAM_BOT_TOKEN` & `TELEGRAM_CHAT_ID` diset:

```
🤖 LAPORAN PHANTOM XXO ⚙️ [LIVE]
🕐 2026-05-08 14:30:00
📊 Total Faucet: 10 (enabled)
✅ Sukses: 7
❌ Gagal: 2
🏃 Dry-run: 0
📈 Success Rate: 70%
📝 CSV Log: .../claim_history.csv
💾 Failure State: saved
━━━━━━━━━━━━━━━━━━━━━━
🔹 ✅ FreeBitco.in | ✅ FreeDoge | ❌ CoinFaucet | ✅ BitcoinZ | 🔴 AutoFaucet (disabled)...
```

---

## 🐛 Troubleshooting

| Masalah | Solusi |
|--------|--------|
| Bot tidak jalan | Cek `CAKE_BTC_ADDR` di Secrets, pastikan format BTC valid |
| Proxy error | Bot fallback ke direct connection, normal |
| "Playwright belum diinstall" | Cek `.github/workflows/bot-runner.yml` → `playwright install --with-deps chromium` |
| Faucet selalu gagal | URL berubah / faucet tutup, update di `faucet_list.json` |
| Tidak dapat laporan Telegram | Cek `TELEGRAM_BOT_TOKEN` & `TELEGRAM_CHAT_ID` di Secrets |
| JSON parsing error | Validate JSON dengan online JSON validator |
| CSV tidak terupdate | Cek Git credentials & permissions di workflow |
| Proxy list unavailable | Bot akan jalan tanpa proxy (pakai direct connection) |

---

## 📊 Contoh Output

```
[14:30:00] 💀 Phantom XXO Ghost - START
[14:30:00] 🏃 DRY-RUN MODE - Tidak akan klaim sebenarnya!
[14:30:01] ✅ BTC Address valid: 1A1z7ago...
[14:30:02] 🔧 Proxy enabled: 45 proxies loaded
[14:30:03] 📊 Loaded failure state: 3 tracked faucets
[14:30:04] 📋 10/10 faucet(s) dimuat.
[14:30:05] 🌐 Fetch dynamic faucets dari external URL...
[14:30:06] ✅ Loaded 2 faucets dari external URL
[14:30:07] 📊 Total faucets setelah merge: 12
[14:30:08]
[14:30:08] [1/12] Mencoba FreeBitco.in...
[14:30:09]   🏃 DRY-RUN: Simulasi POST ke https://freebitco.in/cgi-bin/freebitco.pl
[14:30:09]   📝 Logged: FreeBitco.in → DRY_RUN
[14:30:09]   ✅ SUKSES
[14:30:09] ⏳ Tunggu 45s sebelum faucet berikutnya... (anti-detection)

[14:30:54] [2/12] Mencoba FreeDoge.co.in...
...
[15:00:00] 🤖 LAPORAN PHANTOM XXO ⚙️ [LIVE]
[15:00:00] 🕐 2026-05-08 15:00:00
[15:00:00] 📊 Total Faucet: 12 (enabled)
[15:00:00] ✅ Sukses: 9
[15:00:00] ❌ Gagal: 3
[15:00:00] 🏃 Dry-run: 0
[15:00:00] 📈 Success Rate: 75%
[15:00:00] 📝 CSV Log: .../claim_history.csv
[15:00:00] 💾 Failure State: saved
[15:00:00] 🎭 Selesai, failure state disimpan, CSV updated...
```

---

## 📈 Analytics dari CSV

**Bisa track:**
- Total earnings per faucet (multiplied by BTC rate)
- Success rate per faucet (success / total attempts)
- Average failures sebelum disable
- Peak hours untuk klaim
- Error patterns & root causes

---

## 🔐 Security Notes

- 🔒 BTC address di-mask di logs (hanya first 10 chars ditampilkan)
- 🔒 Secrets tidak pernah di-log atau di-commit
- 🔒 Proxy list di-fetch dari publik GitHub repos (no server dependency)
- 🔒 Keine paid API keys required
- 🔒 GitHub Actions logs available hanya ke repo owner

---

## 🚀 Production Checklist

- [x] Anti-detection system implemented
- [x] Persistent failure tracking
- [x] CSV claim history
- [x] DRY-run mode untuk testing
- [x] Dynamic faucet loader
- [x] Auto-disable after 3 failures
- [x] Telegram notifications
- [x] Error handling comprehensive
- [x] Git auto-commit & push
- [x] 11 faucets sudah di-add

**Status: PRODUCTION READY ✅**

---

## 💡 Tips & Tricks

1. **Maximize Earnings:**
   - Add lebih banyak faucets via `faucet_list.json`
   - Use `DYNAMIC_FAUCET_URL` untuk auto-expand
   - Monitor CSV untuk faucet terbaik

2. **Avoid Bans:**
   - Delays sudah random (30-120s)
   - Proxy rotation built-in
   - User-Agent spoofing active
   - Session management per faucet

3. **Debug Issues:**
   - Check CSV untuk error patterns
   - Check failure state JSON untuk tracked faucets
   - Run dengan `DRY_RUN: true` untuk test tanpa risk

4. **Monitor Success:**
   - Telegram reports setiap jam
   - CSV file untuk detailed analytics
   - GitHub Commits show history

---

## 📝 Lisensi

Made with 👻 by Script Kiddie yang jadi Developer

**Tested & Proven** ✅  
**Anti-Detection Enabled** 🛡️  
**Production Grade** 🚀

**XXO! Hantu tidak tersentuh selalu hidup!** 👻