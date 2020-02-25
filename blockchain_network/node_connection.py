import os
import copy as cp
from random import randint

from blockchain_model.node import Node
from blockchain_model.wallet import Wallet
from blockchain_utils import chain_utils as cu
from blockchain_utils import wallet_utils as wu
from blockchain_network import chain_sync as cs

_max_usr = 2


def generate_random_id(self):
    connected_nodes = self.__blockchain.nodes
    min_port = 5000
    max_port = 9999
    random_id = randint(min_port, max_port)
    return random_id if random_id not in connected_nodes else self.generate_random_id()


# TODO Break class to separate IO from Model
# TODO Create a public property getter for all config values and make config private
# TODO Use the Observer Pattern to improve node communication.
# TODO Improve log/response messages and errors for each operation.
# TODO Integrate node_connection.py with node_view.py and node.py
# TODO Allow the user to login with alias or create new wallet
class NodeConnection:

    def __init__(self, config_info=None):

        self.__wallet = None
        self.__node = None
        self.__connected_nodes = set()

        self.config = {'reward': 0}
        if config_info is not None:
            self.start_connection(config_info)

    @property
    def user(self):
        return self.__wallet.public_key

    @user.setter
    def user(self, user):
        self.config.update({"user": user})
        self.connect_wallet()

    @property
    def open_transactions(self):
        return self.__node.blockchain_info['txs']

    @property
    def blockchain(self):
        return self.__node.blockchain_info['blocks']

    @property
    def node(self):
        return cp.copy(self.__node.node_id)

    @property
    def connected_nodes(self):
        return cp.copy(self.__connected_nodes)

    @property
    def balance(self):
        """
        Method to recover the user balance.
        :return:
        """
        return self.__node.user_balance(self.user)

    @property
    def reward(self):
        """

        :return:
        """
        return self.__node.mining_reward

    def connect_node(self):
        """
        Method that start the node and loads the chain_blocks.
        :return: If the node was added or not.
        """
        new_node_id = self.config.pop('port')
        new_chain_info = cu.load_blockchain(self.config['dir'])
        self.__node = Node(chain_info=new_chain_info, node_id=new_node_id)
        self.config['reward'] = self.__node.mining_reward
        if new_chain_info is None:
            self.__node.new_chain(self.user)
            cu.save_blockchain(**self.__node.blockchain_info)

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
        """

        :param user:
        :return:
        """
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

    # TODO Fix operation return
    def send_transaction(self, recipient, amount, sender=None, signature=None, nodes_info=None):
        """

        :param recipient:
        :param amount:
        :param sender:
        :param signature:
        :param nodes_info:
        :return:
        """
        sender = self.user if sender is None else sender
        if self.__node.verify_balance(sender, amount):

            if signature is None:
                tx_recipient = wu.load_keys(f'{self.config["dir"]}{recipient}.txt')[1]
                signature = self.__wallet.sign_transaction(tx_recipient, amount)
            else:
                tx_recipient = recipient
            if self.__node.receive_transaction(tx_recipient, amount, sender, signature):
                send_nodes_info = self.prepare_nodes(nodes_info)
                cs.broadcast_transaction(sender=sender, recipient=tx_recipient,
                                         amount=amount, signature=signature, nodes_info=send_nodes_info)
                return 200
        else:
            return 409

    def send_block(self, result, nodes_info=None):
        """

        :param result:
        :param nodes_info:
        :return:
        """

        send_nodes_info = self.prepare_nodes(nodes_info)
        incorrect_nodes = cs.broadcast_block(block=result, nodes_info=send_nodes_info)
        if not incorrect_nodes:
            return result
        else:
            cs.broadcast_chain(blocks=self.__node.blockchain_info, peer_nodes=incorrect_nodes)
            return result

    def add_block(self, block, nodes_info):
        result = self.__node.receive_block(block)
        if result['status'] == 201:
            self.send_block(result['block'], nodes_info)
        return result

    def node_mine_block(self):
        mined_block = self.__node.try_mine_block(self.user)
        if mined_block is not None:
            return self.send_block(mined_block)
        return None

    def repair_chain(self, blocks):
        self.__node.receive_chain(blocks)

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

    # TODO
    def sync_node(self, sync_nodes, sync_chain, sync_op):
        pass

    def sync_mining(self, block):
        return self.__node.compare_chains(block)

    def prepare_nodes(self, received_nodes):
        """

        :param received_nodes:
        :return:
        """
        peer_nodes = self.connected_nodes - received_nodes if received_nodes is not None else self.connected_nodes
        sent_nodes = self.connected_nodes | received_nodes \
            if received_nodes is not None else self.connected_nodes | {self.__node.node_id}
        prepared_nodes = {'sent_nodes': list(sent_nodes), 'peer_nodes': list(peer_nodes)}
        return prepared_nodes

    def disconnect_node(self):
        """

        :return:
        """
        if self.__node.verify_chain_is_safe():
            return cu.save_blockchain(**self.__node.blockchain_info)
