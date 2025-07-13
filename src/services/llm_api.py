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


class DeepSeekClient(LLMClient):
    """
    DeepSeek API客户端
    """

    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.deepseek.com"

    async def generate(self, prompt: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用DeepSeek API生成响应
        """
        try:
            from openai import AsyncOpenAI

            # 创建客户端 - 简化版本，按照官方示例
            client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)

            # 构建系统消息和用户消息
            if isinstance(prompt, dict) and "role" in prompt:
                # 如果prompt是结构化的，使用其中的role作为系统消息
                system_message = prompt.get("role", self._build_system_message())
                user_message = json.dumps(prompt, ensure_ascii=False, indent=2)
            else:
                # 否则使用默认系统消息
                system_message = self._build_system_message()
                user_message = json.dumps(prompt, ensure_ascii=False, indent=2)

            # 调用API
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.7,
                max_tokens=150,
                stream=False,
            )

            # 解析响应
            content = response.choices[0].message.content.strip()
            print(f"DeepSeek API原始响应: {content}")  # 调试信息

            # 处理Markdown格式的JSON响应
            if content.startswith("```json"):
                # 提取JSON部分
                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                if json_start != -1 and json_end > json_start:
                    content = content[json_start:json_end]
            elif content.startswith("```"):
                # 处理其他代码块格式
                lines = content.split("\n")
                content = "\n".join(lines[1:-1])  # 去掉首尾的```行

            try:
                result = json.loads(content)
                print(f"成功解析JSON: {result}")  # 调试信息
            except json.JSONDecodeError:
                print(f"JSON解析失败，尝试提取动作...")
                # 如果JSON解析失败，尝试简单的文本解析
                content_upper = content.upper()

                # 尝试提取定缺动作
                if "缺万" in content or "LACK 万" in content_upper or "万" in content:
                    return {"action": "LACK", "suit": "万"}
                elif "缺筒" in content or "LACK 筒" in content_upper or "筒" in content:
                    return {"action": "LACK", "suit": "筒"}
                elif "缺条" in content or "LACK 条" in content_upper or "条" in content:
                    return {"action": "LACK", "suit": "条"}

                # 其他动作
                if "DISCARD" in content_upper:
                    return {"action": "DISCARD", "tile": "九万"}  # 默认出牌
                elif "PONG" in content_upper:
                    return {"action": "PONG"}
                elif "GANG" in content_upper:
                    return {"action": "GANG"}
                elif "HU" in content_upper:
                    return {"action": "HU"}
                else:
                    return {"action": "PASS"}

            return result

        except Exception as e:
            print(f"DeepSeek API调用失败: {e}")
            # 返回默认动作
            return {"action": "PASS"}

    def _build_system_message(self) -> str:
        """构建系统消息"""
        return """你是一个四川麻将AI专家。你的目标是赢得游戏。

重要规则：
1. 四川血战到底麻将规则
2. 不能吃牌（顺子），只能碰、杠
3. 必须缺一门才能胡牌（手牌中不能有缺门花色的牌）
4. 第一个胡牌后游戏继续

决策要求：
- 你必须根据提供的possible_actions列表选择一个合法动作
- 如果是你的回合且手牌超过13张，你必须出牌（DISCARD）
- 出牌时必须选择手牌中实际存在的牌
- 不能随意选择PASS，除非没有其他合法选择

响应格式：
你必须严格返回JSON格式响应，不要添加任何解释文字。只返回JSON对象：

定缺阶段：
{"action": "LACK", "suit": "万"}  // 选择缺万
{"action": "LACK", "suit": "筒"}  // 选择缺筒
{"action": "LACK", "suit": "条"}  // 选择缺条

游戏阶段：
{"action": "DISCARD", "tile": "五万"}  // 出牌
{"action": "PONG"}                    // 碰牌
{"action": "GANG"}                    // 杠牌
{"action": "HU"}                      // 胡牌
{"action": "PASS"}                    // 过牌

重要：只返回JSON，不要添加任何其他文字！"""


def create_llm_client(client_type: str = "mock", **kwargs) -> LLMClient:
    """
    创建LLM客户端

    Args:
        client_type: 客户端类型 ("mock", "openai", "claude", "deepseek")
        **kwargs: 客户端特定参数

    Returns:
        LLM客户端实例
    """
    import os
    from dotenv import load_dotenv

    # 加载环境变量
    load_dotenv()

    if client_type == "mock":
        return MockLLMClient()
    elif client_type == "openai":
        api_key = kwargs.get("api_key") or os.getenv("OPENAI_API_KEY")
        model = kwargs.get("model", "gpt-3.5-turbo")
        return OpenAIClient(api_key, model)
    elif client_type == "claude":
        api_key = kwargs.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
        return ClaudeClient(api_key)
    elif client_type == "deepseek":
        api_key = kwargs.get("api_key") or os.getenv("DEEPSEEK_API_KEY")
        model = kwargs.get("model") or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        return DeepSeekClient(api_key, model)
    else:
        raise ValueError(f"不支持的客户端类型: {client_type}")
