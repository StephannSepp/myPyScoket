import socket
import threading
from typing import Generator
from queue import Queue

class SuperDuperCoolSocket:
    def __init__(self, ip: str, port: int) -> None:
        """
        :param ip: This is the IP address which the socket will be bound to.
        :param port: This is the port which the socket will be bound to.
        """
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client = []
        self.message_pack = {}

    class Decorator:
        """ A simple decorator will make the function threaded. """
        @classmethod
        def run_in_thread(cls, func):
            def wrapper(*args):
                worker = threading.Thread(target=func, args=args)
                worker.start()
            return wrapper

    def start(self) -> None:
        """ This will start the socket. """
        try:
            self.sock.bind((self.ip, self.port))
        except socket.error as err:
            print(err)
        self.sock.listen(5)
        print("Start listening..")
        self._on_connect()

    @Decorator.run_in_thread
    def _on_connect(self) -> None:
        """ Do not call this.

        When a client is connecting,
        their socket object and the address will be saved in self.client.
        """
        while True:
            try:
                conn, addr = self.sock.accept()
                self.client.append((conn, addr))
                print(f"{':'.join(map(str, addr))} has connected.")
                self._receiver(conn, addr)
            except socket.error as err:
                print(err)
                break

    @Decorator.run_in_thread
    def _receiver(self, conn: socket.socket, addr: tuple) -> None:
        """ Do not call this.

        Handling the data receiving and client disconnection.
        All the data will be saved into the Queue, which is in the self.message_pack dict.
        When a client disconnect, they will be removed from self.client.

        :param conn: A socket object usable to send and receive data.
        :param addr: The address bound to the socket of the client end.
        """
        self.message_pack = {addr: Queue(maxsize=10)}
        while True:
            try:
                m = conn.recv(4096).decode()
                if self.message_pack[addr].full():
                    self.message_pack[addr].get(0)
                self.message_pack[addr].put(m)
                print(f"{':'.join(map(str, addr))}: {m}")
            except ConnectionResetError:
                print(f"{':'.join(map(str, addr))} has disconnected.")
                print(f"Messages from {':'.join(map(str, addr))}: {', '.join(self.message_pack[addr].queue)}")
                self.client.remove((conn, addr))
                break

    def close(self) -> None:
        """ This will disconnect all the clients
            and close the socket.
        """
        for conn, addr in self.client:
            conn.close()
            self.client.remove((conn, addr))
        self.sock.close()

    def fetch_message(self, ip: str, port: int) -> Generator:
        """ Fetch a message from a specific address.

        :param ip: The IP which the message is sent from.
        :param port: The port which the message is sent from.

        :return m: A generator object contains the message.
        """
        port = int(port)
        for m in self.message_pack[(ip, port)].queue:
            yield m


if __name__ == "__main__":
    s = SuperDuperCoolSocket("127.0.0.1", 5000)
    s.start()
