#!/bin/bash

# TCL Product Agent - 一键启动脚本

echo "========================================="
echo "  TCL智能产品咨询助手"
echo "========================================="
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3"
    echo "请先安装Python 3.12或更高版本"
    exit 1
fi

echo "✅ Python版本: $(python3 --version)"

# 检查是否在虚拟环境中
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  警告: 未在虚拟环境中运行"
    echo "建议激活虚拟环境: conda activate tcl_agent"
fi

# 检查依赖
echo ""
echo "检查依赖包..."
python3 -c "import langchain, zhipuai, chromadb, gradio" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ 依赖包已安装"
else
    echo "❌ 依赖包未安装"
    echo "请运行: pip install -r requirements.txt"
    exit 1
fi

# 检查环境变量
echo ""
echo "检查环境配置..."
if [ -f ".env" ]; then
    echo "✅ 环境变量文件存在"
    source .env

    if [ -z "$ZHIPUAI_API_KEY" ]; then
        echo "⚠️  警告: ZHIPUAI_API_KEY未设置"
        echo "请在.env文件中设置API密钥"
    else
        echo "✅ API密钥已配置"
    fi
else
    echo "⚠️  警告: .env文件不存在"
    echo "请复制.env.example为.env并配置API密钥"
    echo "命令: cp .env.example .env"
fi

# 创建必要的目录
echo ""
echo "创建数据目录..."
mkdir -p logs
mkdir -p data/vectorstore
echo "✅ 目录准备完成"

# 启动应用
echo ""
echo "========================================="
echo "启动应用..."
echo "========================================="
echo ""
echo "访问地址: http://localhost:7860"
echo "按 Ctrl+C 停止服务"
echo ""

python3 src/app.py