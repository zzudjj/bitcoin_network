from hashlib import sha256
import json
import pickle

class BlockHeader:
    """区块头"""
    def __init__(self, version: int, pre_block_hash: str, merkle_root_hash: str, timestamp: float, target_bits: int, nonce: int):
        self.version = version
        self.pre_block_hash = pre_block_hash
        self.merkle_root_hash = merkle_root_hash
        self.timestamp = timestamp
        self.target_bits = target_bits
        self.nonce = nonce

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "version": self.version,
            "pre_block_hash": self.pre_block_hash,
            "merkle_root_hash": self.merkle_root_hash,
            "timestamp": self.timestamp,
            "target_bits": self.target_bits,
            "nonce": self.nonce
        }
    
    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict(), indent=4)
    
    def serialize(self) -> bytes:
         """序列化"""
         return pickle.dumps(self.to_dict())
    
    def hash(self) -> str:
        """计算区块头哈希"""
        tx_hash = sha256(self.serialize()).hexdigest()
        return sha256(bytes.fromhex(tx_hash)).hexdigest()