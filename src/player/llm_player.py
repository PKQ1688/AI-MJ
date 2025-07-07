"""
LLM玩家类
实现AI玩家的决策逻辑
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from ..core.tile import Tile
from ..core.meld import Meld
from ..core.action import Action
from ..utils.constants import Suit, ActionType
from .hand_analyzer import HandAnalyzer
from ..services.llm_api import LLMClient


class LLMPlayer:
    """
    LLM玩家类

    代表一个AI玩家，负责调用LLM API获取决策
    """

    def __init__(
        self, player_id: int, llm_client: LLMClient, name: Optional[str] = None
    ):
        """
        初始化LLM玩家

        Args:
            player_id: 玩家ID
            llm_client: LLM客户端
            name: 玩家名称
        """
        self.player_id = player_id
        self.name = name or f"AI玩家{player_id}"
        self.hand: List[Tile] = []
        self.melds: List[Meld] = []
        self.lack_suit: Optional[Suit] = None
        self.llm_client = llm_client
        self.hand_analyzer = HandAnalyzer()

        # 统计信息
        self.decisions_made = 0
        self.wins = 0

    def add_tile(self, tile: Tile):
        """添加牌到手牌"""
        self.hand.append(tile)

    def remove_tile(self, tile: Tile) -> bool:
        """
        从手牌中移除牌

        Returns:
            是否成功移除
        """
        if tile in self.hand:
            self.hand.remove(tile)
            return True
        return False

    def add_meld(self, meld: Meld):
        """添加副露"""
        self.melds.append(meld)

    def set_lack_suit(self, suit: Suit):
        """设置缺门花色"""
        self.lack_suit = suit

    async def decide_action(self, game_state: Dict[str, Any]) -> Action:
        """
        决定下一步动作

        Args:
            game_state: 游戏状态

        Returns:
            决定的动作
        """
        try:
            # 分析手牌
            analysis_data = self.hand_analyzer.analyze(self.hand)

            # 构建提示
            prompt = self._build_prompt(game_state, analysis_data)

            # 调用LLM
            response = await self.llm_client.generate(prompt)

            # 解析响应
            action = self._parse_response(response)

            self.decisions_made += 1
            return action

        except Exception as e:
            print(f"玩家{self.player_id}决策失败: {e}")
            # 返回默认动作
            return Action(ActionType.PASS)

    async def choose_lack(self, game_state: Dict[str, Any]) -> Action:
        """
        选择缺门花色

        Args:
            game_state: 游戏状态

        Returns:
            定缺动作
        """
        try:
            # 分析手牌
            analysis_data = self.hand_analyzer.analyze(self.hand)

            # 构建定缺提示
            prompt = self._build_lack_prompt(game_state, analysis_data)

            # 调用LLM
            response = await self.llm_client.generate(prompt)

            # 解析响应
            action = self._parse_response(response)

            if action.action_type == ActionType.LACK and action.suit:
                self.set_lack_suit(action.suit)

            return action

        except Exception as e:
            print(f"玩家{self.player_id}定缺失败: {e}")
            # 默认缺条
            self.set_lack_suit(Suit.TIAO)
            return Action(ActionType.LACK, suit=Suit.TIAO)

    def _build_prompt(
        self, game_state: Dict[str, Any], analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """构建LLM提示"""
        # 获取可能的动作
        from ..engine.rule_engine import RuleEngine

        possible_actions = RuleEngine.get_possible_actions(self.hand, game_state)

        prompt = {
            "role": "You are a Sichuan Mahjong AI expert. Your goal is to win. You must respond in a valid JSON format.",
            "rules": {
                "variant": "Sichuan Blood-Bath (血战到底)",
                "notes": [
                    "No CHOW (吃)",
                    "Must have a LACK SUIT (缺一门) to win",
                    "Game continues after first win",
                ],
            },
            "game_state": {
                "current_player_id": game_state.get("current_player_id"),
                "wall_remaining": game_state.get("wall_remaining", 0),
                "discards": game_state.get("discards", {}),
                "melds": game_state.get("melds", {}),
                "phase": game_state.get("phase", "PLAYING"),
            },
            "my_info": {
                "player_id": self.player_id,
                "lack_suit": self.lack_suit.value if self.lack_suit else None,
                "hand_analysis": analysis_data,
                "melds": [meld.to_dict() for meld in self.melds],
            },
            "last_action": game_state.get("last_action"),
            "possible_actions": [
                action.action_type.value for action in possible_actions
            ],
        }

        return prompt

    def _build_lack_prompt(
        self, game_state: Dict[str, Any], analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """构建定缺提示"""
        prompt = {
            "role": "You are choosing which suit to lack in Sichuan Mahjong. Choose wisely based on your hand.",
            "rules": {
                "variant": "Sichuan Blood-Bath (血战到底)",
                "notes": [
                    "You must choose one suit to lack",
                    "You cannot win with tiles of the lacking suit",
                ],
            },
            "my_info": {"player_id": self.player_id, "hand_analysis": analysis_data},
            "possible_actions": ["LACK"],
            "suits_to_choose": ["万", "筒", "条"],
        }

        return prompt

    def _parse_response(self, response: Dict[str, Any]) -> Action:
        """
        解析LLM响应

        Args:
            response: LLM响应

        Returns:
            解析出的动作
        """
        try:
            action_type_str = response.get("action", "PASS")
            action_type = ActionType(action_type_str)

            tile = None
            if "tile" in response and response["tile"]:
                tile = Tile.from_string(response["tile"])

            suit = None
            if "suit" in response and response["suit"]:
                suit = Suit(response["suit"])

            return Action(action_type, tile, suit)

        except Exception as e:
            print(f"解析LLM响应失败: {e}, 响应: {response}")
            return Action(ActionType.PASS)

    def get_hand_info(self) -> Dict[str, Any]:
        """获取手牌信息"""
        return {
            "hand": [str(tile) for tile in self.hand],
            "hand_count": len(self.hand),
            "melds": [meld.to_dict() for meld in self.melds],
            "lack_suit": self.lack_suit.value if self.lack_suit else None,
        }

    def get_stats(self) -> Dict[str, Any]:
        """获取玩家统计信息"""
        return {
            "player_id": self.player_id,
            "name": self.name,
            "decisions_made": self.decisions_made,
            "wins": self.wins,
            "win_rate": self.wins / max(1, self.decisions_made) * 100,
        }

    def reset_for_new_round(self):
        """为新一轮重置玩家状态"""
        self.hand.clear()
        self.melds.clear()
        self.lack_suit = None

    def __str__(self) -> str:
        """返回玩家的字符串表示"""
        return f"{self.name}(ID:{self.player_id})"

    def __repr__(self) -> str:
        """返回玩家的详细表示"""
        return f"LLMPlayer(id={self.player_id}, name='{self.name}', hand_size={len(self.hand)})"
