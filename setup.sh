#!/bin/bash

# ============================================
# TCL智能产品咨询助手 - 一键启动脚本
# ============================================

echo "========================================="
echo "  TCL智能产品咨询助手"
echo "========================================="
echo ""

# ------------------------------
# 检查Python环境
# ------------------------------
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3"
    echo "请先安装Python 3.12或更高版本"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✅ Python版本: $PYTHON_VERSION"

# ------------------------------
# 检查虚拟环境
# ------------------------------
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  警告: 未在虚拟环境中运行"
    echo "建议创建并激活虚拟环境:"
    echo "   conda create -n tcl_agent python=3.12"
    echo "   conda activate tcl_agent"
    echo ""
fi

# ------------------------------
# 检查依赖包
# ------------------------------
echo "检查依赖包..."
python3 -c "import langchain, zhipuai, chromadb, gradio" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ 依赖包已安装"
else
    echo "❌ 依赖包未安装，正在安装..."
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "✅ 依赖包安装成功"
    else
        echo "❌ 依赖包安装失败，请手动执行:"
        echo "   pip install -r requirements.txt"
        exit 1
    fi
fi

# ------------------------------
# 检查环境变量配置
# ------------------------------
echo ""
echo "检查环境配置..."

if [ -f ".env" ]; then
    echo "✅ 环境变量文件存在"
    source .env

    if [ -z "$ZHIPUAI_API_KEY" ]; then
        echo "❌ 错误: ZHIPUAI_API_KEY未设置"
        echo ""
        echo "请按以下步骤配置API密钥:"
        echo "1. 访问 https://open.bigmodel.cn/ 注册账号"
        echo "2. 获取API密钥"
        echo "3. 修改.env文件，填入您的API密钥:"
        echo "   ZHIPUAI_API_KEY=your_api_key_here"
        exit 1
    else
        echo "✅ API密钥已配置"
        echo "   模型: ${MODEL_NAME:-glm-4.5-air}"
    fi
else
    echo "❌ 错误: .env文件不存在"
    echo ""
    echo "请按以下步骤配置:"
    echo "1. cp .env.example .env"
    echo "2. 编辑.env文件，配置API密钥和模型参数"
    exit 1
fi

# ------------------------------
# 创建必要的目录
# ------------------------------
echo ""
echo "创建数据目录..."
mkdir -p logs
mkdir -p data/vectorstore
echo "✅ 目录准备完成"

# ------------------------------
# 检查模型缓存（Embedding模型）
# ------------------------------
MODEL_CACHE="$HOME/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2"
if [ ! -d "$MODEL_CACHE" ]; then
    echo ""
    echo "⚠️  Embedding模型未缓存"
    echo "   首次运行时会自动下载（可能需要代理）"
    echo ""
    echo "如果下载失败，请设置代理:"
    echo "   export HF_ENDPOINT=https://hf-mirror.com"
    echo ""
fi

# ------------------------------
# 打印启动信息
# ------------------------------
echo ""
echo "========================================="
echo "启动应用..."
echo "========================================="
echo ""
echo "📡 访问地址: http://localhost:7860"
echo "⏹️  按 Ctrl+C 停止服务"
echo ""
echo "🔍 使用提示:"
echo "   - 产品查询: TCL电视保修政策是什么？"
echo "   - 产品推荐: 推荐一款5000元左右的电视"
echo "   - 产品对比: Q10L和T7H哪个好？"
echo "   - 故障排查: 电视开机没反应怎么办？"
echo "   - 问候寒暄: 你好"
echo ""

# ------------------------------
# 启动应用
# ------------------------------
# 临时关闭代理（避免代理干扰本地连接）
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY

# 启动服务
python3 src/app.py