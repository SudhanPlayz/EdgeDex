"""Pokémon MCP tool for generating Pokémon-related datasets using direct PokéAPI access."""

import json
import logging
import time
from typing import Dict, Any, List, Optional
from .tool import MCPTool
from .ipfs_cache import IPFSCache

logger = logging.getLogger('PokemonTool')

class PokemonTool(MCPTool):
    """MCP tool for generating Pokémon datasets using direct PokéAPI access.
    
    This tool can generate various types of Pokémon data including:
    - Individual Pokémon data (stats, types, abilities, etc.)
    - Pokémon species information
    - Move data
    - Type effectiveness data
    - Evolution chains
    - And more based on RFD requirements
    """
    
    def __init__(self):
        """Initialize the Pokémon tool with direct API access and IPFS cache."""
        try:
            import requests
            self.session = requests.Session()
            self.base_url = "https://pokeapi.co/api/v2"
            self.cache = {}  # Simple in-memory cache for API responses
            self.ipfs_cache = IPFSCache(ttl_minutes=30)  # 30-minute TTL for IPFS cache
            logger.info("Initialized Pokémon tool with direct PokéAPI access and IPFS cache")
        except ImportError:
            logger.error("requests not installed. Install with: pip install requests")
            raise
    
    @property
    def name(self) -> str:
        """Get the tool's unique identifier."""
        return "pokemon"
    
    @property
    def description(self) -> str:
        """Get a human-readable description of the tool."""
        return ("Pokémon data tool that can generate datasets containing Pokémon information "
                "including stats, types, abilities, moves, evolution chains, and more using direct PokéAPI access")
    
    @property
    def capabilities(self) -> Dict[str, Any]:
        """Get the tool's capabilities and requirements."""
        return {
            "data_types": [
                "pokemon",      # Individual Pokémon data
                "species",      # Pokémon species information
                "moves",        # Move data
                "abilities",    # Ability data
                "types",        # Type data
                "evolution",    # Evolution chains
                "stats",        # Base stats
                "locations",    # Location data
                "items"         # Item data
            ],
            "parameters": {
                "data_type": {
                    "type": "string",
                    "required": True,
                    "description": "Type of Pokémon data to generate"
                },
                "pokemon_names": {
                    "type": "array",
                    "required": False,
                    "description": "Specific Pokémon names to include (optional)"
                },
                "pokemon_ids": {
                    "type": "array", 
                    "required": False,
                    "description": "Specific Pokémon IDs to include (optional)"
                },
                "generation": {
                    "type": "integer",
                    "required": False,
                    "description": "Pokémon generation to filter by (1-9)"
                },
                "type_filter": {
                    "type": "string",
                    "required": False,
                    "description": "Filter by Pokémon type (e.g., 'fire', 'water')"
                },
                "include_stats": {
                    "type": "boolean",
                    "required": False,
                    "default": True,
                    "description": "Include base stats in the dataset"
                },
                "include_abilities": {
                    "type": "boolean", 
                    "required": False,
                    "default": True,
                    "description": "Include abilities in the dataset"
                },
                "include_moves": {
                    "type": "boolean",
                    "required": False,
                    "default": False,
                    "description": "Include move data (can be large)"
                }
            },
            "output_format": "json",
            "max_records": 1000
        }
    
    def _make_request(self, endpoint: str) -> Optional[Dict]:
        """Make a request to PokéAPI with caching."""
        url = f"{self.base_url}/{endpoint}"
        
        # Check cache first
        if url in self.cache:
            return self.cache[url]
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Cache the response
            self.cache[url] = data
            
            # Add small delay to be respectful to the API
            time.sleep(0.1)
            
            return data
        except Exception as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            return None
    
    def validate_rfd(self, rfd: Dict[str, Any]) -> bool:
        """Validate if the tool can handle the given RFD."""
        try:
            # Check if this is a Pokémon-related request
            data_type = rfd.get("data_type") or rfd.get("type") or rfd.get("pokemon_data_type")
            
            if not data_type:
                # Check if description mentions Pokémon
                description = rfd.get("description", "").lower()
                name = rfd.get("name", "").lower()
                if "pokemon" not in description and "pokemon" not in name:
                    return False
                # Default to pokemon data type if not specified
                data_type = "pokemon"
            
            # Validate data type
            valid_types = self.capabilities["data_types"]
            if data_type not in valid_types:
                logger.warning(f"Unsupported data type: {data_type}")
                return False
            
            # Check num_records is reasonable
            num_records = rfd.get("num_records", 10)
            if num_records > self.capabilities["max_records"]:
                logger.warning(f"Requested {num_records} records exceeds maximum {self.capabilities['max_records']}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating RFD: {e}")
            return False
    
    def generate_data(self, rfd: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Pokémon dataset according to the RFD with IPFS caching."""
        try:
            # 1. Try IPFS cache first
            cached_result = self.ipfs_cache.get_cached(rfd)
            if cached_result is not None:
                logger.info("Returning cached result from IPFS")
                # Ensure cached result has the right structure
                if isinstance(cached_result, dict) and 'data' in cached_result:
                    cached_result['cached'] = True
                    cached_result['source'] = 'IPFS Cache via Pinata'
                    return cached_result
                else:
                    # If cached result doesn't have expected structure, treat as fresh data
                    logger.warning("Cached result has unexpected structure, treating as fresh")
                    pass
            
            # 2. Generate fresh data if not in cache
            data_type = rfd.get("data_type") or rfd.get("type") or rfd.get("pokemon_data_type", "pokemon")
            num_records = rfd.get("num_records", 10)
            pokemon_names = rfd.get("pokemon_names", [])
            pokemon_ids = rfd.get("pokemon_ids", [])
            generation = rfd.get("generation")
            type_filter = rfd.get("type_filter")
            include_stats = rfd.get("include_stats", True)
            include_abilities = rfd.get("include_abilities", True)
            include_moves = rfd.get("include_moves", False)
            
            logger.info(f"Generating fresh {data_type} dataset with {num_records} records")
            
            # Generate data based on type
            if data_type == "pokemon":
                records = self._generate_pokemon_data(
                    num_records, pokemon_names, pokemon_ids, generation, 
                    type_filter, include_stats, include_abilities, include_moves
                )
            elif data_type == "moves":
                records = self._generate_move_data(num_records)
            elif data_type == "abilities":
                records = self._generate_ability_data(num_records)
            elif data_type == "types":
                records = self._generate_type_data()
            elif data_type == "evolution":
                records = self._generate_evolution_data(num_records)
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
            
            result = {
                "data": records,
                "count": len(records),
                "data_type": data_type,
                "source": "PokéAPI via direct requests",
                "cached": False
            }
            
            # 3. Store result in IPFS cache
            cache_stored = self.ipfs_cache.store_cached(rfd, result)
            if cache_stored:
                result["cache_stored"] = True
                logger.info("Result stored in IPFS cache")
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating Pokémon data: {e}")
            raise RuntimeError(f"Failed to generate Pokémon data: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.ipfs_cache.get_cache_stats()
    
    def clear_expired_cache(self) -> int:
        """Clear expired cache entries."""
        return self.ipfs_cache.clear_expired()
    
    def _generate_pokemon_data(self, num_records: int, pokemon_names: List[str], 
                              pokemon_ids: List[int], generation: Optional[int],
                              type_filter: Optional[str], include_stats: bool,
                              include_abilities: bool, include_moves: bool) -> List[Dict[str, Any]]:
        """Generate Pokémon data records."""
        records = []
        
        # Determine which Pokémon to fetch
        if pokemon_names:
            # Use specific names
            targets = pokemon_names[:num_records]
        elif pokemon_ids:
            # Use specific IDs
            targets = pokemon_ids[:num_records]
        else:
            # Generate range of IDs (first 151 Pokémon by default, or based on generation)
            if generation:
                # Approximate ranges for generations
                ranges = {
                    1: (1, 151), 2: (152, 251), 3: (252, 386), 4: (387, 493),
                    5: (494, 649), 6: (650, 721), 7: (722, 809), 8: (810, 905), 9: (906, 1010)
                }
                start, end = ranges.get(generation, (1, 151))
                targets = list(range(start, min(start + num_records, end + 1)))
            else:
                targets = list(range(1, min(num_records + 1, 152)))
        
        for target in targets:
            try:
                # Fetch Pokémon data
                if isinstance(target, str):
                    endpoint = f"pokemon/{target.lower()}"
                else:
                    endpoint = f"pokemon/{target}"
                
                pokemon_data = self._make_request(endpoint)
                if not pokemon_data:
                    continue
                
                # Apply type filter if specified
                if type_filter:
                    pokemon_types = [t["type"]["name"] for t in pokemon_data["types"]]
                    if type_filter.lower() not in pokemon_types:
                        continue
                
                # Build record
                record = {
                    "id": pokemon_data["id"],
                    "name": pokemon_data["name"],
                    "height": pokemon_data["height"],
                    "weight": pokemon_data["weight"],
                    "types": [t["type"]["name"] for t in pokemon_data["types"]],
                    "base_experience": pokemon_data.get("base_experience")
                }
                
                # Add stats if requested
                if include_stats:
                    record["stats"] = {
                        stat["stat"]["name"]: stat["base_stat"] for stat in pokemon_data["stats"]
                    }
                
                # Add abilities if requested
                if include_abilities:
                    record["abilities"] = [
                        {
                            "name": ability["ability"]["name"],
                            "is_hidden": ability["is_hidden"],
                            "slot": ability["slot"]
                        } for ability in pokemon_data["abilities"]
                    ]
                
                # Add moves if requested (limited to first 10 to keep size manageable)
                if include_moves:
                    record["moves"] = [
                        {
                            "name": move["move"]["name"],
                            "learn_method": move["version_group_details"][0]["move_learn_method"]["name"] if move["version_group_details"] else "unknown"
                        } for move in pokemon_data["moves"][:10]
                    ]
                
                records.append(record)
                
            except Exception as e:
                logger.warning(f"Failed to fetch Pokémon {target}: {e}")
                continue
        
        return records
    
    def _generate_move_data(self, num_records: int) -> List[Dict[str, Any]]:
        """Generate move data records."""
        records = []
        
        for move_id in range(1, min(num_records + 1, 101)):  # First 100 moves
            try:
                move_data = self._make_request(f"move/{move_id}")
                if not move_data:
                    continue
                    
                record = {
                    "id": move_data["id"],
                    "name": move_data["name"],
                    "power": move_data.get("power"),
                    "pp": move_data.get("pp"),
                    "accuracy": move_data.get("accuracy"),
                    "priority": move_data.get("priority"),
                    "type": move_data["type"]["name"] if move_data.get("type") else None,
                    "damage_class": move_data["damage_class"]["name"] if move_data.get("damage_class") else None,
                    "effect_chance": move_data.get("effect_chance")
                }
                records.append(record)
            except Exception as e:
                logger.warning(f"Failed to fetch move {move_id}: {e}")
                continue
        
        return records
    
    def _generate_ability_data(self, num_records: int) -> List[Dict[str, Any]]:
        """Generate ability data records."""
        records = []
        
        for ability_id in range(1, min(num_records + 1, 101)):  # First 100 abilities
            try:
                ability_data = self._make_request(f"ability/{ability_id}")
                if not ability_data:
                    continue
                    
                record = {
                    "id": ability_data["id"],
                    "name": ability_data["name"],
                    "is_main_series": ability_data.get("is_main_series"),
                    "generation": ability_data["generation"]["name"] if ability_data.get("generation") else None,
                    "effect": ability_data["effect_entries"][0]["short_effect"] if ability_data.get("effect_entries") else None
                }
                records.append(record)
            except Exception as e:
                logger.warning(f"Failed to fetch ability {ability_id}: {e}")
                continue
        
        return records
    
    def _generate_type_data(self) -> List[Dict[str, Any]]:
        """Generate type effectiveness data."""
        records = []
        
        # Get all types (there are 18 main types)
        type_names = ['normal', 'fire', 'water', 'electric', 'grass', 'ice', 'fighting', 
                     'poison', 'ground', 'flying', 'psychic', 'bug', 'rock', 'ghost', 
                     'dragon', 'dark', 'steel', 'fairy']
        
        for type_name in type_names:
            try:
                type_data = self._make_request(f"type/{type_name}")
                if not type_data:
                    continue
                    
                record = {
                    "id": type_data["id"],
                    "name": type_data["name"],
                    "damage_relations": {
                        "double_damage_to": [t["name"] for t in type_data["damage_relations"]["double_damage_to"]],
                        "half_damage_to": [t["name"] for t in type_data["damage_relations"]["half_damage_to"]],
                        "no_damage_to": [t["name"] for t in type_data["damage_relations"]["no_damage_to"]],
                        "double_damage_from": [t["name"] for t in type_data["damage_relations"]["double_damage_from"]],
                        "half_damage_from": [t["name"] for t in type_data["damage_relations"]["half_damage_from"]],
                        "no_damage_from": [t["name"] for t in type_data["damage_relations"]["no_damage_from"]]
                    }
                }
                records.append(record)
            except Exception as e:
                logger.warning(f"Failed to fetch type {type_name}: {e}")
                continue
        
        return records
    
    def _generate_evolution_data(self, num_records: int) -> List[Dict[str, Any]]:
        """Generate evolution chain data."""
        records = []
        
        for chain_id in range(1, min(num_records + 1, 51)):  # First 50 evolution chains
            try:
                chain_data = self._make_request(f"evolution-chain/{chain_id}")
                if not chain_data:
                    continue
                    
                record = {
                    "id": chain_data["id"],
                    "baby_trigger_item": chain_data["baby_trigger_item"]["name"] if chain_data.get("baby_trigger_item") else None,
                    "chain": self._parse_evolution_chain(chain_data["chain"])
                }
                records.append(record)
            except Exception as e:
                logger.warning(f"Failed to fetch evolution chain {chain_id}: {e}")
                continue
        
        return records
    
    def _parse_evolution_chain(self, chain_link) -> Dict[str, Any]:
        """Parse an evolution chain link recursively."""
        result = {
            "species": chain_link["species"]["name"],
            "evolves_to": []
        }
        
        for evolution in chain_link["evolves_to"]:
            evolution_details = {
                "species": evolution["species"]["name"],
                "min_level": evolution["evolution_details"][0]["min_level"] if evolution["evolution_details"] else None,
                "trigger": evolution["evolution_details"][0]["trigger"]["name"] if evolution["evolution_details"] else None,
                "evolves_to": self._parse_evolution_chain(evolution)["evolves_to"] if evolution["evolves_to"] else []
            }
            result["evolves_to"].append(evolution_details)
        
        return result 