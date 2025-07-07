"""
游戏引擎类
驱动游戏流程，管理状态
"""

import asyncio
import random
from typing import List, Dict, Any, Optional
from ..core.tile import Tile
from ..core.meld import Meld
from ..core.action import Action
from ..player.llm_player import LLMPlayer
from ..utils.constants import (
    Suit,
    ActionType,
    MeldType,
    GamePhase,
    HAND_SIZE,
    TOTAL_TILES_PER_RANK,
    RANKS,
    SUITS_LIST,
)
from .rule_engine import RuleEngine
from ..ui.console_renderer import ConsoleRenderer


class Game:
    """
    游戏引擎类

    驱动游戏流程，管理状态
    """

    def __init__(
        self,
        players: List[LLMPlayer],
        renderer: ConsoleRenderer,
        debug_mode: bool = False,
    ):
        """
        初始化游戏

        Args:
            players: 玩家列表（必须是4个玩家）
            renderer: 渲染器
            debug_mode: 是否开启调试模式
        """
        if len(players) != 4:
            raise ValueError("四川麻将需要4个玩家")

        self.players = players
        self.renderer = renderer
        self.debug_mode = debug_mode

        # 游戏状态
        self.wall: List[Tile] = []
        self.current_player_id = 0
        self.phase = GamePhase.INIT
        self.round_number = 1

        # 游戏状态字典
        self.game_state: Dict[str, Any] = {
            "phase": self.phase.value,
            "current_player_id": self.current_player_id,
            "wall_remaining": 0,
            "discards": {str(i): [] for i in range(4)},
            "melds": {str(i): [] for i in range(4)},
            "last_action": None,
            "last_discard": None,
            "round": self.round_number,
            "debug_mode": debug_mode,
            "players": {},
        }

        self.rule_engine = RuleEngine()
        self.winners: List[int] = []

    async def run(self):
        """游戏主循环"""
        try:
            self.renderer.render_info("🎮 四川麻将游戏开始！")

            while self.phase != GamePhase.ENDED:
                await self._start_round()

                if self.phase == GamePhase.ENDED:
                    break

                # 可以在这里添加多轮游戏逻辑
                self.round_number += 1
                self.game_state["round"] = self.round_number

                # 为了演示，只玩一轮
                break

            self._end_game()

        except Exception as e:
            self.renderer.render_error(f"游戏运行出错: {e}")
            raise

    async def _start_round(self):
        """开始一轮游戏"""
        self.renderer.render_info(f"🔄 开始第{self.round_number}轮游戏")

        # 初始化
        self._initialize_round()

        # 洗牌发牌
        self._shuffle_and_deal()

        # 定缺阶段
        await self._lack_selection_phase()

        # 游戏阶段
        await self._playing_phase()

    def _initialize_round(self):
        """初始化一轮游戏"""
        self.phase = GamePhase.INIT
        self.current_player_id = 0
        self.winners.clear()

        # 重置玩家状态
        for player in self.players:
            player.reset_for_new_round()

        # 重置游戏状态
        self.game_state.update(
            {
                "phase": self.phase.value,
                "current_player_id": self.current_player_id,
                "discards": {str(i): [] for i in range(4)},
                "melds": {str(i): [] for i in range(4)},
                "last_action": None,
                "last_discard": None,
                "players": {},
            }
        )

    def _shuffle_and_deal(self):
        """洗牌和发牌"""
        # 创建牌墙
        self.wall = []
        for suit in SUITS_LIST:
            for rank in RANKS:
                for _ in range(TOTAL_TILES_PER_RANK):
                    self.wall.append(Tile(suit, rank))

        # 洗牌
        random.shuffle(self.wall)

        # 发牌
        for _ in range(HAND_SIZE):
            for player in self.players:
                if self.wall:
                    tile = self.wall.pop()
                    player.add_tile(tile)

        self.game_state["wall_remaining"] = len(self.wall)
        self.renderer.render_info("🃏 洗牌发牌完成")

    async def _lack_selection_phase(self):
        """定缺阶段"""
        self.phase = GamePhase.LACK_SELECTION
        self.game_state["phase"] = self.phase.value

        self.renderer.render_info("🚫 进入定缺阶段")

        # 更新玩家信息到游戏状态
        self._update_players_info()

        # 渲染当前状态
        self.renderer.render(self.game_state, self.players)

        # 每个玩家选择缺门
        for player in self.players:
            self.renderer.render_waiting_for_action(player, ["定缺"])

            action = await player.choose_lack(self.game_state)

            if action.action_type == ActionType.LACK and action.suit:
                player.set_lack_suit(action.suit)
                self.renderer.render_info(f"{player.name} 选择缺 {action.suit.value}")
            else:
                # 默认缺条
                player.set_lack_suit(Suit.TIAO)
                self.renderer.render_info(f"{player.name} 默认缺条")

        self.renderer.render_info("✅ 定缺阶段完成")

    async def _playing_phase(self):
        """游戏阶段"""
        self.phase = GamePhase.PLAYING
        self.game_state["phase"] = self.phase.value

        self.renderer.render_info("🎯 进入游戏阶段")

        turn_count = 0
        max_turns = 200  # 防止无限循环

        while self.phase == GamePhase.PLAYING and turn_count < max_turns:
            # 更新游戏状态
            self._update_game_state()

            # 渲染当前状态
            self.renderer.render(self.game_state, self.players)

            # 执行一个玩家的回合
            await self._game_turn()

            # 检查游戏是否结束
            if self._check_game_end():
                break

            turn_count += 1

        if turn_count >= max_turns:
            self.renderer.render_info("⏰ 游戏达到最大回合数，强制结束")

        self.phase = GamePhase.ENDED

    async def _game_turn(self):
        """执行一个玩家的回合"""
        current_player = self.players[self.current_player_id]

        # 摸牌（如果牌墙还有牌）
        if self.wall:
            new_tile = self.wall.pop()
            current_player.add_tile(new_tile)
            self.game_state["wall_remaining"] = len(self.wall)

            if self.debug_mode:
                self.renderer.render_info(f"{current_player.name} 摸到 {new_tile}")

        # 玩家决策
        self.renderer.render_waiting_for_action(current_player, ["出牌", "杠", "胡"])

        action = await current_player.decide_action(self.game_state)

        # 处理动作
        await self._process_action(action)

    async def _process_action(self, action: Action):
        """处理玩家动作"""
        current_player = self.players[self.current_player_id]

        # 验证动作
        if not self.rule_engine.is_valid_action(action, self.game_state):
            self.renderer.render_error(
                f"{current_player.name} 的动作 {action} 不合法，自动跳过"
            )
            action = Action(ActionType.PASS)

        # 记录动作
        self.game_state["last_action"] = {
            "player_id": self.current_player_id,
            "action": action.action_type.value,
            "tile": str(action.tile) if action.tile else "",
        }

        # 执行动作
        if action.action_type == ActionType.DISCARD:
            await self._handle_discard(action)
        elif action.action_type == ActionType.PONG:
            await self._handle_pong(action)
        elif action.action_type == ActionType.GANG:
            await self._handle_gang(action)
        elif action.action_type == ActionType.HU:
            await self._handle_hu(action)
        elif action.action_type == ActionType.PASS:
            await self._handle_pass(action)

        self.renderer.render_info(f"{current_player.name} {action}")

    async def _handle_discard(self, action: Action):
        """处理出牌"""
        current_player = self.players[self.current_player_id]

        if action.tile and current_player.remove_tile(action.tile):
            # 添加到弃牌池
            self.game_state["discards"][str(self.current_player_id)].append(
                str(action.tile)
            )
            self.game_state["last_discard"] = action.tile

            # 询问其他玩家是否要碰/杠/胡
            await self._ask_other_players_for_response(action.tile)

        # 轮到下一个玩家
        self._next_player()

    async def _handle_pong(self, action: Action):
        """处理碰牌"""
        # 简化实现
        self.renderer.render_info("碰牌功能待实现")

    async def _handle_gang(self, action: Action):
        """处理杠牌"""
        # 简化实现
        self.renderer.render_info("杠牌功能待实现")

    async def _handle_hu(self, action: Action):
        """处理胡牌"""
        current_player = self.players[self.current_player_id]
        self.winners.append(self.current_player_id)
        current_player.wins += 1

        self.renderer.render_info(f"🎉 {current_player.name} 胡牌了！")

        # 血战到底：游戏继续，但这里简化为结束
        self.phase = GamePhase.ENDED

    async def _handle_pass(self, action: Action):
        """处理过牌"""
        # 轮到下一个玩家
        self._next_player()

    async def _ask_other_players_for_response(self, discarded_tile: Tile):
        """询问其他玩家对弃牌的响应"""
        # 简化实现：暂时跳过
        pass

    def _next_player(self):
        """轮到下一个玩家"""
        self.current_player_id = (self.current_player_id + 1) % 4
        self.game_state["current_player_id"] = self.current_player_id

    def _update_game_state(self):
        """更新游戏状态"""
        self._update_players_info()

        # 更新副露信息
        for i, player in enumerate(self.players):
            self.game_state["melds"][str(i)] = [meld.to_dict() for meld in player.melds]

    def _update_players_info(self):
        """更新玩家信息到游戏状态"""
        for player in self.players:
            self.game_state["players"][str(player.player_id)] = {
                "hand": [tile for tile in player.hand],  # 保持Tile对象用于规则判断
                "melds": player.melds,
                "lack_suit": player.lack_suit,
            }

    def _check_game_end(self) -> bool:
        """检查游戏是否结束"""
        # 有人胡牌
        if self.winners:
            return True

        # 牌墙摸完
        if not self.wall:
            self.renderer.render_info("🧱 牌墙摸完，游戏结束")
            return True

        return False

    def _end_game(self):
        """结束游戏"""
        self.phase = GamePhase.ENDED
        self.game_state["phase"] = self.phase.value
        self.game_state["winners"] = self.winners

        self.renderer.render_game_end(self.game_state, self.players)
