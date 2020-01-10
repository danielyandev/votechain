from time import time


class Block:
    def __init__(self, blockchain, proof, previous_hash=None):
        self.index = len(blockchain.chain)
        self.timestamp = time()
        self.votes = blockchain.pending_votes
        self.proof = proof
        self.previous_hash = previous_hash or blockchain.hash(blockchain.chain[-1])
