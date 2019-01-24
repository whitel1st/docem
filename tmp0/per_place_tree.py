if args.payload_mode == 'xss':
	with open(tree_embedding[single_file_key]['tmp_mod_path'],'w') as single_file:

		single_file_mod = tree_embedding[single_file_key]['content'][:offset_in_single_file] 
		single_file_mod += payloads[single_payload_key] + tree_embedding[single_file_key]['content'][offset_in_single_file+1:] 
		
		# Clear other places in a file
		single_file_mod = single_file_mod.replace(magic_symbol,'')

		#print(single_file_mod)

		single_file.write(single_file_mod)
		single_file.close()

elif args.payload_mode == 'xxe':
	with open(tree_embedding[single_file_key]['tmp_mod_path'],'w') as single_file:

		# Loading one payload to dict from string
		xxe_current_payload_dict = json.loads(payloads[single_payload_key])

		# If there is a reference
		# then substitute one magic symbol with reference 
		if xxe_current_payload_dict['reference']:
			single_file_mod = tree_embedding[single_file_key]['content'][:offset_in_single_file] 
			single_file_mod += xxe_current_payload_dict['reference'] + tree_embedding[single_file_key]['content'][offset_in_single_file+1:] 

			# Clear other places in a file
			single_file_mod = single_file_mod.replace(magic_symbol,'')	

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