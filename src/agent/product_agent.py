"""
TCL产品Agent主逻辑
"""
import os
import random
import re
import time
import hashlib
import difflib
from typing import Optional, List, Dict, Tuple
from collections import OrderedDict
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
from ..rag.langchain_rag import LangChainRAG, LRUCacheWithTTL
from .intent_classifier import Intent, IntentClassifier, intent_classifier


def compute_file_hash(filepath: str) -> str:
    """计算文件SHA256哈希值"""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except Exception:
        return ""


def compute_directory_hash(directory: str) -> str:
    """计算目录下所有文件的综合哈希值"""
    hashes = []
    for root, dirs, files in os.walk(directory):
        for filename in sorted(files):
            filepath = os.path.join(root, filename)
            file_hash = compute_file_hash(filepath)
            if file_hash:
                hashes.append(f"{filepath}:{file_hash}")
    return hashlib.sha256("\n".join(hashes).encode()).hexdigest()


def extract_keywords(query: str) -> set:
    """提取查询中的关键词（中文字符+英文单词+数字）"""
    keywords = set()

    # 提取中文单个字符
    for char in query:
        if '\u4e00' <= char <= '\u9fff':
            keywords.add(char)

    # 提取英文单词和数字
    for word in re.findall(r'[a-zA-Z0-9]+', query.lower()):
        keywords.add(word)

    return keywords


