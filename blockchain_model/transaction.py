import time as tm


class Transaction:

    def __init__(self, tx_sender, tx_recipient, tx_amount, tx_signature, tx_time=None):
        self.__recipient = tx_recipient
        self.__sender = tx_sender
        self.__amount = tx_amount
        self.__signature = tx_signature
        self.__timestamp = tx_time if tx_time is not None else tm.time()

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
