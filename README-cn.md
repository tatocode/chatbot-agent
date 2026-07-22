[🇬🇧 English](README.md) · [🇨🇳 中文](#chinese)

<h1 id="chinese">AI Agent — 通用型增强 AI 助手</h1>

> **⚠️ 开发状态：** 本项目正在积极开发中。当前版本仅完成了基本功能 —— 可能出现破坏性变更、功能不完整或体验粗糙等问题。欢迎贡献和反馈！

一个基于 [DeepSeek](https://deepseek.com/) 和 [DeepAgents](https://github.com/deepagents-ai/deepagents) 的通用 AI 助手，配备沙盒代码执行、联网搜索、数据库访问、技能系统和持久化记忆。

这是一个**通用型** AI 代理框架 —— 可以处理日常对话、编程任务、数据分析、调研、写作等各种需求。数据库只是其众多可选能力之一。

## 功能特性

- **🧠 通用对话** — 支持任何话题的自然多轮对话
- **💻 代码执行** — 在安全沙盒中运行 Python 代码，用于计算、数据处理和可视化
- **🌐 联网搜索** — 集成 DuckDuckGo 搜索，获取实时信息
- **🗄️ 数据库访问** — 可选的 MySQL 连接，用于查询和分析数据
- **🧩 技能系统** — 可扩展的文件化技能模块
- **💾 持久化记忆** — 跨会话记住用户偏好和上下文
- **⏯️ 流式响应** — 实时显示推理过程和回复内容

## 环境要求

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)（Python 包管理器）
- [Docker](https://docs.docker.com/engine/install/)（可选 —— 仅使用 MySQL 时需要）
- [OpenSandbox](https://github.com/opensandbox-group/OpenSandbox) 账户（在 [opensandbox.ai](https://opensandbox.ai) 注册获取 API Key）
- DeepSeek API Key

## 后台服务搭建

根据需求选择性启动以下服务：

### 必需：OpenSandbox（代码执行沙盒）

提供安全的 Python 代码运行环境，使用 `uvx` 在后台启动：

```bash
uvx opensandbox --port 8001
```

> 需要设置 `OPENSANDBOX_API_KEY` 环境变量。

### 可选：DuckDuckGo 联网搜索

```bash
npx @nickclyde/duckduckgo-mcp-server --port 7070
```

在 `http://localhost:7070/mcp` 提供网页搜索能力。

### 可选：MySQL 数据库

```bash
# Docker 启动 MySQL
docker run -d \
  --name chat-mysql \
  -e MYSQL_ROOT_PASSWORD=rootpass \
  -e MYSQL_DATABASE=chatdb \
  -e MYSQL_USER=chat \
  -e MYSQL_PASSWORD=chatpass \
  -p 3306:3306 \
  mysql:8.0

# 启动 MySQL MCP HTTP 桥接服务
npx @anthropic/mcp-mysql-server run --port 8000 \
  --host localhost \
  --user chat \
  --password chatpass \
  --database chatdb
```

## 安装与运行

```bash
# 克隆项目
git clone https://github.com/tatocode/chat_with_db.git
cd chat_with_db

# 配置环境变量
# DEEPSEEK_API_KEY=sk-your-deepseek-api-key
# OPENSANDBOX_API_KEY=os-your-opensandbox-api-key

# 安装依赖
uv venv
uv pip install -e .

# 启动
python main.py
```

## 使用示例

进入 REPL 后直接输入：

```
> 你好，你能帮我做什么？
> 写一个 Python 脚本来下载股票数据并绘图
> 搜索一下最近 AI 领域的新闻
> 帮我看看数据库里有哪些表
> 记住我喜欢用公制单位
```

- `/bye` — 退出会话

## 项目结构

```
chat_with_db/
├── main.py                 # 入口——agent 初始化和 REPL 循环
├── system_prompt.md        # 系统提示词，定义 agent 行为
├── tools/
│   ├── mysql_tools.py      # MCP 客户端配置 (MySQL + DuckDuckGo)
├── sandbox/
│   ├── __init__.py
│   └── opensandbox.py      # OpenSandbox 适配器
├── skills/                 # 可扩展的技能模块
├── memories/               # 持久化记忆存储
├── README.md
└── pyproject.toml
```

## 致谢

- [DeepAgents](https://github.com/deepagents-ai/deepagents) — 本项目使用的 AI Agent 框架
- [DeepSeek](https://deepseek.com/) — 底层大语言模型
- [OpenSandbox](https://github.com/opensandbox-group/OpenSandbox) — 沙盒化代码执行环境
- [DuckDuckGo MCP Server](https://github.com/nickclyde/duckduckgo-mcp-server) by [nickclyde](https://github.com/nickclyde) — 联网搜索能力
- [LangChain](https://github.com/langchain-ai/langchain) & [LangChain MCP Adapters](https://github.com/langchain-ai/langchain-mcp-adapters) — MCP 工具集成框架
- [MySQL MCP Server](https://github.com/designcomputer/mysql_mcp_server) — 数据库连接能力
- 感谢所有让本项目成为可能的开源贡献者
