class CoinbaseInput:
    """coinbase输入类"""
    def __init__(self, block_height: int, coinbase_str: str):
         # 将区块高度转换为小端序的十六进制
        block_height_hex = block_height.to_bytes((block_height.bit_length() + 7) // 8, byteorder='little').hex()
        # 添加区块高度的长度前缀
        block_height_len = len(block_height_hex) // 2  # 每个字节占2个十六进制字符
        block_height_hex_len = bytes([block_height_len]).hex()
        # 将 coinbase_str 转换为十六进制
        coinbase_str_hex = coinbase_str.encode().hex()
        # 添加矿工自定义数据的长度前缀
        coinbase_str_len = bytes([len(coinbase_str_hex) // 2]).hex()  # 每个字节占2个十六进制字符
        # 组合 Coinbase 域
        self.coinbase = block_height_hex_len + block_height_hex + coinbase_str_len + coinbase_str_hex

    def to_dict(self) -> dict:
        return {
            'coinbase': self.coinbase
        }
    
    def get_block_height(self):
        """从 Coinbase 域中提取区块高度"""
        # 提取区块高度的长度前缀
        block_height_len = int(self.coinbase[:2], 16)  # 前2个字符是长度前缀
        # 提取区块高度的十六进制数据
        block_height_hex = self.coinbase[2:2 + block_height_len * 2]
        # 将十六进制数据转换为整数（小端序）
        block_height = int.from_bytes(bytes.fromhex(block_height_hex), byteorder='little')
        return block_height
    