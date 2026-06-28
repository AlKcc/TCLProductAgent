"""
辅助函数模块
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from .config import PRODUCTS_DIR, FAQ_DIR, TIPS_DIR


def load_json_file(file_path: Path) -> List[Dict]:
    """加载JSON文件"""
    if not file_path.exists():
        print(f"⚠️  文件不存在: {file_path}")
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_all_products() -> Dict[str, List[Dict]]:
    """加载所有产品数据"""
    products = {
        'tv': [],
        'ac': [],
        'fridge': [],
        'washer': []
    }

    # 加载各品类产品
    products['tv'] = load_json_file(PRODUCTS_DIR / 'tv_products.json')
    products['ac'] = load_json_file(PRODUCTS_DIR / 'ac_products.json')
    products['fridge'] = load_json_file(PRODUCTS_DIR / 'fridge_products.json')
    products['washer'] = load_json_file(PRODUCTS_DIR / 'washer_products.json')

    return products


def load_all_faq() -> List[Dict]:
    """加载FAQ数据"""
    return load_json_file(FAQ_DIR / 'common_faq.json')


def load_all_tips() -> List[Dict]:
    """加载使用技巧数据"""
    return load_json_file(TIPS_DIR / 'usage_tips.json')


def search_product_by_keyword(keyword: str, category: Optional[str] = None) -> List[Dict]:
    """根据关键词搜索产品"""
    products_dict = load_all_products()

    results = []
    categories_to_search = [category] if category else products_dict.keys()

    for cat in categories_to_search:
        for product in products_dict[cat]:
            # 搜索字段
            searchable_text = (
                f"{product.get('model', '')} "
                f"{product.get('series', '')} "
                f"{product.get('description', '')} "
                f"{' '.join(product.get('keywords', []))}"
            ).lower()

            if keyword.lower() in searchable_text:
                results.append(product)

    return results


def filter_products_by_price_range(products: List[Dict], min_price: int, max_price: int) -> List[Dict]:
    """根据价格范围筛选产品"""
    results = []
    for product in products:
        price_range = product.get('basic_params', {}).get('price_range', '')
        # 提取价格范围（简化处理）
        try:
            # 从"5000-6000元"中提取价格
            prices = price_range.replace('元', '').split('-')
            if len(prices) == 2:
                product_min = int(prices[0])
                product_max = int(prices[1])
                # 检查价格区间是否有重叠
                if product_max >= min_price and product_min <= max_price:
                    results.append(product)
        except:
            continue

    return results


def format_product_info(product: Dict) -> str:
    """格式化产品信息"""
    info = f"📺 {product.get('model', '未知型号')}\n"
    info += f"   系列: {product.get('series', '')}\n"
    info += f"   价格: {product.get('basic_params', {}).get('price_range', '未知')}\n"
    info += f"   特点: {'、'.join(product.get('pros', [])[:3])}\n"
    return info


def format_comparison_table(products: List[Dict]) -> str:
    """格式化产品对比表格"""
    if not products:
        return "没有产品可供对比"

    # 表头
    table = "| 项目 | " + " | ".join([p.get('model', '未知') for p in products]) + " |\n"
    table += "|------" + "|------" * len(products) + "|\n"

    # 价格
    table += "| 价格 | " + " | ".join([
        p.get('basic_params', {}).get('price_range', '-')
        for p in products
    ]) + " |\n"

    # 尺寸（如果是电视）
    if products[0].get('category') == '电视':
        table += "| 尺寸 | " + " | ".join([
            p.get('basic_params', {}).get('size', '-')
            for p in products
        ]) + " |\n"

    # 能效（如果是空调）
    if products[0].get('category') == '空调':
        table += "| 能效 | " + " | ".join([
            p.get('tech_params', {}).get('energy_level', '-')
            for p in products
        ]) + " |\n"

    return table


if __name__ == "__main__":
    # 测试函数
    products = load_all_products()
    print(f"加载产品数据: {sum(len(v) for v in products.values())} 款")

    faq = load_all_faq()
    print(f"加载FAQ: {len(faq)} 条")

    tips = load_all_tips()
    print(f"加载使用技巧: {len(tips)} 条")