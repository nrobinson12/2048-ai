import math
import time
import numpy as np
from random import randint, seed, choice
from numba import jit
from helpers import print_board

DEBUG = False

UP, DOWN, LEFT, RIGHT = range(4)
dirs = {
    0: "UP",
    1: "DOWN",
    2: "LEFT",
    3: "RIGHT"
}

# get smoothness of grid
@jit
def get_smoothness(a):
    s = 0
    for i in [0,1,2,3]:
        for j in [0,1,2,3]:
            if a[i][j] != 0:
                # find next occupied

                # right
                k = 1
                while j+k < 3 and a[i][j+k] == 0:
                    k += 1
                if j+k <= 3 and a[i][j+k] != 0:
                    s += abs(a[i][j] - a[i][j+k])

                # down
                k = 1
                while i + k < 3 and a[i+k][j] == 0:
                    k += 1
                if i+k <= 3 and a[i+k][j] != 0:
                    s += abs(a[i][j] - a[i+k][j])
    return s


def eval_board(board, n_empty):
    # evaluate board on 4 properties:
    # 1. max value in board
    # 2. number of empty tiles
    # 3. monotonicity
    # 4. smoothness
    # 5. snake

    grid = board.grid

    # weights we give to each prop
    max_w = 1
    empty_w = 100
    mono_w = 10
    smooth_w = 10

    # ----- snake pattern
    snake_w = [15,14,13,12,8,9,10,11,7,6,5,4,0,1,2,3]
    snake_w = np.array(snake_w).reshape(4,4)
    snake_u = np.sum(grid * snake_w)

    # ----- max tile
    max_u = np.amax(grid) * max_w

    # ----- empty tiles
    empty_u = (math.log(n_empty) * empty_w) if n_empty != 0 else 0

    # ----- monotonicity
    log_grid = np.log2(grid, where=grid != 0)   # for smoothness as well

    mono_h = np.zeros((1, 4))
    mono_v = np.zeros((1, 4))

    for i in range(3):
        mono_h += log_grid[:, i] - log_grid[:, i + 1]   # differences in horizontally adjacent
        mono_v += log_grid[i, :] - log_grid[i + 1, :]   # differences in vertically adjacent

    mono_u = (np.sum(np.abs(mono_h)) + np.sum(np.abs(mono_v))) * mono_w

    # ----- smoothness
    smooth_u = -(get_smoothness(log_grid) * smooth_w)

    # ----- total
    utility = empty_u + mono_u + smooth_u
    utility += max_u
    utility += snake_u

    return (utility, empty_u, mono_u, smooth_u)

            
# -------------------- EXPECTIMAX -------------------- #
class Expectimax():
    def __init__(self):
        self.states_visited = 0

    def get_move(self, board):
        best_move, _ = self.maximize(board)
        return best_move

    # evaluate board; heauristic function of board state
    def eval_board1(self, board, n_empty): 
        # previous eval function
        grid = board.grid

        utility = 0
        smoothness = 0

        big_t = np.sum(np.power(grid, 2))
        s_grid = np.sqrt(grid)
        smoothness -= np.sum(np.abs(s_grid[::,0] - s_grid[::,1]))
        smoothness -= np.sum(np.abs(s_grid[::,1] - s_grid[::,2]))
        smoothness -= np.sum(np.abs(s_grid[::,2] - s_grid[::,3]))
        smoothness -= np.sum(np.abs(s_grid[0,::] - s_grid[1,::]))
        smoothness -= np.sum(np.abs(s_grid[1,::] - s_grid[2,::]))
        smoothness -= np.sum(np.abs(s_grid[2,::] - s_grid[3,::]))
        
        empty_w = 100000
        smoothness_w = 3

        empty_u = n_empty * empty_w
        smooth_u = smoothness ** smoothness_w
        big_t_u = big_t

        utility += big_t
        utility += empty_u
        utility += smooth_u

        return (utility, empty_u, smooth_u, big_t_u)


    def maximize(self, board, depth = 0):
        moves = board.get_available_moves()
        moves_boards = []

        for m in moves:
            m_board = board.clone()
            m_board.move(m)
            moves_boards.append((m, m_board))

        max_utility = (float('-inf'),0,0,0)
        best_direction = None

        for mb in moves_boards:
            if DEBUG:
                print('Testing %s at depth %d:' % (dirs[mb[0]], depth))
                print_board(mb[1])
            utility = self.chance(mb[1], depth + 1)

            if utility[0] >= max_utility[0]:
                max_utility = utility
                best_direction = mb[0]

            self.states_visited += 1

        return best_direction, max_utility

    def chance(self, board, depth = 0):
        empty_cells = board.get_available_cells()
        n_empty = len(empty_cells)

        #if n_empty >= 7 and depth >= 5:
        #    return self.eval_board(board, n_empty)

        if n_empty >= 6 and depth >= 3:
            return eval_board(board, n_empty)

        if n_empty >= 0 and depth >= 5:
            return eval_board(board, n_empty)

        if n_empty == 0:
            _, utility = self.maximize(board, depth + 1)
            return utility

        possible_tiles = []

        chance_2 = (.9 * (1 / n_empty))
        chance_4 = (.1 * (1 / n_empty))
        
        for empty_cell in empty_cells:
            possible_tiles.append((empty_cell, 2, chance_2))
            possible_tiles.append((empty_cell, 4, chance_4))

        avg_utility = [0, 0, 0, 0]

        for t in possible_tiles:
            t_board = board.clone()
            t_board.insert_tile(t[0], t[1])
            _, utility = self.maximize(t_board, depth + 1)

            for i in range(4):
                avg_utility[i] += utility[i] # * t[2]

        for i in range(4):
            avg_utility[i] /= len(possible_tiles)

        return tuple(avg_utility)


# -------------------- MONTE CARLO -------------------- #
class MonteCarlo:
    def __init__(self):
        self.states_visited = 0

    def get_move(self, board):
        moves = board.get_available_moves()
        num_runs = 1000
        boards = []

        runs_sum = {}
        runs_ttl = {}

        for m in moves:
            runs_sum[m] = 0
            runs_ttl[m] = 0

        for _ in range(num_runs):
            b = board.clone()
            boards.append(b)

        for b in boards:
            move = choice(moves)

            value = self.run_board(b, move)

            runs_sum[move] += value
            runs_ttl[move] += 1

        # get best score & move
        best_score = 0
        best_move = None

        for m, val in runs_sum.items():
            if runs_ttl[m] != 0:
                score = val / runs_ttl[m]
                runs_sum[m] = score
                
                if score > best_score:
                    best_score = score
                    best_move = m

        # print(runs_sum)
        return best_move


    def run_board(self, board, move, depth = 0):
        board.move(move)
        empty_cells = board.get_available_cells()
        n_empty = len(empty_cells)


        # base case
        if n_empty == 0 or depth >= 3:
            return eval_board(board, n_empty)[0]


        # random tile generated - we are not checking probabilities anymore
        # self.insert_random_tile(board)

        # choose another random move
        moves = board.get_available_moves()
        if moves:
            move = choice(moves)
            return self.run_board(board, move, depth + 1)
        else:
            return eval_board(board, n_empty-1)[0]

    def insert_random_tile(self, board):
        if randint(0,99) < 100 * 0.9:
            value = 2
        else:
            value = 4

        cells = board.get_available_cells()
        pos = cells[randint(0, len(cells) - 1)] if cells else None

        if pos is None:
            return None
        else:
            board.insert_tile(pos, value)
            return pos