from typing import List
from block import create_genesis_block, Block, deserialize_block
from transaction import verify_transaction, Transaction, comfirm_tx, deserialize_transaction
from merkle_tree import MerkleTree
from proof_of_work import verify_pow
from utxo import UTXOSet
from copy import deepcopy

class BlockChain:
    """区块链"""
    def __init__(self):
        self.data: List[str] = []

    def add_block(self, block: Block, utxo_set: UTXOSet) -> bool:
        """向区块链中加入区块"""
        if verify_block(block=block, utxo_set=utxo_set):
            self.data.append(block.serialize().hex())
            comfirm_tx(utxo_set=utxo_set, transactions=block.transactions)
            return True
        else:
            return False
        
    def find_tx(self, tx_id: str) -> Transaction:
        """在区块链中寻找一个已确认的交易"""
        for block in self.data:
            block = deserialize_block(bytes.fromhex(block))
            transactions = block.transactions
            for tx in transactions: 
                tx = deserialize_transaction(bytes.fromhex(tx))
                if tx.hash() == tx_id:
                    return tx
        return None
    
    def find_block_by_hash(self, block_hash: str) -> Block:
        """在区块链中寻找一个区块"""
        for block in self.data:
            block = deserialize_block(bytes.fromhex(block))
            if block.block_header.hash() == block_hash:
                return block
        return None
    
    def get_best_height(self) -> int:
        """获得最新区块高度"""
        return len(self.data) - 1
    
    def get_best_block_hash(self) -> str:
        """获得最新区块的哈希值"""
        return deserialize_block(bytes.fromhex(self.data[-1])).block_header.hash()

def create_block_chain(to: str, coinbase_str: str, utxo_set: UTXOSet) -> BlockChain:
    """创建创世区块并生成一个新的区块链"""
    block_chain = BlockChain()
    genesis_block = create_genesis_block(to=to, coinbase_str=coinbase_str)
    block_chain.data.append(genesis_block.serialize().hex())
    comfirm_tx(utxo_set=utxo_set, transactions=genesis_block.transactions)
    return block_chain  # 返回BlockChain实例

def verify_block(block: Block, utxo_set: UTXOSet) -> bool:
    """验证区块"""
    is_valid = True
    is_valid = is_valid and verify_pow(header=block.block_header)
    transactions = block.transactions
    merkle_root_hash = MerkleTree(transactions=deepcopy(transactions)).root_node.data
    is_valid = is_valid and (block.block_header.merkle_root_hash == merkle_root_hash)
    for tx in transactions:
        tx = deserialize_transaction(bytes.fromhex(tx))
        is_valid = is_valid and verify_transaction(tx=tx, utxo_set=utxo_set) 
    return is_valid


