from node import Node

new_node = Node(input('Insert user login: '))
if not new_node.start_operations():
    print('The chain is invalid.')
print('Program closed!')


