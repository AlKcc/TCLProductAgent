#!/usr/bin/env python3
"""TCL官网产品数据爬虫"""
import requests
import json
import os
from bs4 import BeautifulSoup
from typing import List, Dict

BASE_URL = "https://www.tcl.com"
TV_CATEGORY_URL = "https://www.tcl.com/cn/zh/tvs?mini-led-screen"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
}


def fetch_page(url: str) -> str:
    """获取页面内容"""
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = "utf-8"
        return response.text
    except Exception as e:
        print(f"获取页面失败: {url} - {e}")
        return ""


def parse_product_list(html: str) -> List[Dict]:
    """解析产品列表页"""
    soup = BeautifulSoup(html, "html.parser")
    products = []

    # 查找产品卡片
    product_cards = soup.find_all("div", class_=["product-card", "product-item", "col-md-4", "col-lg-3"])
    
    if not product_cards:
        # 尝试其他选择器
        links = soup.find_all("a", href=True)
        for link in links:
            href = link.get("href")
            if "/tvs/" in href and "inch" in href:
                products.append({
                    "url": BASE_URL + href if href.startswith("/") else href,
                    "name": link.get_text(strip=True) or "未知产品"
                })
    
    return products


def parse_product_detail(url: str, html: str) -> Dict:
    """解析产品详情页"""
    soup = BeautifulSoup(html, "html.parser")
    
    product = {
        "url": url,
        "model": "",
        "category": "电视",
        "series": "",
        "description": "",
        "features": [],
        "tech_params": {},
        "basic_params": {}
    }

    # 获取产品名称
    title_tag = soup.find("h1") or soup.find("h2")
    if title_tag:
        product["model"] = title_tag.get_text(strip=True)

    # 获取产品描述
    desc_tags = soup.find_all("p")
    for desc in desc_tags:
        text = desc.get_text(strip=True)
        if len(text) > 50 and len(text) < 500:
            product["description"] = text
            break

    # 获取功能特性（通常是列表形式）
    feature_lists = soup.find_all(["ul", "ol"])
    for ul in feature_lists:
        items = ul.find_all("li")
        features = []
        for li in items:
            text = li.get_text(strip=True)
            if text and len(text) < 100:
                features.append(text)
        if features and len(features) <= 10:
            product["features"] = features

    # 获取技术参数（从页面中的加粗文字和参数表格）
    strong_tags = soup.find_all("strong")
    for strong in strong_tags:
        text = strong.get_text(strip=True)
        if len(text) > 2 and len(text) < 30:
            next_sibling = strong.next_sibling
            if next_sibling:
                value = next_sibling.get_text(strip=True) if hasattr(next_sibling, "get_text") else str(next_sibling).strip()
                if value and len(value) < 100:
                    product["tech_params"][text] = value

    # 尝试解析规格参数表格
    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) == 2:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                if key and value:
                    product["basic_params"][key] = value

    # 从URL提取尺寸信息
    if "inch" in url.lower():
        import re
        match = re.search(r"(\d+)-inch", url.lower())
        if match:
            product["basic_params"]["尺寸"] = f"{match.group(1)}英寸"

    return product


def save_products(products: List[Dict], filename: str):
    """保存产品数据到JSON文件"""
    output_dir = os.path.dirname(filename)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print(f"已保存 {len(products)} 条产品数据到 {filename}")


def main():
    """主函数"""
    print("=" * 60)
    print("TCL官网产品数据爬虫")
    print("=" * 60)
    
    # 获取产品列表页
    print("\n1. 获取产品列表...")
    list_html = fetch_page(TV_CATEGORY_URL)
    if not list_html:
        print("无法获取产品列表页")
        return

    # 解析产品列表
    print("2. 解析产品列表...")
    product_links = parse_product_list(list_html)
    print(f"找到 {len(product_links)} 个产品")

    # 获取产品详情
    print("\n3. 获取产品详情...")
    products = []
    for i, item in enumerate(product_links[:10], 1):  # 限制获取数量
        print(f"  [{i}/{len(product_links)}] 获取: {item['name']}")
        detail_html = fetch_page(item["url"])
        if detail_html:
            product = parse_product_detail(item["url"], detail_html)
            if product["model"]:
                products.append(product)

    # 保存数据
    print("\n4. 保存产品数据...")
    save_products(products, "data/products/tv_products_scraped.json")

    print("\n" + "=" * 60)
    print(f"爬取完成！共获取 {len(products)} 条电视产品数据")
    print("=" * 60)


if __name__ == "__main__":
    main()