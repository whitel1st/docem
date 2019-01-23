#!/usr/bin/python3

import os  
import shutil
import json
import uuid
import argparse
# To create random refernces to XXE
import string 
import random
# To work with XXE payloads
import json

from lxml import etree, objectify

def make_tmp_clean_again(paths, mode):

	if mode ==  'original':
		if os.path.exists(paths['path_to_unzipped_folder_original']):
			shutil.rmtree(paths['path_to_unzipped_folder_original'])

		if os.path.exists(paths['path_to_copied_file']):
			os.remove(paths['path_to_copied_file'])

	elif mode == 'copy':

		if os.path.exists(paths['path_to_unzipped_folder_modified']):
			shutil.rmtree(paths['path_to_unzipped_folder_modified'])

		if os.path.exists(paths['path_to_modified_file']):
			os.remove(paths['path_to_modified_file'])

# STEP 0
def document_prepare_initial_paths(path_to_file):

	path_to_script =  os.path.dirname(os.path.relpath(__file__))
	path_to_tmp = path_to_script + '/tmp/'

	# That hack needed because I switched from full paths
	# to relevant; but I still want to have ability to use full paths
	# What it does is: if path_to_script = '' than we need to remove first
	# slash fro path_to_tmp 
	# but it might break something
	if path_to_tmp.find('tmp') == 1: path_to_tmp = 'tmp/'

	# Create separate variables for an original file
	original_file_name = path_to_file.split('/')[-1].split('.')[0]
	original_file_ext = path_to_file.split('/')[-1].split('.')[1]

	# create variables for a copied files
	path_to_copied_file = path_to_tmp + original_file_name + '.zip'

	# create variables for an unzipped files
	unzipped_file_name = original_file_name + '_' + original_file_ext
	path_to_unzipped_folder_original = path_to_tmp + unzipped_file_name + '/'

	paths_and_names = {
		"path_to_script" : path_to_script,
		"path_to_tmp" : path_to_tmp,
		"path_to_orignal_file" : path_to_file,
		"path_to_copied_file" : path_to_copied_file,
		"path_to_unzipped_folder_original" : path_to_unzipped_folder_original,
		"path_to_unzipped_folder_modified" : path_to_unzipped_folder_original,
		"original_file_name" : original_file_name,
		"original_file_ext" : original_file_ext,
		"unzipped_file_name" : unzipped_file_name,
		"modified_file_name" : original_file_name,
		"path_to_modified_file" : ''
	}

	return(paths_and_names)

# Prepare path where document will be unzipped
def docuemnt_prepare_future_paths(paths, payload_type, payload_key, single_place='', offset=''):


	if payload_type == 'per_place':
		#postfix = '%s+%s'%(payload_type, payload) 
		postfix = '%s+%s+%s+%s'%(payload_type, single_place, payload_key, offset) 

	elif payload_type == 'per_file':
		#postfix = '%s+%s'%(payload_type, payload) 
		postfix = '%s+%s+%s'%(payload_type, single_place, payload_key) 

	elif payload_type == 'per_document':
		postfix = '%s+%s'%(payload_type, payload_key) 

	#postfix = '%s+%s+%s+%s'%(payload_type, single_places, payload, str(offset)) 

	paths['modified_file_name'] = paths['original_file_name'] + '-' + postfix 
	print('postfix',postfix)
	print("paths['original_file_name']",paths['original_file_name'])
	paths['path_to_unzipped_folder_modified'] = paths['path_to_tmp'] + paths['modified_file_name'] + '/'
	print("paths['modified_file_name']", paths['modified_file_name'])
	print("paths['path_to_unzipped_folder_modified']",paths['path_to_unzipped_folder_modified'])

	paths['path_to_modified_file'] = paths['path_to_tmp'] + paths['modified_file_name'] + '.zip'
	paths['path_to_packetd_file'] = paths['path_to_tmp'] +  paths['modified_file_name'] + '.' +  paths['original_file_ext']

	#tree_embedding[single_file_key]['pathmod'] = 
	#print(tree[single_place]['path'])

