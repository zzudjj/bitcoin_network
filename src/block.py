import json
import pickle
import time
from typing import List
from merkle_tree import MerkleTree
from proof_of_work import pow
from block_header import BlockHeader

class Block:
    """区块类"""
    def __init__(self, block_header: BlockHeader, tx_num: int, transactions: List[str]):
        self.block_header = block_header
        self.tx_num = tx_num
        self.trsactions = transactions

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "block_header": self.block_header.to_dict(),
            "tx_num": self.tx_num,
            "trsactions": self.trsactions
        }
    
    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict(), indent=4)
    
    def serialize(self) -> bytes:
         """区块序列化"""
         return pickle.dumps(self)
    
def deserialize_block(data: bytes) -> Block:
    """区块反序列化"""
    return pickle.loads(data)

def create_block(transactions: List[str], pre_block_hash: str) -> Block:
    merkle_tree = MerkleTree(transactions=transactions)
    merkle_root_hash = merkle_tree.root_node.data
    block_header = BlockHeader(version=1, 
                               pre_block_hash=pre_block_hash, 
                               merkle_root_hash=merkle_root_hash, 
                               timestamp=time.time(), 
                               target_bits=20,
                               nonce=0
                               )
    block_hash, nonce = pow(block_header)
    block_header.nonce = nonce
    block = Block(block_header=block_header, tx_num=len(transactions), transactions=transactions)
    return block



        

       