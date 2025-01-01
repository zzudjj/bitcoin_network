from ecdsa import SigningKey, SECP256k1, VerifyingKey
import hashlib

sk = SigningKey.generate(curve=SECP256k1)

pk = sk.get_verifying_key()

message = b"Hello, Bitcoin!"

message_hash = hashlib.sha256(message).digest()

signature = sk.sign(message_hash)

pk1 = VerifyingKey.from_string(pk.to_string(), curve=SECP256k1)

is_valid = pk1.verify(signature, message_hash)

print(is_valid)