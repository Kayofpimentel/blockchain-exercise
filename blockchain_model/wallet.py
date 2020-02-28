import binascii

import Cryptodome.Random as CRandom
from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import PKCS1_v1_5 as CSign


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

    def generate_keys(self):
        private_key = RSA.generate(1024, CRandom.new().read)
        public_key = private_key.publickey()
        read_private_key = binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii')
        read_public_key = binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')
        self.__private_key = read_private_key
        self.__public_key = read_public_key

    def sign_transaction(self, recipient, amount):
        signer = CSign.new(RSA.importKey(binascii.unhexlify(self.__private_key)))
        sender = self.public_key
        tx_hash = SHA256.new(f'{sender}{recipient}{amount}'.encode('utf8'))
        user_signature = signer.sign(tx_hash)
        return binascii.hexlify(user_signature).decode('ascii')

    def reset_keys(self):
        self.__private_key = None
        self.__public_key = None
