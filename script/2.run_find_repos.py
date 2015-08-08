from glob import glob

# Run iterations of "find repos" to parse text for github repo links!

topfolder = "/scratch/PI/russpold/data/PUBMED"
pmcfolder = "%s/articles" %(topfolder)
outfolder = "%s/repos" %(topfolder)
subfolders = [ os.path.basename(x) for x in glob("%s/*" %pmcfolder)]
json_path = "/home/vsochat/SCRIPT/python/font-brain/script/fsl.json"

for s in range(5000,len(subfolders)):
    subfolder = subfolders[s]
    jobfile = open(".jobs/%s.job" %subfolder,'w')
    jobfile.writelines("#!/bin/bash\n")
    jobfile.writelines("#SBATCH --job-name=%s_count.job\n" %(subfolder))
    jobfile.writelines("#SBATCH --output=.out/%s_count.out\n" %(subfolder))
    jobfile.writelines("#SBATCH --error=.out/%s_count.err\n" %(subfolder)) 
    jobfile.writelines("#SBATCH --time=2-00:00\n") 
    jobfile.writelines("#SBATCH --mem=12000\n")   
    jobfile.writelines("python /home/vsochat/SCRIPT/python/font-brain/script/2.find_repos.py %s %s %s %s\n" %(pmcfolder,subfolder,outfolder,json_path))  
    jobfile.close()
    os.system('sbatch -p russpold .jobs/%s.job' %subfolder)
