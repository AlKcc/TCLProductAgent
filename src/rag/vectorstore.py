"""
向量存储模块 - 使用 ChromaDB
"""
from typing import List
from pathlib import Path
import chromadb
from chromadb.config import Settings

from ..utils.config import CHROMA_PERSIST_DIRECTORY, EMBEDDING_MODEL
from ..utils.logger import logger


class VectorStore:
    """向量数据库管理"""

    def __init__(self, persist_directory: str = CHROMA_PERSIST_DIRECTORY):
        """
        初始化向量数据库

        Args:
            persist_directory: 持久化目录
        """
        self.persist_directory = persist_directory
        self.client = None

        # 确保目录存在
        Path(persist_directory).mkdir(parents=True, exist_ok=True)

        self._init_client()

    def _init_client(self):
        """初始化ChromaDB客户端"""
        try:
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logger.info(f"向量数据库初始化成功: {self.persist_directory}")
        except Exception as e:
            logger.error(f"向量数据库初始化失败: {e}")
            raise

    def create_collection(self, name: str) -> chromadb.Collection:
        """
        创建或获取集合

        Args:
            name: 集合名称

        Returns:
            Collection: ChromaDB集合
        """
        try:
            # 检查集合是否存在
            existing_collections = [col.name for col in self.client.list_collections()]

            if name in existing_collections:
                logger.info(f"集合 {name} 已存在，获取现有集合")
                collection = self.client.get_collection(name)
            else:
                logger.info(f"创建新集合: {name}")
                collection = self.client.create_collection(name=name)

            return collection

        except Exception as e:
            logger.error(f"创建集合失败: {e}")
            raise

    def add_documents(self, collection_name: str, documents: List[str],
                      metadatas: List[dict] = None, ids: List[str] = None):
        """
        添加文档到集合

        Args:
            collection_name: 集合名称
            documents: 文档文本列表
            metadatas: 元数据列表
            ids: 文档ID列表
        """
        if not documents:
            logger.warning("没有文档需要添加")
            return

        collection = self.create_collection(collection_name)

        # 生成默认ID
        if ids is None:
            ids = [f"{collection_name}_{i}" for i in range(len(documents))]

        # 生成默认元数据
        if metadatas is None:
            metadatas = [{"source": collection_name} for _ in documents]

        try:
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"成功添加 {len(documents)} 条文档到集合 {collection_name}")
        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            raise

    def query(self, collection_name: str, query_texts: List[str],
              n_results: int = 3) -> dict:
        """
        查询相似文档

        Args:
            collection_name: 集合名称
            query_texts: 查询文本列表
            n_results: 返回结果数量

        Returns:
            dict: 查询结果
        """
        collection = self.create_collection(collection_name)

        try:
            results = collection.query(
                query_texts=query_texts,
                n_results=n_results
            )
            return results
        except Exception as e:
            logger.error(f"查询失败: {e}")
            return {"documents": [[]], "metadatas": [[]]}

    def get_collection_info(self, collection_name: str) -> dict:
        """获取集合信息"""
        collection = self.create_collection(collection_name)
        return collection.count()

    def reset(self):
        """重置数据库"""
        try:
            self.client.reset()
            logger.info("向量数据库已重置")
        except Exception as e:
            logger.error(f"重置数据库失败: {e}")


# 全局向量数据库实例
vectorstore = None


def get_vectorstore() -> VectorStore:
    """获取向量数据库单例"""
    global vectorstore
    if vectorstore is None:
        vectorstore = VectorStore()
    return vectorstore


if __name__ == "__main__":
    # 测试向量数据库
    vs = VectorStore()

    # 添加测试文档
    test_docs = [
        "TCL电视采用Mini LED技术，对比度高",
        "Mini LED使用小尺寸LED灯珠，控光精准",
        "量子点技术提供广色域，色彩还原准确"
    ]

    vs.add_documents("test", test_docs)

    # 查询
    results = vs.query("test", ["Mini LED有什么特点"], n_results=2)
    print("查询结果:")
    for i, doc in enumerate(results["documents"][0]):
        print(f"{i+1}. {doc}")