"""
TCL智能产品咨询助手 - 主程序入口
"""
import os
import sys
from pathlib import Path

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