# copy, rename and unzip
def document_unpack(paths, doctype='doc'):

	if doctype == 'doc':
		# copy original file into script_script/dir and rename extension to .zip
		shutil.copy(paths["path_to_orignal_file"],paths["path_to_copied_file"])
		# unzip renamed file into direc
		shutil.unpack_archive(paths["path_to_copied_file"],paths["path_to_unzipped_folder_original"])
		# debug
		#print(paths["path_to_unzipped_folder_original"])

	elif doctype == 'folder':
		shutil.copy(paths["path_to_orignal_file"],paths["path_to_copied_file"])
		

def document_tree_generate(paths, opt=1):
	files_inside_unpacked_dir = {}
	for root, dirs, files in os.walk(paths["path_to_unzipped_folder_original"], topdown = False):
		for full_name in files:
			#print(os.path.join(root, name))

			path_to_file = os.path.join(root, full_name)
			path_in_tmp = path_to_file.replace(paths["path_to_unzipped_folder_original"],'')

			# Remove extension from file
			full_name_extension_offset = full_name.rfind('.')
			if full_name_extension_offset != -1:
				name_without_extension = full_name[:full_name.rfind('.')].replace('.','_')
			else:
				name_without_extension = full_name

			#full_name = full_name.replace('.','_')
			#print('\nfull_name',full_name)
			# Construct future key_name for an array of files inside a document
			key_name = '%s_%s'%(root, name_without_extension)
			# Remove path to a docuemnt and strip '_' symbol for those docuemnts that lies in a root of a docuemnt 
			#print('key_name',key_name)
			#print('key_name',key_name.replace(paths["path_to_unzipped_folder_original"],''))
			#key_name = key_name.replace(paths["path_to_unzipped_folder_original"],'').lstrip('_')
			key_name = key_name.replace(paths["path_to_unzipped_folder_original"],'')
			#print('key_name',key_name)

			files_inside_unpacked_dir[key_name] = {'path': path_to_file, 'path_in_tmp': path_in_tmp}

	return(files_inside_unpacked_dir)


# Add tmp paths of copied unzipped tmp document
# to tree_embedding
def document_tree_embedding_append_mod_paths(paths, tree_embedding):

	n = 'document_tree_embedding_append'
	
	#print(n,'path_to_modified_file', paths['path_to_modified_file'])
	#print(n,'path_to_unzipped_folder_modified', paths['path_to_unzipped_folder_modified'])

	for file_to_embed in tree_embedding.keys():
		tree_embedding[file_to_embed]['tmp_mod_path'] = paths['path_to_unzipped_folder_modified'] + tree_embedding[file_to_embed]['path_in_tmp']
		#print(tree_embedding[file_to_embed]['tmp_mod_path'])

def document_embed_payloads(paths, file_to_embed_name, payload_dict):

	payload_place = "single"
	# #file_to_embed_name = "content.xml" 
	# file_to_embed_path = paths["path_to_unzipped_folder_modified"] + '/' + file_to_embed_name

	# modfied_single_xml_file = modfy_xml_file(file_to_embed_path, payload_dict)

	# # For debug usage
	# #print(modfied_single_xml_file)
	# #print('file_to_embed_path',file_to_embed_path)

	# with open(file_to_embed_path, 'w') as file_to_embed:
	# 	file_to_embed.write(modfied_single_xml_file)
	# 	file_to_embed.close()

def modfy_xml_file(path_to_file, payload, attack ='xxe'):

	path_file_name = path_to_file.split('/')[-1]

	xml_tree = etree.parse(path_to_file)
	xml_root = xml_tree.getroot()

	# Convert xml_tree object to string with full documeetree.tostring(nt
	# 	etree.tostring(xml_tree)
	# Convert with 
	# 	etree.tostring(xml_tree, xml_declaration=True, encoding="UTF-8")

	if path_file_name == "content.xml":
		# main_text_clear 
		xml_root[2][0][1].text += ' ' + payload["var"]
		# main_text_bold
		xml_root[2][0][2][0].text += ' ' + payload["var"]
		# main_text_italic
		xml_root[2][0][3][0].text += ' ' + payload["var"]
		# main_text_und
		xml_root[2][0][4][0].text += ' ' + payload["var"]
		# main_text_strikethrough
		xml_root[2][0][5][0].text += ' ' + payload["var"]

	elif path_file_name == "meta.xml":
		xml_root[0][0].text += ' ' + payload["var"]


	elif path_file_name == "settings.xml":
		# 100
		xml_root[0][0][0][0][0].text += ' ' + payload["var"]
		# view2
		xml_root[0][0][0][0][1].text += ' ' + payload["var"]

	elif path_file_name == "styles.xml":
		# 00000000
		xml_root[1][0][1][0][0][0].text += ' ' + payload["var"]
		# 000000FF
		xml_root[1][0][1][1][0][0].text += ' ' + payload["var"]

	# Nice way. But how to add DTD after that. In TO-DO
	#xml_file_body = etree.tostring(xml_root, xml_declaration=True, encoding="UTF-8")
	# Small dirty trick with replace
	xml_file_body = etree.tostring(xml_root, encoding=str)
	xml_file_body = xml_file_body.replace('&amp;', '&')

	xml_head = '<?xml version="1.0" encoding="UTF-8" standalone="no" ?>'
	xml_head = xml_head + '\n' + payload["head"] + '\n' 
	xml_done = xml_head + xml_file_body

	return(xml_done)

