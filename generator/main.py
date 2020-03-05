import argparse
import os
import random
from dialogue import PlaySkeleton
from grammar import Grammar
from parse_play import Play
from vocabulary import Vocabulary

"""
Running python3 generator/main.py [SOURCE PLAY]
prints a generated play to standard output.
The optional flag --chartag specifies which tag is used in the source html
to specify a character, and --stagetag specifies the tag used
for stage directions.

To save a generated play based on "A Doll's House" as "doll_play.txt", run
>>>python3 generator/main.py source_plays/a_dolls_house.htm > doll_play.txt

To save a generated play based on "Hamlet" as "hamlet_play.txt", run:
>>>python3 generator/main.py source_plays/hamlet.htm --chartag=charname --stagetag=scenedesc > hamlet_play.txt
"""

parser = argparse.ArgumentParser()
parser.add_argument("filename", help="filename of play to parse")
parser.add_argument("--chartag", default="character", required=False,
                    help="tag in the html used to denote a character of the play")
parser.add_argument("--stagetag", default="stage-direction", required=False,
                    help="tag in the html used to denote stage directions")
args = parser.parse_args()
play = Play(args.filename, args.chartag, args.stagetag)
playskeleton = PlaySkeleton(play)

def num_sentences(line):
    return len(line.split("."))

speaker_vocab = {}
speaker_line_length = {}
for char in playskeleton.chars:
    #character-dependent vocabulary
    speaker_vocab[char] = Vocabulary()
    speaker_vocab[char].train(playskeleton.chars[char])

    #character-dependent line length
    speaker_line_length[char] = list(map(num_sentences, playskeleton.chars[char]))

cfg = Grammar()
states = cfg.load_machine(os.path.dirname(os.path.abspath(__file__)) + '/states.txt')

#generate random sentence based on vocabulary
def generate_sentence(vocab):
    template = cfg.make_template_simple(states)
    return vocab.build_sentence(template)

for act in playskeleton.skeleton:
    print(act[0] + "\n")
    speakers = act[1]
    for speaker in speakers:
        if speaker:
            #generate sentences based on speaker
            num_sentences = random.choice(speaker_line_length[speaker])
            print(speaker.upper() + ":")
            sentences = map(lambda i: generate_sentence(speaker_vocab[speaker]), range(num_sentences))
            print(" ".join(sentences) + "\n")
        else:
            #generate stage direction
            print("[" + generate_sentence(speaker_vocab[None]) + "]\n")
