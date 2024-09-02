import random
import socket
import select
import pickle
import logging
from datetime import datetime
from player_controller import PlayerController


class Server:
    def __init__(self, host="localhost", port=1234):
        try:
            self.HEADER_LENGTH = 10
            self.HOST = host
            self.PORT = port
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_list = [self.server_socket]
            self.clients = {}
            self.run_server = True
            self.players = []
            self.game_pair = []

            # Initialize logging
            logging.basicConfig(filename='server_log.log', level=logging.INFO,
                                format='%(asctime)s - %(levelname)s - %(message)s')

        except socket.error as error:
            logging.error(f"Error occurred during socket creation: {error}")
            print("Error occurred during socket creation: ", str(error))

    def binding_socket(self):
        try:
            self.server_socket.bind((self.HOST, self.PORT))
            logging.info(f'Socket bound to IP: {self.HOST} | PORT: {self.PORT}')
            print('Socket is bound to IP : ' + self.HOST + " | PORT : " + str(self.PORT))
            self.server_socket.listen(10)
        except socket.error as error:
            logging.error(f"Error occurred during binding: {error}")
            print("Error occurred during binding: ", str(error))
            self.binding_socket()

    def receive_message(self, client_socket):
        try:
            message_header = client_socket.recv(self.HEADER_LENGTH)

            if not len(message_header):
                return False

            message_length = int(message_header.decode("utf-8").strip())
            return {"header": message_header, "data": client_socket.recv(message_length)}
        except:
            return False

    def send_message(self, client_socket, message):
        try:
            message = pickle.dumps(message)
            message_header = f"{len(message):<{self.HEADER_LENGTH}}".encode('utf-8')
            client_socket.send(message_header + message)
            logging.info(f"Sent message to {client_socket.getpeername()}: {message}")
        except:
            logging.error(f"Failed to send a message to {client_socket.getpeername()}")
            print(f"Failed to send a message to {client_socket.getpeername()}")

    def start_server(self):
        while self.run_server:
            read_sockets, _, socket_exceptions = select.select(self.socket_list, [], self.socket_list)

            for notified_socket in read_sockets:
                if notified_socket == self.server_socket:
                    client_socket, client_address = self.server_socket.accept()
                    self.players.append(client_socket)
                    self.socket_list.append(client_socket)
                    self.clients[client_socket] = client_address
                    logging.info(f"New connection accepted from {client_address}")
                    print(f"Connection accepted from {client_address}")

                    if len(self.players) == 1:
                        data = {"connection": "Waiting for another player to connect."}
                        self.send_message(self.players[0], data)
                    elif len(self.players) == 2:
                        self.game_pair.append([self.players[0], self.players[1]])
                        turn = random.choice([True, False])
                        turns = "O"
                        data = {"action": "Player connected", "turn": turns, "choice": "O" if turn else "X"}
                        self.send_message(self.game_pair[-1][0], data)
                        data = {"action": "Player connected", "turn": turns, "choice": "X" if turn else "O"}
                        self.send_message(self.game_pair[-1][1], data)
                        self.players = []

                else:
                    message = self.receive_message(notified_socket)
                    if message:
                        data = pickle.loads(message['data'])
                        recv = None
                        game = []
                        for game in self.game_pair:
                            if notified_socket in game:
                                recv = game[1] if notified_socket == game[0] else game[0]
                                self.send_message(recv, data)
                                logging.info(f"Message from {self.clients[notified_socket]} to {self.clients[recv]}: {data}")
                                break
                        if data['message']['complete']:
                            self.game_pair.remove(game)

                    if not message:
                        logging.info(f"Closed connection from {self.clients[notified_socket][0]} : {self.clients[notified_socket][1]}")
                        print(f"Closed connection from {self.clients[notified_socket][0]} : {self.clients[notified_socket][1]}")
                        self.socket_list.remove(notified_socket)
                        del self.clients[notified_socket]
                        continue

        for notified_socket in socket_exceptions:
            self.socket_list.remove(notified_socket)
            del self.clients[notified_socket]
            logging.error(f"Socket exception: {notified_socket}")


server = Server()
server.binding_socket()
server.start_server()
