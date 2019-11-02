from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from node import Node
import chain_utils as cu
import wallet_utils as wu

__web_app = Flask(__name__)
CORS(__web_app)
_node = None
_user = None
_ui_path = None


def start_node(default_path=None, new_ui_path=None):
    global __web_app, _node, _user, _ui_path
    _ui_path = '../blockchain_ui/' if new_ui_path is None else new_ui_path
    _node = Node(default_path)
    print(_ui_path)
    _user = 'Kayo'
    _node.add_wallet(_user, f'{_node.resources_path}{_user}.txt')
    print('Node started, application online.')
    __web_app.run(host='127.0.0.1', port=5000)


@__web_app.route('/', methods=['GET'])
def get_ui():
    return send_from_directory(_ui_path, 'node.html')


@__web_app.route('/balance', methods=['GET'])
def get_balance():
    return f'{_node.user_balance(_user)}'


@__web_app.route('/chain', methods=['GET'])
def get_chain():
    dict_chain, dict_transactions = cu.object_to_dict(_node.output_blockchain())
    response = {'chain': dict_chain, 'message': 'These are all the open transactions.'}
    return jsonify(response), 200


@__web_app.route('/txs', methods=['GET'])
def get_transactions():
    dict_chain, dict_transactions = cu.object_to_dict(_node.output_blockchain())
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
    if _node.mine_block(_user):
        blockchain = _node.output_blockchain()
        response['message'] = 'Mining operation was successful.'
        response['block'] = f'This was the block added: \n{blockchain.chain[-1].__dict__}'
        response['mining_reward'] = f'{blockchain.MINING_REWARD}'
        response['balance'] = f'{_node.user_balance(_user)}'
        return jsonify(response), 200
    else:
        response['message'] = 'Error mining a new block.'
        return jsonify(response), 500


@__web_app.route('/quit', methods=['GET'])
def quit_api():
    # TODO
    return ''


if __name__ == '__main__':
    if not start_node():
        print('Error during program. Closing node.')
    print('Program finished.')
