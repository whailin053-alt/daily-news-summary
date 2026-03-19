import feedparser
import smtplib
import os
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def test_local():
    """本地测试函数"""
    print("=== 本地测试开始 ===")
    
    # 测试RSS获取
    print("1. 测试RSS获取...")
    RSS_FEEDS = ['https://36kr.com/feed']
    
    articles = []
    for feed_url in RSS_FEEDS:
        try:
            print(f"  获取 {feed_url}")
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:2]:
                articles.append({
                    'title': entry.title,
                    'link': entry.link
                })
                print(f"    - {entry.title[:50]}...")
        except Exception as e:
            print(f"  获取失败: {e}")
    
    print(f"  共获取到 {len(articles)} 篇文章")
    
    # 测试邮件发送（需要真实配置）
    print("\n2. 测试邮件配置...")
    EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME', '3389495929@qq.com')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '请填入真实授权码')
    RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL', '3389495929@qq.com')
    
    print(f"  发送邮箱: {EMAIL_USERNAME}")
    print(f"  接收邮箱: {RECIPIENT_EMAIL}")
    print(f"  密码长度: {len(EMAIL_PASSWORD)} 字符")
    
    if EMAIL_PASSWORD == '请填入真实授权码':
        print("  ❌ 请设置真实的QQ邮箱授权码")
        return False
    
    # 生成测试邮件内容
    print("\n3. 生成邮件内容...")
    reminder = "💊 【阿司匹林提醒】早上7点到了，请记得服用阿司匹林！"
    content = f"{reminder}\n\n"
    content += f"## 📰 今日新闻摘要 ({datetime.now().strftime('%Y-%m-%d')})\n\n"
    
    for i, article in enumerate(articles, 1):
        content += f"{i}. {article['title']}\n   链接: {article['link']}\n\n"
    
    print("  ✅ 邮件内容生成完成")
    
    # 尝试发送邮件
    print("\n4. 尝试发送邮件...")
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🤖 测试邮件 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        msg['From'] = EMAIL_USERNAME
        msg['To'] = RECIPIENT_EMAIL
        
        msg.attach(MIMEText(content, 'plain', 'utf-8'))
        
        with smtplib.SMTP('smtp.qq.com', 587) as server:
            server.starttls()
            print("  连接SMTP服务器...")
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            print("  登录成功...")
            server.send_message(msg)
            print("  ✅ 邮件发送成功!")
            
        return True
        
    except Exception as e:
        print(f"  ❌ 邮件发送失败: {e}")
        return False

if __name__ == "__main__":
    success = test_local()
    print(f"\n=== 测试结果: {'成功' if success else '失败'} ===")