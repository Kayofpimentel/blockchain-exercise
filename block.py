from time import time


class Block:

    def __init__(self, previous_hash=None, index=None, transactions=[], proof=None, time_=None):

        self.previous_hash = previous_hash
        self.index = index
        self.transactions = transactions
        self.proof = proof
        self.timestamp = time() if time_ is None else time_
