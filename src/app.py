"""
TCL智能产品咨询助手 - 主程序入口
"""
import os
import sys
from pathlib import Path

# 检查模型缓存
MODEL_CACHE = Path.home() / '.cache' / 'huggingface' / 'hub' / 'models--sentence-transformers--all-MiniLM-L6-v2'
if not MODEL_CACHE.exists():
    print("\n" + "=" * 50)
    print("⚠️  模型未缓存，需要先下载")
    print("=" * 50)
    print("\n请先开启代理，然后运行以下命令下载模型：")
    print("\n  python -c \"from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')\"")
    print("\n或者设置国内镜像加速：")
    print("  pip install -U langchain-huggingface")
    print("  export HF_ENDPOINT=https://hf-mirror.com")
    print("  python -c \"from langchain_huggingface import HuggingFaceEmbeddings; HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')\"")
    print("\n下载完成后再运行本程序")
    sys.exit(1)

# 设置no_proxy环境变量，避免localhost连接被代理拦截
current_no_proxy = os.environ.get('no_proxy', '')
localhosts = 'localhost,127.0.0.1,0.0.0.0'
os.environ['no_proxy'] = f"{localhosts},{current_no_proxy}" if current_no_proxy else localhosts
os.environ['NO_PROXY'] = f"{localhosts},{os.environ.get('NO_PROXY', '')}" if os.environ.get('NO_PROXY') else localhosts

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ui.gradio_app import create_gradio_app
from src.utils.logger import logger
from src.rag.retriever import get_retriever


def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("TCL智能产品咨询助手启动中...")
    logger.info("=" * 50)

    try:
        # 初始化知识库（如果需要）
        logger.info("初始化知识库...")
        retriever = get_retriever()

        # 检查知识库是否存在
        from pathlib import Path
        kb_path = Path(__file__).parent.parent / 'data' / 'vectorstore'
        if not kb_path.exists():
            logger.info("知识库不存在，开始构建...")
            retriever.initialize_knowledge_base(rebuild=True)
        else:
            logger.info("使用现有知识库")

        # 创建Gradio应用
        logger.info("创建Web界面...")
        app = create_gradio_app()

        # 启动应用
        logger.info("应用启动成功！")
        logger.info("访问地址: http://localhost:7860")

        app.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            show_error=True
        )

    except KeyboardInterrupt:
        logger.info("用户中断，程序退出")
    except Exception as e:
        logger.error(f"程序运行错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()