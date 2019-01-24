
```
_|_|_|                                                  
_|    _|    _|_|      _|_|_|    _|_|    _|_|_|  _|_|    
_|    _|  _|    _|  _|        _|_|_|_|  _|    _|    _|  
_|    _|  _|    _|  _|        _|        _|    _|    _|  
_|_|_|      _|_|      _|_|_|    _|_|_|  _|    _|    _|
```


Uility to embed XXE and XSS payloads in docx,odt,pptx,etc - any documents that is a zip archive with bunch of xml files inside

This tool is a side-project of a colloborative research with [ShikariSenpai](https://twitter.com/ShikariSenpai) and [ansjdnakjdnajkd](https://twitter.com/ansjdnakjdnajkd) of documents internal structure 


## Install 

```bash
pip3 install -r requirements.txt
```

## Usage Docem

General 

```
python3 docem.py --help
```

- required args
	- `-s` - path to a sample file
	- `-pm` - payload mode
		- `xss` - XSS - Cross Site Scripting 
		- `xxe` - XXE - External XML Entity 
- optional
	- `-pm` - payload type
		- `per_document` - (default mode) for every payload, embed payload in all places in all files and create new doc
		- `per_file` - for every payload, for every file inside a docuement, for all places inside file embed payload and create new doc
		- `per_place` - for every payload, for every place in every file, embed payload and create new doc
	- `-pf` - payload file. Path to a file with payloads
	- `-kt` - do not delete temp folders in tmp 
	- `-h` - print help

Example 
```bash
./docem.py -s samples/xss_sample_0.odt -pm xss -pf payloads/xss_tiny.txt -pm per_place
./docem.py -s samples/xxe/sample_oxml_xxe_mod1.docx -pm xxe -pf payloads/xxe_special_2.txt -kt -pt per_place
```


## File with payloads format

A small documentation to add your custom payloads

### XXE payloads

**Special format**

String from a file

`{"vector":"<!DOCTYPE docem [<!ENTITY xxe_canary_0 \"XXE_STRING\">]>","reference":"&xxe_canary_0;"}`

- `vector` - required key word - script will be searching for it 
- `<!DOCTYPE docem [<!ENTITY xxe_canary_0 \"XXE_STRING\">]>` - payload. Warning all double quotation marks `"` must be escaped with one backslash `\` => `\"`
- `reference` - required key word - script will be searching for it 
- `&xxe_canary_0;` - reference that will be add in all places with magic symbol 

### XSS payloads

No special format.
Just a file with strings. As if you would use it in any other tool.

## ToDo

- [x] Read file with payloads
- [ ] Add flag to specify custom url to use in XXE
- [ ] Add flag to specify custom url to use in XSS
- [ ] Add ability to embed not only in xml but in unzip file also

