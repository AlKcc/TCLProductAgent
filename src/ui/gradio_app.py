"""
Gradio Web界面
"""
import gradio as gr
from typing import List, Tuple

from ..agent.product_agent import TCLProductAgent, get_agent
from ..utils.logger import logger


class GradioInterface:
    """Gradio界面类"""

    def __init__(self):
        """初始化界面"""
        self.agent = get_agent()
        self.chat_history: List[Tuple[str, str]] = []

    def chat_response(self, user_input: str, history: List[Tuple[str, str]]) -> Tuple[str, List[Tuple[str, str]]]:
        """
        处理用户输入并返回响应

        Args:
            user_input: 用户输入
            history: 对话历史

        Returns:
            Tuple[str, List[Tuple[str, str]]]: (新回复, 更新后的历史)
        """
        try:
            # 调用Agent
            response = self.agent.chat(user_input)

            # 更新历史
            new_history = history + [(user_input, response)]

            logger.info(f"用户: {user_input}")
            logger.info(f"Agent: {response[:100]}...")

            return response, new_history

        except Exception as e:
            error_msg = f"抱歉，发生错误: {str(e)}"
            logger.error(error_msg)
            return error_msg, history

    def clear_chat(self, history: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """清除对话"""
        self.agent.clear_history()
        logger.info("对话已清除")
        return []

    def create_interface(self):
        """创建Gradio界面"""
        with gr.Blocks(title="TCL智能产品咨询助手", theme=gr.themes.Soft()) as app:
            gr.Markdown("""
            # 🏢 TCL智能产品咨询助手

            基于GLM-4大模型和LangChain框架的智能客服Agent系统

            ### 功能介绍
            - 📺 **产品查询**: 了解TCL电视、空调、冰箱、洗衣机等产品的详细信息
            - 🎯 **智能推荐**: 根据您的需求推荐最合适的TCL产品
            - 📊 **产品对比**: 对比不同型号的参数和优缺点
            - 🔧 **故障排查**: 提供产品故障的自助排查建议
            - 💡 **使用技巧**: 获取产品使用和保养的专业建议

            ### 使用提示
            - 可以直接提问，例如："TCL 55Q10G Pro怎么样？"
            - 可以描述需求，例如："预算5000元，买什么电视？"
            - 可以要求对比，例如："55Q10G和55T7G哪个好？"
            """)

            with gr.Row():
                with gr.Column(scale=4):
                    chatbot = gr.Chatbot(
                        label="对话历史",
                        height=500,
                        show_copy_button=True,
                        bubble_full_width=False
                    )

                    with gr.Row():
                        user_input = gr.Textbox(
                            label="请输入您的问题",
                            placeholder="例如：TCL 55Q10G Pro电视怎么样？",
                            scale=9
                        )
                        submit_btn = gr.Button("发送", scale=1, variant="primary")

                    with gr.Row():
                        clear_btn = gr.Button("清除对话", scale=1)
                        example_btn = gr.Button("示例问题", scale=1)

                with gr.Column(scale=1):
                    gr.Markdown("### 快捷功能")
                    with gr.Accordion("产品类别", open=True):
                        tv_btn = gr.Button("📺 电视")
                        ac_btn = gr.Button("❄️ 空调")
                        fridge_btn = gr.Button("🧊 冰箱")
                        washer_btn = gr.Button("🧺 洗衣机")

                    gr.Markdown("### 常见问题")
                    with gr.Accordion("快速提问", open=False):
                        q1 = gr.Button("Mini LED是什么？")
                        q2 = gr.Button("空调一级能效和三级区别？")
                        q3 = gr.Button("风冷和直冷冰箱区别？")

                    gr.Markdown("### 示例对话")
                    examples = gr.Examples(
                        examples=[
                            "TCL 55Q10G Pro电视怎么样？",
                            "我想买一台5000元左右的电视，有什么推荐吗？",
                            "55Q10G和55T7G哪个好？",
                            "空调不制冷怎么办？",
                            "电视使用有什么技巧？"
                        ],
                        inputs=user_input,
                        label="点击示例快速输入"
                    )

            # 绑定事件
            submit_btn.click(
                self.chat_response,
                inputs=[user_input, chatbot],
                outputs=[user_input, chatbot]
            )

            user_input.submit(
                self.chat_response,
                inputs=[user_input, chatbot],
                outputs=[user_input, chatbot]
            )

            clear_btn.click(
                self.clear_chat,
                inputs=[chatbot],
                outputs=[chatbot]
            )

            example_btn.click(
                lambda: gr.Examples.update(selected=0),
                inputs=None,
                outputs=None
            )

        return app


def create_gradio_app() -> gr.Blocks:
    """
    创建Gradio应用

    Returns:
        gr.Blocks: Gradio应用实例
    """
    interface = GradioInterface()
    return interface.create_interface()


if __name__ == "__main__":
    # 创建并启动应用
    app = create_gradio_app()

    # 启动服务
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )