#!/bin/bash
# 安装依赖脚本

set -e

echo "🔧 安装 GPT-Researcher 后端依赖"
echo "================================"

# 检查 Python 版本
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "📌 Python 版本: $PYTHON_VERSION"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "❌ 需要 Python 3.10 或更高版本"
    exit 1
fi

# 进入后端目录
cd "$(dirname "$0")/.."

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source venv/bin/activate

# 升级 pip
echo "⬆️  升级 pip..."
pip install --upgrade pip

# 安装依赖
echo "📥 安装依赖包..."
pip install -r requirements.txt

echo ""
echo "✅ 依赖安装完成！"
echo ""
echo "🚀 启动项目："
echo "   source venv/bin/activate"
echo "   python scripts/dev.py"
