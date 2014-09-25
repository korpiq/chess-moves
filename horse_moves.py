"""
Horse move computer

Usage: python horse_moves.py [options] Xn-Ym ...
  Xn = start location (A1-H8)
  Ym = target location (A1-H8)
Options:
  --draw     Show solutions on chessboard
  --verbose  Show solving steps on chessboard
"""

import getopt
import sys


class ChessboardLocation:
    def __init__(self, coordinates, previous_location=None):
        self.x, self.y = isinstance(coordinates, list) and coordinates or [
            (ord(coordinates[0]) - 65) & 7,
            int(coordinates[1]) - 1
        ]
        self.previous_locations = previous_location and {str(previous_location): previous_location} or {}

    def add_previous(self, previous_location):
        self.previous_locations[str(previous_location)] = previous_location

    def get_previous_locations(self):
        return self.previous_locations.values()

    def set_letter(self, letter):
        self.x = (ord(letter[0]) - 65)

    def get_letter(self):
        return chr(65 + self.x)

    def is_valid(self):
        return (self.x == self.x & 7) and (self.y == self.y & 7)

    def list_routes(self):
        result = []
        for previous in self.get_previous_locations():
            for route in previous.list_routes():
                result.append(route + [self])
        return result or [[self]]

    def __str__(self):
        return self.get_letter() + str(1 + self.y)


class HorseMoves:
    def __init__(self, start_location, finish_location):
        self.start_location = start_location
        self.finish_location = finish_location
        self.finish_string = str(finish_location)
        self.move_tree = [[start_location]]
        self.reached = {str(start_location): start_location}

    def solved(self):
        return self.finish_string in self.reached.keys()

    def solve(self, callback=None):
        self.find_shortest_solutions(callback)

        final_location = self.reached[self.finish_string]
        last_locations = [final_location]
        pruned_move_tree = []

        while last_locations:
            pruned_move_tree.insert(0, last_locations)
            previous_locations = []
            for location in last_locations:
                previous_locations = previous_locations + location.get_previous_locations()
            last_locations = previous_locations

        self.move_tree = pruned_move_tree

    def get_solutions(self):
        final_location = self.reached[self.finish_string]
        return final_location.list_routes()

    def find_shortest_solutions(self, callback=None):
        next_moves = self.move_tree[-1]
        while not self.solved():
            next_moves, self.reached = self.possible_next_moves(next_moves, self.reached)
            self.move_tree.append(next_moves)
            if callback:
                callback()

    def possible_next_moves(self, start_locations, reached):
        next_moves = {}

        for start_location in start_locations:
            for long_step in [-2, 2]:
                for short_step in [-1, 1]:
                    for coordinates in [
                        [start_location.x + long_step, start_location.y + short_step],
                        [start_location.x + short_step, start_location.y + long_step]
                    ]:
                        new_location = ChessboardLocation(coordinates, start_location)
                        if new_location.is_valid():
                            new_location_string = str(new_location)

                            if new_location_string in reached.keys():
                                pass # a shorter route there exists
                            elif new_location_string in next_moves.keys():
                                # equally short route found
                                next_moves[new_location_string].add_previous(start_location)
                            else:
                                # first route there found
                                next_moves[new_location_string] = new_location

        reached.update(next_moves)
        return next_moves.values(), reached

    def draw(self):
        chessboard = [[(((y ^ x) & 1) and '#' or '_') for x in range(0,8)] for y in range(0,8)]
        chessboard[self.finish_location.y][self.finish_location.x] = 'X'
        for move_index in range(0, len(self.move_tree)):
            for move in self.move_tree[move_index]:
                chessboard[move.y][move.x] = '%d' % move_index

        print('  A B C D E F G H')
        print('\n'.join(['%d %s' % (y + 1, ' '.join([chessboard[y][x] for x in range(0,8)])) for y in range(0,8)]))


def report_solutions(start, finish, draw, verbose):
    horse = HorseMoves(ChessboardLocation(start), ChessboardLocation(finish))
    if verbose:
        horse.draw()
    horse.solve(callback=verbose and horse.draw or None)
    if draw:
        horse.draw()
    solutions = horse.get_solutions()
    for route_number in range(0, len(solutions)):
        route = solutions[route_number]
        print('%3d: %s' % (route_number + 1, ' '.join([str(location) for location in route])))


def usage():
    print(__doc__.strip())
    sys.exit(1)

if __name__ == '__main__':
    args = sys.argv[1:]
    options_list, desires = getopt.getopt(args, '', ['draw', 'verbose', 'help'])
    options = map(lambda pair: pair[0][2:], options_list)

    if 'help' in options or not desires:
        usage()

    for desire in desires:
        print(desire)
        report_solutions(*desire.split('-'), draw='draw' in options, verbose='verbose' in options)
