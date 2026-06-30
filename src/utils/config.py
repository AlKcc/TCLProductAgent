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
MODEL_NAME = os.getenv("MODEL_NAME", "glm-4.5-air")

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = PROJECT_ROOT / "logs" / "agent.log"

# 向量数据库配置
CHROMA_PERSIST_DIRECTORY = str(VECTOR_DB_PATH)
EMBEDDING_MODEL = "text2vec-base-chinese"

# RAG配置（从环境变量读取，默认值兼容旧配置）
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", "3"))

# LLM参数配置
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
TOP_P = float(os.getenv("TOP_P", "0.9"))

# 缓存配置
CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", "100"))
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))

# 对话配置
MAX_HISTORY_LENGTH = int(os.getenv("MAX_HISTORY_LENGTH", "20"))

# 确保目录存在
VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)
(PROJECT_ROOT / "logs").mkdir(parents=True, exist_ok=True)


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
    CHUNK_SIZE = CHUNK_SIZE
    CHUNK_OVERLAP = CHUNK_OVERLAP
    TOP_K_RETRIEVAL = TOP_K_RETRIEVAL

    # LLM参数配置
    MAX_TOKENS = MAX_TOKENS
    TEMPERATURE = TEMPERATURE
    TOP_P = TOP_P

    # 缓存配置
    CACHE_MAX_SIZE = CACHE_MAX_SIZE
    CACHE_TTL_SECONDS = CACHE_TTL_SECONDS

    # 对话配置
    MAX_HISTORY_LENGTH = MAX_HISTORY_LENGTH

    @classmethod
    def validate(cls):
        """验证配置"""
        if not cls.API_KEY:
            raise ValueError("请设置 ZHIPUAI_API_KEY 环境变量")

        if not cls.API_KEY.startswith(""):
            print("⚠️  警告：API_KEY 格式可能不正确")

    @classmethod
    def print_config(cls):
        """打印当前配置（用于调试）"""
        print("=" * 50)
        print("TCL智能产品咨询助手 - 配置信息")
        print("=" * 50)
        print(f"模型: {cls.MODEL}")
        print(f"API_KEY: {'已配置' if cls.API_KEY else '未配置'}")
        print(f"最大输出Token: {cls.MAX_TOKENS}")
        print(f"温度: {cls.TEMPERATURE}")
        print(f"检索条数: {cls.TOP_K_RETRIEVAL}")
        print(f"缓存大小: {cls.CACHE_MAX_SIZE}")
        print(f"缓存过期时间: {cls.CACHE_TTL_SECONDS}秒")
        print(f"最大历史长度: {cls.MAX_HISTORY_LENGTH}")
        print("=" * 50)


# 启动时验证配置
try:
    Config.validate()
except ValueError as e:
    print(f"❌ 配置错误: {e}")