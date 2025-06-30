# main.py
"""Main entry point for the Pokémon-focused solver node."""

import click
import logging
from solverNode import SolverNode
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('Main')

BANNER = """
  ____       _          _____            _              _   _           _      
 |  _ \ ___ | | _____  |  ___|___   ___  | |_   __ _   | \ | | ___   __| | ___ 
 | |_) / _ \| |/ / _ \ | |_ / _ \ / _ \ | | | | / _` |  |  \| |/ _ \ / _` |/ _ \\
 |  __/ (_) |   <  __/ |  _| (_) | (_) || |_| || (_| |  | |\  | (_) | (_| |  __/
 |_|   \___/|_|\_\___| |_|  \___/ \___/  \___  \__,_|  |_| \_|\___/ \__,_|\___|
                                            |___/                              
🎮 Pokémon Data Solver for Reppo Exchange
"""

@click.group()
def cli():
    """Pokémon Solver Node CLI - Generate Pokémon datasets for RFDs"""
    pass

@cli.command()
@click.option('--test', is_flag=True, help='Test mode: Process a sample Pokémon RFD file')
@click.option('--mock', is_flag=True, help='Mock mode: Simulate the entire pipeline with mock data')
@click.option('--rfd-file', default='sample_pokemon_rfd.json', help='Path to Pokémon RFD JSON file')
def start(test: bool, mock: bool, rfd_file: str):
    """Start the Pokémon solver node
    
    Test mode (--test):
    - Processes a sample Pokémon RFD file
    - Uses real Pokémon data from PokéAPI
    - Skips blockchain interactions
    - Good for testing Pokémon data generation
    
    Mock mode (--mock):
    - Simulates the entire pipeline
    - Uses mock data generation
    - Uses mock blockchain responses
    - Good for development and debugging
    
    Production mode (default):
    - Listens for RFDs on blockchain
    - Processes Pokémon-related RFDs
    - Uses real blockchain interactions
    """
    print(BANNER)
    
    # Initialize solver node
    try:
        node = SolverNode(
            test_mode=test,
            mock_mode=mock
        )
    except Exception as e:
        logger.error(f"Failed to initialize Pokémon solver node: {str(e)}")
        return
    
    # Run the node
    try:
        if test or mock:
            node._run_test_mode(rfd_file)
        else:
            node._run_production_mode()
    except KeyboardInterrupt:
        logger.info("Pokémon solver node stopped by user")
    except Exception as e:
        logger.error(f"Pokémon solver node failed: {str(e)}")

@cli.command()
@click.option('--type', 'data_type', default='pokemon', help='Type of Pokémon data (pokemon, moves, abilities, types, evolution)')
@click.option('--generation', type=int, help='Pokémon generation (1-9)')
@click.option('--count', default=10, help='Number of records to generate')
def pokemon(data_type: str, generation: int, count: int):
    """Quick Pokémon data generation test"""
    print(BANNER)
    print(f"\n🎮 Generating {count} {data_type} records...")
    if generation:
        print(f"📊 Filtering by Generation {generation}")
    
    try:
        node = SolverNode(test_mode=True, mock_mode=False)
        
        # Create a quick RFD for the requested data
        quick_rfd = {
            "rfd_id": f"quick_{data_type}_{generation or 'all'}",
            "name": f"Quick {data_type.title()} Data Generation",
            "description": f"Generate {count} {data_type} records" + (f" from generation {generation}" if generation else ""),
            "data_type": data_type,
            "num_records": count
        }
        
        if generation:
            quick_rfd["generation"] = generation
            
        # Process the RFD
        results = node.process_rfd(quick_rfd)
        if results:
            print(f"✅ Successfully generated Pokémon data: {results}")
        else:
            print("❌ Failed to generate Pokémon data")
    except Exception as e:
        logger.error(f"Pokémon generation failed: {str(e)}")

@cli.command()
def test():
    """Run the default Pokémon test with sample RFD"""
    print(BANNER)
    print("\n🎮 Running Pokémon Test...")
    
    try:
        node = SolverNode(test_mode=True, mock_mode=False)
        node._run_test_mode("sample_pokemon_rfd.json")
    except Exception as e:
        logger.error(f"Pokémon test failed: {str(e)}")

@cli.command()
def cache_stats():
    """Show IPFS cache statistics"""
    print(BANNER)
    print("\n📊 IPFS Cache Statistics...")
    
    try:
        from datasolver.providers.mcp.tools.pokemon import PokemonTool
        tool = PokemonTool()
        stats = tool.get_cache_stats()
        
        print(f"📈 Cache Status:")
        print(f"  • Pinata Available: {'✅' if stats['pinata_available'] else '❌'}")
        print(f"  • Total Entries: {stats['total_entries']}")
        print(f"  • Valid Entries: {stats['valid_entries']}")
        print(f"  • Expired Entries: {stats['expired_entries']}")
        print(f"  • TTL: {stats['ttl_seconds']} seconds ({stats['ttl_seconds']//60} minutes)")
        
        if stats['expired_entries'] > 0:
            cleared = tool.clear_expired_cache()
            print(f"  • Cleared {cleared} expired entries")
        
    except Exception as e:
        logger.error(f"Cache stats failed: {str(e)}")

if __name__ == '__main__':
    cli()