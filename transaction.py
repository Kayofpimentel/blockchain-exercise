import time as tm
from datetime import datetime as dt


class Transaction:

    def __init__(self, tx_sender='MINING', tx_recipient=None, tx_amount=0, tx_time=None):
        self.__sender = tx_sender
        self.__recipient = tx_recipient
        self.__amount = tx_amount
        self.__timestamp = tx_time if tx_time is not None else tm.time()

    @property
    def sender(self):
        return self.__sender

    @property
    def recipient(self):
        return self.__recipient

    @property
    def amount(self):
        return self.__amount

    @property
    def date(self):
        return dt.fromtimestamp(self.__timestamp)
