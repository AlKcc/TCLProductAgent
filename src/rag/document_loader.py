"""
文档加载模块 - 支持多格式文档
"""
from typing import List, Tuple
from pathlib import Path


class DocumentLoader:
    """文档加载器 - 支持JSON、PDF、Markdown、CSV"""

    def __init__(self):
        pass

    def load_from_json(self, file_path: Path) -> List[str]:
        """从JSON文件加载文档"""
        import json

        documents = []

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list):
            for item in data:
                doc_text = self._format_json_item(item)
                documents.append(doc_text)

        return documents

    def _format_json_item(self, item: dict) -> str:
        """格式化JSON条目为文本"""
        text = ""

        if 'model' in item:
            text += f"【产品型号】{item['model']}\n"
        elif 'question' in item:
            text += f"【问题】{item['question']}\n"
        elif 'title' in item:
            text += f"【{item['title']}】\n"

        if 'description' in item:
            text += f"{item['description']}\n"
        elif 'answer' in item:
            text += f"【答案】{item['answer']}\n"
        elif 'content' in item:
            text += f"{item['content']}\n"

        if 'basic_params' in item:
            text += "【基本参数】\n"
            for key, value in item['basic_params'].items():
                text += f"  {key}: {value}\n"

        if 'tech_params' in item:
            text += "【技术参数】\n"
            for key, value in item['tech_params'].items():
                text += f"  {key}: {value}\n"

        if 'warranty' in item:
            text += f"【保修政策】{item['warranty']}\n"

        if 'features' in item:
            text += f"【功能特性】{', '.join(item['features'])}\n"

        if 'pros' in item:
            text += f"【优点】{', '.join(item['pros'])}\n"
        if 'cons' in item:
            text += f"【不足】{', '.join(item['cons'])}\n"

        if 'keywords' in item:
            text += f"【关键词】{', '.join(item['keywords'])}\n"

        return text

    def load_from_pdf(self, file_path: Path) -> List[str]:
        """从PDF文件加载文档"""
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(str(file_path))
            documents = []
            for page in reader.pages:
                text = page.extract_text()
                if text and text.strip():
                    documents.append(text.strip())
            return documents
        except ImportError:
            print("⚠️ PyPDF2未安装，无法加载PDF文件")
            return []
        except Exception as e:
            print(f"⚠️ 加载PDF文件失败: {e}")
            return []

    def load_from_md(self, file_path: Path) -> List[str]:
        """从Markdown文件加载文档"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return [content]
        except Exception as e:
            print(f"⚠️ 加载Markdown文件失败: {e}")
            return []

    def load_from_csv(self, file_path: Path) -> List[str]:
        """从CSV文件加载文档"""
        try:
            import csv
            documents = []
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row:
                        doc_text = "【产品参数】\n"
                        for key, value in row.items():
                            doc_text += f"  {key}: {value}\n"
                        documents.append(doc_text)
            return documents
        except ImportError:
            print("⚠️ csv模块不可用")
            return []
        except Exception as e:
            print(f"⚠️ 加载CSV文件失败: {e}")
            return []

    def load_file(self, file_path: Path) -> List[str]:
        """根据文件扩展名自动选择加载方式"""
        ext = file_path.suffix.lower()

        if ext == '.json':
            return self.load_from_json(file_path)
        elif ext == '.pdf':
            return self.load_from_pdf(file_path)
        elif ext == '.md':
            return self.load_from_md(file_path)
        elif ext == '.csv':
            return self.load_from_csv(file_path)
        else:
            print(f"⚠️ 不支持的文件格式: {ext}")
            return []

    def load_all_knowledge(self, base_dir: Path) -> dict:
        """加载所有知识库文档（支持多格式）"""
        all_documents = {
            'products': [],
            'docs': [],
            'faq': [],
            'tips': []
        }

        products_dir = base_dir / 'products'
        if products_dir.exists():
            for file in products_dir.glob('*'):
                if file.is_file():
                    docs = self.load_file(file)
                    all_documents['products'].extend(docs)

        docs_dir = base_dir / 'docs'
        if docs_dir.exists():
            for file in docs_dir.glob('*'):
                if file.is_file():
                    docs = self.load_file(file)
                    all_documents['docs'].extend(docs)

        faq_file = base_dir / 'faq' / 'common_faq.json'
        if faq_file.exists():
            docs = self.load_from_json(faq_file)
            all_documents['faq'].extend(docs)

        tips_file = base_dir / 'tips' / 'usage_tips.json'
        if tips_file.exists():
            docs = self.load_from_json(tips_file)
            all_documents['tips'].extend(docs)

        return all_documents


if __name__ == "__main__":
    from pathlib import Path

    loader = DocumentLoader()
    data_dir = Path(__file__).parent.parent.parent / 'data'

    docs = loader.load_all_knowledge(data_dir)

    for category, documents in docs.items():
        print(f"{category}: {len(documents)} 条文档")
        if documents:
            print(f"示例: {documents[0][:200]}...")
            print()