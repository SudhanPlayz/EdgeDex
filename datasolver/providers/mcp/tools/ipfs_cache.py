"""IPFS-backed cache layer for Pokémon data using Pinata."""

import json
import hashlib
import time
import logging
from typing import Dict, Any, Optional
import os

logger = logging.getLogger('IPFSCache')

class IPFSCache:
    """IPFS-backed cache using Pinata for Pokémon data."""
    
    def __init__(self, ttl_minutes: int = 60):
        """Initialize IPFS cache with Pinata.
        
        Args:
            ttl_minutes: Time-to-live for cache entries in minutes
        """
        # Load environment variables if not already loaded
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass  # dotenv not installed, environment should be set manually
        
        self.ttl_seconds = ttl_minutes * 60
        self.cache_metadata = {}  # In-memory metadata: fingerprint -> {cid, timestamp}
        self.pinata_available = self._check_pinata_config()
        
        if self.pinata_available:
            logger.info(f"IPFS cache initialized with {ttl_minutes}min TTL using Pinata")
        else:
            logger.warning("Pinata not configured, cache will be disabled")
    
    def _check_pinata_config(self) -> bool:
        """Check if Pinata is properly configured."""
        api_key = os.getenv("PINATA_API_KEY")
        secret_key = os.getenv("PINATA_SECRET_API_KEY")
        return bool(api_key and secret_key)
    
    def _fingerprint_rfd(self, rfd: Dict[str, Any]) -> str:
        """Create a deterministic fingerprint for an RFD."""
        # Create a stable representation by sorting keys
        cache_relevant_fields = {
            'data_type': rfd.get('data_type', 'pokemon'),
            'num_records': rfd.get('num_records', 10),
            'generation': rfd.get('generation'),
            'type_filter': rfd.get('type_filter'),
            'pokemon_names': sorted(rfd.get('pokemon_names', [])),
            'pokemon_ids': sorted(rfd.get('pokemon_ids', [])),
            'include_stats': rfd.get('include_stats', True),
            'include_abilities': rfd.get('include_abilities', True),
            'include_moves': rfd.get('include_moves', False)
        }
        
        # Remove None values for consistent hashing
        cleaned = {k: v for k, v in cache_relevant_fields.items() if v is not None}
        
        # Create stable JSON and hash it
        stable_json = json.dumps(cleaned, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(stable_json.encode()).hexdigest()[:16]  # First 16 chars
    
    def _upload_to_pinata(self, data: Dict[str, Any], cache_key: str) -> Optional[str]:
        """Upload data to Pinata and return CID."""
        if not self.pinata_available:
            return None
            
        try:
            import requests
            
            # Prepare the payload
            cache_payload = {
                'timestamp': int(time.time()),
                'cache_key': cache_key,
                'data': data
            }
            
            # Create a JSON file in memory
            json_data = json.dumps(cache_payload, indent=2)
            
            url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
            headers = {
                "Authorization": f"Bearer {os.getenv('PINATA_JWT_TOKEN', '')}",
                "Content-Type": "application/json"
            }
            
            # If no JWT token, use API keys
            if not headers["Authorization"] or headers["Authorization"] == "Bearer ":
                headers = {
                    "pinata_api_key": os.getenv("PINATA_API_KEY"),
                    "pinata_secret_api_key": os.getenv("PINATA_SECRET_API_KEY"),
                    "Content-Type": "application/json"
                }
            
            payload = {
                "pinataContent": cache_payload,
                "pinataMetadata": {
                    "name": f"pokemon_cache_{cache_key}",
                    "keyvalues": {
                        "type": "pokemon_cache",
                        "cache_key": cache_key
                    }
                }
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                cid = result.get("IpfsHash")
                logger.debug(f"Cached data to IPFS: {cid}")
                return cid
            else:
                logger.warning(f"Failed to upload to Pinata: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.warning(f"Error uploading to Pinata: {e}")
            return None
    
    def _fetch_from_ipfs(self, cid: str) -> Optional[Dict[str, Any]]:
        """Fetch data from IPFS using Pinata gateway."""
        try:
            import requests
            
            # Use Pinata's dedicated gateway or a public one
            gateway_url = f"https://gateway.pinata.cloud/ipfs/{cid}"
            # Fallback to public gateway
            fallback_url = f"https://ipfs.io/ipfs/{cid}"
            
            for url in [gateway_url, fallback_url]:
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        logger.debug(f"Retrieved cached data from IPFS: {cid}")
                        return data
                except Exception as e:
                    logger.debug(f"Failed to fetch from {url}: {e}")
                    continue
            
            logger.warning(f"Could not fetch data from IPFS CID: {cid}")
            return None
            
        except Exception as e:
            logger.warning(f"Error fetching from IPFS: {e}")
            return None
    
    def get_cached(self, rfd: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Try to get cached result for an RFD."""
        if not self.pinata_available:
            logger.debug("Pinata not available, skipping cache check")
            return None
            
        try:
            cache_key = self._fingerprint_rfd(rfd)
            logger.debug(f"Checking cache for key: {cache_key}")
            
            # Check if we have metadata for this cache key
            if cache_key not in self.cache_metadata:
                logger.debug(f"No cache metadata for key: {cache_key}")
                return None
            
            metadata = self.cache_metadata[cache_key]
            current_time = int(time.time())
            
            # Check if cache entry is expired
            if current_time - metadata['timestamp'] > self.ttl_seconds:
                logger.debug(f"Cache expired for key: {cache_key}")
                del self.cache_metadata[cache_key]
                return None
            
            # Fetch from IPFS
            cached_data = self._fetch_from_ipfs(metadata['cid'])
            if cached_data:
                logger.info(f"Cache HIT for RFD fingerprint: {cache_key}")
                return cached_data.get('data')
            else:
                # Remove invalid cache entry
                del self.cache_metadata[cache_key]
                return None
                
        except Exception as e:
            logger.warning(f"Error retrieving from cache: {e}")
            return None
    
    def store_cached(self, rfd: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """Store result in IPFS cache."""
        if not self.pinata_available:
            return False
            
        try:
            cache_key = self._fingerprint_rfd(rfd)
            
            # Upload to Pinata
            cid = self._upload_to_pinata(result, cache_key)
            if cid:
                # Store metadata locally
                self.cache_metadata[cache_key] = {
                    'cid': cid,
                    'timestamp': int(time.time())
                }
                logger.info(f"Cache STORE for RFD fingerprint: {cache_key} -> {cid}")
                return True
            else:
                return False
                
        except Exception as e:
            logger.warning(f"Error storing in cache: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        current_time = int(time.time())
        valid_entries = sum(1 for meta in self.cache_metadata.values() 
                          if current_time - meta['timestamp'] <= self.ttl_seconds)
        
        return {
            'total_entries': len(self.cache_metadata),
            'valid_entries': valid_entries,
            'expired_entries': len(self.cache_metadata) - valid_entries,
            'ttl_seconds': self.ttl_seconds,
            'pinata_available': self.pinata_available
        }
    
    def clear_expired(self) -> int:
        """Clear expired cache entries and return count of cleared entries."""
        current_time = int(time.time())
        expired_keys = [
            key for key, meta in self.cache_metadata.items()
            if current_time - meta['timestamp'] > self.ttl_seconds
        ]
        
        for key in expired_keys:
            del self.cache_metadata[key]
        
        if expired_keys:
            logger.info(f"Cleared {len(expired_keys)} expired cache entries")
        
        return len(expired_keys) 