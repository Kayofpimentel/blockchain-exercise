import json
import hashlib as hl
import functools as ft
import copy as cp
from block import Block
from transaction import Transaction as Tx
from collections import OrderedDict as Od
from datetime import datetime as dt


# import pickle


class BlockchainModel:

    def __init__(self, owner=None):
        self.__chain = []
        self.__open_transactions = []
        self.__owner = owner

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
        return self.__chain

    @property
    def open_transactions(self):
        return self.__open_transactions

    @staticmethod
    def _hash_block(block=None):
        """Hashes a block and returns a string representation of it.

        :param block: The block to be hashed
        :return: Hashed string
        """

        if block is not None:
            dict_block = Od([('previous_hash', block.previous_hash),
                             ('index', block.index),
                             ('proof', block.proof),
                             ('transactions',
                              [Od([('sender', tx.sender),
                                   ('recipient', tx.recipient),
                                   ('amount', tx.amount),
                                   ('timestamp', dt.timestamp(tx.date))])
                               for tx in block.transactions]),
                             ('timestamp', block.timestamp)])
            the_block_hash = f'{dict_block}'
            return hl.sha3_256(json.dumps(the_block_hash).encode()).hexdigest()
        else:
            return None

    @staticmethod
    def _valid_proof(transactions, last_hash, proof):
        guess = [str(tx.amount) + str(tx.sender) + str(tx.recipient)
                 + str(dt.timestamp(tx.date)) for tx in transactions]
        guess = (str(last_hash) + str(proof)) + ft.reduce(lambda x, y: x + y, guess, '')
        guess = guess.encode()
        guess_hash = hl.sha3_256(guess).hexdigest()
        return guess_hash[0:2] == '00'

    def start_money(self):
        last_block = self.blockchain[-1]
        hashed_block = self._hash_block(last_block)
        start_transaction = Tx(tx_recipient=self.owner, tx_amount=100)
        self.__open_transactions.append(start_transaction)
        proof = self.proof_of_work(last_hash=hashed_block)
        start_block = Block(previous_hash=hashed_block, index=len(self.blockchain),
                            transactions=cp.deepcopy(self.open_transactions), proof=proof)
        self.__chain.append(start_block)
        self.__open_transactions.clear()

    def proof_of_work(self, transactions=None, last_hash=None):
        if last_hash is None:
            last_block = self.blockchain[-1]
            last_hash = self._hash_block(last_block)
        if transactions is None:
            transactions = cp.deepcopy(self.open_transactions)
        proof = 0
        while not self._valid_proof(transactions, last_hash, proof):
            proof += 1
        return proof

    def add_transaction(self, new_transaction):
        """
        Append a new value as well as the last blockchain value to the blockchain.

        Arguments:
            :param
        """
        if self.verify_transaction(new_transaction):
            self.__open_transactions.append(new_transaction)
            return True
        print('Not enough balance for this operation.')
        return False

    def verify_transaction(self, transaction):
        """
        Method to verify if the transaction is possible.

        :param transaction:
        :return: True for a possible transaction, False for the lack of funds
        """
        sender_balance = self.get_balance()
        return sender_balance >= transaction.amount

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
            reward_transaction = Tx(tx_recipient=self.owner, tx_amount=self.MINING_REWARD)
            # Create te new block with all open transactions
            temp_transaction = cp.deepcopy(self.open_transactions)[:]
            temp_transaction.append(reward_transaction)
            proof = self.proof_of_work(temp_transaction, hashed_block)
            block_to_mine = Block(previous_hash=hashed_block, index=len(self.blockchain), transactions=temp_transaction,
                                  proof=proof)
            # Append the new block to the blockchain and resets the open transactions
            self.blockchain.append(block_to_mine)
            self.open_transactions.clear()
            return self.save_data()
        else:
            print('There are no transactions to mine a block.')
            return False

    def output_blockchain(self):

        for index, block in enumerate(self.blockchain):
            print('-' * 20)
            print(f'Outputting block {index}:')
            print(block)
            if index == (len(self.blockchain) - 1):
                print('-' * 20)

    def verify_chain_is_safe(self):
        """
         Verify the current blockchain integrity and ret    urn True if it's valid or False if it's not.
        """
        for index, block in enumerate(self.blockchain):
            if index == 0:
                continue
            if not block.previous_hash == self._hash_block(self.blockchain[index - 1]):
                return False
            if not self._valid_proof(block.transactions, block.previous_hash, block.proof):
                print('Proof of work is invalid.')
                return False
        return True

    def get_balance(self):
        """
        Calculates the account balance of the owner

        :return: The total balance of the owner
        """

        # Calculating total amount that was sent to other participants.
        tx_sender = [tx.amount
                     for block in self.blockchain
                     for tx in block.transactions
                     if tx.sender == self.owner]
        open_tx_sender = [tx.amount for tx in self.open_transactions if tx.sender == self.owner]
        tx_sender += open_tx_sender
        amount_sent = ft.reduce(lambda tx_sum, tx_amt: tx_sum + tx_amt, tx_sender, 0)
        # Calculating total amount that was received from other participants.
        tx_recipient = [tx.amount
                        for block in self.blockchain
                        for tx in block.transactions
                        if tx.recipient == self.owner]
        amount_received = ft.reduce(lambda tx_sum, tx_amt: tx_sum + tx_amt, tx_recipient, 0)
        return amount_received - amount_sent

    def save_data(self, filename='./resources/blockchain_data.txt'):
        """
        Method to save the data from recent transactions and mined blocks after the program is closed.
        :param filename:
        :return if the operation was successful:
        """
        dict_blockchain = cp.deepcopy(self.blockchain)
        dict_blockchain = [Od([('previous_hash', block.previous_hash),
                               ('index', block.index),
                               ('proof', block.proof),
                               ('transactions',
                                [Od([('sender', tx.sender),
                                     ('recipient', tx.recipient),
                                     ('amount', tx.amount),
                                     ('timestamp', dt.timestamp(tx.date))])
                                 for tx in block.transactions]),
                               ('timestamp', block.timestamp)]) for block in dict_blockchain]
        dict_transactions = [tx.__dict__ for tx in self.open_transactions]
        try:
            with open(filename, mode='w') as blockchain_file:
                blockchain_file.write(json.dumps(dict_blockchain))
                blockchain_file.write('\n')
                blockchain_file.write(json.dumps(dict_transactions))

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
        try:
            with open(filename, mode='r') as blockchain_file:

                blockchain_info = blockchain_file.readlines()
                loaded_chain = json.loads(blockchain_info[0][:-1])
                self.__chain = [Block(previous_hash=loaded_block['previous_hash'],
                                      index=loaded_block['index'],
                                      proof=loaded_block['proof'],
                                      transactions=[Tx(tx_sender=tx['sender'],
                                                       tx_recipient=tx['recipient'],
                                                       tx_amount=tx['amount'],
                                                       tx_time=tx['timestamp'])
                                                    for tx in loaded_block['transactions'] if
                                                    loaded_block['transactions']],
                                      time_=loaded_block['timestamp']
                                      ) for loaded_block in loaded_chain]

                loaded_transactions = json.loads((blockchain_info[1]))
                self.__open_transactions = [Tx(tx_sender=open_tx['_Transaction__sender'],
                                               tx_recipient=open_tx['_Transaction__recipient'],
                                               tx_amount=open_tx['_Transaction__amount'],
                                               tx_time=open_tx['_Transaction__timestamp'])
                                            for open_tx in loaded_transactions]
            return True

        except (IOError, IndexError):
            self.blockchain.append(Block(previous_hash='', index=0, transactions=[], proof=0, time_=0))
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
