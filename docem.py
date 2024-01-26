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



"""
Class that contains the list of payloads
"""
class Payloads:
	payloads = []

	def _readfile(self, path_to_file: str) -> list:
		if os.path.exists(path_to_file):
			with open(path_to_file, 'r') as file:
				file_as_array = file.read().splitlines()
		else:
			raise Exception
		
		return(file_as_array)
		

	def __init__(self, path_to_file: str, ptype: str): 
		lines = self._readfile(path_to_file)
		for l in lines:
			if ptype == 'xxe':
				p = json.loads(l)
			elif ptype == 'xss':
				p = {'vector':l}  
			self.payloads.append(p)
"""
Class that contains the provided sample
which will be used for the injection
"""
class Sample:
	# Path to a main sample file or dir
	sample_path = ''
	is_sample_folder = None

	embed_files = []
	embed_count_places = 0

	def __init__(self, sample_path) -> None:
		self.sample_path = sample_path

		# Creates tmp in the current folder
		self.tmp_folder_path = f'{os.path.dirname(__file__)}/tmp/'
		self._create_tmp()

		self.is_sample_folder = os.path.isdir(self.sample_path)
		self.sample_file_name = ''

		if self.is_sample_folder:
			# If path was set as 'samples/xxe/sample_oxml_xxe_mod1/'
			if len(self.sample_path) - 1 == self.sample_path.rfind('/'):
				self.sample_path = self.sample_path[:-1]

			self.sample_file_name = self.sample_path.split('/')[-1]
			self.sample_file_ext = args.sample_extension
			
			self.copied_file_path = ''

		else:
			# Create separate variables for an original file
			self.sample_file_name = self.sample_path.split('/')[-1].split('.')[0]
			self.sample_file_ext = self.sample_path.split('/')[-1].split('.')[1]

			self.copied_file_path = f'{self.tmp_folder_path}{self.sample_file_name}.zip'

		# create variables for unzipped files
		# self.unzipped_file_name = f'{self.sample_file_name}_{self.sample_file_ext}'
		self.unzipped_folder_path = f'{self.tmp_folder_path}{self.sample_file_name}_{self.sample_file_ext}/'
		# self.copied_file_filename = f'{self.sample_file_name}_{self.sample_file_ext}'
		# self.copied_file_folder_path = f'{self.tmp_folder_path}{self.unzipped_file_name}/'



	# Creates tmp folder if it does not exist
	def _create_tmp(self) -> None:
		if not os.path.exists(self.tmp_folder_path):
			os.mkdir(self.tmp_folder_path)
	def _delete_tmp(self) -> None:
		if os.path.exists(self.tmp_folder_path):
			os.remove(self.tmp_folder_path)
# 	def print_setup()
# 			out = f"""
# sample path: {self.sample_path}
# sample is a dir: {self.is_sample_folder}

