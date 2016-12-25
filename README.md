# orgFixLinks.py, a Python Command-Line Utility

**WARNING** many users will not want a header added to their org files.  The
script can/will be modified to accomodate this, but at this time adds headers to
all org files.

Be sure to check out
the [wiki](https://github.com/cashTangoTangoCash/orgFixLinks/wiki).  There is a
cookbook section.  Also check out orgFixLinksHighlights.mm, which is readable
using Freeplane.

This is a script aspriring to be in this category: <http://orgmode.org/worg/org-tools/>

I wrote over *800 org files*, which reside on my local disk.  They consist of
simple notes with links to websites and other files on local disk.  **_Broken
links_** would naturally occur as I made changes to files on local disk.  Files
for some of my favorite subjects would gradually become full of broken links,
leaving me unable to make more notes.  I could not find a solution online.  I am
an **amateur** who has been spending some time learning python, but still has a
lot to learn, and this project seemed like the next thing to try.

*I have read almost zero org mode documentation*.  I use org mode to keep simple
notes, and am mostly interested in quickly looking up information in my
collection of org files.  When links are broken, my org files greatly diminish
in usefulness.


The goals of this script:

1.  repair links (inside an org file) to files on local disk

2.  add a [header](header.md) to an org file; this header is a list of incoming links, outgoing
    links, and tags


The script is a command line utility to be used in the terminal.  Currently it
is known to run in the Ubuntu OS only.

## Warnings and State of Development
**WARNING** this python script is amateur work

**WARNING** many users will not want a header added to their org files.  The
script can/will be modified to accomodate this.

**WARNING** bugs are still regularly appearing.  Comprehensively testing this
code is not easy; there is now a test script: orgFixLinksTests.py.  Please
resolve any bugs found via running the test script before running orgFixLinks.py.

**WARNING** it can screw up your files.  Please first backup your files.

**WARNING** it does not recognize all possible org file characteristics and may trample
them (backup first; dry run mode first)

**WARNING** org mode in emacs can change and this script can break as a result

**WARNING** intended for experienced users only

**WARNING** tags that are all caps are changed to all lowercase; if you know
python, this is easy to change

The script is amateur work that overwrites files on your local disk.  **_If you are not
ready, willing, and able to restore all your files from backups, don't run this._**

## Installation
	
**WARNING**  only known to work in Ubuntu 14.04, with default bash


recommended but optional: set up a virtual environment (<http://docs.python-guide.org/en/latest/dev/virtualenvs/>)

emacs 24.3.1 and org mode 7.9.3f

Python 2.7.6


Python add-ons:

pudb (debugger)  not required, but useful; script has a flag to run it.

Output of `pip list` in my virtual environment:

backports.shutil-get-terminal-size (1.0.0)

cffi (1.6.0)

cryptography (1.3.2)

decorator (4.0.9)

enum34 (1.1.4)

idna (2.1)

ipaddress (1.0.16)

ipython (4.2.0)

ipython-genutils (0.1.0)

ndg-httpsclient (0.4.0)

pathlib2 (2.1.0)

pexpect (4.0.1)

pickleshare (0.7.2)

pip (8.1.2)

ptyprocess (0.5.1)

pudb (2016.1)

pyasn1 (0.1.9)

pycparser (2.14)

Pygments (2.1.3)

pyOpenSSL (16.0.0)

pysqlite (2.8.2)

requests (2.10.0)

setuptools (21.0.0)

simplegeneric (0.8.1)

six (1.10.0)

traitlets (4.2.1)

urwid (1.3.1)

## Usage

In terminal, typing `orgFixLinks -h` prints the usage message:

>flags with no input argument:

>-h, --help: show this help blurb

>-u, --userFixesLinks: when automatic link repair fails and it makes sense to do so, prompt user to fix broken links manually (menu-driven)

>-n, --noSpideringStopViaKeystroke: normally spidering can be stopped via typing anything then hitting enter key; -n disables this.  also set by -d.

>-d, --debug:  run script in pudb.  additionally sets -n.

>-D, --dryRun:  make no changes to org files on disk.  make a copy of database and make changes to the copy.

>-l, --showLog:  use pager less to display log file after operating on each org file; this gives you time to inspect a rewritten org file in dry run mode before it's reverted to original

>-b, --noBackup: do not make .bak copy of org file before replacing it on disk

>-q, --quickMode: when a file has been recently spidered, just look up outward links in database and move to next file to spider, rather than making full representation, repairing links, etc;  intention is to speed things up

> 

>flags that require input argument:

>-f, --inputFile:  supply a file to begin spidering; if no -f, all org files in /home/username/Documents are walked

>-L, --loggingLevel:  logging to take place above this level.  valid inputs: None, debug, info, warning, error, critical;  default value None

>-N, --maxFilesToSpider:  max number of files to spider, an integer

>-t, --maxTimeToSpider: max time to spend spidering (seconds)

> 

>`python -O`:  `-O` flag turns off assert statements in the script `orgFixLinks.py`.  Assert statements identify associated preconfigured error conditions.  Suppressing them via `-O` flag speeds up script execution.

> 

>When spidering in dry run mode, the `-O` flag is needed to suppress an error in which the database shows a unique ID for a file, but the file does not contain this unique ID

>(because the file was not rewritten on disk in a dry run)

> 

>example call:

>python -O OrgModeFileCrawler01.py -uD -f /home/userName/Documents/myOrgFilename.org -N 20 -t 300


For further details, please check out the [wiki](https://github.com/cashTangoTangoCash/orgFixLinks/wiki).

## Contributing

There is no question that this script will improve given further development.
It does run on my machine, but bugs can be found.

Boilerplate from <https://gist.github.com/zenorocha/4526327>:

> 1. Fork it!
> 
> 2. Create your feature branch: `git checkout -b my-new-feature`
> 
> 3. Commit your changes: `git commit -am 'Add some feature'`
> 
> 4. Push to the branch: `git push origin my-new-feature`
> 
> 5. Submit a pull request :D

I am a beginner with Github.  I make no promises in terms of maintaining
anything.  The phrase 'the code is free, people are not' applies.  You can at
least fork.  If I can comprehend your changes (far more likely if verbosely
documented), I am much more likely to accept a pull request.  A test in the test
script orgFixLinksTest.py should be written for any nontrivial change.
Submissions must respect intellectual property rights of work they are derived
from (e.g. citing stackexchange).

I put this project on Github because it would make me happy if someone found it
useful.  It would be exciting to see a better programmer improve on it.  There
is nothing promised here except for the free code.

## Credits

This is an **amateur** `python` script originally developed by the github user
[cashTangoTangoCash](https://github.com/cashTangoTangoCash).

The script contains comments which credit sources of code snippets
found on e.g. <http://programmers.stackexchange.com/>.

## License

GNU General Public License v3.0

See: [LICENSE.txt](https://github.com/cashTangoTangoCash/orgFixLinks/blob/master/LICENSE.txt)

## Acknowledgments

Particularly helpful:

The free online book **Python for Informatics Exploring Information** by
Severance: the Twitter spidering example in Ch 14 provided the idea for this script.

The Gauld Tutorial <http://www.alan-g.me.uk/tutor/index.htm>

I am highly aware that I did not read and understand everything, and have much
more to learn.
