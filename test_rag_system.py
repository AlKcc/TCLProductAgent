#!/usr/bin/env python3
"""RAG系统测试脚本"""
import sys
sys.path.insert(0, '/Users/chenkai/Downloads/AGENT_DEMO')

from src.rag.document_loader import DocumentLoader
from src.rag.vectorstore import VectorStore, get_vectorstore
from src.utils.helpers import load_all_products
from pathlib import Path

def test_document_loader():
    """测试文档加载器"""
    print("=" * 60)
    print("测试文档加载器")
    print("=" * 60)
    
    loader = DocumentLoader()
    data_dir = Path('/Users/chenkai/Downloads/AGENT_DEMO/data')
    
    docs = loader.load_all_knowledge(data_dir)
    
    for category, documents in docs.items():
        print(f"\n📂 {category}: {len(documents)} 条文档")
        if documents:
            print(f"示例内容:\n{documents[0][:300]}...")
    
    print("\n" + "=" * 60)

def test_vectorstore():
    """测试向量数据库"""
    print("\n" + "=" * 60)
    print("测试向量数据库")
    print("=" * 60)
    
    vs = get_vectorstore()
    
    # 重置数据库（测试用）
    vs.reset()
    
    # 加载测试文档
    loader = DocumentLoader()
    data_dir = Path('/Users/chenkai/Downloads/AGENT_DEMO/data')
    docs = loader.load_all_knowledge(data_dir)
    
    # 添加所有文档到向量数据库
    all_documents = []
    all_metadatas = []
    
    for category, documents in docs.items():
        for doc in documents:
            all_documents.append(doc)
            all_metadatas.append({"category": category})
    
    if all_documents:
        vs.add_documents("knowledge", all_documents, metadatas=all_metadatas)
        print(f"\n✅ 成功添加 {len(all_documents)} 条文档到向量数据库")
        
        # 查询测试
        test_queries = [
            "Mini LED电视有什么特点？",
            "Q10L Pro和X11L有什么区别？",
            "5000元左右买什么电视？",
            "144Hz刷新率的电视有哪些？"
        ]
        
        for query in test_queries:
            print(f"\n🔍 查询: {query}")
            results = vs.query("knowledge", [query], n_results=2)
            for i, doc in enumerate(results["documents"][0]):
                print(f"  结果{i+1}:\n  {doc[:200]}...")
    else:
        print("\n❌ 没有文档可添加")
    
    print("\n" + "=" * 60)

def test_product_search():
    """测试产品搜索"""
    print("\n" + "=" * 60)
    print("测试产品搜索")
    print("=" * 60)
    
    products = load_all_products()
    
    print(f"\n📦 加载产品总数: {sum(len(v) for v in products.values())} 款")
    
    for category, items in products.items():
        print(f"\n📺 {category}: {len(items)} 款")
        for item in items[:3]:
            print(f"  - {item.get('model', '未知')}: {item.get('basic_params', {}).get('price_range', '')}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_document_loader()
    test_product_search()
    test_vectorstore()
    
    print("\n🎉 所有测试完成！")