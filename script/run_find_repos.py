from glob import glob

# Run iterations of "find repos" to parse text for github repo links!

topfolder = "/scratch/PI/russpold/data/PUBMED/articles"
outfolder = "%s/repos" %(topfolder)
subfolders = glob(topfolder)
json_path = "/home/vsochat/SCRIPT/python/font-brain/script/fsl.json"

for subfolder in subfolders:
    jobfile = open(".jobs/%s.job" %subfolder,'w')
    jobfile.writelines("#!/bin/bash\n")
    jobfile.writelines("#SBATCH --job-name=%s_count.job\n" %(subfolder))
    jobfile.writelines("#SBATCH --output=.out/%s_count.out\n" %(subfolder))
    jobfile.writelines("#SBATCH --error=.out/%s_count.err\n" %(subfolder)) 
    jobfile.writelines("#SBATCH --time=2-00:00\n") 
    jobfile.writelines("#SBATCH --mem=12000\n")   
    jobfile.writelines("python /home/vsochat/SCRIPT/python/font-brain/script/find_repos.py %s %s %s\n" %(topfolder,subfolder, outfolder,json_path))  
    jobfile.close()
    os.system('sbatch -p russpold .jobs/%s.job' %subfolder)
