# TCL智能产品咨询助手 (TCL Product Agent)

<p align="center">
  <h3>基于 LangChain 和 GLM-4 的智能客服 Agent 系统</h3>
  <p>AI应用创新大赛 - 赛道一：智能体（Agent）构建</p>
</p>

***

## 📋 项目简介

TCL智能产品咨询助手是一个基于大语言模型的智能客服系统，能够帮助用户：

- 📺 查询TCL产品信息（电视、空调、冰箱、洗衣机）
- 🎯 获取智能产品推荐
- 📊 对比不同产品型号
- 🔧 排查产品故障
- 💡 获取使用技巧和保养建议

***

## 🎯 核心功能

### 1. 产品知识问答

基于RAG（检索增强生成）技术，提供准确的产品信息查询服务

### 2. 智能产品推荐

根据用户需求（预算、用途、空间等）推荐最合适的产品

### 3. 产品参数对比

多维度对比产品参数，生成对比表格和购买建议

### 4. 故障排查指导

提供产品故障的自助排查步骤和建议

### 5. 使用技巧建议

提供产品使用技巧和保养建议

***

## 🏗️ 技术架构

```
用户交互层 (Gradio) → Agent核心层 (LangChain) → 知识存储层 (ChromaDB)
                      ↓
                 GLM-4-Flash (智谱AI)
```

### 技术栈

| 组件      | 技术                 |
| ------- | ------------------ |
| 大语言模型   | GLM-4-Flash (智谱AI) |
| Agent框架 | LangChain          |
| 向量数据库   | ChromaDB           |
| Web界面   | Gradio             |
| 编程语言    | Python 3.12+       |

***

## 📁 项目结构

```
TCLProductAgent/
├── docs/                    # 文档
│   └── 技术方案文档.md       # 详细技术方案
├── data/                    # 数据
│   ├── products/            # 产品数据
│   ├── faq/                 # FAQ知识库
│   └── tips/                # 使用技巧
├── src/                     # 源代码
│   ├── agent/               # Agent核心模块
│   │   ├── product_agent.py # Agent主逻辑
│   │   └── intent_classifier.py  # 意图识别
│   ├── rag/                 # RAG检索模块
│   │   ├── document_loader.py   # 文档加载
│   │   ├── vectorstore.py       # 向量存储
│   │   └── retriever.py         # 知识检索
│   ├── ui/                  # 用户界面
│   │   └── gradio_app.py    # Gradio界面
│   ├── utils/               # 工具模块
│   │   ├── config.py        # 配置管理
│   │   ├── logger.py        # 日志工具
│   │   └── helpers.py       # 辅助函数
│   └── app.py               # 程序入口
├── tests/                   # 测试
├── demo/                    # Demo材料
├── requirements.txt         # Python依赖
├── README.md                # 项目说明
└── .env.example             # 环境变量示例
```

***

## 🚀 快速开始

### 1. 环境准备

```bash
# 创建Python环境
conda create -n tcl_agent python=3.12
conda activate tcl_agent

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API密钥

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入你的GLM API密钥
# ZHIPUAI_API_KEY=your_api_key_here
```

### 3. 运行应用

```bash
# 启动Web界面
python src/app.py
```

访问地址: <http://localhost:7860>

***

## 💬 使用示例

### 产品查询

```
用户: TCL 55Q10G Pro电视怎么样？
Agent: TCL 55Q10G Pro采用QD-Mini LED技术，具有以下画质优势...
```

### 产品推荐

```
用户: 我想买一台5000元左右的电视
Agent: 根据您的需求，为您推荐以下产品：TCL 55Q10G Pro...
```

### 产品对比

```
用户: 55Q10G和55T7G哪个好？
Agent: 【对比表格】... 总结：如果您追求高画质选择55Q10G...
```

***

## 👥 团队分工

| 成员  | 角色       | 职责                 |
| --- | -------- | ------------------ |
| 成员A | 技术负责人    | Agent架构、LLM集成、核心算法 |
| 成员B | 功能开发     | 业务功能、数据处理、测试       |
| 成员C | 前端\&Demo | 界面开发、文档撰写、Demo制作   |

***

## 📅 开发计划

- [x] 项目规划和数据准备
- [x] 代码框架搭建
- [ ] Agent核心功能开发
- [ ] RAG系统实现
- [ ] Web界面开发
- [ ] 测试和优化
- [ ] 文档完善
- [ ] Demo录制

***

## 🎯 项目亮点

1. **RAG检索增强生成**: 结合知识库检索和LLM生成，提升回答准确性
2. **多工具协作**: Function Calling实现多种功能调用
3. **多轮对话管理**: ConversationBufferMemory保持对话上下文
4. **意图智能识别**: 自动识别用户意图，路由到不同功能模块
5. **产业深度结合**: 针对TCL产品特点设计专属功能

***

## 📝 提交材料

- ✅ 技术文档: `docs/技术方案文档.md`
- ✅ 可运行Demo: Web界面 + 录制视频
- ✅ 代码包: 完整的工程源代码

***

## 📄 许可证

本项目仅供AI应用创新大赛参赛使用。

***

## 🙏 致谢

- [LangChain](https://python.langchain.com/) - 强大的Agent开发框架
- [智谱AI](https://open.bigmodel.cn/) - 提供GLM-4大模型API
- [Gradio](https://www.gradio.app/) - 快速构建ML应用的Web界面
- [ChromaDB](https://docs.trychroma.com/) - 轻量级向量数据库

***

**TCL Agent开发团队 | 2026年6月**
