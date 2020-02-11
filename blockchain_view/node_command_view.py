from blockchain_view.node_view import NodeView


def show_choices():
    print('Please, choose a option: ')
    print('1: Add a new transaction')
    print('2: Mine a new block')
    print('3: Output the chain blocks')
    print('4: Output your balance')
    print('5: Change user')
    print('q: Quit')


# TODO Improve handling of error messages
class NodeCommandView(NodeView):

    def __init__(self):
        super().__init__()

    def run_node(self):
        # User options to interact with the Node
        if not self.node_connection.node_security():
            print('The loaded chain is corrupted!')
            return False
        show_choices()
        while True:
            user_choice = input()

            if user_choice == '0':
                show_choices()

            if user_choice == '1':
                recipient_name = input('Enter the recipient of the transaction: \n')
                # Finding if the user is in the system and recovering his key for the transaction.
                if not self.node_connection.check_wallet(recipient_name):
                    print('This recipient does not exist. Cannot complete transaction.')
                else:
                    tx_amount = float(input("Please insert your transaction amount: \n"))
                    self.create_transaction(recipient_name, tx_amount)

            elif user_choice == '2':
                self.node_connection.ask_mine_block()

            elif user_choice == '3':
                self.node_connection.console_format_blockchain()

            elif user_choice == '4':
                print(f'Your balance is: {self.node_connection.balance:^8.2f}')

            elif user_choice == '5':
                # TODO Offer to create a Wallet if it does not exist already.
                new_user = input('New user name:')
                self.change_wallet(new_user)
                print('Wallet changed.')

            elif user_choice == 'q':
                if self.quit_node():
                    print('Blockchain saved, ending program.')
                else:
                    print('Could not save or create file. Operations lost.')
                break
            else:
                print('Invalid option, select a value from the list.')
            if not self.node_connection.node_security():
                self.node_connection.remove_node()
                print('The chain is not safe. Operations lost.')
                return False

            print('Choose another operation.')
            print('Press 0 to see the menu.')
        return True

