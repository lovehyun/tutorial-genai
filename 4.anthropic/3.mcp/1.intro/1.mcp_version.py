# pip install mcp

# import mcp
# import pkg_resources

# print(f"MCP version: {pkg_resources.get_distribution('mcp').version}")

import mcp
from importlib.metadata import version, PackageNotFoundError

try:
    print(f"MCP version: {version('mcp')}")
    print(f"MCP package location: {mcp.__file__}")
except PackageNotFoundError:
    print("MCP package not found.")
