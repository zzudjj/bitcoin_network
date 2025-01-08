from hashlib import sha256
from typing import List

class MerkleTreeNode:
    """Merkle树节点"""
    def __init__(self, left: 'MerkleTreeNode', right: 'MerkleTreeNode', data: str):
        self.left = left
        self.right = right
        self.data = data
        if left == None and right == None:
            self.data = sha256(sha256(bytes.fromhex(self.data)).digest()).hexdigest()
        else:
            self.data = sha256(sha256(bytes.fromhex(self.left.data+self.right.data)).digest()).hexdigest()

class MerkleTree:
    """Merkle树"""
    def __init__(self, transactions: List[str]):
        self.root_node = self.merkle_root_node(transactions=transactions)

    @staticmethod
    def merkle_root_node(transactions: List[str]) -> MerkleTreeNode:
        """根据一个交易列表获得Merkle树的根节点"""
        nodes = []
        if len(transactions) % 2 != 0:
            transactions.append(transactions[-1])
        
        for tx in transactions:
            node = MerkleTreeNode(left=None, right=None, data=tx)
            nodes.append(node)
        
        while len(nodes) > 1:
            if len(nodes) % 2 != 0:
                nodes.append(nodes[-1])
            new_nodes = []
            for i in range(0, len(nodes), 2):
                node = MerkleTreeNode(nodes[i], nodes[i+1], None)
                new_nodes.append(node)
            nodes = new_nodes
        return nodes[0]
