#!/usr/bin/env python3
"""MCP Server for EdgeDex - Provides Pokemon data tools to Claude Desktop."""

import asyncio
import sys
import os
import json
import logging
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the datasolver path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'datasolver'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('EdgeDxMCPServer')

try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.types import (
        CallToolRequest,
        ListToolsRequest,
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
    )
    from mcp.server.stdio import stdio_server
except ImportError:
    logger.error("MCP package not installed. Install with: pip install mcp")
    sys.exit(1)

from providers.mcp.tools.pokemon import PokemonTool

class EdgeDxMCPServer:
    """MCP Server for EdgeDx Pokemon data tools."""
    
    def __init__(self):
        """Initialize the EdgeDx MCP server."""
        self.pokemon_tool = PokemonTool()
        self.server = Server("edgedx")
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up MCP server handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="generate_pokemon_data",
                    description="Generate Pokemon datasets with IPFS caching for high performance",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "data_type": {
                                "type": "string",
                                "enum": ["pokemon", "moves", "abilities", "types", "evolution"],
                                "description": "Type of Pokemon data to generate"
                            },
                            "num_records": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 100,
                                "default": 10,
                                "description": "Number of records to generate"
                            },
                            "generation": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 9,
                                "description": "Pokemon generation to filter by (1-9)"
                            },
                            "pokemon_names": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Specific Pokemon names to include"
                            },
                            "include_stats": {
                                "type": "boolean",
                                "default": True,
                                "description": "Include base stats in the dataset"
                            },
                            "include_abilities": {
                                "type": "boolean",
                                "default": True,
                                "description": "Include abilities in the dataset"
                            },
                            "include_moves": {
                                "type": "boolean",
                                "default": False,
                                "description": "Include move data (can be large)"
                            }
                        },
                        "required": ["data_type"]
                    }
                ),
                Tool(
                    name="get_cache_stats",
                    description="Get IPFS cache statistics and performance metrics",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False
                    }
                ),
                Tool(
                    name="clear_cache",
                    description="Clear expired cache entries",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            try:
                if name == "generate_pokemon_data":
                    return await self._handle_generate_pokemon_data(arguments)
                elif name == "get_cache_stats":
                    return await self._handle_get_cache_stats()
                elif name == "clear_cache":
                    return await self._handle_clear_cache()
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                logger.error(f"Error handling tool call {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def _handle_generate_pokemon_data(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle Pokemon data generation."""
        try:
            # Create RFD from arguments
            rfd = {
                "rfd_id": f"claude_request_{int(asyncio.get_event_loop().time())}",
                "data_type": arguments.get("data_type", "pokemon"),
                "num_records": arguments.get("num_records", 10),
                "generation": arguments.get("generation"),
                "pokemon_names": arguments.get("pokemon_names", []),
                "include_stats": arguments.get("include_stats", True),
                "include_abilities": arguments.get("include_abilities", True),
                "include_moves": arguments.get("include_moves", False)
            }
            
            # Validate the RFD
            if not self.pokemon_tool.validate_rfd(rfd):
                return [TextContent(type="text", text="Invalid request parameters")]
            
            # Generate the data
            result = self.pokemon_tool.generate_data(rfd)
            
            # Format the response
            response = {
                "success": True,
                "data_type": result["data_type"],
                "count": result["count"],
                "source": result["source"],
                "cached": result.get("cached", False),
                "cache_stored": result.get("cache_stored", False),
                "data": result["data"]
            }
            
            # Create a summary
            summary = f"Generated {result['count']} {result['data_type']} records"
            if result.get("cached"):
                summary += " (from IPFS cache - fast!)"
            else:
                summary += " (fresh from PokeAPI"
                if result.get("cache_stored"):
                    summary += " - now cached for future requests"
                summary += ")"
            
            return [
                TextContent(
                    type="text", 
                    text=f"{summary}\n\nResult:\n{json.dumps(response, indent=2)}"
                )
            ]
            
        except Exception as e:
            logger.error(f"Error generating Pokemon data: {e}")
            return [TextContent(type="text", text=f"Error generating data: {str(e)}")]
    
    async def _handle_get_cache_stats(self) -> List[TextContent]:
        """Handle cache statistics request."""
        try:
            stats = self.pokemon_tool.get_cache_stats()
            
            response = {
                "cache_stats": stats,
                "performance": {
                    "pinata_available": stats["pinata_available"],
                    "cache_hit_speed": "Sub-second response time" if stats["pinata_available"] else "N/A",
                    "performance_improvement": "2-3x faster with cache" if stats["pinata_available"] else "Cache unavailable"
                }
            }
            
            summary = f"IPFS Cache Status:\n"
            summary += f"- Pinata Available: {'Yes' if stats['pinata_available'] else 'No'}\n"
            summary += f"- Total Entries: {stats['total_entries']}\n"
            summary += f"- Valid Entries: {stats['valid_entries']}\n"
            summary += f"- TTL: {stats['ttl_seconds']} seconds ({stats['ttl_seconds']//60} minutes)\n"
            
            if stats["pinata_available"]:
                summary += f"\nEdgeDx provides 2-3x performance improvement with IPFS caching!"
            
            return [
                TextContent(
                    type="text",
                    text=f"{summary}\n\nDetailed Stats:\n{json.dumps(response, indent=2)}"
                )
            ]
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return [TextContent(type="text", text=f"Error getting cache stats: {str(e)}")]
    
    async def _handle_clear_cache(self) -> List[TextContent]:
        """Handle cache clearing request."""
        try:
            cleared_count = self.pokemon_tool.clear_expired_cache()
            
            return [
                TextContent(
                    type="text",
                    text=f"Cache cleanup completed. Cleared {cleared_count} expired entries."
                )
            ]
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return [TextContent(type="text", text=f"Error clearing cache: {str(e)}")]

async def main():
    """Main entry point for the MCP server."""
    server_instance = EdgeDxMCPServer()
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="edgedx",
                server_version="1.0.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main()) 