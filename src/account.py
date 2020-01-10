from uuid import uuid4


class Account:
    def __init__(self):
        pass

    @property
    def address(self):
        return str(uuid4()).replace('-', '')
