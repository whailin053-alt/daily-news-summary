from datetime import datetime
from typing import Dict, List
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Reporter:
    """报告生成器"""
    
    def __init__(self, config):
        self.config = config
        self.output_dir = Path(config.get('app.output_dir', './output'))
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_markdown_report(self, category_summaries: Dict[str, Dict], 
                               daily_digest: str, 
                               all_articles: Dict[str, List]) -> str:
        """生成Markdown格式的日报"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            filename = f"daily_news_{today}.md"
            filepath = self.output_dir / filename
            
            # 生成Markdown内容
            markdown_content = self._build_markdown_content(
                category_summaries, daily_digest, all_articles, today
            )
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"日报已保存至: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"生成Markdown报告失败: {e}")
            raise
    
    def _build_markdown_content(self, category_summaries: Dict[str, Dict], 
                              daily_digest: str, 
                              all_articles: Dict[str, List],
                              date_str: str) -> str:
        """构建Markdown内容"""
        language = self.config.get('app.language', 'zh-CN')
        
        if language == 'zh-CN':
            content = self._build_chinese_markdown(category_summaries, daily_digest, all_articles, date_str)
        else:
            content = self._build_english_markdown(category_summaries, daily_digest, all_articles, date_str)
        
        return content
    
    def _build_chinese_markdown(self, category_summaries: Dict[str, Dict], 
                              daily_digest: str, 
                              all_articles: Dict[str, List],
                              date_str: str) -> str:
        """构建中文Markdown"""
        lines = []
        
        # 标题
        lines.append(f"# 📰 每日新闻摘要 - {date_str}")
        lines.append("")
        lines.append(f"*更新时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}*")
        lines.append("")
        
        # 目录
        lines.append("## 📋 目录")
        lines.append("")
        lines.append("- [今日概览](#今日概览)")
        
        category_names = {
            'tech': '💻 科技',
            'finance': '💰 金融',
            'world': '🌍 国际',
            'business': '🏢 商业',
            'general': '📰 综合'
        }
        
        for category in self.config.categories:
            if category in category_summaries and category_summaries[category]['summary']:
                display_name = category_names.get(category, category)
                lines.append(f"- [{display_name}](#{category})")
        
        lines.append("")
        
        # 今日概览
        lines.append("## 🎯 今日概览")
        lines.append("")
        if daily_digest:
            lines.append(daily_digest)
        else:
            lines.append("今日暂无重要新闻摘要。")
        lines.append("")
        
        # 各分类详情
        for category in self.config.categories:
            if category not in category_summaries or not category_summaries[category]['summary']:
                continue
                
            summary_data = category_summaries[category]
            display_name = category_names.get(category, category)
            
            lines.append(f"## <a name=\"{category}\"></a>{display_name}")
            lines.append("")
            
            # 分类摘要
            lines.append("### 📝 摘要")
            lines.append("")
            lines.append(summary_data['summary'])
            lines.append("")
            
            # 关键要点
            if summary_data['key_points']:
                lines.append("### 🔑 关键要点")
                lines.append("")
                for point in summary_data['key_points']:
                    lines.append(f"- {point}")
                lines.append("")
            
            # 相关文章
            if category in all_articles and all_articles[category]:
                lines.append("### 📚 相关文章")
                lines.append("")
                for i, article in enumerate(all_articles[category][:5], 1):
                    lines.append(f"{i}. [{article.title}]({article.url})")
                    lines.append(f"   *来源: {article.source} | {article.published_date.strftime('%m-%d %H:%M')}*")
                    lines.append("")
            
            lines.append("---")
            lines.append("")
        
        # 页脚
        lines.append("## ℹ️ 关于")
        lines.append("")
        lines.append("本报告由AI自动生成，仅供参考。如需了解更多信息，请访问原始新闻链接。")
        
        return '\n'.join(lines)
    
    def _build_english_markdown(self, category_summaries: Dict[str, Dict], 
                              daily_digest: str, 
                              all_articles: Dict[str, List],
                              date_str: str) -> str:
        """构建英文Markdown"""
        lines = []
        
        # Title
        lines.append(f"# 📰 Daily News Summary - {date_str}")
        lines.append("")
        lines.append(f"*Updated: {datetime.now().strftime('%B %d, %Y %H:%M')}*")
        lines.append("")
        
        # Table of Contents
        lines.append("## 📋 Table of Contents")
        lines.append("")
        lines.append("- [Today's Overview](#todays-overview)")
        
        for category in self.config.categories:
            if category in category_summaries and category_summaries[category]['summary']:
                lines.append(f"- [{category.capitalize()}](#{category})")
        
        lines.append("")
        
        # Today's Overview
        lines.append("## 🎯 Today's Overview")
        lines.append("")
        if daily_digest:
            lines.append(daily_digest)
        else:
            lines.append("No significant news summary available today.")
        lines.append("")
        
        # Category Details
        for category in self.config.categories:
            if category not in category_summaries or not category_summaries[category]['summary']:
                continue
                
            summary_data = category_summaries[category]
            
            lines.append(f"## <a name=\"{category}\"></a>{category.capitalize()}")
            lines.append("")
            
            # Summary
            lines.append("### 📝 Summary")
            lines.append("")
            lines.append(summary_data['summary'])
            lines.append("")
            
            # Key Points
            if summary_data['key_points']:
                lines.append("### 🔑 Key Points")
                lines.append("")
                for point in summary_data['key_points']:
                    lines.append(f"- {point}")
                lines.append("")
            
            # Related Articles
            if category in all_articles and all_articles[category]:
                lines.append("### 📚 Related Articles")
                lines.append("")
                for i, article in enumerate(all_articles[category][:5], 1):
                    lines.append(f"{i}. [{article.title}]({article.url})")
                    lines.append(f"   *Source: {article.source} | {article.published_date.strftime('%m-%d %H:%M')}*")
                    lines.append("")
            
            lines.append("---")
            lines.append("")
        
        # Footer
        lines.append("## ℹ️ About")
        lines.append("")
        lines.append("This report is automatically generated by AI for reference purposes only. Please visit the original news links for more information.")
        
        return '\n'.join(lines)