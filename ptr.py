import math
from math import sqrt, log
from collections import Counter
import nltk
from nltk import Tree, Production, Nonterminal, CFG, ChartParser
from nltk.parse.stanford import StanfordParser
import textacy
import pyphen  # hyphenation library
from matplotlib import pyplot as plt
from numpy import matrix, corrcoef

pyphen.language_fallback('en_US')
dic = pyphen.Pyphen(lang='en_US')

# Helper methods


def tag_sentence(sentence):
    """A helper method to easily tokenize a sentence"""
    return nltk.pos_tag(nltk.word_tokenize(sentence))


def tag_sentences(sentences):
    """A helper method to easily tokenize sentences"""
    return [tag_sentence(sent) for sent in nltk.sent_tokenize(sentences)]


def untag_sentence(tagged_sentence):
    """Get back the original text of a sentence."""
    leading_tags = set(
        ['(', '$', '``'])  # don't need a space after, but do before
    following_tags = set([')', ',', '.', ':', "''", 'POS']
                         )  # need a space after, but not before
    sentence = ''
    no_sp = False
    for w, pos in tagged_sentence:
        if pos != '-NONE-':
            if pos in following_tags or w in {'%'}:
                sentence += w
            else:
                sentence += ('' if no_sp else ' ') + w
            no_sp = pos in leading_tags
    return sentence[1:]  # ignore leading space


def untag_sentences(tagged_sentences):
    """Get back the original text of sentences."""
    return [untag_sentence(tagged_sentence)
            for tagged_sentence in tagged_sentences]


class TextStats:
    """
    Determines basic text statistics, such as word length, syllabification,
    etc. Additionally, computes several standard measures of readability.
    """

    def __init__(self, corpus):
        global dic
        punct_tags = set(['(', ')', ',', '--', '.', ':',
                          '-NONE-', '``', "''", '$'])

        if not dic:
            pyphen.language_fallback('en_US')
            dic = pyphen.Pyphen(lang='en_US')

        f = open('dale-chall.txt')
        dale_long_list = [word.lower() for word in f.read().split()]
        f.close()

        # The corpus is a tagged sentence or list of tagged sentences
        self.corpus = [corpus] if isinstance(corpus[0], tuple) else corpus
        self.depunctuated = [[(word, tag) for word, tag in sentence
                              if tag not in punct_tags]
                             for sentence in self.corpus]
        self.stats = []
        for sentence in self.depunctuated:
            n = max(len(sentence), 1)
            word_lengths = [len(word) for word, tag in sentence]
            syllables = [len(dic.positions(word)) + 1
                         for word, tag in sentence]
            self.stats.append({
                'n_words': n,
                'n_chars': sum(word_lengths),
                'avg_word_length': sum(word_lengths) / n,
                'n_syllables': sum(syllables),
                'monosyllable_words': sum(s == 1 for s in syllables),
                'polysyllable_words': sum(s >= 3 for s in syllables),
                'n_long': sum(1 for word, POS in sentence
                              if word.lower() in dale_long_list),
            })

    def get_stats(self):
        n_s = len(self.corpus)

        return {
            'n_sentences': n_s,
            'n_words': sum(stat['n_words'] for stat in self.stats),
            'n_chars': sum(stat['n_chars'] for stat in self.stats),
            'n_syllables': sum(stat['n_syllables'] for stat in self.stats),
            'n_monosyllable_words': sum(stat['monosyllable_words']
                                        for stat in self.stats),
            'n_polysyllable_words': sum(stat['polysyllable_words']
                                        for stat in self.stats),
            'n_long': sum(stat['n_long'] for stat in self.stats),

        }

    def readabilities(self):
        return {
            'SMOG': self.SMOG(),
            'flesch_kincaid_grade_level': self.flesch_kincaid_grade_level(),
            'dale_chall': self.dale_chall(),
        }

    def SMOG(self):
        """
        Computes the SMOG score of a piece of text, in this case, a list of
        tagged sentences. There should be at least 30 sentences in the text.

        McLaughlin, G. Harry (May 1969). "SMOG Grading — a New Readability
        Formula" (PDF). Journal of Reading. 12 (8): 639–646.
        """
        n_sentences = len(self.corpus)
        n_polysyllables = sum(stat['polysyllable_words']
                              for stat in self.stats)
        return 1.0430 * sqrt(n_polysyllables * (30 / n_sentences)) + 3.1291

    def flesch_kincaid_grade_level(self):
        """
        Computes the Flesch-Kincaid grade level of a piece of text, in this case,
        a list of tagged sentences.

        Kincaid JP, Fishburne RP Jr, Rogers RL, Chissom BS (February 1975).
        "Derivation of new readability formulas (Automated Readability Index,
        Fog Count and Flesch Reading Ease Formula) for Navy enlisted personnel".
        Research Branch Report 8-75, Millington, TN: Naval Technical Training,
        U. S. Naval Air Station, Memphis, TN.
        """
        n_sentences = len(self.corpus)
        n_words = sum(stat['n_words'] for stat in self.stats)
        n_syllables = sum(stat['n_syllables'] for stat in self.stats)
        return 0.39 * (n_words / n_sentences) + \
            11.8 * (n_syllables / n_words) - 15.59

    def dale_chall(self):
        """
        Computes the Dale-Chall Formula for readability, 1961 revision, for a
        list of tagged sentences.

        McCallum, D. and Peterson, J. (1982), Computer-Based Readability
        Indexes, Proceedings of the ACM '82 Conference, (October 1982), 44-48.
        """
        f = open('dale-chall.txt')
        dale_long_list = [word.lower() for word in f.read().split()]
        f.close()

        n_dale_long = sum(1 for sentence in self.depunctuated
                          for word, POS in sentence
                          if word.lower() in dale_long_list)

        n_sentences = len(self.corpus)
        n_words = sum(stat['n_words'] for stat in self.stats)

        grade = 14.863 - 11.42 * (n_dale_long / n_words) + \
            0.0512 * (n_words / n_sentences)
        return grade


