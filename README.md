# AI四川麻将游戏引擎

基于命令行的、支持四个LLM AI对战的四川麻将游戏，严格遵循"血战到底"规则。

## 🎯 项目特点

- **模块化设计**: 清晰的代码结构，易于维护和扩展
- **AI驱动**: 支持多种LLM API（OpenAI、Claude等）
- **专业理牌工具**: 为LLM提供结构化的手牌分析
- **完整规则引擎**: 严格遵循四川麻将血战到底规则
- **实时渲染**: 控制台实时显示游戏状态

## 🏗️ 项目结构

```
AI-MJ/
├── src/
│   ├── core/                    # 核心数据结构
│   │   ├── tile.py             # 麻将牌类
│   │   ├── meld.py             # 副露类
│   │   └── action.py           # 动作类
│   ├── engine/                  # 游戏引擎
│   │   ├── game.py             # 游戏主控制器
│   │   └── rule_engine.py      # 规则引擎
│   ├── player/                  # 玩家相关
│   │   ├── llm_player.py       # LLM玩家
│   │   └── hand_analyzer.py    # 理牌工具
│   ├── services/                # 外部服务
│   │   └── llm_api.py          # LLM API服务
│   ├── ui/                      # 用户界面
│   │   └── console_renderer.py # 控制台渲染器
│   └── utils/                   # 工具类
│       └── constants.py        # 常量定义
├── tests/                       # 测试文件
├── main.py                      # 主入口
├── demo.py                      # 演示脚本
└── requirements.txt             # 依赖文件
```

## 🚀 快速开始

### 方法一：使用uv（推荐）

```bash
# 1. 安装uv（如果未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 运行设置脚本
./scripts/setup.sh

# 3. 激活虚拟环境
source .venv/bin/activate

# 4. 运行演示
python demo.py
```

### 方法二：使用pip

```bash
# 1. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 2. 安装依赖
pip install -e ".[dev]"

# 3. 运行演示
python demo.py
```

### 运行游戏

```bash
# 运行功能演示
python demo.py

# 运行完整游戏（使用模拟LLM）
python main.py

# 使用OpenAI API
python main.py --llm-type openai --api-key YOUR_API_KEY

# 使用Claude API
python main.py --llm-type claude --api-key YOUR_API_KEY

# 开启调试模式
python main.py --debug
```

## 🎮 游戏规则

本游戏严格遵循四川麻将"血战到底"规则：

- **不能吃牌**: 只能碰、杠，不能吃顺子
- **必须缺一门**: 胡牌时手牌中不能有缺门花色的牌
- **血战到底**: 第一个胡牌后游戏继续，直到只剩一个玩家未胡牌

## 🧠 AI设计

### HandAnalyzer（理牌工具）

专门为LLM设计的核心工具，提供结构化的手牌分析：

```json
{
  "sorted_hand": ["一万", "一万", "二万", "三万", "九万"],
  "suits": {
    "万": {"tiles": ["一万", "一万", "二万"], "count": 3},
    "筒": {"tiles": ["三筒", "四筒"], "count": 2}
  },
  "analysis": {
    "pairs": ["一万"],
    "triplets": [],
    "sequences": ["1-2-3万"],
    "ting_info": {"is_ting": true, "ting_tiles": ["四万"]}
  }
}
```

### LLM交互协议

发送给LLM的提示包含：
- 游戏规则说明
- 当前游戏状态
- 理牌分析结果
- 可能的动作列表

LLM返回JSON格式的决策：
```json
{"action": "DISCARD", "tile": "九万"}
```

## 🔧 开发

### 使用开发脚本（推荐）

```bash
# 激活虚拟环境
source .venv/bin/activate

# 运行所有检查（格式化、风格检查、类型检查、测试）
./scripts/dev.sh check

# 单独运行各种检查
./scripts/dev.sh format  # 格式化代码
./scripts/dev.sh lint    # 代码风格检查
./scripts/dev.sh type    # 类型检查
./scripts/dev.sh test    # 运行测试
./scripts/dev.sh demo    # 运行演示
./scripts/dev.sh game    # 启动游戏
```

### 手动运行开发工具

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_core.py -v

# 格式化代码
black src/ tests/

# 检查代码风格
flake8 src/ tests/

# 类型检查
mypy src/
```

## 📚 核心组件

### 1. 核心数据结构
- **Tile**: 麻将牌，包含花色和点数
- **Meld**: 副露（碰、杠）
- **Action**: 玩家动作

### 2. 游戏引擎
- **Game**: 游戏主控制器，管理游戏流程
- **RuleEngine**: 规则引擎，验证动作合法性

### 3. AI玩家
- **LLMPlayer**: AI玩家，调用LLM API做决策
- **HandAnalyzer**: 理牌工具，为LLM提供结构化分析

### 4. 服务层
- **LLMClient**: LLM API客户端抽象
- **MockLLMClient**: 模拟客户端，用于测试
- **OpenAIClient**: OpenAI API客户端
- **ClaudeClient**: Claude API客户端

## 🎯 技术特点

1. **异步设计**: 使用asyncio支持异步LLM API调用
2. **类型提示**: 完整的类型注解，提高代码可读性
3. **模块化**: 清晰的模块划分，便于维护和扩展
4. **测试覆盖**: 完整的单元测试
5. **错误处理**: 健壮的错误处理机制

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License
使用AI来进行麻将游戏
