from ecdsa import SigningKey, SECP256k1, VerifyingKey
from Cryptodome.Hash import SHA256, RIPEMD160
from utxo import UTXOSet
import base58
from utils import get_pubkhash_from_address
import os  # 添加导入os模块

VERSION = bytes.fromhex('00') #主网普通前缀

class Wallet:
    """钱包类"""
    def __init__(self, sigkey: SigningKey, pubkey: VerifyingKey):
        self.sigkey = sigkey
        self.pubkey = pubkey

    def get_address(self) -> str:
        """比特币地址"""
        pubk_hash = self.get_pubk_hash()
        prefixed_hash = VERSION + bytes.fromhex(pubk_hash)
        checksum = SHA256.new(SHA256.new(prefixed_hash).digest()).digest()[:4]
        address = prefixed_hash + checksum
        address = base58.b58encode(address).decode()
        return address

    def get_pubk_hash(self) -> str:
        """公钥哈希"""
        pubk_hex = self.pubkey.to_string().hex()
        pubk_hash = SHA256.new(bytes.fromhex(pubk_hex)).hexdigest()
        pubk_hash = RIPEMD160.new(bytes.fromhex(pubk_hash)).hexdigest()
        return pubk_hash
    
    def get_balance(self, utxo_set: UTXOSet) -> float:
        """获取当前比特币地址的余额"""
        address = self.get_address()
        return utxo_set.get_balance_by_address(address=address)

    
def validate_address(address: str) -> bool:
    """验证地址"""
    address = base58.b58decode(address)
    actual_checksum = address[len(address)-4:]
    prefixed_hash = address[:len(address)-4]
    target_checksum = SHA256.new(SHA256.new(prefixed_hash).digest()).digest()
    if actual_checksum == target_checksum:
        return True
    else:
        return False
    
def load_wallet(dir: str) -> Wallet:
    """加载钱包"""
    wallet_list = []
    if not os.path.exists(dir):  # 检查文件是否存在
        with open(dir, 'w') as fp:  # 如果文件不存在则创建一个新的文件
            pass
    with open(dir, "r") as fp:
        for line in fp:
            wallet_list = line.split(' ')
    if len(wallet_list) == 0:
        sigkey, pubkey = new_key_pair()
        wallet = Wallet(sigkey=sigkey, pubkey=pubkey)
        sk_str = wallet.sigkey.to_string().hex()
        pk_str = wallet.pubkey.to_string().hex()
        with open(dir, 'w') as fp:
            fp.write(f"{sk_str} {pk_str}")
        return wallet
    else:
        sigkey = SigningKey.from_string(bytes.fromhex(wallet_list[0]), curve=SECP256k1)
        pubkey = VerifyingKey.from_string(bytes.fromhex(wallet_list[1]), curve=SECP256k1)
        wallet = Wallet(sigkey=sigkey, pubkey=pubkey)
        return wallet

def new_key_pair() -> tuple:
    """生成一对公私钥对"""
    sigkey = SigningKey.generate(curve=SECP256k1)
    pubkey = sigkey.get_verifying_key()
    return (sigkey, pubkey)


