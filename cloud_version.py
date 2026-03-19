#!/usr/bin/env python3
"""
简化版每日新闻摘要 - 云端部署版本
适合部署到免费云平台如Replit、Railway等
"""

import feedparser
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os
import random
import json

# 配置信息（从环境变量读取）
EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME', '3389495929@qq.com')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL', '3389495929@qq.com')

# RSS源配置
RSS_SOURCES = [
    {
        'name': '机器之心',
        'url': 'https://www.jiqizhixin.com/rss',
        'category': 'tech'
    },
    {
        'name': '36氪',
        'url': 'https://36kr.com/feed',
        'category': 'tech'
    },
    {
        'name': 'InfoQ',
        'url': 'https://www.infoq.cn/feed',
        'category': 'tech'
    }
]

def fetch_news():
    """获取新闻"""
    all_articles = []
    
    for source in RSS_SOURCES:
        try:
            print(f"正在获取 {source['name']} 的新闻...")
            feed = feedparser.parse(source['url'])
            
            for entry in feed.entries[:5]:  # 每个源取5篇文章
                # 检查是否是24小时内发布的
                pub_date = entry.get('published_parsed')
                if pub_date:
                    pub_datetime = datetime(*pub_date[:6])
                    if (datetime.now() - pub_datetime).days < 1:
                        article = {
                            'title': entry.get('title', ''),
                            'link': entry.get('link', ''),
                            'source': source['name'],
                            'published': pub_datetime.strftime('%m-%d %H:%M')
                        }
                        all_articles.append(article)
        except Exception as e:
            print(f"获取 {source['name']} 失败: {e}")
    
    return all_articles

def generate_summary(articles):
    """生成简单摘要"""
    if not articles:
        return "今日暂无重要新闻"
    
    # 按来源分组
    by_source = {}
    for article in articles:
        source = article['source']
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(article)
    
    summary = f"## 📰 今日新闻摘要 ({datetime.now().strftime('%Y-%m-%d')})\n\n"
    
    for source, source_articles in by_source.items():
        summary += f"### {source} ({len(source_articles)}篇)\n"
        for i, article in enumerate(source_articles[:3], 1):  # 每源最多3篇
            summary += f"{i}. [{article['title']}]({article['link']})\n"
            summary += f"   *发布时间: {article['published']}*\n\n"
        summary += "\n"
    
    return summary

def generate_medication_reminder():
    """生成阿司匹林提醒"""
    reminders = [
        "💊 【阿司匹林提醒】早上7点到了，请记得服用阿司匹林！保护心血管健康从每天坚持开始。",
        "⚕️ 【用药提醒】阿司匹林服用时间到！请在早餐前或随餐服用，呵护您的心脏健康。",
        "❤️ 【健康守护】每日阿司匹林时间：7:00 AM，请按时服用，预防心血管疾病。",
        "🌟 【晨间健康】新的一天开始了，记得按时服用阿司匹林，为健康保驾护航！",
        "📅 【用药打卡】7点阿司匹林时间到！坚持规律用药，健康生活每一天。"
    ]
    
    return random.choice(reminders)

def send_email(content):
    """发送邮件"""
    try:
        # 创建邮件
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🤖 每日新闻摘要 - {datetime.now().strftime('%Y-%m-%d')}"
        msg['From'] = EMAIL_USERNAME
        msg['To'] = RECIPIENT_EMAIL
        
        # 添加提醒在最前面
        medication_reminder = generate_medication_reminder()
        full_content = f"{medication_reminder}\n\n---\n\n{content}"
        
        # 添加HTML版本
        html_content = markdown_to_html(full_content)
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # 添加纯文本版本
        text_part = MIMEText(full_content, 'plain', 'utf-8')
        msg.attach(text_part)
        
        # 发送邮件
        with smtplib.SMTP('smtp.qq.com', 587) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.send_message(msg)
        
        print("✅ 邮件发送成功!")
        return True
        
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        return False

def markdown_to_html(markdown_text):
    """简单的Markdown转HTML"""
    import re
    
    html = markdown_text
    
    # 标题
    html = re.sub(r'^## (.+)$', r'<h2 style="color:#1a73e8;margin:20px 0 15px 0;">\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3 style="color:#5f6368;margin:15px 0 10px 0;">\1</h3>', html, flags=re.MULTILINE)
    
    # 列表
    html = re.sub(r'^(\d+)\. (.+)$', r'<p style="margin:8px 0;"><strong>\1.</strong> \2</p>', html, flags=re.MULTILINE)
    
    # 链接
    html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" style="color:#1a73e8;text-decoration:none;">\1</a>', html)
    
    # 强调
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#d93025;">\1</strong>', html)
    
    # 换行
    html = html.replace('\n', '<br>')
    
    return f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #202124; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; }}
            .header {{ background: linear-gradient(135deg, #1a73e8 0%, #4285f4 100%); color: white; padding: 20px; text-align: center; border-radius: 10px; }}
            .content {{ padding: 20px; background: #f8f9fa; border-radius: 10px; margin-top: 20px; }}
            hr {{ border: none; border-top: 2px solid #1a73e8; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📰 每日新闻摘要</h1>
                <p>为您精选的今日要闻</p>
            </div>
            <div class="content">
                {html}
            </div>
        </div>
    </body>
    </html>
    """

def main():
    """主函数"""
    print("🚀 开始执行每日新闻摘要任务...")
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 获取新闻
    print("\n🔍 正在获取新闻...")
    articles = fetch_news()
    print(f"✅ 共获取到 {len(articles)} 篇新闻")
    
    # 生成摘要
    print("\n📝 正在生成摘要...")
    summary = generate_summary(articles)
    
    # 发送邮件
    print("\n📧 正在发送邮件...")
    success = send_email(summary)
    
    if success:
        print("\n🎉 任务完成!")
        print(f"📬 邮件已发送至: {RECIPIENT_EMAIL}")
    else:
        print("\n❌ 任务失败!")
    
    # 返回状态供云平台监控
    return {
        'success': success,
        'articles_count': len(articles),
        'timestamp': datetime.now().isoformat()
    }

if __name__ == "__main__":
    result = main()
    print(json.dumps(result, indent=2))