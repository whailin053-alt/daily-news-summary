# 🚀 云端部署指南

## 方案一：使用Replit（最简单）

### 部署步骤：

1. **注册Replit账号**（免费）
   - 访问 https://replit.com
   - 注册并登录

2. **创建新项目**
   - 点击 "Create Repl"
   - 选择 Python 模板
   - 命名项目（如：daily-news-summary）

3. **上传代码**
   - 将 `cloud_version.py` 文件内容复制到 Replit 编辑器
   - 或者直接上传文件

4. **设置环境变量**
   在 Replit 项目设置中添加：
   ```
   EMAIL_USERNAME=3389495929@qq.com
   EMAIL_PASSWORD=你的QQ邮箱授权码
   RECIPIENT_EMAIL=3389495929@qq.com
   ```

5. **添加依赖**
   在 `requirements.txt` 中添加：
   ```
   feedparser
   requests
   ```

6. **设置定时任务**
   - 在 Replit 中启用 "Always On"（需要付费）
   - 或者使用 UptimeRobot 等免费服务定期访问你的 Replit 应用

## 方案二：使用GitHub Actions

### 部署步骤：

1. **创建GitHub仓库**
   ```
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/daily-news-summary.git
   git push -u origin main
   ```

2. **创建Actions配置文件**
   创建 `.github/workflows/daily_news.yml`：

   ```yaml
   name: Daily News Summary
   
   on:
     schedule:
       - cron: '0 23 * * *'  # UTC时间，对应北京时间早上7点
     workflow_dispatch:  # 手动触发
   
   jobs:
     send-news:
       runs-on: ubuntu-latest
       
       steps:
       - uses: actions/checkout@v3
       
       - name: Set up Python
         uses: actions/setup-python@v4
         with:
           python-version: '3.9'
           
       - name: Install dependencies
         run: |
           pip install feedparser requests
           
       - name: Run news summary
         env:
           EMAIL_USERNAME: ${{ secrets.EMAIL_USERNAME }}
           EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
           RECIPIENT_EMAIL: ${{ secrets.RECIPIENT_EMAIL }}
         run: |
           python cloud_version.py
   ```

3. **设置GitHub Secrets**
   在仓库设置中添加Secrets：
   - `EMAIL_USERNAME`: 3389495929@qq.com
   - `EMAIL_PASSWORD`: 你的QQ邮箱授权码
   - `RECIPIENT_EMAIL`: 3389495929@qq.com

## 方案三：使用Railway（推荐）

### 部署步骤：

1. **注册Railway账号**（免费额度充足）
   - 访问 https://railway.app
   - 使用GitHub账号登录

2. **创建项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择你的仓库

3. **配置环境变量**
   在Railway项目设置中添加：
   ```
   EMAIL_USERNAME=3389495929@qq.com
   EMAIL_PASSWORD=你的QQ邮箱授权码
   RECIPIENT_EMAIL=3389495929@qq.com
   ```

4. **设置定时任务**
   Railway支持Cron Jobs，可以设置每天执行

## 📱 手机接收方式

### 1. QQ邮箱推送
- 确保QQ邮箱开启推送通知
- 在手机QQ邮箱APP中设置及时推送

### 2. 微信推送（可选）
如果想要微信推送，可以：
1. 注册Server酱（https://sct.ftqq.com）
2. 获取推送key
3. 修改代码添加微信推送功能

## ⚙️ 配置说明

### 环境变量：
- `EMAIL_USERNAME`: 发送邮件的QQ邮箱
- `EMAIL_PASSWORD`: QQ邮箱授权码（不是登录密码）
- `RECIPIENT_EMAIL`: 接收邮件的邮箱（可以是同一个）

### 获取QQ邮箱授权码：
1. 登录QQ邮箱网页版
2. 设置 → 账户 → POP3/IMAP/SMTP服务
3. 开启IMAP/SMTP服务
4. 按提示发送短信获取16位授权码

## 🎯 使用建议

1. **首次部署**：建议先手动运行测试
2. **监控日志**：定期检查执行日志确保正常运行
3. **备用方案**：可以同时部署多个平台作为备份

## 🆘 常见问题

**Q: 邮件发送失败怎么办？**
A: 检查QQ邮箱授权码是否正确，网络连接是否正常

**Q: 定时任务不执行怎么办？**
A: 检查Cron表达式是否正确，时区设置是否为北京时间

**Q: 如何修改推送时间？**
A: 修改Cron表达式，例如：
- 每天7点：`0 23 * * *`（UTC时间）
- 每天8点：`0 0 * * *`（UTC时间）

选择任一方案部署后，你就可以每天早上7点在手机QQ邮箱收到新闻摘要和阿司匹林提醒了！