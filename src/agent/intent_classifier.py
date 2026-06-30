"""
意图识别模块
"""
from typing import Optional
from enum import Enum


class Intent(Enum):
    """用户意图枚举"""
    PRODUCT_QUERY = "product_query"      # 产品查询
    RECOMMENDATION = "recommendation"    # 产品推荐
    COMPARISON = "comparison"            # 产品对比
    TROUBLESHOOTING = "troubleshooting"  # 故障排查
    TIPS = "tips"                        # 使用技巧
    GREETING = "greeting"                # 问候寒暄
    GENERAL_CHAT = "general_chat"        # 日常闲聊


class IntentClassifier:
    """意图分类器"""

    def __init__(self):
        # 意图关键词映射（按优先级排序，优先级高的在前）
        self.intent_keywords = {
            # 最高优先级：问候
            Intent.GREETING: [
                "你好", "您好", "嗨", "hi", "hello", "早上好",
                "下午好", "晚上好", "在吗", "有人在吗", "哈喽"
            ],
            # 第二优先级：故障排查（包含更明确的关键词）
            Intent.TROUBLESHOOTING: [
                "故障", "坏了", "不工作", "不制冷", "不制热",
                "打不开", "噪音", "漏水", "报错", "无法启动",
                "没反应", "失灵", "卡住", "黑屏", "无法连接"
            ],
            # 第三优先级：对比
            Intent.COMPARISON: [
                "对比", "区别", "比较", "差异", "哪个好",
                "选哪个", "对比一下"
            ],
            # 第四优先级：推荐
            Intent.RECOMMENDATION: [
                "推荐", "买什么", "适合", "选购", "想买",
                "建议", "需要"
            ],
            # 第五优先级：使用技巧
            Intent.TIPS: [
                "技巧", "保养", "清洁", "维护", "延长寿命", "节能",
                "如何保养", "怎么保养", "保养方法"
            ],
            # 最低优先级：产品查询
            Intent.PRODUCT_QUERY: [
                "参数", "型号", "怎么样", "好不好", "介绍",
                "详细", "规格", "配置", "性能", "功能", "是什",
                "什么是", "如何使用"
            ]
        }

    def classify(self, user_input: str) -> Intent:
        """
        识别用户意图

        Args:
            user_input: 用户输入

        Returns:
            Intent: 识别出的意图
        """
        user_input = user_input.lower()

        # 遍历所有意图
        max_match_count = 0
        matched_intent = Intent.GENERAL_CHAT

        for intent, keywords in self.intent_keywords.items():
            match_count = sum(1 for kw in keywords if kw in user_input)
            if match_count > max_match_count:
                max_match_count = match_count
                matched_intent = intent

        return matched_intent

    def get_intent_description(self, intent: Intent) -> str:
        """获取意图描述"""
        descriptions = {
            Intent.PRODUCT_QUERY: "产品查询",
            Intent.RECOMMENDATION: "产品推荐",
            Intent.COMPARISON: "产品对比",
            Intent.TROUBLESHOOTING: "故障排查",
            Intent.TIPS: "使用技巧",
            Intent.GREETING: "问候寒暄",
            Intent.GENERAL_CHAT: "日常闲聊"
        }
        return descriptions.get(intent, "未知")


# 创建全局实例
intent_classifier = IntentClassifier()


if __name__ == "__main__":
    # 测试意图识别
    classifier = IntentClassifier()

    test_cases = [
        "TCL 55Q10G Pro电视怎么样？",
        "我想买一台5000元左右的电视，有什么推荐吗？",
        "55Q10G和55T7G哪个好？",
        "空调不制冷怎么办？",
        "电视使用有什么技巧？",
        "你好"
    ]

    for case in test_cases:
        intent = classifier.classify(case)
        desc = classifier.get_intent_description(intent)
        print(f"输入: {case}")
        print(f"意图: {desc} ({intent.value})")
        print()