import pickle
import threading
import random
import time
from memory_pool import MemmoryPool
from utxo import load_utxo_set, UTXOSet
from wallet import load_wallet, Wallet
from block_chain import create_block_chain, load_block_chain, BlockChain, verify_block
from block import deserialize_block, create_block
from transaction import deserialize_transaction, create_transaction
import os

class Node(threading.Thread):
    def __init__(self, node_id, network, dir):
        super().__init__()
        self.node_id: int = node_id
        self.network: 'Network' = network  # 网络对象，负责节点间通信
        self.mem_pool = MemmoryPool()
        self.block_chain: BlockChain = None
        self.utxo_set: UTXOSet = None
        self.wallet: Wallet = None
        self.dir = dir
        self.init_data(dir)

    def broadcast_transaction(self, transaction: str):
        """广播交易"""
        self.network.broadcast(self.node_id, "transaction", transaction)
        print(f"节点 {self.node_id} 广播了交易: {deserialize_transaction(bytes.fromhex(transaction)).hash()}")

    def broadcast_block(self, block: str):
        """广播区块"""
        self.network.broadcast(self.node_id, "block", block)
        print(f"节点 {self.node_id} 广播了区块: {deserialize_block(bytes.fromhex(block)).hash()}")

    def broadcast_version(self):
        """广播 version 消息"""
        self.network.broadcast(self.node_id, "version", VersionMessage(node_id=self.node_id, best_height=self.block_chain.get_best_height()).serlialize().hex())
        print(f"节点 {self.node_id} 广播了版本消息: {self.block_chain.get_best_height()}")

    def send_data(self, to_node_id: int, message_type: str, data: str):
        """发送消息"""
        self.network.messages[to_node_id].append((self.node_id, message_type, data))


    def process_message(self, sender_id: int, message_type: str, data: str):
        """处理消息"""
        if message_type == "transaction":
            # print(f"节点 {self.node_id} 收到来自节点 {sender_id} 的交易")
            self.mem_pool.add_tx(deserialize_transaction(bytes.fromhex(data)))
        elif message_type == "block":
            # print(f"节点 {self.node_id} 收到来自节点 {sender_id} 的区块")
            block = deserialize_block(bytes.fromhex(data))
            if verify_block(block=block, utxo_set=self.utxo_set):
                self.block_chain.add_block(block=block, utxo_set=self.utxo_set)
        elif message_type == "version":
            # print(f"节点 {self.node_id} 收到来自节点 {sender_id} 的版本消息")
            version_message = VersionMessage.deserialize(bytes.fromhex(data))
            if version_message.best_height > self.block_chain.get_best_height():
                self.send_data(to_node_id=sender_id, message_type="getblocks", data="")
                self.send_data(to_node_id=sender_id, message_type="getutxos", data="")
            elif version_message.best_height < self.block_chain.get_best_height():
                self.broadcast_version()
        elif message_type == "getblocks":
            # print(f"节点 {self.node_id} 收到来自节点 {sender_id} 的获取区块消息")
            self.send_data(to_node_id=sender_id, message_type="blocks", data=self.block_chain)
        elif message_type == "blocks":
            # print(f"节点 {self.node_id} 收到来自节点 {sender_id} 的区块消息")
            new_chain = data
            self.block_chain.update_all(new_chain=new_chain)
        elif message_type == "getutxos":
            # print(f"节点 {self.node_id} 收到来自节点 {sender_id} 的获取UTXO消息")
            self.send_data(to_node_id=sender_id, message_type="utxos", data=self.utxo_set)
        elif message_type == "utxos":
            # print(f"节点 {self.node_id} 收到来自节点 {sender_id} 的UTXO消息")
            new_utxo_set = data
            self.utxo_set.update_utxo_set(utxo_set=new_utxo_set)
        elif message_type == "getbalance":
            print(f'地址{data}的比特余额:{self.utxo_set.get_balance_by_address(data)}')
            self.send_data(to_node_id=sender_id, message_type="reply", data=True)        
        elif message_type == "create_tx":
            if data['tx_fee'] == None:
                data['tx_fee'] = 0.05
            tx = create_transaction(send=self.wallet, to=data['to'], value=data['value'], utxo_set=self.utxo_set, tx_fee=data['tx_fee'])
            if tx:
                self.mem_pool.add_tx(tx)
                self.broadcast_transaction(tx.serialize().hex())
                self.send_data(to_node_id=sender_id, message_type="reply", data=True)
        elif message_type == "get_tx":
            tx = self.block_chain.find_tx(data)
            if tx:
                print(tx.to_json())
            else:
                print('没有找到交易')
            self.send_data(to_node_id=sender_id, message_type="reply", data=True) 
        elif message_type == "get_block":
            block = self.block_chain.find_block_by_hash(data)
            if block:
                print(block.to_json())
            else:
                print('没有找到区块')
            self.send_data(to_node_id=sender_id, message_type="reply", data=True) 
        elif message_type == "get_best_height":
            print(f'最新区块高度为:{self.block_chain.get_best_height()}')
            self.send_data(to_node_id=sender_id, message_type="reply", data=True) 
        elif message_type == "get_best_block_hash":
            print(f'最新区块哈希值为:{self.block_chain.get_best_block_hash()}')
            self.send_data(to_node_id=sender_id, message_type="reply", data=True) 
        elif message_type == "create_block":
            block = create_block(block_height=self.block_chain.get_best_height()+1, pre_block_hash=self.block_chain.get_best_block_hash(), mem_pool=self.mem_pool, address=self.wallet.get_address(), utxo_set=self.utxo_set)
            if block:
                self.block_chain.add_block(block=block, utxo_set=self.utxo_set)
                self.broadcast_block(block.serialize().hex())
                self.send_data(to_node_id=443, message_type="reply", data=True) 
        elif message_type == "list_address":
            print(self.wallet.get_address())
            self.send_data(to_node_id=443, message_type="reply", data=True) 
        elif message_type == "print_blocks":
            print(self.block_chain.print_blocks())
            self.send_data(to_node_id=sender_id, message_type="reply", data=True) 

    def init_data(self, dir):
        """初始化数据"""
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.utxo_set = load_utxo_set(dir=dir+'/utxo.db')
        self.wallet = load_wallet(dir=dir+'/wallet.conf')
        if self.node_id == 0 and not os.path.exists(os.path.join(dir, 'block.db')):
            self.block_chain = create_block_chain(to=self.wallet.get_address(), utxo_set=self.utxo_set, dir=dir+'/block.db')
        else:
            self.block_chain = load_block_chain(dir=dir+'/block.db')

    def run(self):
        self.broadcast_version()
        while True:
            # 从网络获取所有未处理的消息
            messages = self.network.get_messages(self.node_id)
            for sender_id, message_type, data in messages:
                self.process_message(sender_id, message_type, data)
            time.sleep(random.uniform(0.5, 1))  # 模拟运行延迟