# """ 

	def unpack(self):
		# Sample is a file
		if self.is_sample_folder:
			shutil.copytree(
				src = self.sample_path,
				dst = self.unzipped_folder_path)
		# Sample is a folder
		else:
			shutil.copy(
				src = self.sample_path,
			    dst = self.copied_file_path)
			shutil.unpack_archive(
				filename = self.copied_file_path, 
				extract_dir = self.unzipped_folder_path)
					

	def generate_document_tree(self, paths):
		for root, dirs, files in os.walk(
			self.unzipped_folder_path, topdown = False):

			for filename in files:
				file_path = os.path.join(root, filename)
				file_path_tmp = file_path.replace(self.unzipped_folder_path,'')

			path_to_file = os.path.join(root, full_name)
			path_in_tmp = path_to_file.replace()
	
	"""
	Finds all places where payloads will be embedded.
	Saves them in a class variable.
	Variable is a list of dicts that contain 
		path - path to a file
		places - indexes in a file where to embed
		counts - total number of 
	payload will be embedded
	"""
	def find_embedding_points(self) -> None:
		for root, dirs, files in os.walk(
			self.unzipped_folder_path, topdown = False):		
			for file in files:
				if file.endswith(('.xml','.txt','.rels','.vml')): 
					file_fullpath = f'{root}/{file}'
					with open(file_fullpath, 'r') as f:
						file_in_sample = f.read()

						if file_in_sample.count(magic_symbol):
							to_embed = {
								'filepath' : file_fullpath,
								'places' : [i for i in range(len(file_in_sample)) if file_in_sample.startswith(magic_symbol, i)],
								# 'content' : file_in_sample
								}
							self.embed_files.append(to_embed)
							self.embed_count_places += len(to_embed['places'])
							print(f'{len(to_embed["places"])} symbols in {to_embed["filepath"]}')

	def _verify_docs_creation(self, pmod, payloads):
		print(f'{len(self.embed_files)} total files to embed (used as modifier with -pt per_file')
		print(f'{self.embed_count_places} total places to embed (used as modifier with -pt per_place)')

		modifier = 0
		if pmod == 'per_document':
			modifier = 1
		elif pmod == 'per_file':
			modifier = len(self.embed_files)
		elif pmod == 'per_place':
			modifier = len(len(self.embed_count_places))

		num_of_files= len(payloads) * modifier

		print(f'number_of_payloads * modifier = {len(payloads)} * {modifier} = {num_of_files}')
		print('modifier depends on payload_type (-pt)')
		print(f'Files to be created {num_of_files}')

		# To be sure that you want to create that amount of documents
		answer = input('Continue?(y/n): ')
		
		if answer == 'n':
			self._delete_tmp()
			exit()


	def _inject_header(self, ptype:str, payload, file_content) -> str:
		if ptype == 'xxe':
			# Ending with finding where to place 
			# payload with <DOCTYPE>
			offset_xml_start = int(file_content.find('<?xml'))
			offset_xml_closed_bracket = file_content.find('>',offset_xml_start) + 1 
			file_content = file_content[:offset_xml_start] +  payload['vector'] + file_content[offset_xml_start:] 
			# single_file_mod = single_file_mod[:offset_xml_closed_bracket] + payload['vector'] + single_file_mod[offset_xml_place_closed_bracket:]

		else:
			pass

		return file_content


	def _pack_file(self):

		# postfix = f'{ptype}-{single_place}'
		# if ptype == 'per_place':
		# 	postfix = f'{ptype}-{single_place}-{payload_key}-{offset}' 

		# elif ptype == 'per_file':
		# 	postfix = f'{ptype}-{single_place}-{payload_key}' 

		# elif ptype == 'per_document':
		# 	postfix = f'{ptype}-{single_place}' 


		# postfix += '_' + str(time.time()).replace('.','') 

		# paths['modified_file_name'] = paths['original_file_name'] + '-' + postfix 
		# paths['path_to_unzipped_folder_modified'] = paths['path_to_tmp'] + paths['modified_file_name'] + '/'
		# paths['path_to_modified_file'] = paths['path_to_tmp'] + paths['modified_file_name'] + '.zip'
		# paths['path_to_packetd_file'] = paths['path_to_tmp'] +  paths['modified_file_name'] + '.' +  paths['original_file_ext']

		shutil.make_archive(
			base_name = self.modified_file_name,
			root_dir = self.unzipped_folder_path,
			format='zip'
		)
		# Split - because shutil will add .zip anyway
		#print(paths['path_to_unzipped_folder_modified'])
		shutil.make_archive(
			base_name=paths['path_to_modified_file'].split('.')[0],
					  root_dir=paths['path_to_unzipped_folder_modified'],
					  format='zip')

		# shutil.copy(paths['path_to_modified_file'], paths['path_to_packetd_file'])

		# For debug
		#print('\n%s'%paths['path_to_modified_file'])
		#print(paths['path_to_packetd_file'])

		# # copy & rename zip to odt
		# shutil.copy(paths['path_to_modified_file'], paths['path_to_packetd_file'])


	def _inject_clear_places(self, file):
		a = 0
	"""
	Injects single payload to all places from embed_tree
	pm - payload mode
	pt - payload type
	"""
	def inject_payload(self, payload: dict, pmode: str, ptype: str) -> None:
		if pmode == 'per_document':
			# Replace all magic symbols in all files
			# where there were found
			# and pack the result
			for embed_f in self.embed_files:
				with open(embed_f['file'], 'w') as file_to_inj:
					file_to_inj_content = file_to_inj.read()
					file_to_inj_content.replace(magic_symbol, payload)
					file_to_inj_content = self._inject_header(ptype, payload, file_to_inj_content)
					file_to_inj.write(file_to_inj_content)

			# TODO: clear other places in a file
			self._pack_file()
		elif pmode == 'per_file':
			# Replace all magic symbols in each file
			# where there were found
			# and pack individual results with substitued files
			for embed_f in self.embed_files:
				with open(embed_f['file'], 'w') as file_to_inj:
					file_to_inj_content =  file_to_inj.read()
					file_to_inj_content.replace(magic_symbol, payload)
					file_to_inj_content = self._inject_header(ptype, payload, file_to_inj_content)
					file_to_inj.write(file_to_inj_content)

				# TODO: clear other places in a file
				#_pack_file()
		elif pmode == 'per_place':
			# Replace each magic symbol in each file
			# where there were found
			# and pack individual result with substitued index
			for embed_f in self.embed_files:
				for embed_index in embed_f['places']:
					with open(embed_f['file'], 'w') as file_to_inj:
						file_to_inj_content = file_to_inj.read()
						file_to_inj_content = file_to_inj_content[place] + magic_symbol + file_to_inj_content[place + 1]
						file_to_inj_content = self._inject_header(ptype, payload, file_to_inj_content)
						file_to_inj.write(file_to_inj_content)
					# TODO: clear other places in a file
					#_pack file


