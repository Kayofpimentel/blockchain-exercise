from argparse import ArgumentParser
from blockchain_view.node_command_view import NodeCommandView
from blockchain_network import node_http_requests as nhr

new_node_view = None


def web_node(configs):
    return nhr.start_node_server(configs)


def local_node(configs):
    global new_node_view
    new_node_view = NodeCommandView()
    if not new_node_view.connect_node(configs):
        print('Error during program. Closing node.')


modes = {'web': web_node, 'local': local_node}
parser = ArgumentParser()
parser.add_argument('-m', '--mode', default='web')
parser.add_argument('-p', '--port', default='8000')
parser.add_argument('-u', '--user', default='Kayo')
parser.add_argument('-d', '--dir', default='./resources/')
args = vars(parser.parse_args())
print(args)

try:
    modes[args['mode']](args)

finally:
    print('Program finished.')
