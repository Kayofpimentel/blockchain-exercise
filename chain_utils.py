import json
import hashlib as hl
import functools as ft
from collections import OrderedDict as Od
from datetime import datetime as dt

HASH_VALIDATION = '00'


def valid_proof(transactions, last_hash, proof):
    guess = [str(tx.amount) + str(tx.sender) + str(tx.recipient)
             + str(dt.timestamp(tx.date)) for tx in transactions]
    guess = (str(last_hash) + str(proof)) + ft.reduce(lambda x, y: x + y, guess, '')
    guess = guess.encode()
    guess_hash = hl.sha3_256(guess).hexdigest()
    return guess_hash[0:2] == HASH_VALIDATION


def calculate_proof(transactions=None, last_hash=None):
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


def verify_chain_is_safe(blockchain):
    """
     Verify the current chain integrity and return True if it's valid or False if it's not.

     :param blockchain:
    """
    for index, block in enumerate(blockchain):
        if index == 0:
            continue
        if not block.previous_hash == hash_block(blockchain[index - 1]):
            return False
        if not valid_proof(block.transactions, block.previous_hash, block.proof):
            print('Proof of work is invalid.')
            return False
    return True


def get_balance(blockchain):
    """
    Calculates the account balance of the owner

    :param blockchain:
    :return: The total balance of the owner
    """

    # Calculating total amount that was sent to other participants.
    tx_sender = [tx.amount
                 for block in blockchain.chain
                 for tx in block.transactions
                 if tx.sender == blockchain.owner]
    open_tx_sender = [tx.amount for tx in blockchain.open_transactions if tx.sender == blockchain.owner]
    tx_sender += open_tx_sender
    amount_sent = ft.reduce(lambda tx_sum, tx_amt: tx_sum + tx_amt, tx_sender, 0)
    # Calculating total amount that was received from other participants.
    tx_recipient = [tx.amount
                    for block in blockchain.chain
                    for tx in block.transactions
                    if tx.recipient == blockchain.owner]
    amount_received = ft.reduce(lambda tx_sum, tx_amt: tx_sum + tx_amt, tx_recipient, 0)
    return amount_received - amount_sent


def verify_transaction(transaction, blockchain):
    """
    Method to verify if the transaction is possible.

    :param blockchain:
    :param transaction:
    :return: True for a possible transaction, False for the lack of funds
    """
    sender_balance = get_balance(blockchain)
    return sender_balance >= transaction.amount


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
                               ('amount', tx.amount),
                               ('timestamp', dt.timestamp(tx.date))])
                           for tx in block.transactions]),
                         ('timestamp', block.timestamp)])
        the_block_hash = f'{dict_block}'
        return hl.sha3_256(json.dumps(the_block_hash).encode()).hexdigest()
    else:
        return None
