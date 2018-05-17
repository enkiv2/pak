#!/usr/bin/env python
""" Pak - a python-based HyperCard format
Format is based on the Pickle format, with nested lists and dictionaries.
Supports lists, dictionaries, strings, code, and arbitrary data, in an organized format.
"""
import pickle
import sys
import os

global PAK_VERSION
global datamode

PAK_VERSION='0.04'
data_mode=""

def create_pak(items):
	""" Creates a Pak from a data structure
	Should be in the following format:
	{ name1:{ 
		\'type\':type , 
		\'value\':value , 
		\'links\':{ 
			pos1:{ card:CARD, bpos:BPOS, 
				epos:EPOS } , pos2...
			}
		}
	  name2... }
	Where name* refers to the name of the object, 
	value refers to its data, links refers to the 
	internal hyperlinks, and type is the data type, 
	one of the following: 
	* code - compiled python code
	* text - a string
	* dict - a dictionary
	* list - a list
	* html - an html/xml/etc. (i.e. web-type) file
	* data - some kind of data accessed by code 
	inside the pak or an outside program
	pos* refers to a hash of slices, in the form of 
	\'start:end\', which represents the start and 
	end positions of the link in the data.
	"""
	return pickle.dumps(items)
def create_pak_file(items, file):
	""" Creates a Pak file from data structure
	Calls create_pak
	"""
	x = open(file, "w")
	x.write(create_pak(items))
	x.close
def create_pak_dict(items):
	""" Creates a dictionary suitable for create_pak
	Input is like that of create_pak , except that the 
	key for value is a filename containing the data to 
	be read into it
	Also creates a header (the card named '.header'),
	a dictionary whose possible key values are as 
	follows:
		version		The value of PAK_VERSION
				(for backwards compatibility)
		data_mode	'' for ascii, 'b' for binary
		key_num		The number of keys
		pakker		The program name/vendor/version
				hash:
				'pak' means it is made by the 
				official library (this module)
		index		The index page (like on a web
				site). Currently, there is no 
				way to change this from the 
				command line, so you need to
				accept the default of 'index'
	
	Note: files with data_mode=='b' are encoded using 
	the python struct module. The format is a little-
	endian unsigned byte array.
	"""
	global data_mode
	global PAK_VERSION
	for x in items.keys():
		f = items[x]['value']
		h=open(f, "r"+data_mode)
		items[x]['value'] = h.read()
		if data_mode=='b':
			items[x]['.fmt']='<'+str(len(items[x]['value']))+'B'
			items[x]['value']=struct.pack(items[x]['.fmt'], items[x]['value'])			
	items['.header']={}
	items['.header']['type']='dictionary'
	items['.header']['value']={}
	items['.header']['value']['version']=PAK_VERSION
	items['.header']['value']['data_mode']=data_mode
	items['.header']['value']['key_num']=len(items)
	items['.header']['value']['pakker']="pak "+PAK_VERSION
	items['.header']['value']['index']='index'
	h.close()
	return items
def create(infile, outfile):
	""" Creates a pak from input and output files
	Loads a file in the plaintext format of create_pak_dict, 
	and outputs a pak file.
	"""
	h = open(infile, "r")
	create_pak_file(create_pak_dict(eval(h.read())), outfile)
	h.close()
def get_value(items, name):
	""" Gets the value of the card name in the pak items
	Looks it up in the dictionary.
	"""
	return items[name]['value']
def get_link(items, name, pos):
	""" Finds the links for position pos in card name in pak items
	Looks it up in the dictionary and checks for whether each link 
	found overlaps with pos
	"""
	t = []
	for x in items[name]['links'].keys():
		if pos in range(x[:(x.find(':')-1)], x[(x.find(':')+1):]):
			j = items[name]['links'][x]
			j.append(x)
			t.append(j)
	return t
def get_offset_links(items, name, bpos, epos):
	"""Gets the data slices that a link links to
	Also formats the backlinks to make them point to the right place
	"""
	t=[]
	for x in range(bpos, epos):
		t.append(get_link(items, name, x))
	t2={}
	i=0
	while i<len(t):
		n=str(int(t[i][1][:t[i][1].find(":")-1])-bpos)+(int(t[i][1][t[i][1].find(":")+1])-bpos)
		t2[n][card]=t[i][0][0]
		t2[n][bpos]=int(t[i][1][:t[i][1].find(":")-1])
		t2[n][epos]=int(t[i][1][t[i][1].find(":")+1:])
	return t2
