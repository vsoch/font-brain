#!/usr/bin/env python

import tarfile
import urllib
import numpy as np
import string
import urllib2
import json
from Bio import Entrez
import nltk
from nltk import word_tokenize
import re
import sys
import os.path
import pandas as pd
import os

__author__ = ["Vanessa Sochat (vsochat@stanford.edu)"]
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2011/09/09 $"
__license__ = "Python"

# Pubmed
class Pubmed:

    """Init Pubmed Object"""
    def __init__(self,email):
        self.email = email
        self._get_pmc_lookup()

    def _get_pmc_lookup(self):
        print "Downloading latest version of pubmed central ftp lookup..."
        self.ftp = pd.read_csv("ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/file_list.txt",skiprows=1,sep="\t",header=None)
        self.ftp.columns = ["URL","JOURNAL","PMCID","PMID"]

    def get_pubmed_central_ids(self):
        return list(self.ftp["PMCID"])

    """Download full text of articles with pubmed ids pmids to folder"""
    def download_pubmed(self,pmids,download_folder):
        subset = pd.DataFrame(columns=self.ftp.columns)
        for p in pmids:
            row = self.ftp.loc[self.ftp.index[self.ftp.PMCID == p]]
            subset = subset.append(row)
        # Now for each, assemble the URL
        for row in subset.iterrows():
            url = "ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/%s" % (row[1]["URL"])
            download_place = "%s/" %(download_folder)
            basename = os.path.basename(row[1]["URL"])
            if not os.path.isfile("%s/%s" %(download_folder,basename)):
                print "Downloading %s" % (url)       
                os.system("wget \"%s\" -P %s" % (url,download_place))


    """check if file downloaded"""
    def check_download(self,pmid,download_folder):
        article = self.ftp.loc[self.ftp.index[self.ftp.PMCID == pmid]]
        article = os.path.basename(article["URL"].tolist()[0])
        article = "%s/%s" %(download_folder,article)
        return os.path.exists(article)

    """Read and return single article (or search term) pubmed"""
    def get_single_article(self,id1):
        Entrez.email = self.email
        handle = Entrez.esearch(db='pubmed',term=id1,retmax=1)
        record = Entrez.read(handle)

        # If we have a match
        if "IdList" in record:
            if record["Count"] != "0":
             # Get the id and fetch the paper!
             print "Retrieving paper " + str(id1) + "..."
             handle = Entrez.efetch(db='pubmed', id=record["IdList"][0],retmode='xml',retmax=1)
             record = Entrez.read(handle)
             record = record[0]
             article = Article(record)
             return article
        else:
            print "No articles found for " + str(id1)

    """Compile search terms into one search, return all"""
    def get_many_articles(self,ids):

        pmids = []
        for id1 in ids:
            Entrez.email = self.email
            handle = Entrez.esearch(db='pubmed',term=id1,retmax=1)
            record = Entrez.read(handle)
            # If we have a match
            if "IdList" in record:
                if record["Count"] != "0":
                    pmids.append(record["IdList"][0])

        if len(pmids) > 0:
            # Retrieve them all!
            print "Retrieving %s papers..." % (len(pmids))
            handle = Entrez.efetch(db='pubmed', id=pmids,retmode='xml')
            records = Entrez.read(handle)
            articles = dict()
            for record in records:
                 articles[str(record["MedlineCitation"]["PMID"])] = Article(record)
            return articles
        else:
            print "No articles found."

    """Search article for a term of interest - no processing of expression. return 1 if found, 0 if not"""
    def search_article(self,article,term):
        text = [article.getAbstract()] + article.getMesh() + article.getKeywords()
        text = text[0].lower()
        expression = re.compile(term)
        # Search abstract for terms, return 1 if found
        found = expression.search(text)
        if found:
            return 1
        else:
            return 0


    """Search article for a term of interest - stem list of words first - return 1 if found, 0 if not"""
    def search_article_list(self,article,term):
        text = [article.getAbstract()] + article.getMesh() + article.getKeywords()
        text = text[0].lower()
        # Perform stemming of disorder terms
        words = []
        porter = nltk.PorterStemmer()
        [[words.append(str(porter.stem(t))) for t in word_tokenize(x.lower())] for x in term]
        # Get rid of general disease terms
        diseaseterms = ["disord","diseas","of","mental","impuls","control","health","specif","person","cognit","type","form","syndrom","spectrum","eat","depend","development","languag","by","endog","abus"]
        words = filter(lambda x: x not in diseaseterms, words)
        if len(words) > 0:
            # Get unique words
            words = list(set(words))
            term = "|".join([x.strip(" ").lower() for x in words])
            expression = re.compile(term)
            # Search abstract for terms, return 1 if found
            found = expression.search(text)
            if found:
                return 1
            else:
                return 0
        else:
            print "Insufficient search term for term " + str(term)
            return 0

    """Return list of articles based on search term"""
    def get_articles(self,searchterm):

        print "Getting pubmed articles for search term " + searchterm

        Entrez.email = self.email
        handle = Entrez.esearch(db='pubmed',term=searchterm,retmax=5000)
        record = Entrez.read(handle)

        # If there are papers
        if "IdList" in record:
            if record["Count"] != "0":
                # Fetch the papers
                ids = record['IdList']
                handle = Entrez.efetch(db='pubmed', id=ids,retmode='xml',retmax=5000)
                return Entrez.read(handle)

        # If there are no papers
        else:
            print "No papers found for searchterm " + searchterm + "!"


