import hashlib as hl
import functools as ft
from collections import OrderedDict as Od
import json
# import pickle


class BlockchainModel:

    def __init__(self, owner=None):
        self.__blockchain = []
        self.__open_transactions = []
        self.owner = owner
        self.participants = {owner}

        if self.load_data():
            print('Blockchain loaded.')
        else:
            print('Could not load the Blockchain, ending the program')
            quit()

        self.MINING_REWARD = 10

    @property
    def owner(self):
        return self.__owner

    @owner.setter
    def owner(self, value):
        self.__owner = value

    @property
    def blockchain(self):
        return self.__blockchain

    @property
    def open_transactions(self):
        return self.__open_transactions

    @staticmethod
    def new_transaction():
        tx_recipient = input('Enter the recipient of the transaction: \n')
        tx_amount = float(input("Please insert your transaction amount: \n"))
        return tx_recipient, tx_amount

    @staticmethod
    def _hash_block(block):
        """Hashes a block and returns a string representation of it.

        :param block: The block to be hashed
        :return: Hashed string
        """
        hashed_block = (str(block['transactions']) +
                        str(block['previous_hash']) +
                        str(block['proof'])).encode()

        hashed_block = hl.sha3_256(hashed_block).hexdigest()

        return hashed_block

    @staticmethod
    def _valid_proof(transactions, last_hash, proof):
        guess = (str(transactions) + str(last_hash) + str(proof)).encode()
        guess_hash = hl.sha3_256(guess).hexdigest()
        return guess_hash[0:2] == '00'

    def start_money(self):
        last_block = self.blockchain[-1]
        hashed_block = self._hash_block(last_block)
        start_transaction = Od([('sender', 'MINING'), ('recipient', self.owner), ('amount', 100)])
        self.__open_transactions.append(start_transaction)
        start_transaction = Od([('sender', 'MINING'), ('recipient', self.owner), ('amount', 0)])
        self.__open_transactions.append(start_transaction)
        proof = self.proof_of_work(last_hash=hashed_block)
        block = {'previous_hash': hashed_block, 'index': len(self.__blockchain),
                 'transactions': self.__open_transactions, 'proof': proof}
        self.__blockchain.append(block)
        self.__open_transactions = []

    def proof_of_work(self, transactions=None, last_hash=None):
        if not last_hash:
            last_block = self.blockchain[-1]
            last_hash = self._hash_block(last_block)
        if not transactions:
            transactions = self.open_transactions
        proof = 0
        while not self._valid_proof(transactions, last_hash, proof):
            proof += 1
        return proof

    def add_transaction(self, tx_recipient, tx_sender=None, tx_amount=100):

        """
        Append a new value as well as the last blockchain value to the blockchain.

        Arguments:
            :param tx_sender: The sender of the coins
            :param tx_recipient: The recipient of the coins
            :param tx_amount: The amount of the coins sent with the transaction (default = 1.0)
        """

        if not tx_sender:
            tx_sender = self.owner
        # _new_transaction = {'sender': tx_sender, 'recipient': tx_recipient, 'amount': tx_amount}
        new_transaction = Od([('sender', tx_sender), ('recipient', tx_recipient), ('amount', tx_amount)])
        if self.verify_transaction(new_transaction):
            self.__open_transactions.append(new_transaction)
            self.participants.add(tx_sender)
            self.participants.add(tx_recipient)
            return True
        print('Not enough balance for this operation.')
        return False

    def verify_transaction(self, transaction):
        sender_balance = self.get_balance(transaction['sender'])
        return sender_balance >= transaction['amount']

    def mine_block(self):
        """
        Method add a new block to the blockchain.
        :return:
        """
        if len(self.open_transactions) > 0:
            # Fetch the last block for hashing before mining the new block
            last_block = self.blockchain[-1]
            # Hash the last block
            hashed_block = self._hash_block(last_block)
            # Add the reward transaction for the mining operation
            reward_transaction = Od([('sender', 'MINING'), ('recipient', self.owner), ('amount', self.MINING_REWARD)])
            # Create te new block with all open transactions
            temp_transaction = self.open_transactions[:]
            temp_transaction.append(reward_transaction)
            proof = self.proof_of_work(temp_transaction, hashed_block)
            block = {'previous_hash': hashed_block, 'index': len(self.__blockchain),
                     'transactions': temp_transaction, 'proof': proof}
            # Append the new block to the blockchain and resets the open transactions
            self.__blockchain.append(block)
            self.__open_transactions = []
            return True
        else:
            print('There is no blocks to mine.')
            return False

    def output_blockchain(self):

        for block in self.__blockchain:
            print('Outputting block')
            print(block)

    def verify_chain_is_safe(self):
        """
         Verify the current blockchain integrity and return True if it's valid or False if it's not.
        """
        for index, block in enumerate(self.blockchain):
            if index == 0:
                continue
            if not block['previous_hash'] == self._hash_block(self.blockchain[index - 1]):
                return False
            if not self._valid_proof(block['transactions'], block['previous_hash'], block['proof']):
                print('Proof of work is invalid.')
                return False
        return True

    # noinspection PyTypeChecker
    def get_balance(self, participant=None):
        if not participant:
            participant = self.owner
        tx_sender = [[tx['amount'] for tx in block['transactions'] if tx['sender'] == participant] for block
                     in self.blockchain]
        open_tx_sender = [tx['amount'] for tx in self.open_transactions if tx['sender'] == participant]
        tx_sender.append(open_tx_sender)
        amount_sent = ft.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum,
                                tx_sender, 0)
        tx_recipient = [[tx['amount'] for tx in block['transactions'] if tx['recipient'] == participant] for block
                        in self.blockchain]
        amount_received = ft.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum,
                                    tx_recipient, 0)
        return amount_received - amount_sent

    def save_data(self, filename='./resources/blockchain_data.txt'):
        """
        Method to save the data from recent transactions and mined blocks after the program is closed.
        :param filename:
        :return if the operation was successful:
        """

        try:
            with open(filename, mode='w') as blockchain_file:
                blockchain_file.write(json.dumps(self.blockchain))
                blockchain_file.write('\n')
                blockchain_file.write(json.dumps(self.open_transactions))

                # data_to_save = {'chain': self.blockchain, 'ot': self.open_transactions}
                # with open(filename, mode='wb') as blockchain_file:
                #     blockchain_file.write(pickle.dumps(data_to_save))
            return True

        except IOError:
            return False

    def load_data(self, filename='./resources/blockchain_data.txt'):
        """
        Method to load all the data from the blockchain when the program initiates.
        :param filename:
        :return if the operation was successful:
        """
        blockchain_info = ''

        try:
            with open(filename, mode='r') as blockchain_file:

                blockchain_info = blockchain_file.readlines()
                loaded_chain = json.loads(blockchain_info[0][:-1])
                self.__blockchain = [{'previous_hash': block['previous_hash'],
                                      'index': block['index'],
                                      'proof': block['proof'],
                                      'transactions': [Od(
                                          [('sender', tx['sender']),
                                           ('recipient', tx['recipient']),
                                           ('amount', tx['amount'])])
                                          for tx in block['transactions'] if block['transactions']]
                                      } for block in loaded_chain]

                loaded_transactions = json.loads((blockchain_info[1]))
                self.__open_transactions = [Od(
                    [('sender', open_tx['sender']),
                     ('recipient', open_tx['recipient']),
                     ('amount', open_tx['amount'])])
                    for open_tx in loaded_transactions]

            return True

        except (IOError, IndexError):
            genesis_block = {'previous_hash': '', 'index': 0, 'transactions': [], 'proof': 0}
            self.__blockchain = [genesis_block]
            self.start_money()
            print('File not found, creating new one.')
            return True if self.save_data() else False

        # with open(filename, mode='ab+') as blockchain_file:
        #     blockchain_file.seek(0)
        #     if not blockchain_file.read(1):
        #         return False
        #     else:
        #         blockchain_file.seek(0)
        #         blockchain_info = pickle.loads(blockchain_file.read())
        #
        # self.__blockchain = blockchain_info['chain']
        # self.__open_transactions = blockchain_info['ot']

    def end_session(self):
        return self.save_data()
