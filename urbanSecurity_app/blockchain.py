# urbanSecurity_app/blockchain.py
# Local blockchain simulation using SHA-256 hash chaining.
# Replaces Hyperledger Fabric SDK (not pip-installable for MVP).
# Tamper-proof: each block's hash depends on the previous block's hash.

import hashlib
import json
from datetime import datetime


class LocalBlockchain:
    """In-memory blockchain with SHA-256 hash chain for tamper-proof audit logs."""
    _chain = []

    @classmethod
    def _compute_hash(cls, data_str, prev_hash):
        raw = f"{prev_hash}|{data_str}|{datetime.utcnow().isoformat()}"
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()

    @classmethod
    def add_block(cls, data):
        """Add a new block to the chain. Returns the block dict."""
        prev_hash = cls._chain[-1]['hash'] if cls._chain else '0' * 64
        block_hash = cls._compute_hash(data, prev_hash)
        block = {
            'index': len(cls._chain),
            'data': data,
            'hash': block_hash,
            'prev_hash': prev_hash,
            'timestamp': datetime.utcnow().isoformat(),
        }
        cls._chain.append(block)
        return block

    @classmethod
    def get_chain(cls):
        """Return the full chain."""
        return list(cls._chain)

    @classmethod
    def verify_chain(cls):
        """Verify integrity of the chain. Returns True if untampered."""
        if len(cls._chain) <= 1:
            return True
        for i in range(1, len(cls._chain)):
            if cls._chain[i]['prev_hash'] != cls._chain[i - 1]['hash']:
                return False
        return True

    @classmethod
    def get_block(cls, index):
        """Get a specific block by index."""
        if 0 <= index < len(cls._chain):
            return cls._chain[index]
        return None

    @classmethod
    def reset(cls):
        """Reset chain (for testing only)."""
        cls._chain = []