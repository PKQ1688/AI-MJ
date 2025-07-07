"""
LLM API服务类
与外部大语言模型服务的接口
"""

import json
import asyncio
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class LLMClient(ABC):
    """LLM客户端抽象基类"""

    @abstractmethod
    async def generate(self, prompt: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成LLM响应

        Args:
            prompt: 发送给LLM的提示

        Returns:
            LLM的响应
        """
        pass


class MockLLMClient(LLMClient):
    """
    模拟LLM客户端
    用于测试和开发
    """

    def __init__(self):
        self.response_count = 0

    async def generate(self, prompt: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成模拟响应
        """
        self.response_count += 1

        # 模拟网络延迟
        await asyncio.sleep(0.1)

        # 根据可能的动作生成响应
        possible_actions = prompt.get("possible_actions", [])

        if not possible_actions:
            return {"action": "PASS"}

        # 简单的决策逻辑
        if "HU" in possible_actions:
            return {"action": "HU"}
        elif "PONG" in possible_actions:
            return {"action": "PONG"}
        elif "GANG" in possible_actions:
            return {"action": "GANG"}
        elif "DISCARD" in [
            action for action in possible_actions if isinstance(action, str)
        ]:
            # 如果有出牌选项，随机选择一张牌
            my_info = prompt.get("my_info", {})
            hand_analysis = my_info.get("hand_analysis", {})
            sorted_hand = hand_analysis.get("sorted_hand", [])

            if sorted_hand:
                # 优先出孤张
                analysis = hand_analysis.get("analysis", {})
                isolated = analysis.get("isolated", [])
                if isolated:
                    return {"action": "DISCARD", "tile": isolated[0]}
                else:
                    return {"action": "DISCARD", "tile": sorted_hand[-1]}

        return {"action": "PASS"}


class OpenAIClient(LLMClient):
    """
    OpenAI API客户端
    """

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用OpenAI API生成响应
        """
        try:
            import openai

            # 构建系统消息
            system_message = self._build_system_message()

            # 构建用户消息
            user_message = json.dumps(prompt, ensure_ascii=False, indent=2)

            # 调用API
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.7,
                max_tokens=150,
            )

            # 解析响应
            content = response.choices[0].message.content.strip()
            return json.loads(content)

        except Exception as e:
            print(f"LLM API调用失败: {e}")
            # 返回默认动作
            return {"action": "PASS"}

    def _build_system_message(self) -> str:
        """构建系统消息"""
        return """你是一个四川麻将AI专家。你的目标是赢得游戏。

游戏规则：
- 四川血战到底麻将
- 不能吃牌（顺子）
- 必须缺一门才能胡牌
- 第一个胡牌后游戏继续

请根据提供的游戏状态和手牌分析，做出最佳决策。
你必须返回有效的JSON格式响应，包含action字段。

可能的动作：
- 出牌: {"action": "DISCARD", "tile": "五万"}
- 碰牌: {"action": "PONG"}
- 杠牌: {"action": "GANG"}
- 胡牌: {"action": "HU"}
- 过牌: {"action": "PASS"}
- 定缺: {"action": "LACK", "suit": "条"}"""


class ClaudeClient(LLMClient):
    """
    Claude API客户端
    """

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def generate(self, prompt: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用Claude API生成响应
        """
        try:
            import anthropic

            client = anthropic.AsyncAnthropic(api_key=self.api_key)

            # 构建消息
            system_message = self._build_system_message()
            user_message = json.dumps(prompt, ensure_ascii=False, indent=2)

            # 调用API
            response = await client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=150,
                temperature=0.7,
                system=system_message,
                messages=[{"role": "user", "content": user_message}],
            )

            # 解析响应
            content = response.content[0].text.strip()
            return json.loads(content)

        except Exception as e:
            print(f"Claude API调用失败: {e}")
            return {"action": "PASS"}

    def _build_system_message(self) -> str:
        """构建系统消息"""
        return """你是一个四川麻将AI专家。你的目标是赢得游戏。

游戏规则：
- 四川血战到底麻将
- 不能吃牌（顺子）
- 必须缺一门才能胡牌
- 第一个胡牌后游戏继续

请根据提供的游戏状态和手牌分析，做出最佳决策。
你必须返回有效的JSON格式响应，包含action字段。

可能的动作：
- 出牌: {"action": "DISCARD", "tile": "五万"}
- 碰牌: {"action": "PONG"}
- 杠牌: {"action": "GANG"}
- 胡牌: {"action": "HU"}
- 过牌: {"action": "PASS"}
- 定缺: {"action": "LACK", "suit": "条"}"""


def create_llm_client(client_type: str = "mock", **kwargs) -> LLMClient:
    """
    创建LLM客户端

    Args:
        client_type: 客户端类型 ("mock", "openai", "claude")
        **kwargs: 客户端特定参数

    Returns:
        LLM客户端实例
    """
    if client_type == "mock":
        return MockLLMClient()
    elif client_type == "openai":
        return OpenAIClient(kwargs.get("api_key"), kwargs.get("model", "gpt-3.5-turbo"))
    elif client_type == "claude":
        return ClaudeClient(kwargs.get("api_key"))
    else:
        raise ValueError(f"不支持的客户端类型: {client_type}")
