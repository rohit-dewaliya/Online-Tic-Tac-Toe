import socket
import random
import pickle
from threading import Thread


class Client:
    def __init__(self, host='localhost', port=1234):
        self.header_length = 10
        self.ip = host
        self.port = port
        self.username = random.randint(1, 10)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.ip, self.port))
        self.client_socket.setblocking(True)

    def send_message(self, message):
        message = {'user': self.username, 'message': message}
        message = pickle.dumps(message)
        message_header = f"{len(message):<{self.header_length}}".encode('utf-8')
        self.client_socket.send(message_header + message)

    def receive_messages(self):
        try:
            message_header = self.client_socket.recv(self.header_length)
            if not len(message_header):
                return False

            message_length = int(message_header.decode("utf-8").strip())
            message_data = b""
            while len(message_data) < message_length:
                packet = self.client_socket.recv(message_length - len(message_data))
                if not packet:
                    break
                message_data += packet

            return pickle.loads(message_data)
        except Exception as e:
            print(f"Error receiving message: {str(e)}")
            return None
