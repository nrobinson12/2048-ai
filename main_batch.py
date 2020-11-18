import numpy as np
from game_board import GameBoard, merge, justify_left, get_available_from_zeros
from ai import Expectimax, MonteCarlo, get_smoothness
from game_board import GameBoard
from random import randint
from timeit import default_timer as timer
from time import sleep
from collections import Counter
from joblib import Parallel, delayed
from sys import argv


DELAY = 0

# first calls for Numba to compile fast versions
temp = np.zeros((4, 4))
merge(temp)
justify_left(temp, temp)
get_available_from_zeros(temp)
get_smoothness(temp)
sleep(1)

class Batch:
    def __init__(self):
        # MEASURES
        self.total_moves_time = 0
        self.total_moves = 0
        self.fastest_move = -1
        self.longest_move = 0
        self.time_to_reach = []

        # setup game & ai
        self.board = GameBoard()
        self.ai = Expectimax()
        self.init_game()

        # run ai on game
        self.start = timer()
        self.run_game()
        end = timer()

        # MEASURES
        self.total_time = end - self.start # total time to run
        self.avg_move_time = self.total_moves_time / self.total_moves # moves done
        self.max_tile = self.board.get_max_tile() # max tile
        self.states_visited = self.ai.states_visited # states visited

    def init_game(self):
        self.insert_random_tile()
        self.insert_random_tile()

    def run_game(self):
        cur_max_tile = 8
        while True:
            move_start = timer()
            move = self.ai.get_move(self.board)
            move_end = timer()
            
            # save move time
            move_time = move_end - move_start
            self.total_moves_time += move_time
            self.total_moves += 1
            if self.fastest_move == -1 or move_time < self.fastest_move:
                self.fastest_move = move_time
            if move_time > self.longest_move:
                self.longest_move = move_time

            # do the actual move + the response
            self.board.move(move)
            self.insert_random_tile()

            # check if we got a bigger tile
            if cur_max_tile in self.board.grid:
                reached_end = timer()
                self.time_to_reach.append((cur_max_tile, reached_end - self.start))
                cur_max_tile *= 2

            # if no more moves, game over
            if len(self.board.get_available_moves()) == 0:
                break

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

def log_test(b):
    outputnum = argv[1]
    with open('output' + outputnum + '.log', 'a') as f:
        f.write('-----\n')
        f.write('Max Tile: %d\n' % b.max_tile)
        f.write('Total Moves: %d\n' % b.total_moves)
        f.write('Total States Visited: %d\n' % b.states_visited)
        f.write('Total Time: %f\n' % b.total_time)
        f.write('Average Time / Move: %f\n' % b.avg_move_time)
        f.write('Fastest Move: %f\n' % b.fastest_move)
        f.write('Longest Move: %f\n' % b.longest_move)
        f.write('Time To Get Tiles:\n')
        for tile, time in b.time_to_reach:
            f.write('%d: %f\n' % (tile, time))

def parallel_runs():
    return (Batch(),)

def run_parallel():
    jobs = 10
    tests = 10 / jobs
    return Parallel(n_jobs=jobs, verbose=0)(delayed(parallel_runs)() for i in range(int(tests)))

def main_parallel():
    open('output.log', 'w').close()
    open('average.log', 'w').close()

    b_total = run_parallel()
    print(b_total)

def main():
    outputnum = argv[1]
    open('output' + outputnum + '.log', 'w').close()
    open('average' + outputnum + '.log', 'w').close()
    tests = 0

    max_tile_list = []
    total_moves_sum = 0
    states_visited_sum = 0
    total_time_sum = 0
    avg_move_time_sum = 0
    fastest_move_sum = 0
    longest_move_sum = 0
    time_to_reach_sum = {}

    while tests < 10:
        b = Batch()
        
        max_tile_list.append(b.max_tile)
        total_moves_sum += b.total_moves
        states_visited_sum += b.states_visited
        total_time_sum += b.total_time
        avg_move_time_sum += b.avg_move_time
        fastest_move_sum += b.fastest_move
        longest_move_sum += b.longest_move
        for tile, time in b.time_to_reach:
            if tile not in time_to_reach_sum:
                time_to_reach_sum[tile] = (0,0)
            num = time_to_reach_sum[tile][0] + 1
            new_time = time_to_reach_sum[tile][1] + time
            time_to_reach_sum[tile] = (num, new_time)

        log_test(b)

        tests += 1

    avg_max_tile = Counter(max_tile_list).most_common(1)[0][0]

    with open('average' + outputnum + '.log', 'w') as f:
        f.write('Average Max Tile: %d\n' % avg_max_tile)
        f.write('Average Total Moves: %f\n' % (total_moves_sum / tests))
        f.write('Average Total States Visited: %f\n' % (states_visited_sum / tests))
        f.write('Average Total Time: %f\n' % (total_time_sum / tests))
        f.write('Average Time / Move: %f\n' % (avg_move_time_sum / tests))
        f.write('Average Fastest Move: %f\n' % (fastest_move_sum / tests))
        f.write('Average Longest Move: %f\n' % (longest_move_sum / tests))
        f.write('Average Time To Get Tiles:\n')
        for tile, value in time_to_reach_sum.items():
            num, time = value
            f.write('%d: %f\n' % (tile, time / num))


if __name__ == '__main__':
    main()
