"""
AI四川麻将游戏主入口
"""

import asyncio
import argparse
from src.engine.game import Game
from src.player.llm_player import LLMPlayer
from src.ui.console_renderer import ConsoleRenderer
from src.services.llm_api import create_llm_client


async def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="AI四川麻将游戏")
    parser.add_argument(
        "--llm-type",
        choices=["mock", "openai", "claude"],
        default="mock",
        help="LLM客户端类型",
    )
    parser.add_argument("--api-key", help="LLM API密钥")
    parser.add_argument("--debug", action="store_true", help="开启调试模式")
    parser.add_argument("--model", default="gpt-3.5-turbo", help="LLM模型名称")

    args = parser.parse_args()

    print("🀄️  欢迎来到AI四川麻将游戏！")
    print("=" * 50)

    try:
        # 创建LLM客户端
        llm_kwargs = {}
        if args.api_key:
            llm_kwargs["api_key"] = args.api_key
        if args.model:
            llm_kwargs["model"] = args.model

        llm_client = create_llm_client(args.llm_type, **llm_kwargs)
        print(f"✅ 使用 {args.llm_type} LLM客户端")

        # 创建4个AI玩家
        players = []
        for i in range(4):
            player_name = f"AI玩家{i+1}"
            player = LLMPlayer(i, llm_client, player_name)
            players.append(player)

        print("✅ 创建了4个AI玩家")

        # 创建渲染器
        renderer = ConsoleRenderer()

        # 创建游戏
        game = Game(players, renderer, debug_mode=args.debug)
        print("✅ 游戏初始化完成")

        # 开始游戏
        print("\n🎮 游戏开始！")
        await game.run()

        print("\n🎉 游戏结束，感谢游玩！")

    except KeyboardInterrupt:
        print("\n\n⏹️  游戏被用户中断")
    except Exception as e:
        print(f"\n❌ 游戏运行出错: {e}")
        if args.debug:
            import traceback

            traceback.print_exc()


def create_demo_game():
    """创建演示游戏（同步版本）"""

    async def demo():
        # 创建模拟LLM客户端
        llm_client = create_llm_client("mock")

        # 创建4个AI玩家
        players = []
        for i in range(4):
            player = LLMPlayer(i, llm_client, f"演示玩家{i+1}")
            players.append(player)

        # 创建渲染器和游戏
        renderer = ConsoleRenderer()
        game = Game(players, renderer, debug_mode=True)

        # 运行游戏
        await game.run()

    # 运行演示
    asyncio.run(demo())


if __name__ == "__main__":
    # 检查是否有命令行参数
    import sys

    if len(sys.argv) == 1:
        # 没有参数，运行演示模式
        print("🎮 运行演示模式...")
        print("💡 使用 'python main.py --help' 查看更多选项")
        print()
        create_demo_game()
    else:
        # 有参数，正常解析
        asyncio.run(main())
