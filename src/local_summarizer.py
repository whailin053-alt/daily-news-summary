import jieba
import re
from collections import Counter
from typing import List, Dict
import logging
from news_fetcher import NewsArticle

logger = logging.getLogger(__name__)

class LocalSummarizer:
    """本地摘要生成器（无需API密钥）"""
    
    def __init__(self, config):
        self.config = config
        # 初始化jieba分词
        jieba.initialize()
    
    def summarize_category(self, articles: List[NewsArticle], category: str) -> Dict[str, str]:
        """为特定分类生成本地摘要"""
        if not articles:
            return {'summary': '', 'key_points': []}
        
        try:
            # 提取关键词和生成摘要
            all_titles = [article.title for article in articles]
            all_contents = [article.content for article in articles]
            
            # 生成分类摘要
            summary = self._generate_category_summary(all_titles, all_contents, category)
            
            # 提取关键要点
            key_points = self._extract_key_points(all_titles, all_contents)
            
            logger.info(f"成功生成 {category} 分类本地摘要")
            
            return {
                'summary': summary,
                'key_points': key_points[:5],  # 最多5个要点
                'article_count': len(articles)
            }
            
        except Exception as e:
            logger.error(f"生成 {category} 分类摘要失败: {e}")
            # 返回默认摘要而不是错误信息
            default_summary = f"今日{category}领域共有{len(articles)}篇重要新闻，涵盖行业动态和技术发展。"
            return {
                'summary': default_summary,
                'key_points': [f"共收录{len(articles)}篇相关新闻"],
                'article_count': len(articles)
            }
    
    def generate_daily_digest(self, category_summaries: Dict[str, Dict]) -> str:
        """生成每日综合摘要"""
        try:
            # 收集所有分类的关键词
            all_keywords = []
            for category, summary_data in category_summaries.items():
                if summary_data['summary']:
                    # 从摘要中提取关键词
                    keywords = self._extract_keywords_from_text(summary_data['summary'])
                    all_keywords.extend(keywords)
            
            # 生成综合摘要
            if all_keywords:
                most_common = Counter(all_keywords).most_common(5)
                key_topics = [word for word, count in most_common]
                digest = f"今日重点关注领域：{'、'.join(key_topics)}。"
                
                # 添加各分类简要概述
                category_overviews = []
                for category, summary_data in category_summaries.items():
                    if summary_data['summary']:
                        # 提取摘要的第一句话
                        first_sentence = summary_data['summary'].split('。')[0]
                        category_overviews.append(f"{category}方面{first_sentence}")
                
                if category_overviews:
                    digest += "主要动态：" + "；".join(category_overviews[:3]) + "。"
            else:
                digest = "今日各领域均无重大新闻更新。"
            
            logger.info("成功生成每日综合摘要")
            return digest
            
        except Exception as e:
            logger.error(f"生成每日综合摘要失败: {e}")
            return "生成每日综合摘要时出现错误"
    
    def _generate_category_summary(self, titles: List[str], contents: List[str], category: str) -> str:
        """生成分类摘要"""
        # 合并所有标题和内容
        all_text = " ".join(titles) + " " + " ".join(contents[:3])  # 只取前3篇内容避免过长
        
        # 提取关键词
        keywords = self._extract_keywords_from_text(all_text)
        main_keywords = keywords[:3]
        
        # 根据分类生成不同的摘要模板
        category_templates = {
            'tech': f"科技领域今日关注{'、'.join(main_keywords)}等话题。主要涉及技术发展、产品更新和行业趋势。",
            'finance': f"财经领域聚焦{'、'.join(main_keywords)}等方面。涵盖市场动态、政策变化和企业资讯。",
            'world': f"国际新闻关注{'、'.join(main_keywords)}等议题。涉及全球政治、经济和社会发展。",
            'business': f"商业领域动态围绕{'、'.join(main_keywords)}展开。包括企业战略、市场分析和商业创新。"
        }
        
        # 使用对应分类的模板，如果没有匹配则使用通用模板
        template = category_templates.get(category, 
            f"本领域今日主要关注{'、'.join(main_keywords)}等{'、'.join(keywords[3:6])}相关话题。")
        
        return template
    
    def _extract_key_points(self, titles: List[str], contents: List[str]) -> List[str]:
        """提取关键要点"""
        key_points = []
        
        # 从标题中提取重要信息
        for title in titles[:5]:  # 只处理前5个标题
            # 移除常见的冗余词汇
            cleaned_title = re.sub(r'[【】《》（）()]', '', title)
            
            # 如果标题较长，可能是重要内容
            if len(cleaned_title) > 15:
                key_points.append(cleaned_title)
            elif any(keyword in cleaned_title for keyword in ['发布', '宣布', '推出', '完成', '达成']):
                key_points.append(cleaned_title)
        
        # 如果要点太少，从内容中补充
        if len(key_points) < 3:
            for content in contents[:2]:
                # 提取内容中的关键句子
                sentences = re.split(r'[。！？]', content)
                for sentence in sentences[:3]:
                    if len(sentence) > 20 and len(sentence) < 100:  # 适中长度的句子
                        # 检查是否包含重要词汇
                        if any(keyword in sentence for keyword in ['表示', '指出', '认为', '预计', '将']):
                            key_points.append(sentence.strip() + '。')
                            break
        
        return key_points[:5]  # 最多返回5个要点
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        # 使用jieba分词
        words = jieba.cut(text)
        
        # 过滤停用词和短词
        stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', 
                     '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', 
                     '自己', '这', '那', '里', '时候', '可以', '应该', '出来', '起来', '记者', '报道'}
        
        # 统计词频
        word_freq = Counter()
        for word in words:
            word = word.strip()
            if (len(word) >= 2 and 
                word not in stop_words and 
                not word.isdigit() and 
                not re.match(r'^[^\u4e00-\u9fa5]+$', word)):  # 不是纯英文
                word_freq[word] += 1
        
        # 返回高频词
        return [word for word, freq in word_freq.most_common(10)]

# 为了保持接口兼容性，创建一个包装类
class AISummarizer(LocalSummarizer):
    """AI摘要生成器（本地版）"""
    def __init__(self, config):
        super().__init__(config)
        logger.info("使用本地摘要功能（无需API密钥）")