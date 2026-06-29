"""
TCL产品Agent主逻辑
"""
import os
from typing import Optional, List, Dict
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from ..utils.config import Config, MODEL_NAME, DATA_DIR
from ..utils.logger import logger
from ..utils.helpers import (
    load_all_products, search_product_by_keyword,
    filter_products_by_price_range, format_product_info,
    format_comparison_table
)
from ..rag.document_loader import DocumentLoader
from ..rag.langchain_rag import LangChainRAG
from .intent_classifier import Intent, IntentClassifier, intent_classifier


class TCLProductAgent:
    """TCL产品智能咨询Agent"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化Agent

        Args:
            api_key: GLM API密钥，如果为None则从环境变量读取
        """
        self.api_key = api_key or Config.API_KEY
        self.model_name = MODEL_NAME

        # 初始化LLM
        self.llm = ChatZhipuAI(
            api_key=self.api_key,
            model=self.model_name,
            temperature=Config.TEMPERATURE
        )

        # 初始化意图分类器
        self.intent_classifier = IntentClassifier()

        # 初始化对话记忆（使用列表，兼容LangChain消息格式）
        self.chat_history = []

        # 加载产品数据
        self.products = load_all_products()
        logger.info(f"TCL产品Agent初始化完成，加载产品数据 {sum(len(v) for v in self.products.values())} 款")

        # 加载多格式文档（PDF/MD/CSV）
        self.document_loader = DocumentLoader()
        self.documents = self._load_documents()
        logger.info(f"加载多格式文档: {sum(len(v) for v in self.documents.values())} 条")

        # 初始化LangChain RAG（尝试语义检索，失败则自动降级）
        self.langchain_rag = None
        try:
            self.langchain_rag = LangChainRAG(self.llm)
            logger.info("LangChain RAG语义检索已启用")
        except Exception as e:
            logger.warning(f"LangChain RAG初始化失败，使用关键词检索作为fallback: {e}")

    def _load_documents(self) -> dict:
        """加载所有格式的文档"""
        try:
            docs = self.document_loader.load_all_knowledge(DATA_DIR)
            logger.info("多格式文档加载成功")
            return docs
        except Exception as e:
            logger.error(f"加载多格式文档失败: {e}")
            return {'products': [], 'docs': [], 'faq': [], 'tips': []}

    def _format_document_for_context(self, docs: List[str], max_docs: int = 3) -> str:
        """将文档列表格式化为上下文"""
        if not docs:
            return ""

        context = ""
        for i, doc in enumerate(docs[:max_docs]):
            context += f"\n【文档{i+1}】\n{doc[:500]}...\n" if len(doc) > 500 else f"\n【文档{i+1}】\n{doc}\n"

        return context

    def _search_documents(self, query: str, max_results: int = 3) -> List[str]:
        """搜索相关文档（优先使用LangChain语义检索，失败则使用关键词检索）"""
        # 优先尝试LangChain语义检索
        if self.langchain_rag:
            try:
                docs = self.langchain_rag.retrieve(query, k=max_results)
                if docs:
                    logger.debug(f"LangChain语义检索成功，找到 {len(docs)} 条文档")
                    return docs
            except Exception as e:
                logger.warning(f"LangChain语义检索失败，切换到关键词检索: {e}")

        # Fallback: 使用关键词检索
        query_lower = query.lower()

        keywords = []
        for char in query_lower:
            if '\u4e00' <= char <= '\u9fff':
                keywords.append(char)

        for word in query_lower.split():
            keywords.append(word)

        if not keywords:
            keywords = [query_lower]

        scored_results = []
        for category, docs in self.documents.items():
            for doc in docs:
                doc_lower = doc.lower()
                match_count = sum(1 for keyword in keywords if keyword in doc_lower)
                if match_count > 0:
                    scored_results.append((match_count, doc))

        scored_results.sort(key=lambda x: x[0], reverse=True)

        return [doc for _, doc in scored_results[:max_results]]

    def _create_system_message(self, intent: Intent) -> str:
        """根据意图创建系统提示词"""

        system_prompts = {
            Intent.PRODUCT_QUERY: """你是TCL产品咨询专家，专门回答用户关于TCL产品的技术参数、功能特点、使用体验等问题。

回答要求：
1. 基于产品知识库回答，确保信息准确
2. 重点突出产品的核心技术和优势
3. 语言简洁明了，通俗易懂
4. 如果问题涉及多个型号，逐一说明
""",

            Intent.RECOMMENDATION: """你是TCL产品推荐专家，根据用户需求推荐最合适的TCL产品。

推荐原则：
1. 先了解用户的具体需求（预算、用途、空间等）
2. 推荐最匹配的1-2款产品，并说明推荐理由
3. 提供备选方案
4. 诚实说明产品的优点和不足
""",

            Intent.COMPARISON: """你是TCL产品对比专家，帮助用户对比不同TCL产品的差异。

对比要点：
1. 从价格、核心技术、功能特性、适用场景等多维度对比
2. 指出各产品的优缺点
3. 根据用户需求给出选择建议
""",

            Intent.TROUBLESHOOTING: """你是TCL产品技术支持专家，帮助用户排查产品故障。

重要原则：
1. 提供自助排查步骤，帮助用户尝试解决问题
2. 不提供专业维修建议（安全风险）
3. 如果问题无法解决，建议联系官方售后
4. 添加免责声明，避免误导用户
""",

            Intent.TIPS: """你是TCL产品使用专家，提供产品使用技巧和保养建议。

内容要求：
1. 提供实用、可操作的建议
2. 涵盖日常使用、节能、保养等方面
3. 语言简洁，步骤清晰
""",

            Intent.GENERAL_CHAT: """你是TCL产品智能助手，可以回答关于TCL产品的一般性问题。
保持友好、专业的态度。"""
        }

        return system_prompts.get(intent, system_prompts[Intent.GENERAL_CHAT])

    def _build_context(self, user_input: str, intent: Intent) -> str:
        """构建上下文信息（扩展版：包含产品数据+多格式文档）"""

        context = ""

        # 1. 搜索相关产品
        if intent in [Intent.PRODUCT_QUERY, Intent.RECOMMENDATION, Intent.COMPARISON]:
            products = search_product_by_keyword(user_input)
            if products:
                context += f"\n【相关产品信息】\n"
                for product in products[:3]:
                    context += format_product_info(product) + "\n"

        # 2. 搜索多格式文档（PDF/MD/CSV中的相关内容）
        relevant_docs = self._search_documents(user_input, max_results=2)
        if relevant_docs:
            context += self._format_document_for_context(relevant_docs, max_docs=2)

        # 3. 推荐场景：列出所有产品
        if intent == Intent.RECOMMENDATION:
            context += "\n【可用产品列表】\n"
            for category, products in self.products.items():
                category_names = {'tv': '电视', 'ac': '空调', 'fridge': '冰箱', 'washer': '洗衣机'}
                context += f"\n{category_names.get(category, category)}:\n"
                for product in products:
                    context += f"- {product.get('model', '')}: {product.get('basic_params', {}).get('price_range', '')}\n"

        return context

    def chat(self, user_input: str) -> str:
        """
        与Agent对话

        Args:
            user_input: 用户输入

        Returns:
            str: Agent回复
        """
        try:
            # 1. 意图识别
            intent = self.intent_classifier.classify(user_input)
            logger.info(f"用户意图: {intent.value} - {user_input}")

            # 2. 构建上下文
            context = self._build_context(user_input, intent)

            # 3. 构建消息
            system_prompt = self._create_system_message(intent)

            messages = [
                SystemMessage(content=system_prompt),
            ]

            # 添加对话历史
            for human_msg, ai_msg in self.chat_history[-5:]:
                messages.append(HumanMessage(content=human_msg))
                messages.append(AIMessage(content=ai_msg))

            # 添加当前问题
            if context:
                user_message = f"{context}\n\n用户问题：{user_input}"
            else:
                user_message = user_input

            messages.append(HumanMessage(content=user_message))

            # 4. 调用LLM
            response = self.llm.invoke(messages)
            answer = response.content

            # 5. 更新对话记忆
            self.chat_history.append((user_input, answer))

            return answer

        except Exception as e:
            logger.error(f"对话发生错误: {e}")
            return "抱歉，我遇到了一些问题，请稍后再试。"

    def clear_history(self):
        """清除对话历史"""
        self.chat_history = []
        logger.info("对话历史已清除")


# 创建全局Agent实例
agent_instance = None


def get_agent() -> TCLProductAgent:
    """获取Agent单例"""
    global agent_instance
    if agent_instance is None:
        agent_instance = TCLProductAgent()
    return agent_instance


if __name__ == "__main__":
    # 测试Agent
    agent = TCLProductAgent()

    test_questions = [
        "TCL 55Q10G Pro电视怎么样？",
        "我想买一台5000元左右的电视",
        "55Q10G和55T7G哪个好？"
    ]

    for question in test_questions:
        print(f"\n👤 用户: {question}")
        print(f"🤖 Agent: {agent.chat(question)}")
        print("-" * 50)