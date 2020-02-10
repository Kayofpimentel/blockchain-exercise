from argparse import ArgumentParser
from blockchain_view.node_command_view import NodeCommandView
# from blockchain_view.node_web_view import NodeWebView

parser = ArgumentParser()
parser.add_argument('-m', '--mode', default='web')
parser.add_argument('-p', '--port', default='8000')
parser.add_argument('-u', '--user', default='Kayo')
parser.add_argument('-d', '--dir', default='./resources/')
args = vars(parser.parse_args())
print(args)
try:
    # if mode == 'web':
    #     new_view = NodeWebView()
    # else:
    #     new_view = NodeCommandView()
    new_view = NodeCommandView()
    if not new_view.connect_node(args):
        print('Error during program. Closing node.')
finally:
    print('Program finished.')
