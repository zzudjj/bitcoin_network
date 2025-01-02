from hashlib import sha256
import json
from typing import Dict, List, Union
from ecdsa import SigningKey, SECP256k1
from bitcoin_script import get_script_pubkey, get_script_sig

class TransactionInput:
    '''比特币交易输入类'''
    def __init__(self, tx_id: str, index: int, script_sig: str):
        self.tx_id = tx_id  #指向包含被花费的UTXO的交易的散列值
        self.index = index  #被花费的UTXO的索引号
        self.script_sig = script_sig #解锁脚本
    
    def to_dict(self, for_signing=False):
        """转换为字典格式，支持忽略解锁脚本"""
        return {
            "tx_id": self.tx_id,
            "index": self.index,
            "script_sig": None if for_signing else self.script_sig
        }


class TransactionOutput:
    '''比特币交易输出类'''
    def __init__(self, value: int, script_pubkey: str):
        self.value = value #输出的比特币额
        self.script_pubkey = script_pubkey #锁定脚本

    def to_dict(self):
        """转换为字典格式"""
        return {
            "value": self.value,
            "script_pubkey": self.script_pubkey
        }

class Transaction:
    '''比特币交易类'''
    def __init__(self, version: float, vin_sz: int, vout_sz: int, lock_time: int, inputs: List[TransactionInput], outputs: List[TransactionOutput]):
        self.version = version  #版本
        self.vin_sz = vin_sz    #交易输入列表中交易数量
        self.vout_sz = vout_sz  #交易输出列表中交易数量
        self.lock_time = lock_time  #交易锁定时间
        self.inputs = inputs  #输入列表
        self.outputs = outputs  #输出列表   

    def to_dict(self, for_signing=False):
        """转换为字典格式"""
        return {
            "version": self.version,
            "vin_sz": self.vin_sz,
            "vout_sz": self.vout_sz,
            "lock_time": self.lock_time,
            "inputs": [tx_input.to_dict(for_signing=for_signing) for tx_input in self.inputs],
            "outputs": [tx_output.to_dict() for tx_output in self.outputs]
        }

    def to_json(self, for_signing=False):
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict(for_signing=for_signing), indent=4)
    
    def calculate_hash_from_json(self, for_signing=False):
        """计算 JSON 格式的交易哈希"""
        tx_json = self.to_json(for_signing=for_signing)
        return sha256(tx_json.encode()).hexdigest()

def sign_transaction(transaction: Transaction, private_key: str, input_index: int):
        """利用私钥对交易进行签名"""
        # 计算交易哈希（忽略解锁脚本）
        tx_hash = transaction.calculate_hash_from_json(for_signing=True)

        # 使用私钥生成签名
        sk = SigningKey.from_string(bytes.fromhex(private_key), curve=SECP256k1)
        signature = sk.sign(tx_hash.encode()).hex()

        # 将签名和公钥存入解锁脚本
        public_key = sk.verifying_key.to_string().hex()
        transaction.inputs[input_index].script_sig = get_script_sig(sig=signature, pubkey=public_key)

def create_transaction(version=1.0, lock_time=0, inputs:List[str] = None, outputs:List[Dict[str, Union[int, str]]] = None) -> Transaction:
    if inputs is None or outputs is None or not inputs or not outputs:
        raise ValueError("交易输入和交易输出不能为空")
    tx_inputs = []
    tx_outputs = []
    #由于当前我们还未建立UTXO结构，因此这里的交易输入类型的参数是随意值
    for i in range(0, len(inputs)):
        tx_input = TransactionInput(tx_id=str(i), index=i, script_sig=None)
        tx_inputs.append(tx_input)
        
    #根据outputs创建交易输入列表tx_outputs
    for output_dict in outputs:
        script_pubkey = get_script_pubkey(pubk_hash=output_dict['pubk_hash'])
        tx_output = TransactionOutput(value=output_dict['value'], script_pubkey=script_pubkey)
        tx_outputs.append(tx_output)

    transaction = Transaction(version=version,
                              vin_sz=len(tx_inputs),
                              vout_sz=len(tx_outputs),
                              inputs=tx_inputs,
                              outputs=tx_outputs,
                              lock_time=lock_time
                              )
    
    #利用输入的私钥对交易进行签名
    for i in range(0, len(inputs)):
        sign_transaction(transaction=transaction, private_key=inputs[i], input_index=i)
    return transaction

def validate_transaction():
    '''验证交易'''
    pass



        
        