# Download pubmed without relying on pubmed object
"""Download full text of articles with pubmed ids pmids to folder"""
def download_pubmed(pmids,download_folder,ftp):
    if isinstance(pmids,str):
        pmids = [pmids]
    subset = pd.DataFrame(columns=ftp.columns)
    for p in pmids:
        row = ftp.loc[ftp.index[ftp.PMCID == p]]
        subset = subset.append(row)
    # Now for each, assemble the URL
    for row in subset.iterrows():
        url = "ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/%s" % (row[1]["URL"])
        download_place = "%s/" %(download_folder)
        basename = os.path.basename(row[1]["URL"])
        if not os.path.isfile("%s/%s" %(download_folder,basename)):
            print "Downloading %s" % (url)       
            os.system("wget \"%s\" -P %s" % (url,download_place))



# ARTICLE ------------------------------------------------------------------------------
"""An articles object holds a pubmed article"""
class Article:

    def __init__(self,record):
        self._parseRecord(record)

    def _parseRecord(self,record):
        if "MedlineCitation" in record:
            self.authors = record["MedlineCitation"]["Article"]["AuthorList"]
        if "MeshHeadingList" in record:
            self.mesh = record["MedlineCitation"]["MeshHeadingList"]
        else:
            self.mesh = []
        self.keywords = record["MedlineCitation"]["KeywordList"]
        self.medline = record["MedlineCitation"]["MedlineJournalInfo"]
        self.journal = record["MedlineCitation"]["Article"]["Journal"]
        self.title = record["MedlineCitation"]["Article"]["ArticleTitle"]
        self.year = record["MedlineCitation"]["Article"]["ArticleTitle"]
        if "Abstract" in record["MedlineCitation"]["Article"]:
            self.abstract = record["MedlineCitation"]["Article"]["Abstract"]
        else:
            self.abstract = ""
        self.ids = record["PubmedData"]["ArticleIdList"]

    """get Abstract text"""
    def getAbstract(self):
        if "AbstractText" in self.abstract:
            return self.abstract["AbstractText"][0]
        else:
            return ""

    """get mesh terms"""
    def getMesh(self):
        return [ str(x["DescriptorName"]).lower() for x in self.mesh]

    """get keywords"""
    def getKeywords(self):
        return self.keywords

# PARSE  ------------------------------------------------------------------------------
# General functions for parsing XML

def get_xml_tree(paper):
    if re.search("[.tar.gz]",paper):
        raw = extract_xml_compressed(paper)
    else:
        raw = read_xml(paper)
    return raw

'''Return text for xml tree element'''
def recursive_text_extract(xmltree):
    text = []
    queue = []
    article_ids = []
    for elem in reversed(list(xmltree)):
        queue.append(elem)

    while (len(queue) > 0):
        current = queue.pop()
        if current.text != None:
            text.append(current.text)
        if "pub-id-type" in current.keys():
            article_ids.append(current.text)
        if len(list(current)) > 0:
            for elem in reversed(list(current)):
                queue.append(elem)

    # The pubmed id is the first, so it will be last in the list
    pmid = article_ids[0]
    return (pmid,text)

'''Read XML from compressed file'''
def extract_xml_compressed(paper):
    tar = tarfile.open(paper, 'r:gz')
    for tar_info in tar:
        if os.path.splitext(tar_info.name)[1] == ".nxml":
            print "Extracting text from %s" %(tar_info.name)
            file_object = tar.extractfile(tar_info)
            return file_object.read().replace('\n', '')

'''Extract text from xml or nxml file directory'''
def read_xml(xml):
    with open (xml, "r") as myfile:
        return myfile.read().replace('\n', '')

'''Cut out article sections we aren't interested in'''
def crop_text(text,remove_before="<abstract>",remove_after="<ref-list>"):
    # Remove everything before abstract
    start = re.compile(remove_before)
    end = re.compile(remove_after)
    start = start.search(text)
    end = end.search(text)
    return text[start.start():end.start()]

def remove_formatting(text):
    to_remove = ["<italic>","<bold>","<p>","<sub>","<table>","<td>","<tr>"]
    for remove in to_remove:
        text = text.replace(remove,"")
        text = text.replace(remove.replace("<","</"),"")
    return text

'''Search text for list of terms, return list of match counts'''
def search_text(text,terms):
    vector = np.zeros(len(terms))
    for t in range(0,len(terms)):
        expression = re.compile("\s%s\s|\s%s\." %(terms[t],terms[t]))
        match = expression.findall(text)
        vector[t] = len(match)
    return vector
