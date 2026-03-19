#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Actions环境测试脚本
用于检测CI/CD环境中的SMTP连接问题
"""

import smtplib
import os
import socket
import platform
import sys

def test_github_actions_environment():
    print("=== GitHub Actions Environment Test ===")
    
    # 环境信息
    print(f"Python Version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"System: {platform.system()}")
    
    # 检查环境变量
    EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
    RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL')
    
    print(f"EMAIL_USERNAME set: {'Yes' if EMAIL_USERNAME else 'No'}")
    print(f"EMAIL_PASSWORD set: {'Yes' if EMAIL_PASSWORD else 'No'}")
    print(f"RECIPIENT_EMAIL set: {'Yes' if RECIPIENT_EMAIL else 'No'}")
    
    if EMAIL_USERNAME and EMAIL_PASSWORD:
        print(f"Username: {EMAIL_USERNAME}")
        print(f"Password length: {len(EMAIL_PASSWORD)}")
        print(f"Password preview: {EMAIL_PASSWORD[:4]}...")
    else:
        print("Missing required environment variables!")
        return False
    
    # 网络测试
    print("\n=== Network Tests ===")
    
    # DNS解析测试
    try:
        ip = socket.gethostbyname('smtp.qq.com')
        print(f"smtp.qq.com resolves to: {ip}")
    except Exception as e:
        print(f"DNS resolution failed: {e}")
        return False
    
    # 端口连通性测试
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(15)
        result = sock.connect_ex(('smtp.qq.com', 587))
        sock.close()
        if result == 0:
            print("[SUCCESS] Port 587 is accessible")
        else:
            print(f"[FAILED] Cannot connect to port 587 (result: {result})")
            return False
    except Exception as e:
        print(f"Port connectivity test failed: {e}")
        return False
    
    # SMTP连接测试
    print("\n=== SMTP Connection Test ===")
    try:
        server = smtplib.SMTP('smtp.qq.com', 587, timeout=30)
        print("[SUCCESS] Connected to SMTP server")
        
        # 启用调试
        server.set_debuglevel(1)
        
        # 启动TLS
        print("\n--- Starting TLS ---")
        server.starttls()
        print("[SUCCESS] TLS established")
        
        # 尝试登录
        print(f"\n--- Attempting login for {EMAIL_USERNAME} ---")
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        print("[SUCCESS] Authentication successful!")
        
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"[AUTH FAILED] {e}")
        print("This suggests the authorization code is incorrect")
        return False
        
    except smtplib.SMTPServerDisconnected as e:
        print(f"[DISCONNECTED] {e}")
        print("This confirms QQ Mail is blocking CI/CD environment connections")
        return False
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == "__main__":
    print("Starting GitHub Actions SMTP environment test...")
    success = test_github_actions_environment()
    
    if success:
        print("\n[SUCCESS] All tests passed in GitHub Actions environment!")
    else:
        print("\n[FAILED] Tests failed - environment-specific issue confirmed")
        print("\nRecommendations:")
        print("1. QQ Mail may block CI/CD environments for security reasons")
        print("2. Consider using alternative email providers")
        print("3. Try enabling 'less secure app access' if available")
        print("4. Check if IP whitelisting is required")