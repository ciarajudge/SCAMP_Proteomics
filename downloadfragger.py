#!/usr/bin/env python

from ProjectApi3 import ProjectApi
from AssayApi import AssayApi
from swagger3 import ApiClient
from FileApi3 import FileApi
import datetime
import sys
import os
import wget
import subprocess
import smtplib
import re
import pandas as pd
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#VARIABLE SCRIPT PARAMETERS: BATCH SIZE, THREAD TO RUN IN MQ, ORGANISM AND MODIFICATION DICTIONARY
batch = 10
orgdict = {
        "Saccharomyces cerevisiae (Baker's yeast)": ["/home/DATA2/trips/scamp/proteomes/s_cereviseae_proteome.fa", "yeast", "placeholder", "s_cereviseae_proteome.fa"],
        "Homo sapiens (Human)": ["/home/DATA2/trips/scamp/proteomes/homo_sapiens_proteome.fa", "human", "UP000005640", "homo_sapiens_proteome.fa"],
        "Mus musculus (Mouse)": ["/home/DATA2/trips/scamp/proteomes/mus_musculus_proteome.fa", "mouse", "UP000000589", "mus_musculus_proteome.fa"],
        "Mus musculus": ["/home/DATA2/trips/scamp/proteomes/mus_musculus_proteome.fa", "mouse", "UP000000589", "mus_musculus_proteome.fa"],
        "Rattus norvegicus (Rat)": ["/home/DATA2/trips/scamp/proteomes/rattus_norvegicus_proteome.fa", "rat", "placeholder", "rattus_norvegicus_proteome.fa"],
        "Escherichia coli": ["/home/DATA2/trips/scamp/proteomes/escherichia_coli_proteome.fa", "ecoli", "placeholder", "escherichia_coli_proteome.fa"],
        "Drosophila melanogaster (Fruit fly)": ["/home/DATA2/trips/scamp/proteomes/drosophila_melanogaster_proteome.fa", "drosophila", "placeholder", "drosophila_melanogaster_proteome.fa"],
        "Caenorhabditis elegans": ["/home/DATA2/trips/scamp/proteomes/c_elegans_proteome.fa", "celegans", "placeholder", "c_elegans_proteome.fa"],
        "Danio rerio (Zebrafish)(Brachydanio rerio)": ["/home/DATA2/trips/scamp/proteomes/danio_rerio_proteome.fa", "zebrafish", "placeholder", "danio_rerio_proteome.fa"],
        "Schizosaccaromyces pombe": ["/home/DATA2/trips/scamp/proteomes/schizo_pombe_proteome.fa", "schizo", "placeholder", "schizo_pombe_proteome.fa"],
        }

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


#FIND PROJECT SPECIES, REQUIRED FOR PARAMS FILE GENERATION AND PASSED TO MSFRAGGER_TO_SQLITE SCRIPT
species = str(project["species"][0])

if len(project["species"]) > 1:
        print("There is more than one organism in this study")
        sys.exit()
if not species in orgdict:
        print("The organism in this study is not in our proteome dictionary")
        sys.exit()
fastapath = orgdict[species][0]


#PRINT PROJECT BASICS TO TERMINAL
print(project["title"], "\n")
print(project["projectDescription"], "\n")


#DEFINE PROCESSING PROTOCOL TO FIND TMT, MODIFICATION, CLEAVAGE AND ENZYME
processing_protocol = str(project["sampleProcessingProtocol"]+" "+project["dataProcessingProtocol"])