def compute_similarity(query1: str, query2: str) -> float:
    """
    计算两个查询的相似度（结合文本相似度和关键词重叠）

    Returns:
        float: 0.0 - 1.0 之间的相似度
    """
    # 文本相似度
    text_sim = difflib.SequenceMatcher(None, query1.lower(), query2.lower()).ratio()

    # 关键词相似度
    keywords1 = extract_keywords(query1)
    keywords2 = extract_keywords(query2)

    if not keywords1 and not keywords2:
        keyword_sim = 0.0
    elif not keywords1 or not keywords2:
        keyword_sim = 0.0
    else:
        intersection = len(keywords1 & keywords2)
        union = len(keywords1 | keywords2)
        keyword_sim = intersection / union if union > 0 else 0.0

    # 综合相似度（关键词权重更高）
    similarity = text_sim * 0.4 + keyword_sim * 0.6

    return similarity


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
        self.max_history_length = Config.MAX_HISTORY_LENGTH

        # 加载产品数据（带文件哈希校验缓存）
        self.products = load_all_products()
        logger.info(f"TCL产品Agent初始化完成，加载产品数据 {sum(len(v) for v in self.products.values())} 款")

        # 加载多格式文档（PDF/MD/CSV，带文件哈希校验缓存）
        self.document_loader = DocumentLoader()
        self._last_data_hash = ""
        self.documents = self._load_documents()
        logger.info(f"加载多格式文档: {sum(len(v) for v in self.documents.values())} 条")

        # 关键词搜索结果缓存（从配置读取）
        self.search_cache = LRUCacheWithTTL(
            max_size=int(Config.CACHE_MAX_SIZE / 2),
            ttl_seconds=Config.CACHE_TTL_SECONDS
        )

        # LLM最终回答缓存（从配置读取，最大性能提升点）
        self.answer_cache = LRUCacheWithTTL(
            max_size=Config.CACHE_MAX_SIZE,
            ttl_seconds=Config.CACHE_TTL_SECONDS
        )

        # 初始化LangChain RAG（尝试语义检索，失败则自动降级）
        self.langchain_rag = None
        try:
            self.langchain_rag = LangChainRAG(self.llm)
            # 检查RAG是否真的可用（初始化可能超时但对象仍存在）
            if not self.langchain_rag.retriever:
                self.langchain_rag = None
                logger.info("LangChain RAG初始化超时，使用关键词检索作为fallback")
            else:
                logger.info("LangChain RAG语义检索已启用")
        except Exception as e:
            self.langchain_rag = None
            logger.warning(f"LangChain RAG初始化失败，使用关键词检索作为fallback: {e}")

    def _load_documents(self) -> dict:
        """加载所有格式的文档（带文件哈希校验缓存）"""
        current_hash = compute_directory_hash(DATA_DIR)

        # 如果数据目录内容没有变化，跳过重新加载
        if current_hash and current_hash == self._last_data_hash:
            logger.debug("数据目录内容未变化，使用缓存文档")
            return self.documents if hasattr(self, 'documents') else {'products': [], 'docs': [], 'faq': [], 'tips': []}

        try:
            docs = self.document_loader.load_all_knowledge(DATA_DIR)
            self._last_data_hash = current_hash
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
        """搜索相关文档（优先使用LangChain语义检索，失败则使用关键词检索，带缓存）"""
        # 构建缓存key
        cache_key = f"search_{query}_{max_results}"

        # 先尝试从缓存获取
        cached_result = self.search_cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"关键词搜索命中缓存: {query}")
            return cached_result

        # 优先尝试LangChain语义检索（已自带缓存）
        if self.langchain_rag:
            try:
                docs = self.langchain_rag.retrieve(query, k=max_results)
                if docs:
                    logger.debug(f"LangChain语义检索成功，找到 {len(docs)} 条文档")
                    self.search_cache.set(cache_key, docs)
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

        results = [doc for _, doc in scored_results[:max_results]]

        # 将结果存入缓存
        self.search_cache.set(cache_key, results)
        logger.debug(f"关键词搜索结果已缓存: {query}")

        return results

    def _search_with_sources(self, query: str, max_results: int = 3) -> Tuple[List[str], List[Dict]]:
        """
        搜索相关文档并返回来源信息（带缓存）

        Args:
            query: 查询内容
            max_results: 最大结果数

        Returns:
            Tuple[List[str], List[Dict]]: (文档内容列表, 来源信息列表)
        """
        # 构建缓存key
        cache_key = f"search_with_sources_{query}_{max_results}"

        # 先尝试从缓存获取
        cached_result = self.search_cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"搜索带来源命中缓存: {query}")
            return cached_result

        sources = []

        # 优先尝试LangChain语义检索（已自带缓存）
        if self.langchain_rag:
            try:
                docs = self.langchain_rag.retrieve(query, k=max_results)
                if docs:
                    logger.debug(f"LangChain语义检索成功，找到 {len(docs)} 条文档")
                    for i, doc in enumerate(docs):
                        sources.append({
                            "id": i + 1,
                            "type": "文档",
                            "category": "语义检索"
                        })
                    # 将结果存入缓存
                    self.search_cache.set(cache_key, (docs, sources))
                    return docs, sources
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
                    scored_results.append((match_count, doc, category))

        scored_results.sort(key=lambda x: x[0], reverse=True)

        docs = [doc for _, doc, _ in scored_results[:max_results]]

        # 生成来源信息
        for i, (score, doc, category) in enumerate(scored_results[:max_results]):
            if '产品型号' in doc or '型号' in doc:
                doc_type = "产品参数"
            elif '技术原理' in doc or '原理' in doc:
                doc_type = "技术文档"
            elif '问题' in doc and '答案' in doc:
                doc_type = "FAQ问答"
            elif '保修' in doc:
                doc_type = "保修政策"
            elif '使用技巧' in doc or '日常使用' in doc:
                doc_type = "使用技巧"
            elif '上传文档' in doc:
                doc_type = "用户上传"
            else:
                doc_type = f"{category or '知识库'}文档"

            sources.append({
                "id": i + 1,
                "type": doc_type,
                "category": category or "知识库",
                "relevance": f"{min(score, 100)}%"
            })

        # 将结果存入缓存
        self.search_cache.set(cache_key, (docs, sources))
        logger.debug(f"搜索带来源结果已缓存: {query}")

        return docs, sources

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

    def _build_context(self, user_input: str, intent: Intent) -> Tuple[str, List[Dict]]:
        """
        构建上下文信息（扩展版：包含产品数据+多格式文档+来源信息）

        Returns:
            Tuple[str, List[Dict]]: (上下文文本, 来源信息列表)
        """
        context = ""
        sources = []

        # 1. 搜索相关产品
        if intent in [Intent.PRODUCT_QUERY, Intent.RECOMMENDATION, Intent.COMPARISON]:
            products = search_product_by_keyword(user_input)
            if products:
                context += f"\n【相关产品信息】\n"
                for i, product in enumerate(products[:3], 1):
                    context += f"【产品{i}】\n{format_product_info(product)}\n"
                    sources.append({
                        "id": i,
                        "type": "产品数据",
                        "name": product.get('model', '未知型号'),
                        "category": "产品库"
                    })

        # 2. 搜索多格式文档（使用带来源的搜索）
        relevant_docs, doc_sources = self._search_with_sources(user_input, max_results=3)
        if relevant_docs:
            context += self._format_document_for_context(relevant_docs, max_docs=3)
            sources.extend(doc_sources)

        # 3. 推荐场景：智能筛选和排序相关产品
        if intent == Intent.RECOMMENDATION:
            # 提取用户需求中的关键信息
            user_lower = user_input.lower()

            # 智能识别产品类型
            product_type = None
            if any(kw in user_lower for kw in ['电视', 'tv', 'q10', 't7', 'q9', 'v8', 'p11']):
                product_type = 'tv'
            elif any(kw in user_lower for kw in ['空调', 'ac', '空调器']):
                product_type = 'ac'
            elif any(kw in user_lower for kw in ['冰箱', 'fridge', '冷藏']):
                product_type = 'fridge'
            elif any(kw in user_lower for kw in ['洗衣机', 'washer', '洗衣']):
                product_type = 'washer'

            # 提取价格范围
            import re
            price_pattern = r'(\d+)[-~到至](\d+)|(\d+)元|预算(\d+)|(\d+)左右'
            price_match = re.search(price_pattern, user_lower)

            min_price, max_price = None, None
            if price_match:
                if price_match.group(1) and price_match.group(2):
                    min_price = int(price_match.group(1))
                    max_price = int(price_match.group(2))
                else:
                    # 单个数字，设置±1000的范围
                    price = int(price_match.group(3) or price_match.group(4) or price_match.group(5))
                    min_price = max(0, price - 1000)
                    max_price = price + 1000

            # 智能筛选产品
            filtered_products = []
            for category, products in self.products.items():
                if product_type and category != product_type:
                    continue

                for product in products:
                    relevance_score = 0

                    # 价格匹配度
                    if min_price and max_price:
                        price_range = product.get('basic_params', {}).get('price_range', '')
                        try:
                            prices = price_range.replace('元', '').split('-')
                            if len(prices) == 2:
                                product_min = int(prices[0])
                                product_max = int(prices[1])
                                # 价格区间重叠度
                                if product_max >= min_price and product_min <= max_price:
                                    overlap = min(product_max, max_price) - max(product_min, min_price)
                                    relevance_score += overlap / (max_price - min_price) * 50
                        except:
                            pass

                    # 关键词匹配度
                    product_text = f"{product.get('model', '')} {product.get('series', '')} {' '.join(product.get('keywords', []))}".lower()
                    for word in user_lower.split():
                        if word in product_text:
                            relevance_score += 10

                    if relevance_score > 0 or (not min_price and not product_type):
                        filtered_products.append((relevance_score, product))

            # 按相关度排序，只保留相关度高的产品
            filtered_products.sort(key=lambda x: x[0], reverse=True)
            top_products = [p for score, p in filtered_products[:5] if score > 0]

            if top_products:
                context += "\n【推荐产品列表】\n"
                category_names = {'tv': '电视', 'ac': '空调', 'fridge': '冰箱', 'washer': '洗衣机'}
                for i, product in enumerate(top_products, 1):
                    model = product.get('model', '')
                    price = product.get('basic_params', {}).get('price_range', '')
                    category = None
                    for cat, prods in self.products.items():
                        if product in prods:
                            category = cat
                            break
                    cat_name = category_names.get(category, '产品')
                    context += f"{i}. {cat_name} - {model} ({price})\n"

                # 只添加相关产品的来源信息
                for i, product in enumerate(top_products[:3], 1):
                    # 检查是否已经在sources中，避免重复
                    model = product.get('model', '')
                    if not any(src.get('name') == model for src in sources):
                        sources.append({
                            "id": len(sources) + 1,
                            "type": "推荐产品",
                            "name": model,
                            "category": "产品库",
                            "relevance": "高"
                        })
            else:
                # 如果没有筛选出产品，列出所有产品
                context += "\n【可用产品列表】\n"
                for category, products in self.products.items():
                    category_names = {'tv': '电视', 'ac': '空调', 'fridge': '冰箱', 'washer': '洗衣机'}
                    context += f"\n{category_names.get(category, category)}:\n"
                    for product in products:
                        context += f"- {product.get('model', '')}: {product.get('basic_params', {}).get('price_range', '')}\n"

        return context, sources

    def chat(self, user_input: str) -> str:
        """
        与Agent对话（带LLM回答缓存）

        Args:
            user_input: 用户输入

        Returns:
            str: Agent回复（包含来源引用）
        """
        try:
            # 1. 意图识别
            intent = self.intent_classifier.classify(user_input)
            logger.info(f"用户意图: {intent.value} - {user_input}")

            # 2. 如果是问候类意图，直接返回友好回复（不搜索文档）
            if intent == Intent.GREETING:
                greetings = [
                    "您好！我是TCL产品智能助手，很高兴为您服务。有什么关于TCL产品的问题我可以帮您解答？",
                    "你好！我是TCL产品咨询专家，可以为您解答关于TCL电视、空调、冰箱、洗衣机等产品的任何问题。",
                    "您好！有什么关于TCL产品的问题想了解吗？我可以为您提供产品查询、推荐、对比等服务。"
                ]
                return random.choice(greetings)

            # 3. 尝试从LLM回答缓存获取（支持相似度匹配，最大性能提升点）
            cached_answer = None
            cache_match_info = ""

            # 先尝试完全匹配
            answer_cache_key = f"answer_{user_input}"
            exact_match = self.answer_cache.get(answer_cache_key)
            if exact_match is not None:
                cached_answer = exact_match
                cache_match_info = f"完全匹配: {user_input}"

            # 如果没有完全匹配，尝试相似度匹配
            if cached_answer is None:
                best_similarity = 0.0
                best_match_key = None

                # 遍历缓存寻找相似查询
                for cache_key in list(self.answer_cache.cache.keys()):
                    # 缓存key格式: "answer_{原始查询}"
                    if cache_key.startswith("answer_"):
                        cached_query = cache_key[7:]  # 去掉"answer_"前缀
                        similarity = compute_similarity(user_input, cached_query)

                        if similarity > best_similarity:
                            best_similarity = similarity
                            best_match_key = cache_key

                # 如果相似度超过阈值（0.6），使用缓存答案
                if best_similarity >= 0.6 and best_match_key:
                    cached_answer = self.answer_cache.get(best_match_key)
                    cache_match_info = f"相似度匹配({best_similarity:.2f}): '{user_input}' ~ '{best_match_key[7:]}'"

            if cached_answer is not None:
                logger.info(f"LLM回答命中缓存 - {cache_match_info}")

                # 将当前查询也存入缓存，指向同一个答案
                self.answer_cache.set(answer_cache_key, cached_answer)

                self.chat_history.append((user_input, cached_answer))
                self._trim_history()
                return cached_answer

            # 4. 构建上下文（包含来源信息）
            context, sources = self._build_context(user_input, intent)

            # 5. 过滤低相关度来源（低于10%的来源不展示）
            min_relevance = 10
            filtered_sources = []
            for src in sources:
                relevance = src.get('relevance', '')
                if relevance:
                    try:
                        relevance_num = int(relevance.replace('%', ''))
                        if relevance_num >= min_relevance:
                            filtered_sources.append(src)
                    except:
                        filtered_sources.append(src)
                else:
                    filtered_sources.append(src)

            # 6. 重新分配连续编号
            for i, src in enumerate(filtered_sources, 1):
                src['id'] = i

            # 7. 修改系统提示词，要求引用来源
            system_prompt = self._create_system_message(intent)
            if filtered_sources:
                source_ref_prompt = f"""

【来源引用要求】
根据以下信息回答问题时，请务必在回答末尾引用来源：
{self._format_sources(filtered_sources)}

引用格式示例：
📚 **参考来源**：
- [1] 产品数据 - Q10L Pro
- [2] 技术文档 - Mini LED原理"""
                system_prompt += source_ref_prompt

            # 8. 构建消息
            messages: List = [
                SystemMessage(content=system_prompt),
            ]

            # 添加对话历史（只取最近5条，避免token过多）
            for human_msg, ai_msg in self.chat_history[-5:]:
                messages.append(HumanMessage(content=human_msg))
                messages.append(AIMessage(content=ai_msg))

            # 添加当前问题
            if context:
                user_message = f"{context}\n\n用户问题：{user_input}"
            else:
                user_message = user_input

            messages.append(HumanMessage(content=user_message))

            # 9. 调用LLM
            response = self.llm.invoke(messages)
            answer = response.content

            # 10. 如果没有来源，不添加引用；否则在末尾添加来源摘要
            if filtered_sources and "参考来源" not in answer:
                answer += self._format_sources_section(filtered_sources)

            # 11. 将最终回答存入缓存
            self.answer_cache.set(answer_cache_key, answer)
            logger.info(f"LLM回答已缓存: {user_input}")

            # 12. 更新对话记忆并限制长度
            self.chat_history.append((user_input, answer))
            self._trim_history()

            return answer

        except Exception as e:
            logger.error(f"对话发生错误: {e}")
            return "抱歉，我遇到了一些问题，请稍后再试。"

    def _trim_history(self):
        """限制对话历史长度，避免内存和token膨胀"""
        if len(self.chat_history) > self.max_history_length:
            self.chat_history = self.chat_history[-self.max_history_length:]

    def _format_sources(self, sources: List[Dict]) -> str:
        """格式化来源信息（用于提示词）"""
        lines = []
        for src in sources[:5]:  # 最多显示5个来源
            lines.append(f"- [{src.get('id', '?')}] {src.get('type', '文档')} - {src.get('name', src.get('category', '未知'))}")
        return "\n".join(lines) if lines else "无"

    def _format_sources_section(self, sources: List[Dict]) -> str:
        """格式化来源信息（用于回答末尾）"""
        if not sources:
            return ""

        section = "\n\n---\n📚 **参考来源**：\n"

        # 去重并重新编号
        seen = set()
        unique_sources = []
        for src in sources[:5]:
            key = f"{src.get('type')}_{src.get('name', src.get('category', ''))}"
            if key not in seen:
                seen.add(key)
                unique_sources.append(src)

        # 重新连续编号
        for i, src in enumerate(unique_sources, 1):
            type_name = src.get('type', '文档')
            name = src.get('name', src.get('category', '未知'))
            relevance = src.get('relevance', '')

            if relevance:
                section += f"- [{i}] {type_name} - {name} (相关度: {relevance})\n"
            else:
                section += f"- [{i}] {type_name} - {name}\n"

        return section

    def clear_history(self):
        """清除对话历史"""
        self.chat_history = []
        logger.info("对话历史已清除")

    def add_document(self, file_name: str, content: str, category: str = 'uploads') -> Dict:
        """
        添加上传的文档到知识库

        Args:
            file_name: 文件名
            content: 文件内容
            category: 文档类别，默认为'uploads'

        Returns:
            Dict: 操作结果
        """
        try:
            # 如果documents中没有uploads类别，则创建
            if 'uploads' not in self.documents:
                self.documents['uploads'] = []

            # 根据文件扩展名格式化内容
            file_ext = file_name.lower().split('.')[-1] if '.' in file_name else ''

            formatted_content = f"【上传文档】{file_name}\n{'-'*40}\n"

            if file_ext in ['json']:
                # 尝试解析JSON
                import json
                try:
                    data = json.loads(content)
                    if isinstance(data, list):
                        for item in data:
                            formatted_content += self.document_loader._format_json_item(item) + "\n"
                    else:
                        formatted_content += content
                except:
                    formatted_content += content
            else:
                # 其他格式直接添加
                formatted_content += content[:5000]  # 限制长度

            # 添加到文档库
            self.documents['uploads'].append(formatted_content)
            logger.info(f"已添加上传文档到知识库: {file_name}")

            return {
                "success": True,
                "file_name": file_name,
                "total_docs": len(self.documents['uploads']),
                "message": f"文档 '{file_name}' 已成功添加到知识库！"
            }

        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            return {
                "success": False,
                "file_name": file_name,
                "message": f"添加文档失败: {str(e)}"
            }

    def get_uploaded_docs_count(self) -> int:
        """获取已上传文档数量"""
        return len(self.documents.get('uploads', []))


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