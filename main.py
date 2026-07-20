import asyncio
from pathlib import Path
# from typing import Any

from deepagents.backends import CompositeBackend, FilesystemBackend, StoreBackend
# from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver, RunnableConfig
from deepagents import create_deep_agent
# from deepagents.backends.filesystem import FilesystemBackend
from langchain_deepseek import ChatDeepSeek
import os
from langgraph.store.memory import InMemoryStore
from pydantic import SecretStr
from tools.mysql_tools import mysql_client
from sandbox.opensandbox import OpenSandbox
from opensandbox import SandboxSync
from opensandbox.config.connection_sync import ConnectionConfigSync
from datetime import timedelta


async def main():
    INTERESTING_NODES = {"model", "tools"}
    last_source = ""
    mid_line = False

    try:
        deepseek = ChatDeepSeek(
            model="deepseek-v4-flash",
            api_key=SecretStr(os.environ.get("DEEPSEEK_API_KEY", ""))
        )

        skills_backend = FilesystemBackend(r"C:/Users/33028/PycharmProjects/chat_with_db/skills", virtual_mode=True)
        memories_backend = FilesystemBackend(r"C:/Users/33028/PycharmProjects/chat_with_db/memories", virtual_mode=True)

        sandbox = SandboxSync.create(
            "opensandbox/code-interpreter:v1.1.0",
            entrypoint=["/opt/code-interpreter/code-interpreter.sh"],
            env={"PYTHON_VERSION": "3.12"},
            timeout=timedelta(minutes=10),
            connection_config=ConnectionConfigSync(api_key=os.environ.get("OPENSANDBOX_API_KEY", ""))
        )

        backend = CompositeBackend(
            default=OpenSandbox(sandbox=sandbox),
            routes={
                "/skills/": skills_backend,
                "/memories/": memories_backend
            }
        )

        agent = create_deep_agent(
            model=deepseek,
            system_prompt=Path("system_prompt.md").read_text(encoding="utf-8"),
            tools=await mysql_client.get_tools(),
            backend=backend,
            skills=["/skills"],
            memory=["/memories/preferences.md"],
            checkpointer=MemorySaver()
        )

        # If a checkpoint is used, this is a required field.
        thread_config: RunnableConfig = {"configurable": {"thread_id": "42"}, "recursion_limit": 100}

        while True:
            query = input("> ")

            if query == "/bye": break
            response = agent.astream_events(
                {"messages": [{"role": "user", "content": query}]},
                config=thread_config,
                stream_mode="updates",
                subgraphs=True,
                version="v2"
            )

            thinking_state: bool = False
            async for chunk in response:
                if chunk.get("event", "") == "on_chat_model_stream":
                    if think_text := chunk["data"]["chunk"].additional_kwargs.get("reasoning_content"):
                        if thinking_state:
                            print(think_text, end="", flush=True)
                        else:
                            print(f"\nThinking: {think_text}", end="", flush=True)
                            thinking_state = True
                    elif chunk["data"]["chunk"].content:
                        response_text = chunk["data"]["chunk"].content
                        if thinking_state:
                            print(f"\nAI: {response_text}", end="", flush=True)
                            thinking_state = False
                        else:
                            print(response_text, end="", flush=True)
            print("\n")




    finally:
        if 'sandbox' in locals():
            sandbox.kill()
            sandbox.close()


if __name__ == '__main__':
    asyncio.run(main())
