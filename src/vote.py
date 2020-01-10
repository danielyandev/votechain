import sys
from time import time
from uuid import uuid4


class Vote:
    def __init__(self, sender, recipient):
        self.sender = sender
        self.recipient = recipient
        self.id = str(uuid4()).replace('-', '')
        self.timestamp = time()

    @staticmethod
    def confirmations(chain, block):
        if not block:
            return 0
        return len(chain) - block['index']

    @staticmethod
    def block(block):
        return block['index'] if block else 'Mempool'
