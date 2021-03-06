# 20160920  trying to expand the number of different types of org mode links my script can recognize
# org mode version in manual is 8.3.6; version I am using in ubuntu 14.04 is 7.9.3f

# goal: my script to correctly identify when a link goes to a local file on disk; my script tries to fix links to local files on disk.  otherwise my script should not mangle a link.

#20160924  it seems overly difficult to manually go down a list of example links and assign the correct regex; too boring and error-prone

import re
#TODO use logging module as in main script

from IPython import embed
# import pudb
# import types

#head
class TestLink():
    def __init__(self,link1,desiredRegexToMatch=None):
        self.text=link1 # [[link1][description]]; if no brackets, it's the whole thing
        self.desiredRegex=desiredRegexToMatch  # compiled regex object that should match this link

        self.matchObjFromDesiredRegex=None # does the desired regex match me?  corresponding match object; initialize to None

        self.desiredRegexMatchesMeFirstInList=None  # the desired regex not only has to match this link, but must be the first in line to do so; initialize to None

        self.filenameFromRegexMatchEqualsInputFilenameVar=None  #initialize to None, which I use to represent unknown, or even inapplicable

    def getRegexSearchMatches(self,regexOrderedList1):
        '''
        regexOrderedList1 is a list of compiled regex objects
        '''
        self.regexMatches1=[(a,a.match(self.text)) for a in regexOrderedList1] # a list of tuples
        self.regexMatches2=[z for z in self.regexMatches1 if z[1]]  #the tuples from regexMatches1 where there is a match
        if self.regexMatches2:  #if there are any matches
            if self.desiredRegex and self.regexMatches2[0][0]==self.desiredRegex:  #if there is a desired regex and it matched and was first in the list
                self.matchObjFromDesiredRegex=self.regexMatches2[0][1]
                self.desiredRegexMatchesMeFirstInList=True
                return

            if self.desiredRegex:
                self.desiredRegexMatchesMeFirstInList=False  #does not correspond to first in regexOrderedList; checked for that previously

                matchObj=[tup[1] for tup in self.regexMatches2 if tup[0]==self.desiredRegex]
                if matchObj:
                    self.matchObjFromDesiredRegex=matchObj[0]  #matchObj is a list (generated by a list comprehension)

class InternalTestLink(TestLink):
    def __init__(self,link1):
        TestLink.__init__(self,link1)
        self.toRepairableFile=None  #internal link does not link to a file on disk that script can repair link to
        #org does not see this link as a link to a file on disk; it tries to search inside the file the link is in

class ExternalTestLink(TestLink):
    def __init__(self,link1,toRepairableFile=None,file=None,desiredRegexToMatch=None):

        self.toRepairableFile=toRepairableFile  # either None or filename of repairable local disk file
        #if org does not think it is a link to a file, then it cannot be a link to a repairable file

        if file:
            link1='file:'+link1

        TestLink.__init__(self,link1,desiredRegexToMatch=desiredRegexToMatch)

        #if desiredRegexToMatch has a named group 'filename' and toRepairableFile is None, raise error
        #20160925 unclear if this should really be an error
        if desiredRegexToMatch and ('?P<filename>' in desiredRegexToMatch.pattern):
            assert toRepairableFile, 'Desired regex has named group filename but did not supply filename in toRepairableFile (%s)' % link1 

        #if toRepairableFile and desiredRegexToMatch lacks named group 'filename', raise error
        if toRepairableFile:
            assert desiredRegexToMatch, 'Example link %s has toRepairableFile %s, but no desiredRegexToMatch' % (link1,toRepairableFile)
            assert ('?P<filename>' in desiredRegexToMatch.pattern), 'Example link %s has toRepairableFile %s and desiredRegexToMatch, but desiredRegexToMatch lacks filename group' % (link1,toRepairableFile)

    def filenameFromRegexMatchEqualsInputFilenameFun(self):
        assert self.toRepairableFile, '%s does not have an associated filename of interest' % self.text
        assert self.matchObjFromDesiredRegex, '%s does not have a regex match object from desired regex %s' % (self.text,self.desiredRegexToMatch)

        if self.toRepairableFile==self.matchObjFromDesiredRegex.group('filename'):
            self.filenameFromRegexMatchEqualsInputFilenameVar=True
            return True
        else:
            self.filenameFromRegexMatchEqualsInputFilenameVar=False
            return False

    def regenLinkText(self,newFilename=None):
        pass
        #TODO how to find error when swapping in a new filename via regex operations?

