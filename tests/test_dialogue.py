#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from generator.dialogue import PlaySkeleton
from generator.parse_play import Play
import os
import unittest

play_dir = os.path.dirname(os.path.abspath(__file__)) + '/source_plays/'

class TestPlaySkeleton(unittest.TestCase):

    hamtestplay = Play(play_dir + "hamlet.htm", "charname", "scenedesc")
    dolltestplay = Play(play_dir + "a_dolls_house.htm", "character", "stage-direction")
    hamtestplayskeleton = PlaySkeleton(hamtestplay)
    dolltestplayskeleton = PlaySkeleton(dolltestplay)

    def test_generate_speaker_chain(self):
        self.assertEqual(self.hamtestplayskeleton.generate_speaker_chain(['Hamlet','Hamlet','Hamlet']),
                          ['Hamlet','Hamlet','Hamlet'])
        self.assertEqual(self.hamtestplayskeleton.generate_speaker_chain(['Ghost','Ghost','Ghost']),
                          ['Ghost','Ghost','Ghost'])
        self.assertEqual(self.dolltestplayskeleton.generate_speaker_chain(['Nora','Nora']),
                          ['Nora','Nora'])

    def test_speaker_chain_for_act(self):
        ham_chars = self.hamtestplay.chars
        ham_chars.add(None)
        doll_chars = self.dolltestplay.chars
        doll_chars.add(None)
        self.assertTrue(set(self.hamtestplayskeleton.speaker_chain_for_act('sceneIV_3')).issubset(ham_chars), True)
        self.assertTrue(set(self.dolltestplayskeleton.speaker_chain_for_act('act1')).issubset(doll_chars), True)

    def test_lines_by_char(self):
        hamline1 = "What is he whose grief Bears such an emphasis? whose phrase of sorrow Conjures the wand’ring stars, and makes them stand Like wonder-wounded hearers? This is I, Hamlet the Dane."
        hamline2 = "Thou pray’st not well. I prythee take thy fingers from my throat; For though I am not splenative and rash, Yet have I in me something dangerous, Which let thy wiseness fear. Away thy hand!"
        hamline3 = "Hamlet! Hamlet!"
        dollline1 = "Now you must read your letters, Torvald."
        dollline2 = "No, no; not tonight. I want to be with you, my darling wife."
        self.assertTrue(hamline1 in self.hamtestplayskeleton.lines_by_char('Hamlet'))
        self.assertTrue(hamline2 in self.hamtestplayskeleton.lines_by_char('Hamlet'))
        self.assertTrue(hamline3 in self.hamtestplayskeleton.lines_by_char('Queen'))
        self.assertTrue(dollline1 in self.dolltestplayskeleton.lines_by_char('Nora'))
        self.assertTrue(dollline2 in self.dolltestplayskeleton.lines_by_char('Helmer'))

if __name__ == '__main__':

    unittest.main()
