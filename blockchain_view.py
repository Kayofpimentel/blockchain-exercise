from blockchain_model import BlockchainModel
from block import Block

new_blockchain = BlockchainModel('Kayo')

print('Please, choose a option: ')
print('1: Add a new transaction value')
print('2: Mine a new block')
print('3: Output the blockchain blocks')
print('4: Output the participants')
print('5: Output your balance')
print('q: Quit')

run_crypto_chain = True
user_choice = None

while run_crypto_chain:
    if not new_blockchain.verify_chain_is_safe():
        print('The chain is invalid.')
        break
    if user_choice:
        print('Choose another operation.')
        print('Or press q to leave.')

    user_choice = input('Your choice: ')

    if user_choice == '1':
        tx_data = new_blockchain.new_transaction()
        tx_recipient, tx_amount = tx_data
        if new_blockchain.add_transaction(tx_recipient, None, tx_amount):
            print('Added transaction.')
        else:
            print('Transaction failed.')
    elif user_choice == '2':
        if new_blockchain.mine_block():
            print(f'A new block was mined. {new_blockchain.MINING_REWARD} added to your balance.')
        else:
            print('Could not mine, error with blockchain file.')
    elif user_choice == '3':
        new_blockchain.output_blockchain()
    elif user_choice == '4':
        print(new_blockchain.participants)
    elif user_choice == '5':
        print(f'Your balance is: {new_blockchain.get_balance():^8.2f}')
    elif user_choice == 'q':
        if new_blockchain.end_session():
            print('Blockchain saved, ending program.')
            run_crypto_chain = False
        else:
            print('Could not save or create file. Operations lost.')
    elif user_choice == 'h':
        hacked_block = Block(previous_hash='', index=0, transactions=[{'sender': 'Chris', 'recipient': 'Max',
                                                                       'amount': 100.0}], proof=0)
        new_blockchain.blockchain[len(new_blockchain.blockchain) - 2] = hacked_block
    else:
        print('Invalid option, select a value from the list.')
        continue

print('Program closed!')
