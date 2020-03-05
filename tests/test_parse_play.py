#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from generator.parse_play import Line, Play
from bs4 import BeautifulSoup
import os
import unittest

play_dir = os.path.dirname(os.path.abspath(__file__)) + '/source_plays/'

def soup(line):
    return BeautifulSoup(line, 'html.parser')

line1 = """
        <p>HAMLET.<br/>
        [<i>Advancing.</i>]<br/>
        What is he whose grief<br/>
        Bears such an emphasis? whose phrase of sorrow<br/>
        Conjures the wand&rsquo;ring stars, and makes them stand<br/>
        Like wonder-wounded hearers? This is I,<br/>
        Hamlet the Dane.<br/>
        [<i>Leaps into the grave.</i>]<br/>
        </p>
        """
line2 = """
        <p>HAMLET.<br/>
        Thou pray&rsquo;st not well.<br/>
        I prythee take thy fingers from my throat;<br/>
        For though I am not splenative and rash,<br/>
        Yet have I in me something dangerous,<br/>
        Which let thy wiseness fear. Away thy hand!<br/>
        </p>
        """
line3 = """
        <p>QUEEN.<br/>
        Hamlet! Hamlet!<br/>
        </p>
        """
line4 = """
        <p>HORATIO.<br/>
        Good my lord, be quiet.<br/>
        </p>
        """
line5 = """
        <p class="right"> [<i>The <span class="charname">Attendants</span> part them,
        and they come out of the grave.</i>]</p>
        """
line6 = """
        <p>
        <span class="character">Nora </span><span class="stage-direction">[disengages
        herself, and says firmly and decidedly]</span>. Now you must read your
        letters, Torvald.
        </p>
        """
line7 = """
        <p>
        <span class="character">Helmer</span>. No, no; not tonight. I want to be
        with you, my darling wife.
        </p>
        """
line8 = """
        <p>
          <span class="character">Maid</span>. Very well, sir. <span
          class="stage-direction">[Exit with the letter.]</span>
        </p>
        """

class TestLine(unittest.TestCase):
    ham_chars = ["HAMLET", "CLAUDIUS", "KING", "GHOST", "QUEEN", "POLONIUS",
                 "LAERTES",  "OPHELIA",  "HORATIO", "FORTINBRAS",
                 "VOLTEMAND", "CORNELIUS", "ROSENCRANTZ", "GUILDENSTERN",
                 "MARCELLUS", "BARNARDO", "FRANCISCO", "OSRIC", "REYNALDO"]
    doll_chars = ["Helmer", "Nora", "Doctor Rank", "Mrs Linde",
                  "Nils Krogstad", "Helmer's three young children", "Anne",
                  "A Housemaid", "A Porter"]

    def hamtestline(self):
        return Line("sceneV_2", soup(line1), "charname", "scenedesc", self.ham_chars)
    def dolltestline(self):
        return Line("act1", soup(line6), "character", "stage-direction", self.doll_chars)

    def test_get_speaker(self):
        self.assertEqual(self.hamtestline().get_speaker(soup(line1), self.ham_chars), "HAMLET")
        self.assertEqual(self.hamtestline().get_speaker(soup(line2), self.ham_chars), "HAMLET")
        self.assertEqual(self.hamtestline().get_speaker(soup(line3), self.ham_chars), "QUEEN")
        self.assertEqual(self.hamtestline().get_speaker(soup(line4), self.ham_chars), "HORATIO")
        self.assertEqual(self.hamtestline().get_speaker(soup(line5), self.ham_chars), None)
        self.assertEqual(self.dolltestline().get_speaker(soup(line6), self.doll_chars), "Nora")
        self.assertEqual(self.dolltestline().get_speaker(soup(line7), self.doll_chars), "Helmer")
        self.assertEqual(self.dolltestline().get_speaker(soup(line8), self.doll_chars), "Maid")

    def test_get_stage_direction(self):
        self.assertEqual(self.hamtestline().get_stage_direction(soup(line1)),
                         ["Advancing.", "Leaps into the grave."])
        self.assertEqual(self.hamtestline().get_stage_direction(soup(line2)), [])
        self.assertEqual(self.hamtestline().get_stage_direction(soup(line3)), [])
        self.assertEqual(self.hamtestline().get_stage_direction(soup(line4)), [])
        self.assertEqual(self.hamtestline().get_stage_direction(soup(line5)),
                         ["The Attendants part them, and they come out of the grave."])
        self.assertEqual(self.dolltestline().get_stage_direction(soup(line6)),
                         ["disengages herself, and says firmly and decidedly"])
        self.assertEqual(self.dolltestline().get_stage_direction(soup(line7)), [])
        self.assertEqual(self.dolltestline().get_stage_direction(soup(line8)),
                         ["Exit with the letter."])

    def test_get_line(self):
        self.assertEqual(self.hamtestline().get_line(soup(line1)),
                         "What is he whose grief Bears such an emphasis? whose phrase of sorrow Conjures the wand’ring stars, and makes them stand Like wonder-wounded hearers? This is I, Hamlet the Dane.")
        self.assertEqual(self.hamtestline().get_line(soup(line2)),
                         "Thou pray’st not well. I prythee take thy fingers from my throat; For though I am not splenative and rash, Yet have I in me something dangerous, Which let thy wiseness fear. Away thy hand!")
        self.assertEqual(self.hamtestline().get_line(soup(line3)),
                         "Hamlet! Hamlet!")
        self.assertEqual(self.hamtestline().get_line(soup(line4)),
                         "O. Good my lord, be quiet.")
        self.assertEqual(self.hamtestline().get_line(soup(line5)), "")
        self.assertEqual(self.dolltestline().get_line(soup(line6)),
                         "Now you must read your letters, Torvald.")
        self.assertEqual(self.dolltestline().get_line(soup(line7)),
                         "No, no; not tonight. I want to be with you, my darling wife.")
        self.assertEqual(self.dolltestline().get_line(soup(line8)),
                         "Very well, sir.")

