import openai
from typing import List, Dict
import logging
from news_fetcher import NewsArticle

logger = logging.getLogger(__name__)

class AISummarizer:
    """AI摘要生成器"""
    
    def __init__(self, config):
        self.config = config
        self.client = openai.OpenAI(api_key=config.get('openai.api_key'))
        self.model = config.get('openai.model', 'gpt-3.5-turbo')
        self.temperature = config.get('openai.temperature', 0.3)
        self.max_tokens = config.get('openai.max_tokens', 1000)
    
    def summarize_category(self, articles: List[NewsArticle], category: str) -> Dict[str, str]:
        """为特定分类生成摘要"""
        if not articles:
            return {'summary': '', 'key_points': []}
        
        try:
            # 准备输入文本
            articles_text = self._format_articles_for_prompt(articles)
            
            # 构造提示词
            prompt = self._build_category_prompt(articles_text, category)
            
            # 调用OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的新闻分析师，擅长总结和提炼关键信息。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            summary = response.choices[0].message.content.strip()
            
            # 提取关键要点
            key_points = self._extract_key_points(summary)
            
            logger.info(f"成功生成 {category} 分类摘要，长度: {len(summary)} 字符")
            
            return {
                'summary': summary,
                'key_points': key_points,
                'article_count': len(articles)
            }
            
        except Exception as e:
            logger.error(f"生成 {category} 分类摘要失败: {e}")
            return {
                'summary': f'生成 {category} 分类摘要时出现错误',
                'key_points': [],
                'article_count': len(articles)
            }
    
    def generate_daily_digest(self, category_summaries: Dict[str, Dict]) -> str:
        """生成每日综合摘要"""
        try:
            # 构造综合摘要提示词
            prompt = self._build_daily_digest_prompt(category_summaries)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的编辑，擅长整合多个领域的信息。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            digest = response.choices[0].message.content.strip()
            logger.info(f"成功生成每日综合摘要，长度: {len(digest)} 字符")
            
            return digest
            
        except Exception as e:
            logger.error(f"生成每日综合摘要失败: {e}")
            return "生成每日综合摘要时出现错误"
    
    def _format_articles_for_prompt(self, articles: List[NewsArticle]) -> str:
        """格式化文章用于提示词"""
        formatted = []
        for i, article in enumerate(articles[:5], 1):  # 限制最多5篇文章
            formatted.append(f"{i}. {article.title}\n   {article.content[:200]}...")
        return "\n\n".join(formatted)
    
    def _build_category_prompt(self, articles_text: str, category: str) -> str:
        """构建分类摘要提示词"""
        language = self.config.get('app.language', 'zh-CN')
        
        if language == 'zh-CN':
            prompt = f"""请为以下{category}类新闻生成中文摘要：

要求：
1. 总结主要事件和发展趋势
2. 提取3-5个关键要点
3. 保持客观中立的语调
4. 字数控制在200-300字之间

新闻内容：
{articles_text}

请以清晰简洁的方式总结这些新闻的主要内容。
"""
        else:
            prompt = f"""Please generate an English summary for the following {category} news:

Requirements:
1. Summarize the main events and trends
2. Extract 3-5 key points
3. Maintain objective tone
4. Keep within 150-250 words

News content:
{articles_text}

Please summarize the main content of these news in a clear and concise way.
"""
        
        return prompt
    
    def _build_daily_digest_prompt(self, category_summaries: Dict[str, Dict]) -> str:
        """构建每日综合摘要提示词"""
        language = self.config.get('app.language', 'zh-CN')
        
        # 整理各分类摘要
        category_texts = []
        for category, summary_data in category_summaries.items():
            if summary_data['summary']:
                category_texts.append(f"{category.upper()}分类:\n{summary_data['summary']}")
        
        combined_text = "\n\n".join(category_texts)
        
        if language == 'zh-CN':
            prompt = f"""请基于以下各分类新闻摘要，生成一份今日新闻综合报告：

要求：
1. 突出最重要的发展趋势
2. 识别跨领域的重要联系
3. 提供3-5个核心洞察
4. 字数控制在300-500字之间

各分类摘要：
{combined_text}

请生成一份连贯的每日新闻综述。
"""
        else:
            prompt = f"""Based on the following category summaries, please generate a comprehensive daily news report:

Requirements:
1. Highlight the most important trends
2. Identify cross-domain connections
3. Provide 3-5 key insights
4. Keep within 200-400 words

Category summaries:
{combined_text}

Please generate a coherent daily news overview.
"""
        
        return prompt
    
    def _extract_key_points(self, summary: str) -> List[str]:
        """从摘要中提取关键要点"""
        try:
            # 简单的关键点提取逻辑
            lines = summary.split('\n')
            key_points = []
            
            for line in lines:
                line = line.strip()
                # 寻找可能的要点标识
                if (line.startswith('- ') or line.startswith('* ') or 
                    line.startswith('• ') or (len(line) > 10 and ':' in line)):
                    key_points.append(line.lstrip('-*• '))
            
            # 如果没有找到明确的要点，返回前几行作为要点
            if not key_points:
                sentences = summary.split('。')[:3]
                key_points = [s.strip() + '。' for s in sentences if s.strip()]
            
            return key_points[:5]  # 最多返回5个要点
            
        except Exception as e:
            logger.debug(f"提取关键要点失败: {e}")
            return []