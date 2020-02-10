import json
from blockchain_model.block import Block
from blockchain_model.transaction import Transaction


def save_blockchain(*blockchain, resources_path=None):
    """
    Method to save the data from recent transactions, mined blocks and connected nodes.
    :param resources_path:
    :param blockchain:
    :return if the operation was successful:
    """
    path = resources_path if resources_path is not None else './resources/'
    blockchain_path = f'{path}blockchain_data.txt'
    dict_blockchain, dict_transactions, nodes = blockchain
    try:
        with open(blockchain_path, mode='w') as blockchain_file:
            blockchain_file.write(json.dumps(dict_blockchain))
            blockchain_file.write('\n')
            blockchain_file.write(json.dumps(dict_transactions))
            blockchain_file.write('\n')
            blockchain_file.write(json.dumps(nodes))
            # data_to_save = {'chain': self.chain, 'ot': self.open_transactions}
            # with open(filename, mode='wb') as blockchain_file:
            #     blockchain_file.write(pickle.dumps(data_to_save))
        return True

    except IOError:
        return False


def load_blockchain(resources_path):
    """
    Method to load all the data from the chain when the program initiates.
    :param resources_path: The path
    :return the loaded blockchain
    """
    # TODO Remove use of Block and Transaction classes
    blockchain_path = f'{resources_path}blockchain_data.txt'
    try:
        with open(blockchain_path, mode='r') as blockchain_file:

            blockchain_info = blockchain_file.readlines()
            loaded_chain = json.loads(blockchain_info[0][:-1])
            new_chain = [Block(previous_hash=loaded_block['previous_hash'],
                               index=loaded_block['index'],
                               proof=loaded_block['proof'],
                               transactions=[Transaction(tx_sender=tx['sender'],
                                                         tx_recipient=tx['recipient'],
                                                         tx_signature=tx['signature'],
                                                         tx_amount=tx['amount'],
                                                         tx_time=tx['timestamp'])
                                             for tx in loaded_block['transactions'] if
                                             loaded_block['transactions']],
                               time=loaded_block['timestamp']
                               ) for loaded_block in loaded_chain]

            loaded_transactions = json.loads(blockchain_info[1][:-1])
            new_transactions = [Transaction(tx_sender=open_tx['sender'],
                                            tx_recipient=open_tx['recipient'],
                                            tx_signature=open_tx['signature'],
                                            tx_amount=open_tx['amount'],
                                            tx_time=open_tx['timestamp'])
                                for open_tx in loaded_transactions]
            new_nodes = json.loads(blockchain_info[2])
        return new_chain, new_transactions, new_nodes

    except (IOError, IndexError):
        return None

    # with open(filename, mode='ab+') as blockchain_file:
    #     blockchain_file.seek(0)
    #     if not blockchain_file.read(1):
    #         return False
    #     else:
    #         blockchain_file.seek(0)
    #         blockchain_info = pickle.loads(blockchain_file.read())
    #
    # self.__blockchain = blockchain_info['chain']
    # self.__open_transactions = blockchain_info['ot']
