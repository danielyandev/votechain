from flask import Flask, jsonify, request
from src.blockchain import Blockchain

app = Flask(__name__)

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    response = blockchain.mine()
    return jsonify(response), 200


@app.route('/votes/new', methods=['POST'])
def new_vote():
    values = request.get_json()

    required = ['sender', 'recipient']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # create new vote
    response = blockchain.new_vote(values['sender'], values['recipient'])
    status = 201 if response['success'] else 400
    return jsonify(response), status


@app.route('/votes/count', methods=['POST'])
def votes_count():
    values = request.get_json()
    if 'accounts' not in values or not values['accounts']:
        return 'Missing accounts', 400
    response = blockchain.votes_count(values['accounts'])
    return jsonify(response), 201


@app.route('/votes/<id>', methods=['GET'])
def vote(id):
    response = blockchain.find_vote(id)
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200
