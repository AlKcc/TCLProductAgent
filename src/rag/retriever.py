"""
知识检索模块
"""
from typing import List
from .vectorstore import VectorStore, get_vectorstore
from .document_loader import DocumentLoader
from ..utils.config import TOP_K_RETRIEVAL
from ..utils.logger import logger


class KnowledgeRetriever:
    """知识检索器"""

    def __init__(self):
        """初始化检索器"""
        self.vectorstore = get_vectorstore()
        self.document_loader = DocumentLoader()

    def initialize_knowledge_base(self, rebuild: bool = False):
        """
        初始化知识库

        Args:
            rebuild: 是否重建知识库
        """
        from pathlib import Path

        data_dir = Path(__file__).parent.parent.parent / 'data'

        if rebuild:
            logger.info("重建知识库...")
            self.vectorstore.reset()

        # 加载所有文档
        all_docs = self.document_loader.load_all_knowledge(data_dir)

        # 添加到向量数据库
        for category, documents in all_docs.items():
            if documents:
                self.vectorstore.add_documents(
                    collection_name=category,
                    documents=documents
                )

        logger.info("知识库初始化完成")

    def retrieve(self, query: str, collection_name: str = None,
                 n_results: int = None) -> List[str]:
        """
        检索相关知识

        Args:
            query: 查询文本
            collection_name: 指定集合名称，None表示搜索所有集合
            n_results: 返回结果数量

        Returns:
            List[str]: 检索到的文档列表
        """
        n_results = n_results or TOP_K_RETRIEVAL

        if collection_name:
            # 从指定集合检索
            results = self.vectorstore.query(
                collection_name=collection_name,
                query_texts=[query],
                n_results=n_results
            )
            return results["documents"][0] if results["documents"] else []
        else:
            # 从所有集合检索
            all_results = []
            for col_name in ['products', 'faq', 'tips']:
                results = self.vectorstore.query(
                    collection_name=col_name,
                    query_texts=[query],
                    n_results=2
                )
                if results["documents"]:
                    all_results.extend(results["documents"][0])

            # 返回前n_results个
            return all_results[:n_results]

    def retrieve_context(self, query: str) -> str:
        """
        检索上下文文本

        Args:
            query: 查询文本

        Returns:
            str: 格式化的上下文文本
        """
        documents = self.retrieve(query)

        if not documents:
            return ""

        context = "【相关知识库信息】\n"
        for i, doc in enumerate(documents, 1):
            context += f"\n{i}. {doc}\n"

        return context


# 全局检索器实例
retriever_instance = None


def get_retriever() -> KnowledgeRetriever:
    """获取检索器单例"""
    global retriever_instance
    if retriever_instance is None:
        retriever_instance = KnowledgeRetriever()
    return retriever_instance


if __name__ == "__main__":
    # 测试检索器
    retriever = KnowledgeRetriever()

    # 初始化知识库
    retriever.initialize_knowledge_base(rebuild=True)

    # 测试检索
    query = "Mini LED有什么优势？"
    context = retriever.retrieve_context(query)

    print(f"查询: {query}")
    print(f"上下文:\n{context}")