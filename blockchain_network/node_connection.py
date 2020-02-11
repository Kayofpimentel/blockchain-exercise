import os

from blockchain_model.node import Node
from blockchain_model.wallet import Wallet
from blockchain_utils import chain_utils as cu
from blockchain_utils import wallet_utils as wu

# from blockchain_utils import node_utils as nu

_max_usr = 2


# TODO Break class to separate IO from Model
# TODO Create a public property getter for all config values and make config private
class NodeConnection:

    def __init__(self, config_info=None):

        if config_info is not None:
            self.start_connection(config_info)
        else:
            self.__wallet = None
            self.config = {}
            self.__node = None

    @property
    def user(self):
        return self.__wallet.public_key

    @user.setter
    def user(self, user):
        self.config.update({"user": user})
        self.connect_wallet()

    @property
    def open_transactions(self):
        return self.__node.chain_open_transactions

    @property
    def blockchain(self):
        return self.__node.chain_blocks

    @property
    def nodes(self):
        return self.__node.chain_connected_nodes

    @property
    def balance(self):
        """
        Method to recover the user balance.
        :return:
        """
        return self.__node.get_balance(self.user)

    @property
    def reward(self):
        return self.__node.mining_reward

    def connect_node(self):
        """
        Method that start the node and loads the chain_blocks.
        :return: If the node was added or not.
        """
        new_chain_info = cu.load_blockchain(self.config["dir"])
        self.__node = Node(node_id=self.config["port"], chain_info=new_chain_info)
        if new_chain_info is None:
            self.__node.new_chain(self.user)
            cu.save_blockchain(*self.__node.chain_prep_to_save())


    def connect_wallet(self):
        """
        Method to recover the user keys and create the Wallet object.
        :return:
        """
        wallet_path = f'{self.config["dir"]}{self.config["user"]}.txt'
        if os.path.isfile(wallet_path):
            self.__wallet = Wallet(*wu.load_keys(wallet_path))
        else:
            self.__wallet = Wallet()
            self.__wallet.generate_keys()
            wu.save_keys(self.__wallet, wallet_path)

    def check_wallet(self, user):
        wallet_path = f'{self.config["dir"]}{user}.txt'
        return wu.check_wallet(wallet_path)

    def start_connection(self, config_info):
        """
        Method to start the connection between the Node and the NodeView
        :param config_info:
        :return:
        """
        self.config = config_info
        self.connect_wallet()
        self.connect_node()

    def send_transaction(self, recipient, tx_amount, tx_sender=None, tx_signature=None):
        tx_sender = self.user if tx_sender is None else tx_sender
        if self.__node.verify_balance(tx_sender, tx_amount):
            tx_recipient = wu.load_keys(f'{self.config["dir"]}{recipient}.txt')[1]
            if tx_signature is None:
                tx_signature = self.__wallet.sign_transaction(tx_recipient, tx_amount)
            return self.__node.receive_transaction(tx_sender, tx_recipient, tx_amount, tx_signature)
        else:
            print('Not enough funds to make transaction.')
            return False

    def ask_mine_block(self):

        if self.__node.try_mine_block(self.user):
            print(f'A new block was mined. {self.__node.mining_reward} added to your balance.')
            return True
        print('There was a problem mining the block. Operation lost.')
        return False

    def console_format_blockchain(self):
        return self.__node.output_blockchain()

    def node_security(self):
        return self.__node.verify_chain_is_safe()

    def remove_node(self, ):
        return self.__node.disconnect()

    def disconnect_node(self):
        self.__node.disconnect_to_chain()
        if self.__node.verify_chain_is_safe():
            print(*self.__node.chain_prep_to_save())
            return cu.save_blockchain(*self.__node.chain_prep_to_save())
