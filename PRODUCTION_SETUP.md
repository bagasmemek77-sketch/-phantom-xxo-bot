# ✅ PHANTOM XXO BOT - PRODUCTION SETUP GUIDE

**Status:** 🟢 BOT READY FOR PRODUCTION  
**Last Updated:** 2026-05-08  
**Admin Email:** bagasmemek77@gmail.com

---

## 🚀 QUICK START (3 Steps)

### Step 1: Set GitHub Secret with BTC Address
```
Repository Settings → Secrets and variables → Actions → New repository secret
Name: CAKE_BTC_ADDR
Value: YOUR_BTC_WALLET_ADDRESS
```

**Valid BTC Address Formats:**
- ✅ `1XxxxxxxxxxxxxxxxxxxxxxxxxxxxxXXX` (P2PKH, starts with 1)
- ✅ `3XxxxxxxxxxxxxxxxxxxxxxxxxxxxxXXX` (P2SH, starts with 3)  
- ✅ `bc1xxxxxxxxxxxxxxxxxxxxxxxxxxx` (Bech32, starts with bc1)

**Test If Valid:**
```bash
# P2PKH example (starts with 1)
echo "1KuSaLGfBKaXXBLjvJYW7t7Q5cSSCu9Qjx"

# P2SH example (starts with 3)
echo "3J98t1WpEZ73CNmYviecrnyiWrnqRhWNLy"

# Bech32 example (starts with bc1)
echo "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq"
```

### Step 2: (Optional) Set Telegram Notifications
```
Name: TELEGRAM_BOT_TOKEN
Value: YOUR_BOT_TOKEN_FROM_TELEGRAM

Name: TELEGRAM_CHAT_ID
Value: YOUR_CHAT_ID
```

### Step 3: Trigger Workflow Manually or Wait for Cron
- **Manual:** Go to Actions → Run workflow → "🚀 Phantom XXO Auto Claim" → Run  
- **Automatic:** Bot runs **every hour** (0 * * * * cron)

---

## 📋 PRODUCTION CHECKLIST

- [ ] CAKE_BTC_ADDR secret set with VALID BTC address (not test address)
- [ ] Verified BTC address format (starts with 1, 3, or bc1)
- [ ] DRY_RUN secret **NOT SET** or set to `false` (production mode active)
- [ ] Workflow triggered or waiting for hourly cron
- [ ] Check GitHub Actions log for "✅ SUCCESS" status
- [ ] CSV file updated: `claim_history.csv`
- [ ] Failure state tracked: `faucet_failure_state.json`

---

## 🔔 ADMIN NOTIFICATIONS

Bot sends automatic notifications if:

1. **BTC Address Invalid** → Email to bagasmemek77@gmail.com
   - Problem: Invalid BTC address format
   - Action: Update GitHub secret CAKE_BTC_ADDR

2. **Critical Code Error** → Email to bagasmemek77@gmail.com  
   - Problem: Unhandled exception in bot code
   - Action: Review error details, may need code fix
   - File: `phantom_error_notification.json`

**How to Check Email Notifications:**
- GitHub Actions log has error details
- Check `phantom_error_notification.json` in repo
- Error appears in workflow step "👻 Jalankan Bot"

---

## 📊 MONITORING

### View Real-Time Logs
1. Go to GitHub → Actions → Workflow runs
2. Click latest run → Step "👻 Jalankan Bot"
3. Check for:
   - `✅ SUCCESS` - Faucet claimed successfully
   - `❌ FAIL` - Faucet claimed but failed
   - `🏃 DRY-RUN` - Test mode (no actual claim)

### View Claims History
```bash
# CSV file with all claim attempts
less claim_history.csv

# Format: timestamp,faucet_name,method,status,error_message,wallet_address_hint
```

### View Failure State
```bash
# JSON file with faucet failure tracking
cat faucet_failure_state.json

# Faucet auto-disables after 3 failures
```

