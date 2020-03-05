import re
from collections import defaultdict
from typing import List, Dict, Tuple

import nltk

START_SENTENCE = '<s>'
END_SENTENCE = '</s>'

USE_NEXT_TAG = True


class Vocabulary:
    """
    A trainable vocabulary which can populate sentences given the tag sequence
    for that sentence.

    Train it on a given corpus (which can be passed as an array of raw text
    strings, useful if it is coming from a play), then call build_sentence
    for each desired tag sequence representing a sentence.

    >>> vocab = Vocabulary()
    >>> vocab.train(['Some raw text.', 'More text. It has many sentences!'])
    >>> vocab.build_sentence(['DT', 'NN', 'VBZ', 'JJ', 'NNS'])
    >>> 'Some text has many sentences.'

    """

    def __init__(self):
        self.labels_by_features: Dict[Tuple, List[str]] = None
        self.labels_by_tags: Dict[Tuple, List[str]] = None
        self.labels_by_prev_tag: Dict[Tuple, List[str]] = None
        self.labels_by_tag: Dict[str, List[str]] = None

        self.freqs_by_features: Dict[Tuple, nltk.FreqDist] = None
        self.freqs_by_tags: Dict[Tuple, nltk.FreqDist] = None
        self.freqs_by_prev_tag: Dict[Tuple, nltk.FreqDist] = None
        self.freqs_by_tag: Dict[str, nltk.FreqDist] = None

        self.probs_by_features: Dict[Tuple, nltk.MLEProbDist] = None
        self.probs_by_tags: Dict[Tuple, nltk.MLEProbDist] = None
        self.probs_by_prev_tag: Dict[Tuple, nltk.MLEProbDist] = None
        self.probs_by_tag: Dict[str, nltk.MLEProbDist] = None

    def train(self, utterances: List[str]):
        """
        Train the vocabulary on a list of utterances, each of which is just
        a raw string of text. It's useful to take a list of raw text because
        a play will have one utterance per character rather than a continuous
        stream of sentences. However, passing in a list containing a single
        string with all the data works equally well.

        :param utterances: a list of utterances, i.e. a list of raw text strings
        :return: (the vocabulary updates its state)
        """
        self._populate_labelled_features(utterances)
        self._create_freqs()
        self._create_probabilities()
        self._clear_labelled_features()  # Tidy up to save memory

    def build_sentence(self, tag_sequence: List[str]):
        """
        Populate a syntactic tree given by the sequence of its terminal nodes,
        and return that as a sentence.
        If the list of tags does not start and end with START_SENTENCE and
        END_SENTENCE, these will be added.

        :param tag_sequence: the sequence of tags to fill
        :return: a sentence as a string (capitalised and with a period).
        """
        words = self.tags_to_random_words(tag_sequence)
        words[0] = words[0].capitalize()
        sentence = ' '.join(words)
        sentence = re.sub(r'\s([,;:])', r'\1', sentence)
        sentence += '.'
        return sentence

    def tags_to_random_words(self, tag_sequence: List[str]):
        """
        Map a list of terminal nodes of a syntactic tree / a sequence of tags
        to a sequence of words corresponding to those tags

        :param tag_sequence: the sequence of tags to fill
        :return: a list of words, lowercased.
        """
        words = []
        if tag_sequence[0] != START_SENTENCE:
            tag_sequence.insert(0, START_SENTENCE)
        if tag_sequence[-1] != END_SENTENCE:
            tag_sequence.append(END_SENTENCE)
        for prev_tag, tag, next_tag in zip(tag_sequence[:-2],
                                           tag_sequence[1:-1],
                                           tag_sequence[2:]):
            prev_word = words[-1] if len(words) > 0 else START_SENTENCE
            words.append(self.random_word(prev_word, prev_tag, tag, next_tag))
        return words

    def random_word(self, previous_word: str, previous_tag: str, tag: str,
                    next_tag: str):
        """
        Return a randomly generated word of the specified category that is
        known to follow the previous tag. Chooses from words in the training
        corpus, based on their relative frequencies. (Higher frequency words
        are more likely to be returned.)

        :param previous_word: the previous word (use START_SENTENCE if none)
        :param previous_tag: the tag of the previous word
         (use START_SENTENCE if none)
        :param tag: the tag to fill
        :param next_tag: the tag following this word (use END_SENTENCE if none)
        :return: a randomly chosen word that fits this situation
        """
        self._assert_trained()
        prob_dist = self._get_best_prob_dist(previous_word, previous_tag, tag,
                                             next_tag)
        return prob_dist.generate()

    def _populate_labelled_features(self, utterances):
        self.labels_by_features = defaultdict(list)
        self.labels_by_tags = defaultdict(list)
        self.labels_by_prev_tag = defaultdict(list)
        self.labels_by_tag = defaultdict(list)

        for utterance in utterances:
            sentences = self._tokenize_by_sentence(utterance)
            for sentence in sentences:
                tagged_sentence: List[Tuple] = nltk.pos_tag(
                    sentence)

                tagged_sentence.insert(0, (START_SENTENCE, START_SENTENCE))
                if tagged_sentence[-1][1] == '.':
                    # Remove last period since we're using END_SENTENCE
                    tagged_sentence[-1:] = []
                tagged_sentence.append((END_SENTENCE, END_SENTENCE))

                # Ignore last item as it will always be punctuation
                for prev_tagged_word, tagged_word, (next_word, next_tag) \
                        in zip(tagged_sentence[:-2], tagged_sentence[1:-1],
                               tagged_sentence[2:]):
                    self._add_to_labelled_features(tagged_word,
                                                   prev_tagged_word, next_tag)

    def _tokenize_by_sentence(self, utterance):
        raw_sentences = nltk.sent_tokenize(utterance)
        sentences: List[str] = [nltk.word_tokenize(sentence)
                                for sentence in raw_sentences]
        return sentences

    def _add_to_labelled_features(self, tagged_word, prev_tagged_word,
                                  next_tag):
        tag = tagged_word[1]
        # Assume that capitalised words are proper names unless they
        # are at the start of a sentence
        word = tagged_word[0].lower() \
            if prev_tagged_word[1] == START_SENTENCE else tagged_word[0]

        # This won't be output so keep this lowercased
        prev_word = prev_tagged_word[0].lower()
        prev_tag = prev_tagged_word[1]
        features = (prev_word, prev_tag, tag, next_tag) if USE_NEXT_TAG \
            else (prev_word, prev_tag, tag)
        self.labels_by_features[features].append(word)
        if USE_NEXT_TAG:
            self.labels_by_tags[(prev_tag, tag, next_tag)].append(word)
        self.labels_by_prev_tag[(prev_tag, tag)].append(word)
        self.labels_by_tag[tag].append(word)

    def _clear_labelled_features(self):
        self.labels_by_features = None
        self.labels_by_tag = None
        self.labels_by_prev_tag = None
        self.labels_by_tag = None

    def _create_freqs(self):
        self.freqs_by_features = {features: nltk.FreqDist(labels)
                                  for (features, labels) in
                                  self.labels_by_features.items()}
        if USE_NEXT_TAG:
            self.freqs_by_tags = {features: nltk.FreqDist(labels)
                                  for (features, labels) in
                                  self.labels_by_tags.items()}
        self.freqs_by_prev_tag = {features: nltk.FreqDist(labels)
                                  for (features, labels) in
                                  self.labels_by_prev_tag.items()}
        self.freqs_by_tag = {tag: nltk.FreqDist(labels)
                             for (tag, labels) in
                             self.labels_by_tag.items()}

    def _create_probabilities(self):
        self.probs_by_features = {features: nltk.MLEProbDist(freq_dist)
                                  for (features, freq_dist)
                                  in self.freqs_by_features.items()}
        if USE_NEXT_TAG:
            self.probs_by_tags = {features: nltk.MLEProbDist(freq_dist)
                                  for (features, freq_dist)
                                  in self.freqs_by_tags.items()}
        self.probs_by_prev_tag = {prev_features: nltk.MLEProbDist(freq_dist)
                                  for (prev_features, freq_dist) in
                                  self.freqs_by_prev_tag.items()}
        self.probs_by_tag = {tag: nltk.MLEProbDist(freq_dist)
                             for (tag, freq_dist) in
                             self.freqs_by_tag.items()}

    def _get_best_prob_dist(self, prev_word, prev_tag, tag, next_tag):
        # We only use lowercase for lookup
        prev_word = prev_word.lower()

        features = (prev_word, prev_tag, tag, next_tag) if USE_NEXT_TAG \
            else (prev_word, prev_tag, tag)
        if features \
                in self.probs_by_features.keys():
            prob_dist = self.probs_by_features[
                features]
        elif USE_NEXT_TAG and (prev_tag, tag, next_tag) in self.probs_by_tags.keys():
            # Try just the tags
            prob_dist = self.probs_by_tags[(prev_tag, tag, next_tag)]
        elif (prev_tag, tag) in self.probs_by_prev_tag.keys():
            # Try just the tag plus previous tag
            prob_dist = self.probs_by_prev_tag[(prev_tag, tag)]
        elif tag in self.probs_by_tag.keys():
            # Try just the current tag
            prob_dist = self.probs_by_tag[tag]
        elif 'NN' in self.probs_by_tag.keys():
            # Fall back to assuming the unknown tag is a noun
            prob_dist = self.probs_by_tag['NN']
        else:
            # Our training data was terrible! Just grab something
            some_tag = list(self.probs_by_tag.keys())[0]
            prob_dist = self.probs_by_tag[some_tag]
        return prob_dist

    def _assert_trained(self):
        if self.probs_by_features is None:
            raise RuntimeError('You need to train the vocabulary on a corpus '
                               'before you can call this method')
