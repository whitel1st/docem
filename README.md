
```
_|_|_|                                                  
_|    _|    _|_|      _|_|_|    _|_|    _|_|_|  _|_|    
_|    _|  _|    _|  _|        _|_|_|_|  _|    _|    _|  
_|    _|  _|    _|  _|        _|        _|    _|    _|  
_|_|_|      _|_|      _|_|_|    _|_|_|  _|    _|    _|

version 1.3
```


A utility to embed XXE and XSS payloads in docx, odt, pptx, etc - any documents that is a zip archive with bunch of xml files inside.

This tool is a side-project of a colloborative research of document's internal structure with [ShikariSenpai](https://twitter.com/ShikariSenpai) and [ansjdnakjdnajkd](https://twitter.com/ansjdnakjdnajkd) 


## What it is all about

A lot of common document formats, such as doc,docx,odt,etc are just a zip files with a few xml files inside.

![diag0](https://github.com/whitel1st/docem/blob/master/pics/diag0.png "diag0")

So why don't we try to embed XXE payloads in them?  
That was done in a great [research](http://oxmlxxe.github.io/reveal.js/slides.html#/) by Will Vandevanter (`_will_is`)
To create such documents with embedded payloads there is a famous tool called [oxml_xxe](https://github.com/BuffaloWill/oxml_xxe). 

But. It is not convenient to use `oxml_xxe` when you need to create hundreds of documents with payloads in different places.
So there it goes - Docem.

It works like that: You specify sample document - that is a doc that contains `magic_symbols` (in illustrations it is marked as `፨` (in program it is constant `XXCb8bBA9XX`)) that will be replaced by a XXE or XSS payload.

Also there are three different types of `payload_type` - every type determines how every `magic_symbol` will be processed for a given file in a document.
Every `payload_type` described in a section `Usage`.
Here is a small scheme of how this works:

![diag1](https://github.com/whitel1st/docem/blob/master/pics/diag1.png "diag1")

Payload modes

![diag2](https://github.com/whitel1st/docem/blob/master/pics/diag2.png "diag1")

Programm interface

![screenshot](https://github.com/whitel1st/docem/blob/master/pics/screenshot.png "screenshot")


## Install 

```bash
pip3 install -r requirements.txt
```

## Usage Docem

```
python3 docem.py --help
```


- required args
	- `-s` - path to a `sample file` or a `sample directory`. That sample will be used to create a document with an attacking vector.
	- `-pm` - payload mode
		- `xss` - XSS - Cross Site Scripting 
		- `xxe` - XXE - External XML Entity 
- optional
	- `-pt` - payload type
		- `per_document` - (default mode) for every payload, embed payload in all places in all files and create new document
		- `per_file` - for every payload, for every file inside a document, for all places inside a file embed a payload and create a new document
		- `per_place` - for every payload, for every place in every file, embed a payload and create a new doc
	- `-pf` - payload file
	- `-kt` - do not delete temp folders in a `tmp/` 
	- `-sx ` - sample extension - used when sample is a directory
	- `-h` - print help

Examples 
```bash
./docem.py -s samples/xxe/docx_sample_oxml_xxe_mod0/ -pm xss -pf payloads/xxe_special_6.txt -pt per_document -kt -sx docx
./docem.py -s samples/xxe/docx_sample_oxml_xxe_mod1/ -pm xss -pf payloads/xxe_special_1.txt -pt per_file -kt -sx docx
./docem.py -s samples/xxe/sample_oxml_xxe_mod1.docx -pm xxe -pf payloads/xxe_special_2.txt -kt -pt per_place
./docem.py -s samples/xss_sample_0.odt -pm xss -pf payloads/xss_tiny.txt -pm per_place
```

An equivalent to a `docx` file created by oxml_xxe 
```
./docem.py -s samples/xxe/docx_sample_oxml_xxe_mod0/ -pm xss -pf payloads/xxe_special_6.txt -pt per_document -kt -sx docx
```


## How to create custom sample


### Via new folder sample


1. Unzip your document `example.docx` to a folder `example/`
2. Add magic symbols - `XXCb8bBA9XX` (depicted as `፨` in illustrations of this readme) in places where you want payloads to be embedded
3. Use new sample with the tool as `-s samples/example/ -sx docx`


### Via new file sample

1. Unzip your document `example.docx` to a folder `example/`
2. Add magic symbols - `XXCb8bBA9XX` - (depicted as `፨` in illustrations of this readme) in places where you want payloads to be embedded
3. Zip your new sample into `example_modified0.zip`
4. Rename extension - `example_modified0.docx`
5. Use new sample with the tool as `-s samples/example_modified0.docx`


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

## Features and ToDo

- Features
	- [x] Read file with payloads
		- [x] XXE custom payload file
		- [x] XSS payload file
- ToDo
	- [x] Add ability to embed not only in xml but in unzip file also
	- [ ] Add flag to specify custom url to use in XXE
	- [ ] Add flag to specify custom url to use in XSS

