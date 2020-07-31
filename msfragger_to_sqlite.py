import sys
import sqlite3
from sqlitedict import SqliteDict
import os



if len(sys.argv) != 4:
        print "Error, need 5 arguments, python maxquant_to_sqlite.py batch_folder organism project_accession"
        sys.exit()

#create a folder for all sqlite files of the project
sqlitepath= './'+sys.argv[3]+"_sqlites/"
if not os.path.exists(sqlitepath):
        os.makedirs(sqlitepath)

batch_folder = sys.argv[1]

for filename in os.listdir(batch_folder):
        if filename.endswith(".tsv") and filename.startswith("final_"):
                infile = open(os.path.join(batch_folder+"/"+filename)).readlines()
                print "reading lines for "+batch_folder+"/"+filename
                file = filename.replace(".tsv", "")
                print file
                master_dict = {}

                #Column position changes depending on number of PTMs passed to maxquant, so find relevant column positions here
                peptide_index = 0
                position_index = 0
                protein_index = 0
                ind = 0
                for item in (infile[0].split("\t")):
                        if item == "peptide":
                                peptide_index = ind
                        if item == "protein":
                                protein_index = ind
                        ind += 1
                position_index = len(infile[0].split("\t"))-1

                for line in infile[1:]:
                        splitline = line.split("\t")
                        seq = splitline[peptide_index]
                        cleantranscript = splitline[protein_index].replace("rev_", "")
                        if " " in cleantranscript:
                                print "unrecognised transcript, skipping read for peptide "+seq+" in "+cleantranscript
                                continue
                        transcript = cleantranscript.split("_")[0]
                        frame = int((cleantranscript.split("_")[-1]).replace("frame", ""))
                        length = 3*(len(seq))
                        if frame == 0 :
                                position = int(splitline[position_index])-1
                        elif frame == 1:
                                position = int(splitline[position_index])
                        elif frame == 2:
                                position = int(splitline[position_index])+1

                        if transcript not in master_dict:
                                master_dict[transcript] = {"unambig":{}, "ambig":{}}
                        if length not in master_dict[transcript]["unambig"]:
                                master_dict[transcript]["unambig"][length] = {}
                        if position not in master_dict[transcript]["unambig"][length]:
                                master_dict[transcript]["unambig"][length][position] = 1

                orgidict = {
                "yeast": "/home/DATA/www/tripsviz/tripsviz/trips_annotations/saccharomyces_cerevisiae/saccharomyces_cerevisiae.v2.sqlite",
                "human": "/home/DATA/www/tripsviz/tripsviz/trips_annotations/homo_sapiens/homo_sapiens.v2.sqlite",
                "mouse": "/home/DATA/www/tripsviz/tripsviz/trips_annotations/mus_musculus/mus_musculus.v2.sqlite",
                "rat": "/home/DATA/www/tripsviz/tripsviz/trips_annotations/rattus_norvegicus/rattus_norvegicus.v2.sqlite",
                "ecoli": "/home/DATA/www/tripsviz/tripsviz/trips_annotations/escherichia_coli/escherichia_coli.v2.sqlite",
                "drosophila": "/home/DATA/www/tripsviz/tripsviz/trips_annotations/drosophila_melanogaster/drosophila_melanogaster.v2.sqlite",
                "celegans": "/home/DATA/www/tripsviz/tripsviz/trips_annotations/caenorhabditis_elegans/caenorhabditis_elegans.v2.sqlite",
                "zebrafish": "/home/DATA/www/tripsviz/tripsviz/trips_annotations/danio_rerio/danio_rerio.v2.sqlite",
                "schizo": "/home/DATA/www/tripsviz/tripsviz/trips_annotations/schizosaccharomyces_pombe/schizosaccharomyces_pombe.v2.sqlite",
                }


                path = orgidict[sys.argv[2]]

                traninfo = {}
                connection = sqlite3.connect(path)
                connection.text_factory = str
                cursor = connection.cursor()
                cursor.execute("SELECT transcript,cds_start,cds_stop FROM transcripts;")
                result = cursor.fetchall()
                for row in result:
                        traninfo[row[0]] = {"cds_start":row[1],"cds_stop":row[2]}

                master_dict["unambiguous_fiveprime_totals"] = {}
                master_dict["unambiguous_cds_totals"] = {}
                master_dict["unambiguous_threeprime_totals"] = {}
                master_dict["unambiguous_all_totals"] = {}
                master_dict["ambiguous_fiveprime_totals"] = {}
                master_dict["ambiguous_cds_totals"] = {}
                master_dict["ambiguous_threeprime_totals"] = {}
                master_dict["ambiguous_all_totals"] = {}

                for transcript in master_dict:
                        if transcript in traninfo:
                                cds_start = traninfo[transcript]["cds_start"]
                                cds_stop = traninfo[transcript]["cds_stop"]
                                allcounts = 0
                                fivecount = 0
                                threecount = 0
                                cdscount = 0

                                counts = master_dict[transcript]["unambig"]
                                for result in counts:
                                        for position in counts[result]:
                                                count = counts[result][position]
                                                allcounts += count
                                                if position <= cds_start:
                                                        fivecount += count
                                                elif position > cds_start and position <= cds_stop:
                                                        cdscount += count
                                                elif position > cds_stop:
                                                        threecount += count

                                master_dict["unambiguous_fiveprime_totals"][transcript] = fivecount
                                master_dict["unambiguous_cds_totals"][transcript] = cdscount
                                master_dict["unambiguous_threeprime_totals"][transcript] = threecount
                                master_dict["unambiguous_all_totals"][transcript] = allcounts
                                master_dict["ambiguous_fiveprime_totals"][transcript] = 0
                                master_dict["ambiguous_cds_totals"][transcript] = 0
                                master_dict["ambiguous_threeprime_totals"][transcript] = 0
                                master_dict["ambiguous_all_totals"][transcript] = 0



                output = SqliteDict(sqlitepath+file+".sqlite",autocommit=False)
                for key in master_dict:
                        output[key] = master_dict[key]
                output.commit()
                output.close()
