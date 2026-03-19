# 📰 每日新闻AI摘要工具

一个自动化获取、分析和总结新闻的Python工具，支持RSS订阅源和AI智能摘要。

## 🌟 功能特性

- **多源新闻聚合**: 支持RSS订阅源和NewsAPI
- **AI智能摘要**: 使用OpenAI GPT模型生成中文/英文摘要
- **分类整理**: 自动按科技、金融、国际等分类整理新闻
- **多种输出格式**: 生成Markdown报告和邮件推送
- **灵活配置**: 易于添加/删除新闻源和调整参数
- **定时执行**: 支持一次性执行或定时自动运行

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

编辑 `.env` 文件并填入必要的API密钥：

```env
# 必需：OpenAI API密钥
OPENAI_API_KEY=sk-your-openai-api-key-here

# 可选：NewsAPI密钥
NEWSAPI_KEY=your-newsapi-key-here

# QQ邮箱配置（用于接收新闻摘要）
EMAIL_USERNAME=3389495929@qq.com
EMAIL_PASSWORD=your_qq_email_auth_code_here
```

**重要提醒**：
- QQ邮箱需要使用**授权码**而非登录密码
- 授权码可在QQ邮箱设置中开启IMAP/SMTP服务获取

### 3. 修改配置文件

编辑 `config/config.yaml` 来定制你的新闻源和偏好设置。

### 4. 运行程序

```bash
# 一次性执行（推荐首次测试）
python src/main.py --once

# 详细输出模式（调试用）
python src/main.py --once --verbose

# 定时执行（默认每天9:00）
python src/main.py

# 自定义执行时间
python src/main.py --schedule-time "18:00"
```

## 📁 项目结构

```
daily-news-ai-summary/
├── src/                    # 源代码目录
│   ├── main.py            # 主程序入口
│   ├── config.py          # 配置管理
│   ├── news_fetcher.py    # 新闻获取模块
│   ├── ai_summarizer.py   # AI摘要生成
│   ├── reporter.py        # 报告生成
│   └── email_sender.py    # 邮件发送
├── config/
│   └── config.yaml        # 配置文件
├── output/                # 生成的报告文件
├── requirements.txt       # Python依赖
├── .env                   # 环境变量文件
└── README.md             # 项目说明
```

## ⚙️ 配置说明

### 主要配置项

```yaml
# OpenAI配置
openai:
  api_key: "${OPENAI_API_KEY}"    # OpenAI API密钥
  model: "gpt-3.5-turbo"          # 使用的模型
  temperature: 0.3                # 创造性程度（0-1）
  max_tokens: 1000               # 最大token数

# 新闻源配置
rss_sources:
  - name: "BBC News"
    url: "http://feeds.bbci.co.uk/news/rss.xml"
    category: "world"
    enabled: true

# 邮件配置
email:
  enabled: true                   # 是否启用邮件功能
  smtp_server: "smtp.qq.com"      # QQ邮箱SMTP服务器
  recipients:
    - "3389495929@qq.com"         # 你的QQ邮箱地址
```

## 🛠️ 使用示例

### 命令行选项

```bash
# 查看帮助
python src/main.py --help

# 详细输出模式
python src/main.py --once --verbose

# 指定配置文件
python src/main.py --config ./my_config.yaml --once
```

### 输出示例

程序会生成类似这样的Markdown报告：

```markdown
# 📰 每日新闻摘要 - 2024-03-18

## 🎯 今日概览
今日科技领域重点关注人工智能发展...

## 💻 科技
### 摘要
今天的主要科技新闻包括...

### 🔑 关键要点
- 人工智能技术又有新突破
- 科技公司发布重要产品更新
- 行业监管政策有所调整
```

## 🔧 开发指南

### 添加新的新闻源

在 `config/config.yaml` 中添加新的RSS源：

```yaml
rss_sources:
  - name: "新的新闻源"
    url: "https://example.com/rss"
    category: "tech"  # tech, finance, world, business
    enabled: true
```

### 自定义摘要逻辑

修改 `src/ai_summarizer.py` 中的 `_build_category_prompt` 方法来自定义提示词。

## 📝 日志记录

程序会在当前目录生成 `news_summary.log` 文件记录运行日志。

## ⚠️ 注意事项

1. **API密钥安全**：确保API密钥的安全性，不要提交到版本控制系统
2. **OpenAI费用**：注意OpenAI API的使用配额和费用
3. **邮件配置**：邮件功能需要正确的SMTP权限设置
4. **网络连接**：确保能够访问RSS源和OpenAI API
5. **遵守条款**：遵守各新闻源的使用条款

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License