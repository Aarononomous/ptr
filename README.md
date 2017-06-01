# Parse Tree Readability

`ptr.py` is a python program that measures the readability of a text by inspecting its parse tree, that is, how complicated the sentences are regardless of the words (or word lengths) within them.

`Parse Tree Readability.ipynb` is a Jupyter notebook that walks through the `ptr` code. It contains the same functions, etc., presented in a conversational and exploratory way.

There are no other files needed. Libraries such as `nltk` and `spaCy` themselves contain corpora, so we can use those (at least to begin with).

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
>>> for rating, sentence in top_5:
>>>     print(rating, sentence.leaves())
```

## Using `Parse Tree Readability.ipynb`

The Jupyter notebook `Parse Tree Readability.ipynb` is the best introduction to the theory and usage of this library. Open it (on the command line, with `jupyter notebook "Parse Tree Readability.ipynb"`) and begin exploring.

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

## License

Licensed under the MIT License. See [LICENSE](LICENSE).