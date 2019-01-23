# Initializing our blockchain list
blockchain = []
open_transactions = []
owner = 'Kayo'


def get_last_blockchain_value():
    """Returns the last value of the current blockchain. """

    global  blockchain

    if len(blockchain) < 1:
        print("The blockchain is empty.")
        return None
    return blockchain[-1]


def add_transaction(tx_recipient, tx_sender=owner, tx_amount=1.0):

    global open_transactions

    """Append a new value as well as the last blockchain value to the blockchain.

    Arguments:
        :param tx_sender: The sender of the coins
        :param tx_recipient: The recipient of the coins
        :param tx_amount: The amount of the coins sent with the transaction (default = 1.0)

    """

    transaction_info = {'sender': tx_sender, 'recipient': tx_recipient, 'amount': tx_amount}
    open_transactions.append(transaction_info)


def mine_block():
    global blockchain, open_transactions
    last_block = blockchain[-1]
    block = {'previous_hash': 'XYZ', 'index': len(blockchain), 'transactions': open_transactions}


def get_transaction():
    tx_recipient = input('Enter the recipient of the transaction: \n')
    tx_amount = float(input("Please insert your transaction amount: \n"))
    return tx_recipient, tx_amount


def output_blockchain():

    global blockchain

    if len(blockchain) > 0:
        for block in blockchain:
            print('Outputting block')
            print(block)
    else:
        blockchain.append([0])
        print('Outputting block')
        print(get_last_blockchain_value())


def verify_chain_is_safe(the_chain, counter=0, is_safe=True):
    if len(the_chain) > counter+1:
        if the_chain[counter] in the_chain[counter+1]:
            counter += 1
            return verify_chain_is_safe(the_chain, counter)
        else:
            return False
    else:
        return is_safe

