class TransactionOutput:
    '''比特币交易输出类'''
    def __init__(self, value: float, script_pubkey: str):
        self.value = value #输出的比特币额
        self.script_pubkey = script_pubkey #锁定脚本

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "value": self.value,
            "script_pubkey": self.script_pubkey
        }