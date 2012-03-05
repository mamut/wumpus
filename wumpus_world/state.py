# -*- coding: utf-8 -*-

from collections import namedtuple
from itertools import product
from random import random, choice

import garlicsim.data_structures

BoardTile = namedtuple('BoardTile', 'pit, wumpus, gold')

class State(garlicsim.data_structures.State):

    def __init__(self, board=None, player_pos=(0, 0), points=0,
            player_dir='up', bump=False, player_has_arrow=True,
            wumpus_dead=False, scream=False, gold_grabbed=False,
            game_won=False):
        self.winning_prize = 1000
        self.death_penalty = -1000
        self.action_penalty = -1
        self.arrow_penalty = -10
        self.board_size = 4

        self.player_pos = player_pos
        self.player_dir = player_dir
        self.points = points
        self.board = board or self._initiate_board()

        self.bump = bump
        self.player_has_arrow = player_has_arrow
        self.wumpus_dead = wumpus_dead
        self.scream = scream
        self.gold_grabbed = gold_grabbed
        self.game_won = game_won

    def _initiate_board(self):
        board = {}
        pit_probability = 0.2

        is_pit = lambda: random() <= pit_probability
        field_indices = sorted(list(product(xrange(self.board_size), repeat=2)))

        board[0,0] = BoardTile(pit=False, wumpus=False, gold=False)
        for indices in field_indices[1:]:
            board[indices] = BoardTile(pit=is_pit(), wumpus=False, gold=False)

        random_field_indices = lambda: choice(field_indices[1:])
        wumpus = random_field_indices()
        gold = random_field_indices()
        board[wumpus] = board[wumpus]._replace(wumpus=True)
        board[gold] = board[gold]._replace(gold=True)

        return board

    def next_state(self, *args, **kwargs):

        if self.current_field().wumpus and not self.wumpus_dead:
            raise garlicsim.misc.WorldEnded

        if self.current_field().pit:
            raise garlicsim.misc.WorldEnded

        if self.game_won:
            raise garlicsim.misc.WorldEnded

        defaults = {
                'board': self.board,
                'player_pos': self.player_pos,
                'player_dir': self.player_dir,
                'points': self.points - 1,
                'bump': False,
                'player_has_arrow': self.player_has_arrow,
                'wumpus_dead': self.wumpus_dead,
                'scream': False,
                'gold_grabbed': self.gold_grabbed,
                'game_won': self.game_won
            }
        defaults.update(kwargs)
        return State(**defaults)

    def step_turn_left(self):
        new_dir = {
                'up': 'left',
                'left': 'down',
                'down': 'right',
                'right': 'up'
            }[self.player_dir]
        return self.next_state(player_dir=new_dir)

    def step_turn_right(self):
        new_dir = {
                'up': 'right',
                'left': 'up',
                'down': 'left',
                'right': 'down'
            }[self.player_dir]
        return self.next_state(player_dir=new_dir)

    def step_shoot_arrow(self):
        if not self.player_has_arrow:
            return self.next_state()

        next_state = self.next_state(player_has_arrow=False)
        next_state.points += self.arrow_penalty

        x, y = self.player_pos
        arrow_path = {
                'up': [(x, k) for k in range(y, self.board_size)],
                'left': [(k, y) for k in range(0, x)],
                'down': [(x, k) for k in range(0, y)],
                'right': [(k, y) for k in range(x, self.board_size)]
            }[self.player_dir]

        for pos in arrow_path:
            if self.board[pos].wumpus:
                next_state.wumpus_dead = True
                next_state.scream = True
                break

        return next_state

    def step_go_forward(self):
        x, y = self.player_pos
        new_pos = {
                'up': lambda: (x, y + 1),
                'left': lambda: (x - 1, y),
                'down': lambda: (x, y - 1),
                'right': lambda: (x + 1, y)
            }[self.player_dir]()

        new_x, new_y = new_pos
        if (0 <= new_x < self.board_size) and (0 <= new_y < self.board_size):
            next_state = self.next_state(player_pos=new_pos)
        else:
            next_state = self.next_state(bump=True)

        if next_state.current_field().wumpus and not next_state.wumpus_dead:
            next_state.points += self.death_penalty

        if next_state.current_field().pit:
            next_state.points += self.death_penalty

        return next_state

    def step_grab_gold(self):
        if self.board[self.player_pos].gold:
            return self.next_state(gold_grabbed=True)
        else:
            return self.next_state()

    def step_climb_out(self):
        if self.player_pos == (0, 0):
            next_state = self.next_state(game_won=True)
            if self.gold_grabbed:
                next_state.points += self.winning_prize
        else:
            next_state = self.next_state()

        return next_state

    def sensors(self):
        sensors = {
                'breeze': False,
                'glow': False,
                'stink': False,
                'scream': self.scream,
                'bump': self.bump,
                'gold': self.gold_grabbed,
                'arrow': self.player_has_arrow
            }

        x, y = self.player_pos
        adjacent_fields = [(x, y)]
        adjacent_fields += [(k, y) for k in [x - 1, x + 1]]
        adjacent_fields += [(x, k) for k in [y - 1, y + 1]]
        for field in adjacent_fields:
            if field in self.board:
                tile = self.board[field]
                if tile.wumpus:
                    sensors['stink'] = True
                if tile.pit:
                    sensors['breeze'] = True

        if self.current_field().gold and not self.gold_grabbed:
            sensors['glow'] = True

        return sensors

    def current_field(self):
        return self.board[self.player_pos]

    def actions(self):
        actions = {
            'go_up': lambda: self.go('up'),
            'go_left': lambda: self.go('left'),
            'go_down': lambda: self.go('down'),
            'go_right': lambda: self.go('right'),
            'shoot_up': lambda: self.shoot_to('up'),
            'shoot_left': lambda: self.shoot_to('left'),
            'shoot_down': lambda: self.shoot_to('down'),
            'shoot_right': lambda: self.shoot_to('right'),
            'grab': lambda: self.step_grab_gold(),
            'climb': lambda: self.step_climb_out()
        }
        return actions

    def act(self, action):
        new_state = self.actions()[action]()
        return new_state

    def step_rules(self):
        rules = [
            [(None, ), '', 0]
        ]

    def turn_to(self, direction):
        directions = {'up': 0, 'left': 1, 'down': 2, 'right': 3}
        curr_idx = directions[self.player_dir]
        new_idx = directions[direction]

        diff = (new_idx - curr_idx) % 4

        if diff == 0:
            return self
        if diff == 1:
            return self.step_turn_right()
        if diff == 2:
            return self.step_turn_right().step_self_turn_right()
        if diff == 3:
            return self.step_turn_left()

    def go(self, direction):
        return self.turn_to(direction).step_go_forward()

    def shoot_to(self, direction):
        return self.turn_to(direction).step_shoot_arrow()

    @staticmethod
    def create_root():
        return State()


    #@staticmethod
    #def create_messy_root():
        # In this function you create a messy root state. This usually becomes
        # the first state in your simulation.
        #
        # Why messy? Because sometimes you want to have fun in your
        # simulations. You want to create a world where there's a lot of mess,
        # with many objects interacting with each other. This is a good way to
        # test-drive your simulation.
        #
        # This function may take arguments, if you wish, to be used in making
        # the state. For example, in a Life simulation you may want to specify
        # the width and height of the board using arguments to this function.
        #
        # This function returns the newly-created state.


    #def step_generator(self):
    #    yield None
    #    pass
    #
    # Do you want to use a step generator as your step function? If so, you may
    # uncomment the above and fill it in, and it will be used instead of the
    # normal step function.
    #
    # A step generator is similar to a regular step function: it takes a
    # starting state, and computes the next state. But it doesn't `return` it,
    # it `yield`s it. And then it doesn't exit, it just keeps on crunching and
    # yielding more states one by one.
    #
    # A step generator is useful when you want to set up some environment
    # and/or variables when you do your crunching. It can help you save
    # resources, because you won't have to do all that initialization every
    # time garlicsim computes a step.
    #
    # (You may write your step generator to terminate at some point or to never
    # terminate-- Both ways are handled by `garlicsim`.)
