import os
from flask import jsonify, request, send_from_directory

from blockchain_view.node_web_view import NodeWebView

node_web = NodeWebView()
_DEFAULT_UI_PATH = '../blockchain_ui/'


def start_node_server(config_info):
    return node_web.connect_node(config_info)


@node_web.web_app.route('/', methods=['GET'])
def get_node_ui():
    global _DEFAULT_UI_PATH
    return send_from_directory(_DEFAULT_UI_PATH, 'node.html')


@node_web.web_app.route('/network', methods=['GET'])
def get_network_ui():
    return send_from_directory(_DEFAULT_UI_PATH, 'network.html')


@node_web.web_app.route('/chain', methods=['GET'])
def get_chain():
    global node_web
    status = 500
    response = {}
    dict_chain = node_web.node_connection.blockchain
    if dict_chain is not None:
        response = {'chain': dict_chain, 'message': 'These are all the open transactions.'}
        status = 200
    return jsonify(response), status


@node_web.web_app.route('/txs', methods=['GET'])
def get_transactions():
    global node_web
    dict_transactions = node_web.node_connection.open_transactions
    response = {}
    if len(dict_transactions) > 0:
        response['transactions'] = dict_transactions
        response['message'] = 'These are all the open transactions.'
    else:
        response['error'] = 'Error with open transactions.'
        response['message'] = 'There are no open transactions.'
    return jsonify(response), 200


@node_web.web_app.route('/balance', methods=['GET'])
def get_balance():
    global node_web
    return f'{node_web.node_connection.balance}'


@node_web.web_app.route('/mine', methods=['POST'])
def mine():
    response = {}
    status = 500
    if node_web.node_connection.ask_mine_block():
        blockchain = node_web.node_connection.blockchain
        response['message'] = 'Mining operation was successful.'
        response['block'] = f'This was the block added: \n{blockchain[-1]}'
        response['mining_reward'] = f'{node_web.node_connection.blockchain}'
        response['balance'] = f'{node_web.node_connection.balance}'
        status = 200
    else:
        response['message'] = 'Error mining a new block.'
        response['error'] = 'There is no block to mine.'
    return jsonify(response), status


@node_web.web_app.route('/tx', methods=['POST'])
def new_tx():
    global node_web
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
        tx_recipient = request_info['recipient']
        if not node_web.node_connection.check_wallet(tx_recipient):
            response['message'] = 'Error adding transaction.'
            response['error'] = 'The recipient does not exist.'
        else:
            tx_amount = request_info['amount']
            if not node_web.node_connection.send_transaction(tx_recipient, tx_amount):
                response['message'] = 'Error adding transaction.'
                response['error'] = 'There is no funds for this transaction.'
            else:
                response['message'] = 'Transaction added.'
                response['transaction'] = node_web.node_connection.open_transactions[-1]
                response['balance'] = f'{node_web.node_connection.balance}'
                status = 200

    return jsonify(response), status


@node_web.web_app.route('/bd-tx', methods=['POST'])
def receive_tx():
    global node_web
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
    elif node_web.node_connection.send_transaction(*tx_info):
        response['message'] = 'Transaction added.'
        status = 200
    return jsonify(response), status


@node_web.web_app.route('/user', methods=['GET'])
def load_wallet():
    response = {'message': 'Wallet changed.', 'balance': f'{node_web.node_connection.balance}',
                'public_key': f'{node_web.node_connection.user}'}
    status = 200
    return jsonify(response), status


@node_web.web_app.route('/user', methods=['POST'])
def create_wallet():
    global node_web
    new_user = request.get_json()['user']
    response = {}
    status = 500
    if new_user is None:
        response['message'] = 'Error loading user.'
        response['error'] = 'No username sent.'
    else:
        node_web.node_connection.user = new_user
        response['message'] = 'Wallet changed.'
        response['balance'] = f'{node_web.node_connection.balance}'
        response['public_key'] = f'{node_web.node_connection.user}'
        status = 200
    return jsonify(response), status


# @node_web.web_app.route("/node", methods=['POST'])
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

# @node_web.web_app.route('/node/<node_id>', methods=['DELETE'])
# def delete_node(node_id):
#     global node_web
#     status = 500
#     response = {}
#     if node_id == "" or node_id is None:
#         response['message'] = 'Error removing node.'
#         response['error'] = 'Some data was missing from the request.'
#         status = 400
#     else:
#         if _node.remove_node(node_id):
#
#             response['message'] = 'Node removed.'
#             response['nodes'] = f'These are the remaining nodes: {_node.output_blockchain().nodes}'
#             status = 200
#         else:
#             response['message'] = 'Error removing node.'
#             response['error'] = 'There was a problem with the node.'
#     return jsonify(response), status


@node_web.web_app.route('/node', methods=['GET'])
def get_nodes():
    status = 500
    response = {}
    nodes = node_web.node_connection.nodes
    nodes.remove(node_web.node_connection.config["port"])
    if nodes is not None:
        response['message'] = 'These are all the present nodes.'
        response['nodes'] = nodes
        status = 200
    return jsonify(response), status


@node_web.web_app.route('/quit', methods=['GET'])
def quit_api():
    node_web.node_connection.disconnect_node()
    # noinspection PyProtectedMember
    os._exit(1)