#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 20:51:52 2018

"""

from generator.grammar import Grammar
import unittest


class TestGrammar(unittest.TestCase):
    
    def test_next_transitions(self):
        grammar = Grammar()
        states = grammar.load_machine( 'states_test.txt' )
        self.assertEqual(set(states['V3'].transitions), {'NP2'})
        self.assertEqual(set(states['NNP'].transitions), {'V1'})
        self.assertEqual(list(states['V1'].transitions), ['NP2'])
        self.assertEqual(list(states['NNP2'].transitions), ['<END>'])
        self.assertEqual(list(states['D2'].transitions), ['Deg2'])
        self.assertEqual(list(states['Deg2'].transitions), ['A2'])
        self.assertEqual(list(states['A2'].transitions), ['N2'])
        self.assertEqual(list(states['CC'].transitions), ['<START>'])
        self.assertEqual(list(states['NP2'].transitions), ['A2', 'NNP2'])
        self.assertEqual(list(states['N2'].transitions), ['CC', '<END>'])
    
    def test_next_tag(self):
        grammar = Grammar()
        states = grammar.load_machine( 'states_test.txt' )
        self.assertEqual(states['NNPS'].pick_transition_simple(), 'V3')
        self.assertEqual(states['V3'].pick_transition_simple(), 'NP2')
        self.assertEqual(states['NNP'].pick_transition_simple(), 'V1')
        self.assertEqual(states['NNP2'].pick_transition_simple(), '<END>')
        self.assertEqual(states['A2'].pick_transition_simple(), 'N2')
        self.assertEqual(states['A3'].pick_transition_simple(), 'N4')
        self.assertEqual(states['Deg3'].pick_transition_simple(), 'A3')
        self.assertEqual(states['D3'].pick_transition_simple(), 'N3')
        self.assertEqual(states['CC'].pick_transition_simple(), '<START>')
        
    
    def test_output(self):
        grammar = Grammar()
        states = grammar.load_machine( 'states_test.txt' )
        self.assertEqual(states['V3'].output, 'VB')
        self.assertEqual(states['<START>'].output, '<NULL>')
        self.assertEqual(states['<END>'].output, '<NULL>')
        self.assertEqual(states['NP2'].output, '<NULL>')
        self.assertEqual(states['V'].output, 'VBD')
        self.assertEqual(states['V1'].output, 'VBZ')
        self.assertEqual(states['D1'].output, 'DT')
        self.assertEqual(states['CC'].output, 'CC')
        self.assertEqual(states['A3'].output, 'JJ')
        self.assertEqual(states['Deg2'].output, 'RB')

if __name__ == '__main__':        
    
    unittest.main()

