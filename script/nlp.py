#!/usr/bin/env python

from textblob import TextBlob, Word
from nltk.stem.porter import *
from nltk.stem import *
import numpy
import pandas
import re

__author__ = ["Vanessa Sochat (vsochat@stanford.edu)"]
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2015/07/25 $"
__license__ = "Python"

def find_urls(text):
    pattern=r'(http|ftp|https):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?'
    return re.findall(pattern,text)

def do_stem(words):
    stemmer = PorterStemmer()
    if isinstance(words,str):
        words = [words]
    stems = []
    for word in words:
        stems.append(stemmer.stem(word))
    return numpy.unique([s.lower() for s in stems]).tolist()


def get_total_words(text):

    totalwords = 0

    # Dictionary
    if isinstance(text,dict):
        for label,sentences in text.iteritems():
            if isinstance(sentences,str):
                sentences = [sentences]
            for sentence in sentences:
                blob =  TextBlob(sentence)
                words = do_stem(blob.words)
                totalwords += len(words)
        return totalwords    

    # String or list
    elif isinstance(text,str):
        text = [text]
    for sentence in text:
        blob =  TextBlob(sentence)
        words = do_stem(blob.words)
        totalwords += len(words)
    return totalwords


def get_term_counts(terms,text):
    if isinstance(text,dict):
        return get_term_counts_dict(terms,text)
    elif isinstance(text,str):
        text = [text]
        return get_term_counts_list(terms,text)

def get_term_counts_list(terms,text):
    # Convert words into stems
    stems = do_stem(terms)

    counts = do_count(stems,text)
    return counts        
    

def do_count(terms,text):
    # data frame hold counts
    counts = pandas.DataFrame(0,columns=["count"],index=terms)

    for sentence in text:
        blob =  TextBlob(sentence)
        words = do_stem(blob.words)
        words = [w for w in words if w in terms]
        counts.loc[words] = counts.loc[words] + 1
    return counts


def get_term_counts_dict(terms,text):
    # Convert words into stems
    stems = do_stem(terms)

    # data frame hold counts
    counts = pandas.DataFrame(0,columns=["count"],index=stems)

    for label,sentences in text.iteritems():
        if isinstance(sentences,str):
            sentences = [sentences]
        for sentence in sentences:
            blob =  TextBlob(sentence)
            words = do_stem(blob.words)
            words = [w for w in words if w in stems]
            counts.loc[words] = counts.loc[words] + 1
    return counts        

