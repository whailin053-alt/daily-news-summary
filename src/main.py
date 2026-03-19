#!/usr/bin/env python3
"""
每日新闻AI摘要工具
Daily News AI Summary Tool
"""

import click
import logging
import schedule
import time
from datetime import datetime
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from news_fetcher import NewsFetcher
from local_summarizer import AISummarizer
from reporter import Reporter
from email_sender import EmailSender

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('news_summary.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@click.command()
@click.option('--config', '-c', default='config/config.yaml', help='配置文件路径')
@click.option('--once', '-o', is_flag=True, help='只运行一次，不调度')
@click.option('--schedule-time', '-t', default='09:00', help='调度执行时间 (HH:MM)')
@click.option('--verbose', '-v', is_flag=True, help='详细输出')
def main(config, once, schedule_time, verbose):
    """每日新闻AI摘要工具主程序"""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # 加载配置
        cfg = Config(config)
        logger.info("配置加载成功")
        
        if once:
            # 单次执行模式
            logger.info("开始单次执行模式")
            run_once(cfg)
        else:
            # 调度执行模式
            logger.info(f"启动调度模式，每天 {schedule_time} 执行")
            schedule_daily_run(cfg, schedule_time)
            
    except Exception as e:
        logger.error(f"程序执行出错: {e}")
        sys.exit(1)

def run_once(config):
    """执行一次完整的新闻摘要流程"""
    try:
        start_time = datetime.now()
        logger.info("开始执行新闻摘要任务")
        
        # 1. 获取新闻
        logger.info("步骤1: 获取新闻...")
        fetcher = NewsFetcher(config)
        all_articles = fetcher.fetch_all_news()
        
        total_articles = sum(len(articles) for articles in all_articles.values())
        logger.info(f"共获取到 {total_articles} 篇新闻")
        
        if total_articles == 0:
            logger.warning("未获取到任何新闻，程序退出")
            return
        
        # 2. AI摘要生成
        logger.info("步骤2: 生成AI摘要...")
        summarizer = AISummarizer(config)
        
        category_summaries = {}
        for category, articles in all_articles.items():
            if articles:
                logger.info(f"正在处理 {category} 分类 ({len(articles)} 篇文章)")
                category_summaries[category] = summarizer.summarize_category(articles, category)
            else:
                category_summaries[category] = {'summary': '', 'key_points': [], 'article_count': 0}
        
        # 3. 生成每日综合摘要
        logger.info("步骤3: 生成每日综合摘要...")
        daily_digest = summarizer.generate_daily_digest(category_summaries)
        
        # 4. 生成报告
        logger.info("步骤4: 生成报告...")
        reporter = Reporter(config)
        report_file = reporter.generate_markdown_report(category_summaries, daily_digest, all_articles)
        
        # 5. 发送邮件（如果启用）
        logger.info("步骤5: 发送邮件...")
        email_sender = EmailSender(config)
        email_success = email_sender.send_daily_report(report_file, "🤖 ")
        
        # 记录结果
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 50)
        logger.info("任务完成!")
        logger.info(f"执行时间: {duration:.2f} 秒")
        logger.info(f"报告文件: {report_file}")
        logger.info(f"邮件发送: {'成功' if email_success else '失败'}")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"执行过程中出现错误: {e}")
        raise

def schedule_daily_run(config, schedule_time):
    """调度每日执行"""
    def job():
        try:
            run_once(config)
        except Exception as e:
            logger.error(f"调度任务执行失败: {e}")
    
    # 设置调度
    schedule.every().day.at(schedule_time).do(job)
    
    logger.info(f"调度已设置，将在每天 {schedule_time} 执行")
    logger.info("按 Ctrl+C 停止程序")
    
    # 保持程序运行
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        logger.info("程序已停止")

if __name__ == '__main__':
    main()