import hashlib
import json
import requests

from urllib.parse import urlparse
from src.block import Block
from src.vote import Vote


class Blockchain:
    def __init__(self):
        self.difficulty = 4
        self.difficulty_char = "0"

        self.chain = []
        self.pending_votes = []
        self.nodes = set()
        self.create_genesis_block()

    def create_genesis_block(self):
        """
        Create genesis block
        :param self:
        :return: void
        """
        self.new_block(proof=100, previous_hash=1)

    def new_block(self, proof, previous_hash=None):
        """
        Add block to blockchain
        :param proof:
        :param previous_hash:
        """
        block = Block(self, proof, previous_hash).__dict__
        self.chain.append(block)
        self.pending_votes = []
        return block

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Create block SHA-256 hash

        :param block: Block
        :return: <str>
        """

        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof
        :param last_proof: <int>
        :return: <int>
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    def valid_proof(self, last_proof, proof):
        """
        Validates the Proof: Does hash(last_proof, proof) contain 4 leading zeroes?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        print(guess_hash)
        return guess_hash[:self.difficulty] == self.difficulty_char * self.difficulty

    def new_vote(self, sender, recipient):
        """
        Creates a new transaction to go into the next mined Block
        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :return: <int> The index of the Block that will hold this transaction
        """
        if not self.voted(sender):
            vote = Vote(sender, recipient).__dict__
            self.pending_votes.append(vote)
            response = {
                'success': True,
                'message': vote['id']
            }
        else:
            response = {
                'success': False,
                'message': 'Already voted'
            }
        return response

    def voted(self, account):
        for vote in self.pending_votes:
            if vote['sender'] == account:
                return True

        for block in self.chain:
            for vote in block['votes']:
                if vote['sender'] == account:
                    return True
        return False

    def find_vote(self, id):
        tx = None
        tx_block = None
        for vote in self.pending_votes:
            if vote['id'] == id:
                tx = vote

        if not tx:
            for block in self.chain:
                for vote in block['votes']:
                    if vote['id'] == id:
                        tx = vote
                        tx_block = block

        return self.vote_info(tx, tx_block)

    def vote_info(self, tx=None, block=None):
        if tx is None:
            return tx
        vote = tx.copy()
        vote['confirmations'] = Vote.confirmations(self.chain, block)
        vote['block'] = Vote.block(block)
        return vote

    def votes_count(self, accounts):
        data = {}
        for account in accounts:
            data[account] = 0
        for block in self.chain:
            for vote in block['votes']:
                account = vote['recipient']
                if account in accounts:
                    data[account] += 1

        return data

    def mine(self):
        """
        Mine new block
        """

        if not self.pending_votes:
            response = {
                'message': 'No pending votes, no need to mine new block',
            }
        else:
            last_proof = self.last_block['proof']
            proof = self.proof_of_work(last_proof)

            # crete new block
            previous_hash = self.hash(self.last_block)
            block = self.new_block(proof, previous_hash)

            response = {
                'message': 'New Block Forged',
                'index': block['index'],
                'votes': block['votes'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
            }
        return response

    def register_node(self, address):
        """
        Add a new node to the list of nodes
        :param address: <str> Address of node. Eg. 'http://192.168.0.5:5000'
        :return: None
        """

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid
        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        This is our Consensus Algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        :return: <bool> True if our chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False
