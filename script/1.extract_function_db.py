#!/usr/bin/python

import os
import re
import pickle
import urllib2
from glob import glob

interfaces = ["fsl"]
commandsall = dict()
cmd = re.compile("_cmd")


for interface in interfaces:
    module_folder = "/Users/vsochat/Documents/Code/nipype/nipype/interfaces/%s" %(interface)
    module_scripts = glob("%s/*.py" %module_folder)
    commands = []

    for script in module_scripts:
        basepath = os.path.basename(script)
        if basepath != "__init__.py":
            lines = open(script,"rb").readlines()
            commands_single = []
            for line in lines:
                if cmd.search(line):
                    commands_single.append(line.replace(" ","").replace('_cmd=',''))
            commands = commands + [c.replace("\n","").replace('"',"").replace("'",'') for c in commands_single]

    commandsall[interface] = commands

pickle.dump(commandsall,open("/Users/vsochat/Documents/Code/font-brain/scripts/fsl_commands.pkl","wb"))
