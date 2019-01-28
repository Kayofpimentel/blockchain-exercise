class BlockchainModel:

    def __init__(self, owner=None):
        self.open_transactions = []
        self._owner = owner
        self.genesis_block = {'previous_hash': '', 'index': 0, 'transactions': []}
        self.blockchain = [self.genesis_block]
        print(self.blockchain)

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def set_owner(self, value):
        self._owner = value

    def hash_block(self, block):
        return '-'.join([str(block[key]) for key in block])

    def get_last_blockchain_value(self):
        """Returns the last value of the current blockchain. """

        return self.blockchain[-1]

    def add_transaction(self, tx_recipient, tx_sender=owner, tx_amount=1.0):

        """Append a new value as well as the last blockchain value to the blockchain.
    
        Arguments:
            :param tx_sender: The sender of the coins
            :param tx_recipient: The recipient of the coins
            :param tx_amount: The amount of the coins sent with the transaction (default = 1.0)
    
        """

        transaction_info = {'sender': tx_sender, 'recipient': tx_recipient, 'amount': tx_amount}
        self.open_transactions.append(transaction_info)

    def mine_block(self):

        last_block = self.blockchain[-1]
        hashed_block = self.hash_block(last_block)
        block = {'previous_hash': hashed_block, 'index': len(self.blockchain), 'transactions': self.open_transactions}
        self.blockchain.append(block)
        self.open_transactions = []

    def new_transaction(self):
        tx_recipient = input('Enter the recipient of the transaction: \n')
        tx_amount = float(input("Please insert your transaction amount: \n"))
        return tx_recipient, tx_amount

    def output_blockchain(self):

        for block in self.blockchain:
            print('Outputting block')
            print(block)

    def verify_chain_is_safe(self, the_chain, counter=0, is_safe=True):
        """ Verify the current blockchain integrity and return True if it's valid or False if it's not. """
        for index, block in enumerate(self.blockchain):
            if index == 0:
                continue
            if not block['previous_hash'] == self.hash_block(self.blockchain[index-1]):
                return False
        return True

