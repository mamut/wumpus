# -*- coding: utf-8 -*-

from wumpus_world import State

from garlicsim.misc import WorldEnded

def sensors():
    return sorted(State().sensors().keys())

def actions():
    return sorted(State().actions().keys())

def app():
    messages = []
    print sensors()
    print actions()
    while True:
        try:
            pass
        except WorldEnded:
            pass

if __name__ == "__main__":
    app()
