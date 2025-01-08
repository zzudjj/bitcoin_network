from ecdsa import SigningKey, SECP256k1
from transaction import create_transaction
from Cryptodome.Hash import SHA256, RIPEMD160
#节点1的一对私钥和公钥
sigkey1 = SigningKey.generate(curve=SECP256k1)
pubkey1 = sigkey1.get_verifying_key()
#节点2的一对私钥和公钥
sigkey2 = SigningKey.generate(curve=SECP256k1)
pubkey2 = sigkey2.get_verifying_key()
#节点2的比特币地址
pubk2_hash = SHA256.new(pubkey2.to_string().hex().encode('utf-8')).hexdigest()
pubk2_hash = RIPEMD160.new(pubk2_hash.encode('utf-8')).hexdigest()
#创建交易的输入参数
inputs=[sigkey1.to_string().hex()]
#创建交易的输出参数
outputs=[{'value': 5, 'pubk_hash': pubk2_hash}]
#创建一个交易
transaction = create_transaction(inputs=inputs, outputs=outputs)
#打印该交易的JSON格式
print(transaction.to_json())

s = "hello".encode()
print(s)