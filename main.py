import queue
import threading
import webbrowser
import pygame
from pygame.locals import *
from client import Client
from data.scripts.text import font
from data.scripts.image_functions import import_image

pygame.init()


class GameScreen:
    def __init__(self, width=470, height=470):
        self.SCREEN_SIZE = [width, height]
        self.CENTER = [width // 2, height // 2]
        self.window = pygame.display.set_mode(self.SCREEN_SIZE, 0, 32)
        pygame.display.set_caption("Tic Tac Toe")

        self.tile = pygame.image.load("data/images/tile.png").convert()
        self.tile.set_alpha(15)
        self.tile_hover = pygame.image.load("data/images/tile.png").convert()
        self.tile_hover.set_alpha(20)

        self.name_tile = pygame.transform.scale(self.tile.copy(), [120, 50])
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
        self.server_message_queue = queue.Queue()
        self.connecting = True
        self.run = True

    def switch_turn(self):
        self.turn = "X" if self.turn == "O" else "O"

    def check_row(self, j, value):
        return all(self.board[a][j] == value for a in range(3))

    def check_col(self, i, value):
        return all(self.board[i][a] == value for a in range(3))

    def check_first_diagonal(self, value):
        return all(self.board[a][a] == value for a in range(3))

    def check_second_diagonal(self, value):
        return all(self.board[a][2 - a] == value for a in range(3))

    def check_victory(self, i, j):
        value = self.board[i][j]
        return (self.check_row(j, value) or
                self.check_col(i, value) or
                self.check_first_diagonal(value) or
                self.check_second_diagonal(value))

    def draw_board(self, mouse_pos):
        width = 150
        margin_y = 5
        for i in range(3):
            margin_x = 5
            for j in range(3):
                tile_rect = pygame.Rect(margin_x + width * j, margin_y + width * i, width, width)
                if tile_rect.collidepoint(mouse_pos):
                    self.window.blit(self.tile_hover, tile_rect.topleft)
                    if self.pressed and self.board[i][j] is None and self.turn == self.choice:
                        self.board[i][j] = self.choice
                        if self.check_victory(i, j):
                            print(self.turn, "wins")
                            self.end_game(self.turn)
                        self.switch_turn()
                        self.pressed = False
                        message = {'pos': [i, j], 'choice': self.choice}
                        self.client.send_message(message)
                else:
                    self.window.blit(self.tile, tile_rect.topleft)
                if self.board[i][j] == "X":
                    self.window.blit(self.x, tile_rect.topleft)
                elif self.board[i][j] == "O":
                    self.window.blit(self.o, tile_rect.topleft)
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
            try:
                message = self.client.receive_messages()
                if message:
                    self.server_message_queue.put(message)
            except Exception as e:
                print(f"Error in connect_players_thread: {str(e)}")
                self.connecting = False

    def connecting_screen(self):
        self.connect_server()
        while self.connecting:
            self.window.fill((0, 0, 0))
            self.text.display_fonts(self.window, "Connecting...", [160, 200], 5)
            try:
                message = self.server_message_queue.get_nowait()
                if message and 'action' in message and message['action'] == "Player connected":
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
        while True:
            self.window.fill((0, 0, 0))
            self.window.blit(self.title, (0, 0))
            mouse_pos = pygame.mouse.get_pos()
            pos = [(self.SCREEN_SIZE[0] - self.start_button.get_width()) // 2, 170]
            offset = 0
            for button in self.buttons:
                button_rect = pygame.Rect(pos[0], pos[1] + offset, self.buttons[button][0].get_width(),
                                          self.buttons[button][0].get_height())
                if button_rect.collidepoint(mouse_pos):
                    self.window.blit(self.buttons[button][1], button_rect.topleft)
                    if pygame.mouse.get_pressed()[0]:  # Left button
                        if button == "start":
                            self.connecting_screen()
                        elif button == "exit":
                            pygame.quit()
                            return
                        else:
                            webbrowser.open('www.linkedin.com/in/rohit-dewaliya-a12801280')
                else:
                    self.window.blit(self.buttons[button][0], button_rect.topleft)

                offset += 70

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    return

            pygame.display.update()
            self.clock.tick(self.FPS)

    def game_loop(self):
        while self.run:
            mouse_pos = pygame.mouse.get_pos()
            self.window.fill((0, 0, 0))
            self.draw_board(mouse_pos)

            self.handle_server_messages()

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.run = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.turn == self.choice:
                        self.pressed = True

            pygame.display.update()
            self.clock.tick(self.FPS)

        pygame.quit()

    def handle_server_messages(self):
        while True:
            try:
                message = self.server_message_queue.get_nowait()
                print("Received message:", message)
                if 'message' in message:
                    self.process_server_message(message['message'])
            except queue.Empty:
                break
            except Exception as e:
                print(f"Error handling server message: {str(e)}")

    def process_server_message(self, message):
        try:
            pos = message['pos']
            choice = message['choice']
            if self.board[pos[0]][pos[1]] is None:
                self.board[pos[0]][pos[1]] = choice
                if self.check_victory(pos[0], pos[1]):
                    print(choice, "wins")
                    self.end_game(choice)
                self.switch_turn()
        except KeyError as e:
            print(f"Missing expected key in message: {str(e)}")
        except Exception as e:
            print(f"Error processing server message: {str(e)}")

    def end_game(self, winner):
        self.text.display_fonts(self.window, f"{winner} wins!", [self.CENTER[0] - 50, self.CENTER[1] - 20], 5)
        pygame.display.update()
        pygame.time.wait(2000)  # Show the win message for 2 seconds
        self.run = False


game = GameScreen()
game.starting_screen()
