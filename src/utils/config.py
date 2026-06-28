"""
配置管理模块
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
PRODUCTS_DIR = DATA_DIR / "products"
FAQ_DIR = DATA_DIR / "faq"
TIPS_DIR = DATA_DIR / "tips"
VECTOR_DB_PATH = DATA_DIR / "vectorstore"

# API配置
ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "glm-4-flash")

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = PROJECT_ROOT / "logs" / "agent.log"

# 向量数据库配置
CHROMA_PERSIST_DIRECTORY = str(VECTOR_DB_PATH)
EMBEDDING_MODEL = "text2vec-base-chinese"  # 或使用 GLM 的 embedding

# 确保目录存在
VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)
(Path(__file__).parent.parent / "logs").mkdir(parents=True, exist_ok=True)


class Config:
    """全局配置类"""

    # GLM配置
    API_KEY = ZHIPUAI_API_KEY
    MODEL = MODEL_NAME

    # 数据路径
    PRODUCTS_DIR = PRODUCTS_DIR
    FAQ_DIR = FAQ_DIR
    TIPS_DIR = TIPS_DIR

    # RAG配置
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    TOP_K_RETRIEVAL = 3

    # Agent配置
    MAX_TOKENS = 2000
    TEMPERATURE = 0.7

    @classmethod
    def validate(cls):
        """验证配置"""
        if not cls.API_KEY:
            raise ValueError("请设置 ZHIPUAI_API_KEY 环境变量")

        if not cls.API_KEY.startswith(""):
            print("⚠️  警告：API_KEY 格式可能不正确")


# 启动时验证配置
try:
    Config.validate()
except ValueError as e:
    print(f"❌ 配置错误: {e}")