import blockchain_core.node as node

if __name__ == '__main__':
    if not node.start_new_node(input('Insert user login: ')):
        print('Program failed to start.')
    print('Program finished.')

