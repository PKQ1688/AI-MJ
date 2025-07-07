"""
麻将牌类定义
"""

from typing import Optional
from ..utils.constants import Suit, RANK_NAMES, SUIT_NAMES


class Tile:
    """
    麻将牌类

    代表一张麻将牌，包含花色和点数
    """

    def __init__(self, suit: Suit, rank: int):
        """
        初始化麻将牌

        Args:
            suit: 花色 (万, 筒, 条)
            rank: 点数 (1-9)
        """
        if rank not in range(1, 10):
            raise ValueError(f"Invalid rank: {rank}. Rank must be between 1 and 9.")

        self.suit = suit
        self.rank = rank

    def __str__(self) -> str:
        """返回牌的中文名称，如 '五万'"""
        return f"{RANK_NAMES[self.rank]}{SUIT_NAMES[self.suit]}"

    def __repr__(self) -> str:
        """返回牌的详细表示"""
        return f"Tile(suit={self.suit.value}, rank={self.rank})"

    def __eq__(self, other) -> bool:
        """判断两张牌是否相同"""
        if not isinstance(other, Tile):
            return False
        return self.suit == other.suit and self.rank == other.rank

    def __hash__(self) -> int:
        """支持作为字典键或集合元素"""
        return hash((self.suit, self.rank))

    def __lt__(self, other) -> bool:
        """支持排序，先按花色再按点数"""
        if not isinstance(other, Tile):
            return NotImplemented
        if self.suit != other.suit:
            # 按花色顺序：万 < 筒 < 条
            suit_order = {Suit.WAN: 0, Suit.TONG: 1, Suit.TIAO: 2}
            return suit_order[self.suit] < suit_order[other.suit]
        return self.rank < other.rank

    @classmethod
    def from_string(cls, tile_str: str) -> "Tile":
        """
        从字符串创建牌对象

        Args:
            tile_str: 牌的字符串表示，如 '五万'

        Returns:
            Tile对象

        Raises:
            ValueError: 如果字符串格式不正确
        """
        if len(tile_str) != 2:
            raise ValueError(f"Invalid tile string: {tile_str}")

        rank_char = tile_str[0]
        suit_char = tile_str[1]

        # 查找点数
        rank = None
        for r, name in RANK_NAMES.items():
            if name == rank_char:
                rank = r
                break

        if rank is None:
            raise ValueError(f"Invalid rank character: {rank_char}")

        # 查找花色
        suit = None
        for s, name in SUIT_NAMES.items():
            if name == suit_char:
                suit = s
                break

        if suit is None:
            raise ValueError(f"Invalid suit character: {suit_char}")

        return cls(suit, rank)

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {"suit": self.suit.value, "rank": self.rank, "name": str(self)}
