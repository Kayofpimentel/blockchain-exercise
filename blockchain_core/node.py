import chain_utils as cu
import wallet_utils as wu
import copy as cp
from block import Block
from blockchain import Blockchain


class Node:

    def __init__(self, resources_file_path=None):
        self.resources_path = resources_file_path if resources_file_path is not None else '../resources/'
        self.__wallets = {}
        chain_info = cu.load_blockchain(self.resources_path)
        if chain_info:
            self.__blockchain = Blockchain(*chain_info)
        else:
            self.__blockchain = self.start_new_chain()
            cu.save_blockchain(self.__blockchain, self.resources_path)

    def start_new_chain(self, first_transaction=None):
        if first_transaction is None:
            first_user = 'Kayo'
            wallet_file = f'{self.resources_path}{first_user}.txt'
            tx_sender = 'MINING'
            first_wallet = wu.load_wallet(wallet_file)
            if first_wallet is None:
                first_wallet = wu.create_new_wallet()
                wu.save_keys(first_wallet, wallet_file)
            tx_recipient = first_wallet.public_key
            tx_amount = 100
            first_transaction = cu.create_new_transaction(tx_sender, tx_recipient, tx_amount)
        new_chain = [Block(previous_hash='', index=0, transactions=[first_transaction], proof=0, time=0)]
        new_op = []
        return Blockchain(new_chain, new_op)

    def add_wallet(self, user, wallet_path):
        """

        :param user:
        :param wallet_path:
        :return:
        """
        user_wallet = wu.load_wallet(wallet_path)
        if user_wallet is not None:
            self.__wallets[user] = user_wallet
            return True
        else:
            return False

    def remove_wallet(self,user):
        if user in self.__wallets:
            self.__wallets.pop(user)
            return True
        else:
            return False

    def new_transaction(self, *tx_info):
        user, tx_recipient, tx_amount = tx_info
        user_wallet = self.__wallets[user]
        tx_signature = wu.sign_transaction(user_wallet, tx_recipient, tx_amount)
        new_tx = cu.create_new_transaction(user_wallet.public_key, tx_recipient, tx_amount, tx_signature)
        return self.__blockchain.add_tx(new_tx)

    def mine_block(self, user):
        if len(self.__blockchain.open_transactions) == 0:
            print('There are no transactions to mine a block.')
            return False
        elif self.__blockchain.mine_block(self.__wallets[user].public_key):
            print(f'A new block was mined. {self.__blockchain.MINING_REWARD} added to your balance.')
            return True

    def print_blockchain(self):
        self.__blockchain.output_blockchain()

    def output_blockchain(self):
        return cp.deepcopy(self.__blockchain)

    def user_balance(self, user):
        user_wallet = self.__wallets[user]
        return cu.get_balance(self.__blockchain, user_wallet.public_key)

    def node_security(self):
        return cu.verify_chain_is_safe(self.__blockchain.chain)

    def save_chain(self):
        return cu.save_blockchain(cp.deepcopy(self.__blockchain))
