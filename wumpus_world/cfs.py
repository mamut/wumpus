# -*- coding: utf-8 -*-

from collections import namedtuple, defaultdict
from random import choice

Classifier = namedtuple('Classifier', 'condition, action')

class CFS(object):

    def __init__(self, sensors=None, actions=None):
        self.population_size = 40
        self.sensors = sorted(sensors or [])
        self.actions = sorted(actions or [])
        self.messages = []
        self.scores = defaultdict(int)
        self.generate_random_classifiers(self.population_size)
        self.clf_uses = defaultdict(int)

    def generate_random_classifiers(self, number):
        self.classifiers = []
        for k in xrange(number):
            condition = "11"
            for x in xrange(len(self.sensors)):
                condition += choice(['0', '1', '#'])
            action = choice(self.actions)
            cls = Classifier(condition=condition, action=action)
            self.scores[cls] = 0
            self.classifiers.append(cls)

    def clear_messages(self):
        self.messages = []

    def add_message(self, msg):
        self.messages.append(msg)

    def get_action(self):
        message = self.messages.pop(0)
        choices = [clf for clf in self.classifiers
                if self.message_fits_classifier(message, clf)]
        choices.sort(key=lambda x: self.scores[x], reverse=True)
        if len(choices) == 0:
            return choice(self.actions)
        else:
            clf = choices.get(0)
            self.clf_uses[clf] += 1
            return clf.action

    def give_feedback(self, value):
        for clf in self.classifiers:
            self.scores[clf] *= 0.95
        used_clfs = sum([x for x in self.clf_uses.values()]) or 1
        part = value / used_clfs
        for clf in self.classifiers:
            self.scores[clf] += part * self.clf_uses[clf]
        self.clf_uses = defaultdict(int)

    def evolve(self):
        new_population = []
        new_scores = defaultdict(int)
        for x in xrange(self.population_size):
            first = choice(self.classifiers)
            second = choice(self.classifiers)
            if self.scores[first] >= self.scores[second]:
                new_population.append(first)
                new_scores[first] = self.scores[first]
            else:
                new_population.append(second)
                new_scores[second] = self.scores[second]

        self.classifiers = new_population
        self.scores = new_scores

    def message_fits_classifier(self, msg, clf):
        for k in xrange(len(msg)):
            if clf.condition[k] == '#':
                continue
            if clf.condition[k] != msg[k]:
                return False
        return True
