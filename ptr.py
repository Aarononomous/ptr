from math import sqrt
import nltk
from nltk import Tree
import textacy
import pyphen  # hyphenation library
import spacy

# Set up globals
pyphen.language_fallback('en_US')
dic = pyphen.Pyphen(lang='en_US')

en_nlp = spacy.load('en')

# Textual metrics


def depunctuate(tagged_sentence):
    """
    From a tagged sentence (as a list), returns a sentence without punctuation
    """
    punct_tags = set(['(', ')', ',', '--', '.', ':'])
    return [(word, tag) for word, tag in tagged_sentence
            if tag not in punct_tags]


def n_words(tagged_sentence):
    """
    From a tagged sentence (as a list), returns the number of words in it,
    sans punctuation.
    """
    return len(depunctuate(tagged_sentence))


def word_lengths(tagged_sentence):
    """
    From a tagged sentence (as a list), returns a list of non-punctation
    word lengths
    """
    return [len(word) for word, pair in depunctuate(tagged_sentence)]


def avg_word_length(tagged_sentence):
    """The average word length of the sentence"""
    l = word_lengths(tagged_sentence)
    return sum(l) / len(l)


def syllables(tagged_sentence):
    """
    From a tagged sentence (as a list), returns a list of non-punctation
    syllables per word.
    """
    return [len(dic.positions(word)) + 1
            for word, pair in depunctuate(tagged_sentence)]


def n_monosyllable_words(tagged_sentence):
    """
    Returns the number of one syllable words in the (word, tag)-list sentence
    """
    return len([sylls for sylls in syllables(tagged_sentence) if sylls == 1])


def n_polysyllable_words(tagged_sentence):
    """
    Returns the number of 3+ syllable words in the (word, tag)-list sentence
    """
    return len([sylls for sylls in syllables(tagged_sentence) if sylls >= 3])

# Standard Readability Metrics


def SMOG(text):
    """
    Computes the SMOG score of a piece of text, in this case, a list of tagged sentences.
    There must be at least 30 sentences in the text or an Error will be thrown.

    McLaughlin, G. Harry (May 1969). "SMOG Grading — a New Readability Formula" (PDF).
    Journal of Reading. 12 (8): 639–646.
    """
    if len(text) < 30:
        raise ValueError('There must be at least 30 sentences in the input for an accurate \
        readability score.')

    n_polysyllables = sum(n_polysyllable_words(sentence) for sentence in text)
    n_sentences = len(text)
    grade = 1.0430 * sqrt(n_polysyllables * (30 / n_sentences)) + 3.1291
    return grade


def flesch_kincaid_grade_level(text):
    """
    Computes the Flesch-Kincaid grade level of a piece of text, in this case,
    a list of tagged sentences.

    Kincaid JP, Fishburne RP Jr, Rogers RL, Chissom BS (February 1975).
    "Derivation of new readability formulas (Automated Readability Index,
    Fog Count and Flesch Reading Ease Formula) for Navy enlisted personnel".
    Research Branch Report 8-75, Millington, TN: Naval Technical Training,
    U. S. Naval Air Station, Memphis, TN.
    """
    total_sentences = len(text)
    total_words = sum(n_words(sentence) for sentence in text)
    total_syllables = sum(sum(syllables(sentence)) for sentence in text)
    grade = 0.39 * (total_words / total_sentences) + 11.8 * \
        (total_syllables/total_words) - 15.59
    return grade

#  Tag-based Metrics


def n_POSs(tagged_sentence):
    """Returns the number of unique POS's in the tagged sentence"""
    return len(set(pos for word, pos in tagged_sentence))


def n_repeated_possessives(tagged_sentence):
    """
    The number of 2+ repeated possessives, e.g.:
    "John's mother's neighbor's uncle's dog's Instagram account" -> 5
    "John's dog's Instagram account" -> 2
    "John's Instagram account" -> 0  # because it's not repeated
    """
    return 0  # TODO


def n_repeated_adverbs(tagged_sentence):
    """
    The number of 2+ repeated adverbs (RB, RBR, and RBS/RBT) e.g.:
    "harder better faster stronger" -> 4  # as adverbs, not adjectives!
    "most happily" -> 2
    "likely ready" -> 0  # because "ready" is an adjective
    """
    return 0  # TODO

# Tree-based Metrics


def get_trees(sentence):
    """
    Returns all possible parse trees from a sentence.
    The sentence is POS-tagged, and this returns a list of nltk.Trees
    """
    pass  # TODO


def tree_depth(tree):
    """Returns the tree depth of an individual parse tree. O(n)"""
    return tree.height()


def max_tree_depth(trees):
    """Returns the max tree depth over a collection of parse trees"""
    return max((tree_depth(tree) for tree in trees))


def avg_tree_depth(trees):
    """Returns the average tree depth over a collection of parse trees"""
    return sum((tree_depth(tree) for tree in trees)) / len(trees)
