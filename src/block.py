import json
import pickle
import time
from typing import List
from merkle_tree import MerkleTree
from proof_of_work import pow
from block_header import BlockHeader
from transaction import create_coinbase_transaction, verify_transaction, deserialize_transaction
from memory_pool import MemmoryPool
from utxo import UTXOSet
from copy import deepcopy

class Block:
    """区块类"""
    def __init__(self, block_header: BlockHeader, tx_num: int, transactions: List[str]):
        self.block_header = block_header
        self.tx_num = tx_num
        self.transactions = transactions

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "block_header": self.block_header.to_dict(),
            "tx_num": self.tx_num,
            "transactions": self.transactions
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

def create_block(block_height: int, coinbase_str: str, pre_block_hash: str, mem_pool: MemmoryPool, tx_num: int, utxo_set: UTXOSet, address: str) -> Block:
    """创建一个区块"""
    coinbase_tx = create_coinbase_transaction(block_height=block_height, to=address, coinbase_str=coinbase_str, value=50)
    transactions = [coinbase_tx.serialize().hex()]
    for _ in range(0, tx_num):
        tx = mem_pool.get_tx()
        if tx:
            tx_obj = deserialize_transaction(bytes.fromhex(tx))
            verify_transaction(tx=tx_obj, utxo_set=utxo_set)
            transactions.append(tx)
        else:
            break
    merkle_tree = MerkleTree(transactions=deepcopy(transactions))
    merkle_root_hash = merkle_tree.root_node.data
    block_header = BlockHeader(version=1, 
                               pre_block_hash=pre_block_hash, 
                               merkle_root_hash=merkle_root_hash, 
                               timestamp=time.time(), 
                               target_bits=18,
                               nonce=0
                               )
    block_hash, nonce = pow(block_header)
    block_header.nonce = nonce
    block = Block(block_header=block_header, tx_num=len(transactions), transactions=transactions)
    return block

def create_genesis_block(coinbase_str: str, to: str) -> Block:
    """创建一个创世区块"""
    coinbase_tx = create_coinbase_transaction(block_height=0, to=to, coinbase_str=coinbase_str, value=50)
    transactions = [coinbase_tx.serialize().hex()]
    merkle_tree = MerkleTree(transactions=deepcopy(transactions))
    merkle_root_hash = merkle_tree.root_node.data
    block_header = BlockHeader(version=1, 
                               pre_block_hash='0'*64, 
                               merkle_root_hash=merkle_root_hash, 
                               timestamp=time.time(), 
                               target_bits=18,
                               nonce=0
                               )
    block_hash, nonce = pow(block_header)
    block_header.nonce = nonce
    print(len(transactions))
    block = Block(block_header=block_header, tx_num=len(transactions), transactions=transactions)
    return block





