from block_chain import create_block_chain
from memory_pool import MemmoryPool
from utxo import UTXOSet
from transaction import create_transaction
from wallet import load_wallet
from block import create_block

mem_pool = MemmoryPool()
utxo_set = UTXOSet()
wallet1 = load_wallet(dir='wallet1.conf')
block_chain = create_block_chain(to=wallet1.get_address(), coinbase_str="Hello Bitcoin!", utxo_set=utxo_set)
wallet2 = load_wallet(dir='wallet2.conf')
print(f"wallet1_balance: {wallet1.get_balance(utxo_set=utxo_set)}")
tx = create_transaction(send=wallet1, to=[wallet2.get_address()], value=[10], utxo_set=utxo_set)
print(tx.to_json())
mem_pool.add_tx(tx=tx)
block = create_block(block_height=1, pre_block_hash=block_chain.get_best_block_hash(), mem_pool=mem_pool, utxo_set=utxo_set, address=wallet2.get_address())
print(block.to_json())
block_chain.add_block(block=block, utxo_set=utxo_set)
print(block_chain.get_best_block_hash()==block.block_header.hash())
print(f"wallet1_balance: {wallet1.get_balance(utxo_set=utxo_set)}")
print(f"wallet2_balance: {wallet2.get_balance(utxo_set=utxo_set)}")
block = create_block(block_height=2, pre_block_hash=block_chain.get_best_block_hash(), mem_pool=mem_pool, utxo_set=utxo_set, address=wallet1.get_address())
block_chain.add_block(block=block, utxo_set=utxo_set)
print(f"wallet1_balance: {wallet1.get_balance(utxo_set=utxo_set)}")
tx_last = block_chain.find_tx(tx_id=tx.inputs[0].tx_id)
print(tx_last.to_json())
print(tx_last.hash())
for utxo in utxo_set.data:
    print(utxo.tx_id)
    for out in utxo.vout:
        if out:
            print(out.value)