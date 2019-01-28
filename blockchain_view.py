from blockchain_model import BlockchainModel

run_crypto_chain = True
new_blockchain = BlockchainModel('Kayo')


while run_crypto_chain:
    print('Please, choose a option: ')
    print('1: Add a new transaction value')
    print('2: Mine a new block')
    print('3: Output the blockchain blocks')
    print('q: Quit')
    user_choice = input('Your choice: ')
    if user_choice == '1':
        transaction = new_blockchain.new_transaction()
        recipient, amount = transaction
        new_blockchain.add_transaction(recipient, new_blockchain.owner, tx_amount=amount)
        print(new_blockchain.open_transactions)
    elif user_choice == '2':
        new_blockchain.mine_block()
    elif user_choice == '3':
        new_blockchain.output_blockchain()
    elif user_choice == 'q':
        run_crypto_chain = False
    elif user_choice == 'h':
        if len(new_blockchain.blockchain) > 1:
            new_blockchain.blockchain[len(new_blockchain.blockchain)-2] = \
                {'previous_hash': '', 'index': 0, 'transactions': [{'sender': 'Chris', 'recipient': 'Max', 'amount': 100.0}]}
    else:
        print('Invalid option, select a value from the list.')
        continue
    if not new_blockchain.verify_chain_is_safe(new_blockchain.blockchain):
        print('The chain is invalid.')
        break
print('Done!')
