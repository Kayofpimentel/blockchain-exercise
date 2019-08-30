from blockchain_util import chain_utils as cu
import copy as cp
from blockchain_core.block import Block
from blockchain_core.transaction import Transaction as Tx


class Blockchain:

    def __init__(self, chain=None, open_txs=None,  mining_reward=10):
        self.__chain = chain
        self.__open_transactions = open_txs
        self.MINING_REWARD = mining_reward

    @property
    def chain(self):
        return self.__chain

    @property
    def open_transactions(self):
        return self.__open_transactions

    def add_transaction(self, new_transaction):
        """
        Append a new value as well as the last chain value to the chain.

        Arguments:
            :param
        """
        if cu.verify_balance(transaction=new_transaction, blockchain=cp.deepcopy(self)):
            self.__open_transactions.append(new_transaction)
            return True
        print('Not enough balance for this operation.')
        return False

    def mine_block(self, user):
        """
        Method to add a new block to the chain.
        :return:
        """
        last_block = self.chain[-1]
        hashed_block = cu.hash_block(last_block)
        temp_transactions = cp.deepcopy(self.__open_transactions)
        # Checking if all the transactions are verified with the right signature
        block_status = True
        for count, tx in enumerate(temp_transactions):
            if not cu.verify_transaction(tx):
                print('Unsafe transaction found, removing it.')
                del self.open_transactions[count]
                block_status = False
        if not block_status:
            return False
        # Add the reward transaction for the mining operation
        reward_transaction = Tx(tx_recipient=user, tx_amount=self.MINING_REWARD)
        temp_transactions.append(reward_transaction)
        proof = cu.calculate_proof(temp_transactions, hashed_block)
        block_to_mine = Block(previous_hash=hashed_block, index=len(self.chain), transactions=temp_transactions,
                              proof=proof)
        self.__chain.append(block_to_mine)
        self.__open_transactions.clear()
        return cu.save_blockchain(self)

    def output_blockchain(self):

        for index, block in enumerate(self.chain):
            print('-' * 20)
            print(f'Outputting block {index}:')
            print(block)
            if index == (len(self.chain) - 1):
                print('-' * 20)

    def load_chain(self, loaded_chain, loaded_transactions):
        self.__chain = cp.deepcopy(loaded_chain)
        self.__open_transactions = cp.deepcopy(loaded_transactions)
