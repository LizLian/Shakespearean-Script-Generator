#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nltk, random, os

NUM_RULE = 50

class State:

    def __init__(self, pos, output, transitions):
        self.pos = pos
        self.transitions = transitions
        self.output = output

    def __repr__(self):
        rhs = [transition.__str__() for transition in self.transitions]
        return self.pos.__str__() + "," + str(rhs)

    def pick_transition(self):
        trans = [transition for transition, freq in self.transitions]
        return random.choice(trans)

    def pick_transition_simple(self):
        picked_state = random.choice(self.transitions)
        return picked_state


class Grammar:

    def __init__(self):
        self.ruleset = None
        self.terminal_nodes = []
        self.template = []
        self.states = {}
        self.most_common_rules = []
        self.common_rules = []


    def make_template_simple(self, states):
        """
        generate sentence templates (PSRs) from simple rules storing in states.txt file
        all the tags in states.txt file match the tags in the Penn Treebank
        rules are randomly chosen using random.choice()
        """
        current_state = states['<START>']
        template = []
        rep_state = {'P3':0, 'CC':0}
        while current_state.pos != '<END>':
            template.append(current_state.output)
            picked_state = current_state.pick_transition_simple()
            current_state = states[picked_state]
            # control the depth of PP and CC
            if picked_state in ('P3', 'CC'):
                rep_state[picked_state] += 1
            if rep_state['P3'] >= 2:
                while(picked_state == 'P3'):
                    picked_state = current_state.pick_transition_simple()
            if rep_state['CC'] >= 2:
                while(picked_state in ('P3', 'CC')):
                    picked_state = current_state.pick_transition_simple()

        return [t for t in template if t != '<NULL>']

        # make template from simple rules
    def load_machine(self, filename):
        """
        load finite state machine storing in states.txt file for make_template_simple method

        """
        f = open(filename)
        states = {}
        for line in f:
            linelist = line.split()
            pos = linelist[0]
            output = linelist[1]
            transitions = linelist[2:]
            state = State(pos, output, transitions)
            states[pos] = state
        f.close()
        return states

    def make_template(self, root_symbol):
        """
        return a rule template. It then can combine with lexicon to generate a sentence
        example of a rule: ['NNP', 'NNP', 'VBG', 'DT', 'JJ', 'NN']
        In the Penn Treebank, the rule "NP-SBJ -> NNP NNP" appeared 357 times. 
        This explains the two NNPs appearing in a row

        root_symbol: start symbol S in the first iteration. a Non-terminal node in other recursions

        the node is appended to template list once a terminal node is found
        all the rules are extracted from the Penn Treebank, most frequent 100 rules.
        parameter NUM_RULE can be used to adjust the most frequent rules to choose from.
        """

        current_state = self.states[root_symbol]
        rhs = current_state.pick_transition()
        for part in rhs:
            if part in self.terminal_nodes:
                self.template.append(part.__str__())
            else:
                self.make_template(part.__str__())
        return self.template


    def load_rules(self):
        self._extract_ruleset()
        self._rule_freq()
        self._get_terminal_nodes()
        for rule in self.ruleset:
            if rule.lhs() not in self.terminal_nodes:
                pos = rule.lhs()
                # get the possible rules from most common rules
                transitions = [(rule.rhs(), freq) for rule, freq in self.most_common_rules if rule.lhs() == pos]
                # fall back to still common rules
                if len(transitions) == 0:
                    transitions = [(rule.rhs(), freq) for rule, freq in self.common_rules if rule.lhs() == pos]
                # fall back to search from all rules
                if len(transitions) == 0:
                    transitions = [rule.rhs() for rule in self.ruleset if rule.lhs() == pos]
                state = State(pos, '', transitions)
                self.states[pos.__str__()] = state


    def _extract_ruleset(self):
        """
        extract a set of grammar rules from the Penn Treebank
        strip the lexical items

        """
        # extract CFG on the parsed sentence object
        self.ruleset = [rule for tree in nltk.corpus.treebank.parsed_sents()
                                    for rule in tree.productions()
                                        if rule.is_nonlexical()]

    def _rule_freq(self):
        self.most_common_rules = nltk.FreqDist(self.ruleset).most_common(NUM_RULE)
        self.common_rules = nltk.FreqDist(self.ruleset).most_common(NUM_RULE*3)


    def _get_terminal_nodes(self):
        self.terminal_nodes = set(rule.lhs() for tree in nltk.corpus.treebank.parsed_sents()
                                    for rule in tree.productions()
                                        if rule.is_lexical())
