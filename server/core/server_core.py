import pickle
import sqlite3
from logging import INFO, Formatter, StreamHandler, getLogger
from socket import socket

from general.enums import RequestData
from server.endpoints.mapping import EndpointMapper
from server.Server_socket import Socket


logger = getLogger(__name__)
logger.setLevel(INFO)
logger.addHandler(StreamHandler())
logger.handlers[0].setFormatter(
    Formatter('%(asctime)s - (%(name)s) - [%(levelname)s] - %(message)s')
)


class Server(Socket):
    def __init__(self, db_path):
        super(Server, self).__init__()
        self.users = []  # сокеты клиентов
        self.addresses = []  # ip, port клиентов
        self.teams_count = 0  # количество команд
        self.timer_secs = 0  # timer стоит на нуле
        self.current_task = 1  # Текущий номер задания (по умолчанию 1)
        self.admin_sock = []
        self.cur = None
        self.con = None
        self.db_path = db_path

        # Массивы сокетов каждой команды
        self.socket_team1 = []
        self.socket_team2 = []
        self.socket_team3 = []
        self.socket_team4 = []
        self.socket_team5 = []
        self.socket_team6 = []

        self.team1_queue = 0
        self.team2_queue = 0
        self.team3_queue = 0
        self.team4_queue = 0
        self.team5_queue = 0
        self.team6_queue = 0

        self.team1_current_turn = 0
        self.team2_current_turn = 0
        self.team3_current_turn = 0
        self.team4_current_turn = 0
        self.team5_current_turn = 0
        self.team6_current_turn = 0

    def set_up(self):
        self.socket.bind(('127.0.0.1', 9669))
        self.socket.listen(50)
        self.socket.setblocking(False)
        self.con = sqlite3.connect(self.db_path)
        self.cur = self.con.cursor()
        logger.info('Server is running and listening!')
        self.cur.execute('SELECT COUNT(*) FROM teams')
        self.teams_count = self.cur.fetchall()[0][
            0
        ]  # запись количества существующих команд
        self.cur.execute('DELETE FROM users')
        self.con.commit()

    def start(self):
        self.main_loop.run_until_complete(self.main())

    async def listen_socket(self, listened_socket=None):
        if not listened_socket:
            return 0
        while True:
            try:
                logger.info('Listening socket....')
                data = await self.main_loop.sock_recv(listened_socket, 4096)
                data_obj: RequestData = pickle.loads(data)
                logger.info(f'RequestData = {data_obj}')
                await self.distributor(data_obj, listened_socket)
            except pickle.UnpicklingError as exc:
                logger.info(f'UnpicklingError caught: {exc}')
                continue
            except (EOFError, ConnectionResetError):
                logger.info('Connection Reset Error')
                if listened_socket in self.admin_sock:
                    self.admin_sock.remove(listened_socket)
                addr = self.addresses[self.users.index(listened_socket)]
                self.addresses.remove(addr)
                self.users.remove(listened_socket)
                logger.info('User disconnected!')

                # _________________________________________________________________________________________________
                ip, port = addr[0], addr[1]
                self.cur.execute(
                    'SELECT team FROM users WHERE ip=? AND port=?', (ip, port)
                )
                team_index = self.cur.fetchall()[0][0]  # Ищется индекс команды
                self.cur.execute(
                    'DELETE FROM users WHERE ip=? AND port=?',
                    (str(addr[0]), str(addr[1])),
                )
                self.con.commit()
                if not team_index:
                    return 0
                socket_team_by_id = eval(f'self.socket_team{team_index}')
                socket_team_by_id.remove(listened_socket)
                return 0

    async def accept_sockets(self):
        while True:
            user_socket, address = await self.main_loop.sock_accept(
                self.socket
            )

            self.users.append(user_socket)
            self.addresses.append(address)
            self.cur.execute(
                'INSERT INTO users VALUES (?, ?, NULL, NULL)',
                (str(address[0]), str(address[1])),
            )
            self.con.commit()
            self.main_loop.create_task(self.listen_socket(user_socket))

    async def main(self):
        await self.main_loop.create_task(self.accept_sockets())

    async def distributor(self, data_object: RequestData, sock: socket):
        response, send_to = EndpointMapper[data_object.endpoint](
            data_object.data, sock, self.con, self.cur, self
        )
        logger.info(response)
        response_obj = pickle.dumps(response)
        for sender in send_to:
            try:
                sender.send(response_obj)
                # await self.main_loop.sock_sendall(sender, response_obj)
            except Exception as exc:
                logger.info(
                    f'Exception caught at sock sendall from server: {exc}'
                )
