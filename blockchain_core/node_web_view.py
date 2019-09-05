from flask import Flask, jsonify, request
from flask_cors import CORS
from blockchain import Blockchain
from block import Block
import chain_utils as cu

__web_app = Flask(__name__)
CORS(__web_app)
__wallet = cu.load_wallet('Kayo')
__blockchain = Blockchain()
resources_path = '../resources/'


def start_node(new_path=None):
    global __blockchain, resources_path, __web_app
    if new_path is not None:
        resources_path = new_path
    data = cu.load_blockchain(resources_path)
    if data is not None:
        __blockchain.load_chain(*data)
        print('Blockchain loaded.')
    else:
        print('No data found, starting new chain.')
        if not start_new_chain():
            print('Could not start chain, ending the program')
            quit()
    print('Node started, application online.')
    __web_app.run(host='127.0.0.1', port=5000)


def start_new_chain(first_transaction=None):
    if first_transaction is None:
        tx_sender = 'System0'
        tx_recipient = __wallet.public_key
        tx_amount = 100
        first_transaction = cu.create_new_transaction(tx_sender, tx_recipient, tx_amount)
    new_chain = [Block(previous_hash='', index=0, transactions=[first_transaction], proof=0, time=0)]
    new_op = []
    __blockchain.load_chain(new_chain, new_op)
    return cu.save_blockchain(blockchain=__blockchain)


@__web_app.route('/', methods=['GET'])
def get_ui():
    return 'This works!'


@__web_app.route('/wallet', methods=['GET'])
def change_wallet():
    response = {}
    status = 500
    request_info = request.get_json()
    if request_info is None:
        response['message'] = 'Error loading wallet.'
        response['error'] = 'No username sent.'
    else:
        __wallet.reset_keys()
        if __wallet.load_keys(request_info['user'], False):
            response['message'] = 'Wallet changed.'
            response['balance'] = f'Your balance is {cu.get_balance(__blockchain, __wallet.public_key)}'
            status = 200
        else:
            response['message'] = 'Error loading wallet.'
            response['error'] = 'Could not find user keys.'
    return jsonify(response), status


@__web_app.route('/wallet', methods=['GET'])
def create_wallet():
    # TODO
    return ''


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
        recipient_wallet = cu.load_wallet(response['recipient'], False)
        tx_recipient = recipient_wallet.public_key
        tx_amount = request_info['amount']
        tx_sender = __wallet.public_key
        tx_info = (tx_sender, tx_recipient, tx_amount)
        tx_signature = __wallet.sign_transaction(*tx_info)
        tx_to_add = cu.create_new_transaction(*tx_info, tx_signature)
        message = __blockchain.add_tx(tx_to_add)
        if 'Error' in message:
            response['message'] = 'Error adding transaction.'
            response['error'] = 'Not enough founds for this transaction'
        else:
            response['message'] = 'Transaction added.'
            response['transaction'] = tx_to_add.get_dict()
            response['mining_reward'] = f'New balance is: {cu.get_balance(__blockchain, __wallet.public_key)}'
            status = 200

        return jsonify(response), status


@__web_app.route('/mine', methods=['POST'])
def mine():
    response = {}
    block = __blockchain.mine_block(__wallet.public_key)
    if isinstance(block, Block):
        response['message'] = 'Mining operation was successful'
        response['block'] = f'This was the block added: \n{block.get_dict()}'
        response['mining_reward'] = f'Added {__blockchain.MINING_REWARD} to your balance. New balance is: ' \
                                    f'{cu.get_balance(__blockchain, __wallet.public_key)}'
        return jsonify(response), 201
    else:
        response['message'] = 'Error mining a new block.'
        response['error'] = f'{block}'
        response['wallet_status'] = 'Wallet set' if __wallet.public_key is not None else 'No public key found.'
        return jsonify(response), 500


@__web_app.route('/balance', methods=['GET'])
def get_balance():
    return f'Your balance is {cu.get_balance(blockchain=__blockchain, user=__wallet.public_key)}'


@__web_app.route('/chain', methods=['GET'])
def get_chain():
    dict_chain = [block.get_dict() for block in __blockchain.chain]
    for block in dict_chain:
        block['transactions'] = [tx.get_dict() for tx in block['transactions']]
    return jsonify(dict_chain), 200


if __name__ == '__main__':
    if not start_node():
        print('Error during program. Closing node.')
    print('Program finished.')