# STEP 4
# zip into archive and rename
def document_pack(paths):

	# Split - because shutil will add .zip anyway
	#print(paths['path_to_unzipped_folder_modified'])
	shutil.make_archive(base_name=paths['path_to_modified_file'].split('.')[0],root_dir=paths['path_to_unzipped_folder_modified'],format='zip')
	# copy & rename zip to odt
	print('\n%s'%paths['path_to_modified_file'])
	print(paths['path_to_packetd_file'])
	shutil.copy(paths['path_to_modified_file'], paths['path_to_packetd_file'])

	
def document_copy_dir(paths):

	shutil.copytree(paths['path_to_unzipped_folder_original'], paths['path_to_unzipped_folder_modified'])


# 
# tree embeding structure
# { 
# 	'file1':{
# 		'tmp_mod_path':'',
# 		'places':[], 
# 		'path':'',
# 		'content':'',
# 		'path_in_tmp':'',
# 		'count':''
# 	},
# 	'file2':{

# 	},
# 	'file3':{

# 	},
# 	etc.
# }
def document_tree_embedding_points(paths, tree, magic_symbol):

	print('\nCount magic symbols')

	count_places = 0
	
	embedding = []
	tree_embedding = {}

	embedding_info = {}
	# For every document in a tree
	for file_key_name in tree.keys():
		# Read file and find all places 
		file_in_sample_path = tree[file_key_name]['path']

		with open(file_in_sample_path, 'r') as file_in_sample:
			file_in_sample_read = file_in_sample.read()
			file_in_sample.close()

			embedding_count = file_in_sample_read.count(magic_symbol)

			#tree_embedding will be consist only with those files does have magic symbols
			if embedding_count != 0:

				tree_embedding[file_key_name] = dict(tree[file_key_name])
				tree_embedding[file_key_name]['count'] =  embedding_count
				tree_embedding[file_key_name]['places'] = [index for index in range(len(file_in_sample_read)) if file_in_sample_read.startswith(magic_symbol, index)]	
				tree_embedding[file_key_name]['content'] = file_in_sample_read

				count_places += len(tree_embedding[file_key_name]['places'])
			print('\t%d\tsymbols in %s'%(embedding_count,file_key_name))


	embedding_info['num_of_files_to_embed'] = len(tree_embedding)
	embedding_info['num_of_places_to_embed'] = count_places

	#print('\n\t%d\ttotal files to embed' % len(tree_embedding))
	#print('\t%d\ttotal places to embed' % count_places)
	return(tree_embedding,embedding_info)

def payloads_read_file(path_to_payloads):

	payloads = {}

	with open(path_to_payloads, 'r') as payload_vectors_file:
		payload_vectors_file_read = payload_vectors_file.read().splitlines()

	payloads_number = len(payload_vectors_file_read)
	for p in range(payloads_number):
		payloads['payload_%d' % p] = payload_vectors_file_read[p]

	return(payloads)

def make_embedding_tree_clear_again(tree_embedding, current_file_key):

	to_clear_files = dict(tree_embedding)
	del(to_clear_files[current_file_key])

	# for debug
	#print(tree_embedding.keys())
	#print(to_clear_files.keys())
	
	for to_clear_file_key in to_clear_files.keys():
		cleared_file_content = to_clear_files[to_clear_file_key]['content'].replace(magic_symbol,'')

		with open(to_clear_files[to_clear_file_key]['tmp_mod_path'],'w') as cleared_file:
			cleared_file.write(cleared_file_content)
			cleared_file.close()

