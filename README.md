# Search #

This project is a simple and fast command line tool that allows the user to Search for file names, file types, and text strings within the files. A real effort has been made to ensure that Search is as fast as possible, including making Search truly mulit-threaded. Currently Search will recursively trawl a 500GB SSD in about 15 seconds but we're always trying to make it faster.

## What Do I Need? ##
If you already have Python 3.5 (or higher) installed on your computer then you can just add `search.py` to PATH and use Search from the command line whenever you want. Otherwise, if you are a Windows user we have a compiled executable `search.exe` that you can download and add to your PATH environment variable and Search that way.

## How To Use Search ##
Search is based as a command line tool that accepts numerous arguments e.g. if you want to Search for HelloWord.txt.

`$ search.py -d=/home/andy -n=HelloWorld.txt`

Or if you want to Search for some text in every Python file on your computer, try this.

`$ search.py -e=.py -t="import numpy"`

Note that if you don't specify the directory then Search will start from `C:\` for Windows users or `/` for Linux users. 

Alternatively, if you're just curious about the number of lines of Python that you've written, Search can do that.

`$ search.py -d=/home/andy/my_project -e=.py -c`

If your Search is likely to yield a lot of results e.g. Searching for every text file on your computer, then you can output the results to a file like so.

`$ search.py -d=/home/andy -e=.txt -o=My_Text_Files.txt`

That's basically it for your day to day use, but there are a couple of other options that can also be useful.
* `-i` Indicates a case-insensitive Search, for either text Searches or file name Searches.
* `-h` Prints out the help message, showing all your options and what each of them does.
* `-v` Indicates a verbatim Search for file names. Ordinarily a file name Search will return any file with the Search term in it's name, e.g. a Search with `-n=hello` would match with files `hello_there`, `why_hello_there`, and `oh_hello_there`, while a verbatim Search will only match with a perfect name match.

## Things to do ##
* Implement text find and replace option.
* Implement a more equitable division of the workload than just what directories happen to be in the top branch.
* Add an optional parameter `files` to let the Pool processes work on the files in the top directory(s) instead of doing serial processing after the Pool processesors are killed.
