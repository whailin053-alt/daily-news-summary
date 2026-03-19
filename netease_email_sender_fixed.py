#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复版网易邮箱发送脚本 - 解决类型错误问题
"""

import smtplib
import os
import feedparser
import random
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

# 设置UTF-8编码
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# 加载环境变量
if os.path.exists('.env'):
    load_dotenv()

def get_news():
    """获取新闻"""
    RSS_FEEDS = ['https://36kr.com/feed', 'https://www.infoq.cn/feed']
    articles = []
    
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:3]:
                articles.append({
                    'title': entry.title,
                    'link': entry.link
                })
        except Exception as e:
            print(f"获取新闻源失败 {feed_url}: {e}")
            continue
    
    return articles

def generate_reminder():
    """生成服药提醒"""
    reminders = [
        "[阿司匹林提醒] 早上7点到了，请记得服用阿司匹林！保护心血管健康从每天坚持开始。",
        "[用药提醒] 阿司匹林服用时间到！请按时服用，呵护您的心脏健康。",
        "[健康守护] 每日阿司匹林时间：7:00 AM，请按时服用，预防心血管疾病。"
    ]
    return random.choice(reminders)

def send_email_163_safe(articles):
    """使用网易邮箱发送邮件 - 安全版本"""
    # 确保环境变量是字符串类型
    NETEASE_USER = str(os.environ.get('NETEASE_USER', '')).strip()
    NETEASE_PASSWORD = str(os.environ.get('NETEASE_PASSWORD', '')).strip()
    RECIPIENT_EMAIL = str(os.environ.get('RECIPIENT_EMAIL', '')).strip()
    
    print(f"网易邮箱用户: {NETEASE_USER}")
    print(f"收件人邮箱: {RECIPIENT_EMAIL}")
    
    if not NETEASE_USER or not NETEASE_PASSWORD:
        print("网易邮箱凭证未配置或为空")
        return False
    
    if not RECIPIENT_EMAIL:
        print("收件人邮箱未配置")
        return False
    
    try:
        # 生成内容
        reminder = generate_reminder()
        content = f"{reminder}\n\n"
        content += f"## 今日新闻摘要 ({datetime.now().strftime('%Y-%m-%d')})\n\n"
        
        for i, article in enumerate(articles, 1):
            content += f"{i}. {article['title']}\n   链接: {article['link']}\n\n"
        
        # 创建邮件 - 确保所有字段都是字符串
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"[每日新闻摘要] {datetime.now().strftime('%Y-%m-%d')}"
        msg['From'] = NETEASE_USER
        msg['To'] = RECIPIENT_EMAIL
        
        # 添加内容 - 使用UTF-8编码
        msg.attach(MIMEText(content, 'plain', 'utf-8'))
        
        print("正在连接网易邮箱SMTP服务器...")
        # 使用安全的连接方式
        with smtplib.SMTP('smtp.163.com', 25, timeout=30) as server:
            print("SMTP服务器连接成功")
            # 确保用户名和密码是字符串类型
            username_str = str(NETEASE_USER)
            password_str = str(NETEASE_PASSWORD)
            
            print("尝试登录...")
            server.login(username_str, password_str)
            print("登录成功")
            
            print("发送邮件...")
            server.send_message(msg)
            print("邮件发送成功")
            
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"网易邮箱认证失败: {e}")
        print("请检查用户名和授权码是否正确")
        return False
        
    except smtplib.SMTPException as e:
        print(f"网易邮箱SMTP错误: {e}")
        return False
        
    except Exception as e:
        print(f"网易邮箱发送异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def send_email_qq_fallback(articles):
    """QQ邮箱备用方案"""
    EMAIL_USERNAME = str(os.environ.get('EMAIL_USERNAME', '3389495929@qq.com')).strip()
    EMAIL_PASSWORD = str(os.environ.get('EMAIL_PASSWORD', '')).strip()
    RECIPIENT_EMAIL = str(os.environ.get('RECIPIENT_EMAIL', '3389495929@qq.com')).strip()
    
    if not EMAIL_PASSWORD:
        print("QQ邮箱密码未配置")
        return False
    
    try:
        # 生成内容
        reminder = generate_reminder()
        content = f"{reminder}\n\n"
        content += f"## 今日新闻摘要 ({datetime.now().strftime('%Y-%m-%d')})\n\n"
        
        for i, article in enumerate(articles, 1):
            content += f"{i}. {article['title']}\n   链接: {article['link']}\n\n"
        
        # 创建邮件
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"[每日新闻摘要] {datetime.now().strftime('%Y-%m-%d')}"
        msg['From'] = EMAIL_USERNAME
        msg['To'] = RECIPIENT_EMAIL
        
        # 添加内容
        msg.attach(MIMEText(content, 'plain', 'utf-8'))
        
        # 发送邮件
        with smtplib.SMTP('smtp.qq.com', 587, timeout=30) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.send_message(msg)
        return True
        
    except Exception as e:
        print(f"QQ邮箱发送失败: {e}")
        return False

def main():
    """主函数 - 尝试多种发送方式"""
    print("=== 开始执行每日新闻摘要 ===")
    
    # 获取新闻
    articles = get_news()
    print(f"获取到 {len(articles)} 篇新闻")
    
    if not articles:
        print("未获取到新闻内容")
        return 1
    
    # 首先尝试网易邮箱
    print("\n--- 尝试网易邮箱发送 ---")
    netease_success = send_email_163_safe(articles)
    if netease_success:
        print("[SUCCESS] 邮件通过网易邮箱发送成功!")
        return 0
    
    # 如果网易邮箱失败，回退到QQ邮箱
    print("\n--- 尝试QQ邮箱发送 ---")
    qq_success = send_email_qq_fallback(articles)
    if qq_success:
        print("[SUCCESS] 邮件通过QQ邮箱发送成功!")
        return 0
    else:
        print("[FAILED] 所有邮件发送方式都失败了")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)