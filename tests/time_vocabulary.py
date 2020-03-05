import time

import nltk

from generator.vocabulary import Vocabulary, START_SENTENCE, END_SENTENCE


class TimeVocabulary:

    def time_emma(self):
        emma_raw_text = nltk.corpus.gutenberg.raw('austen-emma.txt')

        time_before = time.perf_counter()
        vocab = Vocabulary()
        vocab.train([(emma_raw_text)])
        time_after_training = time.perf_counter()

        sentence_tags = [START_SENTENCE, 'DT', 'JJ', 'NN', 'VBZ', 'DT', 'NN',
                         'IN', 'DT', 'NN', END_SENTENCE]
        sentences = []
        count = 10
        for i in range(0, count):
            sentence = vocab.build_sentence(sentence_tags)
            sentences.append(sentence)

        time_after_sentence = time.perf_counter()

        diff_training = time_after_training - time_before
        diff_sentence = time_after_sentence - time_after_training
        print('Time to train on Emma:', diff_training, 'seconds')
        print('Time to generate', count, 'sentences:', diff_sentence)
        print('Sentences generated:')
        for sentence in sentences:
            print(sentence)


if __name__ == '__main__':
    timer = TimeVocabulary()
    timer.time_emma()
