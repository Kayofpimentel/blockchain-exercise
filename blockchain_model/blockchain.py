import json
import binascii
import copy as cp
import hashlib as hl
import functools as ft

from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import PKCS1_v1_5 as CSign

from blockchain_model.block import Block
from blockchain_model.transaction import Transaction as Tx

__DEFAULT_SENDER = 'SYSTEM'
__DEFAULT_SIGNATURE = 'MINING'
__HASH_VALIDATION = '00'


def create_new_transaction(tx_recipient=__DEFAULT_SENDER, tx_amount=0,
                           tx_sender=__DEFAULT_SENDER, tx_signature=__DEFAULT_SIGNATURE, tx_time=None):
    new_transaction = Tx(tx_sender, tx_recipient, tx_amount, tx_signature, tx_time)
    return new_transaction


def hash_block(block):
    """Hashes a block and returns a string representation of it.

    :param block: The block to be hashed
    :return: Hashed string if the block is not None else None
    """

    return hl.sha3_256(json.dumps(f'{block}').encode()).hexdigest()


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

    def __init__(self, chain=None, open_txs=None, mining_reward=10):
        # TODO Improve first block check and creation
        # TODO Remove real user from first transaction
        # TODO Account for the total number of users registered on the chain_blocks
        # TODO Implement new user reward
        # TODO Implement decrease of reward with registered number of users
        # TODO Secure chain operations just inside Blockchain Class, returning just copies.
        self.__chain = chain if chain is not None else []
        self.__open_transactions = open_txs if open_txs is not None else []
        self.__MINING_REWARD = mining_reward
        self.__DEFAULT_PRIZE = 50

    @property
    def chain(self):
        return self.__chain

    @property
    def open_transactions(self):
        return self.__open_transactions

    @property
    def reward(self):
        return self.__MINING_REWARD

    def add_tx(self, new_transaction_info):
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

    def start_new_chain(self, new_user):
        """
        Method that starts a chain with a zero Block.
        :return:
        """
        first_transactions = [create_new_transaction(), create_new_transaction(tx_recipient=new_user,
                                                                               tx_amount=self.__DEFAULT_PRIZE)]
        self.__chain.append(Block(previous_hash='', index=0, transactions=first_transactions, proof=0, time=0))
