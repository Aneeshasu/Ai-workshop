# Practice: MCP + Strands Agent

This folder contains a simple local MCP setup where:

- `MCP_Server.py` exposes Wikipedia tools over MCP Streamable HTTP (`/mcp` on port `8000`)
- `main.py` connects to that MCP server, loads its tools, and runs a Strands + OpenAI agent

## What we fixed

1. **`.env` loading**
   - `main.py` now loads env vars explicitly from this folder:
   - `load_dotenv(Path(__file__).resolve().parent / ".env")`
   - This avoids failures when running from different working directories.

2. **OpenAI config validation**
   - `main.py` now fails fast if either `OPENAI_API_KEY` or `OPENAI_MODEL` is missing.

3. **System prompt formatting**
   - Prompt is defined as a multiline string with `dedent(...).strip()` so indentation in code does not pollute the actual prompt text.

## Required env vars

Create `Practice/.env`:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

## Run steps

From project root (`Agentic AI`):

1. Activate venv:

```bash
source .venv/bin/activate
```

2. Start MCP server (Terminal 1):

```bash
cd Practice
python MCP_Server.py
```

3. Run agent app (Terminal 2):

```bash
cd Practice
python main.py
```

## Expected behavior

- `main.py` connects to `http://localhost:8000/mcp/`
- Pulls tools via `MCPClient`
- Invokes the agent query (`"Arizona State University"`)
- Prints the model response after tool-backed reasoning

## Common issues

- **`OpenAIError: api_key must be set`**
  - Usually means `.env` was not loaded or key is missing/empty.
- **MCP connection errors**
  - Ensure `MCP_Server.py` is running first on `127.0.0.1:8000`.
- **Import or module errors**
  - Ensure you are in the project venv (`.venv`) before running.
