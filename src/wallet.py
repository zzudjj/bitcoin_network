from ecdsa import SigningKey, SECP256k1, VerifyingKey
from Cryptodome.Hash import SHA256, RIPEMD160
import base58

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

def get_pubkhash_from_address(address: str) -> str:
    """根据比特币地址获取公钥哈希"""
    address = base58.b58decode(address)
    pubkhash = address[1:len(address)-4]
    return pubkhash.hex()

    
    