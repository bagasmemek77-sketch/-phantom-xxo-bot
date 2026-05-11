#!/usr/bin/env python3
"""
CAPTCHA Solver Module - Auto-solve CAPTCHA blocks using 2captcha API
Free tier: 100 CAPTCHAs/day
Paid: $0.002-0.005 per CAPTCHA (very cheap)
"""
import os
import time
import requests
from typing import Optional, Tuple


class CaptchaSolver:
    """Auto-solve CAPTCHA using 2captcha.com API."""
    
    def __init__(self, api_key: Optional[str] = None):
        # Use env var or provided key
        self.api_key = api_key or os.environ.get("CAPTCHA_2CAPTCHA_KEY", "")
        self.enabled = bool(self.api_key)
        self.base_url = "http://2captcha.com"
        self.max_retries = 5
        self.timeout = 60  # Max wait for CAPTCHA solve
        
    def log(self, msg: str):
        """Log with timestamp."""
        from datetime import datetime
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    
    def solve_recaptcha_v2(self, site_key: str, page_url: str) -> Optional[str]:
        """
        Solve Google reCAPTCHA v2.
        
        Args:
            site_key: The 'data-sitekey' attribute from CAPTCHA widget
            page_url: The page URL containing CAPTCHA
            
        Returns:
            Token string or None if failed
        """
        if not self.enabled:
            self.log("⚠️ CAPTCHA solver disabled (no API key)")
            return None
        
        try:
            # Submit CAPTCHA to 2captcha
            submit_url = f"{self.base_url}/api/upload"
            payload = {
                "key": self.api_key,
                "method": "userrecaptcha",
                "googlekey": site_key,
                "pageurl": page_url,
                "json": 1
            }
            
            self.log(f"📤 Submitting reCAPTCHA v2 to 2captcha...")
            resp = requests.post(submit_url, data=payload, timeout=10)
            data = resp.json()
            
            if data.get("status") != 1:
                self.log(f"⚠️ Submit failed: {data.get('error_text', 'Unknown')}")
                return None
            
            captcha_id = data.get("captcha")
            self.log(f"✅ CAPTCHA submitted (ID: {captcha_id}), waiting for solution...")
            
            # Poll for result
            result_url = f"{self.base_url}/api/res.php"
            for attempt in range(self.max_retries):
                time.sleep(3)  # Wait 3 seconds before polling
                
                result_payload = {
                    "key": self.api_key,
                    "action": "get",
                    "captcha_id": captcha_id,
                    "json": 1
                }
                
                result_resp = requests.get(result_url, params=result_payload, timeout=10)
                result_data = result_resp.json()
                
                if result_data.get("status") == 1:
                    token = result_data.get("request")
                    self.log(f"✅ reCAPTCHA solved in {(attempt+1)*3}s")
                    return token
                
                if result_data.get("status") == 0:
                    # Still processing
                    continue
                
                # Error
                self.log(f"⚠️ Error: {result_data.get('error_text', 'Unknown')}")
                return None
            
            self.log("⏱️ CAPTCHA solve timeout after 60s")
            return None
            
        except Exception as e:
            self.log(f"❌ CAPTCHA solver error: {e}")
            return None
    
    def solve_recaptcha_v3(self, site_key: str, page_url: str, action: str = "verify") -> Optional[str]:
        """Solve Google reCAPTCHA v3."""
        if not self.enabled:
            return None
        
        try:
            submit_url = f"{self.base_url}/api/upload"
            payload = {
                "key": self.api_key,
                "method": "userrecaptcha",
                "googlekey": site_key,
                "pageurl": page_url,
                "version": 3,
                "action": action,
                "min_score": 0.3,
                "json": 1
            }
            
            self.log(f"📤 Submitting reCAPTCHA v3 to 2captcha...")
            resp = requests.post(submit_url, data=payload, timeout=10)
            data = resp.json()
            
            if data.get("status") != 1:
                return None
            
            captcha_id = data.get("captcha")
            
            # Poll for result
            result_url = f"{self.base_url}/api/res.php"
            for attempt in range(self.max_retries):
                time.sleep(3)
                
                result_payload = {
                    "key": self.api_key,
                    "action": "get",
                    "captcha_id": captcha_id,
                    "json": 1
                }
                
                result_resp = requests.get(result_url, params=result_payload, timeout=10)
                result_data = result_resp.json()
                
                if result_data.get("status") == 1:
                    token = result_data.get("request")
                    self.log(f"✅ reCAPTCHA v3 solved in {(attempt+1)*3}s")
                    return token
                
                if result_data.get("status") == 0:
                    continue
                
                return None
            
            return None
            
        except Exception as e:
            self.log(f"❌ reCAPTCHA v3 error: {e}")
            return None
    
    def solve_hcaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve hCaptcha."""
        if not self.enabled:
            return None
        
        try:
            submit_url = f"{self.base_url}/api/upload"
            payload = {
                "key": self.api_key,
                "method": "hcaptcha",
                "sitekey": site_key,
                "pageurl": page_url,
                "json": 1
            }
            
            self.log(f"📤 Submitting hCaptcha to 2captcha...")
            resp = requests.post(submit_url, data=payload, timeout=10)
            data = resp.json()
            
            if data.get("status") != 1:
                return None
            
            captcha_id = data.get("captcha")
            
            result_url = f"{self.base_url}/api/res.php"
            for attempt in range(self.max_retries):
                time.sleep(3)
                
                result_payload = {
                    "key": self.api_key,
                    "action": "get",
                    "captcha_id": captcha_id,
                    "json": 1
                }
                
                result_resp = requests.get(result_url, params=result_payload, timeout=10)
                result_data = result_resp.json()
                
                if result_data.get("status") == 1:
                    token = result_data.get("request")
                    self.log(f"✅ hCaptcha solved in {(attempt+1)*3}s")
                    return token
                
                if result_data.get("status") == 0:
                    continue
                
                return None
            
            return None
            
        except Exception as e:
            self.log(f"❌ hCaptcha error: {e}")
            return None


# Free tier usage tracker
def check_free_tier_limit() -> bool:
    """Check if under free tier limit (100/day)."""
    # Could track in local file or env var
    # For now, return True (assume not exceeded)
    return True