#head
def makeOrderedListOfRegex():
    global webLinkRegex1

    global localOrgFilesRegex100
    global localOrgFilesRegex150
    global localFilesRegex100
    global localFilesRegex150

    global localOrgFilesRegex200
    global localOrgFilesRegex250
    global localFilesRegex200
    global localFilesRegex250

    #regex101.com seems ideal for developing regexes; be sure to select python

    webLinkRegex1=re.compile(ur'^(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))$')

    # localDiskFileRegex2=re.compile(r'[.~]?[/][^@*]*')  #should last asterisk be + instead?  link to root / of filesystem works when inside brackets, but is not clickable without brackets

    #text search inside a file being linked to: replace (::\d+) with (::.+) in the previous two
    #also works for headline search

    #some link types of interest:
    #  ./*.org  wildcard in filename
    # file+sys:
    # file+emacs:
    #docview:  and  ::32

    #local file: quick googling suggests filenames containing colon exist, so cannot exclude it from filename
    
    #TODO can a raw string be stored in a variable?  want to build up these regex: re.compile(a+b) where a=r'one string' and b=r'another string'

    # anyFilename does not include @ or * characters

    # file:anyFilename.org::anything or file+sys:anyFilename.org::anything or file+emacs:anyFilename.org::anything or docview:anyFilename.org::anything
    # localOrgFilesRegex100=re.compile(r'^((file(([+]sys)|([+]emacs))?:)|(docview:))(?P<filename>[^@*]+?[.]org)(::.+)$')  #be sure to select python in regex101.com
    # make many groups non-capturing; want to be able to reconstruct link when changing filename; link = preFilename + filename + postFilename
    localOrgFilesRegex100=re.compile(r'^(?P<preFilename>(?:file(?:(?:[+]sys)|(?:[+]emacs))?:)|(?:docview:))(?P<filename>[^@*]+?[.]org)(?P<postFilename>::.+)$')  #cannot have spaces in named group names

    # /anyFilename.org::anything  or  ./anyFilename.org::anything  or  ~/anyFilename.org::anything
    localOrgFilesRegex150=re.compile(r'^(?P<preFilename>)(?P<filename>[.~]?[/][^@*]+?[.]org)(?P<postFilename>::.+)$')  #be sure to select python in regex101.com

    # file:anyFilename::anything or file+sys:anyFilename::anything or file+emacs:anyFilename::anything or docview:anyFilename::anything
    localFilesRegex100=re.compile(r'^(?P<preFilename>(?:file(?:(?:[+]sys)|(?:[+]emacs))?:)|(?:docview:))(?P<filename>[^@*]+?)(?P<postFilename>::.+)$')  #cannot have spaces in named group names

    # /anyFilename::anything  or  ./anyFilename::anything  or  ~/anyFilename::anything
    localFilesRegex150=re.compile(r'^(?P<preFilename>)(?P<filename>[.~]?[/][^@*]+?)(?P<postFilename>::.+)$')


    # file:anyFilename.org or file+sys:anyFilename.org or file+emacs:anyFilename.org or docview:anyFilename.org
    localOrgFilesRegex200=re.compile(r'^(?P<preFilename>(?:file(?:(?:[+]sys)|(?:[+]emacs))?:)|(?:docview:))(?P<filename>[^@*]+?[.]org$)(?P<postFilename>)')

    # /anyFilename.org  or  ./anyFilename.org  or  ~/anyFilename.org
    localOrgFilesRegex250=re.compile(r'^(?P<preFilename>)(?P<filename>[.~]?[/][^@*]+?[.]org$)(?P<postFilename>)')

    # file:anyFilename or file+sys:anyFilename or file+emacs:anyFilename or docview:anyFilename
    localFilesRegex200=re.compile(r'^(?P<preFilename>(?:file(?:(?:[+]sys)|(?:[+]emacs))?:)|(?:docview:))(?P<filename>[^@*]+$)(?P<postFilename>)')

    # /anyFilename  or  ./anyFilename  or  ~/anyFilename
    localFilesRegex250=re.compile(r'^(?P<preFilename>)(?P<filename>[.~]?[/][^@*]+$)(?P<postFilename>)')

    # other link types of interest:
    #  info:org#External links
    #  shell:ls *.org
    
    return [webLinkRegex1,localOrgFilesRegex100,localOrgFilesRegex150,localFilesRegex100,localFilesRegex150,localOrgFilesRegex200,localOrgFilesRegex250,localFilesRegex200,localFilesRegex250]

