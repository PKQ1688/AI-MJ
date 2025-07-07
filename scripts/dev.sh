#!/bin/bash
# 开发工具脚本

set -e

# 确保在虚拟环境中
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  请先激活虚拟环境: source .venv/bin/activate"
    exit 1
fi

case "$1" in
    "format")
        echo "🎨 格式化代码..."
        black src/ tests/ *.py
        echo "✅ 代码格式化完成"
        ;;
    "lint")
        echo "🔍 检查代码风格..."
        flake8 src/ tests/ *.py
        echo "✅ 代码风格检查完成"
        ;;
    "type")
        echo "🔍 类型检查..."
        mypy src/
        echo "✅ 类型检查完成"
        ;;
    "test")
        echo "🧪 运行测试..."
        python -m pytest tests/ -v
        echo "✅ 测试完成"
        ;;
    "check")
        echo "🔍 运行所有检查..."
        echo "1. 格式化代码..."
        black src/ tests/ *.py
        echo "2. 检查代码风格..."
        flake8 src/ tests/ *.py
        echo "3. 类型检查..."
        mypy src/
        echo "4. 运行测试..."
        python -m pytest tests/ -v
        echo "✅ 所有检查完成"
        ;;
    "demo")
        echo "🎮 运行演示..."
        python demo.py
        ;;
    "game")
        echo "🀄️  启动游戏..."
        python main.py
        ;;
    *)
        echo "🛠️  开发工具脚本"
        echo ""
        echo "用法: ./scripts/dev.sh <命令>"
        echo ""
        echo "可用命令:"
        echo "  format  - 格式化代码"
        echo "  lint    - 检查代码风格"
        echo "  type    - 类型检查"
        echo "  test    - 运行测试"
        echo "  check   - 运行所有检查"
        echo "  demo    - 运行演示"
        echo "  game    - 启动游戏"
        ;;
esac
