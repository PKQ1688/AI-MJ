"""
常量定义模块
定义游戏中使用的枚举类型和常量
"""

from enum import Enum
from typing import List


class Suit(Enum):
    """花色枚举"""

    WAN = "万"  # 万子
    TONG = "筒"  # 筒子
    TIAO = "条"  # 条子


class ActionType(Enum):
    """动作类型枚举"""

    DISCARD = "DISCARD"  # 出牌
    PONG = "PONG"  # 碰
    GANG = "GANG"  # 杠
    HU = "HU"  # 胡
    PASS = "PASS"  # 过
    LACK = "LACK"  # 定缺


class MeldType(Enum):
    """副露类型枚举"""

    PONG = "PONG"  # 碰（明刻）
    MING_GANG = "MING_GANG"  # 明杠
    AN_GANG = "AN_GANG"  # 暗杠
    BU_GANG = "BU_GANG"  # 补杠


class GamePhase(Enum):
    """游戏阶段枚举"""

    INIT = "INIT"  # 初始化
    LACK_SELECTION = "LACK_SELECTION"  # 定缺阶段
    PLAYING = "PLAYING"  # 游戏进行中
    ENDED = "ENDED"  # 游戏结束


# 游戏常量
HAND_SIZE = 13  # 手牌数量
TOTAL_TILES_PER_RANK = 4  # 每种牌的数量
RANKS = list(range(1, 10))  # 点数范围 1-9
SUITS_LIST = [Suit.WAN, Suit.TONG, Suit.TIAO]

# 牌的中文名称映射
RANK_NAMES = {
    1: "一",
    2: "二",
    3: "三",
    4: "四",
    5: "五",
    6: "六",
    7: "七",
    8: "八",
    9: "九",
}

# 花色中文名称
SUIT_NAMES = {Suit.WAN: "万", Suit.TONG: "筒", Suit.TIAO: "条"}
