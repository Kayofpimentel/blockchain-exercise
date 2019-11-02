from Crypto.Signature import PKCS1_v1_5 as CSign
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import Crypto.Random as CRandom
import binascii

from wallet import Wallet


def load_wallet(path):
    """
    Method to load keys of a user from file on the disk.
    :param path: The path of the file
    :return: Returns a new wallet with the loaded keys. If the file can't be found, returns None.
    """
    try:
        print('Loading keys from user file.')
        with open(path, mode='r') as wallet_file:
            keys = wallet_file.readlines()
            public_key = keys[0][:-1]
            private_key = keys[1]
        return Wallet(private_key, public_key)

    except (IOError, IndexError):
        return None


def save_keys(new_wallet, path):
    try:
        with open(path, mode='w') as wallet_file:
            wallet_file.write(new_wallet.public_key)
            wallet_file.write('\n')
            wallet_file.write(new_wallet.private_key)
        return True

    except IOError:
        return False


def generate_keys():
    private_key = RSA.generate(1024, CRandom.new().read)
    public_key = generate_public_key(private_key)
    read_private_key = binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii')
    read_public_key = binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')
    return read_private_key, read_public_key


def generate_public_key(private_key):
    public_key = private_key.publickey()
    return public_key


def sign_transaction(wallet, recipient, amount):
    signer = CSign.new(RSA.importKey(binascii.unhexlify(wallet.private_key)))
    sender = wallet.public_key
    tx_hash = SHA256.new(f'{sender}{recipient}{amount}'.encode('utf8'))
    user_signature = signer.sign(tx_hash)
    return binascii.hexlify(user_signature).decode('ascii')


def get_public_key(path):
    wallet = load_wallet(path)
    return wallet.public_key if wallet is not None else None


def create_new_wallet():
    return Wallet(*generate_keys())
