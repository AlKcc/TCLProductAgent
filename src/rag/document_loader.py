"""
文档加载模块
"""
from typing import List
from pathlib import Path


class DocumentLoader:
    """文档加载器"""

    def __init__(self):
        pass

    def load_from_json(self, file_path: Path) -> List[str]:
        """
        从JSON文件加载文档

        Args:
            file_path: JSON文件路径

        Returns:
            List[str]: 文档文本列表
        """
        import json

        documents = []

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 根据数据类型构建文档
        if isinstance(data, list):
            for item in data:
                doc_text = self._format_json_item(item)
                documents.append(doc_text)

        return documents

    def _format_json_item(self, item: dict) -> str:
        """格式化JSON条目为文本"""
        text = ""

        # 添加标题
        if 'model' in item:
            text += f"【产品型号】{item['model']}\n"
        elif 'question' in item:
            text += f"【问题】{item['question']}\n"
        elif 'title' in item:
            text += f"【{item['title']}】\n"

        # 添加描述
        if 'description' in item:
            text += f"{item['description']}\n"
        elif 'answer' in item:
            text += f"【答案】{item['answer']}\n"
        elif 'content' in item:
            text += f"{item['content']}\n"

        # 添加技术参数
        if 'tech_params' in item:
            text += "【技术参数】\n"
            for key, value in item['tech_params'].items():
                text += f"  {key}: {value}\n"

        # 添加功能特性
        if 'features' in item:
            text += f"【功能特性】{', '.join(item['features'])}\n"

        # 添加优缺点
        if 'pros' in item:
            text += f"【优点】{', '.join(item['pros'])}\n"
        if 'cons' in item:
            text += f"【不足】{', '.join(item['cons'])}\n"

        # 添加关键词
        if 'keywords' in item:
            text += f"【关键词】{', '.join(item['keywords'])}\n"

        return text

    def load_all_knowledge(self, base_dir: Path) -> dict:
        """
        加载所有知识库文档

        Args:
            base_dir: 数据目录

        Returns:
            dict: 分类文档列表
        """
        all_documents = {
            'products': [],
            'faq': [],
            'tips': []
        }

        # 加载产品文档
        products_dir = base_dir / 'products'
        if products_dir.exists():
            for json_file in products_dir.glob('*.json'):
                docs = self.load_from_json(json_file)
                all_documents['products'].extend(docs)

        # 加载FAQ
        faq_file = base_dir / 'faq' / 'common_faq.json'
        if faq_file.exists():
            docs = self.load_from_json(faq_file)
            all_documents['faq'].extend(docs)

        # 加载使用技巧
        tips_file = base_dir / 'tips' / 'usage_tips.json'
        if tips_file.exists():
            docs = self.load_from_json(tips_file)
            all_documents['tips'].extend(docs)

        return all_documents


if __name__ == "__main__":
    # 测试文档加载
    from pathlib import Path

    loader = DocumentLoader()
    data_dir = Path(__file__).parent.parent.parent / 'data'

    docs = loader.load_all_knowledge(data_dir)

    for category, documents in docs.items():
        print(f"{category}: {len(documents)} 条文档")
        if documents:
            print(f"示例: {documents[0][:200]}...")
            print()