class TagStats:
    """
    Determines tag-based statistics, such as POS counts, etc.
    """

    def __init__(self, corpus):
        def n_repeated_possessives(tagged_sentence):
            """
            The number of 2+ repeated possessives, e.g.:
            "John's mother's neighbor's uncle's dog's Instagram account" -> 5
            "John's dog's Instagram account" -> 2
            "John's Instagram account" -> 0  # because it's not repeated
            """
            max_count = 0

            count, loc = 0, -1
            for i, (word, pos) in enumerate(tagged_sentence[::2]):
                if pos == 'POS':
                    count = count + 1 if (loc == i - 1) else 1
                    max_count = max(max_count, count)
                    loc = i

            count, loc = 0, -1
            for i, (word, pos) in enumerate(tagged_sentence[1::2]):
                if pos == 'POS':
                    count = count + 1 if (loc == i - 1) else 1
                    max_count = max(max_count, count)
                    loc = i

            return max_count if max_count >= 2 else 0

        def n_repeated_adverbs(tagged_sentence):
            """
            The number of 2+ repeated adverbs (RB, RBR, and RBS/RBT) e.g.:
            "harder better faster stronger" -> 4  # as adverbs, not adjectives!
            "most happily" -> 2
            "likely ready" -> 0  # because "ready" is an adjective
            """
            adverbs = {'RB', 'RBR', 'RBS', 'RBT', 'RB$',
                       'RB+BEZ', 'RB+CS', 'RBR+CS', 'RN', 'RP'}
            max_count = 0
            count, loc = 0, -1
            for i, (word, pos) in enumerate(tagged_sentence):
                if pos in adverbs:
                    count = count + 1 if (loc == i - 1) else 1
                    max_count = max(max_count, count)
                    loc = i

            return max_count if max_count >= 2 else 0

        # the corpus is a tagged sentence or list of tagged sentences
        self.corpus = [corpus] if isinstance(corpus[0], tuple) else corpus
        self.stats = []

        for sentence in self.corpus:
            self.stats.append({
                'n_POSs': len(set(pos for word, pos in sentence)),
                'n_pronouns':
                    len([pos for word, pos in sentence if pos == 'PRP']),
                'n_repeated_possessives': n_repeated_possessives(sentence),
                'n_repeated_adverbs': n_repeated_adverbs(sentence),
            })

        self.POSs = [set(pos for word, pos in sentence)
                     for sentence in self.corpus]

    def get_stats(self):
        """Combine all the statistics together"""
        ...
        n = len(self.stats)
        return {
            'total_POSs': len({POS for POSs in self.POSs for POS in POSs}),
            'avg_POSs': sum(stat['n_POSs'] for stat in self.stats) / n,
            'avg_pronouns': sum(stat['n_pronouns'] for stat in self.stats) / n,
            'avg_repeated_possessives':
                sum(stat['n_repeated_possessives'] for stat in self.stats) / n,
            'avg_repeated_adverbs':
                sum(stat['n_repeated_adverbs'] for stat in self.stats) / n,
        }


