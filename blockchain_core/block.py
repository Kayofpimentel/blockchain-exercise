import time as tm
import datetime as dt


class Block:

    def __init__(self, previous_hash=None, index=None, transactions=None, proof=None, time_=None):
        self.previous_hash = previous_hash
        self.index = index
        self.transactions = transactions if transactions is not None else []
        self.proof = proof
        self.timestamp = time_ if time_ is not None else tm.time()

    def __repr__(self):
        return f'Block Info:\n' \
               f'Index: {self.index} \n' \
               f'Proof: {self.proof} \n' \
               f'Date: {dt.date.fromtimestamp(self.timestamp)} \n' \
               f'Transactions: {[tx.__dict__ for tx in self.transactions]} \n' \
               f'End of block.'
