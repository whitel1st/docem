						if args.payload_mode == 'xss':
							with open(tree_embedding[single_file_key]['tmp_mod_path'],'w') as single_file:

								single_file_mod = tree_embedding[single_file_key]['content'].replace(magic_symbol, payloads[single_payload_key])
								single_file.write(single_file_mod)
								single_file.close()

						elif args.payload_mode == 'xxe':
							with open(tree_embedding[single_file_key]['tmp_mod_path'],'w') as single_file:
							
								# Loading one payload to dict from string
								xxe_current_payload_dict = json.loads(payloads[single_payload_key])

								# If there is a reference
								# then substitute all magic symblos with references 
								if xxe_current_payload_dict['reference']:
									single_file_mod = tree_embedding[single_file_key]['content'].replace(magic_symbol, xxe_current_payload_dict['reference'])

								# If there is no reference
								# then delete all magic symblos
								else:
									single_file_mod = tree_embedding[single_file_key]['content'].replace(magic_symbol,'')

								# Ending with finding where to place 
								# payload with <DOCTYPE and stuf>
								offset_xml_start = int(tree_embedding[single_file_key]['content'].find('<?xml'))
								# find where the tag closes
								offset_xml_place_closed_bracket = tree_embedding[single_file_key]['content'].find('>',offset_xml_start) + 1 

								single_file_mod = single_file_mod[:offset_xml_place_closed_bracket] + xxe_current_payload_dict['vector'] + single_file_mod[offset_xml_place_closed_bracket:]

								single_file.write(single_file_mod)
								single_file.close()