class Network:
    def __init__(self):
        self.lock = threading.Lock()
        self.messages = {}  # 存储每个节点的消息队列
        self.messages[443] = []  # 专门用于命令行的消息队列 
        self.mp = {}

    def register_node(self, node):
        """注册节点"""
        with self.lock:
            self.messages[node.node_id] = []
            self.mp[node.dir] = node.node_id

    def broadcast(self, sender_id, message_type, data):
        """广播消息"""
        with self.lock:
            for node_id, queue in self.messages.items():
                if node_id != sender_id:  # 不广播给自己
                    queue.append((sender_id, message_type, data))

    def get_messages(self, node_id):
        """获取节点的消息"""
        with self.lock:
            messages = self.messages[node_id]
            self.messages[node_id] = []  # 清空队列
        return messages
    
    def send_data(self, to_node_id: int, message_type: str, data: str):
        """专用于命令行向主网络发送消息"""
        self.messages[to_node_id].append((443, message_type, data))

class VersionMessage:
    """version消息"""
    def __init__(self, node_id: int, best_height: int):
        self.node_id = node_id
        self.best_height = best_height

    def serlialize(self) -> bytes:
        """序列化"""
        return pickle.dumps(self)
    
    def deserialize(data: bytes) -> 'VersionMessage':
        """反序列化"""
        return pickle.loads(data)
    

def create_and_start_node(node_id: int, network: Network, dir: str):
    """模拟比特币网络"""
    node = Node(node_id=node_id, network=network, dir=dir)  # 确保传递正确的整数值
    # 注册节点到网络
    network.register_node(node)
    # 启动节点
    node.start()
