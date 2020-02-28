import os


def load_keys(path):
    """
    Method to load keys of a user from file on the disk.
    :param path: The path of the file
    :return: Returns a new user with the loaded keys. If the file can't be found, returns None.
    """
    try:
        print('Loading keys from user file.')
        with open(path, mode='r') as wallet_file:
            keys = wallet_file.readlines()
            public_key = keys[0][:-1]
            private_key = keys[1]
        return private_key, public_key

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


def check_wallet(path):
    return os.path.isfile(path)
