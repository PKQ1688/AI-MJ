# UV 环境管理指南

本项目已配置为使用 [uv](https://github.com/astral-sh/uv) 进行Python环境和依赖管理。

## 🚀 快速开始

### 1. 安装 uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或使用 pip
pip install uv
```

### 2. 设置项目环境

```bash
# 运行自动设置脚本
./scripts/setup.sh

# 或手动设置
uv venv                    # 创建虚拟环境
uv pip install -e .       # 安装项目依赖
uv pip install -e ".[dev]" # 安装开发依赖
```

### 3. 激活环境

```bash
# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

## 📦 依赖管理

### 项目结构

- `pyproject.toml` - 项目配置和依赖定义
- `uv.lock` - 锁定的依赖版本
- `.uvignore` - uv忽略文件

### 添加新依赖

```bash
# 添加运行时依赖
uv add package-name

# 添加开发依赖
uv add --dev package-name

# 手动编辑 pyproject.toml 后同步
uv pip install -e ".[dev]"
```

### 更新依赖

```bash
# 更新所有依赖
uv pip install --upgrade -e ".[dev]"

# 更新特定包
uv pip install --upgrade package-name
```

## 🛠️ 开发工具

### 使用开发脚本

```bash
# 查看所有可用命令
./scripts/dev.sh

# 运行所有检查
./scripts/dev.sh check

# 单独运行工具
./scripts/dev.sh format  # 代码格式化
./scripts/dev.sh lint    # 代码风格检查
./scripts/dev.sh type    # 类型检查
./scripts/dev.sh test    # 运行测试
```

### 手动运行工具

```bash
# 代码格式化
black src/ tests/

# 代码风格检查
flake8 src/ tests/

# 类型检查
mypy src/

# 运行测试
pytest tests/
```

## 🎮 运行项目

```bash
# 运行演示
python demo.py

# 运行游戏
python main.py

# 使用真实LLM API
python main.py --llm-type openai --api-key YOUR_API_KEY
```

## 📋 常用命令

```bash
# 查看已安装的包
uv pip list

# 查看包信息
uv pip show package-name

# 生成requirements.txt（如需要）
uv pip freeze > requirements.txt

# 检查依赖冲突
uv pip check

# 清理缓存
uv cache clean
```

## 🔧 配置说明

### pyproject.toml 配置

```toml
[project]
dependencies = [
    "openai>=1.0.0",
    "anthropic>=0.7.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
]
```

### 工具配置

- **Black**: 代码格式化，行长度88字符
- **Flake8**: 代码风格检查
- **MyPy**: 静态类型检查
- **Pytest**: 测试框架，支持异步测试

## 🚨 故障排除

### 常见问题

1. **虚拟环境未激活**
   ```bash
   source .venv/bin/activate
   ```

2. **依赖冲突**
   ```bash
   uv pip check
   uv pip install --force-reinstall -e ".[dev]"
   ```

3. **缓存问题**
   ```bash
   uv cache clean
   rm -rf .venv
   uv venv
   uv pip install -e ".[dev]"
   ```

## 📚 更多资源

- [uv 官方文档](https://github.com/astral-sh/uv)
- [Python 包管理最佳实践](https://packaging.python.org/)
- [pyproject.toml 规范](https://peps.python.org/pep-0621/)

## 🤝 贡献

在提交代码前，请确保：

1. 运行 `./scripts/dev.sh check` 通过所有检查
2. 添加必要的测试
3. 更新文档（如需要）

---

**注意**: 本项目已从 `requirements.txt` 迁移到 `pyproject.toml`，建议使用 uv 进行环境管理以获得最佳体验。
