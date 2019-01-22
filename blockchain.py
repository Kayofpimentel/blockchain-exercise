# Initializing our blockchain list
blockchain = []
open_transactions = []
owner = 'Kayo'
run_crypto_chain = True


def get_last_blockchain_value():
    """Returns the last value of the current blockchain. """
    if len(blockchain) < 1:
        print("The blockchain is empty.")
        return None
    return blockchain[-1]


def add_transaction(tx_recipient, tx_sender=owner, tx_amount=1.0):
    """Append a new value as well as the last blockchain value to the blockchain.

    Arguments:
        :param tx_sender: The sender of the coins
        :param tx_recipient: The recipient of the coins
        :param tx_amount: The amount of the coins sent with the transaction (default = 1.0)

    """

    transaction_info = {'sender': tx_sender, 'recipient': tx_recipient, 'amount': tx_amount}
    open_transactions.append(transaction_info)


def mine_block():
    pass


def get_transaction():
    tx_recipient = input('Enter the recipient of the transaction: \n')
    tx_amount = float(input("Please insert your transaction amount: \n"))
    return tx_recipient, tx_amount


def output_blockchain():
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


while run_crypto_chain:
    print('Please, choose a option: ')
    print('1: Add a new transaction value')
    print('2: Output the blockchain blocks')
    print('q: Quit')
    user_choice = input('Your choice: ')
    if user_choice == '1':
        transaction = get_transaction()
        recipient, amount = transaction
        add_transaction(recipient, owner, tx_amount=amount)
        print(open_transactions)
    elif user_choice == '2':
        output_blockchain()
    elif user_choice == 'q':
        run_crypto_chain = False
    elif user_choice == 'h':
        if len(blockchain) > 2:
            blockchain[2] = [2]
    else:
        print('Invalid option, select a value from the list.')
        continue
    if not verify_chain_is_safe(blockchain):
        print('The chain is invalid.')
        break
print('Done!')
