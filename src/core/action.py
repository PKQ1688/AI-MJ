"""
动作类定义
"""

from typing import Optional
from .tile import Tile
from ..utils.constants import ActionType, Suit


class Action:
    """
    动作类

    代表一个玩家可以执行的动作
    """

    def __init__(
        self,
        action_type: ActionType,
        tile: Optional[Tile] = None,
        suit: Optional[Suit] = None,
    ):
        """
        初始化动作

        Args:
            action_type: 动作类型 (出牌, 碰, 杠, 胡, 过, 定缺)
            tile: 与该动作相关的牌 (例如，要打出或碰的牌)
            suit: 定缺时选择的花色
        """
        self.action_type = action_type
        self.tile = tile
        self.suit = suit

        # 验证动作的有效性
        self._validate()

    def _validate(self):
        """验证动作是否有效"""
        if self.action_type == ActionType.DISCARD:
            if self.tile is None:
                raise ValueError("出牌动作必须指定要出的牌")

        elif self.action_type == ActionType.LACK:
            if self.suit is None:
                raise ValueError("定缺动作必须指定要缺的花色")

        elif self.action_type in [ActionType.PONG, ActionType.GANG]:
            # 碰和杠可能需要指定牌，但也可能从上下文推断
            pass

        elif self.action_type in [ActionType.HU, ActionType.PASS]:
            # 胡牌和过牌不需要额外参数
            pass

    def __str__(self) -> str:
        """返回动作的字符串表示"""
        if self.action_type == ActionType.DISCARD and self.tile:
            return f"出牌({self.tile})"
        elif self.action_type == ActionType.LACK and self.suit:
            return f"定缺({self.suit.value})"
        elif self.action_type == ActionType.PONG:
            if self.tile:
                return f"碰({self.tile})"
            return "碰"
        elif self.action_type == ActionType.GANG:
            if self.tile:
                return f"杠({self.tile})"
            return "杠"
        elif self.action_type == ActionType.HU:
            return "胡"
        elif self.action_type == ActionType.PASS:
            return "过"
        else:
            return self.action_type.value

    def __repr__(self) -> str:
        """返回动作的详细表示"""
        return (
            f"Action(type={self.action_type.value}, tile={self.tile}, suit={self.suit})"
        )

    def __eq__(self, other) -> bool:
        """判断两个动作是否相同"""
        if not isinstance(other, Action):
            return False
        return (
            self.action_type == other.action_type
            and self.tile == other.tile
            and self.suit == other.suit
        )

    def to_dict(self) -> dict:
        """转换为字典格式"""
        result = {"action_type": self.action_type.value}

        if self.tile:
            result["tile"] = str(self.tile)
            result["tile_obj"] = self.tile.to_dict()

        if self.suit:
            result["suit"] = self.suit.value

        return result

    @classmethod
    def from_dict(cls, data: dict) -> "Action":
        """
        从字典创建动作对象

        Args:
            data: 包含动作信息的字典

        Returns:
            Action对象
        """
        action_type = ActionType(data["action_type"])

        tile = None
        if "tile" in data and data["tile"]:
            tile = Tile.from_string(data["tile"])

        suit = None
        if "suit" in data and data["suit"]:
            suit = Suit(data["suit"])

        return cls(action_type, tile, suit)