class TreeStats:
    """
    Determine tree-based statistics, such as tree depths, production counts,
    etc.
    """

    def __init__(self, corpus):
        """
        We'll use the Stanford Parser to do the heavy lifting here.
        """
        def n_productions(parse_tree, production):
            """
            Returns the number of productions of type `production` in
            parse_tree.
            """
            productions = list(parse_tree.subtrees(
                filter=lambda t: t.label() == production))
            return len(productions)

        jar = '/usr/local/Cellar/stanford-parser/'
        '3.6.0/libexec/stanford-parser.jar'
        model = '/usr/local/Cellar/stanford-parser/'
        '3.6.0/libexec/stanford-parser-3.6.0-models.jar'
        self.corpus = [corpus] if isinstance(corpus[0], tuple) else corpus
        self.parser = StanfordParser(path_to_jar=jar, path_to_models_jar=model)
        self.stats = []

        parsed_sents = self.parser.tagged_parse_sents(self.corpus)
        self.trees = [t for tree in parsed_sents for t in tree]

        for tree in self.trees:
            self.stats.append({
                'depth': tree.height(),
                'noun_phrases': n_productions(tree, 'NP'),
                'prepositional_phrases': n_productions(tree, 'PP'),
                'sbars': n_productions(tree, 'SBAR'),
                'nonterminals': len(tree.productions()),
            })

    def get_stats(self):
        """
        Combines all the statistics together
        """
        n = len(self.stats)
        max_tree_depth = max(stat['depth'] for stat in self.stats)
        avg_tree_depth = sum(stat['depth'] for stat in self.stats) / n
        avg_noun_phrases = sum(stat['noun_phrases'] for stat in self.stats) / n
        avg_prep_phrases = sum(stat['prepositional_phrases']
                               for stat in self.stats) / n
        avg_sbars = sum(stat['sbars'] for stat in self.stats) / n
        avg_nonterminals = sum(stat['nonterminals'] for stat in self.stats) / n

        return {
            'max_tree_depth': max_tree_depth,
            'avg_tree_depth': avg_tree_depth,
            'avg_noun_phrases': avg_noun_phrases,
            'avg_prepositional_phrases': avg_prep_phrases,
            'avg_sbars': avg_sbars,
            'avg_nonterminals': avg_nonterminals,
        }


def ptr(text_stats, tag_stats, tree_stats):
    """
    From the textual, tag-based, and tree-based statistics, create a
    parse tree readability measurement.
    """
    stats = [{pair for d in L for pair in d.items()}
             for L in zip(text_stats, tag_stats, tree_stats)]

    text_complexity = [15 +
                       10 * (stats['polysyllable_words'] / stats['n_words']) -
                       15 * (stats['n_long'] / stats['n_words'])
                       for stats in all_stats]
    tag_complexity = [stats['n_POSs'] / (stats['n_words'] -
                                         stats['n_repeated_adverbs'] -
                                         stats['n_repeated_possessives'])
                      for stats in all_stats]
    tree_complexity = [1.7 * (stats['prepositional_phrases'] +
                              stats['noun_phrases']) / stats['depth'] +
                       0.7 * stats['depth']
                       for stats in all_stats]
    ptr_per_sent = [0.4 * text + tag + 0.6 * tree
                    for text, tag, tree in
                    zip(text_complexity, tag_complexity, tree_complexity)]

    return sum(ptr_per_sent) / len(ptr_per_sent)
