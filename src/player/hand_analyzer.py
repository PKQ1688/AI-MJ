"""
理牌工具类
专门为LLM设计的核心工具，将手牌转换成结构化信息
"""

from typing import List, Dict, Any, Set, Tuple
from collections import Counter
from ..core.tile import Tile
from ..core.meld import Meld
from ..utils.constants import Suit, SUITS_LIST


class HandAnalyzer:
    """
    理牌工具类

    将一手杂乱的牌转换成富有洞察力的结构化信息
    """

    def analyze(self, hand: List[Tile]) -> Dict[str, Any]:
        """
        执行完整的手牌分析

        Args:
            hand: 手牌列表

        Returns:
            包含分析结果的字典
        """
        # 排序手牌
        sorted_hand = sorted(hand)

        # 按花色分组
        suits_info = self._group_by_suits(sorted_hand)

        # 分析牌型
        analysis = self._analyze_patterns(sorted_hand)

        # 分析听牌信息
        ting_info = self._find_ting(sorted_hand)

        return {
            "sorted_hand": [str(tile) for tile in sorted_hand],
            "suits": suits_info,
            "analysis": {
                "pairs": analysis["pairs"],
                "triplets": analysis["triplets"],
                "sequences": analysis["sequences"],
                "isolated": analysis["isolated"],
                "ting_info": ting_info,
            },
        }

    def _group_by_suits(self, hand: List[Tile]) -> Dict[str, Dict[str, Any]]:
        """按花色分组手牌"""
        suits_info = {}

        for suit in SUITS_LIST:
            suit_tiles = [tile for tile in hand if tile.suit == suit]
            suits_info[suit.value] = {
                "tiles": [str(tile) for tile in suit_tiles],
                "count": len(suit_tiles),
                "ranks": sorted([tile.rank for tile in suit_tiles]),
            }

        return suits_info

    def _analyze_patterns(self, hand: List[Tile]) -> Dict[str, List[str]]:
        """分析手牌中的牌型模式"""
        tile_counter = Counter(hand)

        pairs = []  # 对子
        triplets = []  # 刻子
        sequences = []  # 顺子（虽然四川麻将不能吃，但可以分析潜在顺子）
        isolated = []  # 孤张

        # 找对子和刻子
        for tile, count in tile_counter.items():
            if count >= 2:
                pairs.append(str(tile))
            if count >= 3:
                triplets.append(str(tile))

        # 找潜在顺子
        sequences = self._find_potential_sequences(hand)

        # 找孤张
        for tile, count in tile_counter.items():
            if count == 1:
                # 检查是否能形成顺子
                if not self._is_part_of_sequence(tile, hand):
                    isolated.append(str(tile))

        return {
            "pairs": pairs,
            "triplets": triplets,
            "sequences": sequences,
            "isolated": isolated,
        }

    def _find_potential_sequences(self, hand: List[Tile]) -> List[str]:
        """找出潜在的顺子"""
        sequences = []

        for suit in SUITS_LIST:
            suit_tiles = [tile for tile in hand if tile.suit == suit]
            suit_ranks = sorted(set(tile.rank for tile in suit_tiles))

            # 查找连续的3张牌
            for i in range(len(suit_ranks) - 2):
                if (
                    suit_ranks[i + 1] == suit_ranks[i] + 1
                    and suit_ranks[i + 2] == suit_ranks[i] + 2
                ):
                    seq_str = f"{suit_ranks[i]}-{suit_ranks[i+1]}-{suit_ranks[i+2]}{suit.value}"
                    sequences.append(seq_str)

        return sequences

    def _is_part_of_sequence(self, tile: Tile, hand: List[Tile]) -> bool:
        """检查牌是否可能是顺子的一部分"""
        suit_tiles = [t for t in hand if t.suit == tile.suit]
        ranks = set(t.rank for t in suit_tiles)

        # 检查前后是否有连续的牌
        has_prev = (tile.rank - 1) in ranks
        has_next = (tile.rank + 1) in ranks
        has_prev2 = (tile.rank - 2) in ranks
        has_next2 = (tile.rank + 2) in ranks

        # 能形成顺子的条件
        return (
            (has_prev and has_next)
            or (has_prev and has_prev2)
            or (has_next and has_next2)
        )

    def _find_ting(self, hand: List[Tile]) -> Dict[str, Any]:
        """
        分析听牌信息

        Returns:
            听牌信息字典
        """
        ting_info = {"is_ting": False, "ting_tiles": [], "discard_options": []}

        # 简化的听牌分析：检查是否只差一张牌就能胡
        # 这里实现基础的听牌逻辑
        for discard_tile in set(hand):
            temp_hand = hand.copy()
            temp_hand.remove(discard_tile)

            # 检查去掉这张牌后，加上什么牌能胡
            winning_tiles = self._check_winning_tiles(temp_hand)

            if winning_tiles:
                ting_info["is_ting"] = True
                ting_info["discard_options"].append(
                    {"discard": str(discard_tile), "can_win_with": winning_tiles}
                )

        # 获取所有可能的听牌
        all_ting_tiles = set()
        for option in ting_info["discard_options"]:
            all_ting_tiles.update(option["can_win_with"])

        ting_info["ting_tiles"] = list(all_ting_tiles)

        return ting_info

    def _check_winning_tiles(self, hand: List[Tile]) -> List[str]:
        """
        检查手牌加上什么牌能胡

        这是一个简化的实现，实际的胡牌判断会更复杂
        """
        winning_tiles = []

        # 生成所有可能的牌
        all_possible_tiles = []
        for suit in SUITS_LIST:
            for rank in range(1, 10):
                all_possible_tiles.append(Tile(suit, rank))

        # 检查加上每张牌是否能胡
        for test_tile in all_possible_tiles:
            test_hand = hand + [test_tile]
            if self._is_winning_hand_simple(test_hand):
                winning_tiles.append(str(test_tile))

        return winning_tiles

    def _is_winning_hand_simple(self, hand: List[Tile]) -> bool:
        """
        简化的胡牌判断

        基本规则：需要有一个对子，其余都是刻子
        """
        if len(hand) != 14:  # 胡牌时应该是14张牌
            return False

        tile_counter = Counter(hand)

        pairs = 0
        triplets = 0

        for tile, count in tile_counter.items():
            if count == 2:
                pairs += 1
            elif count == 3:
                triplets += 1
            elif count == 4:
                triplets += 1  # 4张可以看作刻子+单张，但这里简化处理
            elif count == 1:
                # 单张牌，不符合胡牌条件
                return False
            else:
                return False

        # 基本胡牌条件：1个对子 + 4个刻子
        return pairs == 1 and triplets == 4
