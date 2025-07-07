"""
AI四川麻将游戏演示脚本
"""

import asyncio
from src.core.tile import Tile
from src.player.hand_analyzer import HandAnalyzer
from src.player.llm_player import LLMPlayer
from src.services.llm_api import create_llm_client
from src.utils.constants import Suit


async def demo_hand_analyzer():
    """演示理牌工具"""
    print("🔍 理牌工具演示")
    print("=" * 40)

    analyzer = HandAnalyzer()

    # 创建一个示例手牌
    hand = [
        Tile(Suit.WAN, 1),
        Tile(Suit.WAN, 1),
        Tile(Suit.WAN, 2),
        Tile(Suit.TONG, 5),
        Tile(Suit.TONG, 5),
        Tile(Suit.TONG, 5),
        Tile(Suit.TIAO, 9),
        Tile(Suit.TIAO, 8),
        Tile(Suit.TIAO, 7),
        Tile(Suit.WAN, 3),
        Tile(Suit.WAN, 4),
        Tile(Suit.WAN, 5),
        Tile(Suit.TONG, 2),
    ]

    print("📋 原始手牌:")
    print(" ".join(str(tile) for tile in hand))
    print()

    # 分析手牌
    result = analyzer.analyze(hand)

    print("📊 分析结果:")
    print(f"排序后手牌: {' '.join(result['sorted_hand'])}")
    print()

    print("🃏 按花色分组:")
    for suit, info in result["suits"].items():
        if info["count"] > 0:
            print(f"  {suit}: {info['count']}张 - {' '.join(info['tiles'])}")
    print()

    print("🔍 牌型分析:")
    analysis = result["analysis"]
    if analysis["pairs"]:
        print(f"  对子: {', '.join(analysis['pairs'])}")
    if analysis["triplets"]:
        print(f"  刻子: {', '.join(analysis['triplets'])}")
    if analysis["sequences"]:
        print(f"  顺子: {', '.join(analysis['sequences'])}")
    if analysis["isolated"]:
        print(f"  孤张: {', '.join(analysis['isolated'])}")

    print()
    print("🎯 听牌信息:")
    ting_info = analysis["ting_info"]
    if ting_info["is_ting"]:
        print("  状态: 听牌中")
        for option in ting_info["discard_options"]:
            print(
                f"  打出 {option['discard']} 可听: {', '.join(option['can_win_with'])}"
            )
    else:
        print("  状态: 未听牌")


async def demo_llm_player():
    """演示LLM玩家"""
    print("\n🤖 LLM玩家演示")
    print("=" * 40)

    # 创建模拟LLM客户端
    llm_client = create_llm_client("mock")

    # 创建玩家
    player = LLMPlayer(0, llm_client, "演示玩家")

    # 给玩家一些牌
    hand = [
        Tile(Suit.WAN, 1),
        Tile(Suit.WAN, 2),
        Tile(Suit.WAN, 3),
        Tile(Suit.TONG, 5),
        Tile(Suit.TONG, 5),
        Tile(Suit.TONG, 5),
        Tile(Suit.TIAO, 9),
        Tile(Suit.TIAO, 9),
        Tile(Suit.WAN, 7),
        Tile(Suit.WAN, 8),
        Tile(Suit.WAN, 9),
        Tile(Suit.TONG, 2),
        Tile(Suit.TONG, 3),
    ]

    for tile in hand:
        player.add_tile(tile)

    print(f"👤 玩家: {player.name}")
    print(f"🃏 手牌: {' '.join(str(tile) for tile in sorted(player.hand))}")
    print()

    # 模拟游戏状态
    game_state = {
        "phase": "LACK_SELECTION",
        "current_player_id": 0,
        "wall_remaining": 50,
        "discards": {"0": [], "1": [], "2": [], "3": []},
        "melds": {"0": [], "1": [], "2": [], "3": []},
        "players": {},
    }

    # 演示定缺
    print("🚫 定缺演示:")
    lack_action = await player.choose_lack(game_state)
    print(f"  选择: {lack_action}")
    print(f"  缺门: {player.lack_suit.value if player.lack_suit else '未设置'}")
    print()

    # 演示决策
    game_state["phase"] = "PLAYING"
    print("🎯 决策演示:")
    action = await player.decide_action(game_state)
    print(f"  决策: {action}")

    # 显示玩家统计
    print("\n📊 玩家统计:")
    stats = player.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


async def demo_tile_operations():
    """演示牌的基本操作"""
    print("\n🀄️ 麻将牌操作演示")
    print("=" * 40)

    # 创建牌
    tile1 = Tile(Suit.WAN, 5)
    tile2 = Tile.from_string("五万")
    tile3 = Tile(Suit.TONG, 3)

    print("🎴 创建牌:")
    print(f"  tile1 = Tile(Suit.WAN, 5) -> {tile1}")
    print(f"  tile2 = Tile.from_string('五万') -> {tile2}")
    print(f"  tile3 = Tile(Suit.TONG, 3) -> {tile3}")
    print()

    # 比较牌
    print("⚖️  比较牌:")
    print(f"  tile1 == tile2: {tile1 == tile2}")
    print(f"  tile1 == tile3: {tile1 == tile3}")
    print()

    # 排序牌
    tiles = [tile3, tile1, Tile(Suit.TIAO, 1), Tile(Suit.WAN, 1)]
    print("📊 排序前:")
    print(f"  {' '.join(str(t) for t in tiles)}")

    sorted_tiles = sorted(tiles)
    print("📊 排序后:")
    print(f"  {' '.join(str(t) for t in sorted_tiles)}")
    print()

    # 转换为字典
    print("📋 转换为字典:")
    tile_dict = tile1.to_dict()
    for key, value in tile_dict.items():
        print(f"  {key}: {value}")


async def main():
    """主演示函数"""
    print("🀄️  AI四川麻将游戏演示")
    print("=" * 50)

    try:
        await demo_tile_operations()
        await demo_hand_analyzer()
        await demo_llm_player()

        print("\n✅ 演示完成！")
        print("💡 运行 'python main.py' 开始完整游戏")

    except Exception as e:
        print(f"\n❌ 演示出错: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
