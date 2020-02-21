import os
from flask import jsonify, request, send_from_directory

from blockchain_view.node_web_view import NodeWebView

__node_web = NodeWebView()
_DEFAULT_UI_PATH = '../blockchain_ui/'


def start_node_server(config_info):
    return __node_web.connect_node(config_info)


def data_check(required_info, request_info):
    request_problem = None
    if request_info is None:
        request_problem = {'message': 'Error in operation.', 'error': 'No data sent.'}
    elif not all(key in request_info for key in required_info):
        request_problem = {'message': 'Error in operation', 'error': 'Some data was missing from the request.'}
    return request_problem


@__node_web.web_app.route('/', methods=['GET'])
def get_node_ui():
    global _DEFAULT_UI_PATH
    return send_from_directory(_DEFAULT_UI_PATH, 'node.html')


@__node_web.web_app.route('/network', methods=['GET'])
def get_network_ui():
    return send_from_directory(_DEFAULT_UI_PATH, 'network.html')


@__node_web.web_app.route('/chain', methods=['GET'])
def get_chain():
    global __node_web
    status = 400
    response = {}
    dict_chain = __node_web.node_connection.blockchain
    if dict_chain is not None:
        response = {'chain': dict_chain, 'message': 'These are all the open transactions.'}
        status = 200
    return jsonify(response), status


@__node_web.web_app.route('/txs', methods=['GET'])
def get_transactions():
    global __node_web
    dict_transactions = __node_web.node_connection.open_transactions
    response = {}
    if len(dict_transactions) > 0:
        response['transactions'] = dict_transactions
        response['message'] = 'These are all the open transactions.'
    else:
        response['error'] = 'Error with open transactions.'
        response['message'] = 'There are no open transactions.'
    return jsonify(response), 200


@__node_web.web_app.route('/balance', methods=['GET'])
def get_balance():
    global __node_web
    return f'{__node_web.node_connection.balance}'


@__node_web.web_app.route('/user', methods=['GET'])
def load_wallet():
    response = {'message': 'Wallet changed.', 'balance': f'{__node_web.node_connection.balance}',
                'public_key': f'{__node_web.node_connection.user}'}
    status = 200
    return jsonify(response), status


@__node_web.web_app.route('/node', methods=['GET'])
def get_nodes():
    status = 400
    response = {}
    nodes = list(__node_web.node_connection.connected_nodes)
    if nodes is not None:
        response['message'] = 'These are all the present nodes.'
        response['nodes'] = nodes
        status = 200
    return jsonify(response), status


@__node_web.web_app.route('/mine', methods=['POST'])
def mine():
    response = {}
    status = __node_web.mine_block()
    if status/300 < 1:
        blockchain = __node_web.get_blocks()
        response['message'] = 'Mining operation was successful.'
        response['block'] = f'This was the block added: \n{blockchain[-1]}'
        response['mining_reward'] = f'{__node_web.node_connection.reward}'
        response['balance'] = f'{__node_web.node_connection.balance}'
    elif status == 409:
        response['message'] = 'Error mining a new block.'
        response['error'] = 'There is no block to mine.'
    return jsonify(response), status


@__node_web.web_app.route('/tx', methods=['POST'])
def new_tx():
    response = {}
    status = 400
    required_info = ['recipient', 'amount']
    request_info = request.get_json()
    request_problem = data_check(required_info, request_info)
    if request_problem is None:
        tx_recipient = request_info['recipient']
        if not __node_web.node_connection.check_wallet(tx_recipient):
            response['message'] = 'Error adding transaction.'
            response['error'] = 'The recipient does not exist.'
        else:
            tx_amount = request_info['amount']
            status = __node_web.node_connection.send_transaction(tx_recipient, tx_amount)
            if status == 409:
                response['message'] = 'Error adding transaction.'
                response['error'] = 'There is no funds for this transaction.'
            else:
                response['message'] = 'Transaction added.'
                response['transaction'] = __node_web.node_connection.open_transactions[-1]
                response['balance'] = f'{__node_web.node_connection.balance}'
    else:
        response.update(request_problem)
    return jsonify(response), status


