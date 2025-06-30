#!/usr/bin/env python3
"""Standalone test for Pokemon MCP tool."""

import json
import sys
import os

# Add the datasolver path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'datasolver'))

def test_pokemon_tool():
    """Test the Pokemon tool directly."""
    print("🎮 Testing Pokémon MCP Tool...")
    
    try:
        # Import the Pokemon tool
        from providers.mcp.tools.pokemon import PokemonTool
        
        # Create tool instance
        tool = PokemonTool()
        print(f"✅ Created {tool.name} tool: {tool.description}")
        
        # Test with a simple Pokemon RFD
        test_rfd = {
            "rfd_id": "test_pokemon",
            "name": "Test Pokémon Data",
            "description": "Generate first 5 Pokémon for testing",
            "data_type": "pokemon",
            "num_records": 5,
            "generation": 1,
            "include_stats": True,
            "include_abilities": True,
            "include_moves": False
        }
        
        print("\n📝 Testing RFD validation...")
        is_valid = tool.validate_rfd(test_rfd)
        print(f"RFD validation result: {is_valid}")
        
        if is_valid:
            print("\n🔄 Generating Pokémon data...")
            result = tool.generate_data(test_rfd)
            
            print(f"✅ Generated {result['count']} {result['data_type']} records")
            print(f"Source: {result['source']}")
            
            # Save result to file
            output_file = "test_pokemon_output.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            print(f"📁 Saved results to {output_file}")
            
            # Show first record as sample
            if result['data'] and len(result['data']) > 0:
                print("\n📊 Sample record:")
                sample = result['data'][0]
                print(f"  Name: {sample.get('name', 'Unknown')}")
                print(f"  ID: {sample.get('id', 'Unknown')}")
                print(f"  Types: {sample.get('types', [])}")
                if 'stats' in sample:
                    hp = sample['stats'].get('hp', 'Unknown')
                    attack = sample['stats'].get('attack', 'Unknown')
                    print(f"  Stats: HP={hp}, Attack={attack}")
        else:
            print("❌ RFD validation failed")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure pokepy is installed: pip install pokepy")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pokemon_tool() 