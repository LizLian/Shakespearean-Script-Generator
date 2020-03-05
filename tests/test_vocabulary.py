import unittest

from generator.vocabulary import Vocabulary, START_SENTENCE


class TestVocabulary(unittest.TestCase):

    def test_train_single_utterance(self):
        vocab = Vocabulary()
        text = """The white cat saw the black cat in the night. 
        The black cat saw the white cat in the night."""
        vocab.train([text])

        cfd = vocab.freqs_by_features
        self.assertSetEqual(set(cfd.keys()),
                            {('<s>', '<s>', 'DT', 'JJ'),
                             ('the', 'DT', 'JJ', 'NN'),
                             ('white', 'JJ', 'NN', 'VBD'),
                             ('black', 'JJ', 'NN', 'VBD'),
                             ('white', 'JJ', 'NN', 'IN'),
                             ('black', 'JJ', 'NN', 'IN'),
                             ('cat', 'NN', 'VBD', 'DT'),
                             ('saw', 'VBD', 'DT', 'JJ'),
                             ('cat', 'NN', 'IN', 'DT'),
                             ('in', 'IN', 'DT', 'NN'),
                             ('the', 'DT', 'NN', '</s>')})
        self.assertSetEqual(set(cfd[('the', 'DT', 'JJ', 'NN')].keys()),
                            {'black', 'white'})
        self.assertSetEqual(set(cfd[('the', 'DT', 'NN', '</s>')].keys()),
                            {'night'})
        self.assertEqual(cfd[('the', 'DT', 'NN', '</s>')]['night'], 2)

    def test_train_different_character_utterances(self):
        vocab = Vocabulary()
        text1 = 'The white cat saw the black cat in the night.'
        text2 = 'The black cat saw the white cat in the night.'
        vocab.train([text1, text2])

        cfd = vocab.freqs_by_features
        self.assertSetEqual(set(cfd.keys()),
                            {('<s>', '<s>', 'DT', 'JJ'),
                             ('the', 'DT', 'JJ', 'NN'),
                             ('white', 'JJ', 'NN', 'VBD'),
                             ('black', 'JJ', 'NN', 'VBD'),
                             ('white', 'JJ', 'NN', 'IN'),
                             ('black', 'JJ', 'NN', 'IN'),
                             ('cat', 'NN', 'VBD', 'DT'),
                             ('saw', 'VBD', 'DT', 'JJ'),
                             ('cat', 'NN', 'IN', 'DT'),
                             ('in', 'IN', 'DT', 'NN'),
                             ('the', 'DT', 'NN', '</s>')})
        self.assertSetEqual(set(cfd[('the', 'DT', 'JJ', 'NN')].keys()),
                            {'black', 'white'})
        self.assertSetEqual(set(cfd[('the', 'DT', 'NN', '</s>')].keys()),
                            {'night'})
        self.assertEqual(cfd[('the', 'DT', 'NN', '</s>')]['night'], 2)

    def test_random_word_when_only_one(self):
        vocab = Vocabulary()
        text = """The black cat saw a white cat in the night. 
           The white cat was easy to see."""
        vocab.train([text])

        word = vocab.random_word(START_SENTENCE, START_SENTENCE, 'DT', 'NN')
        self.assertEqual(word, 'the')

    def test_random_word_when_prev_tag_not_found(self):
        vocab = Vocabulary()
        text = """The black cat saw a white cat. 
              The white cat was easy to see."""
        vocab.train([text])

        word = vocab.random_word(START_SENTENCE, START_SENTENCE, 'NN', 'VBD')
        self.assertEqual(word, 'cat')

    def test_random_word_when_tag_not_found(self):
        vocab = Vocabulary()
        text = """The black cat saw a white cat. 
              The white cat saw the black cat."""
        vocab.train([text])

        word = vocab.random_word('night', 'NN', 'RB', 'RB')
        self.assertEqual(word, 'cat')

    def test_random_word_when_two(self):
        vocab = Vocabulary()
        text = """The black cat saw a white cat in the black night. 
        The black night was darker than usual."""
        vocab.train([text])

        random_noun = vocab.random_word('black', 'JJ', 'NN', 'VBD')
        self.assertTrue(random_noun == 'cat' or random_noun == 'night')

    def test_tags_to_random_words(self):
        vocab = Vocabulary()
        text = """The black cat saw the white cat. 
                   The white cat was easy to see."""
        vocab.train([text])

        words = vocab.tags_to_random_words(['<s>', 'DT', 'NN'])
        self.assertListEqual(words, ['the', 'cat'])

    def test_build_sentence_basic(self):
        vocab = Vocabulary()
        text = "The black cat was very cold."
        vocab.train([text])

        sentence = vocab.build_sentence(['<s>', 'DT', 'JJ', 'NN', 'VBD',
                                         'RB', 'JJ', '</s>'])
        self.assertEqual(sentence, text)

    def test_build_sentence_with_comma(self):
        vocab = Vocabulary()
        text = "The black cat was very cold, and looked quite sad."
        vocab.train([text])

        sentence = vocab.build_sentence(['<s>', 'DT', 'JJ', 'NN', 'VBD',
                                         'RB', 'JJ', ',', 'CC', 'VBD',
                                         'RB', 'JJ', '</s>'])
        self.assertEqual(sentence, text)

    def test_build_sentence_with_proper_noun(self):
        vocab = Vocabulary()
        text = "The black cat was very cold, and said so to Emma."
        vocab.train([text])

        sentence = vocab.build_sentence(['<s>', 'DT', 'JJ', 'NN', 'VBD',
                                         'RB', 'JJ', ',', 'CC', 'VBD',
                                         'RB', 'TO', 'NNP', '</s>'])
        self.assertEqual(sentence, text)

    def test_tokenize_by_sentence_for_single_sentence(self):
        vocab = Vocabulary()
        utterance = 'It was a dark and dreary morning.'

        sentences = vocab._tokenize_by_sentence(utterance)

        self.assertEqual(len(sentences), 1)
        self.assertEqual(sentences[0],
                         ['It', 'was', 'a', 'dark', 'and', 'dreary', 'morning',
                          '.'])

    def test_tokenize_by_sentence_for_multiple_sentences(self):
        vocab = Vocabulary()
        utterance = 'To be. Or not to be?'

        sentences = vocab._tokenize_by_sentence(utterance)

        self.assertEqual(len(sentences), 2)
        self.assertEqual(sentences[0], ['To', 'be', '.'])
        self.assertEqual(sentences[1],
                         ['Or', 'not', 'to', 'be', '?'])

    def test_tokenize_by_sentence_with_line_breaks(self):
        vocab = Vocabulary()
        utterance = 'To be. Or not\nto be?'

        sentences = vocab._tokenize_by_sentence(utterance)

        self.assertEqual(len(sentences), 2)
        self.assertEqual(sentences[0], ['To', 'be', '.'])
        self.assertEqual(sentences[1],
                         ['Or', 'not', 'to', 'be', '?'])


if __name__ == '__main__':
    unittest.main()
