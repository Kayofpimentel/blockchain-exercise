import os

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

import blockchain_utils.chain_utils as cu
import blockchain_utils.wallet_utils as wu
from blockchain_view.node_view import NodeView


class NodeWebView(NodeView):

    def __init__(self, new_ui_path=None):
        super().__init__()
        self.__web_app = Flask(__name__)
        CORS(self.__web_app)
        self._ui_path = 'bla' if new_ui_path is None else new_ui_path

    def run(self):
        print('Node started, application online.')
        self.__web_app.run(host='127.0.0.1', port=_node.node_id)

    @__web_app.route('/', methods=['GET'])
    def get_node_ui(self):
        return send_from_directory(_ui_path, 'node.html')

    @__web_app.route('/network', methods=['GET'])
    def get_network_ui(self):
        return send_from_directory(_ui_path, 'network.html')

    @__web_app.route('/chain', methods=['GET'])
    def get_chain(self):
        status = 500
        response = {}
        dict_chain, _, _ = cu.chain_prep_to_save(_node.output_blockchain())
        if dict_chain is not None:
            response = {'chain': dict_chain, 'message': 'These are all the open transactions.'}
            status = 200
        return jsonify(response), status

    @__web_app.route('/txs', methods=['GET'])
    def get_transactions(self):
        _, dict_transactions, _ = cu.chain_prep_to_save(_node.output_blockchain())
        response = {}
        if len(dict_transactions) > 0:
            response['transactions'] = dict_transactions
            response['message'] = 'These are all the open transactions.'
        else:
            response['error'] = 'Error with open transactions.'
            response['message'] = 'There are no open transactions.'
        return jsonify(response), 200

    @__web_app.route('/balance', methods=['GET'])
    def get_balance(self):
        return f'{_node.user_balance(_user)}'

    @__web_app.route('/mine', methods=['POST'])
    def mine(self):
        response = {}
        status = 500
        if _node.try_mine_block(_user):
            blockchain = _node.output_blockchain()
            response['message'] = 'Mining operation was successful.'
            response['block'] = f'This was the block added: \n{blockchain.chain[-1].__dict__}'
            response['mining_reward'] = f'{blockchain.MINING_REWARD}'
            response['balance'] = f'{_node.user_balance(_user)}'
            status = 200
        else:
            response['message'] = 'Error mining a new block.'
            response['error'] = 'There is no block to mine.'
        return jsonify(response), status

    @__web_app.route('/tx', methods=['POST'])
    def new_tx(self):
        response = {}
        status = 400
        required_info = ['recipient', 'amount']
        request_info = request.get_json()
        if request_info is None:
            response['message'] = 'Error adding transaction.'
            response['error'] = 'No data found for the transaction.'
        elif not all(key in request_info for key in required_info):
            response['message'] = 'Error adding transaction.'
            response['error'] = 'Some data was missing from the request.'
        else:
            recipient_name = request_info['recipient']
            tx_recipient = wu.get_public_key(f'{_node.resources_path}{recipient_name}.txt')
            if tx_recipient is None:
                response['message'] = 'Error adding transaction.'
                response['error'] = 'The recipient does not exist.'
            else:
                tx_amount = request_info['amount']
                if not _node.new_transaction(_user, tx_recipient, tx_amount):
                    response['message'] = 'Error adding transaction.'
                    response['error'] = 'There is no funds for this transaction.'
                else:
                    response['message'] = 'Transaction added.'
                    response['transaction'] = _node.output_blockchain().open_transactions[-1].__dict__
                    response['balance'] = f'{_node.user_balance(_user)}'
                    status = 200

        return jsonify(response), status

    @__web_app.route('/bd-tx', methods=['POST'])
    def receive_tx(self):
        tx_info = request.get_json()
        response = {}
        status = 500
        required_info = ['sender', 'recipient', 'amount', 'signature']

        if tx_info is None:
            response['message'] = 'Error adding transaction.'
            response['error'] = 'No data found for the transaction.'
        elif not all(key in tx_info for key in required_info):
            response['message'] = 'Error adding transaction.'
            response['error'] = 'Some data was missing from the request.'
        elif _node.receive_transaction(tx_info):
            response['message'] = 'Transaction added.'
            status = 200
        return jsonify(response), status

    @__web_app.route('/user', methods=['PUT'])
    def change_wallet(self):
        response = {}
        status = 500
        wallet = wu.load_wallet(f'{_node.resources_path}{_user}.txt')
        if wallet is None:
            response['message'] = 'Error loading user.'
            response['error'] = 'No username sent.'
        else:
            response['message'] = 'Wallet changed.'
            response['balance'] = f'{_node.user_balance(_user)}'
            response['public_key'] = f'{wallet.public_key}'
            status = 200
        return jsonify(response), status

    @__web_app.route('/user', methods=['POST'])
    def create_wallet(self):
        response = {}
        status = 500
        wallet = wu.load_wallet(f'{_node.resources_path}{_user}.txt')
        if wallet is None:
            response['message'] = 'Error loading user.'
            response['error'] = 'No username sent.'
        else:
            response['message'] = 'Wallet changed.'
            response['balance'] = f'{_node.user_balance(_user)}'
            response['public_key'] = f'{wallet.public_key}'
            status = 200
        return jsonify(response), status

    # @__web_app.route("/node", methods=['POST'])
    # def add_node():
    #     global _node
    #     response = {}
    #     required_info = ['node_id']
    #     request_info = request.get_json()
    #     status = 500
    #     if request_info is None:
    #         response['message'] = 'Error adding node.'
    #         response['error'] = 'No data found regarding the node.'
    #         status = 400
    #     elif not all(key in request_info for key in required_info):
    #         response['message'] = 'Error adding node.'
    #         response['error'] = 'Some data was missing from the request.'
    #         status = 400
    #     else:
    #         new_node = int(request_info['node_id'])
    #         if _node.add_node_to_chain(new_node):
    #             response['message'] = f'New node added.'
    #             status = 200
    #         else:
    #             response['message'] = 'Error adding node.'
    #             response['error'] = 'Node already connected to chain.'
    #     return jsonify(response), status

    @__web_app.route('/node/<node_id>', methods=['DELETE'])
    def delete_node(self, node_id):
        global _node
        status = 500
        response = {}
        if node_id == "" or node_id is None:
            response['message'] = 'Error removing node.'
            response['error'] = 'Some data was missing from the request.'
            status = 400
        else:
            if _node.remove_node(node_id):

                response['message'] = 'Node removed.'
                response['nodes'] = f'These are the remaining nodes: {_node.output_blockchain().nodes}'
                status = 200
            else:
                response['message'] = 'Error removing node.'
                response['error'] = 'There was a problem with the node.'
        return jsonify(response), status

    @__web_app.route('/node', methods=['GET'])
    def get_nodes(self):
        global _node
        status = 500
        response = {}
        nodes = _node.output_blockchain().nodes
        nodes.remove(_node.node_id)
        if nodes is not None:
            response['message'] = 'These are all the present nodes.'
            response['nodes'] = nodes
            status = 200
        return jsonify(response), status

    @__web_app.route('/quit', methods=['GET'])
    def quit_api(self):
        global _node
        _node.remove_node(_node.node_id)
        _node.save_chain()
        # noinspection PyProtectedMember
        os._exit(1)

# if __name__ == '__main__':
#     from argparse import ArgumentParser
#     parser = ArgumentParser()
#     parser.add_argument('-p', '--port', default=None)
#     parser.add_argument('-u', '--user', default='Kayo')
#     parser.add_argument('-d', '--path', default='../blockchain_ui/')
#     args = parser.parse_args()
#     if not start_connection():
#         print('Error during program. Closing node.')
#     print('Program finished.')