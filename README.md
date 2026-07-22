[🇬🇧 English](#english) · [🇨🇳 中文](README-cn.md)

<h1 id="english">AI Agent — General-Purpose Assistant with Tool Augmentation</h1>

> **⚠️ Development Status:** This project is actively under development. The current version implements basic functionality only — expect breaking changes, incomplete features, and rough edges. Contributions and feedback are welcome!

A versatile AI agent powered by [DeepSeek](https://deepseek.com/) and [DeepAgents](https://github.com/deepagents-ai/deepagents), equipped with a sandboxed code interpreter, web search, database access, skills, and persistent memory.

This is a **general-purpose** agent framework — it handles everyday questions, coding tasks, data analysis, research, writing, and more. Database connectivity is one of many optional capabilities.

## Features

- **🧠 General Conversation** — Natural, multi-turn dialogue for any topic
- **💻 Code Execution** — Run Python code safely in a sandboxed environment for computation, data processing, and visualization
- **🌐 Web Search** — DuckDuckGo integration for real-time information retrieval
- **🗄️ Database Access** — Optional MySQL connectivity for querying and analyzing data
- **🧩 Skill System** — Extensible file-based skills for specialized tasks
- **💾 Persistent Memory** — Remembers user preferences and context across sessions
- **⏯️ Streaming Responses** — Real-time token streaming with visible reasoning

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   AI Agent (main.py)                     │
│                                                          │
│  ┌─────────────┐  ┌────────────┐  ┌──────────────────┐  │
│  │   DeepSeek   │  │ DeepAgents │  │    MCP Client    │  │
│  │   (LLM)      │◄─┤   Agent    │──┤  (Tool Layer)    │  │
│  └─────────────┘  └────────────┘  └───┬───┬───┬───────┘  │
│                                       │   │   │          │
│         ┌─────────────────────────────┘   │   └───────┐  │
│         ▼                                 ▼           ▼  │
│  ┌───────────┐  ┌────────────────┐  ┌───────────────┐   │
│  │ MySQL MCP │  │ DuckDuckGo MCP│  │ Skills &      │   │
│  │ (optional)│  │   (search)     │  │ Memory (FS)   │   │
│  └─────┬─────┘  └───────┬────────┘  └───────────────┘   │
│        │                 │                               │
│  ┌─────┴──────┐  ┌──────┴────────┐                      │
│  │  MySQL DB  │  │ DuckDuckGo   │                       │
│  │  (Docker)  │  │   Search     │                       │
│  └────────────┘  └───────────────┘                      │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │     OpenSandbox (Sandboxed Code Interpreter)     │   │
│  │     - Execute Python / analyze data / plot       │   │
│  │     - File upload / download                     │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [Docker](https://docs.docker.com/engine/install/) (optional — only if using MySQL)
- [OpenSandbox](https://github.com/opensandbox-group/OpenSandbox) account — sign up at [opensandbox.ai](https://opensandbox.ai) for an API key
- DeepSeek API key

## Quick Start

### 1. Clone and Configure

```bash
git clone https://github.com/tatocode/chat_with_db.git
cd chat_with_db
```

Create a `.env` file (or set environment variables):

```bash
DEEPSEEK_API_KEY=sk-your-deepseek-api-key
OPENSANDBOX_API_KEY=os-your-opensandbox-api-key
```

### 2. Install Dependencies

```bash
uv venv
uv pip install -e .
```

### 3. Start Backend Services

The agent relies on several backend services. Only start the ones you need for your use case.

#### Required: OpenSandbox (Code Execution)

[OpenSandbox](https://github.com/opensandbox-group/OpenSandbox) provides a secure sandboxed environment for running Python code. Start it in the background via `uvx`:

```bash
uvx opensandbox --port 8001
```

This launches the OpenSandbox background service. The `OPENSANDBOX_API_KEY` environment variable must be set. The Python `opensandbox` package handles communication with the cloud service.

#### Optional: DuckDuckGo Web Search

If you want web search capabilities, start the [DuckDuckGo MCP Server](https://github.com/nickclyde/duckduckgo-mcp-server):

```bash
npx @nickclyde/duckduckgo-mcp-server --port 7070
```

This exposes a search tool at `http://localhost:7070/mcp`.

#### Optional: MySQL Database Access

If you need database querying capabilities, start MySQL via Docker and its MCP bridge:

```bash
# Start MySQL in Docker
docker run -d \
  --name chat-mysql \
  -e MYSQL_ROOT_PASSWORD=rootpass \
  -e MYSQL_DATABASE=chatdb \
  -e MYSQL_USER=chat \
  -e MYSQL_PASSWORD=chatpass \
  -p 3306:3306 \
  mysql:8.0

# Start the MySQL MCP HTTP bridge
npx @anthropic/mcp-mysql-server run --port 8000 \
  --host localhost \
  --user chat \
  --password chatpass \
  --database chatdb
```

> **Note:** Any MySQL MCP server (HTTP transport) exposing schema/query tools at `http://localhost:8000/mcp` will work. Adjust the URL in `tools/mysql_tools.py` if needed.

### 4. Run

```bash
python main.py
```

## Usage

The agent runs as an interactive REPL. Type naturally:

```
> Hello, what can you help me with?
> Write a Python script to download stock data and plot it
> Search the web for the latest AI news
> Show me the tables in my database
> What's the average order value per customer?
> Remember that I prefer metric units
```

- `/bye` — Exit the session
- The agent streams responses token-by-token, showing its reasoning process

## Configuration

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DEEPSEEK_API_KEY` | Yes | DeepSeek LLM API key |
| `OPENSANDBOX_API_KEY` | Yes | OpenSandbox cloud API key |

### MCP Server Configuration

The tools are configured in `tools/mysql_tools.py`. You can enable/disable services by adding or removing entries:

```python
mysql_client = MultiServerMCPClient({
    "MySQL": {
        "transport": "http",
        "url": "http://localhost:8000/mcp",
    },
    "DuckDuckGo": {
        "transport": "http",
        "url": "http://localhost:7070/mcp",
    },
})
```

### Model

The agent uses `deepseek-v4-flash` by default. Change the model name in `main.py`:

```python
deepseek = ChatDeepSeek(
    model="deepseek-v4-flash",  # Change to another model if needed
    api_key=SecretStr(os.environ.get("DEEPSEEK_API_KEY", ""))
)
```

### System Prompt

The agent's behavior is defined in `system_prompt.md`. Edit it to customize the assistant's personality, capabilities description, and working principles.

## Project Structure

```
chat_with_db/
├── main.py                 # Entry point — agent initialization & REPL loop
├── system_prompt.md        # System prompt defining agent behavior
├── tools/
│   ├── mysql_tools.py      # MCP client configuration (MySQL + DuckDuckGo)
│   └── __pycache__/
├── sandbox/
│   ├── __init__.py
│   └── opensandbox.py      # OpenSandbox adapter (BaseSandbox implementation)
├── skills/                 # Extensible skill definitions
├── memories/               # Persistent memory storage
│   ├── preferences.md
│   └── name.md
├── README.md
└── pyproject.toml
```

## Acknowledgements

- [DeepAgents](https://github.com/deepagents-ai/deepagents) — The agent framework powering this project
- [DeepSeek](https://deepseek.com/) — LLM backend
- [OpenSandbox](https://github.com/opensandbox-group/OpenSandbox) — Sandboxed code execution environment
- [DuckDuckGo MCP Server](https://github.com/nickclyde/duckduckgo-mcp-server) by [nickclyde](https://github.com/nickclyde) — Web search capability
- [LangChain](https://github.com/langchain-ai/langchain) & [LangChain MCP Adapters](https://github.com/langchain-ai/langchain-mcp-adapters) — MCP tool integration framework
- [MySQL MCP Server](https://github.com/designcomputer/mysql_mcp_server) — Database connectivity
- All open-source contributors whose work made this project possible

