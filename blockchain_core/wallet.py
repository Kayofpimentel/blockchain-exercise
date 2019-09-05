from Crypto.Signature import PKCS1_v1_5 as CSign
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import Crypto.Random as CRandom
import binascii


class Wallet:

    def __init__(self, user_name=None, private_key=None, create_key=True):
        # Setting keys for operations in the node.
        self.__public_key = None
        self.__private_key = private_key
        self.__user = user_name if user_name is not None else 'System0'
        if self.__private_key is None and create_key:
            self.load_keys(create_key)

    @property
    def public_key(self):
        return self.__public_key

    def load_keys(self, user, create_key=True):
        user = user
        file_name = f'../resources/{user}.txt'
        try:
            print('Loading keys from user file.')
            with open(file_name, mode='r') as wallet_file:
                keys = wallet_file.readlines()
                self.__public_key = keys[0][:-1]
                self.__private_key = keys[1]
            self.__user = user
            return 'Keys loaded.'

        except (IOError, IndexError):
            if create_key:
                if self.create_keys(user):
                    return 'Could not load keys, new keys created.'
                else:
                    return 'Error": could not save new keys.'
            else:
                return 'Error: could not load keys, user not found.'

    def create_keys(self, user):
        if self.__private_key is None:
            self.__private_key, self.__public_key = self.generate_keys()
        else:
            self.__public_key = binascii.hexlify(RSA.importKey(binascii.unhexlify(self.__private_key))
                                                 .publickey().exportKey(format='DER')).decode(
                'ascii')
        print('Saving new keys to user file.')
        return self.save_keys(user)

    def save_keys(self, user):
        user = user
        file_name = f'../resources/{user}.txt'
        try:
            with open(file_name, mode='w') as wallet_file:
                wallet_file.write(self.public_key)
                wallet_file.write('\n')
                wallet_file.write(self.__private_key)
            self.__user = user
            return True

        except IOError:
            print('Could not save new keys')
            return False

    def generate_keys(self):
        private_key = RSA.generate(1024, CRandom.new().read)
        public_key = self.generate_public_key(private_key)
        return (binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'),
                public_key)

    @staticmethod
    def generate_public_key(private_key):
        public_key = private_key.publickey()
        return binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')

    def reset_keys(self):
        self.__private_key = None
        self.__public_key = None

    def sign_transaction(self, sender, recipient, amount):
        signer = CSign.new(RSA.importKey(binascii.unhexlify(self.__private_key)))
        tx_hash = SHA256.new(f'{sender}{recipient}{amount}'.encode('utf8'))
        user_signature = signer.sign(tx_hash)
        return binascii.hexlify(user_signature).decode('ascii')
