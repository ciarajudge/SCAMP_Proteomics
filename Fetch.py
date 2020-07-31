import sys
import json
import wget
import requests

#Welcome to Fetch

keyword = str(sys.argv[1])

#Count Relevant Projects
print("Searching PRIDE for count of projects containing keyword "+ keyword)
counturl = str("https://www.ebi.ac.uk/pride/ws/archive/project/count?query="+ keyword)
count = (requests.get(counturl)).text
print(count+" projects on the PRIDE Archive matched this keyword")

#Retrieve List of Relevant Projects
relurl = str("https://www.ebi.ac.uk/pride/ws/archive/project/list?query="+keyword+"&show="+str(count))
biglist = (requests.get(relurl)).text
interlist = biglist.split("PXD")

finallist = []

print ("interlist",interlist)
for x in interlist:
    accessionno = x[0]+x[1]+x[2]+x[3]+x[4]+x[5]
    accession = "PXD"+accessionno
    finallist.append(accession)

del finallist[0]

print("List of relevant projects has been obtained")
print (finallist)

#Read in already completed projects
print("Checking list obtained from PRIDE fro already completed projects")
finishedprojects = open("finishedprojects.txt","r")
projectlist = finishedprojects.readlines()
finishedlist = []
for x in projectlist:
    x = x.strip("\n")
    finishedlist.append(x)

#Eliminate already completed projects from list
for x in finishedlist:
    query = x
    if query in finallist:
        finallist.remove(x)
        print(x+" has already been run through SCAMP and has been removed from the list obtained from PRIDE")

#Ask how to proceed
number = len(finallist)
print("Fetch can recommend "+str(number)+" of projects from the PRIDE archive based on your criteria. How many of these would you like to send to the SCAMP Pipeline?")
scamparg = input()

#could insert a subprocess call here using scamparg to call the first x number of projects in the list

sys.exit()