class TestPlay(unittest.TestCase):

    hamtestplay = Play(play_dir + "hamlet.htm", "charname", "scenedesc")
    dolltestplay = Play(play_dir + "a_dolls_house.htm", "character", "stage-direction")
    with open(play_dir + "hamlet.htm") as f:
        hamlet_soup = soup(f.read())
    with open(play_dir + "a_dolls_house.htm") as f:
        doll_soup = soup(f.read())

    def test_in_act(self):
        self.assertEqual(self.hamtestplay.in_act(soup('<p class="scene"><a name="sceneV_2" id="sceneV_2"></a></p>')), False)
        self.assertEqual(self.hamtestplay.in_act(soup(line2)), True)
        self.assertEqual(self.hamtestplay.in_act(soup(line3)), True)
        self.assertEqual(self.dolltestplay.in_act(soup(line6)), True)
        self.assertEqual(self.dolltestplay.in_act(soup(line7)), True)
        self.assertEqual(self.dolltestplay.in_act(soup('<p><br /> <br /> <a name="act2" id="act2"></a></p>')), False)

    def test_get_acts(self):
        self.assertEqual(self.hamtestplay.get_acts(self.hamlet_soup),
                         [('sceneI_1', 'Scene I.'), ('sceneI_2', 'Scene II.'),
                          ('sceneI_3', 'Scene III.'), ('sceneI_4', 'Scene IV.'),
                          ('sceneI_5', 'Scene V.'), ('sceneII_1', 'Scene I.'),
                          ('sceneII_2', 'Scene II.'), ('sceneIII_1', 'Scene I.'),
                          ('sceneIII_2', 'Scene II.'), ('sceneIII_3', 'Scene III.'),
                          ('sceneIII_4', 'Scene IV.'), ('sceneIV_1', 'Scene I.'),
                          ('sceneIV_2', 'Scene II.'), ('sceneIV_3', 'Scene III.'),
                          ('sceneIV_4', 'Scene IV.'), ('sceneIV_5', 'Scene V.'),
                          ('sceneIV_6', 'Scene VI.'), ('sceneIV_7', 'Scene VII.'),
                          ('sceneV_1', 'Scene I.'), ('sceneV_2', 'Scene II.')])
        self.assertEqual(self.dolltestplay.get_acts(self.doll_soup),
                         [('act1', 'ACT I.'), ('act2', 'ACT II.'), ('act3', 'ACT III.')])

    def test_get_characters(self):
        ham_chars = self.hamtestplay.get_characters(self.hamlet_soup)
        doll_chars = self.dolltestplay.get_characters(self.doll_soup)
        self.assertTrue(set(['Ophelia', 'Cornelius', 'Clowns', 'Hamlet', 'Sailors', 'Polonius', 'Attendants']).issubset(set(ham_chars)))
        self.assertTrue(set(['Nora', 'Rank', 'Servant', 'Anne', 'Krogstad']).issubset(set(doll_chars)))

if __name__ == '__main__':

    unittest.main()
