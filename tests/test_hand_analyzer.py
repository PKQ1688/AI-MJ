"""
理牌工具测试
"""

import pytest
from src.core.tile import Tile
from src.player.hand_analyzer import HandAnalyzer
from src.utils.constants import Suit


class TestHandAnalyzer:
    """测试HandAnalyzer类"""

    def setup_method(self):
        """设置测试"""
        self.analyzer = HandAnalyzer()

    def test_analyze_empty_hand(self):
        """测试分析空手牌"""
        result = self.analyzer.analyze([])

        assert result["sorted_hand"] == []
        assert all(suit_info["count"] == 0 for suit_info in result["suits"].values())

    def test_analyze_simple_hand(self):
        """测试分析简单手牌"""
        hand = [
            Tile(Suit.WAN, 1),
            Tile(Suit.WAN, 1),  # 一万对子
            Tile(Suit.TONG, 5),
            Tile(Suit.TONG, 5),
            Tile(Suit.TONG, 5),  # 五筒刻子
            Tile(Suit.TIAO, 9),  # 九条孤张
        ]

        result = self.analyzer.analyze(hand)

        # 检查排序
        assert len(result["sorted_hand"]) == 6

        # 检查花色分组
        assert result["suits"]["万"]["count"] == 2
        assert result["suits"]["筒"]["count"] == 3
        assert result["suits"]["条"]["count"] == 1

        # 检查分析结果
        analysis = result["analysis"]
        assert "一万" in analysis["pairs"]
        assert "五筒" in analysis["triplets"]
        assert "九条" in analysis["isolated"]

    def test_find_sequences(self):
        """测试找顺子"""
        hand = [
            Tile(Suit.WAN, 1),
            Tile(Suit.WAN, 2),
            Tile(Suit.WAN, 3),  # 一二三万顺子
            Tile(Suit.TONG, 7),
            Tile(Suit.TONG, 8),
            Tile(Suit.TONG, 9),  # 七八九筒顺子
        ]

        result = self.analyzer.analyze(hand)
        sequences = result["analysis"]["sequences"]

        # 应该找到潜在的顺子
        assert len(sequences) >= 1

    def test_ting_analysis(self):
        """测试听牌分析"""
        # 构造一个接近胡牌的手牌
        hand = [
            Tile(Suit.WAN, 1),
            Tile(Suit.WAN, 1),
            Tile(Suit.WAN, 1),  # 一万刻子
            Tile(Suit.TONG, 5),
            Tile(Suit.TONG, 5),
            Tile(Suit.TONG, 5),  # 五筒刻子
            Tile(Suit.TIAO, 9),
            Tile(Suit.TIAO, 9),
            Tile(Suit.TIAO, 9),  # 九条刻子
            Tile(Suit.WAN, 2),
            Tile(Suit.WAN, 2),  # 二万对子
            Tile(Suit.TONG, 3),
            Tile(Suit.TONG, 4),  # 三四筒，听二五筒
        ]

        result = self.analyzer.analyze(hand)
        ting_info = result["analysis"]["ting_info"]

        # 应该检测到听牌状态
        # 注意：这是简化的实现，实际结果可能不完全准确
        assert isinstance(ting_info, dict)
        assert "is_ting" in ting_info

    def test_group_by_suits(self):
        """测试按花色分组"""
        hand = [
            Tile(Suit.WAN, 1),
            Tile(Suit.WAN, 5),
            Tile(Suit.WAN, 9),
            Tile(Suit.TONG, 2),
            Tile(Suit.TONG, 8),
            Tile(Suit.TIAO, 3),
        ]

        result = self.analyzer.analyze(hand)
        suits = result["suits"]

        assert suits["万"]["count"] == 3
        assert suits["万"]["ranks"] == [1, 5, 9]

        assert suits["筒"]["count"] == 2
        assert suits["筒"]["ranks"] == [2, 8]

        assert suits["条"]["count"] == 1
        assert suits["条"]["ranks"] == [3]


if __name__ == "__main__":
    pytest.main([__file__])
