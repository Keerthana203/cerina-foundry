"""
MCP Server for Cerina Protocol Foundry

Exposes the LangGraph multi-agent workflow
as an MCP Tool using the official MCP runtime SDK.
"""

from mcp.server import Server
from .mcp_tool import run_protocol_tool


server = Server(
    name="cerina-protocol-foundry",
    description="Multi-agent CBT protocol generation system with human-in-the-loop approval",
)


@server.tool(
    name="cerina_protocol_generator",
    description="Generate a safe CBT protocol using Cerina's multi-agent clinical foundry"
)
def cerina_protocol_generator(prompt: str) -> dict:
    return run_protocol_tool({"prompt": prompt})


if __name__ == "__main__":
    server.run()
