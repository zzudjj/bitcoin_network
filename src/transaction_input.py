class TransactionInput:
    '''比特币交易输入类'''
    def __init__(self, tx_id: str, index: int, script_sig: str):
        self.tx_id = tx_id  #指向包含被花费的UTXO的交易的散列值
        self.index = index  #被花费的UTXO的索引号
        self.script_sig = script_sig #解锁脚本
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "tx_id": self.tx_id,
            "index": self.index,
            "script_sig": self.script_sig
        }
