from hashlib import sha256
import json
import pickle
from typing import Dict, List, Union
from ecdsa import SigningKey, SECP256k1
from bitcoin_script import get_script_pubkey, get_script_sig
from transaction_input import TransactionInput
from transaction_output import TransactionOutput
from coinbase_input import CoinbaseInput
from wallet import Wallet

class Transaction:
    '''比特币交易类'''
    def __init__(self, version: float, vin_sz: int, vout_sz: int, lock_time: int, inputs, outputs: List[TransactionOutput]):
        self.version = version  #版本
        self.vin_sz = vin_sz    #交易输入列表中交易数量
        self.vout_sz = vout_sz  #交易输出列表中交易数量
        self.lock_time = lock_time  #交易锁定时间
        self.inputs = inputs  #输入列表
        self.outputs = outputs  #输出列表   

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "version": self.version,
            "vin_sz": self.vin_sz,
            "vout_sz": self.vout_sz,
            "lock_time": self.lock_time,
            "inputs": [tx_input.to_dict() for tx_input in self.inputs],
            "outputs": [tx_output.to_dict() for tx_output in self.outputs]
        }

    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict(), indent=4)
    
    def serialize(self) -> bytes:
         """交易序列化"""
         return pickle.dumps(self)

    def is_coinbase(self) -> bool:
        """该交易是否是创币交易"""
        return type(self.inputs) == CoinbaseInput
    
    def trimmed_copy(self) -> 'Transaction':
        """返回该交易修剪之后的复制实例"""
        inputs = []
        for tx_input in self.inputs:
            inputs.append(TransactionInput(tx_id=tx_input.tx_id, index=tx_input.index, script_sig=None))
        return Transaction(version=self.version, vin_sz=self.vin_sz, vout_sz=self.vout_sz, lock_time=self.lock_time, inputs=inputs, outputs=self.outputs)
    
    def hash(self) -> str:
        """计算交易哈希"""
        tx_hash = sha256(self.serialize()).hexdigest()
        return sha256(bytes.fromhex(tx_hash)).hexdigest()

    def sign(self,  private_key: str):
        """签名"""
        if self.is_coinbase():
            return
        tx_copy = self.trimmed_copy()
        for i in range(0, len(tx_copy.inputs)):
            tx_copy.inputs[i].script_sig = self.inputs[i].script_sig
            tx_copy_id = tx_copy.hash()
            sk = SigningKey.from_string(bytes.fromhex(private_key), curve=SECP256k1)
            signature = sk.sign(bytes.fromhex(tx_copy_id)).hex()
            self.inputs[i].script_sig = get_script_sig(sig=signature, pubkey=tx_copy.inputs[i].script_sig)
            tx_copy.inputs[i].script_sig = None

def create_transaction(version=1, lock_time=0, send: Wallet=None, to: List[str]=None, value: List[int]=None) -> Transaction:
    if Wallet == None or to == None or len(to) == 0:
       print("交易创建出错")
    pass


def verify_transaction(tx: Transaction) -> bool:
    '''验证交易'''
    pass

def deserialize_trasaction(data: bytes) -> Transaction:
    """反序列化为交易实例"""
    data = pickle.loads(data)


        
        