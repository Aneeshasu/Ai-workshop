from app.mcp_server.server import mcp_server

from app.mcp_server.tools import extract_receipt_text  # noqa: F401
from app.mcp_server.tools import validate_receipt_data  # noqa: F401
from app.mcp_server.tools import save_receipt_data  # noqa: F401


if __name__ == "__main__":
    mcp_server.run()