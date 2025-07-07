### 技术设计文档：AI四川麻将游戏引擎

#### 1. 项目概述

本文档旨在设计一个基于命令行的、支持四个LLM AI对战的四川麻将游戏。游戏严格遵循“血战到底”规则。设计的核心是模块化、状态驱动，并为LLM AI提供一个专用的`HandAnalyzer`工具，使其能基于预处理和分析过的数据进行高效决策，而非原始手牌。

#### 2. 系统架构

系统由以下几个核心模块组成，它们之间的交互关系如下：

```
+-----------------+      +------------------+      +--------------------+
|   Game Engine   | <--> |   LLM Player     | <--> |   LLM API Service  |
| (Game Loop)     |      | (Decision Logic) |      | (External)         |
+-----------------+      +------------------+      +--------------------+
        |                      |
        | (Validate Action)    | (Analyze Hand)
        v                      v
+-----------------+      +------------------+
|   Rule Engine   |      |  Hand Analyzer   |
| (Game Rules)    |      |  (Tool for LLM)  |
+-----------------+      +------------------+
        |
        | (Render State)
        v
+-----------------+
| Console Renderer|
| (UI)            |
+-----------------+
```

*   **Game Engine**: 游戏的主控制器，负责驱动游戏流程。
*   **LLM Player**: 代表一个AI玩家，负责调用LLM API获取决策。
*   **Hand Analyzer**: 一个工具模块，负责将手牌整理成结构化数据。
*   **Rule Engine**: 封装所有麻将规则的判断逻辑。
*   **Console Renderer**: 负责在控制台显示游戏状态。
*   **LLM API Service**: 外部的大语言模型服务接口。

#### 3. 核心数据结构

这些是贯穿整个系统的基础数据对象。

*   **`Tile` (麻将牌)**
    *   **描述:** 代表一张麻将牌。
    *   **属性:**
        *   `suit: Enum` - 花色 (万, 筒, 条)
        *   `rank: int` - 点数 (1-9)
    *   **示例:** `Tile(suit='万', rank=5)` 代表“五万”。

*   **`Meld` (副露)**
    *   **描述:** 代表玩家已经公开的牌组（碰或杠）。
    *   **属性:**
        *   `meld_type: Enum` - 类型 (碰, 明杠, 暗杠, 补杠)
        *   `tiles: list[Tile]` - 组成的牌。

*   **`Action` (动作)**
    *   **描述:** 代表一个玩家可以执行的动作。
    *   **属性:**
        *   `action_type: Enum` - 动作类型 (出牌, 碰, 杠, 胡, 过, 定缺)
        *   `tile: Tile | None` - 与该动作相关的牌 (例如，要打出或碰的牌)。
        *   `suit: Suit | None` - 定缺时选择的花色。

#### 4. 模块/类详细设计

**4.1. `HandAnalyzer` (理牌工具)**

这是专门为LLM设计的核心工具，目的是将一手杂乱的牌转换成富有洞察力的结构化信息。

*   **职责:**
    1.  对手牌进行排序。
    2.  按花色分组。
    3.  识别潜在的组合（对子、刻子）。
    4.  分析听牌信息（如果手牌只差一张即可胡牌）。
*   **输入:** `hand: list[Tile]`
*   **输出:** 一个JSON（字典）对象，结构如下：
    ```json
    {
      "sorted_hand": ["一万", "一万", "二万", "三万", "九万", "三筒", ...],
      "suits": {
        "万": {
          "tiles": ["一万", "一万", "二万", "三万", "九万"],
          "count": 5
        },
        "筒": {
          "tiles": ["三筒", "四筒", "五筒", "七筒", "八筒"],
          "count": 5
        },
        "条": {
          "tiles": ["六条", "六条"],
          "count": 2
        }
      },
      "analysis": {
        "pairs": ["一万", "六条"],
        "triplets": [],
        "ting_info": {
          "if_discard": "九万",
          "can_win_with": ["一万", "四万"]
        }
      }
    }
    ```
*   **方法:**
    *   `analyze(hand: list[Tile]) -> dict`: 执行完整的分析并返回上述结构的字典。
    *   `_find_ting(hand: list[Tile]) -> dict`: 内部方法，用于计算听牌信息。

**4.2. `LLMPlayer` (AI玩家)**

*   **职责:** 实现玩家的决策逻辑。
*   **属性:**
    *   `player_id: int`
    *   `hand: list[Tile]`
    *   `melds: list[Meld]`
    *   `lack_suit: Suit`
    *   `llm_client: LLM_API` - 用于调用LLM的客户端。
    *   `hand_analyzer: HandAnalyzer` - 持有理牌工具的实例。
