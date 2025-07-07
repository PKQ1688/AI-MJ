"""
简单测试脚本，不依赖pytest
"""

from src.core.tile import Tile
from src.core.meld import Meld
from src.core.action import Action
from src.utils.constants import Suit, ActionType, MeldType


def test_tile():
    """测试Tile类"""
    print("🧪 测试Tile类...")

    # 测试创建
    tile1 = Tile(Suit.WAN, 5)
    assert tile1.suit == Suit.WAN
    assert tile1.rank == 5
    assert str(tile1) == "五万"
    print("  ✅ 创建测试通过")

    # 测试从字符串创建
    tile2 = Tile.from_string("五万")
    assert tile2.suit == Suit.WAN
    assert tile2.rank == 5
    print("  ✅ 从字符串创建测试通过")

    # 测试相等性
    assert tile1 == tile2
    tile3 = Tile(Suit.TONG, 5)
    assert tile1 != tile3
    print("  ✅ 相等性测试通过")

    # 测试排序
    tiles = [
        Tile(Suit.TIAO, 3),
        Tile(Suit.WAN, 1),
        Tile(Suit.TONG, 9),
        Tile(Suit.WAN, 5),
    ]
    sorted_tiles = sorted(tiles)
    expected_order = [
        Tile(Suit.WAN, 1),
        Tile(Suit.WAN, 5),
        Tile(Suit.TONG, 9),
        Tile(Suit.TIAO, 3),
    ]
    assert sorted_tiles == expected_order
    print("  ✅ 排序测试通过")


def test_meld():
    """测试Meld类"""
    print("🧪 测试Meld类...")

    # 测试碰
    tiles = [Tile(Suit.WAN, 5), Tile(Suit.WAN, 5), Tile(Suit.WAN, 5)]
    meld = Meld(MeldType.PONG, tiles)
    assert meld.meld_type == MeldType.PONG
    assert len(meld.tiles) == 3
    assert not meld.is_concealed()
    print("  ✅ 碰测试通过")

    # 测试暗杠
    tiles = [Tile(Suit.TONG, 3)] * 4
    meld = Meld(MeldType.AN_GANG, tiles)
    assert meld.meld_type == MeldType.AN_GANG
    assert len(meld.tiles) == 4
    assert meld.is_concealed()
    print("  ✅ 暗杠测试通过")

    # 测试无效副露
    try:
        tiles = [Tile(Suit.WAN, 5), Tile(Suit.WAN, 6)]  # 只有2张牌
        Meld(MeldType.PONG, tiles)
        assert False, "应该抛出异常"
    except ValueError:
        print("  ✅ 无效副露测试通过")


def test_action():
    """测试Action类"""
    print("🧪 测试Action类...")

    # 测试出牌动作
    tile = Tile(Suit.WAN, 5)
    action = Action(ActionType.DISCARD, tile)
    assert action.action_type == ActionType.DISCARD
    assert action.tile == tile
    assert str(action) == "出牌(五万)"
    print("  ✅ 出牌动作测试通过")

    # 测试定缺动作
    action = Action(ActionType.LACK, suit=Suit.TIAO)
    assert action.action_type == ActionType.LACK
    assert action.suit == Suit.TIAO
    assert str(action) == "定缺(条)"
    print("  ✅ 定缺动作测试通过")

    # 测试从字典创建
    data = {"action_type": "DISCARD", "tile": "五万"}
    action = Action.from_dict(data)
    assert action.action_type == ActionType.DISCARD
    assert action.tile == Tile(Suit.WAN, 5)
    print("  ✅ 从字典创建测试通过")


def test_hand_analyzer():
    """测试HandAnalyzer类"""
    print("🧪 测试HandAnalyzer类...")

    from src.player.hand_analyzer import HandAnalyzer

    analyzer = HandAnalyzer()

    # 测试空手牌
    result = analyzer.analyze([])
    assert result["sorted_hand"] == []
    print("  ✅ 空手牌测试通过")

    # 测试简单手牌
    hand = [
        Tile(Suit.WAN, 1),
        Tile(Suit.WAN, 1),  # 一万对子
        Tile(Suit.TONG, 5),
        Tile(Suit.TONG, 5),
        Tile(Suit.TONG, 5),  # 五筒刻子
        Tile(Suit.TIAO, 9),  # 九条孤张
    ]

    result = analyzer.analyze(hand)
    assert len(result["sorted_hand"]) == 6
    assert result["suits"]["万"]["count"] == 2
    assert result["suits"]["筒"]["count"] == 3
    assert result["suits"]["条"]["count"] == 1

    analysis = result["analysis"]
    assert "一万" in analysis["pairs"]
    assert "五筒" in analysis["triplets"]
    assert "九条" in analysis["isolated"]
    print("  ✅ 简单手牌测试通过")


def main():
    """运行所有测试"""
    print("🧪 开始运行简单测试...")
    print("=" * 50)

    try:
        test_tile()
        test_meld()
        test_action()
        test_hand_analyzer()

        print("\n✅ 所有测试通过！")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
