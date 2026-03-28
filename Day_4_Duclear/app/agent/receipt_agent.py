import os
from textwrap import dedent

from strands import Agent
from strands.models.openai import OpenAIModel
from strands.tools.mcp.mcp_client import MCPClient
from mcp.client.streamable_http import streamablehttp_client

from app.core.config import settings


SYSTEM_PROMPT = dedent("""
You are a receipt processing assistant.

Your job is to process uploaded grocery receipt images using the available MCP tools.

Instructions:
1. First use the OCR tool to extract text from the uploaded receipt image.
2. Read the OCR output carefully and normalize it into this receipt structure:
   - merchant
   - date
   - time
   - currency
   - items
   - discounts
   - subtotal
   - tax
   - total
   - raw_text
3. Then use the validation tool to validate the parsed receipt data.
4. Only if validation recommends saving, use the save tool.
5. If validation recommends manual review or reupload, do not save.

Rules:
- Do not invent values unless strongly supported by OCR text.
- If a field is unclear, use null.
- Ignore footer/promotional noise when possible.
- Keep item extraction accurate.
- Prefer structured output over explanation.
""").strip()


def create_transport():
    return streamablehttp_client(settings.mcp_server_url)


class ReceiptAgent:
    def __init__(self) -> None:
        api_key = settings.openai_api_key
        model_id = settings.llm_model_name

        if not api_key or not model_id:
            raise ValueError("Missing OPENAI_API_KEY or llm_model_name.")

        self.model = OpenAIModel(
            client_args={"api_key": api_key},
            model_id=model_id,
            params={"temperature": 0.2, "max_tokens": 2000},
        )

        self.mcp_client = MCPClient(create_transport)

    async def invoke(self, prompt: str):
        with self.mcp_client:
            tools = self.mcp_client.list_tools_sync()

            agent = Agent(
                model=self.model,
                system_prompt=SYSTEM_PROMPT,
                tools=tools,
            )

            response = await agent.invoke_async(prompt)
            return response