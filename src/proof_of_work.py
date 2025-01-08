from block_header import BlockHeader

def pow(header: BlockHeader) -> tuple:
    target_bits = header.target_bits
    target = 2 ** (256 - target_bits)
    nonce = 0
    hash_result = ''
    while True:
        header.nonce = nonce
        hash_result = header.hash()
        actual = int(hash_result, 16)
        print(f'\rblock_hash:{hash_result}', end="")
        if actual < target:
           break
        nonce += 1
    print("")
    return (hash_result, nonce)

def verify_pow(header: BlockHeader) -> bool:
    target_bits = header.target_bits
    target = 2 ** (256 - target_bits)
    hash_result = header.hash()
    actual = int(hash_result, 16)
    if actual < target:
        return True
    else:
        return False
