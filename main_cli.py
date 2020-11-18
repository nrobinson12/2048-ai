from game_board import GameBoard
from ai import Expectimax, MonteCarlo
from random import randint, seed
import time
from helpers import print_board

DELAY = 1000 / 1000

dirs = {
    0: "UP",
    1: "DOWN",
    2: "LEFT",
    3: "RIGHT"
}

class CLIRunner:
    def __init__(self):
        self.board = GameBoard()
        self.ai = Expectimax()

        self.init_game()
        print_board(self.board)

        self.run_game()

        self.over = False

    def init_game(self):
        self.insert_random_tile()
        self.insert_random_tile()

    def run_game(self):
        moves = 0
        while True and moves < 2:
            move = self.ai.get_move(self.board)
            print("Player's Turn:", end="")
            self.board.move(move)
            print(dirs[move])
            print_board(self.board)
            print("Computer's Turn")
            self.insert_random_tile()
            print_board(self.board)

            if len(self.board.get_available_moves()) == 0:
                print("GAME OVER (max tile): " + str(self.board.get_max_tile()))
                break

            moves += 1
            if DELAY:
                time.sleep(DELAY)

    def insert_random_tile(self):
        if randint(0,99) < 100 * 0.9:
            value = 2
        else:
            value = 4

        cells = self.board.get_available_cells()
        pos = cells[randint(0, len(cells) - 1)] if cells else None

        if pos is None:
            return None
        else:
            self.board.insert_tile(pos, value)
            return pos

if __name__ == '__main__':
    CLIRunner = CLIRunner()
