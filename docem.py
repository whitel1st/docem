#!/usr/bin/python3

import os  
import shutil
import json
import uuid
import argparse
import json
import copy
import re


"""
Class that contains the list of payloads
"""
class Payloads:
	list = []

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
				try:
					p = json.loads(l)
				except Exception as e:
					print(f'\n! Error: {e}')
					print(f'\nLooks like payload file is not properly formatted')
					print(f'Please check that you are using apropriate payload_type with appropriate payload format:\n\t-pt xss means that list of payloads is just a list;\n\t-pt xxe means that payload file is a list of dictionaries;\n')
					raise
			elif ptype == 'xss':
				p = {'reference':l}  
			self.list.append(p)

"""
Class that contains the provided sample
which will be used for the injection
"""
class Sample:
	# Path to a main sample file or dir
	sample_path = ''
	is_sample_folder = None


	# embed_files - a dictionary that stores a list
	# of files that contain magic_symbols
	# key - path to a file
	# value - array of indices where magic_symbols are present
	# embed_files = {
	# 	'app.xml':[1,32,423],
	# 	'core/file.xml':[32,423],
	# 	'ref/new/test.xml':[5],
	# }
	# To Do change it to a struct
	embed_files = {}
	embed_count_places = 0

	"""
	Mostly prepares a bunch of paths
	that will be used throughout the programm
	"""
	def __init__(self, sample_path: str) -> None:
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
		self.unzipped_folder_path = f'{self.tmp_folder_path}{self.sample_file_name}_{self.sample_file_ext}/'
		


	# Creates tmp folder if it does not exist
	def _create_tmp(self) -> None:
		if not os.path.exists(self.tmp_folder_path):
			os.mkdir(self.tmp_folder_path)

	def _delete_folder(self, folder_path: str, keep_folder: bool = False) -> None:
		if os.path.exists(folder_path):
			shutil.rmtree(folder_path)

			if keep_folder:
				os.mkdir(folder_path)



	"""
	Copy sample file/folder to the tmp location
	If a sample is a file - zip extract
	"""
	def unpack(self):
		# Sample is a folder
		if self.is_sample_folder:
			self._copy_folder(
				src = self.sample_path,
				dst = self.unzipped_folder_path
			)
		# Sample is a file
		else:
			self._copy_file(
				src = self.sample_path,
			    dst = self.copied_file_path
			)
			shutil.unpack_archive(
				filename = self.copied_file_path, 
				extract_dir = self.unzipped_folder_path)
		
	"""
	Copy file from src to dst
	"""
	def _copy_file(self, src: str, dst: str) -> None:
		shutil.copy(src = src, dst = dst)
		
	"""
	Copy file from src to dst
	"""
	def _copy_folder(self, src: str, dst:str) -> None:
		shutil.copytree(src = src, dst = dst)				
	
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
		print('Searching for magic_symbols in a sampled file/dir')
		for root, dirs, files in os.walk(
			self.unzipped_folder_path, topdown = False):		
			for file in files:
				if file.endswith(magic_file_extensions): 
					file_fullpath = f'{root}/{file}'
					with open(file_fullpath, 'r') as f:
						file_in_sample = f.read()

						if file_in_sample.count(magic_symbol):
							# to_embed = {
							# 	'filepath' : file_fullpath,
							# 	'places' : [i for i in range(len(file_in_sample)) if file_in_sample.startswith(magic_symbol, i)],
							# 	# 'content' : file_in_sample
							# 	}
							# Add a file and a list of indices with magic symbols to the list
							places = [i for i in range(len(file_in_sample)) if file_in_sample.startswith(magic_symbol, i)]
							file_path = file_fullpath.replace(self.unzipped_folder_path,'')
							self.embed_files[file_path] = places
							
							self.embed_count_places += len(places)
							print(f'{len(places)} symbols in {file_path}')
		print()

	"""
	Print a message to a user about a number
	of files that would be created
	"""
	def ask_to_confirm_docs_creation(self, pmod, payloads):
		print(f'{len(self.embed_files)} potential files to embed')
		print(f'{self.embed_count_places} potential places to embed (as a sum of number of symbols)')

		modifier = 0
		if pmod == 'per_document':
			modifier = 1
		elif pmod == 'per_file':
			modifier = len(self.embed_files)
		elif pmod == 'per_place':
			modifier = self.embed_count_places

		num_of_files= len(payloads) * modifier

		print(f'modifier = {modifier}. Based on selected -pm {pmod}')
		print(f'\nFiles to be created = number_of_payloads * modifier = {len(payloads)} * {modifier} = {num_of_files}')

		# For debug
		# To be sure that you want to create that amount of documents
		answer = input('\nContinue?(y/n): ')
		if answer == 'n':
			self._delete_folder(self.tmp_folder_path)
			exit()


	"""
	Inject payload header for XXE payloads
	for XSS payloads - do nothing
	"""
	def _inject_header(self, ptype:str, payload: dict, file_content: str) -> str:
		if ptype == 'xxe':
			# Ending with finding where to place  
			# payload with <DOCTYPE>
			
			offset_xml_start = file_content.find('<?xml')
			if offset_xml_start != -1:
				file_content = file_content[:offset_xml_start] +  payload['vector'] + file_content[offset_xml_start:]

		else:
			pass

		return file_content

	"""
	Archive the specified folder (full path)
	to the speecified file (full path)
	"""
	def _archive_folder(self, src_folder_path: str, dst_archive_path: str) -> None:
		# Shutil adds .zip 
		# To avoid .zip.zip we strip it
		if dst_archive_path.endswith('.zip'):
			index = dst_archive_path.rfind('.zip')
			dst_archive_path = dst_archive_path[:index]

		shutil.make_archive(
			base_name = dst_archive_path,
			root_dir = src_folder_path,
			format='zip'
		)


		
	def _rename_object(self, src: str, dst: str) -> None:
		os.rename(src=src, dst=dst)
		

	"""
	Prepare paths for a new file that
	will have specif injection
	pmode: payload_mode
	ptype: payload_type
	pfile: payload file - used for pmode = per_file
	pplace: payload file - used for pmode = per_file / per_place
	"""
	def __prepare_paths_for_injected_file(self, suffix_run:str,  pmode:str, ptype:str, pfile: str = '', pplace: int = None) -> None:
		if pfile or pplace:
			pfile = pfile[pfile.rfind('/') + 1:].replace('.','_')
			pfile = re.sub('[\[\]]','',pfile)
			if pplace:
				final_file_name_core = f'{self.sample_file_name}-{pmode}_{ptype}_{suffix_run}_{pfile}_{pplace}'
			else:
				final_file_name_core = f'{self.sample_file_name}-{pmode}_{ptype}_{suffix_run}_{pfile}'
		else:
			final_file_name_core = f'{self.sample_file_name}-{pmode}_{ptype}_{suffix_run}'
		

		self.final_file_folder = f'{self.tmp_folder_path}{final_file_name_core}/'
		self.final_file_packed_zip = f'{self.tmp_folder_path}{final_file_name_core}.zip'
		self.final_file_packed_ext = f'{self.tmp_folder_path}{final_file_name_core}.{self.sample_file_ext}'

	"""
	Create new folder for specific injection
	"""
	def _copy_before_injection(self):
		self._copy_folder(
			src = self.unzipped_folder_path, 
			dst = self.final_file_folder)

	"""
	Archive and rename previously created
	new folder for specific injection
	"""
	def _pack_after_injection(self):
		self._archive_folder(
			src_folder_path = self.final_file_folder,
			dst_archive_path = self.final_file_packed_zip
		)
		self._rename_object(
			src = self.final_file_packed_zip,
			dst = self.final_file_packed_ext
		)

		self._delete_folder(self.final_file_folder)

		print(f'File with payload created: {self.final_file_packed_ext.replace(self.tmp_folder_path,"tmp/")}')


	"""
	For the specified directory remove magic_symbols
	from all of the nested files
	"""
	def _remove_magic_symbols(self, base_folder:str, list_of_relative_paths: dict) -> None:
		for file in list_of_relative_paths:
			file_fp = base_folder + file
			with open(file_fp, 'r') as f:
				file_content = f.read()	
				file_content= file_content.replace(magic_symbol, '')
			with open(file_fp, 'w') as f:
				f.write(file_content)
	
	def _convert_tmp_folder_path_to_specific_payload_path(self, path: str) -> str:
		return(path.replace(self.unzipped_folder_path, self.final_file_folder))
		
	def __test_unzip_and_verify(self, path):
		
		pass

	"""
	Injects single payload to all places from embed_tree
	pm - payload mode
	pt - payload type
	"""
	def inject_payload(self, payload: dict, pmode: str, ptype: str) -> None:
		suffix_run = uuid.uuid4().hex[:5]

		if pmode == 'per_document':
			# Replace all magic symbols in all files
			# where there were found
			# and pack the result
			self.__prepare_paths_for_injected_file(suffix_run=suffix_run, pmode=pmode, ptype=ptype)
			self._copy_before_injection()

			for embed_f_path in self.embed_files:
				embed_f_path = self.final_file_folder + embed_f_path
				with open(embed_f_path, 'r') as file_to_inj:
					file_to_inj_content = file_to_inj.read()
					file_to_inj_content = file_to_inj_content.replace(magic_symbol, payload['reference'])
					file_to_inj_content = self._inject_header(ptype, payload, file_to_inj_content)
				with open(embed_f_path, 'w') as file_to_inj:
					file_to_inj.write(file_to_inj_content)
			self._pack_after_injection()

		elif pmode == 'per_file':
			# Replace all magic symbols in each file
			# where there were found
			# and pack individual results with substitued files
			for embed_f_path in self.embed_files:
				self.__prepare_paths_for_injected_file(suffix_run=suffix_run, pmode=pmode, ptype=ptype, pfile=embed_f_path)
				self._copy_before_injection()

				embed_f_fp = self.final_file_folder + embed_f_path
				with open(embed_f_fp, 'r') as file_to_inj:
					file_to_inj_content =  file_to_inj.read()
					file_to_inj_content = file_to_inj_content.replace(magic_symbol, payload['reference'])
					file_to_inj_content = self._inject_header(ptype, payload, file_to_inj_content)
				with open(embed_f_fp, 'w') as file_to_inj:
					file_to_inj.write(file_to_inj_content)
				
				files_with_magic_symbols_to_remove = copy.deepcopy(self.embed_files)
				files_with_magic_symbols_to_remove.pop(embed_f_path)
				self._remove_magic_symbols(
					base_folder = self.final_file_folder,
					list_of_relative_paths = files_with_magic_symbols_to_remove)

				self._pack_after_injection()
				
		elif pmode == 'per_place':
			# Replace each magic symbol in each file
			# where there were found
			# and pack individual result with substitued index
			for embed_f_path, embed_f_indices in self.embed_files.items():
				for index in embed_f_indices:

					self.__prepare_paths_for_injected_file(suffix_run=suffix_run, pmode=pmode, ptype=ptype, pfile=embed_f_path, pplace=index)
					self._copy_before_injection()
					embed_f_fp = self.final_file_folder + embed_f_path

					with open(embed_f_fp, 'r') as file_to_inj:
						file_to_inj_content = file_to_inj.read()
						file_to_inj_content = file_to_inj_content[:index] + payload['reference'] + file_to_inj_content[index + len(magic_symbol):]
						file_to_inj_content = file_to_inj_content.replace(magic_symbol,'')
						file_to_inj_content = self._inject_header(ptype, payload, file_to_inj_content)
					with open(embed_f_fp, 'w') as file_to_inj:
						file_to_inj.write(file_to_inj_content)
					
					# We don't do deep copy here, because the current file
					# still contains other occurences of magic_symbol
					self._remove_magic_symbols(
						base_folder = self.final_file_folder,
						list_of_relative_paths = self.embed_files)
				
					self._pack_after_injection()
						