*   **方法:**
    *   `decide_action(game_state: dict) -> Action`:
        1.  调用 `self.hand_analyzer.analyze(self.hand)` 得到理牌后的 `analysis_data`。
        2.  构建一个包含 `game_state` 和 `analysis_data` 的详细Prompt。
        3.  调用 `self.llm_client.generate(prompt)` 获取LLM的决策。
        4.  解析LLM返回的JSON，并将其转换为 `Action` 对象返回。
    *   `choose_lack(game_state: dict) -> Action`: 类似 `decide_action`，但用于开局定缺。

**4.3. `Game` (游戏引擎)**

*   **职责:** 驱动游戏流程，管理状态。
*   **属性:**
    *   `players: list[LLMPlayer]`
    *   `wall: list[Tile]`
    *   `current_player_id: int`
    *   `game_state: dict` - 包含所有玩家可见信息的公共游戏状态。
    *   `rule_engine: RuleEngine`
    *   `renderer: ConsoleRenderer`
*   **方法:**
    *   `run()`: 游戏主循环，管理整个对局的生命周期。
    *   `_start_round()`: 初始化一局游戏（洗牌、发牌、定缺）。
    *   `_game_turn()`: 执行一个玩家的回合（摸牌、决策、出牌）。
    *   `_process_action(action: Action)`:
        1.  使用 `rule_engine` 验证动作是否合法。
        2.  如果合法，则更新 `game_state`。
        3.  触发后续流程（例如，出牌后询问其他玩家）。

**4.4. `RuleEngine` (规则引擎)**

*   **职责:** 提供静态方法用于规则判断。
*   **方法 (均为静态方法):**
    *   `is_valid_action(action: Action, game_state: dict) -> bool`: 验证一个动作在当前状态下是否合法。
    *   `is_winning_hand(hand, melds, win_tile, lack_suit) -> bool`: 判断是否满足胡牌条件。
    *   `calculate_score(...) -> int`: 计算番数。
    *   `get_possible_actions(player_hand, game_state) -> list[Action]`: 找出当前所有可能的合法操作。

#### 5. 详细工作流程：一个玩家的回合

1.  **轮到玩家A (`player_A`)。**
2.  `Game` 引擎从 `wall` 摸一张牌 `new_tile`，并将其加入 `player_A.hand`。
3.  `Game` 引擎调用 `player_A.decide_action(game_state)`。
4.  在 `player_A` 内部：
    a.  `hand_analyzer.analyze(player_A.hand)` 被调用，返回 `analysis_data`。
    b.  一个包含 `game_state` 和 `analysis_data` 的Prompt被精心构建。
    c.  Prompt通过API发送给LLM。
    d.  LLM返回一个JSON决策，例如: `{ "action": "DISCARD", "tile": "九万" }`。
    e.  `player_A` 将JSON解析成 `Action` 对象并返回给 `Game` 引擎。
5.  `Game` 引擎收到 `Action(action_type='DISCARD', tile='九万')`。
6.  `Game` 引擎调用 `rule_engine.is_valid_action(...)` 进行验证。
7.  验证通过后，`Game` 引擎更新 `game_state`：从 `player_A.hand` 移除“九万”，并将其放入弃牌池。
8.  `Game` 引擎向其他三位玩家广播“九万”被丢弃的事件，并依次询问他们是否要碰/杠/胡。
9.  `ConsoleRenderer.render(game_state)` 被调用，刷新控制台显示。
10. 流程继续，轮到下一个玩家。

#### 6. LLM交互协议 (Prompt & Response)

**Prompt 模板 (发送给LLM):**

```json
{
  "role": "You are a Sichuan Mahjong AI expert. Your goal is to win. You must respond in a valid JSON format.",
  "rules": {
    "variant": "Sichuan Blood-Bath (血战到底)",
    "notes": ["No CHOW (吃)", "Must have a LACK SUIT (缺一门) to win", "Game continues after first win"]
  },
  "game_state": {
    "current_player_id": 0,
    "wall_remaining": 45,
    "discards": {
      "0": ["一万", "二筒"],
      "1": ["九条", "八万"],
      "2": ["三筒", "东风"],
      "3": ["五条", "六筒"]
    },
    "melds": { ... }
  },
  "my_info": {
    "player_id": 0,
    "lack_suit": "条",
    "hand_analysis": {
      "sorted_hand": [...],
      "suits": { ... },
      "analysis": { ... }
    }
  },
  "last_action": {
    "player_id": 3,
    "action": "DISCARD",
    "tile": "二万"
  },
  "possible_actions": ["PONG", "GANG", "HU", "PASS"]
}
```

**期望的LLM响应 (JSON格式):**

*   出牌: `{ "action": "DISCARD", "tile": "九万" }`
*   碰牌: `{ "action": "PONG" }`
*   胡牌: `{ "action": "HU" }`
*   过/跳过: `{ "action": "PASS" }`
