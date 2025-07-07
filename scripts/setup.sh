#!/bin/bash
# AI四川麻将项目环境设置脚本

set -e

echo "🀄️  AI四川麻将项目环境设置"
echo "=" * 50

# 检查uv是否安装
if ! command -v uv &> /dev/null; then
    echo "❌ uv未安装，请先安装uv:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ uv已安装: $(uv --version)"

# 创建虚拟环境
echo "🔧 创建虚拟环境..."
uv venv

# 安装项目依赖
echo "📦 安装项目依赖..."
uv pip install -e .

# 安装开发依赖
echo "🛠️  安装开发依赖..."
uv pip install -e ".[dev]"

echo ""
echo "✅ 环境设置完成！"
echo ""
echo "🚀 使用方法:"
echo "  激活环境: source .venv/bin/activate"
echo "  运行演示: python demo.py"
echo "  运行游戏: python main.py"
echo "  运行测试: python -m pytest"
echo "  代码格式化: black src/ tests/"
echo "  代码检查: flake8 src/ tests/"
echo "  类型检查: mypy src/"