@__node_web.web_app.route('/bc-tx', methods=['POST'])
def receive_tx():
    tx_info = request.get_json()
    tx_info['nodes_info'] = set(tx_info['nodes_info']['sent_nodes']) | \
                            set(tx_info['nodes_info']['peer_nodes'])
    response = {}
    status = 400
    required_info = ['sender', 'recipient', 'amount', 'signature', 'nodes_info']
    request_problem = data_check(required_info, tx_info)
    if request_problem is None:
        status = __node_web.node_connection.send_transaction(**tx_info)
        response['message'] = 'Transaction added.'
    else:
        response.update(request_problem)
    return jsonify(response), status


@__node_web.web_app.route('/bc-block', methods=['POST'])
def receive_block():
    block_info = request.get_json()
    block_info['nodes_info'] = set(block_info['nodes_info']['sent_nodes']) | set(block_info['nodes_info']['peer_nodes'])
    response = {}
    status = 400
    required_info = ['block', 'nodes_info']
    request_problem = data_check(required_info, block_info)
    if request_problem is None:
        status = __node_web.node_connection.send_block(**block_info)
        response['message'] = 'Block added.'
    else:
        response.update(request_problem)
    return jsonify(response), status

# @__node_web.web_app.route('/bc-chain', methods=['POST'])
# def receive_chain():
#     chain_info = request.get_json()
#     chain_info['nodes_info'] = set(chain_info['nodes_info']['sent_nodes']) | \
#                             set(chain_info['nodes_info']['peer_nodes'])
#     response = {}
#     status = 400
#     required_info = ['chain', 'open_transactions', 'nodes_info']
#     request_problem = data_check(required_info, chain_info)
#     if request_problem is None:
#         status = __node_web.node_connection.send_transaction(**chain_info)
#
#         response['message'] = 'Transaction added.'
#     else:
#         response.update(request_problem)
#     return jsonify(response), status
#     pass


@__node_web.web_app.route('/user', methods=['POST'])
def create_wallet():
    request_response = request.get_json()
    response = {}
    status = 400
    request_problem = data_check(['new_user'], request_response)
    if request_problem is None:
        __node_web.node_connection.user = request_response['new_user']
        response['message'] = 'Wallet changed.'
        response['balance'] = f'{__node_web.node_connection.balance}'
        response['public_key'] = f'{__node_web.node_connection.user}'
        status = 200
    else:
        response.update(request_problem)
    return jsonify(response), status


@__node_web.web_app.route("/node", methods=['POST'])
def add_nodes():
    response = {}
    required_info = ['nodes_id']
    request_info = request.get_json()
    if request_info is None:
        response['message'] = 'Error adding node.'
        response['error'] = 'No data found regarding the node.'
        status = 400
    elif not all(key in request_info for key in required_info):
        response['message'] = 'Error adding node.'
        response['error'] = 'Some data was missing from the request.'
        status = 400
    else:
        try:
            new_nodes = {request_info['nodes_id']}
        except TypeError:
            new_nodes = set(request_info['nodes_id'])
        __node_web.node_connection.add_peer_node(new_nodes)
        response['message'] = 'New node added.'
        status = 200
    return jsonify(response), status


@__node_web.web_app.route('/node/<node_id>', methods=['DELETE'])
def delete_nodes(node_id):
    response = {}
    status = 400
    if not (node_id is None or node_id == ''):
        if __node_web.node_connection.remove_node({node_id}):
            response['message'] = 'Node removed.'
            response['nodes'] = f'These are the remaining nodes: {__node_web.node_connection.connected_nodes}'
            status = 200
        else:
            response['message'] = 'Error removing node.'
            response['error'] = 'There was a problem with the node.'
    else:
        response.update({'message': 'Error removing node.', 'error': 'No node id was sent.'})
    return jsonify(response), status


@__node_web.web_app.route('/quit', methods=['GET'])
def quit_api():
    __node_web.node_connection.disconnect_node()
    # noinspection PyProtectedMember
    os._exit(1)
