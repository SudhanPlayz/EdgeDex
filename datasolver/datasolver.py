"""Main data solver implementation focused on Pokémon data generation."""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from .types import ProviderType
from .config import DatasetConfig
from .providers.provider import DataProvider
from .providers.mcp.tools.tool import MCPTool
from .providers.mcp.tools.pokemon import PokemonTool
from .providers.mcp.client import MCPClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('DataSolver')

class DataSolver:
    """Data solver for generating Pokémon datasets using MCP tools"""
    
    @classmethod
    def from_env(cls, config_file: str = "config.json", mock_mode: bool = False) -> "DataSolver":
        """Factory method to instantiate a DataSolver from environment variables.
        
        This solver is optimized for Pokémon data generation using MCP tools.
        
        Args:
            config_file (str): Path to the JSON config file (default: "config.json")
            mock_mode (bool): Whether to run in mock mode (default: False)
        Returns:
            DataSolver: A configured DataSolver instance for Pokémon data.
        """
        # For Pokémon-focused solver, always use MCP with PokemonTool
        return cls(provider_type=ProviderType.MCP, mcp_tools=[PokemonTool])

    def __init__(self, provider_type: ProviderType = ProviderType.MCP, mcp_tools: Optional[list] = None):
        """Initialize solver with Pokémon-focused MCP provider
        
        Args:
            provider_type: Type of provider to use (defaults to MCP for Pokémon)
            mcp_tools: List of MCP tool classes to use (defaults to [PokemonTool])
        """
        # Always use MCP provider with PokemonTool for this focused implementation
        from .providers.mcp.client import MCPClient
        self.provider = MCPClient(tools=mcp_tools or [PokemonTool])
        logger.info(f"Initialized Pokémon DataSolver with MCP provider")
    
    def solve(self, rfd: Dict) -> Optional[str]:
        """Generate Pokémon dataset for RFD
        
        Args:
            rfd: Request for data (should be Pokémon-related)
            
        Returns:
            Path to generated dataset file
        """
        try:
            # Validate that this is a Pokémon request
            if not self._is_pokemon_request(rfd):
                logger.warning("RFD does not appear to be Pokémon-related. Processing anyway...")
            
            dataset = self.provider.generate_dataset(rfd)
            if not dataset:
                return None
                
            file_path = f"data/pokemon_rfd_{rfd.get('rfd_id', 'unknown')}_solution.json"
            os.makedirs("data", exist_ok=True)
            
            with open(file_path, 'w') as f:
                json.dump(dataset, f, indent=2)
            
            logger.info(f"Pokémon dataset generated successfully at: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to generate Pokémon dataset: {e}")
            return None
    
    def _is_pokemon_request(self, rfd: Dict) -> bool:
        """Check if the RFD is requesting Pokémon data."""
        # Check explicit data type
        data_type = rfd.get("data_type") or rfd.get("type") or rfd.get("pokemon_data_type")
        if data_type and "pokemon" in data_type.lower():
            return True
        
        # Check description and name for Pokémon keywords
        description = rfd.get("description", "").lower()
        name = rfd.get("name", "").lower()
        pokemon_keywords = ["pokemon", "pokémon", "pokeapi", "pikachu", "charizard", "generation"]
        
        return any(keyword in description or keyword in name for keyword in pokemon_keywords) 