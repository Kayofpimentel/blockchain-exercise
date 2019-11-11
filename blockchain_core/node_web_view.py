import os
import chain_utils as cu
import wallet_utils as wu
from node import Node
from flask_cors import CORS
from flask import Flask, jsonify, request, send_from_directory


__web_app = Flask(__name__)
CORS(__web_app)
_ui_path = None


def start_node(new_ui_path=None):
    global __web_app, _ui_path
    _ui_path = '../blockchain_ui/' if new_ui_path is None else new_ui_path
    _node.add_wallet(_user, f'{_node.resources_path}{_user}.txt')
    print('Node started, application online.')
    __web_app.run(host='127.0.0.1', port=_node.node_id)


@__web_app.route('/', methods=['GET'])
def get_node_ui():
    return send_from_directory(_ui_path, 'node.html')


@__web_app.route('/network', methods=['GET'])
def get_network_ui():
    return send_from_directory(_ui_path, 'network.html')


@__web_app.route('/balance', methods=['GET'])
def get_balance():
    return f'{_node.user_balance(_user)}'


@__web_app.route('/chain', methods=['GET'])
def get_chain():
    status = 500
    response = {}
    dict_chain, _, _ = cu.chain_prep_to_save(_node.output_blockchain())
    if dict_chain is not None:
        response = {'chain': dict_chain, 'message': 'These are all the open transactions.'}
        status = 200
    return jsonify(response), status


@__web_app.route('/txs', methods=['GET'])
def get_transactions():
    _, dict_transactions, _ = cu.chain_prep_to_save(_node.output_blockchain())
    response = {}
    if len(dict_transactions) > 0:
        response['transactions'] = dict_transactions
        response['message'] = 'These are all the open transactions.'
    else:
        response['error'] = 'Error with open transactions.'
        response['message'] = 'There are no open transactions.'
    return jsonify(response), 200


@__web_app.route('/wallet', methods=['PUT'])
def change_wallet():
    response = {}
    status = 500
    wallet = wu.load_wallet(f'{_node.resources_path}{_user}.txt')
    if wallet is None:
        response['message'] = 'Error loading wallet.'
        response['error'] = 'No username sent.'
    else:
        response['message'] = 'Wallet changed.'
        response['balance'] = f'{_node.user_balance(_user)}'
        response['public_key'] = f'{wallet.public_key}'
        status = 200
    return jsonify(response), status


@__web_app.route('/wallet', methods=['POST'])
def create_wallet():
    response = {}
    status = 500
    wallet = wu.load_wallet(f'{_node.resources_path}{_user}.txt')
    if wallet is None:
        response['message'] = 'Error loading wallet.'
        response['error'] = 'No username sent.'
    else:
        response['message'] = 'Wallet changed.'
        response['balance'] = f'{_node.user_balance(_user)}'
        response['public_key'] = f'{wallet.public_key}'
        status = 200
    return jsonify(response), status


@__web_app.route('/tx', methods=['POST'])
def new_tx():
    response = {}
    status = 500
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


@__web_app.route('/mine', methods=['POST'])
def mine():
    response = {}
    status = 500
    if _node.mine_block(_user):
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


@__web_app.route("/node", methods=['POST'])
def add_node():
    global _node
    response = {}
    required_info = ['node_id']
    request_info = request.get_json()
    status = 500
    if request_info is None:
        response['message'] = 'Error adding node.'
        response['error'] = 'No data found regarding the node.'
        status = 400
    elif not all(key in request_info for key in required_info):
        response['message'] = 'Error adding node.'
        response['error'] = 'Some data was missing from the request.'
        status = 400
    else:
        new_node = int(request_info['node_id'])
        if _node.add_node_to_chain(new_node):
            response['message'] = f'New node added.'
            status = 200
        else:
            response['message'] = 'Error adding node.'
            response['error'] = 'Node already connected to chain.'
    return jsonify(response), status


@__web_app.route('/node/<node_id>', methods=['DELETE'])
def delete_node(node_id):
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
def get_nodes():
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
def quit_api():
    global _node
    _node.remove_node(_node.node_id)
    _node.save_chain()
    # noinspection PyProtectedMember
    os._exit(1)


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=None)
    parser.add_argument('-u', '--user', default='Kayo')
    args = parser.parse_args()
    _node = Node(node_id=args.port)
    _user = args.user
    if not start_node():
        print('Error during program. Closing node.')
    print('Program finished.')
