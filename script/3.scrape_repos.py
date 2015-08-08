#!/usr/bin/python

import os
import re
import pickle
import pandas
import urllib2
from glob import glob

# Read in the repos list
repos = pandas.read_pickle("/scratch/PI/russpold/data/PUBMED/repos/repos_github_pandas_unques_df.pkl")
