# orgFixLinks.py, a Python Command-Line Utility

**Please see Warnings and State of Development below.**

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

2.  Optionally add a [header](header.md) to an org file; this header is a list of incoming links, outgoing
    links, and tags.  This feature is off by default.


The script is a command line utility to be used in the terminal.  Currently it
is known to run in the Ubuntu OS only.  Display its help message:

>python orgFixLinks.py -h

## Warnings and State of Development
**WARNING** this python script is amateur work

**WARNING** bugs are still regularly appearing.  Comprehensively testing this
code is not easy; there is now a test script: `orgFixLinksTests.py`.  First run
the test script.  If it finds a problem, fixing that problem is recommended
before operating on your files.

**WARNING** `orgFixLinks.py` can screw up your files.  Please first backup your files.

**WARNING** `orgFixLinks.py` does not recognize all possible org file characteristics and may trample
them (backup first; dry run mode first)

**WARNING** org mode in emacs can change and this script can break as a result

**WARNING** intended for experienced users only

~~**WARNING** tags that are all caps are changed to all lowercase; if you know
python, this is easy to change~~

The script is amateur work that overwrites files on your local disk.  **_If you are not
ready, willing, and able to restore all your files from backups, don't run this._**

## Installation
	
**WARNING**  only known to work in `Ubuntu 14.04`, with default bash


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

## Getting Help

In terminal, typing `python orgFixLinks.py -h` prints the usage message:

	`Before running orgFixLinks.py on your org files, first run orgFixLinksTests.py, and resolve any errors it reports

    example of running orgFixLinks.py:
    python -O orgFixLinks.py -uD -f /home/userName/Documents/myOrgFilename.org -N 20 -t 300

    flags with no input argument:
    -h, --help: show this help blurb
    -H, --addHeader: add a header to org files; default is to not add a header to any org file
    -u, --userFixesLinks: when automatic link repair fails and it makes sense to do so, prompt user to fix broken links manually (menu-driven)
    -n, --noSpideringStopViaKeystroke: normally spidering can be stopped via typing anything then hitting enter key; -n disables this.  also set by -d.
    -d, --debug:  run script in pudb.  additionally sets -n.
    -D, --dryRun:  make no changes to org files on disk.  make a copy of database and make changes to the copy.
    -l, --showLog:  display log file in terminal after operating on each org file; this gives user time to inspect a rewritten org file in dry run mode before the file is reverted to original
    -b, --noBackup: do not make .bak copy of each org file before replacing it on disk
    -q, --quickMode: when a file has been recently spidered, just look up outward links in database and move to next file to spider, rather than making full representation, repairing links, etc;  intention is to speed things up

    flags that require input argument:
    -f, --inputFile:  supply a file to begin spidering; if no -f, all org files in /home/username/Documents (default) are walked; see also -F, --folderToSpider
    -L, --loggingLevel:  logging to take place above this level.  valid inputs: None, debug, info, warning, error, critical;  default value None
    -N, --maxFilesToSpider:  max number of files to spider, an integer
    -t, --maxTimeToSpider: max time to spend spidering (seconds)
    -F, --folderToSpider: specify a folder to spider in (will spider in this folder and subfolders recursively); default is /home/username/Documents

    useful python flags:
    python -O:  -O flag turns off assert statements in the script orgFixLinks.py.  Assert statements identify associated preconfigured error conditions.  Suppressing them via -O flag speeds up script execution.
    At current state of development of orgFixLinks.py, it is recommended to not use the -O flag.

    files that affect the behavior of orgFixLinks.py:
    pastInteractiveRepairs.csv: contains data from past runs of orgFixLinks.py in which a user interactively repaired broken links

    orgFilesDryRunCopy.sqlite, orgFiles.sqlite: sqlite database used by orgFixLinks.py

    .OFLDoNotSpider: each line is a pattern corresponding to files or folders that will not be spidered.  Each line is interpreted to match files/folders on disk using the Python module glob.glob.
    Any folder will blacklist all files whose path contains that folder.

    .OFLDoNotRepairLinks:  same as .OFLDoNotSpider, but broken links to matching files/folders will not be repaired.  Also, the matches will not be used to repair broken links.`

For further details, please check out the [wiki](https://github.com/cashTangoTangoCash/orgFixLinks/wiki).

## Configuring; Settings
Search inside orgFixLinks.py for comments that include the text 'setting'

Blacklisting for spidering and repairing links is essential since many users
will have a subset of their files that they do not want orgFixLinks.py to
modify.  To control blacklisting, create configuration files
.OFLDoNotSpider, .OFLDoNotRepairLinks.  Each line is interpreted using
glob.glob: see [a PyMOTW article](https://pymotw.com/2/glob/).

Example configuration file contents:

> \# this is a comment

> /home/userName/Documents/Computer/Software/OrgModeNotes/MyOrgModeScripts/OrgModeFileCrawler/contributeToWorgNotes/worg

> /home/userName/Documents/Computer/Software/OrgModeNotes/MyOrgModeScripts/OrgModeFileCrawler/20160720TestFile.org

> \# /home/userName/Documents/Computer

> \# /home/userName/Documents

There are further blacklisting controls inside orgFixLinks.py, primarily two lists
of individual folder names (e.g. 'env', 'venv') for blacklisting; find them via
text search for 'setting.'

## Contributing

There is no question that this script will improve given further development.
It does run on my machine, but bugs appear regularly.

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
least fork.  If I can comprehend your changes (far more likely if sufficiently
documented), I am much more likely to accept a pull request.  A test in the test
script `orgFixLinksTest.py` should be written for any nontrivial change.
Submissions must respect intellectual property rights of work they are derived
from (e.g. citing `stackexchange`).

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
