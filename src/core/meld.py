"""
副露类定义
"""

from typing import List
from .tile import Tile
from ..utils.constants import MeldType


class Meld:
    """
    副露类

    代表玩家已经公开的牌组（碰或杠）
    """

    def __init__(self, meld_type: MeldType, tiles: List[Tile]):
        """
        初始化副露

        Args:
            meld_type: 副露类型 (碰, 明杠, 暗杠, 补杠)
            tiles: 组成副露的牌
        """
        self.meld_type = meld_type
        self.tiles = tiles.copy()  # 创建副本避免外部修改

        # 验证副露的有效性
        self._validate()

    def _validate(self):
        """验证副露是否有效"""
        if self.meld_type == MeldType.PONG:
            if len(self.tiles) != 3:
                raise ValueError("碰牌必须包含3张牌")
            if not all(tile == self.tiles[0] for tile in self.tiles):
                raise ValueError("碰牌必须是3张相同的牌")

        elif self.meld_type in [MeldType.MING_GANG, MeldType.AN_GANG, MeldType.BU_GANG]:
            if len(self.tiles) != 4:
                raise ValueError("杠牌必须包含4张牌")
            if not all(tile == self.tiles[0] for tile in self.tiles):
                raise ValueError("杠牌必须是4张相同的牌")

    def __str__(self) -> str:
        """返回副露的字符串表示"""
        tile_names = [str(tile) for tile in self.tiles]
        return f"{self.meld_type.value}({', '.join(tile_names)})"

    def __repr__(self) -> str:
        """返回副露的详细表示"""
        return f"Meld(type={self.meld_type.value}, tiles={self.tiles})"

    def get_base_tile(self) -> Tile:
        """获取副露的基础牌（第一张牌）"""
        return self.tiles[0]

    def is_concealed(self) -> bool:
        """判断是否为暗副露（暗杠）"""
        return self.meld_type == MeldType.AN_GANG

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "meld_type": self.meld_type.value,
            "tiles": [tile.to_dict() for tile in self.tiles],
            "tile_names": [str(tile) for tile in self.tiles],
            "base_tile": str(self.get_base_tile()),
            "is_concealed": self.is_concealed(),
        }