class Interface:
	def print_logo(self):
		logo = '''

_|_|_|                                                  
_|    _|    _|_|      _|_|_|    _|_|    _|_|_|  _|_|    
_|    _|  _|    _|  _|        _|_|_|_|  _|    _|    _|  
_|    _|  _|    _|  _|        _|        _|    _|    _|  
_|_|_|      _|_|      _|_|_|    _|_|_|  _|    _|    _|  
                                                                                                        
	'''
		version = '1.5'
		print(logo)
		print('Current version: %s\n'%version)

	def print_examples(self):
		examples = 	[
			'./docem.py -s samples/marked/docx_sample_oxml_xxe_mod0/ -pt xxe -pf payloads/xxe_special_6.txt -pm per_document -sx docx',
			'./docem.py -s samples/marked/docx_sample_oxml_xxe_mod1/ -pt xxe -pf payloads/xxe_special_1.txt -pm per_file -sx docx',
			'./docem.py -s samples/marked/sample_oxml_xxe_mod1.docx -pt xxe -pf payloads/xxe_special_2.txt -pm per_place',
			'./docem.py -s samples/marked/docx_sample_oxml_xxe_mod0/ -pt xss -pf payloads/xss_tiny.txt -pm per_place -sx docx'
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
	magic_file_extensions = ('.xml','.txt','.rels','.vml')
	
	if args.sample:
		if not os.path.exists(args.sample):		
			print(f'Error: Sample file does not exist: {args.sample}')
		elif not os.path.exists(args.payload_file):
			print(f'Error: Payload file does not exist: {args.payload_file}')
		else:
			print(f'Document Embed XSS & XXE tool')
			print(f'Current magic_symbol: {magic_symbol}')

			p = Payloads(
				path_to_file = args.payload_file,
				ptype = args.payload_type)
			s = Sample(args.sample)

			# only for debug
			# s._delete_folder(s.tmp_folder_path, keep_folder=True)

			print('\n=========== Current setup ===========')
			print('sample file path:\t', s.sample_path)
			print('sample is a directory:\t', s.is_sample_folder)
			print('payload mode:\t\t', args.payload_mode)
			print('payload file:\t\t', args.payload_file)
			print('payload type:\t\t', args.payload_type)
			print('number of payloads:\t', len(p.list))
			print()

			s.unpack()
			s.find_embedding_points()
			s.ask_to_confirm_docs_creation(args.payload_mode, p.list)
			for payload in p.list: 
				s.inject_payload(
					payload = payload,
					pmode = args.payload_mode,
					ptype = args.payload_type
				)

			s._delete_folder(s.unzipped_folder_path)
			if not s.is_sample_folder:
				os.remove(s.copied_file_path)
				
					
	else:
		parser.print_help()