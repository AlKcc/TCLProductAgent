"""
LangChain RAG检索模块 - 使用本地sentence-transformers Embedding
LangChain 1.x 现代API实现
"""
import threading
import time
from typing import List, Dict, Any
from langchain_chroma import Chroma
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from ..utils.config import Config, DATA_DIR, VECTOR_DB_PATH
from ..utils.logger import logger
from .document_loader import DocumentLoader


class LangChainRAG:
    """基于LangChain的RAG检索系统"""

    def __init__(self, llm: ChatZhipuAI):
        self.llm = llm
        self.vectorstore = None
        self.retriever = None
        self.qa_chain = None
        self._init_rag_with_timeout()

    def _init_rag_with_timeout(self):
        """带超时限制的RAG初始化"""
        result = [None]

        def init_task():
            try:
                self._init_rag()
                result[0] = True
            except Exception as e:
                logger.error(f"LangChain RAG初始化失败: {e}")
                result[0] = False

        thread = threading.Thread(target=init_task)
        thread.start()
        thread.join(timeout=30)

        if thread.is_alive():
            logger.warning("LangChain RAG初始化超时，使用关键词检索作为fallback")
            self.vectorstore = None
        elif result[0] is False:
            self.vectorstore = None

    def _init_rag(self):
        """初始化RAG系统"""
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings

            self.embeddings = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2"
            )

            self.vectorstore = Chroma(
                embedding_function=self.embeddings,
                persist_directory=str(VECTOR_DB_PATH),
                collection_name="tcl_knowledge"
            )

            collection = self.vectorstore._client.get_collection("tcl_knowledge")
            count = collection.count()
            if count == 0:
                self._load_documents()
            else:
                logger.info(f"向量数据库已有 {count} 条文档")

            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            )

            template = """你是TCL产品智能助手。请根据提供的文档内容回答用户问题。

文档内容：
{context}

用户问题：{question}

请基于文档内容回答，不要编造信息。如果文档中没有相关信息，请说明无法回答。"""

            prompt = ChatPromptTemplate.from_template(template)

            self.qa_chain = (
                {"context": self.retriever, "question": RunnablePassthrough()}
                | prompt
                | self.llm
                | StrOutputParser()
            )

            logger.info("LangChain RAG系统初始化成功")

        except Exception as e:
            raise e

    def _load_documents(self):
        """加载文档到向量数据库"""
        try:
            loader = DocumentLoader()
            docs_dict = loader.load_all_knowledge(DATA_DIR)

            langchain_docs = []
            for category, docs in docs_dict.items():
                for doc in docs:
                    langchain_docs.append(Document(
                        page_content=doc,
                        metadata={"category": category}
                    ))

            if langchain_docs:
                self.vectorstore.add_documents(langchain_docs)
                logger.info(f"成功添加 {len(langchain_docs)} 条文档到向量数据库")
            else:
                logger.warning("没有文档可添加")

        except Exception as e:
            logger.error(f"加载文档失败: {e}")

    def retrieve(self, query: str, k: int = 3) -> List[str]:
        """检索相关文档"""
        if not self.retriever:
            return []

        try:
            results = self.retriever.invoke(query)
            return [doc.page_content for doc in results]
        except Exception as e:
            logger.error(f"检索失败: {e}")
            return []

    def query(self, query: str) -> Dict[str, Any]:
        """使用RAG链回答问题"""
        if not self.qa_chain:
            return {"answer": "", "sources": []}

        try:
            answer = self.qa_chain.invoke(query)

            sources = []
            if self.retriever:
                try:
                    docs = self.retriever.invoke(query)
                    for doc in docs:
                        sources.append({
                            "content": doc.page_content[:200],
                            "category": doc.metadata.get("category", "")
                        })
                except Exception as e:
                    logger.error(f"获取来源文档失败: {e}")

            return {"answer": answer, "sources": sources}
        except Exception as e:
            logger.error(f"RAG查询失败: {e}")
            return {"answer": "", "sources": []}


if __name__ == "__main__":
    from langchain_community.chat_models import ChatZhipuAI

    llm = ChatZhipuAI(
        api_key=Config.API_KEY,
        model="glm-4-flash",
        temperature=0.7
    )

    rag = LangChainRAG(llm)

    test_queries = [
        "TCL电视保修政策是什么？",
        "Q10L Pro有多少个分区？",
        "Mini LED技术原理是什么？"
    ]

    for query in test_queries:
        print(f"\n🔍 查询: {query}")
        result = rag.query(query)
        print(f"📝 回答: {result['answer']}")
        if result['sources']:
            print(f"📚 来源: {len(result['sources'])} 个文档")