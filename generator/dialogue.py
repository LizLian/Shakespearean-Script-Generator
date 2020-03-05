from nltk.util import ngrams
import random
from parse_play import Play

def flatten(L):
    return [item for sublist in L for item in sublist]

class PlaySkeleton:
    """
    An outline for a play.
    Lists acts, and sequences of characters within each act.
    The sequence of characters represents speakers of ongoing dialogue.
    Acts and character sequences are generated based on an input play.
    >>> playskeleton = PlaySkeleton(play)
    """

    def __init__(self, play):
        self._source_lines = play.lines
        #maps character to lines spoken by char
        self.chars = {}
        for char in play.chars:
            self.chars[char] = self.lines_by_char(char)
        self.acts = play.acts
        #maps acts to sequences of speaking chars
        self.skeleton = []
        for act in play.acts:
            self.skeleton.append((act[1], self.speaker_chain_for_act(act[0])))

    #creates new sequence of speakers for given act
    def speaker_chain_for_act(self, act):
        act_lines = filter(lambda line: line.act == act, self._source_lines)
        act_speakers = list(map(lambda line: line.speaker, act_lines))
        return self.generate_speaker_chain(act_speakers)

    #gets all lines spoken by given character
    def lines_by_char(self, char):
        char_lines = filter(lambda line: line.speaker == char, self._source_lines)
        if char:
            return list(map(lambda line: line.line, char_lines))
        else:
            #stage directions
            return flatten(map(lambda line: line.stage_direction, char_lines))


    #predicts with bigrams sequence of speakers
    def generate_speaker_chain(self, speakers):
        bigrams = list(ngrams(speakers, 2))
        generated_speakers = [random.choice(bigrams)[0]]
        for i in range(0, len(speakers)-1):
            last_speaker = generated_speakers[-1]
            bigrams_for_speaker = list(filter(lambda b: b[0] == last_speaker, bigrams))
            if bigrams_for_speaker:
                #choose bigram based on previous speaker
                generated_speakers.append(random.choice(bigrams_for_speaker)[1])
            else:
                #no bigram starts with previous speaker
                generated_speakers.append(random.choice(bigrams)[0])
        return generated_speakers
