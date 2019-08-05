import chain_utils as cu
from block import Block
from blockchain_model import Blockchain
from transaction import Transaction as Tx


class Node:

    def __init__(self, owner):
        self.__blockchain = Blockchain(owner)

    @property
    def blockchain(self):
        return self.__blockchain

    def create_new_transaction(self):
        tx_recipient = input('Enter the recipient of the transaction: \n')
        tx_amount = float(input("Please insert your transaction amount: \n"))
        new_transaction = Tx(tx_sender=self.blockchain.owner, tx_recipient=tx_recipient,
                             tx_amount=tx_amount)
        return new_transaction

    @staticmethod
    def get_user_choice():
        user_choice = input('Your command: ')
        return user_choice

    def start_operations(self):

        print('Please, choose a option: ')
        print('1: Add a new transaction value')
        print('2: Mine a new block')
        print('3: Output the blockchain blocks')
        print('4: Output your balance')
        print('q: Quit')

        run_crypto_chain = True
        if not cu.verify_chain_is_safe(self.blockchain.blockchain):
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
                    print('Could not mine, error with blockchain file.')
            elif user_choice == '3':
                self.blockchain.output_blockchain()
            elif user_choice == '4':
                print(f'Your balance is: {cu.get_balance(self.blockchain):^8.2f}')
            elif user_choice == 'q':
                if self.blockchain.end_session():
                    print('Blockchain saved, ending program.')
                    run_crypto_chain = False
                else:
                    print('Could not save or create file. Operations lost.')
            elif user_choice == 'h':
                hacked_block = Block(previous_hash='', index=0, transactions=[{'sender': 'Chris', 'recipient': 'Max',
                                                                               'amount': 100.0}], proof=0)
                self.blockchain.blockchain[len(self.blockchain.blockchain) - 2] = hacked_block
            else:
                print('Invalid option, select a value from the list.')
            if not cu.verify_chain_is_safe(self.blockchain.blockchain):
                return False
            print('Choose another operation.')
            print('Or press q to leave.')
        return True
