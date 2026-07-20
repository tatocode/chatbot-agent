from __future__ import annotations
from typing import TYPE_CHECKING, Any

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from sandbox.opensandbox import OpenSandbox

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph


class AgentRunner:
    def __init__(self, agent: CompiledStateGraph, backend: OpenSandbox):
        self._agent = agent
        self._backend = backend

    def _parser_artifact(self, text: str) -> list[str]:
        """
        Extract artifact file paths from LLM output.

        Example:
            Input:
                <artifact>
                [
                  "/workspace/report.pdf"
                ]
                </artifact>

            Output:
                [
                  "/workspace/report.pdf"
                ]

        :param text: output of llm
        :return: list of file paths
        """
        import json
        import re

        if not text:
            return []
        match = re.search(
            r"<artifact>\s*(.*?)\s*</artifact>",
            text,
            flags=re.DOTALL | re.IGNORECASE,
        )
        if not match:
            return []

        try:
            artifacts = json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            return []
        if not isinstance(artifacts, list):
            return []

        return [
            path
            for path in artifacts
            if isinstance(path, str) and path.strip()
        ]


    async def run(self, query: str, config: RunnableConfig) -> dict[str, Any]:
        response = await self._agent.ainvoke({"messages": HumanMessage(query)}, config=config)
        messages = response["messages"]
        content = messages[-1].content

        artifact = self._parser_artifact(content)
        self._backend.download_files(artifact)


