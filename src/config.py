"""
配置管理模块
"""

import os
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class LLMConfig:
    """LLM配置类"""

    def __init__(self):
        self.client_type = os.getenv("LLM_CLIENT_TYPE", "mock")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.deepseek_model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    def get_client_kwargs(self) -> dict:
        """获取客户端初始化参数"""
        if self.client_type == "openai":
            return {"api_key": self.openai_api_key, "model": self.openai_model}
        elif self.client_type == "claude":
            return {"api_key": self.anthropic_api_key}
        elif self.client_type == "deepseek":
            return {"api_key": self.deepseek_api_key, "model": self.deepseek_model}
        return {}

    def validate(self) -> bool:
        """验证配置是否有效"""
        if self.client_type == "openai" and not self.openai_api_key:
            return False
        if self.client_type == "claude" and not self.anthropic_api_key:
            return False
        if self.client_type == "deepseek" and not self.deepseek_api_key:
            return False
        return True


# 全局配置实例
llm_config = LLMConfig()
