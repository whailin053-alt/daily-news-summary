import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EmailSender:
    """邮件发送器"""
    
    def __init__(self, config):
        self.config = config
        self.enabled = config.get('email.enabled', False)
        
        if self.enabled:
            self.smtp_server = config.get('email.smtp_server')
            self.smtp_port = config.get('email.smtp_port', 587)
            self.username = config.get('email.username')
            self.password = config.get('email.password')
            self.recipients = config.get('email.recipients', [])
    
    def send_daily_report(self, report_file: str, subject_prefix: str = "") -> bool:
        """发送每日报告邮件"""
        if not self.enabled:
            logger.info("邮件功能未启用")
            return True
        
        if not self.recipients:
            logger.warning("未配置收件人")
            return False
        
        try:
            # 读取报告内容
            with open(report_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 生成邮件主题
            today = datetime.now().strftime('%Y-%m-%d')
            subject = f"{subject_prefix}每日新闻摘要 - {today}" if subject_prefix else f"每日新闻摘要 - {today}"
            
            # 生成个性化提醒（放在最顶部）
            personalized_message = self._generate_personalized_message()
            
            # 将提醒放在内容最前面
            content_with_reminder = f"{personalized_message}\n\n---\n\n{content}"
            
            # 发送邮件
            success_count = 0
            for recipient in self.recipients:
                if self._send_email(recipient, subject, content_with_reminder):
                    success_count += 1
                    logger.info(f"邮件已发送至: {recipient}")
                else:
                    logger.error(f"发送邮件失败: {recipient}")
            
            return success_count == len(self.recipients)
            
        except Exception as e:
            logger.error(f"发送邮件时出现错误: {e}")
            return False
    
    def _generate_personalized_message(self) -> str:
        """生成个性化提醒消息"""
        import random
        
        # 阿司匹林专用提醒语录库
        aspirin_reminders = [
            "💊 【阿司匹林提醒】早上7点到了，请记得服用阿司匹林！保护心血管健康从每天坚持开始。",
            "⚕️ 【用药提醒】阿司匹林服用时间到！请在早餐前或随餐服用，呵护您的心脏健康。",
            "❤️ 【健康守护】每日阿司匹林时间：7:00 AM，请按时服用，预防心血管疾病。",
            "🌟 【晨间健康】新的一天开始了，记得按时服用阿司匹林，为健康保驾护航！",
            "📅 【用药打卡】7点阿司匹林时间到！坚持规律用药，健康生活每一天。",
            "🌿 【健康管理】晨起第一件事：服用阿司匹林！小小药片，大大健康保障。",
            "💪 【健康习惯】7点准时服用阿司匹林，养成良好用药习惯，远离心血管风险。",
            "🌈 【每日必备】阿司匹林7点提醒：按时服用，健康常伴，活力满满一整天！",
            "🩺 【医生叮嘱】每日7点阿司匹林服用提醒，请遵医嘱按时用药。",
            "✨ 【健康伴侣】7点阿司匹林时间到！坚持就是胜利，健康需要您的用心呵护。"
        ]
        
        # 随机选择一条阿司匹林提醒
        reminder = random.choice(aspirin_reminders)
        
        # 添加时间和鼓励话语
        current_time = datetime.now().strftime("%H:%M")
        encouragement = "新的一天开始了，愿您身体健康，工作顺利！"
        
        return f"⏰ 当前时间：{current_time}\n\n{reminder}\n\n{encouragement}"
    
    def _send_email(self, recipient: str, subject: str, content: str) -> bool:
        """发送单封邮件"""
        try:
            # 创建邮件对象
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.username
            msg['To'] = recipient
            
            # 添加HTML版本（如果内容看起来像Markdown）
            html_content = self._markdown_to_html(content)
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 添加纯文本版本
            text_part = MIMEText(content, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # 连接SMTP服务器并发送
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            logger.error(f"发送邮件到 {recipient} 失败: {e}")
            return False
    
    def _markdown_to_html(self, markdown_content: str) -> str:
        """优化的Markdown转HTML转换（针对移动端QQ邮箱）"""
        import re
        
        # 基本的Markdown转HTML规则
        html = markdown_content
        
        # 标题转换（适配移动端）
        html = re.sub(r'^# (.+)$', r'<h1 style="color:#1a73e8;font-size:24px;margin:20px 0 15px 0;border-bottom:2px solid #1a73e8;padding-bottom:10px;">\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2 style="color:#202124;font-size:20px;margin:25px 0 12px 0;padding:10px;background:#f8f9fa;border-left:4px solid #1a73e8;">\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', r'<h3 style="color:#5f6368;font-size:18px;margin:20px 0 10px 0;">\1</h3>', html, flags=re.MULTILINE)
        
        # 列表转换
        html = re.sub(r'^\* (.+)$', r'<li style="margin:8px 0;padding:8px 0;border-bottom:1px solid #eee;">\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'^- (.+)$', r'<li style="margin:8px 0;padding:8px 0;border-bottom:1px solid #eee;">\1</li>', html, flags=re.MULTILINE)
        
        # 链接转换（移动端友好的样式）
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" style="color:#1a73e8;text-decoration:none;font-weight:bold;">\1</a>', html)
        
        # 粗体转换
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#202124;background:#fff3cd;padding:2px 6px;border-radius:3px;">\1</strong>', html)
        
        # 斜体转换
        html = re.sub(r'\*(.+?)\*', r'<em style="color:#5f6368;font-style:italic;">\1</em>', html)
        
        # 换行转换
        html = html.replace('\n', '<br>\n')
        
        # 包装在移动端优化的HTML结构中
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    line-height: 1.6; 
                    color: #202124; 
                    max-width: 100%;
                    padding: 15px;
                    background: #ffffff;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #1a73e8 0%, #4285f4 100%);
                    color: white;
                    padding: 25px 20px;
                    text-align: center;
                }}
                .content {{
                    padding: 25px 20px;
                }}
                .section {{
                    margin: 25px 0;
                    padding: 20px;
                    background: #f8f9fa;
                    border-radius: 10px;
                    border-left: 4px solid #1a73e8;
                }}
                .article-item {{
                    background: white;
                    margin: 15px 0;
                    padding: 15px;
                    border-radius: 8px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }}
                .source-tag {{
                    display: inline-block;
                    background: #e8f0fe;
                    color: #1a73e8;
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: bold;
                    margin: 5px 0;
                }}
                a {{ 
                    color: #1a73e8; 
                    text-decoration: none; 
                }}
                a:hover {{ 
                    text-decoration: underline; 
                }}
                li {{ 
                    margin: 10px 0; 
                    padding-left: 10px;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #5f6368;
                    font-size: 14px;
                    border-top: 1px solid #eee;
                    margin-top: 30px;
                }}
                @media (max-width: 480px) {{
                    body {{ padding: 10px; }}
                    .header {{ padding: 20px 15px; }}
                    .content {{ padding: 20px 15px; }}
                    h1 {{ font-size: 22px !important; }}
                    h2 {{ font-size: 18px !important; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📰 每日新闻摘要</h1>
                    <p style="opacity: 0.9; margin: 10px 0 0 0;">为您精选的今日要闻</p>
                </div>
                <div class="content">
                    {html}
                </div>
                <div class="footer">
                    <p>🤖 由AI智能生成 | 📧 自动发送至您的邮箱</p>
                    <p>点击链接查看全文，收藏您感兴趣的内容</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template