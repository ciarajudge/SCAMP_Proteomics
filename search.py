from sqlitedict import SqliteDict
import sqlite3
import os
import sys

connection = sqlite3.connect("/home/DATA/www/tripsviz/tripsviz/trips_annotations/homo_sapiens/homo_sapiens.v2.sqlite")
connection.text_factory = str
cursor = connection.cursor()

master_dict = {}

traninfo = {}

cursor.execute("SELECT transcript, cds_start, cds_stop FROM transcripts;")
result = cursor.fetchall()
for row in result:
	cds_start = min(row[1],row[2])
	cds_stop = max(row[1],row[2])
	traninfo[row[0]] = {"cds_start":cds_start,"cds_stop":cds_stop}

sqlite_list = []


for file in os.listdir(sys.argv[1]):
    if file.endswith(".sqlite"):
        sqlite_list.append(os.path.join(sys.argv[1], file))

for filename in sqlite_list:
	opendict = SqliteDict(filename)
	for tran in opendict:
		if tran not in master_dict:
			master_dict[tran] = {"five":0,"three":0, "oof":0, "nc":0}
		try:
			counts = opendict[tran]["unambig"]
		except:
			continue
		for readlen in counts:
			#print "readlen", readlen
			#print "cds start, cds stop", traninfo[tran]["cds_start"], traninfo[tran]["cds_stop"]
			for pos in counts[readlen]:
				#print "pos", pos	
				if pos < traninfo[tran]["cds_start"]:
					#print "adding to fiveprime"
					master_dict[tran]["five"] += counts[readlen][pos]
				elif pos+readlen > traninfo[tran]["cds_stop"]:
					#print "adding to threeprime"
					master_dict[tran]["three"] += counts[readlen][pos]
				elif pos%3 != (traninfo[tran]["cds_start"]+1)%3:
					master_dict[tran]["oof"] += counts[readlen][pos]

outfile = open("{}Unexpected_peptides.txt".format(sys.argv[1]),"w")
outfile.write("Tran, 5',3',OOF,NC\n")

for tran in master_dict:
	outfile.write("{},{},{},{},{}\n".format(tran, master_dict[tran]["five"], master_dict[tran]["three"], master_dict[tran]["oof"], master_dict[tran]["nc"]))
