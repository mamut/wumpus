# -*- coding: utf-8 -*-

from collections import namedtuple
from itertools import product
from random import random, choice

import garlicsim.data_structures

BoardTile = namedtuple('BoardTile', 'pit, wumpus, gold')

class State(garlicsim.data_structures.State):

    def __init__(self, board=None, player_pos=(0, 0), points=0):
        self.winning_prize = 1000
        self.death_penalty = -1000
        self.action_penalty = -1
        self.arrow_penalty = -10
        self.board_size = 4

        self.player_pos = player_pos
        self.player_dir = 'up'
        self.points = points
        self.board = board or self._initiate_board()

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


    def step(self):
        return State(board=self.board)


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
