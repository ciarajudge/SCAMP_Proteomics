from sqlitedict import SqliteDict
import sys
import collections
import os
import glob, os



    
    
    
    
master_dict = {}



input_dir = sys.argv[1]
outfile_name = sys.argv[2]
sqlite_files = []
os.chdir(input_dir)
for filename in glob.glob("*.sqlite"):
    sqlite_files.append(input_dir+filename)



file_count = 0
for filename in sqlite_files:
	#print "filename", filename
	count_dict = SqliteDict(filename,autocommit=False)
	keys = count_dict.keys()
	file_count += 1
	print "file count", file_count
	for key in count_dict.keys():
		#print "key", key
		if key not in master_dict:
			master_dict[key] = count_dict[key]
		else:
			value_type = type(count_dict[key])
			file_key = count_dict[key]
			if value_type == dict:
				if "unambig" in file_key or "ambig" in file_key:
					for ambig_type in file_key:
						if ambig_type not in master_dict[key]:
							master_dict[key][ambig_type] = file_key[ambig_type]
						else:
							for readlen in file_key[ambig_type]:
								if readlen not in master_dict[key][ambig_type]:
									master_dict[key][ambig_type][readlen] = file_key[ambig_type][readlen]
								else:
									for pos in file_key[ambig_type][readlen]:
										if pos not in master_dict[key][ambig_type][readlen]:
											master_dict[key][ambig_type][readlen][pos] = file_key[ambig_type][readlen][pos]
										else:
											master_dict[key][ambig_type][readlen][pos] += file_key[ambig_type][readlen][pos]
				else:
					#print key
					for tran in file_key:
						if tran not in master_dict[key]:
							master_dict[key][tran] = file_key[tran]
						else:
							try:
								master_dict[key][tran] += file_key[tran]
							except:
								print "Skipping entry", tran
			elif value_type == str:
				print "skipping key:",key
			elif value_type == int:
				master_dict[key] += file_key





print "saving to {}/{}".format(input_dir ,outfile_name)

outfile = SqliteDict("{}/{}.sqlite".format(input_dir ,outfile_name))
for key in master_dict:
	outfile[key] = master_dict[key]
outfile.commit()
outfile.close()
