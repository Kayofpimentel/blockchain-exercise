import time as tm


class Transaction:

    def __init__(self, tx_recipient, tx_sender=None, tx_amount=0, tx_time=None, tx_signature=None):
        self.__recipient = tx_recipient
        self.__sender = tx_sender if tx_sender is not None else 'System0'
        self.__amount = tx_amount
        self.__timestamp = tx_time if tx_time is not None else tm.time()
        self.__signature = tx_signature if tx_signature is not None else 'MINING'

    @property
    def sender(self):
        return self.__sender

    @property
    def recipient(self):
        return self.__recipient

    @property
    def signature(self):
        return self.__signature

    @property
    def amount(self):
        return self.__amount

    @property
    def timestamp(self):
        return self.__timestamp