#CHECK FOR TMT DATA
TMT = ["TMT", "Tandem Mass Tag", "Tandem mass tag", "SILAC", "iTRAQ"]
for x in TMT:
        if x in processing_protocol:
                print("SCAMP has found reference to Isotope-labelled data in the processing protocol for this project. Such data is not currently recommended for analysis with this pipeline. Please$
                print(processing_protocol)
                input = input()
                if input != "":
                        sys.exit()


#GET PROJECT FIXED MODIFICATION
cmm_cys = ["Carbamidomethylation of cysteine", "Carbamidomethyl (C)", "carbamidomethylation of cysteine", "cysteine carbamidomethylation", "carbamidomethylation on cysteine"]
fixedmod = "unknown"
for x in cmm_cys:
        if x in processing_protocol:
                fixedmod = "0"
prop_cys = ["Propionamide on cysteine", "propionamide of cysteine", "Propionamide of cysteine"]
for x in prop_cys:
        if x in processing_protocol:
                fixedmod = "1"
dit_cys = ["Dithiomethylation of cysteine", "dithiomethylation of cysteine"]
for x in dit_cys:
        if x in processing_protocol:
                fixedmod = "2"
cxm_cys = ["Carboxymethylation of cysteine", "carboxymethylation of cysteine", "Carboxymethyl (C)", "cysteine carboxymethylation", "Cysteine carboxymethylation"]
for x in cxm_cys:
        if x in processing_protocol:
                fixedmod = "3"
if fixedmod == "unknown":
        print("SCAMP could not find the fixed modification in the information retrieved from PRIDE. The default of Carbamidomethyl (C) will be used.")
        fixedmod = 0

#GET MISSED CLEAVAGE NUM
onemissed = ["one missed cleavage", "One missed cleavage", "1 missed cleavage", "single missed cleavage"]
twomissed = ["two missed cleavages", "2 missed cleavage", "Two missed cleavages", "2 missed cleavages", "two missed cleavages"]
threemissed = ["three missed cleavages", "Three missed cleavages", "3 missed cleavages", "three missed cleavage"]
fourmissed = ["four missed cleavages", "four missed cleavage", "Four missed cleavages", "4 missed cleavage"]
fivemissed = ["five missed cleavages", "five missed cleavage", "Five missed cleavages", "5 missed cleavage"]

cleavage = "2"
for x in onemissed:
        if x in processing_protocol:
                cleavage = "1"
for x in twomissed:
        if x in processing_protocol:
                cleavage = "2"
for x in threemissed:
        if x in processing_protocol:
                cleavage = "3"
for x in fourmissed:
        if x in processing_protocol:
                cleavage = "4"
for x in fivemissed:
        if x in processing_protocol:
                cleavage = "5"


#GET ENZYME
enzyme = "unknown"
trypsin = ["trypsin", "Trypsin", "Tryptic", "tryptic"]
for x in trypsin:
        if x in processing_protocol:
                enzyme = "Trypsin"
if enzyme == "unknown":
        print("SCAMP could not find the enzyme in the information retrieved from PRIDE. Please read the processing protocol to see if the enzyme is specified \n")
        print(processing_protocol)
        print(" Please manually enter the enzyme for this study, or press enter to proceed with the default (Trypsin) \n")
        answer = input()
        if answer == "":
                enzyme = "Trypsin"
        else:
                enzyme = answer
if not os.path.isfile(enzyme+".txt"):
        print("The enzyme for this study has not been encountered by SCAMP before. Please enter the residues after which this enzyme cleaves (for example for Trypsin, KR - Lysine and Arginine)")
        aftercleave = input()
        print("Now please enter residues after which the enzyme WILL NOT cut (For example for Trypsin, P - Proline), or press enter if there is no such residue")
        afternocleave = input()
        tempenz = open("./Trypsin.txt", "r")
        newenz = open("./"+enzyme+".txt", "w")
        for line in tempenz:
                newenz.write(line.replace("KR", aftercleave).replace("P", afternocleave))
        tempenz.close()
        newenz.close()

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
filelist.sort()


#CONTINGENCY FOR PROJECTS WITH NO RAW FILES, MANUAL DOWNLOAD FUNCTION
if len(filelist) == 0:
        print("This project does not have any raw files, would you like to execute the manual download function? (y/n)")
        response = input()
        if response == "y":
                if not os.path.isdir(sys.argv[1]+"_manualdwnld"):
                        os.makedirs(sys.argv[1]+"_manualdwnld")
                print("INSTRUCTIONS: Please manually download the files from PRIDE into the "+sys.argv[1]+"_manualdwnld folder that has just been created in the scamp directory")
                print("When the download is complete, press enter to continue")
                manualready = input()
                if manualready == "":

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
                                                subprocess.call("mv "+rawpaths[x]+" "+batchdirect, shell=True)

                                        batch_no += 1

        else:
                sys.exit()

#PIPELINE ACTION IN BATCH SYSTEM
batch_no = -1
print(len(filelist))
total_files = 0

for i in range(0,len(filelist),batch):
        batch_no += 1
        print("batch "+str(batch_no))
        print("Checking for completion")
        sqlitetest = []
        for x in range(i,i+batch):
                if x > (len(filelist)-1):
                        break
                filename = filelist[x]
                sqlitecheck = filename.replace(".raw", ".sqlite").replace(".RAW",".sqlite")
                if os.path.isfile("./"+sys.argv[1]+"_sqlites/final_"+sqlitecheck):
                        total_files += 1
                        #print("success", "./"+sys.argv[1]+"_sqlites/"+sqlitecheck)
                        #print("total files "+str(total_files))
                        sqlitetest.append("yes")
                else:
                        #print(sqlitecheck+" does not exist")
                        sqlitetest.append("no")

        #if no not in sqlite test, continue
        if not "no" in sqlitetest:
                print ("All sqlite files for this batch have already been made, continuing to the next batch")
                continue


        #MAKE DIRECTORY FOR THE BATCH CONSISTING OF THE PROJECT ACCESSION AND BATCH NUMBER
        if not os.path.isdir("{}_{}".format(sys.argv[1],batch_no)):
                os.makedirs("{}_{}".format(sys.argv[1],batch_no))
        pathlist = []

        #FETCH RAW FILES PROVIDED NEITHER THEY DONT ALREADY EXIST
        print("\n DOWNLOADING FILES FOR BATCH "+str(batch_no))
        jnames = []
        rnames = []
        for x in range(i,i+batch):
                if x > (len(filelist)-1):
                        break
                filename = filelist[x]
                jname = filename.split(".")
                jnames.append(jname[0])
                rnames.append(filename)
                if os.path.isfile("./"+sys.argv[1]+"_sqlites/final_"+jname[0]+".sqlite"):
                        continue
                if not os.path.isfile("./"+sys.argv[1]+"_"+str(batch_no)+"/"+filename):
                        if not os.path.isdir("./"+sys.argv[1]+"_"+str(batch_no)+"/combined.txt"):
                                if not os.path.isfile("./"+sys.argv[1]+"_sqlites/"+jname[0]+".sqlite"):
                                        #print(filedict[filename])
                                        print("downloading", filename, "to", "/home/DATA2/trips/scamp/"+str(sys.argv[1])+"_"+str(batch_no))
                                        wget.download(filedict[filename], "/home/DATA2/trips/scamp/"+str(sys.argv[1])+"_"+str(batch_no))
                pathlist.append("/home/DATA2/trips/scamp/"+str(sys.argv[1])+"_"+str(batch_no)+"/"+filename)
        email(batch_no, "Files downloaded")

        #STRING CREATION FOR SOME OF THE MSFRAGGER CALLS
        joinerraw = " "+sys.argv[1]+"_"+str(batch_no)+"/"
        rawstring = sys.argv[1]+"_"+str(batch_no)+"/"+(joinerraw.join([x for x in rnames]))

        joinerpepXML = ".pepXML "+sys.argv[1]+"_"+str(batch_no)+"/"
        pepXMLstring = sys.argv[1]+"_"+str(batch_no)+"/"+(joinerpepXML.join([x for x in jnames]))+".pepXML"

        joinerinter = ".pep.xml "+sys.argv[1]+"_"+str(batch_no)+"/interact-"
        interpepxmlstring = sys.argv[1]+"_"+str(batch_no)+"/interact-"+(joinerinter.join([x for x in jnames]))+".pep.xml"

        today = datetime.date.today()
        date = today.strftime("%Y-%m-%d")
        databasename = date+"-decoys-contam-"+orgdict[species][3]

        tsvlist = []
        for j in jnames:
                tsvlist.append(sys.argv[1]+"_"+str(batch_no)+"/"+j+".tsv")


        #PARAMS FILE TEMPLATE MODIFICATION
        print("\n CREATING PARAMETER FILE FOR BATCH "+str(batch_no))
        f = open("./fragger.params", 'r')
        nf = open("./"+sys.argv[1]+"_"+str(batch_no)+".params", "w")
        mf = open("msfmods_"+str(fixedmod)+".txt", "r")
        ef = open(enzyme+".txt", "r")
        fixedmodlst = mf.readlines()
        fixedmodcontent = "".join([i for i in fixedmodlst])
        enzymelst = ef.readlines()
        enzymecontent = "".join([i for i in enzymelst])
        for line in f:
                nf.write(line.replace('FASTAPATH', databasename).replace('CLEAVAGE', cleavage).replace('FIXEDMOD', fixedmodcontent).replace("ENZYME", enzymecontent))
        nf.close()
        f.close()
        mf.close()
        parampath = sys.argv[1]+"_"+str(batch_no)+".params"

        #PASS TO MSFRAGGER
        tsvcheck = []
        removelist = []
        for x in tsvlist:
                if os.path.isfile(x):
                        tsvcheck.append("yes")
                        removelist.append(x)
                else:
                        tsvcheck.append("no")

        if "no" in tsvcheck:
                print("\n RUNNING MSFRAGGER ANALYSIS ON BATCH "+str(batch_no))
                for x in removelist:
                        subprocess.call("rm "+x, shell=True)
                subprocess.call("philosopher workspace --init", shell=True)
                subprocess.call("philosopher database --custom "+fastapath+" --contam", shell=True)
                subprocess.call("java -Xmx32g -jar MSFragger/MSFragger.jar "+parampath+" "+rawstring, shell=True)
                #subprocess.call("philosopher peptideprophet --database "+databasename+" --ppm --accmass --expectscore --decoyprobs --nonparam "+pepXMLstring, shell=True)
                #subprocess.call("philosopher proteinprophet "+interpepxmlstring, shell=True)
                #subprocess.call("philosopher filter --razor --pepxml "+interpepxmlstring+" --protxml "+sys.argv[1]+"_"+str(batch_no)+"/interact.prot.xml", shell=True)
                #subprocess.call("philosopher report", shell=True)
                subprocess.call("philosopher workspace --clean", shell=True)
        else:
                pass

        #OBTAIN POSITIONAL INFO FROM PEPTIDE.TSV
        print("\n OBTAINING POSITIONAL INFORMATION FOR BATCH "+str(batch_no))
        fasta_dict = {}
        fasta_file = open(databasename).read()
        for line in fasta_file.split(">")[1:]:
                splitline = line.split("\n")
                header = re.sub(r".*\|(\w{5,12})\|.*", r"\1", splitline[0])
                seq = "".join(splitline[1:]).replace('L', 'I')
                fasta_dict[header] = seq

        label = 0
        for x in tsvlist:
                indlabel = label
                if not os.path.isfile("./"+sys.argv[1]+"_"+str(batch_no)+"/final_"+jnames[indlabel]+".tsv"):
                        print(x)
                        df = pd.read_csv(x, sep='\t')
                        sequence_positions = []
                        for index, entry in enumerate(df['protein']):
                                try:
                                        pept_seq = df['peptide'].iloc[index].replace('L', 'I')  # replace L with I for matchi$
                                        prot_seq = fasta_dict[entry]
                                        sequence_positions.append(3*(prot_seq.find(pept_seq) + 1))
                                except:
                                        sequence_positions.append(000)

                        df['sequence_start_position'] = sequence_positions
                        df.to_csv(sys.argv[1]+"_"+str(batch_no)+'/final_'+jnames[indlabel]+".tsv", sep='\t', index=False)
                label +=1


        #CHECK IF THERE IS AN SQLITE FILE FOR EVERY FILE IN THE BATCH, IF NOT RUNS MAXQUANT_TO_SQLITE SCRIPT. IF SOME BUT NOT ALL FILES HAVE SQLITE FILE, DELETES EVERY SQLITE FILE BEFORE RUNNING SC$
        sqlitetest = []
        sqliteyes = []
        for x in jnames:
                if not os.path.isfile("./"+sys.argv[1]+"_sqlites/final_"+x+".sqlite"):
                        sqlitetest.append("no")
                else:
                        sqlitetest.append("yes")
                        sqliteyes.append(x)

        if "no" in sqlitetest:
                for x in sqliteyes:
                        subprocess.call("rm /home/DATA2/trips/scamp/"+str(sys.argv[1])+"_"+str(batch_no)+"/"+x+".sqlite", shell="True")
                print("\n CREATING SQLITE FILES FOR BATCH "+str(batch_no))
                subprocess.call("python msfragger_to_sqlite.py ./"+sys.argv[1]+"_"+str(batch_no)+" "+orgdict[species][1]+" "+sys.argv[1], shell=True)

        #REMOVES RAW FILES IF BOTH RAW AND SQLITE ARE PRESENT
        for x in filelist:
                basename = x.replace(".raw", "")
                if os.path.isfile("./"+sys.argv[1]+"_sqlites/final_"+basename+".sqlite") and os.path.isfile("./"+sys.argv[1]+"_"+str(batch_no)+"/"+x):
                                subprocess.call("rm /home/DATA2/trips/scamp/"+str(sys.argv[1])+"_"+str(batch_no)+"/"+x, shell="True")


        #EMAIL NOTIFICATION OF SUCCESSFUL RUN
        sqlitetest = []
        for x in jnames:
                if not os.path.isfile("./"+sys.argv[1]+"_sqlites/final_"+x+".sqlite"):
                        sqlitetest.append("no")
                else:
                        sqlitetest.append("yes")

        print(sqlitetest)
        if not "no" in sqlitetest:
                email(batch_no, "sqlite file creation successful")
                pass

        #DELETE DATABASE USED FOR SEARCH
        subprocess.call("rm "+databasename, shell=True)
        subprocess.call("rm "+parampath, shell=True)

#WHEN PROJECT IS FINISHED APPEND ACCESSION TO FILE
finishedlist = open("finishedprojects.txt", "a+")
finishedlist.write(sys.argv[1] + '\n')
finishedlist.close()





