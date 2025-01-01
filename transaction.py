class Transaction:
    '''比特币交易类'''
    def __init__(self, verison, vin_sz, vout_sz, lock_time, inputs, outputs):
        self.version = verison  #版本
        self.vin_sz = vin_sz    #交易输入列表中交易数量
        self.vout_sz = vout_sz  #交易输出列表中交易数量
        self.lock_time = lock_time  #交易锁定时间
        self.inputs = inputs  #输入列表
        self.outputs = outputs  #输出列表


class TransactionInput:
    '''比特币交易输入类'''
    def __init__(self, tx_id, index, script_sig):
        self.tx_id = tx_id  #指向包含被花费的UTXO的交易的散列值
        self.index = index  #被花费的UTXO的索引号
        self.script = script_sig #解锁脚本


class TransactionOutput:
    '''比特币交易输出类'''
    def __init__(self, value, script_pubkey):
        self.value = value #输出的比特币额
        self.script_pubkey = script_pubkey #锁定脚本


def create_transaction(verion = 1.0, lock_time = 0, inputs = [], outputs = []):
    '''创建交易'''
    if not inputs or not outputs:
        ValueError("交易输入和交易输出不能为空");
    transaction = Transaction(
        verison = verion, 
        lock_time = lock_time,
        vin_sz = len(inputs),
        vout_sz = len(outputs),
        inputs = inputs,
        outputs = outputs
        )
    return transaction


def validate_transaction():
    '''验证交易'''
    pass



        
        