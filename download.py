#!/usr/bin/env python

from ProjectApi3 import ProjectApi
from AssayApi import AssayApi
from swagger3 import ApiClient
from FileApi3 import FileApi
#from ProteinApi import ProteinApi
#from PeptideApi import PeptideApi
import sys
import os
import wget
from elementtree import ElementTree as ET
import subprocess
import smtplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#VARIABLE SCRIPT PARAMETERS: BATCH SIZE, THREAD TO RUN IN MQ, ORGANISM AND MODIFICATION DICTIONARY
batch = 10
threadnum = "8"
orgdict = {
        "Saccharomyces cerevisiae (Baker's yeast)": ["home/DATA2/trips/scamp/proteomes/s_cereviseae_proteo$
        "Homo sapiens (Human)": ["home/DATA2/trips/scamp/proteomes/homo_sapiens_proteome.fa", "human"],
        "Mus musculus (Mouse)": ["home/DATA2/trips/scamp/proteomes/mus_musculus_proteome.fa", "mouse"],
        "Rattus norvegicus (Rat)": ["home/DATA2/trips/scamp/proteomes/rattus_norvegicus_proteome.fa", "rat$
        "Escherichia coli": ["home/DATA2/trips/scamp/proteomes/escherichia_coli_proteome.fa", "ecoli"],
        "Drosophila melanogaster (Fruit fly)": ["home/DATA2/trips/scamp/proteomes/drosophila_melanogaster_$
        "Caenorhabditis elegans": ["home/DATA2/trips/scamp/proteomes/c_elegans_proteome.fa", "celegans"],
        "Danio rerio (Zebrafish)(Brachydanio rerio)": ["home/DATA2/trips/scamp/proteomes/danio_rerio_prote$
        "Schizosaccaromyces pombe": ["home/DATA2/trips/scamp/proteomes/schizo_pombe_proteome.fa", "schizo"$
        }
moddict = {
        "phosphorylated residue": "Phospho (STY)",
        "N6-succinyl-L-Lysine": "Succi(K)",
        "deamidated residue": "Deamidation(NQ)"
        }
trickymods = ["acetylated residue", "monohydroxylated residue", "iodoacetamide derivatized residue"]

#EMAIL FUNCTION
def email(x, y):
        fromaddr = "ribopipe@gmail.com"
        toaddr = "judge.ciara@gmail.com"
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = "Scamp Pipeline Batch "+sys.argv[1]+"_"+str(x)
        body = y
        msg.attach(MIMEText(body, 'html'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(fromaddr, "Ribosome")
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
        print("email sent")

def finalemail():
        fromaddr = "ribopipe@gmail.com"
        toaddr = "judge.ciara@gmail.com"
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = "Scamp Pipeline Project "+sys.argv[1]
        body = "This project has been successfully processed."
        msg.attach(MIMEText(body, 'html'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(fromaddr, "Ribosome")
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
        print("Job done")


#PRIDE API USED TO GATHER PROJECT SPECIES, PTMS, FILE NAMES ETC
clientBase = ApiClient("", "http://www.ebi.ac.uk/pride/ws/archive")
projectClient = ProjectApi(clientBase)
project = projectClient.getProjectSummary(sys.argv[1])

#FIND PROJECT SPECIES, REQUIRED FOR XML FILE GENERATION AND PASSED TO MAXQUANT_TO_SQLITE2 SCRIPT
species = str(project["species"][0])
#if len(project["species"]) > 1:
#       print "There is more than one organism in this study"
#       sys.exit()
if not species in orgdict:
        print("The organism in this study is not in our proteome dictionary")
        sys.exit()
fastapath = orgdict[species][0]


#PRINT PROJECT BASICS TO TERMINAL
print(project["title"])
print(project["projectDescription"])

#MODIFICATION PROCESSING, REQUIRED FOR XML FILE GENERATION
mods = list(map(str, project["ptmNames"]))
if mods[0] == "No PTMs are included in the dataset":
        mods = []
for x in trickymods:
        if x in mods:
                mods.remove(x)
for x in mods:
        if not x in moddict:
                mods.remove(x)
                print("One of the modifications fetched from PRIDE is not in the modification dictionary a$
print(mods)


#GENERATING FILE LIST AND DICTIONARY
filedict = {}
fileClient = FileApi(clientBase)
fileList = fileClient.getFilesByProjectAccession(sys.argv[1])
print(fileList)
for file in fileList.list:
  fname =  file.fileName.replace("#","")
  print(file.fileType)
  print(file.downloadLink)
  ext = (fname.split(".")[-1]).lower()
  if ext == "raw":
    filedict[fname] = file.downloadLink.replace("#","%23")


filelist = list(filedict.keys())

if len(filelist) == 0:
        print("This project does not have any raw files, would you like to execute the manual download fun$
        response = input()
        if response == "y":
                if not os.path.isdir(sys.argv[1]+"_manualdwnld"):
                        os.makedirs(sys.argv[1]+"_manualdwnld")
                print("INSTRUCTIONS: Please manually download the files from PRIDE into the "+sys.argv[1]+$
                print("When the download is complete, enter y to continue")
                manualready = input()
                if manualready == "y":

                        manualdr = sys.argv[1]+"_manualdwnld/"
                        rawnum = 0
                        rawpaths = []
                        filelist = []
                        for file in os.listdir(manualdr):
                                if file.endswith(".raw"):
                                        rawnum += 1
                                        rawpaths.append(manualdr+"/"+file)
                                        filelist.append(file)

                        batch_no = 0
                        for i in range(0,len(rawpaths),batch):
                                print("Creating folder for batch "+str(batch_no))
                                if not os.path.isdir("{}_{}".format(sys.argv[1],batch_no)):
                                        os.makedirs("{}_{}".format(sys.argv[1],batch_no))
                                        batchdirect = "{}_{}".format(sys.argv[1],batch_no)
                                        for x in range(i, i+batch):
                                                if x > (len(rawpaths)-1):
                                                        break
                                                subprocess.call("mv "+rawpaths[x]+" "+batchdirect, shell=T$

                                        batch_no += 1

        else:
                sys.exit()


#PIPELINE ACTION IN BATCH SYSTEM
batch_no = 0
print(len(filelist))
total_files = 0

for i in range(0,len(filelist),batch):
        print("batch "+str(batch_no))
        print("Checking for completion")
        sqlitetest = []
        for x in range(i,i+batch):
                if x > (len(filelist)-1):
                        break
                filename = filelist[x]
                sqlitecheck = filename.replace(".raw", ".sqlite").replace(".RAW",".sqlite")
                if os.path.isfile("./"+sys.argv[1]+"_sqlites/"+sqlitecheck):
                        total_files += 1
                        print("success", "./"+sys.argv[1]+"_sqlites/"+sqlitecheck)
                        print("total files "+str(total_files))
                else:
                        print("./"+sys.argv[1]+"_sqlites/"+sqlitecheck+" does not exist!")
                # If the file does not exist append no, otherwise append yes to sqlitetest
                if not os.path.isfile("./"+sys.argv[1]+"_sqlites/"+sqlitecheck):
                        sqlitetest.append("no")
                else:
                        sqlitetest.append("yes")
        print(sqlitetest)
        # if no not in sqlite test, increase batch by 1 and continue
        if not "no" in sqlitetest:
                batch_no += 1
                #print ("no not in sqlitetest, coninuing",sqlitetest)
                #sys.exit()
                continue
        #MAKE DIRECTORY FOR THE BATCH CONSISTING OF THE PROJECT ACCESSION AND BATCH NUMBER
        if not os.path.isdir("{}_{}".format(sys.argv[1],batch_no)):
                os.makedirs("{}_{}".format(sys.argv[1],batch_no))
        pathlist = []


        #FETCH RAW FILES PROVIDED NEITHER THEY NOR THE COMBINED FOLDER ALREADY EXIST    
        for x in range(i,i+batch):
                if x > (len(filelist)-1):
                        break
                jnames = []
                filename = filelist[x]
                jname = filename.split(".")
                jnames.append(jname[0])
                if os.path.isfile("./"+sys.argv[1]+"_sqlites/"+jname[0]+".sqlite"):
                        continue
                if not os.path.isfile("./"+sys.argv[1]+"_"+str(batch_no)+"/"+filename):
                        if not os.path.isdir("./"+sys.argv[1]+"_"+str(batch_no)+"/combined/txt"):
                                if not os.path.isfile("./"+sys.argv[1]+"_sqlites/"+jname[0]+".sqlite"):
                                        print(filedict[filename])
                                        print("downloading", filename, "to", "/home/DATA2/trips/scamp/"+st$
                                        wget.download(filedict[filename], "/home/DATA2/trips/scamp/"+str(s$
                pathlist.append("/home/DATA2/trips/scamp/"+str(sys.argv[1])+"_"+str(batch_no)+"/"+filename)
        #print(pathlist)
        print(jnames)
        #email(batch_no, "files downloaded successfully")

	
	#XML FILE TEMPLATE MODIFICATION
	tree = ET.parse('/home/DATA2/trips/scamp/mqpar.xml')
	root = tree.getroot()
	filepaths = root.find("./filePaths")
	fastafile = root.find("./fastaFiles/FastaFileInfo")
	experiments = root.find("./experiments")
	refchan = root.find("./referenceChannel")
	fractions = root.find("./fractions")
	ptms = root.find("./ptms")
	paramgroup = root.find("./paramGroupIndices")	
	variablemods = root.find("./parameterGroups/parameterGroup/variableModifications")
	
	if not os.path.isfile("./"+sys.argv[1]+"_"+str(batch_no)+"/mqpar_"+str(batch_no)+".xml"):	
		for x in pathlist:
			string = ET.Element("string")
			string.text = x
			filepaths.append(string)
		for x in range(i, i+batch):
			short = ET.Element("short")
			short.text = "32767"
			fractions.append(short)

			if len(mods) > 0:
				boolean = ET.Element("boolean")
				boolean.text = "true"
				ptms.append(boolean)
			else:
				boolean = ET.Element("boolean")
				boolean.text = "false"
				ptms.append(boolean)

			inti = ET.Element("int")
			inti.text = "0"
			paramgroup.append(inti)
		
			string = ET.Element("string")
			experiments.append(string)
			refchan.append(string)
	
		nt = ET.Element("numThreads")
		nt.text = threadnum
		root.append(nt)

		if len(mods) > 0:
			for mod in mods:
				string = ET.Element("string")
				string.text = moddict[mod]
				variablemods.append(string)		
			
		ff = ET.Element("fastaFilePath")
		ff.text = fastapath
		fastafile.append(ff)
		tree.write("./"+sys.argv[1]+"_"+str(batch_no)+"/mqpar_"+str(batch_no)+".xml")
	

	#PASS TO MAXQUANT AND ERROR EMAIL
	if not os.path.isdir("./"+sys.argv[1]+"_"+str(batch_no)+"/combined"):
		#email(batch_no, "files passed to maxquant")
		subprocess.call("mono /home/DATA2/trips/scamp/MaxQuant/bin/MaxQuantCmd.exe "+sys.argv[1]+"_"+str(batch_no)+"/mqpar_"+str(batch_no)+".xml", shell=True)
		

	else:
		if not os.path.isdir("./"+sys.argv[1]+"_"+str(batch_no)+"/combined/txt"):
			subprocess.call("rm -r /home/DATA2/trips/scamp/"+str(sys.argv[1])+"_"+str(batch_no)+"/combined", shell="True")
			#email(batch_no, "files passed to maxquant")
			subprocess.call("mono /home/DATA2/trips/scamp/MaxQuant/bin/MaxQuantCmd.exe "+sys.argv[1]+"_"+str(batch_no)+"/mqpar_"+str(batch_no)+".xml", shell=True)

	if not os.path.isdir("./"+sys.argv[1]+"_"+str(batch_no)+"/combined/txt"):
		#email(batch_no, "maxquant unsuccessful")
		batch_no += 1
		continue
	else:
		pass
		#email(batch_no, "maxquant successful")

	#CHECK IF THERE IS AN SQLITE FILE FOR EVERY FILE IN THE BATCH, IF NOT RUNS MAXQUANT_TO_SQLITE SCRIPT. IF SOME BUT NOT ALL FILES HAVE SQLITE FILE, DELETES EVERY SQLITE FILE BEFORE RUNNING SCRIPT TO 		AVOID ADDING TO ALREADY PRESENT FILES
	sqlitetest = []
	sqliteyes = []
	for x in jnames:
		if not os.path.isfile("./"+sys.argv[1]+"_sqlites/"+x+".sqlite"):
			sqlitetest.append("no")
		else:
			sqlitetest.append("yes")
			sqliteyes.append(x)

	if "no" in sqlitetest:
		for x in sqliteyes:
			subprocess.call("rm /home/DATA2/trips/scamp/"+str(sys.argv[1])+"_"+str(batch_no)+"/"+x+".sqlite", shell="True")
		
		subprocess.call("python /home/DATA/raw_files/maxquant_to_sqlite2.py ./"+sys.argv[1]+"_"+str(batch_no)+" "+orgdict[species][1]+" "+sys.argv[1], shell=True)

	#REMOVES RAW FILES IF BOTH RAW AND SQLITE ARE PRESENT
	for x in filelist:
		basename = x.replace(".raw", "")
		if os.path.isfile("./"+sys.argv[1]+"_sqlites/"+basename+".sqlite") and os.path.isfile("./"+sys.argv[1]+"_"+str(batch_no)+"/"+x):
				subprocess.call("rm /home/DATA2/trips/scamp/"+str(sys.argv[1])+"_"+str(batch_no)+"/"+x, shell="True")

	#REMOVES FILE SPECIFIC DIRECTORIES CREATED BY MAXQUANT TO SAVE STORAGE
	for x in jnames:
		if os.path.isdir("./"+sys.argv[1]+"_"+str(batch_no)+"/"+x):
			subprocess.call("rm -r /home/DATA2/trips/scamp/"+str(sys.argv[1])+"_"+str(batch_no)+"/"+x, shell="True")			

	#EMAIL NOTIFICATION OF SUCCESSFUL RUN
	sqlitetest = []
	for x in jnames:
		if not os.path.isfile("./"+sys.argv[1]+"_sqlites/"+x+".sqlite"):
			sqlitetest.append("no")
		else:
			sqlitetest.append("yes")

	print sqlitetest
	if not "no" in sqlitetest:
		#email(batch_no, "sqlite file creation successful")		
		pass

	#ESTABLISHES NEW BATCH NUMBER, LOOP BEGINS AGAIN	
	batch_no += 1


#WHEN PROJECT IS FINISHED APPEND ACCESSION TO FILE
finishedlist = open("finishedprojects.txt", "a+")
finishedlist.write(sys.argv[1] + '\n')
finishedlist.close()

#EMAIL NOTIFICATION OF PROJECT COMPLETION
finalemail()






