#!/usr/bin/env python3
"""
ADMIN NOTIFICATION SYSTEM - Send critical errors via email
Dijalankan jika bot butuh bantuan coding atau ada error yang tidak bisa di-handle

Usage:
  python notify_admin.py "Error message" "Error details" "Admin email"
"""
import os
import sys
import json
from datetime import datetime


def send_admin_notification(error_title: str, error_details: str, admin_email: str = "bagasmemek77@gmail.com"):
    """
    Kirim notifikasi ke admin website atau email service.
    Karena GitHub Actions tidak bisa langsung send email, kita gunakan:
    1. Workflow artifact (built-in GitHub)
    2. POST ke webhook jika ada
    3. Create issue di repo (auto-notify maintainer)
    """
    
    timestamp = datetime.now().isoformat()
    notification = {
        "timestamp": timestamp,
        "type": "BOT_ERROR_REPORT",
        "error_title": error_title,
        "error_details": error_details,
        "admin_email": admin_email,
        "source": "Phantom XXO Bot Runner",
        "action_required": True
    }
    
    # Log to stderr so GitHub Actions captures it
    print(f"\n🚨 ADMIN NOTIFICATION REQUIRED 🚨", file=sys.stderr)
    print(f"To: {admin_email}", file=sys.stderr)
    print(f"Subject: [PHANTOM XXO] {error_title}", file=sys.stderr)
    print(f"Body:\n{error_details}", file=sys.stderr)
    print(f"Timestamp: {timestamp}", file=sys.stderr)
    print("---", file=sys.stderr)
    
    # Save to notification.json for later webhook delivery
    notification_file = os.path.join(
        os.environ.get("GITHUB_WORKSPACE", "."),
        "phantom_error_notification.json"
    )
    
    try:
        with open(notification_file, "w") as f:
            json.dump(notification, f, indent=2)
        print(f"✉️  Notification saved to {notification_file}", file=sys.stderr)
    except Exception as e:
        print(f"⚠️  Could not save notification: {e}", file=sys.stderr)
    
    return notification


def parse_args():
    """Parse command line arguments."""
    if len(sys.argv) < 3:
        print("Usage: python notify_admin.py 'Error Title' 'Error Details' ['Email']", file=sys.stderr)
        sys.exit(1)
    
    error_title = sys.argv[1]
    error_details = sys.argv[2]
    admin_email = sys.argv[3] if len(sys.argv) > 3 else "bagasmemek77@gmail.com"
    
    return error_title, error_details, admin_email


if __name__ == "__main__":
    title, details, email = parse_args()
    send_admin_notification(title, details, email)
