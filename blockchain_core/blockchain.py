import json
from blockchain_util import chain_utils as cu
import copy as cp
from blockchain_core.block import Block
from blockchain_core.transaction import Transaction as Tx
from collections import OrderedDict as Od
from datetime import datetime as dt


# import pickle

class Blockchain:

    def __init__(self, user=None, hosting_node=None):
        self.__chain = []
        self.__open_transactions = []
        self.__node = hosting_node
        self.__owner = user if user is not None else ''

        if self.load_data():
            print('Blockchain loaded.')
        else:
            print('Could not load the Blockchain, ending the program')
            quit()

        self.MINING_REWARD = 10

    @property
    def node(self):
        return self.__node

    @property
    def owner(self):
        return self.__owner

    @owner.setter
    def owner(self, new_user=None):
        if new_user is not None:
            self.__owner = new_user

    @owner.setter
    def owner(self, value):
        self.__owner = value

    @property
    def chain(self):
        return self.__chain[:]

    @property
    def open_transactions(self):
        return self.__open_transactions[:]

    def start_money(self):
        last_block = self.chain[-1]
        hashed_block = cu.hash_block(last_block)
        tx_start_amount = 100
        start_signature = self.node.wallet.sign_transaction(amount=tx_start_amount, sender=self.owner)
        start_transaction = Tx(tx_recipient=self.owner, tx_amount=100)
        self.__open_transactions.append(start_transaction)
        proof = cu.calculate_proof(transactions=self.open_transactions, last_hash=hashed_block)
        start_block = Block(previous_hash=hashed_block, index=len(self.chain),
                            transactions=cp.deepcopy(self.open_transactions), proof=proof)
        self.__chain.append(start_block)
        self.__open_transactions.clear()

    def add_transaction(self, new_transaction):
        """
        Append a new value as well as the last chain value to the chain.

        Arguments:
            :param
        """
        if cu.verify_transaction(transaction=new_transaction, blockchain=self):
            self.__open_transactions.append(new_transaction)
            return True
        print('Not enough balance for this operation.')
        return False

    def mine_block(self):
        """
        Method add a new block to the chain.
        :return:
        """
        if len(self.open_transactions) > 0:
            # Fetch the last block for hashing before mining the new block
            last_block = self.chain[-1]
            # Hash the last block
            hashed_block = cu.hash_block(last_block)
            # Add the reward transaction for the mining operation
            reward_transaction = Tx(tx_recipient=self.owner, tx_amount=self.MINING_REWARD)
            # Create te new block with all open transactions
            temp_transaction = cp.deepcopy(self.open_transactions)
            temp_transaction.append(reward_transaction)
            proof = cu.calculate_proof(temp_transaction, hashed_block)
            block_to_mine = Block(previous_hash=hashed_block, index=len(self.chain), transactions=temp_transaction,
                                  proof=proof)
            # Append the new block to the chain and resets the open transactions
            self.__chain.append(block_to_mine)
            self.__open_transactions.clear()
            return self.save_data()
        else:
            print('There are no transactions to mine a block.')
            return False

    def output_blockchain(self):

        for index, block in enumerate(self.chain):
            print('-' * 20)
            print(f'Outputting block {index}:')
            print(block)
            if index == (len(self.chain) - 1):
                print('-' * 20)

    def save_data(self, filename='../resources/blockchain_data.txt'):
        """
        Method to save the data from recent transactions and mined blocks after the program is closed.
        :param filename:
        :return if the operation was successful:
        """
        dict_blockchain = cp.deepcopy(self.chain)
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

                # data_to_save = {'chain': self.chain, 'ot': self.open_transactions}
                # with open(filename, mode='wb') as blockchain_file:
                #     blockchain_file.write(pickle.dumps(data_to_save))
            return True

        except IOError:
            return False

    def load_data(self, file_name='../resources/blockchain_data.txt'):
        """
        Method to load all the data from the chain when the program initiates.
        :param file_name:
        :return if the operation was successful:
        """
        try:
            with open(file_name, mode='r') as blockchain_file:

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
            self.__chain.append(Block(previous_hash='', index=0, transactions=[], proof=0, time_=0))
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
