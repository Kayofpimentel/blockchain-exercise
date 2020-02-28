from flask import Flask
from flask_cors import CORS

from blockchain_view.node_view import NodeView


class NodeWebView(NodeView):

    def __init__(self):
        super().__init__()
        self.__web_app = Flask(__name__)
        CORS(self.__web_app)

    def run_node(self):
        print('Node started, application online.')
        port_to_run = self.node_connection.node
        self.__web_app.run(host='127.0.0.1', port=port_to_run)

    @property
    def web_app(self):
        return self.__web_app
