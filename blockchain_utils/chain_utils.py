import json
from blockchain_model.block import Block
from blockchain_model.transaction import Transaction


def save_blockchain(blocks, txs, resources_path=None):
    """
    Method to save the data from recent transactions, mined blocks and connected nodes.
    :param txs:
    :param blocks:
    :param resources_path:
    :return if the operation was successful:
    """
    path = resources_path if resources_path is not None else './resources/'
    blockchain_path = f'{path}blockchain_data.txt'
    try:
        with open(blockchain_path, mode='w') as blockchain_file:
            blockchain_file.write(json.dumps(blocks))
            blockchain_file.write('\n')
            blockchain_file.write(json.dumps(txs))
            # blockchain_file.write('\n')
            # blockchain_file.write(json.dumps(nodes))
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
    :return the loaded chain_blocks
    """
    # TODO Remove use of Block and Transaction classes
    blockchain_path = f'{resources_path}blockchain_data.txt'
    try:
        with open(blockchain_path, mode='r') as blockchain_file:

            blockchain_info = blockchain_file.readlines()
            loaded_chain = json.loads(blockchain_info[0][:-1])
            loaded_transactions = json.loads(blockchain_info[1])
        return loaded_chain, loaded_transactions

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
