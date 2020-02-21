from blockchain_network.node_connection import NodeConnection


# TODO Improve communication between view and connection(controller) with Command Design Pattern.
class NodeView:

    def __init__(self):
        self.__node_connection = NodeConnection()

    @property
    def node_connection(self):
        return self.__node_connection

    def connect_node(self, config_info):
        self.__node_connection.start_connection(config_info)
        return self.run_node()

    def create_transaction(self, recipient_name, tx_amount):
        self.node_connection.send_transaction(recipient_name, tx_amount)

    def mine_block(self):
        return self.node_connection.node_mine_block()

    def change_wallet(self, user):
        self.node_connection.user = user

    def run_node(self):
        raise NotImplementedError

    def get_blocks(self):
        return self.node_connection.blockchain

    def quit_node(self):
        return self.node_connection.disconnect_node()