#head
def get_internal_link_examples():
    # internal links  http://orgmode.org/manual/Internal-links.html#Internal-links

    internalLinkExamples=[]

    #these will not be clickable in org mode without brackets
    #I do not want these in header

    link1='#my-custom-id'
    internalLinkExamples.append(InternalTestLink(link1))

    link1='a link'
    internalLinkExamples.append(InternalTestLink(link1))

    #link heading by ID; this is in 4.3 external links but seems to be an internal link
    link1='id:B7423F4D-2E8A-471B-8810-C40F074717E9'
    internalLinkExamples.append(InternalTestLink(link1))

    # radio targets are internal links to <<<target>>> and have no brackets; no need to repair them

    return internalLinkExamples

def get_external_link_examples_part_1():
    # external links  http://orgmode.org/manual/External-links.html#External-links

    externalLinkExamples=[]

    link1='http://www.astro.uva.nl/~dominik'  # on the web
    externalLinkExamples.append(ExternalTestLink(link1,desiredRegexToMatch=webLinkRegex1))

    #clickable without brackets
    # do not want to include this type of link in machine-generated header since I have no personal use for this
    link1='doi:10.1000/182'
    externalLinkExamples.append(ExternalTestLink(link1))

    return externalLinkExamples

def get_external_link_examples_part_2():
    # external links  http://orgmode.org/manual/External-links.html#External-links

    externalLinkExamples=[]

    regex1=None
    regex2=localOrgFilesRegex200

    link1='OrgModeFileCrawlerMain.org'
    externalLinkExamples.append(ExternalTestLink(link1,desiredRegexToMatch=regex1))  #org will not see this as clickable link without brackets
    #if it has brackets, it will look like internal link to org

    #with file: in front, it will be clickable without brackets
    externalLinkExamples.append(ExternalTestLink(link1,toRepairableFile=link1,file=True,desiredRegexToMatch=regex2))


    regex1=localOrgFilesRegex250
    regex2=localOrgFilesRegex200

    link1='/OrgModeFileCrawlerMain.org'
    externalLinkExamples.append(ExternalTestLink(link1,toRepairableFile=link1,desiredRegexToMatch=regex1))  #without brackets, this would not be clickable
    externalLinkExamples.append(ExternalTestLink(link1,toRepairableFile=link1,file=True,desiredRegexToMatch=regex2))

    link1='./OrgModeFileCrawlerMain.org'
    externalLinkExamples.append(ExternalTestLink(link1,toRepairableFile=link1,desiredRegexToMatch=regex1))  #without brackets, this would not be clickable
    externalLinkExamples.append(ExternalTestLink(link1,toRepairableFile=link1,file=True,desiredRegexToMatch=regex2))

    link1='~/OrgModeFileCrawlerMain.org'
    externalLinkExamples.append(ExternalTestLink(link1,toRepairableFile=link1,desiredRegexToMatch=regex1))  #without brackets, this would not be clickable
    externalLinkExamples.append(ExternalTestLink(link1,toRepairableFile=link1,file=True,desiredRegexToMatch=regex2))


    regex1=None
    regex2=localOrgFilesRegex100

    #text search in org file
    file1='OrgModeFileCrawlerMain.org'
    link1=file1+'::what about'
    externalLinkExamples.append(ExternalTestLink(link1,desiredRegexToMatch=regex1))  #org will not see this as clickable link without brackets
    #if it has brackets, it will look like internal link to org

    #with file: in front, it will be clickable without brackets
    externalLinkExamples.append(ExternalTestLink(link1,toRepairableFile=file1,file=True,desiredRegexToMatch=regex2))

    return externalLinkExamples

