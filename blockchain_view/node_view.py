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
        if self.node_connection.send_transaction(recipient_name, tx_amount):
            print('Added transaction.')
        else:
            print('Transaction failed.')

    def change_wallet(self, user):
        self.node_connection.user = user

    def run_node(self):
        pass

    def quit_node(self):
        return self.node_connection.disconnect_node()
