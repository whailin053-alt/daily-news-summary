import feedparser
import smtplib
import os
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# 从环境变量获取配置
EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME', '3389495929@qq.com')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL', '3389495929@qq.com')

# RSS源
RSS_FEEDS = [
    'https://36kr.com/feed',
    'https://www.infoq.cn/feed'
]

def get_news():
    """获取新闻"""
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
        "💊 早上7点到了，请记得服用阿司匹林！保护心血管健康从每天坚持开始。",
        "⚕️ 阿司匹林服用时间到！请按时服用，呵护您的心脏健康。",
        "❤️ 每日阿司匹林时间：7:00 AM，请按时服用，预防心血管疾病。"
    ]
    return random.choice(reminders)

def send_email(articles):
    """发送邮件"""
    # 生成内容
    reminder = generate_reminder()
    content = f"{reminder}\n\n"
    content += f"## 📰 今日新闻摘要 ({datetime.now().strftime('%Y-%m-%d')})\n\n"
    
    for i, article in enumerate(articles, 1):
        content += f"{i}. [{article['title']}]({article['link']})\n\n"
    
    # 创建邮件
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"🤖 每日新闻摘要 - {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = EMAIL_USERNAME
    msg['To'] = RECIPIENT_EMAIL
    
    # HTML版本
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #1a73e8; text-align: center;">📰 每日新闻摘要</h1>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <p style="font-size: 18px; color: #d93025; font-weight: bold;">{reminder}</p>
            </div>
            <hr>
            <h2>今日精选新闻</h2>
    """
    
    for i, article in enumerate(articles, 1):
        html_content += f'<p><strong>{i}.</strong> <a href="{article["link"]}" style="color: #1a73e8;">{article["title"]}</a></p>'
    
    html_content += """
        </div>
    </body>
    </html>
    """
    
    # 添加内容
    msg.attach(MIMEText(content, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))
    
    # 发送邮件
    with smtplib.SMTP('smtp.qq.com', 587) as server:
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.send_message(msg)

def main():
    """主函数"""
    print("开始执行每日新闻摘要...")
    
    # 获取新闻
    articles = get_news()
    print(f"获取到 {len(articles)} 篇新闻")
    
    # 发送邮件
    if articles:
        send_email(articles)
        print("邮件发送成功!")
    else:
        print("未获取到新闻")

if __name__ == "__main__":
    main()