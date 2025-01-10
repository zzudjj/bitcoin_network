from typing import List
from utils import get_pubkhash_from_address
from transaction_output import TransactionOutput
from transaction_input import TransactionInput
import pickle
import pickledb

class UTXO:
    """未花费输出"""
    def __init__(self, tx_id: str, vout: List[TransactionOutput]):
        self.tx_id = tx_id
        self.vout = vout
    
    def serialize(self) -> bytes:
        return pickle.dumps(self)
    
    @staticmethod
    def derserialize(data: bytes) -> 'UTXO':
        return pickle.loads(data)

class UTXOSet:
    """UTXO集合"""
    def __init__(self):
        self.db: pickledb.PickleDB = None

    def add_utxo(self, utxo: UTXO):
        """向UTXO集合中添加一个UTXO"""
        self.db.set(utxo.tx_id, utxo.serialize().hex())

    def find_utxo_by_address(self, address: str, value: float) -> tuple:
        """找到指定地址的足够的utxo"""
        pubk_hash = get_pubkhash_from_address(address=address)
        utxos = []
        utxo_value_sum = 0
        tx_id_list = self.db.getall()
        for tx_id in tx_id_list:
            utxo = UTXO.derserialize(bytes.fromhex(self.db.get(tx_id)))
            for index, out in enumerate(utxo.vout):
                if out == None:
                    continue
                l = out.script_pubkey.split(' ')
                if pubk_hash == l[2]:
                    utxo_value_sum += out.value
                    utxos.append((utxo.tx_id, index))
            if utxo_value_sum > value:
                break
        return (utxo_value_sum, utxos)
    
    def remove_utxo_by_vin(self, vin: List[TransactionInput]):
        """从UTXO集合中移除utxo"""
        tx_id_list = self.db.getall()
        del_index = []
        for tx_in in vin:
            tx_id = tx_in.tx_id
            index = tx_in.index
            for tx_id_u in tx_id_list:  # 在复制的列表上进行迭代
                if tx_id_u == tx_id:
                    utxo = UTXO.derserialize(bytes.fromhex(self.db.get(tx_id)))
                    utxo.vout[index] = None
                    self.db.set(tx_id, utxo.serialize().hex())
                    if all([x == None for x in utxo.vout]):
                        del_index.append(tx_id)
        for tx_id in del_index:
            self.db.rem(tx_id)
    
    def find_utxo_by_vin(self, vin: List[TransactionInput]) -> List[TransactionOutput]:
        """根据tx_in从UTXO集合中获取utxo"""
        utxos = []
        tx_id_list = self.db.getall()
        for tx_in in vin:
            tx_id = tx_in.tx_id
            index = tx_in.index
            for tx_id_u in tx_id_list:
                if tx_id_u == tx_id:
                    utxo = UTXO.derserialize(bytes.fromhex(self.db.get(tx_id)))
                    utxos.append(utxo.vout[index])
                    break
        return utxos
    
    def get_balance_by_address(self, address: str) -> float:
        """根据比特币地址从UTXO中找到余额"""
        pubk_hash = get_pubkhash_from_address(address=address)
        utxo_value_sum = 0
        tx_id_list = self.db.getall()
        for tx_id in tx_id_list:
            utxo = UTXO.derserialize(bytes.fromhex(self.db.get(tx_id)))
            for out in utxo.vout:
                if out == None:
                    continue
                l = out.script_pubkey.split(' ')
                if pubk_hash == l[2]:
                    utxo_value_sum += out.value
        return utxo_value_sum

def load_utxo_set(dir: str) -> UTXOSet:
    utxo_set = UTXOSet()
    utxo_set.db = pickledb.load(dir, True)
    return utxo_set