def get_external_link_examples_part_3():
    # external links  http://orgmode.org/manual/External-links.html#External-links

    externalLinkExamples=[]

    regex1=localFilesRegex250
    regex2=localFilesRegex200

    link1='/home/dad84/Documents/Computer/Software/OrgModeNotes/MyOrgModeScripts/OrgModeFileCrawler/20160908ExceptionTest.py'
    externalLinkExamples.append(ExternalTestLink(link1,toRepairableFile=link1,desiredRegexToMatch=regex1))  #without brackets, this would not be clickable
    externalLinkExamples.append(ExternalTestLink(link1,toRepairableFile=link1,file=True,desiredRegexToMatch=regex2))

    link1='./20160908ExceptionTest.py'
    externalLinkExamples.append(ExternalTestLink(link1,toRepairableFile=link1,desiredRegexToMatch=regex1))  #without brackets, this would not be clickable
    externalLinkExamples.append(ExternalTestLink(link1,toRepairableFile=link1,file=True,desiredRegexToMatch=regex2))

    link1='./20160908Exception Test.py'
    #org will get goofed up by the space if there are no brackets; only the first part will be the clickable link
    externalLinkExamples.append(ExternalTestLink(link1,toRepairableFile=link1,desiredRegexToMatch=regex1))  #without brackets, this would not be clickable
    externalLinkExamples.append(ExternalTestLink(link1,toRepairableFile=link1,file=True,desiredRegexToMatch=regex2))

    link1='~/20160908ExceptionTest.py'
    externalLinkExamples.append(ExternalTestLink(link1,toRepairableFile=link1,desiredRegexToMatch=regex1))  #without brackets, this would not be clickable
    externalLinkExamples.append(ExternalTestLink(link1,toRepairableFile=link1,file=True,desiredRegexToMatch=regex2))


    regex1=None
    regex2=localFilesRegex200

    link1='20160908ExceptionTest.py'
    externalLinkExamples.append(ExternalTestLink(link1,desiredRegexToMatch=regex1))  #org will not see this as clickable link without brackets
    #if it has brackets, it will look like internal link to org

    #with file: in front, it will be clickable without brackets
    externalLinkExamples.append(ExternalTestLink(link1,toRepairableFile=link1,file=True,desiredRegexToMatch=regex2))

    #a directory
    link1='PythonScriptOldVersions'
    externalLinkExamples.append(ExternalTestLink(link1,desiredRegexToMatch=regex1))  #org will not see this as clickable link without brackets
    #if it has brackets, it will look like internal link to org

    #with file: in front, it will be clickable without brackets
    externalLinkExamples.append(ExternalTestLink(link1,toRepairableFile=link1,file=True,desiredRegexToMatch=regex2))

    return externalLinkExamples

def get_external_link_examples_part_4():
    # external links  http://orgmode.org/manual/External-links.html#External-links

    externalLinkExamples=[]

    #file on remote machine; my script will not repair this
    #do not want any regex to match it; do not want it in header
    link1='/myself@some.where:papers/last.pdf'
    externalLinkExamples.append(ExternalTestLink(link1))
    externalLinkExamples.append(ExternalTestLink(link1,file=True))

    regex1=None
    regex2=localFilesRegex100

    #jump to line number (non org file)
    file1='20160908ExceptionTest.py'
    link1=file1+'::23'
    externalLinkExamples.append(ExternalTestLink(link1,desiredRegexToMatch=regex1))  #not clickable in org mode without brackets; with brackets it looks like internal link
    externalLinkExamples.append(ExternalTestLink(link1,toRepairableFile=file1,file=True,desiredRegexToMatch=regex2))  #with file: in front, it is clickable with or without brackets


    regex1=localFilesRegex150
    regex2=localFilesRegex100

    file1='/home/dad84/Documents/Computer/Software/PythonNotes/SeverancePythonForInformatics/PythonForInformaticsSeverance009d2.pdf'
    link1=file1+'::32'
    externalLinkExamples.append(ExternalTestLink(link1,toRepairableFile=file1,desiredRegexToMatch=regex1))  #not clickable without brackets
    externalLinkExamples.append(ExternalTestLink(link1,toRepairableFile=file1,file=True,desiredRegexToMatch=regex2))  #with file: in front, it is clickable with or without brackets


    return externalLinkExamples

