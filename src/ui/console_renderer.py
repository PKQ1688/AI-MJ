"""
控制台渲染器
负责在控制台显示游戏状态
"""

import os
from typing import Dict, Any, List
from ..core.tile import Tile
from ..core.meld import Meld
from ..player.llm_player import LLMPlayer


class ConsoleRenderer:
    """
    控制台渲染器类

    负责在控制台显示游戏状态
    """

    def __init__(self):
        self.width = 80
        self.separator = "=" * self.width

    def render(self, game_state: Dict[str, Any], players: List[LLMPlayer]):
        """
        渲染游戏状态

        Args:
            game_state: 游戏状态
            players: 玩家列表
        """
        self.clear_screen()

        print(self.separator)
        print("🀄️  四川麻将 - 血战到底  🀄️".center(self.width))
        print(self.separator)

        # 显示游戏基本信息
        self._render_game_info(game_state)

        # 显示玩家信息
        self._render_players_info(players, game_state)

        # 显示弃牌池
        self._render_discards(game_state)

        # 显示最近动作
        self._render_last_action(game_state)

        print(self.separator)

    def clear_screen(self):
        """清屏"""
        os.system("cls" if os.name == "nt" else "clear")

    def _render_game_info(self, game_state: Dict[str, Any]):
        """渲染游戏基本信息"""
        phase = game_state.get("phase", "UNKNOWN")
        current_player = game_state.get("current_player_id", 0)
        wall_remaining = game_state.get("wall_remaining", 0)
        round_num = game_state.get("round", 1)

        print(f"🎮 游戏阶段: {self._get_phase_name(phase)}")
        print(f"🎯 当前玩家: 玩家{current_player}")
        print(f"🧱 剩余牌数: {wall_remaining}")
        print(f"🔄 第{round_num}轮")
        print()

    def _get_phase_name(self, phase: str) -> str:
        """获取阶段中文名称"""
        phase_names = {
            "INIT": "初始化",
            "LACK_SELECTION": "定缺阶段",
            "PLAYING": "游戏进行中",
            "ENDED": "游戏结束",
        }
        return phase_names.get(phase, phase)

    def _render_players_info(
        self, players: List[LLMPlayer], game_state: Dict[str, Any]
    ):
        """渲染玩家信息"""
        print("👥 玩家信息:")
        print("-" * self.width)

        current_player_id = game_state.get("current_player_id", 0)

        for player in players:
            is_current = player.player_id == current_player_id
            marker = "👉 " if is_current else "   "

            print(f"{marker}玩家{player.player_id} ({player.name})")

            # 显示手牌数量
            hand_count = len(player.hand)
            print(f"    🃏 手牌: {hand_count}张")

            # 显示缺门
            if player.lack_suit:
                print(f"    🚫 缺门: {player.lack_suit.value}")

            # 显示副露
            if player.melds:
                melds_str = ", ".join([str(meld) for meld in player.melds])
                print(f"    🔓 副露: {melds_str}")

            # 如果是当前玩家，显示详细手牌（仅用于调试）
            if is_current and game_state.get("debug_mode", False):
                hand_str = " ".join([str(tile) for tile in sorted(player.hand)])
                print(f"    🎴 手牌详情: {hand_str}")

            print()

    def _render_discards(self, game_state: Dict[str, Any]):
        """渲染弃牌池"""
        discards = game_state.get("discards", {})

        if not any(discards.values()):
            return

        print("🗑️  弃牌池:")
        print("-" * self.width)

        for player_id, player_discards in discards.items():
            if player_discards:
                discards_str = " ".join(player_discards)
                print(f"玩家{player_id}: {discards_str}")

        print()

    def _render_last_action(self, game_state: Dict[str, Any]):
        """渲染最近的动作"""
        last_action = game_state.get("last_action")

        if not last_action:
            return

        print("📝 最近动作:")
        print("-" * self.width)

        player_id = last_action.get("player_id", "?")
        action = last_action.get("action", "?")
        tile = last_action.get("tile", "")

        action_text = self._get_action_text(action, tile)
        print(f"玩家{player_id}: {action_text}")
        print()

    def _get_action_text(self, action: str, tile: str = "") -> str:
        """获取动作的中文描述"""
        action_texts = {
            "DISCARD": f"出牌 {tile}",
            "PONG": f"碰 {tile}",
            "GANG": f"杠 {tile}",
            "HU": "胡牌",
            "PASS": "过",
            "LACK": f"定缺 {tile}",
        }
        return action_texts.get(action, f"{action} {tile}")

    def render_game_end(self, game_state: Dict[str, Any], players: List[LLMPlayer]):
        """渲染游戏结束画面"""
        self.clear_screen()

        print(self.separator)
        print("🎉  游戏结束  🎉".center(self.width))
        print(self.separator)

        # 显示最终结果
        winners = game_state.get("winners", [])
        if winners:
            print("🏆 获胜者:")
            for winner_id in winners:
                winner = next((p for p in players if p.player_id == winner_id), None)
                if winner:
                    print(f"   🥇 {winner.name} (玩家{winner_id})")

        print()

        # 显示玩家统计
        print("📊 游戏统计:")
        print("-" * self.width)

        for player in players:
            stats = player.get_stats()
            print(f"{player.name}:")
            print(f"   决策次数: {stats['decisions_made']}")
            print(f"   获胜次数: {stats['wins']}")
            print()

        print(self.separator)

    def render_waiting_for_action(self, player: LLMPlayer, possible_actions: List[str]):
        """渲染等待玩家动作的提示"""
        print(f"⏳ 等待 {player.name} 做出决策...")
        if possible_actions:
            actions_str = ", ".join(possible_actions)
            print(f"   可选动作: {actions_str}")
        print()

    def render_error(self, message: str):
        """渲染错误信息"""
        print(f"❌ 错误: {message}")
        print()

    def render_info(self, message: str):
        """渲染信息"""
        print(f"ℹ️  {message}")
        print()

    def pause(self, message: str = "按回车键继续..."):
        """暂停等待用户输入"""
        input(message)
