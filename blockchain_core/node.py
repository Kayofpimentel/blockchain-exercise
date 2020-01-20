import node_utils
import requests
import copy as cp
import chain_utils as cu
import wallet_utils as wu
from block import Block
from blockchain import Blockchain


class Node:

    def __init__(self, resources_file_path=None, node_id=None):
        self.resources_path = resources_file_path if resources_file_path is not None else '../resources/'
        self.__wallets = {}
        chain_info = cu.load_blockchain(self.resources_path)
        if chain_info is not None:
            self.__blockchain = Blockchain(*chain_info)
            self.node_id = node_utils.generate_node_id(self.__blockchain.nodes) if node_id is None else node_id
            self.__blockchain.add_node(self.node_id)
        else:
            self.__blockchain = self.start_new_chain()
            self.node_id = node_utils.generate_node_id() if node_id is None else node_id
            self.__blockchain.add_node(self.node_id)
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
        Add a wallet(user) to a node.
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

    def remove_wallet(self, user):
        if user in self.__wallets:
            self.__wallets.pop(user)
            return True
        else:
            return False

    def receive_transaction(self, *tx_info):
        new_tx = cu.create_new_transaction(tx_info)
        return self.__blockchain.add_tx(new_tx)

    def new_transaction(self, *tx_info):
        user, tx_recipient, tx_amount = tx_info
        user_wallet = self.__wallets[user]
        tx_sender = user_wallet.public_key
        tx_signature = wu.sign_transaction(user_wallet, tx_recipient, tx_amount)
        result = self.receive_transaction(tx_sender, tx_recipient, tx_amount, tx_signature)
        if result:
            for node in self.__blockchain.nodes:
                url = f'http://127.0.0.1:{node}/bc-tx'
                try:
                    response = requests.post(url, json=
                    {'sender': tx_sender,
                     'recipient': tx_recipient,
                     'amount': tx_amount,
                     'signature': tx_signature})
                    # Check for positive response on broadcast
                    if (response.status_code / 400) > 1:
                        result = False
                        # TODO check the problem and resolve, since the tx has already been added
                        break
                except requests.exceptions.ConnectionError:
                    # TODO check with other nodes if the node is active
                    continue
        return result

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

    def add_node_to_chain(self, new_node_id):
        return self.__blockchain.add_node(new_node_id)

    def remove_node(self, node_id):
        return self.__blockchain.remove_node(node_id)
