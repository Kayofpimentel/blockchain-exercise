from blockchain_util import chain_utils as cu
from uuid import uuid4
from blockchain_core.block import Block
from blockchain_core.blockchain import Blockchain
from blockchain_core.transaction import Transaction as Tx
from blockchain_wallet.wallet import Wallet


def start_new_node(user_name):
    new_node = Node(user_name)
    if new_node.start_operations():
        return True
    else:
        return False


class Node:

    def __init__(self, logged_user=None):
        self.__user = logged_user if logged_user is not None else 'Test'
        self.__wallet = Wallet(user_name=self.user)
        self.__node_id = str(uuid4())
        self.__blockchain = Blockchain(self.wallet.public_key, hosting_node=self.node_id)

    @property
    def user(self):
        return self.__user

    @user.setter
    def user(self, new_user='Test'):
        self.__user = new_user
        self.wallet.change_user(self.user)

    @property
    def node_id(self):
        return self.__node_id

    @property
    def blockchain(self):
        return self.__blockchain

    @property
    def wallet(self):
        return self.__wallet

    def create_new_transaction(self):
        tx_recipient = input('Enter the recipient of the transaction: \n')
        tx_amount = float(input("Please insert your transaction amount: \n"))
        tx_signature = self.wallet.sign_transaction(sender=self.user, recipient=tx_recipient, amount=tx_amount)
        new_transaction = Tx(tx_sender=self.user, tx_recipient=tx_recipient,
                             tx_amount=tx_amount, tx_signature=tx_signature)
        return new_transaction

    @staticmethod
    def get_user_choice():
        user_choice = input('Your command: ')
        return user_choice

    def change_wallet(self, new_user):
        if self.wallet.save_keys():
            self.wallet.reset_keys()
            self.user = new_user
            if self.wallet.load_keys():
                self.blockchain.owner = self.wallet.public_key
                return True
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
            return False
        while run_crypto_chain:
            user_choice = self.get_user_choice()

            if user_choice == '1':
                new_tx = self.create_new_transaction()
                if self.blockchain.add_transaction(new_tx):
                    print('Added transaction.')
                else:
                    print('Transaction failed.')

            elif user_choice == '2':
                if self.blockchain.mine_block():
                    print(f'A new block was mined. {self.blockchain.MINING_REWARD} added to your balance.')
                else:
                    print('Could not mine, error with chain file.')

            elif user_choice == '3':
                self.blockchain.output_blockchain()

            elif user_choice == '4':
                print(f'Your balance is: {cu.get_balance(self.blockchain):^8.2f}')

            elif user_choice == '5':
                new_user = input('New user name:')
                if self.change_wallet(new_user):
                    print('Wallet changed.')
                else:
                    print('Could not change user. Finishing program.')
                    return False

            elif user_choice == 'q':
                if self.wallet.save_keys():
                    if self.blockchain.end_session():
                        print('Blockchain saved, ending program.')
                        run_crypto_chain = False
                    else:
                        print('Could not save or create file. Operations lost.')

            elif user_choice == 'h':
                hacked_block = Block(previous_hash='', index=0, transactions=[{'sender': 'Chris', 'recipient': 'Max',
                                                                               'amount': 100.0}], proof=0)
                self.blockchain.chain[len(self.blockchain.chain) - 2] = hacked_block
            else:
                print('Invalid option, select a value from the list.')
            if not cu.verify_chain_is_safe(self.blockchain.chain):
                return False

            print('Choose another operation.')
            print('Or press q to leave.')
        return True


if __name__ == '__main__':
    if not start_new_node(input('Insert user login: ')):
        print('Error during program. Closing node.')
    print('Program finished.')
