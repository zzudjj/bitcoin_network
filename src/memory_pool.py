from queue import Queue
from transaction import Transaction

class MemmoryPool:
    """交易池"""
    def __init__(self):
        self.data = Queue()

    def add_tx(self, tx: Transaction):
        self.data.put(tx.serialize().hex())
    
    def get_tx(self) -> str:
        if self.data.empty():
            return None
        else:
            return self.data.get()