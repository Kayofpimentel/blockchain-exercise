import requests


# TODO check with other nodes if the node is active
def broadcast_transaction(**bc_info):
    sent = False
    for node in bc_info['nodes_info']['peer_nodes']:
        url = f'http://127.0.0.1:{node}/bc-tx'
        print(bc_info)
        try:
            request_response = requests.post(url=url, json=bc_info)
            status = request_response.status_code
            if status == 400 or status == 500:
                raise ConnectionError
            sent = True
        except ConnectionError:
            continue
    return sent


def broadcast_chain(**bc_info):
    sent = False
    for node in bc_info['nodes_info']['peer_nodes']:
        bc_info['nodes_info']['peer_nodes'].remove(node)
        url = f'http://127.0.0.1:{node}/bc-block'
        print(bc_info)
        try:
            request_response = requests.post(url=url, json=bc_info)
            status = request_response.status_code
            if status == 400 or status == 500:
                raise ConnectionError
            sent = True
        except ConnectionError:
            continue
    return sent
