#!/usr/bin/env python3
"""Demo script showing IPFS cache functionality for Pokemon data."""

import json
import sys
import os
import time

# Add the datasolver path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'datasolver'))

def demo_cache():
    """Demonstrate IPFS cache functionality."""
    print("🎮 IPFS Cache Demo for Pokémon Data")
    print("=" * 50)
    
    try:
        # Import the Pokemon tool
        from providers.mcp.tools.pokemon import PokemonTool
        
        # Create tool instance (this persists during the demo)
        tool = PokemonTool()
        print(f"✅ Created Pokemon tool with IPFS cache")
        
        # Show initial cache stats
        stats = tool.get_cache_stats()
        print(f"\n📊 Initial Cache Stats:")
        print(f"  • Pinata Available: {'✅' if stats['pinata_available'] else '❌'}")
        print(f"  • Cache Entries: {stats['total_entries']}")
        print(f"  • TTL: {stats['ttl_seconds']//60} minutes")
        
        # Test RFD - Generation 1, 3 Pokemon
        test_rfd = {
            "rfd_id": "cache_demo",
            "data_type": "pokemon",
            "num_records": 3,
            "generation": 1,
            "include_stats": True,
            "include_abilities": True,
            "include_moves": False
        }
        
        print(f"\n🔄 First Request (should fetch fresh data):")
        start_time = time.time()
        result1 = tool.generate_data(test_rfd)
        elapsed1 = time.time() - start_time
        
        print(f"  • Generated {result1['count']} records in {elapsed1:.2f}s")
        print(f"  • Source: {result1['source']}")
        print(f"  • Cached: {result1.get('cached', 'N/A')}")
        print(f"  • Cache Stored: {result1.get('cache_stored', 'N/A')}")
        
        # Show updated cache stats
        stats = tool.get_cache_stats()
        print(f"\n📊 Cache Stats After First Request:")
        print(f"  • Cache Entries: {stats['total_entries']}")
        print(f"  • Valid Entries: {stats['valid_entries']}")
        
        print(f"\n🔄 Second Request (should hit cache):")
        start_time = time.time()
        result2 = tool.generate_data(test_rfd)
        elapsed2 = time.time() - start_time
        
        print(f"  • Retrieved {result2['count']} records in {elapsed2:.2f}s")
        print(f"  • Source: {result2['source']}")
        print(f"  • Cached: {result2.get('cached', 'N/A')}")
        
        # Compare performance
        if elapsed1 > 0 and elapsed2 > 0:
            speedup = elapsed1 / elapsed2
            print(f"\n⚡ Performance Improvement: {speedup:.1f}x faster with cache!")
        
        # Test different request (should be fresh)
        test_rfd2 = {
            "rfd_id": "cache_demo2", 
            "data_type": "moves",
            "num_records": 5
        }
        
        print(f"\n🔄 Different Request - Moves (should fetch fresh):")
        start_time = time.time()
        result3 = tool.generate_data(test_rfd2)
        elapsed3 = time.time() - start_time
        
        print(f"  • Generated {result3['count']} {result3['data_type']} in {elapsed3:.2f}s")
        print(f"  • Cache Stored: {result3.get('cache_stored', 'N/A')}")
        
        # Final cache stats
        stats = tool.get_cache_stats()
        print(f"\n📊 Final Cache Stats:")
        print(f"  • Total Entries: {stats['total_entries']}")
        print(f"  • Valid Entries: {stats['valid_entries']}")
        
        print(f"\n✅ IPFS Cache Demo Complete!")
        print(f"   Cache is working with Pinata IPFS storage")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_cache() 