import json
import binascii
import hashlib as hl
import functools as ft
from block import Block
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from collections import OrderedDict as Od
from transaction import Transaction as Tx
from Crypto.Signature import PKCS1_v1_5 as CSign

HASH_VALIDATION = '00'


def valid_proof(transactions, last_hash, proof):
    guess = [str(tx.amount) + str(tx.sender) + str(tx.recipient)
             + str(tx.timestamp) for tx in transactions]
    guess = (str(last_hash) + str(proof)) + ft.reduce(lambda x, y: x + y, guess, '')
    guess = guess.encode()
    guess_hash = hl.sha3_256(guess).hexdigest()
    return guess_hash[0:2] == HASH_VALIDATION


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


def verify_chain_is_safe(chain):
    """
     Verify the current chain integrity and return True if it's valid or False if it's not.

     :param chain:
    """
    for index, block in enumerate(chain):
        if index == 0:
            continue
        if not block.previous_hash == hash_block(chain[index - 1]):
            return False
        if not valid_proof(block.transactions, block.previous_hash, block.proof):
            return False
    return True


def get_balance(blockchain, user):
    """
    Calculates the account balance of the owner

    :param user: The public key for this user.
    :param blockchain: The blockchain to calculate the balance of this user.
    :return: The total balance of the owner.
    """
    # Calculating total amount that was sent to other participants.
    tx_sender = [tx.amount
                 for block in blockchain.chain
                 for tx in block.transactions
                 if tx.sender == user]
    open_tx_sender = [tx.amount for tx in blockchain.open_transactions if tx.sender == user]
    tx_sender += open_tx_sender
    amount_sent = ft.reduce(lambda tx_sum, tx_amt: tx_sum + tx_amt, tx_sender, 0)
    # Calculating total amount that was received from other participants.
    tx_recipient = [tx.amount
                    for block in blockchain.chain
                    for tx in block.transactions
                    if tx.recipient == user]
    open_tx_recipient = [tx.amount for tx in blockchain.open_transactions if tx.recipient == user]
    tx_recipient += open_tx_recipient
    amount_received = ft.reduce(lambda tx_sum, tx_amt: tx_sum + tx_amt, tx_recipient, 0)
    return amount_received - amount_sent


def verify_balance(transaction, blockchain):
    """
    Method to verify if the transaction is possible.

    :param blockchain:
    :param transaction:
    :return: True for a possible transaction, False for the lack of funds
    """
    sender_balance = get_balance(blockchain, transaction.sender)
    return sender_balance >= transaction.amount


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


def create_new_transaction(tx_sender=None, tx_recipient=None, tx_amount=None, tx_signature=None):
    if tx_recipient is not None:
        new_transaction = Tx(tx_sender=tx_sender, tx_recipient=tx_recipient,
                             tx_amount=tx_amount, tx_signature=tx_signature)
        return new_transaction
    else:
        return None


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


def save_blockchain(blockchain, resources_path=None):
    """
    Method to save the data from recent transactions and mined blocks after the program is closed.
    :param resources_path:
    :param blockchain:
    :return if the operation was successful:
    """
    path = resources_path if resources_path is not None else '../resources/'
    blockchain_path = f'{path}blockchain_data.txt'
    dict_blockchain, dict_transactions = object_to_dict(blockchain)
    try:
        with open(blockchain_path, mode='w') as blockchain_file:
            blockchain_file.write(json.dumps(dict_blockchain))
            blockchain_file.write('\n')
            blockchain_file.write(json.dumps(dict_transactions))

            # data_to_save = {'chain': self.chain, 'ot': self.open_transactions}
            # with open(filename, mode='wb') as blockchain_file:
            #     blockchain_file.write(pickle.dumps(data_to_save))
        return True

    except IOError:
        print(f'Could not save chain on {resources_path}. The error is the following {IOError}')
        raise SystemExit(0)


def load_blockchain(resources_path=None):
    """
    Method to load all the data from the chain when the program initiates.
    :param resources_path: The path
    :return the loaded blockchain
    """
    path = resources_path if resources_path is not None else '../resources/'
    blockchain_path = f'{path}blockchain_data.txt'
    try:
        with open(blockchain_path, mode='r') as blockchain_file:

            blockchain_info = blockchain_file.readlines()
            loaded_chain = json.loads(blockchain_info[0][:-1])

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

            loaded_transactions = json.loads((blockchain_info[1]))
            new_transactions = [Tx(tx_sender=open_tx['sender'],
                                   tx_recipient=open_tx['recipient'],
                                   tx_signature=open_tx['signature'],
                                   tx_amount=open_tx['amount'],
                                   tx_time=open_tx['timestamp'])
                                for open_tx in loaded_transactions]

        return new_chain, new_transactions

    except (IOError, IndexError):
        return False

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


def object_to_dict(blockchain):
    """
    Method to transform a object blockchain in ordered dictionaries.
    :param blockchain:
    :return:
    """
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
                           ('timestamp', block.timestamp)]) for block in blockchain.chain]
    dict_transactions = [Od([('sender', tx.sender),
                             ('recipient', tx.recipient),
                             ('amount', tx.amount),
                             ('timestamp', tx.timestamp),
                             ('signature', tx.signature)])
                         for tx in blockchain.open_transactions]
    return dict_blockchain, dict_transactions