import queue
import threading
import webbrowser
import pygame
from pygame.locals import *
from client import Client
from data.scripts.text import font
from data.scripts.image_functions import import_image, scale_image_size

pygame.init()

class GameScreen:
    def __init__(self, width=470, height=470):
        self.SCREEN_SIZE = [width, height]
        self.CENTER = [width // 2, height // 2]
        self.window = pygame.display.set_mode(self.SCREEN_SIZE, 0, 32)
        pygame.display.set_caption("Tic Tac Toe")

        self.tile = pygame.image.load("data/images/tile.png").convert()
        self.name_tile = self.tile.copy()
        self.tile.set_alpha(15)

        self.tile_hover = pygame.image.load("data/images/tile.png").convert()
        self.tile_hover.set_alpha(20)

        self.name_tile = pygame.transform.scale(self.name_tile, [120, 50])
        self.name_tile.set_alpha(30)

        self.start_button = import_image('start_button.png', (0, 0, 0))
        self.start_button_hover = import_image('start_button_hover.png', (0, 0, 0))

        self.exit_button = import_image('exit.png', (0, 0, 0))
        self.exit_button_hover = import_image('exit_hover.png', (0, 0, 0))

        self.like = import_image('like.png', (0, 0, 0))
        self.like_button_hover = import_image('like_hover.png', (0, 0, 0))

        self.buttons = {
            "start": [self.start_button, self.start_button_hover],
            "exit": [self.exit_button, self.exit_button_hover],
            "like": [self.like, self.like_button_hover]
        }

        self.x = pygame.image.load("data/images/X.png").convert()
        self.x.set_colorkey((0, 0, 0))

        self.o = pygame.image.load("data/images/O.png").convert()
        self.o.set_colorkey((0, 0, 0))

        self.title = import_image('title.png', [8, 8, 8])

        self.text = font('small_font.png', (255, 255, 255), 3)

        self.clock = pygame.time.Clock()
        self.FPS = 30

        self.board = [[None for _ in range(3)] for _ in range(3)]
        self.turn = ""
        self.choice = ""
        self.pressed = False

        self.client = None
        self.server_message_queue = queue.Queue()  # Shared queue for communication
        self.connecting = True

        self.run = True

    def switch_turn(self):
        self.turn = "X" if self.turn == "O" else "O"

    def check_row(self, j, value):
        for a in range(3):
            if self.board[a][j] != value:
                return False
        return True

    def check_col(self, i, value):
        for a in range(3):
            if self.board[i][a] != value:
                return False
        return True

    def check_first_diagonal(self, value):
        for a in range(3):
            if self.board[a][a] != value:
                return False
        return True

    def check_second_diagonal(self, value):
        for a in range(3):
            if self.board[a][2 - a] != value:
                return False
        return True

    def check_victory(self, i, j):
        value = self.board[i][j]
        return self.check_row(j, value) or self.check_col(i, value) or self.check_first_diagonal(
            value) or self.check_second_diagonal(value)

    def draw_board(self, mouse_pos):
        width = 150
        margin_y = 5
        for i in range(3):
            margin_x = 5
            for j in range(3):
                if margin_x + width * j < mouse_pos[0] < margin_x + width * j + 150 and margin_y + width * i < \
                        mouse_pos[1] < margin_y + width * i + 150:
                    self.window.blit(self.tile_hover, (margin_x + width * j, margin_y + width * i))
                    if self.pressed and self.board[i][j] is None and self.turn == self.choice:
                        self.board[i][j] = self.choice
                        if self.check_victory(i, j):
                            print(self.turn, " wins")
                        self.switch_turn()
                        self.pressed = False
                        message = {'pos': [i, j], 'choice': self.choice}
                        self.client.send_message(message)
                        print(message, "message sent!\n")
                    else:
                        self.pressed = False
                else:
                    self.window.blit(self.tile, (margin_x + width * j, margin_y + width * i))
                if self.board[i][j] == "X":
                    self.window.blit(self.x, (margin_x + width * j, margin_y + width * i))
                elif self.board[i][j] == "O":
                    self.window.blit(self.o, (margin_x + width * j, margin_y + width * i))
                margin_x += 5
            margin_y += 5

    def connect_server(self):
        try:
            self.client = Client()
            threading.Thread(target=self.connect_players_thread, daemon=True).start()
        except Exception as e:
            print(f"Error connecting to server: {str(e)}")

    def connect_players_thread(self):
        while self.connecting:
            message = self.client.receive_messages()
            if message:
                self.server_message_queue.put(message)  # Add message to queue

    def connecting_screen(self):
        self.connect_server()
        run = True
        while run:
            self.window.fill((0, 0, 0))
            mouse_pos = pygame.mouse.get_pos()

            self.text.display_fonts(self.window, "Connecting...", [160, 200], 5)

            try:
                message = self.server_message_queue.get_nowait()
                if message:
                    if 'action' in message and message['action'] == "Player connected":
                        self.turn = message['turn']
                        self.choice = message['choice']
                        self.connecting = False
                        self.game_loop()
            except queue.Empty:
                pass

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.connecting = False
                    self.run = False

            pygame.display.update()
            self.clock.tick(self.FPS)

        pygame.quit()

    def starting_screen(self):
        run = True
        pressed = False
        while run:
            self.window.fill((0, 0, 0))
            self.window.blit(self.title, (0, 0))
            mouse_pos = pygame.mouse.get_pos()

            pos = [(self.SCREEN_SIZE[0] - self.start_button.get_width()) // 2, 170]
            offset = 0
            for button in self.buttons:
                if pos[0] <= mouse_pos[0] <= pos[0] + self.buttons[button][0].get_width() and pos[1] + offset <= \
                        mouse_pos[1] < pos[1] + self.buttons[button][0].get_height() + offset:
                    self.window.blit(self.buttons[button][1], [pos[0], pos[1] + offset])
                    if pressed:
                        if button == "start":
                            self.connecting_screen()
                        elif button == "exit":
                            run = False
                        else:
                            webbrowser.open('www.linkedin.com/in/rohit-dewaliya-a12801280')
                        pressed = False
                else:
                    self.window.blit(self.buttons[button][0], [pos[0], pos[1] + offset])

                offset += 70

            for event in pygame.event.get():
                if event.type == QUIT:
                    run = False

                if event.type == KEYDOWN:
                    pass

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        pressed = True

            pygame.display.update()
            self.clock.tick(self.FPS)

        pygame.quit()

    def game_loop(self):
        while self.run:
            mouse_pos = pygame.mouse.get_pos()
            self.window.fill((0, 0, 0))

            # Draw the board and handle player moves
            self.draw_board(mouse_pos)

            # Check for messages from the server (opponent's move)
            try:
                message = self.server_message_queue.get_nowait()
                if message:
                    message = message['message']
                    print(message)
                    pos = message['pos']
                    choice = message['choice']
                    self.board[pos[0]][pos[1]] = choice
                    if self.check_victory(pos[0], pos[1]):
                        print(choice, " wins")
                    self.switch_turn()
            except queue.Empty:
                pass

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.run = False

                if event.type == KEYDOWN:
                    pass

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.pressed = True

            pygame.display.update()
            self.clock.tick(self.FPS)

        pygame.quit()


game = GameScreen()
game.starting_screen()
