from glob import glob
import pandas
import numpy
import pickle
import re

# Run iterations of "find repos" to parse text for github repo links!

topfolder = "/scratch/PI/russpold/data/PUBMED/repos"
files = glob("%s/*" %topfolder)
#json_path = "/home/vsochat/SCRIPT/python/font-brain/script/fsl.json"

domains = []

# First get unique domains
for f in range(0,len(files)):
    print "%s of %s" %(f,len(files))
    filey = files[f]
    urls = pickle.load(open(filey,"rb"))
    for journal,url in urls.iteritems():
        if len(url) > 0:
            domain = numpy.unique([u[1] for u in url]).tolist()
            domains = numpy.unique(domains + domain).tolist()

pickle.dump(domains,open("/scratch/PI/russpold/data/PUBMED/domains_list.pkl","wb"))
domains.sort()

# Now we want to summarize the counts for each journal
urldf = pandas.DataFrame(0,index=domains,columns=["count"])
for f in range(0,len(files)):
    print "%s of %s" %(f,len(files))
    filey = files[f]
    urls = pickle.load(open(filey,"rb"))
    for journal,url in urls.iteritems():
        if len(url) > 0:
            domain = numpy.unique([u[1] for u in url]).tolist()
            urldf.loc[domain] = urldf.loc[domain] + 1

# Save to pickle
urldf = urldf.sort(columns="count",ascending=False)
urldf.to_pickle("/scratch/PI/russpold/data/PUBMED/repos/repos_url_count_pandas_df.pkl")

# Finally (if they exist) we want to save the papers that have github

expression = re.compile("github")
len([x for x in domains if expression.search(x)])
# 240

journals = []
uurls = []

for f in range(0,len(files)):
    print "%s of %s" %(f,len(files))
    filey = files[f]
    urls = pickle.load(open(filey,"rb"))
    for journal,url in urls.iteritems():
        if len(url) > 0:
            domain = [u[1] for u in url]
            for d in range(0,len(domain)):
                if expression.search(domain[d]):
                    journals.append(journal)
                    fullurl = "%s://%s%s" %(url[d][0],url[d][1],url[d][2])
                    uurls.append(fullurl)

github = pandas.DataFrame()
github["journals"] = journals
github["urls"] = uurls
github.to_pickle("/scratch/PI/russpold/data/PUBMED/repos/repos_github_pandas_df.pkl")
gunique = github["urls"].value_counts()
gunique.to_pickle("/scratch/PI/russpold/data/PUBMED/repos/repos_github_pandas_unques_df.pkl")

# Now try for ALL possible places with code
expression = re.compile("github|bitbucket|mercurial|git|alioth|cloudforge|codeplex|assembla|berlios|beanstalk|gogs|gitlab|gitorious|fedora|gna|gnome|code.google.com|sourceforge|javaforge|launchpad|osdn|ourproject|tigris")

len([x for x in domains if expression.search(x)])
# 1998!

journals = []
uurls = []

for f in range(0,len(files)):
    print "%s of %s" %(f,len(files))
    filey = files[f]
    urls = pickle.load(open(filey,"rb"))
    for journal,url in urls.iteritems():
        if len(url) > 0:
            domain = [u[1] for u in url]
            for d in range(0,len(domain)):
                if expression.search(domain[d]):
                    journals.append(journal)
                    fullurl = "%s://%s%s" %(url[d][0],url[d][1],url[d][2])
                    uurls.append(fullurl)

result = pandas.DataFrame()
result["journals"] = journals
result["urls"] = uurls

# Save format will depend on the size...
result.to_pickle("/scratch/PI/russpold/data/PUBMED/repos/repos_code_pandas_df.pkl")
