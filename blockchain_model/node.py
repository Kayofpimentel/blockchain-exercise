import copy as cp
import functools as ft
from random import randint
from collections import OrderedDict as Od

import blockchain_model.blockchain as bm


class Node:

    def __init__(self, node_id, chain_info=None):
        self.node_id = node_id
        self.__blockchain = bm.Blockchain(*chain_info)
        self.__blockchain.add_node(self.node_id)

    @property
    def blockchain(self):
        return cp.deepcopy(self.__blockchain.chain)

    @property
    def mining_reward(self):
        return self.__blockchain.reward

    def receive_transaction(self, tx_sender, tx_recipient, tx_amount, tx_signature):
        result = self.__blockchain.add_tx(tx_recipient, tx_amount, tx_sender, tx_signature)
        return result

    def try_mine_block(self, miner_key):
        if len(self.__blockchain.open_transactions) == 0:
            print('There are no transactions to mine a block.')
            return False
        return self.__blockchain.mine_block(miner_key)

    def connect_to_chain(self):
        return self.__blockchain.add_node(self.node_id)

    def disconnect_to_chain(self):
        return self.__blockchain.remove_node(self.node_id)

    def verify_chain_is_safe(self):
        """
         Verify the current chain integrity and return True if it's valid or False if it's not.
        :return Returns True if the chain is safe or False if not.
        """
        for index, block in enumerate(self.blockchain):
            if index == 0:
                continue
            if not block.previous_hash == bm.hash_block(self.blockchain[index - 1]):
                return False
            if not bm.valid_proof(block.transactions, block.previous_hash, block.proof):
                return False
        return True

    def get_balance(self, user):
        """
        Calculates the account balance of the owner

        :param user: The public key for this user.
        :return: The total balance of the owner.
        """
        open_tx = self.__blockchain.open_transactions
        # Calculating total amount that was sent to other participants.
        tx_sender = [tx.amount
                     for block in self.blockchain
                     for tx in block.transactions
                     if tx.sender == user]
        open_tx_sender = [tx.amount for tx in open_tx if tx.sender == user]
        tx_sender += open_tx_sender
        amount_sent = ft.reduce(lambda tx_sum, tx_amt: tx_sum + tx_amt, tx_sender, 0)
        # Calculating total amount that was received from other participants.
        tx_recipient = [tx.amount
                        for block in self.blockchain
                        for tx in block.transactions
                        if tx.recipient == user]
        open_tx_recipient = [tx.amount for tx in open_tx if tx.recipient == user]
        tx_recipient += open_tx_recipient
        amount_received = ft.reduce(lambda tx_sum, tx_amt: tx_sum + tx_amt, tx_recipient, 0)
        return amount_received - amount_sent

    def verify_balance(self, sender, amount):
        """
        Method to verify if the transaction is possible.
        :param sender:
        :param amount:
        :return: True for a possible transaction, False for the lack of funds
        """
        sender_balance = self.get_balance(sender)
        return sender_balance >= amount

    def output_blockchain(self):
        """
        Method that prints the blockchain in the console.
        :return: Nothing
        """
        for index, block in enumerate(self.blockchain):
            print('-' * 20)
            print(f'Outputting block {index}:')
            print(block)
            if index == (len(self.blockchain) - 1):
                print('-' * 20)

    def chain_prep_to_save(self):
        """
        Method to transform a object blockchain in ordered dictionaries.
        :return: This node's blockchain blocks, transactions that are still open and all the nodes connected to it.
        """
        chain_to_save = cp.deepcopy(self.__blockchain)
        dict_blockchain = [Od([('previous_hash', block.previous_hash),
                               ('index', block.index),
                               ('proof', block.proof),
                               ('transactions',
                                [Od([('sender', tx.sender),
                                     ('recipient', tx.recipient),
                                     ('amount', tx.amount),
                                     ('timestamp', tx.timestamp),
                                     ('signature', tx.signature)])
                                 for tx in block.transactions]),
                               ('timestamp', block.timestamp)]) for block in chain_to_save.chain]
        dict_transactions = [Od([('sender', tx.sender),
                                 ('recipient', tx.recipient),
                                 ('amount', tx.amount),
                                 ('timestamp', tx.timestamp),
                                 ('signature', tx.signature)])
                             for tx in chain_to_save.open_transactions]
        return dict_blockchain, dict_transactions, chain_to_save.nodes

    def generate_random_id(self):
        connected_nodes = self.__blockchain.nodes
        min_port = 5000
        max_port = 9999
        random_id = randint(min_port, max_port)
        return random_id if random_id not in connected_nodes else self.generate_random_id()
