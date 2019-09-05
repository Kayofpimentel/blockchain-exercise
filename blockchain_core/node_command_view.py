from blockchain import Blockchain
import chain_utils as cu
from block import Block
from transaction import Transaction as Tx

import copy as cp


def start_new_node(user_name):
    new_node = Node(user_name)
    if new_node.start_operations():
        return True
    else:
        return False


class Node:

    def __init__(self, logged_user=None, resources_file_path=None):
        self.__wallet = cu.load_wallet(logged_user)
        self.resources_path = resources_file_path
        self.__blockchain = Blockchain()
        if resources_file_path is None:
            self.resources_path = '../resources/'
        data = cu.load_blockchain(self.resources_path)
        if data is not None:
            self.__blockchain.load_chain(*data)
            print('Blockchain loaded.')
        else:
            print('No data found, starting new chain.')
            if not self.start_new_chain():
                print('Could not start chain, ending the program')
                quit()

    @property
    def blockchain(self):
        return self.__blockchain

    @property
    def wallet(self):
        return self.__wallet

    @staticmethod
    def get_user_choice():
        user_choice = input('Your command: ')
        return user_choice

    def change_wallet(self, new_user):
        self.wallet.reset_keys()
        if self.wallet.load_keys(new_user):
            return True
        print('Could not load or create keys.')
        return False

    def start_operations(self):

        print('Please, choose a option: ')
        print('1: Add a new transaction value')
        print('2: Mine a new block')
        print('3: Output the chain blocks')
        print('4: Output your balance')
        print('5: Change wallet')
        print('q: Quit')

        run_crypto_chain = True
        if not cu.verify_chain_is_safe(self.blockchain.chain):
            print('The chain is not safe!')
            return False
        while run_crypto_chain:
            user_choice = self.get_user_choice()

            if user_choice == '1':
                # Finding if the user is in the system and recovering his keys for the transaction
                recipient_name = input('Enter the recipient of the transaction: \n')
                recipient_wallet = cu.load_wallet(recipient_name, False)
                tx_recipient = recipient_wallet.public_key
                tx_amount = float(input("Please insert your transaction amount: \n"))
                tx_sender = self.wallet.public_key
                new_tx = cu.create_new_transaction(tx_sender, tx_recipient, tx_amount)
                if self.blockchain.add_tx(new_tx):
                    print('Added transaction.')
                else:
                    print('Transaction failed.')

            elif user_choice == '2':
                if len(self.blockchain.open_transactions) == 0:
                    print('There are no transactions to mine a block.')
                elif self.blockchain.mine_block(self.wallet.public_key):
                    print(f'A new block was mined. {self.blockchain.MINING_REWARD} added to your balance.')
                else:
                    print('Could not mine, error with chain file.')

            elif user_choice == '3':
                self.blockchain.output_blockchain()

            elif user_choice == '4':
                print(f'Your balance is: {cu.get_balance(self.blockchain, self.wallet.public_key):^8.2f}')

            elif user_choice == '5':
                new_user = input('New user name:')
                if self.change_wallet(new_user):
                    print('Wallet changed.')
                else:
                    print('Could not change user. Finishing program.')
                    return False

            elif user_choice == 'q':
                data = cp.deepcopy(self.blockchain)
                if cu.save_blockchain(data):
                    print('Blockchain saved, ending program.')
                    break
                else:
                    print('Could not save or create file. Operations lost.')
            else:
                print('Invalid option, select a value from the list.')
            if not cu.verify_chain_is_safe(self.blockchain.chain):
                return False

            print('Choose another operation.')
            print('Or press q to leave.')
        return True

    def start_new_chain(self, first_transaction=None):
        if first_transaction is None:
            tx_sender = 'MINING'
            tx_recipient = self.wallet.public_key
            tx_amount = 100
            first_transaction = cu.create_new_transaction(tx_sender, tx_recipient, tx_amount)
        new_chain = [Block(previous_hash='', index=0, transactions=[first_transaction], proof=0, time=0)]
        new_op = []
        self.blockchain.load_chain(new_chain, new_op)
        return cu.save_blockchain(blockchain=self.blockchain)


if __name__ == '__main__':
    if not start_new_node(input('Insert user login: ')):
        print('Error during program. Closing node.')
    print('Program finished.')
