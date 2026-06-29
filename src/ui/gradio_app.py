"""
Gradio Web界面
"""
import gradio as gr
from typing import List, Dict, Tuple

from ..agent.product_agent import TCLProductAgent, get_agent
from ..utils.logger import logger


class GradioInterface:
    """Gradio界面类"""

    def __init__(self):
        """初始化界面"""
        self.agent = get_agent()
        self.chat_history: List[Dict] = []
        self.uploaded_files_status = gr.State(value="暂无上传文档")

    def chat_response(self, user_input: str, history: List[Dict]) -> Tuple[str, List[Dict]]:
        """
        处理用户输入并返回响应

        Args:
            user_input: 用户输入
            history: 对话历史

        Returns:
            Tuple[str, List[Dict]]: (清空输入框, 更新后的历史)
        """
        try:
            # 调用Agent
            response = self.agent.chat(user_input)

            # 更新历史 - Gradio 6.x 需要字典格式
            new_history = history + [
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": response}
            ]

            logger.info(f"用户: {user_input}")
            logger.info(f"Agent: {response[:100]}...")

            return "", new_history

        except Exception as e:
            error_msg = f"抱歉，发生错误: {str(e)}"
            logger.error(error_msg)
            return "", history + [
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": error_msg}
            ]

    def handle_file_upload(self, file):
        """
        处理文件上传

        Args:
            file: 上传的文件对象

        Returns:
            str: 上传结果消息
        """
        if file is None:
            return "⚠️ 未选择文件"

        try:
            # 读取文件内容
            if hasattr(file, 'name'):
                # 从文件路径读取
                file_path = file.name
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                file_name = file_path.split('/')[-1]
            else:
                content = str(file)
                file_name = "uploaded_file"

            # 添加到Agent知识库
            result = self.agent.add_document(file_name, content)

            if result['success']:
                uploaded_count = self.agent.get_uploaded_docs_count()
                return f"""✅ 上传成功！

📄 文件名: {file_name}
📊 当前知识库文档数: {uploaded_count} 条

文档已添加到知识库，现在可以询问相关内容了！"""

            return f"""❌ 上传失败

{result['message']}"""

        except UnicodeDecodeError:
            return "❌ 文件读取失败：无法识别的编码格式，请确保文件为UTF-8编码"
        except Exception as e:
            logger.error(f"文件上传处理失败: {e}")
            return f"❌ 文件处理失败: {str(e)}"

    def clear_chat(self, history: List[Dict]) -> List[Dict]:
        """清除对话"""
        self.agent.clear_history()
        logger.info("对话已清除")
        return []

    def create_interface(self):
        """创建Gradio界面"""
        with gr.Blocks(title="TCL智能产品咨询助手") as app:
            gr.Markdown("""
            # 🏢 TCL智能产品咨询助手

            基于GLM-4大模型和LangChain框架的智能客服Agent系统

            ### 功能介绍
            - 📺 **产品查询**: 了解TCL电视、空调、冰箱、洗衣机等产品的详细信息
            - 🎯 **智能推荐**: 根据您的需求推荐最合适的TCL产品
            - 📊 **产品对比**: 对比不同型号的参数和优缺点
            - 🔧 **故障排查**: 提供产品故障的自助排查建议
            - 💡 **使用技巧**: 获取产品使用和保养的专业建议
            - 📤 **文档上传**: 支持上传JSON/MD/TXT文档，扩展知识库
            """)

            with gr.Row():
                with gr.Column(scale=4):
                    chatbot = gr.Chatbot(
                        label="对话历史",
                        height=500
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

                with gr.Column(scale=1):
                    # 文档上传区域
                    gr.Markdown("### 📤 文档上传")
                    gr.Markdown("上传JSON/MD/TXT文档，自动添加到知识库")

                    with gr.Accordion("支持格式", open=False):
                        gr.Markdown("""
                        - **JSON**: 产品数据、FAQ等结构化数据
                        - **Markdown**: 技术文档、说明书等
                        - **TXT**: 纯文本格式
                        """)

                    file_output = gr.Textbox(
                        label="上传状态",
                        lines=3,
                        interactive=False,
                        value="请上传文档..."
                    )

                    file_input = gr.File(
                        label="选择文件",
                        file_count="single",
                        file_types=[".json", ".md", ".txt", ".csv"],
                        height=100
                    )

                    upload_btn = gr.Button("上传到知识库", variant="primary")

                    upload_btn.click(
                        self.handle_file_upload,
                        inputs=[file_input],
                        outputs=[file_output]
                    )

                    # 快捷功能
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