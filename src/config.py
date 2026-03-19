import os
import yaml
from typing import Dict, List, Any
from pathlib import Path
from dotenv import load_dotenv

class Config:
    """配置管理类"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        # 加载环境变量
        load_dotenv()
        
        # 加载YAML配置
        self.config_path = Path(config_path)
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
            
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 替换环境变量占位符
        self._resolve_env_vars(self.config)
    
    def _resolve_env_vars(self, data: Any) -> Any:
        """递归解析环境变量"""
        if isinstance(data, dict):
            return {k: self._resolve_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._resolve_env_vars(item) for item in data]
        elif isinstance(data, str) and data.startswith("${") and data.endswith("}"):
            env_var = data[2:-1]
            return os.getenv(env_var, data)
        else:
            return data
    
    def get(self, key_path: str, default=None):
        """获取配置值，支持点号分隔的路径"""
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    @property
    def rss_sources(self) -> List[Dict]:
        """获取启用的RSS源"""
        sources = self.get('rss_sources', [])
        return [source for source in sources if source.get('enabled', True)]
    
    @property
    def categories(self) -> List[str]:
        """获取配置的分类"""
        return self.get('app.categories', ['tech', 'finance', 'world'])