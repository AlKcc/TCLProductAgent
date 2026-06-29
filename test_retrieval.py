#!/usr/bin/env python3
"""测试文档检索功能"""
import sys
sys.path.insert(0, '/Users/chenkai/Downloads/AGENT_DEMO')

from src.rag.document_loader import DocumentLoader
from src.agent.product_agent import TCLProductAgent
from pathlib import Path

def test_document_search():
    """测试文档检索"""
    print("=" * 60)
    print("测试文档检索功能")
    print("=" * 60)

    # 创建Agent实例
    agent = TCLProductAgent()

    # 测试查询
    test_queries = [
        "保修",
        "warranty",
        "Mini LED",
        "Q10L Pro",
        "144Hz"
    ]

    for query in test_queries:
        print(f"\n🔍 查询关键词: '{query}'")
        docs = agent._search_documents(query, max_results=2)

        if docs:
            print(f"✅ 检索到 {len(docs)} 条文档")
            for i, doc in enumerate(docs):
                preview = doc[:200] + "..." if len(doc) > 200 else doc
                print(f"\n文档{i+1}预览:\n{preview}\n")
        else:
            print(f"❌ 未找到相关文档")

    print("\n" + "=" * 60)

def test_context_building():
    """测试上下文构建"""
    print("\n" + "=" * 60)
    print("测试上下文构建")
    print("=" * 60)

    agent = TCLProductAgent()

    query = "TCL电视保修政策是什么？"
    print(f"\n问题: {query}")

    # 获取意图
    from src.agent.intent_classifier import intent_classifier
    intent = intent_classifier.classify(query)
    print(f"意图: {intent.value}")

    # 构建上下文
    context = agent._build_context(query, intent)
    print(f"\n构建的上下文:\n{context}\n")

    print("=" * 60)

if __name__ == "__main__":
    test_document_search()
    test_context_building()