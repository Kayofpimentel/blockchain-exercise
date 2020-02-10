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

__DEFAULT_SENDER = 'SYSTEM'
__DEFAULT_SIGNATURE = 'MINING'
__DEFAULT_PRIZE = 50
__HASH_VALIDATION = '00'


def start_new_chain(transaction_info):
    """
    Method that starts a chain with a zero Block.
    :return:
    """
    first_transaction = Tx(*transaction_info[0])
    return [Block(previous_hash='', index=0, transactions=[first_transaction], proof=0, time=0)]


def create_first_transaction():
    """
    Method that starts a chain with a zero Block.
    :return:
    """
    first_transaction = Tx(tx_recipient=__DEFAULT_SENDER, tx_sender=__DEFAULT_SENDER,
                           tx_amount=0, tx_signature='ZERO')
    return first_transaction


def create_new_transaction(tx_recipient, tx_amount,
                           tx_sender=__DEFAULT_SENDER, tx_signature=__DEFAULT_SIGNATURE, tx_time=None):
    new_transaction = Tx(tx_sender, tx_recipient, tx_amount, tx_signature, tx_time)
    return new_transaction


def hash_block(block=None):
    """Hashes a block and returns a string representation of it.

    :param block: The block to be hashed
    :return: Hashed string if the block is not None else None
    """

    if block is not None:
        dict_block = Od([('previous_hash', block.previous_hash),
                         ('index', block.index),
                         ('proof', block.proof),
                         ('transactions',
                          [Od([('sender', tx.sender),
                               ('recipient', tx.recipient),
                               ('signature', tx.signature),
                               ('amount', tx.amount),
                               ('timestamp', tx.timestamp)])
                           for tx in block.transactions]),
                         ('timestamp', block.timestamp)])
        the_block_hash = f'{dict_block}'
        return hl.sha3_256(json.dumps(the_block_hash).encode()).hexdigest()
    else:
        return None


def verify_transaction(transaction):
    """
    Method to verify if the transaction is properly signed.
    :param transaction:
    :return: True if the transaction signature matches, false if it does not.
    """
    public_key = RSA.importKey(binascii.unhexlify(transaction.sender))
    verifier = CSign.new(public_key)
    tx_hash = SHA256.new(f'{transaction.sender}{transaction.recipient}{transaction.amount}'.encode('utf8'))
    return verifier.verify(tx_hash, binascii.unhexlify(transaction.signature))


def calculate_proof(transactions, last_hash):
    """
    Calculates the proof of work for the chain.

    :param transactions:
    :param last_hash:
    :return:
    """
    proof = 0
    while not valid_proof(transactions, last_hash, proof):
        proof += 1
    return proof


def valid_proof(transactions, last_hash, proof):
    guess = [str(tx.amount) + str(tx.sender) + str(tx.recipient)
             + str(tx.timestamp) for tx in transactions]
    guess = (str(last_hash) + str(proof)) + ft.reduce(lambda x, y: x + y, guess, '')
    guess = guess.encode()
    guess_hash = hl.sha3_256(guess).hexdigest()
    return guess_hash[0:2] == __HASH_VALIDATION


class Blockchain:

    def __init__(self, chain=None, open_txs=None, nodes=None, mining_reward=10):
        # TODO Improve first block check and creation
        # TODO Remove real user from first transaction
        # TODO Account for the total number of users registered on the blockchain
        # TODO Implement new user reward
        # TODO Implement decrease of reward with registered number of users
        self.__chain = chain if chain is not None else create_first_transaction()
        if chain:
            self.__chain = chain
        else:
            self.__chain = start_new_chain(chain) if chain is not None else []
        self.__chain = chain if chain is not None else []
        self.__open_transactions = open_txs if open_txs is not None else []
        self.__nodes = set() if nodes is None else set(nodes)
        self.__MINING_REWARD = mining_reward

    @property
    def chain(self):
        return self.__chain

    @property
    def open_transactions(self):
        return self.__open_transactions

    @property
    def nodes(self):
        return list(self.__nodes)

    @property
    def reward(self):
        return self.__MINING_REWARD

    def add_tx(self, *new_transaction_info):
        """
        Append a new value as well as the last chain value to the chain.
        Arguments:
        :param new_transaction_info
        """
        new_transaction = create_new_transaction(*new_transaction_info)
        # if result:
        #     for node in self.__blockchain.nodes:
        #         url = f'http://127.0.0.1:{node}/bc-tx'
        #         try:
        #             response = requests.post(url, json={
        #                 'sender': tx_sender,
        #                 'recipient': tx_recipient,
        #                 'amount': tx_amount,
        #                 'signature': tx_signature})
        #             # Check for positive response on broadcast
        #             if (response.status_code / 400) > 1:
        #                 result = False
        #                 # TODO check the problem and resolve, since the tx has already been added
        #                 break
        #         except requests.exceptions.ConnectionError:
        #             # TODO check with other nodes if the node is active
        #             continue
        self.__open_transactions.append(new_transaction)
        return True

    def mine_block(self, miner_key):
        """
        Method to add a new block to the chain.
        :return:
        """
        last_block = self.chain[-1]
        hashed_block = hash_block(last_block)
        temp_transactions = cp.deepcopy(self.__open_transactions)
        # Checking if all the transactions are verified with the right signature.
        block_status = True
        for count, tx in enumerate(temp_transactions):
            if not verify_transaction(tx):
                # Removing non verified transactions.
                del self.open_transactions[count]
                block_status = False
        if not block_status:
            return False
        # Add the reward transaction for the mining operation
        reward_transaction = create_new_transaction(tx_recipient=miner_key, tx_amount=self.reward)
        temp_transactions.append(reward_transaction)
        proof = calculate_proof(temp_transactions, hashed_block)
        block_to_mine = Block(previous_hash=hashed_block, index=len(self.chain), transactions=temp_transactions,
                              proof=proof)
        self.__chain.append(block_to_mine)
        self.__open_transactions.clear()
        return True

    def add_node(self, node_id):
        """
        Method to add a node connected to this blockchain.
        :param node_id:
        :return: :return: If the node was added or not.
        """
        if not self.check_node(node_id):
            self.__nodes.add(node_id)
            return True
        return False

    def remove_node(self, node_id):
        """
        Method to remove a node connected to this blockchain.
        :param node_id:
        :return: If the node was removed or not.
        """
        if self.check_node(node_id):
            self.__nodes.discard(node_id)
            return True
        return False

    def check_node(self, node_id):
        """
        Method to check if node id is already being used.
        :param node_id:
        :return: If the node is or not in being used.
        """
        return node_id in self.__nodes
