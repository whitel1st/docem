
```
_|_|_|                                                  
_|    _|    _|_|      _|_|_|    _|_|    _|_|_|  _|_|    
_|    _|  _|    _|  _|        _|_|_|_|  _|    _|    _|  
_|    _|  _|    _|  _|        _|        _|    _|    _|  
_|_|_|      _|_|      _|_|_|    _|_|_|  _|    _|    _|
```


Uility to embed XXE and XSS payloads in docx,odt,pptx,etc - any documents that is a zip archive with bunch of xml files inside

This tool is a side-project of a colloborative research of document's internal structure with [ShikariSenpai](https://twitter.com/ShikariSenpai) and [ansjdnakjdnajkd](https://twitter.com/ansjdnakjdnajkd) 


## What it is all about

A lot of common document formats, such as doc,docx,odt,etc is just a zip file with a few xml files inside 

![diag0](https://github.com/whitel1st/docem/blob/master/pics/diag0.png "diag0")

So why not embed XXE payloads in them?  
That was done by a great [research](http://oxmlxxe.github.io/reveal.js/slides.html#/) by Will Vandevanter (`_will_is`)
To create such documents with embedded payloads there is a famous tool called [oxml_xxe](https://github.com/BuffaloWill/oxml_xxe). 

But. It is not convinient to use `oxml_xxe` when you need to create hundreds of documents with payloads in different places.
So there it goes - Docem.

It works like that: You specify sample document - that is a doc that has some `magic_symbols` (in this case it is `፨`)  that will be replaced by your refernce to a payload in case of XXE payload, or will be replaces by your XSS payload.

Also there are three different types of `payload_type` - every type determine how every `magic_symbol` will be processed for a given file in a document.
Every `payload_type` described in section `Usage`.
Here is a small scheme of how this works:

![diag1](https://github.com/whitel1st/docem/blob/master/pics/diag1.png "diag1")

Payload modes

![diag2](https://github.com/whitel1st/docem/blob/master/pics/diag1.png "diag1")

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
	- `-s` - path to a `sample file` or a `sample directory`
	- `-pm` - payload mode
		- `xss` - XSS - Cross Site Scripting 
		- `xxe` - XXE - External XML Entity 
- optional
	- `-pt` - payload type
		- `per_document` - (default mode) for every payload, embed payload in all places in all files and create new doc
		- `per_file` - for every payload, for every file inside a docuement, for all places inside file embed payload and create new doc
		- `per_place` - for every payload, for every place in every file, embed payload and create new doc
	- `-pf` - payoload file
	- `-kt` - do not delete temp folders in tmp 
	- `-sx ` - sample extension - used when sample is a directory
	- `-h` - print help

Examples 
```bash
./docem.py -s samples/xxe/sample_oxml_xxe_mod0/ -pm xss -pf payloads/xss_all.txt -pt per_document -kt -sx docx
./docem.py -s samples/xxe/sample_oxml_xxe_mod1.docx -pm xxe -pf payloads/xxe_special_2.txt -kt -pt per_place
./docem.py -s samples/xss_sample_0.odt -pm xss -pf payloads/xss_tiny.txt -pm per_place
./docem.py -s samples/xxe/sample_oxml_xxe_mod0/ -pm xss -pf payloads/xss_all.txt -pt per_file -kt -sx docx
```


## How to create custom sample

### Via new file

1. Extract your document `example.docx`
2. Add magic symbols - `፨` (yes, literally - those fancy 5 dots) in places where you want payloads to be embed
3. Zip your new sample into `example_modified0.zip`
4. Rename extension - `example_modified0.docx`
5. Use new sample with tool

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
	- [ ] Add flag to specify custom url to use in XXE
	- [ ] Add flag to specify custom url to use in XSS
	- [ ] Add ability to embed not only in xml but in unzip file also