def interface_ask_user(embedding_info,paths):

	# embedding_info['num_of_files_to_embed'] = len(tree_embedding)
	# embedding_info['num_of_places_to_embed'] = len(tree_embedding)

	print('\n\t%d\ttotal files to embed' % embedding_info['num_of_files_to_embed'])
	print('\t%d\tplaces in a doc file to embed' % embedding_info['num_of_places_to_embed'])

	num_of_files = embedding_info['num_of_payloads']


	if embedding_info['payload_type'] == 'per_file':
		num_of_files *= embedding_info['num_of_files_to_embed']

	elif embedding_info['payload_type'] == 'per_place':
		num_of_files *= embedding_info['num_of_places_to_embed']

	print('\nFiles to be created %d' % num_of_files)
	#embedding_info
	answer = input('Continue?(y/n): ')
	
	if answer == 'n':
		make_tmp_clean_again(paths,'original')
		exit()

def interface_print_logo():
	logo = '''

_|_|_|                                                  
_|    _|    _|_|      _|_|_|    _|_|    _|_|_|  _|_|    
_|    _|  _|    _|  _|        _|_|_|_|  _|    _|    _|  
_|    _|  _|    _|  _|        _|        _|    _|    _|  
_|_|_|      _|_|      _|_|_|    _|_|_|  _|    _|    _|  
                                                                                                        
	'''
	print(logo)