def get_external_link_examples_part_5():
    # external links  http://orgmode.org/manual/External-links.html#External-links

    externalLinkExamples=[]

    regex1=None
    regex2=localOrgFilesRegex100

    #a heading search in org file
    file1='OrgModeFileCrawlerMain.org'
    link1=file1+'::**what about'
    externalLinkExamples.append(ExternalTestLink(link1,desiredRegexToMatch=regex1))  #org will not see this as clickable link without brackets
    #if it has brackets, it will look like internal link to org

    #with file: in front, it will be clickable without brackets
    externalLinkExamples.append(ExternalTestLink(link1,toRepairableFile=file1,file=True,desiredRegexToMatch=regex2))


    regex1=localFilesRegex200 

    #open via OS, like double-click; this type of link seems not to work
    file1='./20160807PuzzleOverProgramLogic.xoj'
    link1='file+sys:'+file1
    externalLinkExamples.append(ExternalTestLink(link1,toRepairableFile=file1,desiredRegexToMatch=regex1))

    #force opening by emacs
    file1='./20160807PuzzleOverProgramLogic.xoj'
    link1='file+emacs:'+file1
    externalLinkExamples.append(ExternalTestLink(link1,toRepairableFile=file1,desiredRegexToMatch=regex1))


    regex1=localFilesRegex100

    # open in doc-view mode at page
    file1='/home/dad84/Documents/Computer/Software/PythonNotes/SeverancePythonForInformatics/PythonForInformaticsSeverance009d2.pdf'
    link1='docview:'+file1+'::32'
    externalLinkExamples.append(ExternalTestLink(link1,toRepairableFile=file1,desiredRegexToMatch=regex1))

    return externalLinkExamples

def get_external_link_examples_part_6():
    # external links  http://orgmode.org/manual/External-links.html#External-links

    externalLinkExamples=[]

    #put link to heading by ID in internal links where I believe it belongs

    link1List=[]

    link1='news:comp.emacs'  # usenet link;  does not require brackets; nothing happens when I try opening it in org mode
    link1List.append(link1)
    link1='mailto:adent@galaxy.net'  # mail link;  does not require brackets
    link1List.append(link1)
    link1='mhe:folder' # MH-E folder link
    link1List.append(link1)
    link1='mhe:folder#id' # MH-E message link
    link1List.append(link1)
    link1='rmail:folder' # RMAIL folder link
    link1List.append(link1)
    link1='rmail:folder#id' # RMAIL message link
    link1List.append(link1)
    link1='gnus:folder' # GNUS folder link
    link1List.append(link1)
    link1='gnus:folder#id' # GNUS message link
    link1List.append(link1)
    link1='gnus:group' # Gnus group link
    link1List.append(link1)
    link1='gnus:group#id' # Gnus article link
    link1List.append(link1)
    link1='bbdb:R.*Stallman' # BBDB link (with regexp)
    link1List.append(link1)
    link1='irc:/irc.com/#emacs/bob' # IRC link
    link1List.append(link1)
    link1='vm:folder' # VM folder link 
    link1List.append(link1)
    link1='vm:folder#id' # VM message link 
    link1List.append(link1)
    link1='vm://myself@some.where.org/folder#id' # VM on remote machine 
    link1List.append(link1)
    link1='vm-imap:account:folder' #VM IMAP folder link 
    link1List.append(link1)
    link1='vm-imap:account:folder#id' #VM IMAP message link 
    link1List.append(link1)
    link1='wl:folder' # WANDERLUST folder link
    link1List.append(link1)
    link1='wl:folder#id' # WANDERLUST message link
    link1List.append(link1)
    #might want this in a header, but it needs its own section; SKIP
    link1='info:org#External links' #info node or index link  USEFUL 
    link1='shell:ls *.org' #a shell command; anything with a space has to be in brackets to be a link 
    link1List.append(link1)
    link1='elist:org-agenda' #interactive Elisp command; must have brackets
    link1List.append(link1)
    link1='elisp:(find-file-other-frame "Elisp.org")' #Elisp form to evaluate; must have brackets 
    link1List.append(link1)

    #I don't want these in machine-generated header, and they do not have link to local file to repair
    for link1 in link1List:
        externalLinkExamples.append(ExternalTestLink(link1))

    return externalLinkExamples

