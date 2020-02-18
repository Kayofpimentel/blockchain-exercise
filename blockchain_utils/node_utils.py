import json


def load_nodes(resources_path=None):
    """
    Method to load all the data from the chain when the program initiates.
    :param resources_path: The path
    :return the loaded chain_blocks
    """
    path = resources_path if resources_path is not None else '../resources/'
    nodes_path = f'{path}network_nodes.txt'
    try:
        with open(nodes_path, mode='r') as nodes_file:
            network_info = nodes_file.readlines()
            network_nodes = json.loads(network_info[0])
        return set(network_nodes)
    except (IOError, IndexError):
        return set()


# TODO Separate method into save and update
def update_nodes(nodes_to_add, resources_path=None):
    """
    Method to save the data from recent transactions, mined blocks and connected nodes.
    :param resources_path:
    :param nodes_to_add:
    :return if the operation was successful:
    """
    path = resources_path if resources_path is not None else '../resources/'
    nodes_path = f'{path}network_nodes.txt'
    try:
        with open(nodes_path, mode='w') as nodes_file:
            nodes_file.truncate(0)
            nodes_file.write(json.dumps(list(nodes_to_add)))
        return True

    except (IOError, TypeError) as the_error:
        print(f'Could not update nodes on {resources_path}. The error is the following \n{str(the_error)}')
        return False
