"""
规则引擎类
封装所有麻将规则的判断逻辑
"""

from typing import List, Dict, Any, Optional
from collections import Counter
from ..core.tile import Tile
from ..core.meld import Meld
from ..core.action import Action
from ..utils.constants import ActionType, Suit, MeldType


class RuleEngine:
    """
    规则引擎类

    提供静态方法用于规则判断
    """

    @staticmethod
    def is_valid_action(action: Action, game_state: Dict[str, Any]) -> bool:
        """
        验证一个动作在当前状态下是否合法

        Args:
            action: 要验证的动作
            game_state: 当前游戏状态

        Returns:
            是否合法
        """
        player_id = game_state.get("current_player_id")
        if player_id is None:
            return False

        player_info = game_state.get("players", {}).get(str(player_id), {})
        hand = player_info.get("hand", [])

        if action.action_type == ActionType.DISCARD:
            # 出牌：必须是手牌中的牌
            if action.tile is None:
                return False
            return action.tile in hand

        elif action.action_type == ActionType.PONG:
            # 碰牌：手牌中必须有2张相同的牌，且有人刚出了这张牌
            last_discard = game_state.get("last_discard")
            if last_discard is None:
                return False

            tile_count = sum(1 for tile in hand if tile == last_discard)
            return tile_count >= 2

        elif action.action_type == ActionType.GANG:
            # 杠牌：手牌中必须有3张相同的牌（明杠）或4张相同的牌（暗杠）
            if action.tile is None:
                return False

            tile_count = sum(1 for tile in hand if tile == action.tile)

            # 暗杠：手牌中有4张
            if tile_count == 4:
                return True

            # 明杠：手牌中有3张，且有人刚出了这张牌
            last_discard = game_state.get("last_discard")
            if last_discard == action.tile and tile_count == 3:
                return True

            # 补杠：已经碰了这张牌，手牌中还有1张
            melds = player_info.get("melds", [])
            has_pong = any(
                meld.meld_type == MeldType.PONG and meld.get_base_tile() == action.tile
                for meld in melds
            )
            if has_pong and tile_count == 1:
                return True

            return False

        elif action.action_type == ActionType.HU:
            # 胡牌：检查是否满足胡牌条件
            return RuleEngine.is_winning_hand(
                hand,
                player_info.get("melds", []),
                game_state.get("last_discard"),
                player_info.get("lack_suit"),
            )

        elif action.action_type == ActionType.PASS:
            # 过牌：总是合法的
            return True

        elif action.action_type == ActionType.LACK:
            # 定缺：只在定缺阶段有效
            return game_state.get("phase") == "LACK_SELECTION"

        return False

    @staticmethod
    def is_winning_hand(
        hand: List[Tile],
        melds: List[Meld],
        win_tile: Optional[Tile],
        lack_suit: Optional[Suit],
    ) -> bool:
        """
        判断是否满足胡牌条件

        Args:
            hand: 手牌
            melds: 已有的副露
            win_tile: 胡的牌（可能是自摸或点炮）
            lack_suit: 缺的花色

        Returns:
            是否可以胡牌
        """
        # 四川麻将胡牌基本条件：
        # 1. 必须缺一门
        # 2. 基本牌型：4个面子 + 1个对子
        # 3. 不能有缺门的牌

        if lack_suit is None:
            return False

        # 检查是否有缺门的牌
        full_hand = hand.copy()
        if win_tile:
            full_hand.append(win_tile)

        for tile in full_hand:
            if tile.suit == lack_suit:
                return False

        # 检查基本牌型
        return RuleEngine._check_basic_winning_pattern(full_hand, melds)

    @staticmethod
    def _check_basic_winning_pattern(hand: List[Tile], melds: List[Meld]) -> bool:
        """
        检查基本的胡牌牌型

        四川麻将：4个面子 + 1个对子
        面子可以是：刻子（3张相同）或已经副露的牌组
        """
        # 计算已有的面子数量
        meld_count = len(melds)

        # 剩余手牌需要组成的面子数量
        remaining_melds_needed = 4 - meld_count

        # 手牌应该是 remaining_melds_needed * 3 + 2 张（最后2张是对子）
        expected_hand_size = remaining_melds_needed * 3 + 2

        if len(hand) != expected_hand_size:
            return False

        # 尝试组合剩余手牌
        return RuleEngine._can_form_melds_and_pair(hand, remaining_melds_needed)

    @staticmethod
    def _can_form_melds_and_pair(hand: List[Tile], melds_needed: int) -> bool:
        """
        检查手牌是否能组成指定数量的面子和一个对子
        """
        if melds_needed == 0:
            # 只需要检查是否是一个对子
            return len(hand) == 2 and hand[0] == hand[1]

        tile_counter = Counter(hand)

        # 尝试所有可能的刻子组合
        return RuleEngine._try_form_melds(list(tile_counter.items()), melds_needed, 0)

    @staticmethod
    def _try_form_melds(
        tile_counts: List[tuple], melds_needed: int, current_index: int
    ) -> bool:
        """
        递归尝试组成面子
        """
        if melds_needed == 0:
            # 检查剩余的牌是否能组成一个对子
            remaining_tiles = []
            for tile, count in tile_counts:
                remaining_tiles.extend([tile] * count)
            return (
                len(remaining_tiles) == 2 and remaining_tiles[0] == remaining_tiles[1]
            )

        if current_index >= len(tile_counts):
            return False

        tile, count = tile_counts[current_index]

        # 尝试用这种牌组成刻子
        if count >= 3:
            # 使用3张组成刻子
            new_tile_counts = tile_counts.copy()
            new_tile_counts[current_index] = (tile, count - 3)
            if new_tile_counts[current_index][1] == 0:
                new_tile_counts.pop(current_index)
                return RuleEngine._try_form_melds(
                    new_tile_counts, melds_needed - 1, current_index
                )
            else:
                return RuleEngine._try_form_melds(
                    new_tile_counts, melds_needed - 1, current_index
                )

        # 不使用这种牌组成刻子，继续下一种牌
        return RuleEngine._try_form_melds(tile_counts, melds_needed, current_index + 1)

    @staticmethod
    def calculate_score(
        hand: List[Tile], melds: List[Meld], win_tile: Tile, is_self_drawn: bool
    ) -> int:
        """
        计算番数

        Args:
            hand: 手牌
            melds: 副露
            win_tile: 胡的牌
            is_self_drawn: 是否自摸

        Returns:
            番数
        """
        score = 1  # 基础番

        # 自摸加番
        if is_self_drawn:
            score += 1

        # 暗杠加番
        for meld in melds:
            if meld.meld_type == MeldType.AN_GANG:
                score += 2
            elif meld.meld_type in [MeldType.MING_GANG, MeldType.BU_GANG]:
                score += 1

        # 其他番型判断可以在这里扩展

        return score

    @staticmethod
    def get_possible_actions(
        player_hand: List[Tile], game_state: Dict[str, Any]
    ) -> List[Action]:
        """
        找出当前所有可能的合法操作

        Args:
            player_hand: 玩家手牌
            game_state: 游戏状态

        Returns:
            可能的动作列表
        """
        possible_actions = []
        current_player = game_state.get("current_player_id")
        player_id = game_state.get("asking_player_id", current_player)

        # 如果是自己的回合
        if current_player == player_id:
            # 如果手牌超过13张，必须出牌，不能过
            if len(player_hand) > 13:
                # 只能出牌或暗杠，不能过
                for tile in set(player_hand):  # 使用set避免重复
                    possible_actions.append(Action(ActionType.DISCARD, tile))

                # 检查是否可以暗杠
                tile_counter = Counter(player_hand)
                for tile, count in tile_counter.items():
                    if count == 4:
                        possible_actions.append(Action(ActionType.GANG, tile))
            else:
                # 手牌正常时，可以过牌
                possible_actions.append(Action(ActionType.PASS))
        else:
            # 不是自己的回合，总是可以过牌
            possible_actions.append(Action(ActionType.PASS))

        # 检查是否可以碰、明杠、胡
        last_discard = game_state.get("last_discard")
        if last_discard and current_player != player_id:
            tile_counter = Counter(player_hand)
            discard_count = tile_counter.get(last_discard, 0)

            # 可以碰
            if discard_count >= 2:
                possible_actions.append(Action(ActionType.PONG))

            # 可以明杠
            if discard_count >= 3:
                possible_actions.append(Action(ActionType.GANG, last_discard))

            # 可以胡
            player_info = game_state.get("players", {}).get(str(player_id), {})
            if RuleEngine.is_winning_hand(
                player_hand,
                player_info.get("melds", []),
                last_discard,
                player_info.get("lack_suit"),
            ):
                possible_actions.append(Action(ActionType.HU))

        return possible_actions
