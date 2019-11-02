class Wallet:

    def __init__(self, private_key=None, public_key=None):
        # Setting keys for operations in the node.
        self.__public_key = public_key
        self.__private_key = private_key

    @property
    def public_key(self):
        return self.__public_key

    @property
    def private_key(self):
        return self.__private_key

    def reset_keys(self):
        self.__private_key = None
        self.__public_key = None
