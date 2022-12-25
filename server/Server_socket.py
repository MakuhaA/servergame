import asyncio
import socket


class Socket:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.main_loop = asyncio.get_event_loop()

    async def listen_socket(self, listened_socket=None):
        raise NotImplementedError()

    async def main(self):
        raise NotImplementedError()

    async def distributor(self, data_object, listened_socket):
        raise NotImplementedError()

    async def accept_sockets(self):
        raise NotImplementedError()

    def start(self):
        raise NotImplementedError()

    def set_up(self):
        raise NotImplementedError()
