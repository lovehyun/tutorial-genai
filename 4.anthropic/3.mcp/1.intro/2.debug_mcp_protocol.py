import inspect
from importlib.metadata import version
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.server.fastmcp import FastMCP

# Print MCP version
print(f"MCP version: {version('mcp')}")

# Look at FastMCP documentation
print("\nFastMCP class documentation:")
print(inspect.getdoc(FastMCP))
print("\nFastMCP.sse_app method documentation:")
print(inspect.getdoc(FastMCP.sse_app))

# Look at ClientSession documentation
print("\nClientSession class documentation:")
print(inspect.getdoc(ClientSession))
print("\nClientSession.initialize method documentation:")
print(inspect.getdoc(ClientSession.initialize))

# Look at streamablehttp_client documentation
print("\nstreamablehttp_client function documentation:")
print(inspect.getdoc(streamablehttp_client))

# Print the actual implementation of some key functions
print("\nImplementation of streamablehttp_client:")
print(inspect.getsource(streamablehttp_client))
