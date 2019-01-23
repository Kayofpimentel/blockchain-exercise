import blockchain_model

run_crypto_chain = True

while run_crypto_chain:
    print('Please, choose a option: ')
    print('1: Add a new transaction value')
    print('2: Output the blockchain blocks')
    print('q: Quit')
    user_choice = input('Your choice: ')
    if user_choice == '1':
        transaction = blockchain_model.get_transaction()
        recipient, amount = transaction
        blockchain_model.add_transaction(recipient, blockchain_model.owner, tx_amount=amount)
        print(blockchain_model.open_transactions)
    elif user_choice == '2':
        blockchain_model.output_blockchain()
    elif user_choice == 'q':
        run_crypto_chain = False
    elif user_choice == 'h':
        if len(blockchain_model.blockchain) > 2:
            blockchain_model.blockchain[2] = [2]
    else:
        print('Invalid option, select a value from the list.')
        continue
    if not blockchain_model.verify_chain_is_safe(blockchain_model.blockchain):
        print('The chain is invalid.')
        break
print('Done!')
