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
    
    def get_height(self) -> int:
        """获得区块高度"""
        if len(self.transactions) == 0:
            return 0
        coinbase_tx = deserialize_transaction(bytes.fromhex(self.transactions[0]))
        return coinbase_tx.inputs[0].get_block_height()
    
    def hash(self) -> str:
        return self.block_header.hash()
    
def deserialize_block(data: bytes) -> Block:
    """区块反序列化"""
    return pickle.loads(data)

def create_block(block_height: int, pre_block_hash: str, mem_pool: MemmoryPool, utxo_set: UTXOSet, address: str, tx_num: int=5, coinbase_str: str="Hello Bitcoin!") -> Block:
    """创建一个区块"""
    #从交易池中获取交易
    transactions = []
    for _ in range(0, tx_num):
        tx = mem_pool.get_tx()
        if tx:
            tx_obj = deserialize_transaction(bytes.fromhex(tx))
            verify_transaction(tx=tx_obj, utxo_set=utxo_set)
            transactions.append(tx)
        else:
            break
    #计算交易费
    tx_fee = calculate_transaction_fee(transactions=transactions, utxo_set=utxo_set)
    coinbase_tx = create_coinbase_transaction(block_height=block_height, to=address, coinbase_str=coinbase_str, tx_fee=tx_fee)
    transactions.insert(0, coinbase_tx.serialize().hex())
    #计算默克尔树根哈希
    merkle_tree = MerkleTree(transactions=deepcopy(transactions))
    merkle_root_hash = merkle_tree.root_node.data
    #创建区块头
    block_header = BlockHeader(version=1, 
                               pre_block_hash=pre_block_hash, 
                               merkle_root_hash=merkle_root_hash, 
                               timestamp=time.time(), 
                               target_bits=12,
                               nonce=0
                               )
    #计算工作量证明
    block_hash, nonce = pow(block_header)
    block_header.nonce = nonce
    block = Block(block_header=block_header, tx_num=len(transactions), transactions=transactions)
    return block

def create_genesis_block(coinbase_str: str, to: str) -> Block:
    """创建一个创世区块"""
    coinbase_tx = create_coinbase_transaction(block_height=0, to=to, coinbase_str=coinbase_str)
    transactions = [coinbase_tx.serialize().hex()]
    merkle_tree = MerkleTree(transactions=deepcopy(transactions))
    merkle_root_hash = merkle_tree.root_node.data
    block_header = BlockHeader(version=1, 
                               pre_block_hash='0'*64, 
                               merkle_root_hash=merkle_root_hash, 
                               timestamp=time.time(), 
                               target_bits=12,
                               nonce=0
                               )
    block_hash, nonce = pow(block_header)
    block_header.nonce = nonce
    block = Block(block_header=block_header, tx_num=len(transactions), transactions=transactions)
    return block

def calculate_transaction_fee(transactions: List[str], utxo_set: UTXOSet) -> float:
    """计算交易费"""
    fee = 0
    for tx in transactions:
        tx = deserialize_transaction(bytes.fromhex(tx))
        if tx.is_coinbase():
            continue
        input_value = 0
        output_value = 0
        utxos = utxo_set.find_utxo_by_vin(vin=tx.inputs)
        for utxo in utxos:
            input_value += utxo.value
        for vout in tx.outputs:
            output_value += vout.value
        fee += input_value - output_value
    return fee



