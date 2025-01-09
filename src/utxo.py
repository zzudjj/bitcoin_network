from typing import List
from utils import get_pubkhash_from_address
from transaction_output import TransactionOutput
from transaction_input import TransactionInput

class UTXO:
    """未花费输出"""
    def __init__(self, tx_id: str, vout: List[TransactionOutput]):
        self.tx_id = tx_id
        self.vout = vout

class UTXOSet:
    """UTXO集合"""
    def __init__(self):
        self.data: List[UTXO] = []

    def add_utxo(self, utxo: UTXO):
        """向UTXO集合中添加一个UTXO"""
        self.data.append(utxo)

    def find_utxo_by_address(self, address: str, value: float) -> tuple:
        """找到指定地址的足够的utxo"""
        pubk_hash = get_pubkhash_from_address(address=address)
        utxos = []
        utxo_value_sum = 0
        for utxo in self.data:
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
        del_index = []
        for tx_in in vin:
            tx_id = tx_in.tx_id
            index = tx_in.index
            for i in range(0, len(self.data)):
                if self.data[i].tx_id == tx_id:
                    self.data[i].vout[index] = None
                    if all([x == None for x in self.data[i].vout]):
                        del_index.append(i)
        self.data = [self.data[i] for i in range(0, len(self.data)) if i not in del_index]
    
    def find_utxo_by_vin(self, vin: List[TransactionInput]) -> List[TransactionOutput]:
        """根据tx_in从UTXO集合中获取utxo"""
        utxos = []
        for tx_in in vin:
            tx_id = tx_in.tx_id
            index = tx_in.index
            for i in range(0, len(self.data)):
                if self.data[i].tx_id == tx_id:
                   utxos.append(self.data[i].vout[index])
                   break
        return utxos
    
    def get_balance_by_address(self, address: str) -> float:
        """根据比特币地址从UTXO中找到余额"""
        pubk_hash = get_pubkhash_from_address(address=address)
        utxo_value_sum = 0
        for utxo in self.data:
            for out in utxo.vout:
                if out == None:
                    continue
                l = out.script_pubkey.split(' ')
                if pubk_hash == l[2]:
                    utxo_value_sum += out.value
        return utxo_value_sum


