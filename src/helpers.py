import sys
from src.exceptions import InvalidPort


def get_port():
    """
    Parse --port option from command line
    :return:
    """
    port = 5000
    for arg in sys.argv:
        options = arg.split('=')
        if options[0] == '--port':
            try:
                port = options[1]
                if not port.isdigit():
                    port = None
            except IndexError:
                port = None

    if not port:
        raise InvalidPort('Invalid port, check configurations or specify with --port option')
    return port
