import socket
import threading
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

    def _on_connect(self) -> None:
        """ Do not call this.

        When a client is connect,
        their socket object and the address will be saved in self.client.
        """
        while True:
            conn, addr = self.sock.accept()
            self.client.append((conn, addr))
            print(f"{':'.join(map(str, addr))} has connected.")
            self._receiver(conn, addr)

    @Decorator.run_in_thread
    def _receiver(self, conn: socket.socket, addr: tuple) -> None:
        """ Do not call this.

        Handling the data receiving and clent disconnection.
        All the data will be saved into the Queue, which is in the recv_data dict.
        When a client disconnect, they will be removed form self.client.

        :param conn: A socket object usable to send and receive data.
        :param addr: The address bound to the socket of the client end.
        """
        recv_data = {addr: Queue(maxsize=10)}
        while True:
            try:
                response = conn.recv(4096).decode("gbk")
                if recv_data[addr].full():
                    recv_data[addr].get(0)
                recv_data[addr].put(response)
                print(f"{':'.join(map(str, addr))}: {response}")
            except ConnectionResetError:
                print(f"{':'.join(map(str, addr))} has disconnected.")
                print(f"Messages from {':'.join(map(str, addr))}: {', '.join(recv_data[addr].queue)}")
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


if __name__ == "__main__":
    s = SuperDuperCoolSocket("127.0.0.1", 5000)
    s.start()
