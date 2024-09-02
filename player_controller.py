import random

class PlayerController:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.turn = random.choice([0, 1])
        self.choice = "O" if self.turn == 1 else "X"