if __name__ == '__main__':



	# Working with arguments
	parser = argparse.ArgumentParser(description='Create test ODT files')
	
	optional = parser._action_groups.pop()
	required = parser.add_argument_group('required arguments')
	
	required.add_argument('-s', dest='sample', type=str, help='path to sample file')
	
	optional.add_argument('-pm', dest='payload_mode',type=str,choices=['xss','xxe'])
	optional.add_argument('-xf', dest='xxe_file', type=str, help='url to use in XXE payload. Default is: \'file:///etc/lsb-release\'', default='file:///etc/lsb-release')
	optional.add_argument('-kt', dest='keep_tmp', action='store_true', help='do not delete unpacked and modified folders')
	optional.add_argument('-xu', dest='xxe_url', type=str, help='url to use in XXE payload')
	optional.add_argument('-pt', dest='payload_type', type=str, help='how many payloads will be in one file. per_document is default',choices=['per_place','per_file','per_document'],default='per_document')
	optional.add_argument('-pf', dest='payload_file',type=str, help='path to a file with payloads to embed',default='payloads/no_payload.txt')

	parser._action_groups.append(optional)
	
	args = parser.parse_args()	

	# Symbol that is used to determine a place where to place payload
	magic_symbol = '፨'

	path_to_complex_file = args.sample

	interface_print_logo()
	if args.sample:

		if os.path.exists(args.sample) and os.path.exists(args.payload_file):
			print('Document Embed XXS & XXE tool')
			
			payloads = payloads_read_file(args.payload_file)

			paths = document_prepare_initial_paths(path_to_complex_file)
			
			# Create tmp directory if it is not exists
			if not os.path.exists(paths["path_to_tmp"]):
				os.mkdir(paths["path_to_tmp"])

			print('\nCurrent setup')
			print('sample:\t\t\t',args.sample)
			print('payload file:\t\t',args.payload_file)
			print('payload mode:\t\t',args.payload_type)
			print('number of payloads:\t',len(payloads))
			print('keep upacked files:\t',args.keep_tmp)

			document_unpack(paths)
			tree = document_tree_generate(paths)
			tree_embedding, embedding_info = document_tree_embedding_points(paths, tree, magic_symbol)
			embedding_info['num_of_payloads'] = len(payloads)
			embedding_info['payload_type'] = args.payload_type

			#make_tmp_clean_again(paths,'original')
			interface_ask_user(embedding_info,paths)

			for single_payload_key in payloads.keys():

				print('\n%s'%single_payload_key, args.payload_type)

				if args.payload_type == 'per_document':
					
					docuemnt_prepare_future_paths(paths, args.payload_type, single_payload_key)
					document_tree_embedding_append_mod_paths(paths, tree_embedding)
					document_copy_dir(paths)

					# For 'per_document' we are looking only
					# for those documents that have embedded magic symbols
					# and we do not need to clear anything
					for single_file_key in tree_embedding:

						#print('\n',tree_embedding[single_file_key]['path_in_tmp'])

						with open(tree_embedding[single_file_key]['tmp_mod_path'],'w') as single_file:

							#print('\tembed',payloads[single_payload_key])
							single_file_mod = tree_embedding[single_file_key]['content'].replace(magic_symbol, payloads[single_payload_key])
							#print(single_file_mod)
							single_file.write(single_file_mod)
							single_file.close()

						
					document_pack(paths)

					print('\tpacked to: %s' % paths['path_to_packetd_file'])

					if not args.keep_tmp: 			
						make_tmp_clean_again(paths,'copy')

				elif args.payload_type == 'per_file':
	

					for single_file_key in tree_embedding:
	
						print('\t%s'%single_file_key)

						docuemnt_prepare_future_paths(paths, args.payload_type, single_payload_key, single_file_key)
						document_tree_embedding_append_mod_paths(paths, tree_embedding)						
						document_copy_dir(paths)

						#print('\n',tree_embedding[single_file_key]['path_in_tmp'])

						if args.payload_mode == 'xxs':

							with open(tree_embedding[single_file_key]['tmp_mod_path'],'w') as single_file:
								#print('\tembed',payloads[single_payload_key])
								single_file_mod = tree_embedding[single_file_key]['content'].replace(magic_symbol, payloads[single_payload_key])
								single_file.write(single_file_mod)
								single_file.close()

						elif args.payload_mode == 'xxe':
							with open(tree_embedding[single_file_key]['tmp_mod_path'],'w') as single_file:

								#single_file_mod = tree_embedding[single_file_key]['content'].replace(magic_symbol, payloads[single_payload_key])
								#xxe_current_refernce = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))

								xxe_current_payload_dict = json.loads(payloads[single_payload_key])
								#xxe_current_payload = payloads[single_payload_key].replace('xxe',xxe_current_refernce)
								print(xxe_current_payload_dict)
								single_file.close()
						#document_embed_payloads(payload_embed_file, args.payload_type)


						make_embedding_tree_clear_again(tree_embedding, single_file_key)
						document_pack(paths)
						
						print('\t\tpacked to: %s'%paths['path_to_packetd_file'])

						if not args.keep_tmp: 			
							make_tmp_clean_again(paths,'copy')

				elif args.payload_type == 'per_place':

					for single_file_key in tree_embedding:

						print('\t%s'%single_file_key)
					
						for offset_in_single_file in tree_embedding[single_file_key]['places']:

							docuemnt_prepare_future_paths(paths, args.payload_type, single_payload_key, single_file_key, offset_in_single_file)

							document_tree_embedding_append_mod_paths(paths, tree_embedding)

							document_copy_dir(paths)

							#print('\n',tree_embedding[single_file_key]['path_in_tmp'])

							with open(tree_embedding[single_file_key]['tmp_mod_path'],'w') as single_file:

								#print('\tembed',payloads[single_payload_key])

								single_file_mod = tree_embedding[single_file_key]['content'][:offset_in_single_file] 
								single_file_mod += payloads[single_payload_key] + tree_embedding[single_file_key]['content'][offset_in_single_file+1:] 
								
								# Clear other places in a file
								single_file_mod = single_file_mod.replace(magic_symbol,'')

								#print(single_file_mod)

								single_file.write(single_file_mod)
								single_file.close()

							make_embedding_tree_clear_again(tree_embedding, single_file_key)

							document_pack(paths)

							print('\t\tpacked to: %s'%paths['path_to_packetd_file'])
						
							if not args.keep_tmp: 			
								make_tmp_clean_again(paths,'copy')

					if not args.keep_tmp: 			
						make_tmp_clean_again(paths,'copy')

			make_tmp_clean_again(paths,'original')
					
		else:
			print("Error: One of specified files: '%s' or '%s' - does not exist"% (args.sample, args.payload_file))
	else:
		parser.print_help()