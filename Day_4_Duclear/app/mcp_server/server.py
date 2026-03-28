from fastmcp import FastMCP


class MCPServer:
    """
    Wrapper class around FastMCP server.
    Keeps server creation and server startup in one place.
    """

    def __init__(self) -> None:
        self.mcp = FastMCP("receipt-processing-mcp")

    def run(self) -> None:
        """
        Starts the MCP server.
        """
        self.mcp.run(
            transport="http",
            host="127.0.0.1",
            port=8001,
        )


mcp_server = MCPServer()
mcp = mcp_server.mcp