class Interface:
	def print_logo(self):
		logo = '''

_|_|_|                                                  
_|    _|    _|_|      _|_|_|    _|_|    _|_|_|  _|_|    
_|    _|  _|    _|  _|        _|_|_|_|  _|    _|    _|  
_|    _|  _|    _|  _|        _|        _|    _|    _|  
_|_|_|      _|_|      _|_|_|    _|_|_|  _|    _|    _|  
                                                                                                        
	'''
		version = '1.4'
		print(logo)
		print('Current version: %s\n'%version)

	def print_examples(self):
		examples = 	[
			'./docem.py -s samples/xxe/docx_sample_oxml_xxe_mod0/ -pt xxe -pf payloads/xxe_special_6.txt -pm per_document -kt -sx docx',
			'./docem.py -s samples/xxe/docx_sample_oxml_xxe_mod1/ -pt xxe -pf payloads/xxe_special_1.txt -pm per_file -kt -sx docx',
			'./docem.py -s samples/xxe/sample_oxml_xxe_mod1.docx -pt xxe -pf payloads/xxe_special_2.txt -kt -pm per_place',
			'./docem.py -s samples/xss_sample_0.odt -pt xss -pf payloads/xss_tiny.txt -pm per_place'
		]
		
		print('Examples:\n%s\n' % '\n'.join(e for e in examples))
		

if __name__ == '__main__':
	interface = Interface()
	interface.print_logo()
	interface.print_examples()

	parser = argparse.ArgumentParser(
		description='Create docx, odt, pptx files with XXE/XSS payloads')
	
	optional = parser._action_groups.pop()
	required = parser.add_argument_group('required arguments')
	
	required.add_argument('-s', 
							dest='sample', 
							type=str, 
							help='path to sample file')
	required.add_argument('-pt', 
							dest='payload_type',
							type=str,choices=['xss','xxe'],
							help='payload type: embedding XXE or XSS in a file')
	optional.add_argument('-kt',
							dest='keep_tmp',
							action='store_true',
							help='do not delete unpacked and modified folders')
	optional.add_argument('-pm',
							dest='payload_mode',
							type=str,
							help='how many payloads will be in one file. per_document is default', 
							choices=['per_place','per_file','per_document'],
							default='per_document')
	optional.add_argument('-sx', 
						dest='sample_extension', 
						type=str, help='d ')
	optional.add_argument('-pf', 
						dest='payload_file',
						type=str, help='path to a file with payloads to embed',
						default='payloads/no_payload.txt')

	parser._action_groups.append(optional)
	args = parser.parse_args()	

	# Symbol that is used to determine a place where to place payload
	magic_symbol = 'XXCb8bBA9XX'
	
	if args.sample:
		if os.path.exists(args.sample) and os.path.exists(args.payload_file):
			print('Document Embed XSS & XXE tool')
			print('\nCurrent magic_symbol: ',magic_symbol)

			p = Payloads(
				path_to_file = args.payload_file,
				ptype = args.payload_type)
			s = Sample(args.sample)

			print('\n=========== Current setup ===========')
			print('sample file path:\t\t', s.sample_path)
			print('sample is a directory:\t', s.is_sample_folder)
			print('payload mode:\t\t', args.payload_mode)
			print('payload file:\t\t', args.payload_file)
			print('payload type:\t\t', args.payload_type)
			print('number of payloads:\t', len(p.payloads))
			print('keep unpacked files:\t', args.keep_tmp)

			s.unpack()
			s.find_embedding_points()
			s._verify_docs_creation(args.payload_mode, p.payloads)
			s.inject_payload()
			s._delete_tmp()
					
		else:
			print("Error: One of specified files: '%s' or '%s' - does not exist"% (args.sample, args.payload_file))
	else:
		parser.print_help()