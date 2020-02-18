import requests


def broadcast_transaction(**bc_info):
    for node in bc_info['nodes_info']['peer_nodes']:
        bc_info['nodes_info']['peer_nodes'].remove(node)
        url = f'http://127.0.0.1:{node}/bc-tx'
        print(bc_info)
        try:
            request_response = requests.post(url=url, json=bc_info)
            status = request_response.status_code
            if status == 400 or status == 500:
                print('Transaction declined.')
                return False
        except ConnectionError:
            continue
    return True
