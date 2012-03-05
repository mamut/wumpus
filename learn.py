# -*- coding: utf-8 -*-

from wumpus_world import State

def sensors():
    return sorted(State().sensors().keys())

def actions():
    return sorted(State().actions().keys())

def app():
    print sensors()
    print actions()

if __name__ == "__main__":
    app()
