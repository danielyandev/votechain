from src.helpers import get_port
import src.app as app


if __name__ == '__main__':
    app.app.run('127.0.0.1', port=get_port())
