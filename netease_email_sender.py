#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网易邮箱版本 - 发送每日新闻摘要到网易邮箱
"""

import smtplib
import os
import feedparser
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

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
        except:
            pass
    
    return articles

def generate_reminder():
    """生成服药提醒"""
    reminders = [
        "[阿司匹林提醒] 早上7点到了，请记得服用阿司匹林！保护心血管健康从每天坚持开始。",
        "[用药提醒] 阿司匹林服用时间到！请按时服用，呵护您的心脏健康。",
        "[健康守护] 每日阿司匹林时间：7:00 AM，请按时服用，预防心血管疾病。"
    ]
    return random.choice(reminders)

def send_email_163(articles):
    """使用网易邮箱发送邮件"""
    # 网易邮箱配置
    NETEASE_USER = os.environ.get('NETEASE_USER')  # 您的网易邮箱地址
    NETEASE_PASSWORD = os.environ.get('NETEASE_PASSWORD')  # 网易邮箱授权码
    RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL', '您的网易邮箱地址')
    
    if not NETEASE_USER or not NETEASE_PASSWORD:
        print("网易邮箱凭证未配置")
        return False
    
    # 生成内容
    reminder = generate_reminder()
    content = f"{reminder}\n\n"
    content += f"## 今日新闻摘要 ({datetime.now().strftime('%Y-%m-%d')})\n\n"
    
    for i, article in enumerate(articles, 1):
        content += f"{i}. {article['title']}\n   链接: {article['link']}\n\n"
    
    # 创建邮件
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"[每日新闻摘要] {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = NETEASE_USER
    msg['To'] = RECIPIENT_EMAIL
    
    # 添加内容
    msg.attach(MIMEText(content, 'plain', 'utf-8'))
    
    # 发送邮件
    try:
        with smtplib.SMTP('smtp.163.com', 25) as server:
            server.login(NETEASE_USER, NETEASE_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"网易邮箱发送失败: {e}")
        return False

def send_email_qq_fallback(articles):
    """QQ邮箱备用方案"""
    EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME', '3389495929@qq.com')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
    RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL', '3389495929@qq.com')
    
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
    try:
        with smtplib.SMTP('smtp.qq.com', 587) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"QQ邮箱发送失败: {e}")
        return False

def main():
    """主函数 - 尝试多种发送方式"""
    print("开始执行每日新闻摘要...")
    
    # 获取新闻
    articles = get_news()
    print(f"获取到 {len(articles)} 篇新闻")
    
    if not articles:
        print("未获取到新闻")
        return
    
    # 首先尝试网易邮箱
    netease_success = send_email_163(articles)
    if netease_success:
        print("[SUCCESS] 邮件通过网易邮箱发送成功!")
        return
    
    # 如果网易邮箱失败，回退到QQ邮箱
    qq_success = send_email_qq_fallback(articles)
    if qq_success:
        print("[SUCCESS] 邮件通过QQ邮箱发送成功!")
    else:
        print("[FAILED] 所有邮件发送方式都失败了")

if __name__ == "__main__":
    main()