from pubmed import get_xml_tree
from nlp import get_term_counts, do_stem, find_urls
from glob import glob
import pandas
import json
import pickle
import sys
import os

# Here is the path to the folder with xml files
topfolder = sys.argv[1]
subfolder = sys.argv[2]
outfolder = sys.argv[3]
json_path = sys.argv[4]

folder = "%s/%s" %(topfolder,subfolder)

# Get compressed files in folder.
zips = glob("%s/*.tar.gz" %folder)

# Read in fsl commands
with open(json_path) as data_file:    
    myjson = json.load(data_file)

data = myjson
commands = []
for method in data[0]["children"]:
    if "commands" in method.keys():
        commands = commands + [c for c in method["commands"]] 
    if "children" in method.keys():
        for child in method["children"]:
            if "commands" in child.keys():
                commands = commands + [c for c in child["commands"]]
# checked that they are unique

urls = dict()
for z in zips:
    zname = "%s/%s" %(subfolder,os.path.basename(z))
    text = get_xml_tree(z)
    # First url is always xml schema
    urls[zname] = (find_urls(text)[1:])

# Save to output file
pickle.dump(urls,open("%s/%s_urls.pkl" %(outfolder,subfolder)),"wb")
