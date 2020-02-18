import os
import copy as cp
from random import randint

from blockchain_model.node import Node
from blockchain_model.wallet import Wallet
from blockchain_utils import chain_utils as cu
from blockchain_utils import wallet_utils as wu
from blockchain_utils import node_utils as nu
from blockchain_network import node_sync as ns

_max_usr = 2


def generate_random_id(self):
    connected_nodes = self.__blockchain.nodes
    min_port = 5000
    max_port = 9999
    random_id = randint(min_port, max_port)
    return random_id if random_id not in connected_nodes else self.generate_random_id()


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
            self.__connected_nodes = set()

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
    def node(self):
        return self.__node.node_id

    @property
    def connected_nodes(self):
        return cp.copy(self.__connected_nodes)

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
        running_nodes = nu.load_nodes(self.config["dir"])
        new_node_id = self.config.pop("port")
        if new_node_id not in running_nodes:
            new_chain_info = cu.load_blockchain(self.config["dir"])
            self.__node = Node(chain_info=new_chain_info, node_id=new_node_id)
            if new_chain_info is None:
                self.__node.new_chain(self.user)
                cu.save_blockchain(*self.__node.chain_prep_to_save())
            self.add_node(nu.load_nodes(self.config["dir"]))
            nodes_to_save = self.connected_nodes
            nodes_to_save.add(new_node_id)
            nu.update_nodes(nodes_to_save, resources_path=self.config["dir"])
            print(self.connected_nodes)
        else:
            raise Exception(f'The node {self.config["dir"]} is already running.')

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
        self.config.update(config_info)
        self.connect_wallet()
        self.connect_node()

    def send_transaction(self, recipient, amount, sender=None, signature=None, nodes_info=None):
        sender = self.user if sender is None else sender
        if self.__node.verify_balance(sender, amount):

            if signature is None:
                tx_recipient = wu.load_keys(f'{self.config["dir"]}{recipient}.txt')[1]
                signature = self.__wallet.sign_transaction(tx_recipient, amount)
            else:
                tx_recipient = recipient
            if self.__node.receive_transaction(tx_recipient, amount, sender, signature):
                peer_nodes = self.connected_nodes - nodes_info if nodes_info is not None else self.connected_nodes
                send_nodes_info = {'self_id': [self.node], 'peer_nodes': list(peer_nodes)}
                return ns.broadcast_transaction(sender=sender, recipient=tx_recipient,
                                                amount=amount, signature=signature, nodes_info=send_nodes_info)
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

    def add_peer_node(self, nodes):
        self.add_node(nodes)
        return True

    def add_node(self, node_id):
        """
        Method to add a node connected to this chain_blocks.
        :param node_id:
        :return: :return: If the node was added or not.
        """
        if not self.check_node(node_id):
            self.__connected_nodes.update(node_id)
            return True
        return False

    def remove_node(self, node_id):
        """
        Method to remove a node connected to this chain_blocks.
        :param node_id:
        :return: If the node was removed or not.
        """
        if self.check_node(node_id):
            self.__connected_nodes = self.__connected_nodes - node_id
            return True
        return False

    def check_node(self, node_id):
        """
        Method to check if node id is already being used.
        :param node_id:
        :return: If the node is or not in being used.
        """
        return node_id.issubset(self.__connected_nodes)

    def disconnect_node(self):
        if self.__node.verify_chain_is_safe():
            blockchain_info = self.__node.chain_prep_to_save()
            nu.update_nodes(self.__connected_nodes, self.config["dir"])
            return cu.save_blockchain(*blockchain_info)
