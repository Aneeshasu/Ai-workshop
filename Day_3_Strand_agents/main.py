import asyncio
import os
from pathlib import Path
from textwrap import dedent

from dotenv import load_dotenv
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.models.openai import OpenAIModel
from strands.tools.mcp.mcp_client import MCPClient

from utils import setup_run_logger

load_dotenv(Path(__file__).resolve().parent / ".env")

SYSTEM_PROMPT = dedent("""
You are a university research assistant.
Use the available MCP Wikipedia tools first.
Do not rely on prior knowledge if tool verification fails.
If the facts cannot be verified from the MCP Wikipedia tools, say exactly:
"I could not verify this on Wikipedia."
""").strip()

def create_transport():
    return streamablehttp_client("http://localhost:8000/mcp/")

class RunAgent:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        model_id = os.getenv("OPENAI_MODEL")
        if not api_key or not model_id:
            raise ValueError(
                "Missing OPENAI_API_KEY or OPENAI_MODEL."
            )

        self.model = OpenAIModel(
            client_args={"api_key": api_key},
            model_id=model_id,
            params={"temperature": 0.3, "max_tokens": 1000},
        )
        self.mcp_client = MCPClient(create_transport)

    async def run(self):
        with self.mcp_client:
            tools = self.mcp_client.list_tools_sync()

            agent = Agent(
                model=self.model,
                system_prompt=SYSTEM_PROMPT,
                tools=tools,
            )

            response = await agent.invoke_async("Arizona State University")
            print(response)


if __name__ == "__main__":
    asyncio.run(RunAgent().run())
