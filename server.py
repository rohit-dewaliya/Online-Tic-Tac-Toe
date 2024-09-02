import random
import socket
import select
import pickle
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

        except socket.error as error:
            print("Error occurred during socket creation: ", str(error))

    def binding_socket(self):
        try:
            self.server_socket.bind((self.HOST, self.PORT))
            print('Socket is bound to IP : ' + self.HOST + " | PORT : " + str(self.PORT))
            self.server_socket.listen(10)
        except socket.error as error:
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
        except:
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
                    print(f"Connection accepted from {client_address}")

                    if len(self.players) == 1:
                        data = {"connection": "Waiting for another player to connect."}
                        print(data)
                        self.send_message(self.players[0], data)
                    elif len(self.players) == 2:
                        new_game = PlayerController(self.players[0], self.players[1])
                        self.game_pair.append(new_game)
                        turn = random.choice([True, False])
                        turn = "O"
                        data = {"action": "Player connected", "turn": turn, "choice": "O" if turn else "X"}
                        self.send_message(new_game.player1, data)
                        data = {"action": "Player connected", "turn": turn, "choice": "X" if turn else "O"}
                        self.send_message(new_game.player2, data)
                        print("new game begins")
                        self.players = []

                else:
                    message = self.receive_message(notified_socket)
                    if message:
                        recv = None
                        for game in self.game_pair:
                            if game.player1 == notified_socket:
                                recv = game.player2
                                break
                            elif game.player2 == notified_socket:
                                recv = game.player1
                                break

                        if recv:
                            data = pickle.loads(message['data'])
                            self.send_message(recv, data)

                    if not message:
                        print(
                            f"Closed connection from {self.clients[notified_socket][0]} : {self.clients[notified_socket][1]}")
                        self.socket_list.remove(notified_socket)
                        del self.clients[notified_socket]
                        continue

        for notified_socket in socket_exceptions:
            self.socket_list.remove(notified_socket)
            del self.clients[notified_socket]

# Initialize and start the server
server = Server()
server.binding_socket()
server.start_server()
