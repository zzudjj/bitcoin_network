from hashlib import sha256
import json
import pickle
from typing import List
from ecdsa import SigningKey, SECP256k1
from bitcoin_script import get_script_pubkey, get_script_sig, execute_script
from transaction_input import TransactionInput
from transaction_output import TransactionOutput
from coinbase_input import CoinbaseInput
from wallet import Wallet
from utxo import UTXOSet, UTXO
from utils import get_pubkhash_from_address
from copy import deepcopy
from reward import get_coinbase_reward

class Transaction:
    '''比特币交易类'''
    def __init__(self, version: int, vin_sz: int, vout_sz: int, lock_time: int, inputs, outputs: List[TransactionOutput]):
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
        return type(self.inputs[0]) == CoinbaseInput
    
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

def create_transaction(send: Wallet, to: List[str], value: List[float], utxo_set: UTXOSet, version=1, lock_time=0, tx_fee=0.05) -> Transaction:
    """创建一个普通交易"""
    if Wallet == None or to == None or len(to) == 0:
       print("交易创建出错")
    send_address = send.get_address()
    pubkey = send.pubkey.to_string().hex()
    #如果发送者并没有明确后面的一些接收者应该接收的金额，value将默认复制最后一个金额
    while len(value) < len(to):
        value.append(value[-1])
    utxos_value_sum, utxos = utxo_set.find_utxo_by_address(address=send_address, value=sum(value)+tx_fee)
    inputs = []
    for tx_id, index in utxos:
        tx_in = TransactionInput(tx_id=tx_id, index=index, script_sig=pubkey)
        inputs.append(tx_in)
    if not inputs:  # 检查inputs是否为空
        raise ValueError("没有足够的UTXO来创建交易")
    outputs = []
    for i in range(0, len(value)):
        pubkey_hash = get_pubkhash_from_address(address=to[i])
        script_pubkey = get_script_pubkey(pubk_hash=pubkey_hash)
        tx_out = TransactionOutput(value=value[i], script_pubkey=script_pubkey)
        outputs.append(tx_out)
    #找零
    if utxos_value_sum > sum(value)+tx_fee:
        change_value = utxos_value_sum - sum(value) - tx_fee
        change_pubkhash = get_pubkhash_from_address(address=send_address)
        change_script_pubkey = get_script_pubkey(pubk_hash=change_pubkhash)
        change_tx_out = TransactionOutput(value=change_value, script_pubkey=change_script_pubkey)
        outputs.append(change_tx_out)
    tx = Transaction(version = version,
                     vin_sz=len(inputs),
                     vout_sz=len(outputs),
                     lock_time=lock_time,
                     inputs=inputs,
                     outputs=outputs)
    tx.sign(private_key=send.sigkey.to_string().hex())
    return tx

def create_coinbase_transaction(block_height: int, coinbase_str: str, to: str, tx_fee: float=0) -> Transaction:
    """创建一个铸币交易"""
    coinbase = CoinbaseInput(block_height=block_height, coinbase_str=coinbase_str)
    pubkhash = get_pubkhash_from_address(address=to)
    script_pubkey = get_script_pubkey(pubk_hash=pubkhash)
    value = get_coinbase_reward(block_height=block_height) + tx_fee
    output = TransactionOutput(value=value, script_pubkey=script_pubkey)
    outputs = [output]
    coinbase_tx = Transaction(version=1,
                              vin_sz=0,
                              vout_sz=1,
                              lock_time=0,
                              inputs=[coinbase],
                              outputs=outputs
                              )
    return coinbase_tx

def verify_transaction(tx: Transaction, utxo_set: UTXOSet) -> bool:
    '''验证交易'''
    if tx.is_coinbase():
        return True
    is_valid = True
    utxos = utxo_set.find_utxo_by_vin(vin=tx.inputs)
    tx_copy = tx.trimmed_copy()
    for i in range(0, len(utxos)):
        if utxos[i] == None:
            return False
        tx_copy.inputs[i].script_sig = tx.inputs[i].script_sig.split(' ')[1]
        is_valid = is_valid and execute_script(script_sig=tx.inputs[i].script_sig, script_pubkey=utxos[i].script_pubkey, tx_hash=tx_copy.hash())
        tx_copy.inputs[i].script_sig = None
    input_value = 0
    for utxo in utxos:
        input_value += utxo.value
    output_value = 0
    for tx_out in tx.outputs:
        output_value += tx_out.value
    is_valid = is_valid and (input_value >= output_value)
    return is_valid
    
def deserialize_transaction(data: bytes) -> Transaction:
    """反序列化为交易实例"""
    return pickle.loads(data)

def comfirm_tx(utxo_set: UTXOSet, transactions: List[str]):
    """确认交易"""
    for tx in transactions:
        tx = deserialize_transaction(bytes.fromhex(tx))
        utxo = UTXO(tx_id=tx.hash(), vout=deepcopy(tx.outputs))
        utxo_set.add_utxo(utxo=utxo)
        if not tx.is_coinbase():
            utxo_set.remove_utxo_by_vin(vin=tx.inputs)



