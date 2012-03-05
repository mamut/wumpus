# -*- coding: utf-8 -*-

from collections import namedtuple, defaultdict
from random import choice
from random import random as random_f

Classifier = namedtuple('Classifier', 'condition, action')

class CFS(object):

    def __init__(self, sensors=None, actions=None):
        self.population_size = 80
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
        mutation_p = 0.01
        for x in xrange(self.population_size - 40):
            first = choice(self.classifiers)
            second = choice(self.classifiers)
            if self.scores[first] >= self.scores[second]:
                new_population.append(first)
                new_scores[first] = self.scores[first]
            else:
                new_population.append(second)
                new_scores[second] = self.scores[second]

        def crossover(first, second):
            idx = choice(xrange(len(first.condition)))
            condition = first[:idx] + second[idx:]
            action = choice([first.action, second.action])
            return Classifier(condition=condition, action=action)

        crossovers = []
        for x in xrange(self.population_size - len(new_population)):
            first = choice(new_population)
            second = choice(new_population)
            crossovers.append(crossover(first, second))

        def mutate_cond(clf):
            idx = choice(len(clf.condition))
            condition = clf.condition[:]
            condition[idx] = choice("01#")
            return Classifier(condition=condition, action=clf.action)

        def mutate_action(clf):
            action = choice(self.actions)
            return Classifier(condition=clf.condition, action=action)

        mutants = []
        for clf in new_population:
            if random_f() < mutation_p:
                new_clf = mutate_cond(clf)
                mutants.append(new_clf)
        for clf in new_population:
            if random_f() < mutation_p:
                new_clf = mutate_action(clf)
                mutants.append(new_clf)

        self.classifiers = new_population + + crossovers + mutants
        self.scores = new_scores

    def message_fits_classifier(self, msg, clf):
        for k in xrange(len(msg)):
            if clf.condition[k] == '#':
                continue
            if clf.condition[k] != msg[k]:
                return False
        return True
