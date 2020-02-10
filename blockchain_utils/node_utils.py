import json


# def save_nodes(nodes, resources_path=None):
#     """
#     Method to save the data from recent transactions, mined blocks and connected nodes.
#     :param resources_path:
#     :param nodes:
#     :return if the operation was successful:
#     """
#     path = resources_path if resources_path is not None else '../resources/'
#     nodes_path = f'{path}network_nodes.txt'
#     try:
#         with open(nodes_path, mode='w') as nodes_file:
#             nodes_file.write(json.dumps(nodes))
#         return True
#
#     except IOError:
#         print(f'Could not save chain on {resources_path}. The error is the following {IOError}')
#         raise SystemExit(0)
#
#
# def load_nodes(resources_path=None):
#     """
#     Method to load all the data from the chain when the program initiates.
#     :param resources_path: The path
#     :return the loaded blockchain
#     """
#     path = resources_path if resources_path is not None else '../resources/'
#     nodes_path = f'{path}network_nodes.txt'
#     try:
#         with open(nodes_path, mode='r') as nodes_file:
#             network_info = nodes_file.readlines()
#             network_nodes = json.loads(network_info[0])
#         return network_nodes
#     except (IOError, IndexError):
#         return None
#
#
# def update_nodes(nodes_to_add, resources_path=None):
#     """
#     Method to save the data from recent transactions, mined blocks and connected nodes.
#     :param resources_path:
#     :param nodes_to_add:
#     :return if the operation was successful:
#     """
#     path = resources_path if resources_path is not None else '../resources/'
#     nodes_path = f'{path}network_nodes.txt'
#     try:
#         with open(nodes_path, mode='a+') as nodes_file:
#             nodes_file.seek(0, 0)
#             nodes_info = nodes_file.readlines()
#             nodes_in_file = json.loads(nodes_info)
#             nodes_to_add.update(nodes_in_file)
#             nodes_file.seek(0, 0)
#             nodes_file.write(json.dumps(nodes_to_add))
#         return True
#
#     except IOError:
#         print(f'Could not update nodes on {resources_path}. The error is the following {IOError}')
#         return False
