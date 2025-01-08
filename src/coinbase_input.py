class CoinbaseInput:
    """coinbase输入类"""
    def __init__(self, coinbase: str):
        self.coinbase = coinbase

    def to_dict(self) -> dict:
        return {
            'coinbase': self.coinbase
        }