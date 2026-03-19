import feedparser
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class NewsArticle:
    """新闻文章数据结构"""
    def __init__(self, title: str, content: str, url: str, 
                 published_date: datetime, source: str, category: str):
        self.title = title
        self.content = content
        self.url = url
        self.published_date = published_date
        self.source = source
        self.category = category
    
    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'content': self.content,
            'url': self.url,
            'published_date': self.published_date.isoformat(),
            'source': self.source,
            'category': self.category
        }

class NewsFetcher:
    """新闻获取器"""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DailyNewsAISummary/1.0'
        })
    
    def fetch_rss_news(self, source: Dict) -> List[NewsArticle]:
        """从RSS源获取新闻"""
        try:
            logger.info(f"正在获取RSS源: {source['name']}")
            feed = feedparser.parse(source['url'])
            
            articles = []
            max_articles = self.config.get('app.max_articles_per_source', 10)
            
            for entry in feed.entries[:max_articles]:
                # 过滤24小时内的新闻
                published_date = self._parse_date(entry.get('published'))
                if not published_date or (datetime.now() - published_date).days > 1:
                    continue
                
                article = NewsArticle(
                    title=entry.get('title', ''),
                    content=self._extract_content(entry),
                    url=entry.get('link', ''),
                    published_date=published_date,
                    source=source['name'],
                    category=source.get('category', 'general')
                )
                articles.append(article)
            
            logger.info(f"从 {source['name']} 获取到 {len(articles)} 篇文章")
            return articles
            
        except Exception as e:
            logger.error(f"获取RSS源失败 {source['name']}: {e}")
            return []
    
    def fetch_newsapi_news(self) -> List[NewsArticle]:
        """从NewsAPI获取新闻"""
        if not self.config.get('newsapi.enabled', False):
            return []
        
        try:
            api_key = self.config.get('newsapi.api_key')
            if not api_key:
                logger.warning("NewsAPI密钥未配置")
                return []
            
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            params = {
                'apiKey': api_key,
                'from': yesterday,
                'language': 'zh' if self.config.get('app.language') == 'zh-CN' else 'en',
                'sortBy': 'publishedAt'
            }
            
            response = self.session.get(
                'https://newsapi.org/v2/everything',
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for item in data.get('articles', [])[:20]:
                article = NewsArticle(
                    title=item.get('title', ''),
                    content=item.get('description', '') + ' ' + item.get('content', ''),
                    url=item.get('url', ''),
                    published_date=self._parse_date(item.get('publishedAt')),
                    source=item.get('source', {}).get('name', 'NewsAPI'),
                    category='general'
                )
                articles.append(article)
            
            logger.info(f"从NewsAPI获取到 {len(articles)} 篇文章")
            return articles
            
        except Exception as e:
            logger.error(f"获取NewsAPI新闻失败: {e}")
            return []
    
    def fetch_all_news(self) -> Dict[str, List[NewsArticle]]:
        """获取所有新闻并按分类组织"""
        all_articles = {}
        
        # 初始化分类
        for category in self.config.categories:
            all_articles[category] = []
        
        # 获取RSS新闻
        for source in self.config.rss_sources:
            articles = self.fetch_rss_news(source)
            category = source.get('category', 'general')
            if category in all_articles:
                all_articles[category].extend(articles)
        
        # 获取NewsAPI新闻
        newsapi_articles = self.fetch_newsapi_news()
        # 将NewsAPI文章分配到相应分类（这里简化处理）
        for article in newsapi_articles:
            if article.category in all_articles:
                all_articles[article.category].append(article)
        
        # 去重和排序
        for category in all_articles:
            all_articles[category] = self._deduplicate_and_sort(all_articles[category])
        
        return all_articles
    
    def _extract_content(self, entry) -> str:
        """提取文章内容"""
        # 优先级：content > summary > description
        content_fields = ['content', 'summary', 'description']
        for field in content_fields:
            content = entry.get(field, '')
            if content:
                # 如果是列表，取第一个元素
                if isinstance(content, list) and len(content) > 0:
                    content = content[0].get('value', '') if isinstance(content[0], dict) else str(content[0])
                return str(content)
        return ''
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """解析日期字符串"""
        if not date_str:
            return None
        
        try:
            # 尝试多种日期格式
            formats = [
                '%a, %d %b %Y %H:%M:%S %z',
                '%Y-%m-%dT%H:%M:%S%z',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d'
            ]
            
            for fmt in formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    # 如果没有时区信息，添加UTC时区
                    if parsed_date.tzinfo is None:
                        from datetime import timezone
                        parsed_date = parsed_date.replace(tzinfo=timezone.utc)
                    return parsed_date
                except ValueError:
                    continue
                    
        except Exception as e:
            logger.debug(f"日期解析失败: {date_str}, 错误: {e}")
        
        # 如果所有格式都失败，返回当前时间
        return datetime.now()
    
    def _deduplicate_and_sort(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """去重并按时间排序"""
        # 使用标题和URL进行去重
        seen = set()
        unique_articles = []
        
        for article in articles:
            identifier = f"{article.title}|{article.url}"
            if identifier not in seen:
                seen.add(identifier)
                unique_articles.append(article)
        
        # 按发布时间排序（最新的在前）
        return sorted(unique_articles, key=lambda x: x.published_date or datetime.min, reverse=True)