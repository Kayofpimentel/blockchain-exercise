import os
import wallet_utils as wu
from node import Node


def start_operations(default_path):
    if default_path == "":
        default_path = None
    _node = Node(default_path)
    _user_name = input('Insert user login: ')
    wallet_path = f'{_node.resources_path}{_user_name}.txt'

    def change_wallet(old_user, user, new_path):
        if _node.add_wallet(user, new_path):
            _node.remove_wallet(old_user)
            return True
        else:
            print('Could not change user. Finishing program.')
            return False

    if not _node.add_wallet(_user_name, wallet_path):
        print('This user does not exist.')
        return False
    # User options to interact with the Node
    if not _node.node_security():
        print('The chain is not safe!')
        return False
    show_choices()
    while True:
        user_choice = input()

        if user_choice == '0':
            show_choices()

        if user_choice == '1':
            recipient_name = input('Enter the recipient of the transaction: \n')
            # Finding if the user is in the system and recovering his keys for the transaction
            tx_recipient = wu.get_public_key(f'{_node.resources_path}{recipient_name}.txt')
            if tx_recipient is None:
                print('This recipient does not exist.')
                success = False
            else:
                tx_amount = float(input("Please insert your transaction amount: \n"))
                success = _node.new_transaction(_user_name, tx_recipient, tx_amount)
            if success:
                print('Added transaction.')
            else:
                print('Transaction failed.')

        elif user_choice == '2':
            _node.mine_block(_user_name)
            print('Could not mine, error with chain file.')

        elif user_choice == '3':
            _node.print_blockchain()

        elif user_choice == '4':
            print(f'Your balance is: {_node.user_balance(_user_name):^8.2f}')

        elif user_choice == '5':
            new_user = input('New user name:')
            wallet_path = f'{_node.resources_path}{new_user}.txt'
            if not os.path.isfile(wallet_path):
                wu.save_keys(wu.create_new_wallet(), wallet_path)
            if change_wallet(_user_name, new_user, wallet_path):
                _user_name = new_user
                print('Wallet changed.')
            else:
                print('Could not change Wallet, ending program.')
                return False

        elif user_choice == 'q':
            if _node.save_chain():
                print('Blockchain saved, ending program.')
                break
            else:
                print('Could not save or create file. Operations lost.')
        else:
            print('Invalid option, select a value from the list.')
        if not _node.node_security():
            print('Chain is not safe.')
            return False

        print('Choose another operation.')
        print('Press 0 to see the menu.')
    return True


def show_choices():
    print('Please, choose a option: ')
    print('1: Add a new transaction value')
    print('2: Mine a new block')
    print('3: Output the chain blocks')
    print('4: Output your balance')
    print('5: Change wallet')
    print('q: Quit')


if __name__ == '__main__':
    if not start_operations(input('Insert the resources path: ')):
        print('Error during program. Closing node.')
    print('Program finished.')
