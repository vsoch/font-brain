#!/usr/bin/python

import os
import re
import pickle
import pandas
import requests
import json
from nlp import do_count
from textblob import Word
from glob import glob

# Github access
token="88e8f958ddaa70b7a9ff05e491efabdf2d2f69b7"

# Ignore urllib3 warnings
import warnings
warnings.filterwarnings('ignore')

# Read in the repos list
repos = pandas.read_csv("data/repos.txt",sep="\t").url.tolist()

# Read in spm functions, fsl functions
spm = pandas.read_csv("spm_commands.txt",sep="\t",header=None)[0].tolist()
fsl = json.loads(open("fsl.json","rb").read())

# Parse fsl json to get commands
commands = []
for domain in fsl[0]["children"]:
    for method in domain["children"]:
        if "children" in domain.keys():
            for child in domain["children"]:
                commands = commands + child["commands"]
        if "commands" in domain.keys():
            commands = commands + domain["commands"]

# Combine with spm, get unique
commands = pandas.DataFrame(commands + spm,columns=[0])[0].unique().tolist()    

# We will append results to this data frame, each script in a repo is a document
gcounts = pandas.DataFrame(columns=commands)
problems = []

for repo in repos:
    print "NEW REPO %s" %repo
    ghrepo = repo.split("/")[-1]
    ghuser = repo.split("/")[-2]
    originalurl = "https://api.github.com/repos/%s/%s/contents?access_token=%s" %(ghuser,ghrepo,token)
    # First recursively get all file urls
    queue = [originalurl]
    download_urls = []
    sniff = requests.get(originalurl).json()
    if isinstance(sniff,list):
        while queue:
            url = queue.pop()
            contents = requests.get(url).json()
            if isinstance(contents,list):    
                for content in contents:
                    if content["download_url"] != None:
                        download_urls.append("%s?access_token=%s" %(content["download_url"],token))
                    else:
                        queue.append("%s&access_token=%s" %(content["url"],token))
        # Now parse for features
        for url in download_urls:
            text = requests.get(url)
            try:
                gcounts.loc[url] = do_count(commands,text)["count"].tolist()
            except:
                print "Cannot parse %s" %url
        # Save intermediate
        gcounts.to_pickle("commandCountsGithub.pkl")
    else:
        print "Problem with %s" %(originalurl)
        problems.append(originalurl)

# Find the repos that have tags
gsub = gcounts[gcounts.sum(axis==1) != 0]

# Remove empty tags
definedvars = gsub.columns[gsub.sum(axis=0)!=0]
gsub = gsub[definedvars]
gsub.to_pickle("commandCountsGithubNonZero.pkl")

# Also save version collapsing across repos
reponames = [x.split("master")[0] for x in gsub.index]
reponames = [x.split("MAGeTbrain")[0] for x in reponames]
reponames = [x.split("BIC-MNI")[0] for x in reponames]
holdernames = gsub.index.tolist()
gsub.index = range(0,len(holdernames))
df = pandas.DataFrame(columns=gsub.columns)
for name in numpy.unique(reponames).tolist():
    print "Adding repo %s" %name
    idx = [x for x in range(0,len(reponames)) if reponames[x] == name]
    subset = gsub.loc[idx]
    df.loc[name,subset.sum().index] = subset.sum().values 

# Export all data for application
alldata = gsub.copy()
alldata.index = [x.replace("https://raw.githubusercontent.com","http://www.github.com") for x in holdernames]
alldata.index = [x.replace("?access_token=%s" %token,"") for x in alldata.index]

# Export to pickle
alldata.to_pickle("commandsGithub210.pkl")

df.index = numpy.unique(reponames).tolist()
df.index =[x.replace("https://raw.githubusercontent.com","") for x in df.index]
df = df[df.index.isin("/")==False]

# Remove "noisy terms"
noise = ["find","flush","get","move","parent","root","set","view","make","editor","paint","add","branch","char",
"children","convert","copy","nifti","time","type","path","toolbox","export","save","display","length","check","size",
"struct","end","first","dtype","fname","src","plot","cluster","cat","disp"]

df = df.loc[df.index,df.columns.isin(noise)==False]

# Remove functions only called once
df = df.loc[df.index,df.sum()!=1]
df = df[df.sum(axis=1)!=0]
df.to_csv("commandGithubFiltered.tsv",sep="\t")

