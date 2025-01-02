from collections import deque
from Cryptodome.Hash import SHA256, RIPEMD160
from ecdsa import SigningKey, SECP256k1, VerifyingKey

def get_script_sig(sig: str, pubkey: str) -> str:
    '''返回P2PKH模式下的解锁脚本'''
    script_sig = sig + " " + pubkey
    return script_sig

def get_script_pubkey(pubk_hash: str) -> str:
    '''返回P2PKH模式下的锁定脚本'''
    script_pubkey = 'OP_DUP OP_HASH160 ' + pubk_hash + ' OP_EQUALVERIFY OP_CHECKSIG'
    return script_pubkey

def execute_script(script_sig, script_pubkey):
    '''执行脚本'''
    script = script_sig + script_pubkey
    stack = deque()
    for cmd in script:
        match cmd:
            case 'OP_DUP':
                if len(stack) > 0 :
                    top = stack[-1]
                    stack.append(top)
                else:
                    return False
            case 'OP_HASH160':
                if len(stack) > 0:
                    top = str(stack.pop())
                    top_sha256 = SHA256.new(top.encode('utf-8')).hexdigest()
                    top_hash = RIPEMD160.new(top_sha256.encode('utf-8')).hexdigest()
                    stack.append(top_hash)
                else:
                    return False
            case 'OP_EQUALVERIFY':
                if len(stack) > 1:
                    pubkey_hash1 = str(stack.pop())
                    pubkey_hash2 = str(stack.pop())
                    if pubkey_hash1 != pubkey_hash2:
                        return False
                else: 
                    return False
            case 'OP_CHECKSIG':
                if len(stack) > 1:
                    pk = VerifyingKey(stack.pop())
                    sig = stack.pop()
                    if pubkey_hash1 != pubkey_hash2:
                        return False
                else: 
                    return False
            case _ :
                pass 
            