def get_external_link_examples_part_7():

    externalLinkExamples=[]

    #skipping putting this in header; seems hard to repair link if broken
    link1='./*.org' # asterisk (wildcard) in filename; works in emacs
    externalLinkExamples.append(ExternalTestLink(link1))
    externalLinkExamples.append(ExternalTestLink(link1,file=True))

    #skipping putting this in header; seems hard to repair link if broken
    link1='./*.py' # asterisk (wildcard) in filename; works in emacs
    externalLinkExamples.append(ExternalTestLink(link1))
    externalLinkExamples.append(ExternalTestLink(link1,file=True))

    return externalLinkExamples

#head
def getOrgModeLinkExamples():
    ret1=[]

    #this list is not comprehensive (not all possible variations)

    ret1.extend(get_internal_link_examples())

    ret1.extend(get_external_link_examples_part_1())
    ret1.extend(get_external_link_examples_part_2())
    ret1.extend(get_external_link_examples_part_3())
    ret1.extend(get_external_link_examples_part_4())
    ret1.extend(get_external_link_examples_part_5())
    ret1.extend(get_external_link_examples_part_6())
    ret1.extend(get_external_link_examples_part_7())

    return ret1

#head

regexOrderedList=makeOrderedListOfRegex()

orgModeLinkExamples=getOrgModeLinkExamples()

for a in orgModeLinkExamples:
    a.getRegexSearchMatches(regexOrderedList)

print 'Now printing test results'
print 'True means no mistakes; False means mistakes exist'
print 'T/F: In every single example, if there was a desired regex to match first in list, it matched: %s' % all([a.desiredRegexMatchesMeFirstInList for a in orgModeLinkExamples if a.desiredRegex])
print 'T/F: For every single example, if the example should not match any regex, it matched none: %s' % (not any([any(a.regexMatches2) for a in orgModeLinkExamples if (not a.desiredRegex)]))
# type this into ipython to see a list of unwanted matches: [(b,a.text) for b,a in enumerate(orgModeLinkExamples) if ((not a.desiredRegex) and any(a.regexMatches2))]
print 'T/F: In every single example, if link was to a local file (repairable) and desired regex matched, the filename from match with desired regex equals known input filename: %s' % all([a.filenameFromRegexMatchEqualsInputFilenameFun() for a in orgModeLinkExamples if (a.toRepairableFile and a.matchObjFromDesiredRegex)])

# TODO also check filename identified by regex is the same as input filename
# TODO also check that entire link output by regex is same as input link

#google: python script go into ipython
#embed()  #drop into an ipython session; variables don't retain changes

# use ipython and rege101.com to inspect the failed examples; use enumerate function and list comprehensions

#which have failed matches between input filename and filename captured via desired regex?

# [(a.text,a.desiredRegex) for a in orgModeLinkExamples if a.filenameFromRegexMatchEqualsInputFilenameVar==False]
# from output of this, you can go into regex101.com and see what went wrong

#TODO idea with the classes: trying to come up with automated test of orgFixLinks.py ability to recognize correct type of link, and to recognize if there ia a repairable link to a local disk file & pick out the correct filename

