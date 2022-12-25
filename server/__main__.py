from logging import INFO, Formatter, StreamHandler, getLogger

from server.core.server_core import Server


logger = getLogger(__name__)
logger.setLevel(INFO)
logger.addHandler(StreamHandler())
logger.handlers[0].setFormatter(
    Formatter('%(asctime)s - (%(name)s) - [%(levelname)s] - %(message)s')
)


if __name__ == '__main__':
    logger.info('Server is starting!')
    server = Server(db_path='main_database.db')
    server.set_up()
    server.start()
    logger.info('Server is stopped!')
