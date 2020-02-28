import requests


# TODO check with other nodes if the node is active
# TODO Refactor for code reuse

def broadcast(bc_info, operation):
    responses = []
    for node in bc_info['nodes_info']['peer_nodes']:
        url = f'http://127.0.0.1:{node}{operation}'
        try:
            responses.append(requests.post(url=url, json=bc_info))
        except ConnectionError:
            continue
    return responses


def broadcast_transaction(**bc_info):
    operation = '/bc-tx'
    broadcast(bc_info, operation)
    return None


def broadcast_block(**bc_info):
    incorrect_peers = set()
    operation = '/bc-block'
    responses = broadcast(bc_info, operation)
    for each_r in responses:
        print(each_r)
        info = each_r.json()
        if each_r.status_code == 202:
            incorrect_peers.add(info['self_id'])
    return incorrect_peers


def broadcast_chain(**bc_info):
    for node in bc_info['nodes_info']['peer_nodes']:
        bc_info['nodes_info']['peer_nodes'].remove(node)
        url = f'http://127.0.0.1:{node}/bc-block'
        print(bc_info)
        try:
            request_response = requests.post(url=url, json=bc_info)
            status = request_response.status_code
            if status == 500:
                raise ConnectionError
        except ConnectionError:
            continue
    return None

