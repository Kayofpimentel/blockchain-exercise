import json
import binascii
import copy as cp
import hashlib as hl
import functools as ft
from collections import OrderedDict as Od

from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import PKCS1_v1_5 as CSign

from blockchain_model.block import Block
from blockchain_model.transaction import Transaction as Tx


class Blockchain:
    __DEFAULT_SENDER = 'SYSTEM'
    __DEFAULT_SIGNATURE = 'MINING'
    __HASH_VALIDATION = '00'
    __DEFAULT_PRIZE = 10

    def __init__(self, chain_info=None, op_info=None):
        # TODO Improve first block check and creation
        # TODO Remove real user from first transaction
        # TODO Account for the total number of users registered on the chain_blocks
        # TODO Implement new user reward
        # TODO Implement decrease of reward with registered number of users
        # TODO Secure chain operations just inside Blockchain Class, returning just copies.
        self.__chain = []
        self.__open_transactions = []
        if chain_info is not None:
            self.__chain, self.__open_transactions = self.info_to_chain(blocks=chain_info, txs=op_info)

    @property
    def chain_info(self):
        chain_info, _ = self.chain_to_info(blocks=self.__chain)
        return chain_info

    @property
    def op_txs_info(self):
        _, txs_info = self.chain_to_info(txs=self.__open_transactions)
        return txs_info

    @property
    def reward(self):
        return self.__DEFAULT_PRIZE

    def add_tx(self, new_transaction_info):
        """
        Append a new value as well as the last chain value to the chain.
        Arguments:
        :param new_transaction_info
        """
        new_transaction = self.create_new_transaction(*new_transaction_info)
        self.__open_transactions.append(new_transaction)
        return True

    def add_block(self, new_block_info):
        """
        TODO
        :param new_block_info:
        :return:
        """
        try:
            block_to_add, _ = self.info_to_chain(blocks=new_block_info, txs=None)
            block_to_add = block_to_add[0]
            hashes_match = self.hash_block(self.__chain[-1]) == block_to_add.previous_hash
            is_valid = self.valid_proof(block_to_add.transactions, block_to_add.previous_hash, block_to_add.proof)
            if not (is_valid or hashes_match):
                return None
            else:
                self.__chain.append(block_to_add)
                self.__open_transactions.clear()
                return block_to_add
        except IndexError:
            print(f'The blockchain has no blocks to compare.')
            self.start_new_chain(None)
            return None

    def mine_block(self, miner_key):
        """
        Method to add a new block to the chain.
        :return:
        """
        last_block = self.__chain[-1]
        hashed_block = self.hash_block(last_block)
        temp_transactions = cp.deepcopy(self.__open_transactions)
        # Checking if all the transactions are verified with the right signature.
        block_status = True
        for count, tx in enumerate(temp_transactions):
            if not self.verify_transaction(tx):
                # Removing non verified transactions.
                del self.__open_transactions[count]
                block_status = False
        if not block_status:
            return False
        # Add the reward transaction for the mining operation
        reward_transaction = self.create_new_transaction(tx_recipient=miner_key, tx_amount=self.reward)
        temp_transactions.append(reward_transaction)
        proof = self.calculate_proof(temp_transactions, hashed_block)
        block_to_mine = Block(previous_hash=hashed_block, index=len(self.__chain), transactions=temp_transactions,
                              proof=proof)
        self.__chain.append(block_to_mine)
        self.__open_transactions.clear()
        mined_block_info, _ = self.chain_to_info(blocks=[block_to_mine])
        return mined_block_info

    def start_new_chain(self, new_user):
        """
        Method that starts a chain with a zero Block.
        :return:
        """
        first_transactions = [self.create_new_transaction(),
                              self.create_new_transaction(tx_recipient=new_user, tx_amount=self.__DEFAULT_PRIZE)]
        a = Block(previous_hash='', index=0, transactions=first_transactions, proof=0, time=0)
        self.__chain.append(a)
        print(self.__chain[0].index)

    def compare_blocks(self, new_block):
        chain_block_hash = self.hash_block(self.__chain[new_block.index])
        new_block_hash = self.hash_block(new_block)
        return chain_block_hash == new_block_hash

    def compare_txs(self, txs):
        new_txs = filter(lambda x: x not in self.__open_transactions, txs)
        missing_txs = filter(lambda x: x not in txs, self.__open_transactions)
        return new_txs, missing_txs

    def compare_chains(self, new_blocks_info):
        """
        TODO
        :param new_blocks_info:
        :return:
        """
        new_blocks = Blockchain.info_to_chain(blocks=new_blocks_info)
        last_block = new_blocks[-1]
        if last_block.index == self.__chain[-1].index + 1:
            return self.__chain.append(last_block)
        else:
            pass

    def get_balance(self, user):
        """
        Calculates the account balance of the owner
        :param user: The public key for this user.
        :return: The total balance of the owner.
        """
        temp_open_tx = self.__open_transactions
        temp_chain_blocks = self.__chain
        # Calculating total amount that was sent to other participants.
        tx_sender = [tx.amount
                     for block in temp_chain_blocks
                     for tx in block.transactions
                     if tx.sender == user]
        open_tx_sender = [tx.amount for tx in temp_open_tx if tx.sender == user]
        tx_sender += open_tx_sender
        amount_sent = ft.reduce(lambda tx_sum, tx_amt: tx_sum + tx_amt, tx_sender, 0)
        # Calculating total amount that was received from other participants.
        tx_recipient = [tx.amount
                        for block in temp_chain_blocks
                        for tx in block.transactions
                        if tx.recipient == user]
        amount_received = ft.reduce(lambda tx_sum, tx_amt: tx_sum + tx_amt, tx_recipient, 0)
        return amount_received - amount_sent

    def is_safe(self):
        """
        Verify the current chain integrity and return True if it's valid or False if it's not.
        :return Returns True if the chain is safe or False if not.
        """
        for index, block in enumerate(self.__chain):
            if index == 0:
                continue
            if not block.previous_hash == Blockchain.hash_block(self.__chain[index - 1]):
                return False
            if not Blockchain.valid_proof(block.transactions, block.previous_hash, block.proof):
                return False
        return True

    @staticmethod
    def create_new_transaction(tx_recipient=__DEFAULT_SENDER, tx_amount=0,
                               tx_sender=__DEFAULT_SENDER, tx_signature=__DEFAULT_SIGNATURE, tx_time=None):
        new_transaction = Tx(tx_sender, tx_recipient, tx_amount, tx_signature, tx_time)
        return new_transaction

    @staticmethod
    def hash_block(block):
        """Hashes a block and returns a string representation of it.

        :param block: The block to be hashed
        :return: Hashed string if the block is not None else None
        """

        return hl.sha3_256(json.dumps(f'{block}').encode()).hexdigest()

    @staticmethod
    def verify_transaction(transaction):
        """
        Method to verify if the transaction is properly signed.
        :param transaction:
        :return: True if the transaction signature matches, false if it does not.
        """
        public_key = RSA.importKey(binascii.unhexlify(transaction.sender))
        verifier = CSign.new(public_key)
        tx_hash = SHA256.new(f'{transaction.sender}{transaction.recipient}{transaction.amount}'.encode('utf8'))
        # noinspection PyTypeChecker
        return verifier.verify(tx_hash, binascii.unhexlify(transaction.signature))

    @staticmethod
    def calculate_proof(transactions, last_hash):
        """
        Calculates the proof of work for the chain.

        :param transactions:
        :param last_hash:
        :return:
        """
        proof = 0
        while not Blockchain.valid_proof(transactions, last_hash, proof):
            proof += 1
        return proof

    @staticmethod
    def valid_proof(transactions, last_hash, proof):
        guess = [str(tx.amount) + str(tx.sender) + str(tx.recipient)
                 + str(tx.timestamp) for tx in transactions]
        guess = (str(last_hash) + str(proof)) + ft.reduce(lambda x, y: x + y, guess, '')
        guess = guess.encode()
        guess_hash = hl.sha3_256(guess).hexdigest()
        return guess_hash[0:2] == Blockchain.__HASH_VALIDATION

    @staticmethod
    def info_to_chain(**raw_info):
        """
        Converts the information of a chain from dict to objects.
        :param raw_info:
        :return: mounted_blockchain
        """
        loaded_chain = raw_info['blocks'] if raw_info['blocks'] is not None and 'blocks' in raw_info else []
        loaded_transactions = raw_info['txs'] if raw_info['txs'] is not None and 'txs' in raw_info else []
        new_chain = [Block(previous_hash=loaded_block['previous_hash'],
                           index=loaded_block['index'],
                           proof=loaded_block['proof'],
                           transactions=[Tx(tx_sender=tx['sender'],
                                            tx_recipient=tx['recipient'],
                                            tx_signature=tx['signature'],
                                            tx_amount=tx['amount'],
                                            tx_time=tx['timestamp'])
                                         for tx in loaded_block['transactions'] if
                                         loaded_block['transactions']],
                           time=loaded_block['timestamp']
                           ) for loaded_block in loaded_chain]

        new_transactions = [Tx(tx_sender=open_tx['sender'],
                               tx_recipient=open_tx['recipient'],
                               tx_signature=open_tx['signature'],
                               tx_amount=open_tx['amount'],
                               tx_time=open_tx['timestamp'])
                            for open_tx in loaded_transactions]
        return new_chain, new_transactions

    @staticmethod
    def chain_to_info(**blockchain):
        """
        TODO
        :param blockchain:
        :return:
        """
        temp_chain = cp.deepcopy(blockchain['blocks']) if 'blocks' in blockchain else []
        temp_txs = cp.deepcopy(blockchain['txs']) if 'txs' in blockchain else []
        # Converting the blocks in the chain to ordered dictionaries
        blocks_info = [Od([('previous_hash', block.previous_hash),
                           ('index', block.index),
                           ('proof', block.proof),
                           ('transactions',
                            [Od([('sender', tx.sender),
                                 ('recipient', tx.recipient),
                                 ('amount', tx.amount),
                                 ('timestamp', tx.timestamp),
                                 ('signature', tx.signature)])
                             for tx in block.transactions]),
                           ('timestamp', block.timestamp)]) for block in temp_chain]
        # Converting the transactions in the chain to ordered dictionaries
        txs_info = [Od([('sender', tx.sender),
                        ('recipient', tx.recipient),
                        ('amount', tx.amount),
                        ('timestamp', tx.timestamp),
                        ('signature', tx.signature)])
                    for tx in temp_txs]
        return blocks_info, txs_info
