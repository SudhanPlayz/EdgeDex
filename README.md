# EdgeDex 🎮
*Edge Caching + Pokédex = EdgeDex*

![EdgeDex](https://img.shields.io/badge/Version-0.1.0-blue.svg) ![License](https://img.shields.io/badge/License-MIT-green.svg)

**EdgeDex** is a specialized decentralized application that combines edge caching with Pokémon data delivery for the **Reppo.Exchange** ecosystem. This high-performance solver node focuses exclusively on Pokémon-related data generation using the PokéAPI with IPFS-backed caching, making it perfect for AI agents, researchers, and developers who need fast, reliable access to comprehensive Pokémon data.

EdgeDex listens for Pokémon-related Requests for Data (RFDs), generates datasets using the PokéAPI through the Model Context Protocol (MCP), caches results on IPFS via Pinata, and submits solutions to the Reppo Exchange smart contract.

---

## Table of Contents 📋

- [Overview](#overview)
- [Pokémon Data Capabilities](#pokémon-data-capabilities)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Example Pokémon RFDs](#example-pokémon-rfds)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)

---

## Overview ✨

EdgeDex provides:
- **⚡ Edge Caching**: IPFS-backed caching via Pinata for sub-second response times
- **🔗 Comprehensive Pokémon Data**: Access to complete Pokémon information via PokéAPI
- **🏗️ MCP-Compliant Architecture**: Uses Model Context Protocol for standardized data access
- **📊 Multiple Data Types**: Pokémon stats, moves, abilities, types, evolution chains, and more
- **⛓️ Blockchain Integration**: Participates in the Reppo Exchange ecosystem
- **🎯 Generation Filtering**: Support for all Pokémon generations (1-9)
- **🔄 Real-time API Access**: Always up-to-date data from the official PokéAPI

EdgeDex performs these key functions:
1. **🎮 Pokémon RFD Processing**: Automatically detects and processes Pokémon-related requests
2. **📡 PokéAPI Integration**: Fetches real-time data from the comprehensive Pokémon database
3. **💾 Edge Caching**: Stores frequently requested datasets on IPFS for instant access
4. **📋 Data Generation**: Creates structured datasets with stats, abilities, moves, and more
5. **🌐 IPFS Storage**: Stores datasets on IPFS for decentralized access
6. **⛓️ Blockchain Submission**: Submits solutions to the Reppo Exchange for rewards

---

## Pokémon Data Capabilities 🎯

The solver supports generating various types of Pokémon data:

### Individual Pokémon Data
- **Basic Info**: ID, name, height, weight, base experience
- **Types**: Primary and secondary types
- **Stats**: HP, Attack, Defense, Special Attack, Special Defense, Speed
- **Abilities**: Normal and hidden abilities with descriptions
- **Moves**: Learnable moves with learn methods (optional)

### Specialized Data Types
- **Moves**: Power, PP, accuracy, type, damage class, effects
- **Abilities**: Descriptions, generation introduced, main series flag
- **Types**: Type effectiveness relationships and damage multipliers
- **Evolution Chains**: Complete evolution trees with triggers and requirements

### Filtering Options
- **Generation**: Filter by Pokémon generation (1-9)
- **Type**: Filter by specific Pokémon types (fire, water, grass, etc.)
- **Custom Lists**: Specify exact Pokémon by name or ID
- **Stat Inclusion**: Choose which data to include for optimal dataset size

---

## Architecture 🏗️

EdgeDex uses a focused, MCP-compliant architecture with IPFS edge caching:

### Core Components

1. **PokemonTool (`datasolver/providers/mcp/tools/pokemon.py`)**
   - **Purpose**: MCP tool for generating Pokémon datasets with edge caching
   - **Functionality**: 
     - Connects to PokéAPI via direct HTTP requests
     - Generates various Pokémon data types
     - Implements IPFS-backed caching via Pinata
     - Validates RFD requirements
     - Cache-first data retrieval
   - **Dependencies**: `requests`, IPFS cache layer

2. **MCPClient (`datasolver/providers/mcp/client.py`)**
   - **Purpose**: MCP client specialized for Pokémon tools
   - **Functionality**: 
     - Manages PokemonTool registration
     - Routes RFDs to appropriate data generation methods
     - Handles tool validation and execution
   - **Dependencies**: Simplified MCP implementation

3. **DataSolver (`datasolver/datasolver.py`)**
   - **Purpose**: Main solver orchestrator for Pokémon data
   - **Functionality**: 
     - Auto-detects Pokémon-related RFDs
     - Manages dataset generation workflow
     - Saves datasets in structured format
   - **Dependencies**: MCP provider ecosystem

4. **Blockchain Components** (unchanged from base Reppo solver)
   - **RFDListener**: Monitors for Pokémon-related RFDs
   - **IPFSUploader**: Stores datasets on IPFS
   - **NFTAuthorizer**: Verifies Reppo NFT ownership
   - **SolutionSubmitter**: Submits solutions to blockchain

4. **IPFSCache (`datasolver/providers/mcp/tools/ipfs_cache.py`)**
   - **Purpose**: IPFS-backed edge caching layer using Pinata
   - **Functionality**: 
     - RFD fingerprinting for cache key generation
     - Pinata JSON upload/download with 30-minute TTL
     - Automatic cache expiration and cleanup
     - Graceful degradation when Pinata unavailable
   - **Dependencies**: Pinata API, deterministic hashing

### Workflow

1. **🎯 RFD Detection**: Listens for RFDs containing Pokémon keywords
2. **🔍 Cache Check**: First checks IPFS cache for existing data (sub-second response)
3. **📊 Data Type Analysis**: Determines what type of Pokémon data is requested (if cache miss)
4. **📡 API Querying**: Fetches data from PokéAPI with appropriate filters (if cache miss)
5. **💾 Cache Storage**: Stores generated data in IPFS via Pinata for future requests
6. **📋 Dataset Assembly**: Structures data according to RFD schema requirements
7. **🌐 IPFS Upload**: Stores final dataset for decentralized access
8. **⛓️ Solution Submission**: Submits to Reppo Exchange for validation

---

## Prerequisites ✅

To run EdgeDex, ensure you have the following:

- **Python**: Version 3.8 or higher
- **Internet Connection**: Required for PokéAPI access
- **Ethereum Node Access**: RPC URL for blockchain interactions (production mode)
- **Pinata Account**: API keys for IPFS pinning (production mode)
- **Reppo Node NFT**: Required for solution submission (production mode)

### For Testing (Minimal Requirements)
- Python 3.8+
- Internet connection for PokéAPI
- Basic environment setup

### For Production
- All testing requirements plus:
- Ethereum wallet with Reppo NFT
- Pinata IPFS account
- Ethereum node access (Infura/Alchemy)

---

## Installation 💾

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/edgedex.git
   cd edgedex
   ```

2. **Set Up a Virtual Environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create the Output Directory**:
   ```bash
   mkdir data
   ```

5. **Configure Environment Variables** (for production):
   Create a `.env` file in the project root (see [Configuration](#configuration)).

---

## Configuration ⚙️

### Environment Variables

#### Test Mode (Minimal Setup)
```env
# Optional - any wallet address for testing
WALLET_ADDRESS=0xYourTestWalletAddress
```

#### Production Mode (Full Setup)
```env
# Ethereum configuration
WEB3_RPC_URL=https://mainnet.infura.io/v3/your-infura-key
CHAIN_ID=1
WALLET_ADDRESS=0xYourWalletAddress
PRIVATE_KEY=your-private-key

# Reppo Exchange smart contract
EXCHANGE_CONTRACT_ADDRESS=0xExchangeContractAddress
EXCHANGE_CONTRACT_ABI_PATH=./abis/exchange_abi.json

# Reppo Node NFT contract
NFT_CONTRACT_ADDRESS=0xNFTContractAddress
NFT_CONTRACT_ABI_PATH=./abis/nft_abi.json

# Pinata IPFS configuration
PINATA_API_KEY=your-pinata-api-key
PINATA_SECRET_API_KEY=your-pinata-secret-api-key
```

**Security Notes**:
- Keep your `PRIVATE_KEY` secure and never commit it
- The `.env` file should be in your `.gitignore`
- Test mode doesn't require sensitive credentials

---

## IPFS Edge Caching 🚀

EdgeDex features a sophisticated IPFS-backed caching layer using Pinata for lightning-fast data retrieval:

### Cache Performance
- **🎯 Cache Hit**: Sub-second response times from IPFS
- **⚡ Speed Improvement**: 3-5x faster than fresh API calls
- **🔄 TTL**: 30-minute cache expiration for data freshness
- **🌐 Decentralized**: Cached on IPFS for global accessibility

### Cache Features
- **Fingerprinting**: Deterministic cache keys based on RFD parameters
- **Automatic Storage**: Fresh data automatically cached on IPFS via Pinata
- **Graceful Degradation**: Falls back to direct API if cache unavailable
- **Cache Management**: Built-in statistics and cleanup functionality

### Cache Demo
```bash
# Run the IPFS cache demonstration
python test_cache_demo.py
```

This will show you:
- Fresh data generation and caching
- Cache hit performance improvements  
- Cache statistics and management

---

## Usage 🖥️

EdgeDex offers several commands for different use cases:

### Quick Pokémon Data Generation
```bash
# Generate 10 random Pokémon
python main.py pokemon

# Generate Generation 1 Pokémon
python main.py pokemon --generation 1 --count 20

# Generate move data
python main.py pokemon --type moves --count 50

# Generate evolution chains
python main.py pokemon --type evolution --count 10
```

### Test with Sample RFD
```bash
# Run the default Pokémon test
python main.py test

# Test with custom RFD file
python main.py start --test --rfd-file my_pokemon_rfd.json
```

### Production Mode
```bash
# Start listening for Pokémon RFDs on blockchain
python main.py start
```

### Development Mode
```bash
# Mock mode for development
python main.py start --mock
```

### Cache Management
```bash
# View cache statistics
python main.py cache-stats

# Run cache performance demo
python test_cache_demo.py
```

---

## Example Pokémon RFDs 📊

Below are examples of Pokémon RFDs that EdgeDex can process:

```json
{
    "rfd_id": "generation_1_starter_pokemon",
    "name": "Generation 1 Starter Pokémon Dataset",
    "description": "Complete dataset of Generation 1 starter Pokémon including stats, types, and abilities",
    "data_type": "pokemon",
    "num_records": 9,
    "generation": 1,
    "pokemon_names": ["bulbasaur", "ivysaur", "venusaur", "charmander", "charmeleon", "charizard", "squirtle", "wartortle", "blastoise"],
    "include_stats": true,
    "include_abilities": true,
    "include_moves": false
}
```

```json
{
    "rfd_id": "powerful_water_moves",
    "name": "High-Power Water Type Moves",
    "description": "Dataset of powerful water-type moves with 80+ base power",
    "data_type": "moves",
    "num_records": 15,
    "type_filter": "water"
}
```

When processed, EdgeDex:
- 🔍 Checks IPFS cache for existing matching data (sub-second if cached)
- 📡 Generates fresh Pokémon data from PokéAPI if not cached
- 💾 Stores the dataset in IPFS cache via Pinata for future requests
- 📋 Saves it as `data/rfd_generation_1_starter_pokemon_solution.json`
- 🌐 Uploads final result to IPFS, obtaining an `ipfs://<CID>` URI
- ⛓️ Submits the URI to the Reppo Exchange smart contract if the wallet owns a Reppo Node NFT

---

## Dependencies 📦

EdgeDex relies on the following Python packages, listed in `requirements.txt`:

```text
# Blockchain interactions
web3>=6.10.0
eth-account>=0.9.0
eth-typing>=3.4.0
eth-utils>=2.2.0

# HTTP requests
requests>=2.31.0

# Environment variables
python-dotenv>=1.0.0

# JSON processing
json5>=0.9.14

# CLI interface
click>=8.1.7

# Testing
pytest>=7.4.0
pytest-mock>=3.11.1
```

Install them using:
```bash
pip install -r requirements.txt
```

---

## Contributing 🤝

We welcome contributions to improve EdgeDex! To contribute:

1. **Fork the Repository**:
   ```bash
   git clone https://github.com/your-repo/pokemon-solver-node.git
   ```

2. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/your-feature
   ```

3. **Make Changes**:
   - Follow PEP 8 for Python code style.
   - Add tests for new functionality in the `tests/` directory.
   - Update documentation if necessary.

4. **Submit a Pull Request**:
   - Push your branch to your fork and create a pull request against the main repository.
   - Describe your changes clearly in the pull request description.

5. **Run Tests**:
   ```bash
   pytest
   ```

Please report issues or feature requests via the GitHub issue tracker.

---

## License 📜

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

This README provides a comprehensive guide to understanding, setting up, and running EdgeDex. For further questions, please open an issue on the GitHub repository or contact the maintainers.
