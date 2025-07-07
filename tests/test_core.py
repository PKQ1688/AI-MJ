"""
核心数据结构测试
"""

import pytest
from src.core.tile import Tile
from src.core.meld import Meld
from src.core.action import Action
from src.utils.constants import Suit, ActionType, MeldType


class TestTile:
    """测试Tile类"""

    def test_tile_creation(self):
        """测试牌的创建"""
        tile = Tile(Suit.WAN, 5)
        assert tile.suit == Suit.WAN
        assert tile.rank == 5
        assert str(tile) == "五万"

    def test_tile_from_string(self):
        """测试从字符串创建牌"""
        tile = Tile.from_string("五万")
        assert tile.suit == Suit.WAN
        assert tile.rank == 5

    def test_tile_equality(self):
        """测试牌的相等性"""
        tile1 = Tile(Suit.WAN, 5)
        tile2 = Tile(Suit.WAN, 5)
        tile3 = Tile(Suit.TONG, 5)

        assert tile1 == tile2
        assert tile1 != tile3

    def test_tile_sorting(self):
        """测试牌的排序"""
        tiles = [
            Tile(Suit.TIAO, 3),
            Tile(Suit.WAN, 1),
            Tile(Suit.TONG, 9),
            Tile(Suit.WAN, 5),
        ]

        sorted_tiles = sorted(tiles)

        # 应该按花色再按点数排序
        assert sorted_tiles[0] == Tile(Suit.WAN, 1)
        assert sorted_tiles[1] == Tile(Suit.WAN, 5)
        assert sorted_tiles[2] == Tile(Suit.TONG, 9)
        assert sorted_tiles[3] == Tile(Suit.TIAO, 3)


class TestMeld:
    """测试Meld类"""

    def test_pong_creation(self):
        """测试碰的创建"""
        tiles = [Tile(Suit.WAN, 5), Tile(Suit.WAN, 5), Tile(Suit.WAN, 5)]
        meld = Meld(MeldType.PONG, tiles)

        assert meld.meld_type == MeldType.PONG
        assert len(meld.tiles) == 3
        assert not meld.is_concealed()

    def test_gang_creation(self):
        """测试杠的创建"""
        tiles = [Tile(Suit.TONG, 3)] * 4
        meld = Meld(MeldType.AN_GANG, tiles)

        assert meld.meld_type == MeldType.AN_GANG
        assert len(meld.tiles) == 4
        assert meld.is_concealed()

    def test_invalid_meld(self):
        """测试无效副露"""
        tiles = [Tile(Suit.WAN, 5), Tile(Suit.WAN, 6)]  # 只有2张牌

        with pytest.raises(ValueError):
            Meld(MeldType.PONG, tiles)


class TestAction:
    """测试Action类"""

    def test_discard_action(self):
        """测试出牌动作"""
        tile = Tile(Suit.WAN, 5)
        action = Action(ActionType.DISCARD, tile)

        assert action.action_type == ActionType.DISCARD
        assert action.tile == tile
        assert str(action) == "出牌(五万)"

    def test_lack_action(self):
        """测试定缺动作"""
        action = Action(ActionType.LACK, suit=Suit.TIAO)

        assert action.action_type == ActionType.LACK
        assert action.suit == Suit.TIAO
        assert str(action) == "定缺(条)"

    def test_action_from_dict(self):
        """测试从字典创建动作"""
        data = {"action_type": "DISCARD", "tile": "五万"}

        action = Action.from_dict(data)
        assert action.action_type == ActionType.DISCARD
        assert action.tile == Tile(Suit.WAN, 5)


if __name__ == "__main__":
    pytest.main([__file__])
