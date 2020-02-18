import functools as ft
from collections import OrderedDict as Od

import blockchain_model.blockchain as bm


class Node:

    # TODO More elegant way to pass the set for the add_node method
    def __init__(self, node_id, chain_info=None):
        self.node_id = node_id
        self.__blockchain = bm.Blockchain(*chain_info) if chain_info is not None else bm.Blockchain()

    @property
    def chain_blocks(self):
        temp_blocks = self.__blockchain.chain
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
                               ('timestamp', block.timestamp)]) for block in temp_blocks]
        return dict_blockchain

    @property
    def mining_reward(self):
        return self.__blockchain.reward

    @property
    def chain_open_transactions(self):
        temp_transactions = self.__blockchain.open_transactions
        dict_transactions = [Od([('sender', tx.sender),
                                 ('recipient', tx.recipient),
                                 ('amount', tx.amount),
                                 ('timestamp', tx.timestamp),
                                 ('signature', tx.signature)])
                             for tx in temp_transactions]
        return dict_transactions

    def new_chain(self, new_user):
        self.__blockchain.start_new_chain(new_user)

    def receive_transaction(self, *tx_info):
        result = self.__blockchain.add_tx(tx_info)
        return result

    def try_mine_block(self, miner_key):
        if len(self.__blockchain.open_transactions) == 0:
            print('There are no transactions to mine a block.')
            return False
        return self.__blockchain.mine_block(miner_key)

    def verify_chain_is_safe(self):
        """
         Verify the current chain integrity and return True if it's valid or False if it's not.
        :return Returns True if the chain is safe or False if not.
        """
        for index, block in enumerate(self.__blockchain.chain):
            if index == 0:
                continue
            if not block.previous_hash == bm.hash_block(self.__blockchain.chain[index - 1]):
                return False
            if not bm.valid_proof(block.transactions, block.previous_hash, block.proof):
                return False
        return True

    def get_balance(self, user):
        """
        Calculates the account balance of the owner

        :rtype: object
        :param user: The public key for this user.
        :return: The total balance of the owner.
        """
        temp_open_tx = self.__blockchain.open_transactions
        temp_chain_blocks = self.__blockchain.chain
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
        open_tx_recipient = [tx.amount for tx in temp_open_tx if tx.recipient == user]
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

    # TODO Return the result as a String instead of printing it directly.
    def output_blockchain(self):
        """
        Method that prints the chain_blocks in the console.
        :return: Nothing
        """
        for index, block in enumerate(self.chain_blocks):
            print('-' * 20)
            print(f'Outputting block {index}:')
            print(block)
            if index == (len(self.chain_blocks) - 1):
                print('-' * 20)

    def chain_prep_to_save(self):
        """
        Method to transform a object chain_blocks in ordered dictionaries.
        :return: This node's chain_blocks blocks, transactions that are still open and all the nodes connected to it.
        """
        return self.chain_blocks, self.chain_open_transactions
