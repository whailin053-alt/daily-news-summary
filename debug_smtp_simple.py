#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import smtplib
import os
import socket
import sys
from dotenv import load_dotenv

# 设置编码
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# 加载环境变量
if os.path.exists('.env'):
    load_dotenv()

def test_smtp_connection():
    EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME', '3389495929@qq.com')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
    RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL', '3389495929@qq.com')
    
    print("=== SMTP Connection Debug Info ===")
    print(f"Sender Email: {EMAIL_USERNAME}")
    print(f"Recipient Email: {RECIPIENT_EMAIL}")
    print(f"Password Length: {len(EMAIL_PASSWORD) if EMAIL_PASSWORD else 0}")
    
    # Test DNS resolution
    try:
        ip_address = socket.gethostbyname('smtp.qq.com')
        print(f"SMTP Server IP: {ip_address}")
    except Exception as e:
        print(f"DNS Resolution Failed: {e}")
        return False
    
    # Test port connectivity
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex(('smtp.qq.com', 587))
        sock.close()
        if result == 0:
            print("[SUCCESS] Port 587 connection OK")
        else:
            print("[FAILED] Port 587 connection failed")
            return False
    except Exception as e:
        print(f"Port test failed: {e}")
        return False
    
    # Test SMTP connection
    try:
        print("\n--- Starting SMTP Connection Test ---")
        server = smtplib.SMTP('smtp.qq.com', 587, timeout=30)
        print("[SUCCESS] SMTP server connected")
        
        server.set_debuglevel(1)
        
        print("\n--- Starting TLS Encryption ---")
        server.starttls()
        print("[SUCCESS] TLS started")
        
        print(f"\n--- Attempting login for {EMAIL_USERNAME} ---")
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        print("[SUCCESS] Login successful!")
        
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"[AUTH ERROR] Authentication failed: {e}")
        print("Possible causes:")
        print("1. Incorrect authorization code (not QQ login password)")
        print("2. IMAP/SMTP service not enabled in QQ Mail")
        print("3. Account locked or requires verification")
        return False
        
    except smtplib.SMTPServerDisconnected as e:
        print(f"[DISCONNECT ERROR] Server disconnected: {e}")
        print("Possible causes:")
        print("1. QQ Mail security policy blocking CI/CD environments")
        print("2. IP address restrictions")
        print("3. Connection timeout")
        return False
        
    except Exception as e:
        print(f"[OTHER ERROR] Other error: {e}")
        return False

if __name__ == "__main__":
    success = test_smtp_connection()
    if success:
        print("\n[SUCCESS] All tests passed! SMTP configuration is correct.")
    else:
        print("\n[FAILED] Test failed, please check the error messages above.")