---

## 🔧 ADVANCED SETTINGS

### Enable Dynamic Faucet Loader
```
Secret Name: DYNAMIC_FAUCET_URL
Value: https://example.com/faucets.json
```
Bot will merge faucets from external JSON source.

### Premium Mode (Not Available Yet)
- CAPTCHA solver integration
- Multi-currency support (BTC, ETH, DOGE, BNB)
- Discord/Slack notifications
- Database logging

---

## ⚠️ TROUBLESHOOTING

### Problem: "BTC Address format tidak valid"
**Solution:** 
- Verify address starts with 1, 3, or bc1
- Check length (25-35 chars for P2PKH/P2SH, 42-62 for bech32)
- Make sure no spaces or extra chars
- Example valid: `1KuSaLGfBKaXXBLjvJYW7t7Q5cSSCu9Qjx`

### Problem: "Semua faucet disabled"  
**Solution:**
- Faucets auto-disable after 3 consecutive failures
- Reset failure state: Edit `faucet_failure_state.json` 
- Or update faucet URLs in `faucet_list.json`

### Problem: "Tidak bisa load proxy"
**Solution:** (Normal - bot has fallback)
- Bot tries to load free proxies from external sources
- If proxy sources down, bot continues without proxy
- Sites may detect non-proxy requests (normal for low volumes)

### Problem: No Claims in CSV  
**Solution:**
- Check workflow log for errors
- Verify BTC address is valid
- Wait for next hourly trigger
- Check faucet URLs - some may be offline

---

## 🛡️ SAFETY & SECURITY

✅ **What Bot Does:**
- Sends legitimate claim requests to faucet websites
- Uses anti-detection: proxy rotation, random UA, smart delays
- Tracks failures persistently (auto-disable bad sites)
- Logs all attempts to CSV for audit trail

✅ **What Bot DOESN'T Do:**
- Never exposes private keys or wallet secrets
- Never installs malware or spyware
- Never modifies your computer files (runs on GitHub Actions server)
- Anti-detection is passive (not aggressive scraping)

⚠️ **Limitations:**
- Some faucets require manual CAPTCHA (not automated)
- Free proxy sources may be unreliable
- Earnings very small (~$0.01 per faucet per day typical)
- Depends on faucet URLs staying live

---

## 📞 SUPPORT

**If Bot Needs Code Fixes:**
- Check `phantom_error_notification.json` for details
- Email: bagasmemek77@gmail.com with:
  - Error message from notification
  - Faucet name (which one failed?)
  - Steps you took before error

**For Design Decisions:**
- Bot self-adapts to faucet failures (auto-disable)
- Email notifications only for true critical errors
- Graceful fallbacks for network issues

---

## 📝 NOTES

- Bot runs on **GitHub Actions** (free, always on)
- No cost to run (uses GitHub's free tier)
- No laptop needed (runs on GitHub servers)
- Works 24/7 even if your computer is off
- Earnings auto-logged to CSV for tracking

**Earnings Calculator:**
- Typical per faucet: $0.001 - $0.01 per day
- 11 active faucets: $0.01 - $0.11 per day
- Per month: $0.30 - $3.30
- Per year: $3.65 - $40

**Very low earnings** but ✨ **100% passive & hands-off** ✨

---

## 🎯 NEXT STEPS

1. ✅ Set CAKE_BTC_ADDR secret
2. ✅ Verify in GitHub Actions log (wait for next run or manual trigger)
3. ✅ Monitor csv file daily for claims
4. ❌ DO NOT touch code unless error occurs
5. ✅ Enjoy passive earnings (if any!)

**Expected First Run:** Bot runs within 1 hour (or manual trigger)  
**Expected Result:** CSV gets 1-11 claim entries, some success/fail  
**Expected Earnings:** Varies by faucet/time, tracked in CSV

---

🎭 **Bot is ready. You're all set. No more action needed unless error occurs.**
