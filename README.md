# Parse Tree Readability

`ptr.py` is a python program that measures the readability of a text by inspecting its parse tree, that is, how complicated the sentences are regardless of the words (or word lengths) within them.

`Parse Tree Readability.ipynb` is a Jupyter notebook that walks through the `ptr` code. It contains the same functions, etc., presented in a conversational and exploratory way.

There are no other files needed. Libraries such as `nltk` and `spaCy` themselves contain corpora, so we can use those (at least to begin with).

## Overview

[ TODO: overview ]

### Example: Finding the reading level of a text file within the console

```python
>>> import ptr
>>> file = open('moby-dick.txt')
>>> text = file.read()
>>> file.close()
>>> readability = ptr.readability(text)
16.74
>>>
```

### Example: Finding the 5 most ambiguous sentences in a tagged corpus

```python
>>> import ptr
>>> import nltk
>>> wsj_12 = nltk.corpus.treebank.parsed_sents('wsj_0012.mrg')
>>> ambiguities = [ptr.n_parse_trees(sentence) for sentence in wsj_12]
>>> rated_sentences = zip(ambiguities, wsj_12)
>>> top_5 = sorted(rated_sentences)[:5]
>>> print(top_5)  # TODO: there's a better way of outputting this sentence and its rating
```

[ TODO: introduction to the Jupyter notebook ]

## Tutorial

[ TODO: examples of most of the functions, with step-by-step procedures ]

## Installation

Installation is simple. Download (or clone) this repository to your working directory. Then `import ptr` inside _your_ python file.

Installing the required libraries can be done with `pip` or `conda`, your preference, on the command line, ex.:

```bash
$ pip install spacy
```

You may need to download the spaCy english language parser; an error such as `Warning: no model found for 'en'` will alert you of this. This can be done on the command line as well:

```bash
$ python -m spacy download en
```

## TODO

- [ ] Determine which tree metrics $T_1 \dots T_n$ and parse-tree specific metrics $P_1 \dots P_m$ might be useful. A quick literature review suggests that besides tree depth, the number of certain structures, such as noun phrases and subordinate clauses, correlate strongly with readability; I need to dig down into these. I'd also like to examine the ambiguousness of a sentence, i.e., how many parse trees are createable from its POS tags.

- [ ] finish the literature review. There must be something

- [ ] Write algorithms (or filters) to get counts of all the metrics I need.

- [ ] Add to the README; finish up all TODO's in here.

- [ ] From my data and the calculated SMOG readability, find this relationship $f$ where $f(T_1(S), \dots, T_n(S),  P_1(S), \dots, P_m(S)) \approx \mathrm{SMOG}(S)$ for all sentences $S \in$ my corpus. $f$ will be my readability metric. I'm not totally sure how I'll do this---I don't think a linear relationship will be useful.

- [ ] Will I have to write a CKY algorithm myself?

- [ ] figure out how to get the SMOG, etc. reading levels of text. What's the best unit to measure this in? Paragraphs? How about groups of minimum 30 words? It will have to be per-sentence for the grammatical measurements.
    - [ ] need a function to join measurements from individual sentences into the group.
    - [ ] throw an error when the sentence/text is too short

- [ ] what functions do I need?
    - [ ] find all parse trees from a tokenized sentence
    - [ ] number of parse trees
    - [ ] max tree depth
    - [ ] average tree depth
    - [ ] count of noun phrases
    - [ ] count of subordinate phrases. count_of_nonterminals(sentence, parse). This will be over _all_ possible parses? Or just the most likely?
    - [ ] sentence length
    - [ ] anaphora
    - [ ] ???
    
- [ ] compare readability of texts

- [ ] graphing?

- [ ] refactor list comprehensions to generator comprehensions, if possible

## License

Licensed under the MIT License. See [LICENSE](LICENSE).