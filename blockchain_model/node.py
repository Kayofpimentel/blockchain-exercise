from blockchain_model.blockchain import Blockchain


class Node:

    # TODO More elegant way to pass the set for the add_node method
    def __init__(self, node_id, chain_info=None):
        self.node_id = node_id
        self.__blockchain = Blockchain(*chain_info) if chain_info is not None else Blockchain()

    @property
    def blockchain_info(self):
        """
        Method to transform a object chain_blocks in ordered dictionaries.
        :return: This node's chain blocks and transactions that are still open.
        """
        dict_blockchain = {'blocks': self.__blockchain.chain_info, 'txs': self.__blockchain.op_txs_info}
        return dict_blockchain

    @property
    def mining_reward(self):
        return self.__blockchain.reward

    def user_balance(self, user):
        return self.__blockchain.get_balance(user)

    def new_chain(self, new_user):
        self.__blockchain.start_new_chain(new_user)

    def receive_chain(self, blocks_info):
        blocks, _ = self.__blockchain.info_to_chain(blocks=blocks_info, txs=None)
        self.__blockchain.reset_chain(blocks)

    def receive_transaction(self, *tx_info):
        result = self.__blockchain.add_tx(tx_info)
        return result

    def receive_block(self, block_info):
        block_to_add, _ = self.__blockchain.info_to_chain(blocks=block_info, txs=None)
        result = self.__blockchain.add_block(block_to_add)
        result.update({'block': block_info})
        return result

    def try_mine_block(self, miner_key):
        if len(self.__blockchain.op_txs_info) == 0:
            return None
        added_block = self.__blockchain.mine_block(miner_key)
        block_info, _ = self.__blockchain.chain_to_info(blocks=[added_block])
        return block_info if block_info else None

    def verify_chain_is_safe(self):
        return self.__blockchain.is_safe()

    def verify_balance(self, sender, amount):
        """
        Method to verify if the transaction is possible.
        :param sender:
        :param amount:
        :return: True for a possible transaction, False for the lack of funds
        """
        sender_balance = self.__blockchain.get_balance(sender)
        return sender_balance >= amount

    # TODO Return the result as a String instead of printing it directly.
    # TODO Move to node_terminal_view.py
    def output_blockchain(self):
        """
        Method that prints the chain_blocks in the console.
        :return: Nothing
        """
        for index, block in enumerate(self.__blockchain.chain_info):
            print('-' * 20)
            print(f'Outputting block {index}:')
            print(block)
            if index == (len(self.__blockchain.chain_info) - 1):
                print('-' * 20)