def get_link_data(items, name, pos):
	""" Gets all data linked to by a certain link, if it exists
	Finds the link name and position using get_link, and then 
	finds the data and returns it, with markers.
	The returned data is in the following format:
		{ name1:{
			'backlink':{ 'card':CARD, 'bpos':BPOS, 'epos':EPOS },
			'value':VALUE,
			'links':{ pos1:{ 'card':CARD, 'bpos':BPOS, 
					'epos':EPOS },
				pos2...
			},
		name2... }
	backlink contains the data for where the link came from. BPOS and 
	EPOS are beginning and ending positions, respectively. 
	"""
	t2={}
	t=get_link(items, name, pos)
	i=0
	while i<len(t):
		t2[t[i][0][0]][backlink][card]=name
		t2[t[i][0][0]][backlink][bpos]=int(t[i][1][:t[i][1].find(":")-1])
		t2[t[i][0][0]][backlink][epos]=int(t[i][1][t[i][1].find(":")+1:])
		t2[t[i][0][0]][value]=get_value(items, name)[t[i][0][1]:t[i][0][2]]
		t2[t[i][0][0]][links]=get_offset_links(items, t[i][0][0], t[i][0][1], t[i][0][2])
	return t2
def main():
	global data_mode
	global PAK_VERSION
	infile=""
	outfile=""
	operation=""
	print (sys.argv)
	sys.argv.pop(0)
	print (sys.argv)
	for x in sys.argv:
		if x == "-if":
			infile=sys.argv[sys.argv.index(x) + 1]
		elif x == "-of":
			outfile=sys.argv[sys.argv.index(x) + 1]
		elif x == "-c":
			operation="create"
		elif x == "-d":
			operation="dump"
		elif x == "-b":
			mode='b'
		elif x == '-u':
			operation='unpak'
		elif x == '-v':
			print (PAK_VERSION)
			sys.exit(0)
		elif x == "-h" or x == "--help":
			print (""" pak - the python hypercard format utility
Usage:
	pak [ -h ] | [ -v ] | [ [ -if FILE ] [ -of FILE ] [ -c | -d | -u ]  
		[ -b ] ]
Options:
-h		Print this help
-v		Print version
-if		Make FILE the input file
-of		Make FILE the output file
-c		Create PAK file
-d		Dump PAK file
-u		UnPAK file
-b		Binary format

(c) 2006 John Ohno
Licensed under the GNU LGPL
""")
			sys.exit(0)
	if operation=="":
		print ("pak: could not determine operation! Please try pak -h for usage details")
		sys.exit(-1)
	elif operation=="create":
		try:
			create(infile, outfile)
		except IOError:
			print ("An IO exception occurred while creating the PAK. Check your files and permissions.")
			sys.exit(-1)
	elif operation=="dump":
		try:
			i=open(infile)
			x=pickle.load(i)
			data_mode=x['.header']['value']['data_mode']
			if data_mode=='b':
				for item in x.keys:
					x[item]['value']=struct.unpack('<'+x[item]['.fmt']+'B', x[item]['value'])
			if (outfile==""):
				print (x)
			else:
				o=open(outfile, 'w')
				o.write(str(x))
		except IOError:
			print ("An IO exception occurred while dumping. Check your files and permissions.")
			sys.exit(-1)
	elif operation=="unpak":
		try:
			i=open(infile)
			x=pickle.load(i)
			path=os.curdir+os.sep+outfile+os.sep
			os.mkdir(path)
			data_mode=x['.header']['value']['data_mode']
			if data_mode=='b':
				for item in x.keys():
					x[item]['value']=struct.unpack(x[item]['.fmt'], x[item]['value'])
			for item in x.keys():
				print (item)
				temp=open(path+item, 'w'+data_mode)
				if 'type' in x[item]:
					if x[item]['type']!='data':
						temp.write(str(x[item]['value']))
					else:
						print ("Type existed and == 'data'.")
						temp.write(x[item]['value'])
				else:
					temp.write(x[item]['value'])
				temp.close()
				if 'links' in x[item]:
					temp=open(path+item+'.__links__', 'w')
					temp.write(str(x[item]['links']))
					temp.close()
		except IOError:
			print ("An IO exception has occurred while unpacking. Check your files, directories, and permissions.")
			sys.exit(-1)
if sys.argv[0].find("pak") != -1:
	main()
