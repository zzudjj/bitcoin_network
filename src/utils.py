import base58

def get_pubkhash_from_address(address: str) -> str:
    """根据比特币地址获取公钥哈希"""
    address = base58.b58decode(address)
    pubkhash = address[1:len(address)-4]
    return pubkhash.hex()
