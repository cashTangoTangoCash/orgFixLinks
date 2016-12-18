'''
A python console-based simple interactive script for crawling through org files on local disk
Updating header lines in org files
Fixing broken links inside org files
Focus is on links within org files
'''

import sys
import getopt
import os
import subprocess
import pudb
import datetime
import re
import random
import types
import shutil
import sqlite3
import time
import logging
import glob
import traceback
import threading
import select
import urllib2
# import shelve
import csv

#head  User-defined exception classes:
class CannotInitiallyOperateOnOrgFileError(Exception):
    '''unable to do initial operations on org file'''
    pass

class CannotMakeFullRepresentationError(Exception):
    '''unable to make full representation of org file'''
    pass

class CannotReconcileFileWithDatabaseError(Exception):
    '''unable to reconcile file with sqlite database'''
    pass
class CannotProcessOutgoingLinksError(Exception):
    '''unable to process outgoing links from org file'''
    pass

class CannotRegenerateFileError(Exception):
    '''unable to regenerate org file from full representation'''
    pass

class OrgFileLacksMainlineNodesError(Exception):
    '''
    there are no mainline nodes in org file
    i.e. no lines begin with asterisk followed by space
    '''
    pass

#head  Used for logging:
class CallCounted(object):
    """
    Decorator to determine number of calls for a method
    http://stackoverflow.com/questions/812477/how-many-times-was-logging-error-called
    answer by Mark Roddy 20090501
    """

    def __init__(self,method):
        self.method=method
        self.counter=0

    def __call__(self,*args,**kwargs):
        self.counter+=1
        return self.method(*args,**kwargs)

#head
#head
#head  Database-related classes:
class Database1():
    def __init__(self,filename):
        '''Database1 Class'''

        #TODO is there any issue with filename vs absolute path filename?
        self.filename=filename

        self.conn=sqlite3.connect(filename)
        self.cur=self.conn.cursor()

    def setUpOrgTables(self):
        '''Database1 Class'''
        self.filenameAPsOrgTable=FilenameAPsOrgTable()
        self.pathToBasenameOrgTable=PathToBasenameOrgTable()
        self.basenameOrgTable=BasenameOrgTable()

        self.myOrgFilesTable=MyOrgFilesTable()

        self.symlinksOrgTable=SymlinksOrgTable()
        self.linksToOrgTable=LinksToOrgTable()
        self.previousFilenamesOrgTable=PreviousFilenamesOrgTable()

        self.myOrgFilesTable.createTable(self.filenameAPsOrgTable,self.pathToBasenameOrgTable,self.basenameOrgTable)

        self.symlinksOrgTable.createTable(self.filenameAPsOrgTable,self.myOrgFilesTable)
        self.linksToOrgTable.createTable(self.myOrgFilesTable,self.myOrgFilesTable)
        self.previousFilenamesOrgTable.createTable(self.myOrgFilesTable,self.filenameAPsOrgTable)

    def addFilenameToThreeOrgTables(self,name):
        '''Database1 Class'''
        if name:  #don't try adding None to database tables
            self.filenameAPsOrgTable.addName(name)
            self.pathToBasenameOrgTable.addName(os.path.split(name)[0])  #TODO is there a possibility that argument could turn out to be None?  is that a problem?
            self.basenameOrgTable.addName(os.path.basename(name))

    def setUpNonOrgTables(self):
        '''Database1 Class'''
        self.filenameAPsNonOrgTable=FilenameAPsNonOrgTable()
        self.pathToBasenameNonOrgTable=PathToBasenameNonOrgTable()
        self.basenameNonOrgTable=BasenameNonOrgTable()

        self.myNonOrgFilesTable=MyNonOrgFilesTable()

        self.symlinksNonOrgTable=SymlinksNonOrgTable()
        self.linksToNonOrgTable=LinksToNonOrgTable()
        self.previousFilenamesNonOrgTable=PreviousFilenamesNonOrgTable()

        self.myNonOrgFilesTable.createTable(self.filenameAPsNonOrgTable,self.pathToBasenameNonOrgTable,self.basenameNonOrgTable)

        self.symlinksNonOrgTable.createTable(self.filenameAPsNonOrgTable,self.myNonOrgFilesTable)
        self.linksToNonOrgTable.createTable(self.myOrgFilesTable,self.myNonOrgFilesTable)
        self.previousFilenamesNonOrgTable.createTable(self.myNonOrgFilesTable,self.filenameAPsNonOrgTable)

    def addFilenameToThreeNonOrgTables(self,name):
        '''Database1 Class'''
        if name:  #don't try adding None to database tables
            self.filenameAPsNonOrgTable.addName(name)
            self.pathToBasenameNonOrgTable.addName(os.path.split(name)[0])  #TODO could argument end up being None and is that a problem?
            self.basenameNonOrgTable.addName(os.path.basename(name))

    def execCommitLog(self,command1):
        #goal is to log what was done database-wise
        #TODO instead of editing this long file to use this function, go to apsw, which apparently has logging
        self.cur.execute(command1)
        self.conn.commit()
        logging.debug('database command: '+command1)

#head
class MyFilesTable():
    def __init__(self,tableName,listOfTimeFieldNames,listOfBooleanFieldNames):
        '''MyFilesTable Class; ancestor class for MyOrgFilesTable, MyNonOrgFilesTable
        there should be no instance of MyFilesTable in this script; should only inherit from this class
        '''
        #this table is for non-symlinks; put target of symlink in here as long as it is not also a symlink
        #sqlite will throw syntax error if you mix the FOREIGN KEY pieces in with the other pieces

        self.tableName=tableName
        self.listOfTimeFieldNames=listOfTimeFieldNames
        self.listOfBooleanFieldNames=listOfBooleanFieldNames

    #head
    def updateTimeField(self,file1,timeFieldName):
        '''MyFilesTable Class
        the specified time field is set to the current time
        '''
        assert not file1.inHeader, 'script attempting database operation on file from header link'
        assert file1.myFilesTableID, 'file1 lacks myFilesTableID'

        assert (timeFieldName in self.listOfTimeFieldNames), 'unknown timeFieldName %s' % timeFieldName

        db1.cur.execute('UPDATE '+self.tableName+' SET '+timeFieldName+'=? WHERE id=?',(int(time.time()),file1.myFilesTableID))
        db1.conn.commit()

    def updateBooleanField(self,file1,TrueOrFalse,BooleanFieldName):
        '''MyFilesTable Class
        '''
        assert not file1.inHeader, 'script attempting database operation on file from header link'
        assert file1.myFilesTableID, 'file1 lacks myFilesTableID'
        assert TrueOrFalse in [True,False,None], 'input must be True, False, or None; input was %s' % TrueOrFalse
        assert (BooleanFieldName in self.listOfBooleanFieldNames), 'unknown BooleanFieldName %s' % BooleanFieldName

        if TrueOrFalse==None:
            #convention used in this script: None means unknown
            BoolIn1=None
        else:
            if TrueOrFalse:
                BoolIn1='1'
            else:
                BoolIn1='0'

        db1.cur.execute('UPDATE '+self.tableName+' SET '+BooleanFieldName+'=? WHERE id=?',(BoolIn1,file1.myFilesTableID))

        db1.conn.commit()

    #head
    def incrNumFailedRepairAttempts(self,file1):
        '''MyFilesTable Class
        add one to nConsFailedRepairs
        '''
        assert not file1.inHeader, 'script attempting database operation on file from header link'
        assert file1.myFilesTableID, 'file1 lacks myFilesTableID'

        db1.cur.execute('SELECT nConsFailedRepairs FROM '+self.tableName+' WHERE id = ? LIMIT 1',(file1.myFilesTableID,))

        try:
            (NInitial,) = db1.cur.fetchone()
        except:
            logging.warning('unable to lookup nConsFailedRepairs for id %s in table %s' % (file1.myFilesTableID,self.tableName))
            NInitial=0

        NPlusOne=int(NInitial)+1

        db1.cur.execute('UPDATE '+self.tableName+' SET nConsFailedRepairs=? WHERE id=?',(NPlusOne,file1.myFilesTableID))

        db1.conn.commit()

        logging.debug('incremented number of failed repair attempts in table %s for %s' % (self.tableName,file1.filenameAP))

    def zeroOutNumFailedRepairAttempts(self,file1):
        '''MyFilesTable Class
        set nConsFailedRepairs to zero
        '''
        assert not file1.inHeader, 'script attempting database operation on file from header link'
        assert file1.myFilesTableID, 'file1.myFilesTableID must be set in order to zero out number of failed repair attempts for %s' % file1.filenameAP

        db1.cur.execute('UPDATE '+self.tableName+' SET nConsFailedRepairs=0 WHERE id=?',(file1.myFilesTableID,))

        db1.conn.commit()

        logging.debug('zeroed out number of failed repair attempts in table %s for %s' % (self.tableName,file1.filenameAP))

    #head
    def lookupID_UsingName(self,file1,nameToLookup=None):
        '''MyFilesTable Class
        Use file1.filenameAP to look up file1 in database table
        '''
        assert not file1.inHeader, 'script attempting database operation on file from header link'

        if not nameToLookup:
            nameToLookup=file1.filenameAP

        nameToLookup_LookupID=self.filenameAPsTable.lookupID(nameToLookup)

        assert nameToLookup_LookupID, 'no id found in table %s for %s' % (self.filenameAPsTable.tableName,nameToLookup) 

        db1.cur.execute('SELECT id FROM '+self.tableName+' WHERE filenameAP_id = ? LIMIT 1',(nameToLookup_LookupID,))

        try:
            (id,) = db1.cur.fetchone()
        except:
            id=None

        if id:
            logging.debug('looked up id %s in table %s using name %s' % (id,self.tableName,nameToLookup))
            file1.myFilesTableID=id

        return id

    #head
    def lookupName_UsingID(self,myFilesTableID,returnForm='name'):
        '''MyOrgFiles Class
        given id, return either filenameAP_id, or filenameAP
        depending on optional input returnForm
        '''

        assert returnForm in ['name','id'], 'optional input returnForm must be either name or id'

        db1.cur.execute('SELECT filenameAP_id FROM '+self.tableName+' WHERE id = ? LIMIT 1',(myFilesTableID,))
        try:
            (filenameAP_id,) = db1.cur.fetchone()
        except:
            filenameAP_id=None
            logging.debug('no filenameAP in table %s found given myFilesTableID %s' % (self.tableName,myFilesTableID))
            return None

        if returnForm=='name':
            return self.filenameAPsTable.lookupName(filenameAP_id)
        elif returnForm=='id':
            return filenameAP_id

    #head
    def lookupNumFailedRepairAttemptsByID(self,id):
        '''MyFilesTable Class
        given id, return nConsFailedRepairs
        '''

        db1.cur.execute('SELECT nConsFailedRepairs FROM '+self.tableName+' WHERE id = ? LIMIT 1',(id,))

        try:
            (ncfra,) = db1.cur.fetchone()
        except:
            ncfra = None  #None means unknown

        return ncfra

    #head
    def findBestMatchForMissingFile(self,file1):
        '''MyFilesTable Class
        input: instance of class OrgFile
        output: select the best match in database table myOrgFiles
        return the id of the best match, or None if no match
        '''
        assert not file1.inHeader, 'script attempting database operation on file from header link'
        assert not file1.myFilesTableID, '%s already has id %s in table %s' % (file1.filenameAP,file1.myFilesTableID,self.tableName)
        assert not file1.exists, 'file %s is not missing' % file1.filenameAP

        #this function is less useful because it does set flags in file1?

        idB=None

        idB=self.lookupID_UsingName(file1)

        if not idB:
            idB=self.previousFilenamesTable.lookupUsing_OldName(file1.filenameAP)

        if not idB and (file1.isSymlink or file1.changedFromSymlinkToNonSymlink):
            idB=self.symlinksTable.lookupTarget(file1.originalFilenameAP)

        return idB

    #head
    def updateNameAndLogChange(self,file1,id=None,newName=None):
        '''MyFilesTable Class
        change database value filenameAP to match newName
        if a filename change is performed, log it in previous filenames table
        '''
        assert not file1.inHeader, 'script attempting database operation on file from header link'

        if not id:
            assert file1.myFilesTableID,'did not supply id and default value file1.myFilesTableID is missing for %s' % file1.filenameAP
            id=file1.myFilesTableID

        if not newName:
            newName=file1.filenameAP

        oldName_filenameAP_id=self.lookupName_UsingID(id,returnForm='id')
        assert oldName_filenameAP_id, 'unable to lookup oldName_filenameAP_id'
        oldName=self.filenameAPsTable.lookupName(oldName_filenameAP_id)

        #look up current value in file1
        newName_filenameAP_id=self.filenameAPsTable.lookupID(newName)
        assert newName_filenameAP_id, 'unable to lookup newName_filenameAP_id'

        newPathToBasename_id=self.pathToBasenameTable.lookupID(os.path.split(newName)[0])  #TODO any issue with argument evaluating to None?
        assert newPathToBasename_id, 'unable to lookup newPathToBasename_id'

        newBasename_id=self.basenameTable.lookupID(os.path.basename(newName))
        assert newBasename_id, 'unable to lookup newBasename_id'

        if (newName_filenameAP_id != oldName_filenameAP_id):
            #there has been a name change, so log it in table previousFilenamesOrg
            self.previousFilenamesTable.addRecord(file1,oldName)

        #finally make the requested change

        db1.cur.execute('UPDATE '+self.tableName+' SET filenameAP_id=? WHERE id=?',(newName_filenameAP_id,id))
        db1.cur.execute('UPDATE '+self.tableName+' SET pathToBasename_id=? WHERE id=?',(newPathToBasename_id,id))
        db1.cur.execute('UPDATE '+self.tableName+' SET basename_id=? WHERE id=?',(newBasename_id,id))

        db1.conn.commit()

        logging.debug('changing name of id %s in table %s from %s to %s' % (id,self.tableName,oldName,newName))

    #head
    def syncTableToFile(self,file1):
        '''MyFilesTable Class
        '''
        assert not file1.inHeader, 'script attempting database operation on file from header link'
        assert file1.myFilesTableID, 'file1.myFilesTableID must be non-None for %s' % file1.filenameAP

        logging.debug('syncing existing entry in table %s to %s' % (self.tableName,file1.filenameAP))

        self.updateNameAndLogChange(file1)

        self.updateTimeField(file1,'tLastCheckedExist')

        file1.testIfExists()

        self.updateBooleanField(file1,file1.exists,'fileExists')

        #TODO unsure if numFailedRepairAttempts should be touched here

    #head
    def lookupBasenamesInFolder(self,folder):
        '''MyFilesTable Class
        input: abs path name of folder
        return value: list of basenames of files in that folder (files which are not folders themselves)
        '''

        folder=os.path.realpath(folder)  #get rid of any symlinks

        folder_id=self.pathToBasenameTable.lookupID(folder)

        if not folder_id:
            return None  #TODO this looks undesirable; maybe log a warning?  #no way to tell if no matches found in folder vs folder not in database

        # #TODO I can imagine problems with slashes and so forth; /home/userName will not lookup /home/userName/
        # assert folder_id, 'folder %s not found in %s table' % (folder,self.pathToBasenameTable.tableName)

        db1.cur.execute('SELECT basename_id FROM '+self.tableName+' WHERE pathToBasename_id = ?',(folder_id,))
        #TODO do you always get tuple of tuples back out?

        try:
            basenameID_TupleOfTuples = db1.cur.fetchall()  #expecting it to look like ((1,),(3,),(4,))
        except:
            basenameID_TupleOfTuples=None

        if basenameID_TupleOfTuples:
            basenameIDList=[a[0] for a in basenameID_TupleOfTuples]
            basenameList=[self.basenameTable.lookupName(a) for a in basenameIDList]
        else:
            # basenameList=[]  #TODO or should it be None?
            basenameList=None

        return basenameList

    def constructFileFromTable(self,id):
        '''MyNonOrgFilesTable Class
        input: id value in table myNonOrgFiles
        return value: instance of class NonOrgFile constructed using data in record looked up in myNonOrgFiles table using id
        '''

        file1=None
        name=self.lookupName_UsingID(id)
        if name:
            inHeader=None  #unknown
            file1=self.fileClass(name,inHeader)
            file1.myFilesTableID=id
            if self.__class__.__name__=='MyOrgFilesTable':
                file1.uniqueIDFromDatabase=self.lookupUniqueID_UsingID(id)
            file1.numFailedRepairsFromDatabase=self.lookupNumFailedRepairAttemptsByID(id)
        else:
            logging.warning('Failed to construct %s instance given id %s' % (self.fileClass.__name__,id))

        return file1

class MyOrgFilesTable(MyFilesTable):
    def __init__(self):

        MyFilesTable.__init__(self,'myOrgFiles',['tLastCheckedExist','tLastFullyAnalyzed'],['fileExists'])

        self.fileClass=OrgFile

    def createTable(self,filenameAPsTable,pathToBasenameTable,basenameTable):
        '''MyOrgFilesTable Class'''

        self.filenameAPsTable=filenameAPsTable
        self.pathToBasenameTable=pathToBasenameTable
        self.basenameTable=basenameTable

        self.previousFilenamesTable=db1.previousFilenamesOrgTable
        self.symlinksTable=db1.symlinksOrgTable

        # db1.cur.execute('''CREATE TABLE IF NOT EXISTS myOrgFiles
        # (id INTEGER PRIMARY KEY,
        # filenameAP_id INTEGER NOT NULL,
        # pathToBasename_id INTEGER NOT NULL,
        # basename_id INTEGER NOT NULL,
        # uniqueID TEXT UNIQUE,
        # fileExists INTEGER,
        # tLastCheckedExist INTEGER,
        # tLastFullyAnalyzed INTEGER,
        # nConsFailedRepairs INTEGER,
        # FOREIGN KEY(filenameAP_id) REFERENCES filenameAPsOrg(id),
        # FOREIGN KEY(pathToBasename_id) REFERENCES pathToBasenameOrg(id),
        # FOREIGN KEY(basename_id) REFERENCES basenameOrg(id))''')

        #idea behind nConsFailedRepairs: stop trying to repair a link if have already searched over and over for file

        db1.cur.execute('CREATE TABLE IF NOT EXISTS '+self.tableName+' (id INTEGER PRIMARY KEY, filenameAP_id INTEGER NOT NULL, pathToBasename_id INTEGER NOT NULL, basename_id INTEGER NOT NULL, uniqueID TEXT UNIQUE, fileExists INTEGER, tLastCheckedExist INTEGER, tLastFullyAnalyzed INTEGER, nConsFailedRepairs INTEGER, FOREIGN KEY(filenameAP_id) REFERENCES '+self.filenameAPsTable.tableName+'(id), FOREIGN KEY(pathToBasename_id) REFERENCES '+self.pathToBasenameTable.tableName+'(id), FOREIGN KEY(basename_id) REFERENCES '+self.basenameTable.tableName+'(id))')

    def addFile(self,file1):
        '''MyOrgFilesTable Class'''

        assert isinstance(file1,self.fileClass), 'file1 is not an instance of %s' % self.fileClass.__name__
        assert not file1.inHeader, 'script attempting database operation on file from header link'

        if file1.myFilesTableID:
            logging.warning('tried to add %s to database but it already has database ID set at %s' % (file1.filenameAP,file1.myFilesTableID))
            return None

        argList=['filenameAP_id','pathToBasename_id','basename_id','uniqueID','fileExists']
        argList+=['tLastCheckedExist','tLastFullyAnalyzed']
        argList+=['nConsFailedRepairs']
        argDict1={a:None for a in argList}  #dictionary comprehension

        argDict1['filenameAP_id']=self.filenameAPsTable.lookupID(file1.filenameAP)
        argDict1['pathToBasename_id']=self.pathToBasenameTable.lookupID(os.path.split(file1.filenameAP)[0])
        argDict1['basename_id']=self.basenameTable.lookupID(os.path.basename(file1.filenameAP))

        if file1.uniqueID:
            argDict1['uniqueID']=file1.uniqueID

        file1.testIfExists()
        if file1.exists:
            argDict1['fileExists']='1'
        else:
            argDict1['fileExists']='0'

        argDict1['tLastCheckedExist']=int(time.time())

        if file1.fullRepresentation:
            argDict1['tLastFullyAnalyzed']=int(time.time())

        argDict1['nConsFailedRepairs']='0'

        valList=[argDict1[a] for a in argList]  #list comprehension
        valTuple=tuple(a for a in valList)  #google: tuple comprehension; simply making a tuple from valList

        #TODO do you want INSERT OR IGNORE instead?

        #painful typo to catch: had 4 's instead of 3 's before INSERT and sqlite threw a generic error
        try:
            db1.cur.execute('INSERT INTO '+self.tableName+' (filenameAP_id, pathToBasename_id, basename_id, uniqueID, fileExists, tLastCheckedExist, tLastFullyAnalyzed, nConsFailedRepairs) VALUES (?,?,?,?,?,?,?,?)',valTuple)
        except Exception as err1:
            #try except here is meant to allow me to zero in a problem via pudb
            raise err1

        db1.conn.commit()

        file1.addedToDatabase=True

        file1.myFilesTableID=db1.cur.lastrowid

        assert file1.myFilesTableID, 'missing myFilesTableID from file1 %s' % file1.filenameAP

        logging.debug('added entry with id %s to table %s; filename is %s' % (file1.myFilesTableID,self.tableName,file1.filenameAP))

        return file1.myFilesTableID

    #head
    def lookupID_UsingUniqueID(self,orgFile,uniqueIDName='uniqueID',nameToMatch=None):
        '''MyOrgFilesTable Class
        Use unique ID to look up record
        optional input nameToMatch: if given, require that filenameAP in database match it
        '''
        assert not orgFile.inHeader, 'script attempting database operation on file from header link'

        assert uniqueIDName in ('uniqueID','uniqueIDFromHeader','uniqueIDFromDatabase'), 'unique ID name supplied for lookup does not match a known name'

        uniqueID=getattr(orgFile,uniqueIDName)

        assert uniqueID, 'no unique ID for lookup'

        if nameToMatch:
            nameToMatch_id=self.filenameAPsTable.lookupID(nameToMatch)
            db1.cur.execute('SELECT id FROM myOrgFiles WHERE uniqueID = ? AND filenameAP_id = ? LIMIT 1',(uniqueID,nameToMatch_id,))
        else:
            db1.cur.execute('SELECT id FROM myOrgFiles WHERE uniqueID = ? LIMIT 1',(uniqueID,))

        try:
            (id,) = db1.cur.fetchone()
        except:
            id=None

        if id:
            orgFile.myFilesTableID=id

        return id

    def lookupID_UsingUniqueIDFromHeader(self,orgFile):
        '''MyOrgFilesTable Class
        '''
        return self.lookupID_UsingUniqueID(orgFile,uniqueIDName='uniqueIDFromHeader')

    def lookupID_UsingUniqueIDFromDatabase(self,orgFile):
        '''MyOrgFilesTable Class
        '''
        return self.lookupID_UsingUniqueID(orgFile,uniqueIDName='uniqueIDFromDatabase')

    def lookupUniqueID_UsingID(self,id):
        '''MyOrgFiles Class
        given id, return uniqueID
        '''

        db1.cur.execute('SELECT uniqueID FROM myOrgFiles WHERE id = ? LIMIT 1',(id,))

        try:
            (uniqueID,) = db1.cur.fetchone()
        except:
            uniqueID = None

        return uniqueID

    def lookupTimeLastFullyAnalyzed_UsingID(self,id):
        '''MyOrgFiles Class
        given id, return tLastFullyAnalyzed
        '''

        db1.cur.execute('SELECT tLastFullyAnalyzed FROM myOrgFiles WHERE id = ? LIMIT 1',(id,))

        try:
            (ret,) = db1.cur.fetchone()
        except:
            ret = None

        return ret

    def findBestMatchForExistingFileUsingUniqueID(self,orgFile):
        '''MyOrgFilesTable Class
        input: instance of class OrgFile
        output: select the best match in database table myOrgFiles using the unique ID inside orgFile
        return the id of the best match, or None if no match

        assumed: orgFile.exists is True (or else could not have looked inside it for unique ID)
        assumed: orgFile contains a unique ID inside it
        '''
        assert not orgFile.inHeader, 'script attempting database operation on file from header link'
        assert orgFile.exists, 'orgFile.exists must be True'
        assert orgFile.uniqueID, 'orgFile.uniqueID missing'
        assert orgFile.lookedInsideForUniqueID, 'orgFile.lookedInsideForUniqueID must be True'

        id=self.lookupID_UsingUniqueID(orgFile)  #lookup database record via unique ID

        assert not (id and orgFile.insertedUniqueID), 'a new unique ID was just inserted inside orgFile this session, but somehow that same unique ID is showing up in database'

        if id: #database contains an org file with that unique ID
            logging.debug('using unique ID %s inside %s, looked in myOrgFiles table and found id %s' % (orgFile.uniqueID,orgFile.filenameAP,id))
            orgFile.myFilesTableID=id
            orgFile.uniqueIDFromDatabase=orgFile.uniqueID
            orgFile.checkConsistencyOfThreeUniqueIDDataItems()
            return id
        else:
            logging.debug('using unique ID %s inside %s, looked in myOrgFiles table and did not find a matching id' % (orgFile.uniqueID,orgFile.filenameAP))
            orgFile.uniqueIDFromDatabase=False
            return None

    def updateUniqueID(self,orgFile,id=None,uniqueID=None):
        '''MyOrgFilesTable Class
        '''
        assert not orgFile.inHeader, 'script attempting database operation on file from header link'
        if not id:
            id=orgFile.myFilesTableID

        assert id, 'missing id in MyOrgFilesTable.updateUniqueID'

        if not uniqueID:
            uniqueID=orgFile.uniqueID

        if not uniqueID:
            return None

        oldUniqueIDInDatabase=self.lookupUniqueID_UsingID(id)
        if oldUniqueIDInDatabase and (oldUniqueIDInDatabase != uniqueID):
            logging.warning('unique ID %s to add to database for %s is different than unique ID %s already in database' % (uniqueID,orgFile.filenameAP,oldUniqueIDInDatabase))

        db1.cur.execute('''UPDATE myOrgFiles SET uniqueID=? WHERE id=?''',(uniqueID,id))

        db1.conn.commit()

    #head
    def syncTableToFile(self,file1):
        '''MyOrgFilesTable Class
        '''
        MyFilesTable.syncTableToFile(self,file1)

        if file1.lookedInsideForUniqueID and file1.uniqueID:
            self.updateUniqueID(file1)

class MyNonOrgFilesTable(MyFilesTable):
    def __init__(self):

        MyFilesTable.__init__(self,'myNonOrgFiles',['tLastCheckedExist'],['fileExists'])

        self.fileClass=NonOrgFile
        self.className='MyNonOrgFilesTable'

    def createTable(self,filenameAPsTable,pathToBasenameTable,basenameTable):
        '''MyNonOrgFilesTable Class'''

        self.filenameAPsTable=filenameAPsTable
        self.pathToBasenameTable=pathToBasenameTable
        self.basenameTable=basenameTable

        self.previousFilenamesTable=db1.previousFilenamesNonOrgTable
        self.symlinksTable=db1.symlinksNonOrgTable

        # db1.cur.execute('''CREATE TABLE IF NOT EXISTS myNonOrgFiles
        # (id INTEGER PRIMARY KEY,
        # filenameAP_id INTEGER NOT NULL,
        # pathToBasename_id INTEGER NOT NULL,
        # basename_id INTEGER NOT NULL,
        # fileExists INTEGER,
        # tLastCheckedExist INTEGER,
        # nConsFailedRepairs INTEGER,
        # FOREIGN KEY(filenameAP_id) REFERENCES filenameAPsNonOrg(id),
        # FOREIGN KEY(pathToBasename_id) REFERENCES pathToBasenameNonOrg(id),
        # FOREIGN KEY(basename_id) REFERENCES basenameNonOrg(id))''')

        db1.cur.execute('CREATE TABLE IF NOT EXISTS '+self.tableName+' (id INTEGER PRIMARY KEY, filenameAP_id INTEGER NOT NULL, pathToBasename_id INTEGER NOT NULL, basename_id INTEGER NOT NULL, fileExists INTEGER, tLastCheckedExist INTEGER, nConsFailedRepairs INTEGER, FOREIGN KEY(filenameAP_id) REFERENCES '+self.filenameAPsTable.tableName+'(id), FOREIGN KEY(pathToBasename_id) REFERENCES '+self.pathToBasenameTable.tableName+'(id), FOREIGN KEY(basename_id) REFERENCES '+self.basenameTable.tableName+'(id))')

    def addFile(self,file1):
        '''MyNonOrgFilesTable Class'''

        assert isinstance(file1,self.fileClass), 'file1 is not an instance of %s' % self.fileClass.__name__
        assert not file1.inHeader, 'script attempting database operation on file from header link'

        if file1.myFilesTableID:
            logging.warning('tried to add %s to database but it already has database ID set at %s' % (file1.filenameAP,file1.myFilesTableID))
            return None

        argList=['filenameAP_id','pathToBasename_id','basename_id','fileExists']
        argList+=['tLastCheckedExist']
        argList+=['nConsFailedRepairs']
        argDict1={a:None for a in argList}  #dictionary comprehension

        argDict1['filenameAP_id']=self.filenameAPsTable.lookupID(file1.filenameAP)
        argDict1['pathToBasename_id']=self.pathToBasenameTable.lookupID(os.path.split(file1.filenameAP)[0])
        argDict1['basename_id']=self.basenameTable.lookupID(os.path.basename(file1.filenameAP))

        file1.testIfExists()
        if file1.exists:
            argDict1['fileExists']='1'
        else:
            argDict1['fileExists']='0'

        argDict1['tLastCheckedExist']=int(time.time())

        argDict1['nConsFailedRepairs']='0'

        valList=[argDict1[a] for a in argList]  #list comprehension
        valTuple=tuple(a for a in valList)  #google: tuple comprehension; simply making a tuple from valList

        db1.cur.execute('INSERT INTO '+self.tableName+' (filenameAP_id, pathToBasename_id, basename_id, fileExists, tLastCheckedExist, nConsFailedRepairs) VALUES (?,?,?,?,?,?)',valTuple)

        db1.conn.commit()

        file1.addedToDatabase=True

        file1.myFilesTableID=db1.cur.lastrowid

        assert file1.myFilesTableID, 'missing myFilesTableID from file1 %s' % file1.filenameAP

        logging.debug('added entry with id %s to table %s; filename is %s' % (file1.myFilesTableID,self.tableName,file1.filenameAP))

        return file1.myFilesTableID

#head
class FilenameAPsTable():
    def __init__(self,tableName):
        '''FilenameAPsTable Class'''

        self.tableName=tableName
        db1.cur.execute('CREATE TABLE IF NOT EXISTS '+tableName+'(id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL)')

    def addName(self,name):
        '''FilenameAPsTable Class
        '''
        db1.cur.execute('INSERT OR IGNORE INTO '+self.tableName+' (name) VALUES (?)',(name,))

        db1.conn.commit()

        logging.debug('added %s to table %s at index %s' % (name,self.tableName,db1.cur.lastrowid))

    def lookupID(self,name):
        '''FilenameAPsTable Class
        given name, return id
        '''

        db1.cur.execute('SELECT id FROM '+self.tableName+' WHERE name = ? LIMIT 1',(name,))

        try:
            (id,) = db1.cur.fetchone()
        except:
            id=None

        return id

    def lookupName(self,id):
        '''FilenameAPsOrgTable Class
        given id, return name
        '''

        db1.cur.execute('SELECT name FROM '+self.tableName+' WHERE id = ? LIMIT 1',(id,))

        try:
            (name,) = db1.cur.fetchone()
        except:
            name=None

        return name

class FilenameAPsOrgTable(FilenameAPsTable):
    def __init__(self):
        '''FilenameAPsOrgTable Class'''

        FilenameAPsTable.__init__(self,'filenameAPsOrg')

class FilenameAPsNonOrgTable(FilenameAPsTable):
    def __init__(self):
        '''FilenameAPsNonOrgTable Class'''

        FilenameAPsTable.__init__(self,'filenameAPsNonOrg')

#head
class PathToBasenameTable():
    def __init__(self,tableName):
        '''PathToBasenameTable Class'''

        self.tableName=tableName
        db1.cur.execute('CREATE TABLE IF NOT EXISTS '+tableName+'(id INTEGER PRIMARY KEY, absPathToFile TEXT UNIQUE NOT NULL)')

    def addName(self,name):
        '''PathToBasenameTable Class
        '''
        db1.cur.execute('INSERT OR IGNORE INTO '+self.tableName+' (absPathToFile) VALUES (?)',(name,))

        db1.conn.commit()

        logging.debug('added %s to table %s at index %s' % (name,self.tableName,db1.cur.lastrowid))

    def lookupID(self,name):
        '''PathToBasenameTable Class
        given name, return id
        '''

        db1.cur.execute('SELECT id FROM '+self.tableName+' WHERE absPathToFile = ? LIMIT 1',(name,))

        try:
            (id,) = db1.cur.fetchone()
        except:
            id=None

        return id

    def lookupName(self,id):
        '''PathToBasenameOrgTable Class
        given id, return name
        '''

        db1.cur.execute('SELECT absPathToFile FROM '+self.tableName+' WHERE id = ? LIMIT 1',(id,))

        try:
            (name,) = db1.cur.fetchone()
        except:
            name=None

        return name

class PathToBasenameOrgTable(PathToBasenameTable):
    def __init__(self):
        '''PathToBasenameOrgTable Class'''

        PathToBasenameTable.__init__(self,'pathToBasenameOrg')

class PathToBasenameNonOrgTable(PathToBasenameTable):
    def __init__(self):
        '''PathToBasenameNonOrgTable Class'''

        PathToBasenameTable.__init__(self,'pathToBasenameNonOrg')

#head
class BasenameTable():
    def __init__(self,tableName):
        '''BasenameTable Class'''

        self.tableName=tableName
        db1.cur.execute('CREATE TABLE IF NOT EXISTS '+tableName+'(id INTEGER PRIMARY KEY, basename TEXT UNIQUE NOT NULL)')

    def addName(self,name):
        '''BasenameTable Class
        '''
        db1.cur.execute('INSERT OR IGNORE INTO '+self.tableName+' (basename) VALUES (?)',(name,))

        db1.conn.commit()

        logging.debug('added %s to table %s at index %s' % (name,self.tableName,db1.cur.lastrowid))

    def lookupID(self,name):
        '''BasenameTable Class
        given name, return id
        '''

        db1.cur.execute('SELECT id FROM '+self.tableName+' WHERE basename = ? LIMIT 1',(name,))

        try:
            (id,) = db1.cur.fetchone()
        except:
            id=None

        return id

    def lookupName(self,id):
        '''PathToBasenameOrgTable Class
        given id, return name
        '''

        db1.cur.execute('SELECT basename FROM '+self.tableName+' WHERE id = ? LIMIT 1',(id,))

        try:
            (name,) = db1.cur.fetchone()
        except:
            name=None

        return name

class BasenameOrgTable(BasenameTable):
    def __init__(self):
        '''BasenameOrgTable Class'''

        BasenameTable.__init__(self,'basenameOrg')

class BasenameNonOrgTable(BasenameTable):
    def __init__(self):
        '''BasenameNonOrgTable Class'''

        BasenameTable.__init__(self,'basenameNonOrg')

#head
class SymlinksTable():
    def __init__(self,tableName):
        '''SymlinksTable Class
        '''

        self.tableName=tableName

    def createTable(self,filenameAPsTable,myFilesTable):
        '''SymlinksTable Class
        '''

        self.filenameAPsTable=filenameAPsTable
        self.myFilesTable=myFilesTable

        # a symlink is treated as just a filenameAP string
        # do you want a column for isBroken?  seems like it would be out of date?
        # use this table to attempt to repair a missing file; it could be a moved/deleted symlink

        db1.cur.execute('CREATE TABLE IF NOT EXISTS '+self.tableName+' (symlink_id INTEGER UNIQUE NOT NULL,target_id INTEGER NOT NULL,FOREIGN KEY(symlink_id) REFERENCES '+self.filenameAPsTable.tableName+'(id),FOREIGN KEY(target_id) REFERENCES '+self.myFilesTable.tableName+'(id),UNIQUE(symlink_id,target_id))')

    def addSymlink(self,symlinkName,targetFileObj):
        '''SymlinksTable Class'''

        assert not targetFileObj.inHeader, 'script attempting database operation on file from header link'
        symlinkName_id=self.filenameAPsTable.lookupID(symlinkName)
        assert symlinkName_id, 'symlink name %s not found in table %s' % (symlinkName,self.filenameAPsTable.tableName)

        assert targetFileObj.myFilesTableID, 'targetFileObj lacks myFilesTableID'
        target_id=targetFileObj.myFilesTableID

        db1.cur.execute('INSERT OR IGNORE INTO '+self.tableName+' (symlink_id,target_id) VALUES (?,?)',(symlinkName_id,target_id))

        db1.conn.commit()

        logging.debug('added record in table %s for symlink %s pointing at id %s in table myOrgFiles' % (self.tableName,symlinkName,targetFileObj.myFilesTableID))

    def lookupTarget(self,symlinkName):
        '''SymlinksTable Class'''

        symlinkName_id=self.filenameAPsTable.lookupID(symlinkName)

        assert symlinkName_id, 'symlinkName %s not in %s' % (symlinkName,self.filenameAPsTable.tableName)

        db1.cur.execute('SELECT target_id FROM '+self.tableName+' WHERE symlink_id = ? LIMIT 1',(symlinkName_id,))

        try:
            (id,) = db1.cur.fetchone()
        except:
            id=None

        return id

    def lookupSymlinks(self,targetFileObj):
        '''SymlinksTable Class
        given a target name, return a result set of the symlinks that point to that target
        result set is in form of tuple of tuples
        '''
        assert not targetFileObj.inHeader, 'script attempting database operation on file from header link'
        assert targetFileObj.myFilesTableID, 'targetFileObj lacks myOrgFilesID'

        target_id=targetFileObj.myFilesTableID

        db1.cur.execute('SELECT symlink_id FROM '+self.tableName+' WHERE target_id = ?',(target_id,))

        try:
            ids = db1.cur.fetchall()
        except:
            # ids=((None,),)  #tuple of tuples
            ids=None

        if ids:
            #convert tuple of tuples of ids into list of filenames
            filenameList=[self.filenameAPsTable.lookupName(a[0]) for a in ids]
        else:
            filenameList=[]

        return filenameList

    def removeSymlinkByName(self,symlinkName):
        '''SymlinksTable Class
        was thinking this is for when symlink file is deleted, but you could still use the info
        in trying to repair a link?
        '''
        pass

    def removeSymlinksByTarget(self,targetFileObj):
        '''SymlinksTable Class
        was thinking this is for when symlink file is deleted, but you could still use the info
        in trying to repair a link?
        '''
        assert not targetFileObj.inHeader, 'script attempting database operation on file from header link'
        pass

class SymlinksOrgTable(SymlinksTable):
    def __init__(self):

        SymlinksTable.__init__(self,'symlinksOrg')

class SymlinksNonOrgTable(SymlinksTable):
    def __init__(self):

        SymlinksTable.__init__(self,'symlinksNonOrg')

#head
class LinksToTable():
    def __init__(self,tableName,targetClass):
        '''LinksToTable Class'''

        self.tableName=tableName
        self.targetClass=targetClass

        assert (targetClass in [OrgFile,NonOrgFile]),'targetClass is not one of OrgFile, NonOrgFile'

    def createTable(self,sourceTable,targetTable):
        '''LinksToTable Class'''

        #this is not symlinks; this is which org file contains a link to which other org files
        #TODO should ON DELETE CASCADE be used here?
        #isBroken means would link work in org mode

        self.sourceTable=sourceTable
        self.targetTable=targetTable

        db1.cur.execute('CREATE TABLE IF NOT EXISTS '+self.tableName+' (from_id INTEGER NOT NULL, to_id INTEGER NOT NULL, isBroken INTEGER, FOREIGN KEY(from_id) REFERENCES '+self.sourceTable.tableName+'(id), FOREIGN KEY(to_id) REFERENCES '+self.targetTable.tableName+'(id), UNIQUE(from_id,to_id))')

    def addLink(self,fromFile,toFile):
        '''LinksToTable Class'''
        assert isinstance(fromFile,OrgFile),'fromFile is not of Class OrgFile'
        assert isinstance(toFile,self.targetClass), 'toFile is not of class %s' % self.targetClass
        assert fromFile.myFilesTableID,'fromFile lacks myFilesTableID'
        assert toFile.myFilesTableID,'toFile lacks myFilesTableID'

        fromFile.testIfExists()
        toFile.testIfExists()

        if fromFile.exists and toFile.exists:
            isBroken=0
        else:
            isBroken=1

        logging.debug('adding link to table %s with fromFile %s and toFile %s' % (self.tableName,fromFile.filenameAP,toFile.filenameAP))

        db1.cur.execute('INSERT OR IGNORE INTO '+self.tableName+' (from_id,to_id,isBroken) VALUES (?,?,?)',(fromFile.myFilesTableID,toFile.myFilesTableID,isBroken))

        db1.conn.commit()

    def updateLinkStatus(self,fromFile,toFile):
        '''LinksToTable Class'''
        assert isinstance(fromFile,OrgFile),'fromFile is not of Class OrgFile'
        assert isinstance(toFile,self.targetClass), 'toFile is not of class %s' % self.targetClass
        assert fromFile.myFilesTableID,'fromFile lacks myFilesTableID'
        assert toFile.myFilesTableID,'toFile lacks myFilesTableID'

        fromFile.testIfExists()
        toFile.testIfExists()

        if fromFile.exists and toFile.exists:
            isBroken=0
        else:
            isBroken=1

        logging.debug('updating isBroken in %s to %s for fromFile %s and toFile %s' % (self.tableName,isBroken,fromFile.filenameAP,toFile.filenameAP))

        db1.cur.execute('UPDATE '+self.tableName+' SET isBroken=? WHERE from_id=? AND to_id=?',(isBroken,fromFile.myFilesTableID,toFile.myFilesTableID))

        db1.conn.commit()

    def removeEntriesMatchingFromFile(self,fromFile):
        '''LinksToTable Class'''

        assert isinstance(fromFile,OrgFile),'fromFile is not of Class OrgFile'
        assert fromFile.myFilesTableID, 'fromFile lacks myFilesTableID'

        db1.cur.execute('DELETE FROM '+self.tableName+' WHERE from_id = ?',(fromFile.myFilesTableID,))
        db1.conn.commit()

        logging.debug('removed all entries in %s where link originates from %s' % (self.tableName,fromFile.filenameAP))

    def makeListOfFilesAFileLinksTo(self,fromFile):
        '''LinksToTable Class'''

        assert isinstance(fromFile,OrgFile),'fromFile %s is not of Class OrgFile' % fromFile.filenameAP
        assert fromFile.myFilesTableID,'fromFile %s lacks myFilesTableID' % fromFile.filenameAP

        db1.cur.execute('SELECT to_id FROM '+self.tableName+' WHERE from_id = ?',(fromFile.myFilesTableID,))

        try:
            ids = db1.cur.fetchall()
        except:
            # ids=((None,),)  #tuple of tuples
            ids=None

        if ids:
            #convert tuple of tuples of ids into list of filenames
            retList=[self.targetTable.constructFileFromTable(a[0]) for a in ids]
        else:
            retList=None

        return retList

class LinksToOrgTable(LinksToTable):
    def __init__(self):

        LinksToTable.__init__(self,'linksToOrg',OrgFile)

    def makeListOfFilesThatLinkToAFile(self,orgFile):
        '''LinksToOrgTable Class
        given an org file, use database to make a list of org files that link to it
        '''
        #this method is restricted to looking files that link to an org file because there is no need in this script for making a list of files that link to a non-org file

        assert isinstance(orgFile,OrgFile), "org file must be of class OrgFile; %s is not" % orgFile.filenameAP
        assert orgFile.myFilesTableID, "org file must be in table myOrgFiles; %s is not" % orgFile.filenameAP

        db1.cur.execute('SELECT from_id FROM '+self.tableName+' WHERE to_id = ?',(orgFile.myFilesTableID,))

        try:
            ids = db1.cur.fetchall()
        except:
            # ids=((None,),)  #tuple of tuples
            ids=None

        if ids:
            #convert tuple of tuples of ids into list of filenames
            orgFileList=[db1.myOrgFilesTable.constructFileFromTable(a[0]) for a in ids]
        else:
            orgFileList=None

        return orgFileList

class LinksToNonOrgTable(LinksToTable):
    def __init__(self):

        LinksToTable.__init__(self,'linksToNonOrg',NonOrgFile)

#head
class PreviousFilenamesTable():
    def __init__(self,tableName):
        '''PreviousFilenamesTable Class'''

        self.tableName=tableName

    def createTable(self,myFilesTable,filenameAPsTable):
        '''PreviousFilenamesTable Class'''
        # purpose: keeping track of repairedlinks, so can do the same fix again without searching filesystem
        # what is UNIQUE here?  it's possible for user to do the same name changes again
        # TODO sqlite maybe can add entries to this table automatically with triggers; see zetcode sqlite tutorial

        #timeOfChange refers to the time when the prev filename is discovered to have become outdated

        self.myFilesTable=myFilesTable
        self.filenameAPsTable=filenameAPsTable

        db1.cur.execute('CREATE TABLE IF NOT EXISTS '+self.tableName+' (myFiles_id INTEGER NOT NULL, prevFilenameAP_id INTEGER NOT NULL, timeOfChange INTEGER, FOREIGN KEY(myFiles_id) REFERENCES '+self.myFilesTable.tableName+'(id), FOREIGN KEY(prevFilenameAP_id) REFERENCES '+self.filenameAPsTable.tableName+'(id), UNIQUE(myFiles_id,prevFilenameAP_id,timeOfChange))')

    def addRecord(self,file1,oldName,myFilesTableID=None):
        '''PreviousFilenamesTable Class'''

        # this table is problematic: only add to it when discover and repair a broken link
        # the time doesn't reflect when the actual change took place; just tells when a broken link was fixed

        if oldName==file1.filenameAP:
            return None  #TODO seems like method should log a warning or ?

        if not myFilesTableID:
            myFilesTableID=file1.myFilesTableID

        assert myFilesTableID, 'lacking myFilesTableID'

        oldName_id=self.filenameAPsTable.lookupID(oldName)

        assert oldName_id, 'no filenamesAPTable id found for old name'

        argList=['myFiles_id','prevFilenameAP_id','timeOfChange']
        argDict1={a:None for a in argList}  #dictionary comprehension
        argDict1['myFiles_id']=myFilesTableID
        argDict1['prevFilenameAP_id']=oldName_id
        argDict1['timeOfChange']=int(time.time())

        valList=[argDict1[a] for a in argList]  #list comprehension
        valTuple=tuple(a for a in valList)  #google: tuple comprehension; simply making a tuple from a list

        db1.cur.execute('INSERT OR IGNORE INTO '+self.tableName+' (myFiles_id, prevFilenameAP_id, timeOfChange) VALUES (?,?,?)',valTuple)

        db1.conn.commit()

        logging.debug('adding previous name %s to table %s for %s, which has id %s in table %s' % (oldName,self.tableName,file1.filenameAP,file1.myFilesTableID,file1.myFilesTable.tableName))

    def lookupUsing_OldName(self,oldName):
        '''PreviousFilenamesTable Class
        most recently, oldName was the previous filenameAP of myFiles_id
        '''

        oldName_id=self.filenameAPsTable.lookupID(oldName)

        assert oldName_id, 'oldName %s is not in self.filenameAPsTable' % oldName
 
        db1.cur.execute('SELECT timeOfChange,myFiles_id FROM '+self.tableName+' WHERE prevFilenameAP_id = ?',(oldName_id,))

        try:
            ret = db1.cur.fetchall()
        except:
            return None

        if ret:
            #sort tuple of tuples by timeOfChange ascending
            retSorted=sorted(ret,reverse=True)
            return retSorted[0][1]

    def lookupOldNames(self,file1):
        '''PreviousFilenamesTable Class
        '''

        assert file1.myFilesTableID, 'lacking file1.myFilesTableID'

        db1.cur.execute('SELECT prevFilenameAP_id FROM '+self.tableName+' WHERE myFiles_id = ?',(file1.myFilesTableID,))

        try:
            ids = db1.cur.fetchall()
        except:
            # ids=((None,),)  #tuple of tuples
            ids=None

        if ids:
            #convert tuple of tuples of ids into list of filenames
            filenameList=[self.filenameAPsTable.lookupName(a[0]) for a in ids]
        else:
            filenameList=None

        return filenameList

class PreviousFilenamesOrgTable(PreviousFilenamesTable):
    def __init__(self):
        '''PreviousFilenamesOrgTable Class'''

        PreviousFilenamesTable.__init__(self,'previousFilenamesOrg')

class PreviousFilenamesNonOrgTable(PreviousFilenamesTable):
    def __init__(self):
        '''PreviousFilenamesNonOrgTable Class'''

        PreviousFilenamesTable.__init__(self,'previousFilenamesNonOrg')

#head
#head
#head  Classes for links found in org files
class Link():
    '''
    a general link in an org file
    may or may not have brackets
    this is intended to be a base class; not intending to have any instances of this class in use
    '''

    #this one matches both [[link][description]] and [[link]]

    orgLinkWBracketsRegex=re.compile(r'(\[\[(?P<link>.+?)(?:\]\[(?P<description>.*?))?\]\])')  #a link in org mode; 20160926 brief googling indicates sometimes a URL can contain an asterisk

    #non-capturing version
    #see splitting strings in regular expression HOWTO by A.M. Kuchling; outermost parens are required for splitting operation in Node class
    orgLinkWBracketsRegexNC=re.compile(r'(\[\[(?:.+?)(?:\]\[(?:.*?))?\]\])')  #a version that allows asterisks in link; 20160926 brief googling indicates sometimes a URL can contain an asterisk

    def __init__(self,text,inHeader,sourceFile,hasBrackets):
        '''
        Link Class
        '''
        self.text=text  #text is the whole thing including brackets: [[link][description]] or [[link]]
        self.inHeader=inHeader #was this link found in machine-generated header of an org file?
        self.sourceFile=sourceFile  #link is found inside this file, which must be .org
        self.hasBrackets=hasBrackets

        #TODO hasBrackets could be confusing; this code does not add brackets or remove brackets

        matchObjBrackets=self.orgLinkWBracketsRegex.match(text)
        if hasBrackets:
            assert matchObjBrackets, 'link with text %s does not have brackets, but __init__ was called with hasBrackets set to True' % text
            self.link=matchObjBrackets.group('link')  #[[link][description]] or [[link]]
            #when there is no description, self.description will be None, as verified in ipython
            self.description=matchObjBrackets.group('description')  #[[link][description]]
            if self.link.startswith(' ') or self.link.endswith(' '):  #sometimes have a typo with leading or trailing space
                if '::' not in self.link: #link does not end with a search term
                    self.link=self.link.strip()
                    self.regenTextFromLinkAndDescription()
                else: #link ends with a search term; do not want to remove trailing spaces since they matter to search
                    if self.link.startswith(' '):
                        self.link=self.link.lstrip()
                        self.regenTextFromLinkAndDescription()

        else:
            assert (not matchObjBrackets), 'link with text %s has brackets, but __init__ was called with hasBrackets set to False' % text
            self.link=self.text
            self.description=None

        self.originalText=self.text
        self.originalLink=self.link
        self.originalDescription=self.description

        if sourceFile<>None:  #need to be able to tolerate None in order to do unit testing
            assert isinstance(sourceFile,OrgFile),'sourceFile is not of class OrgFile'

        #initialize
        self.targetObjList=[]  #list of target objects a link gets over its repair process, most recent last
        self.nodeWhereFound=None
        self.targetObj=None

    def associateWNode(self,Node):
        '''
        Link Class        
        connect a link to the node in the org file where it's found
        one purpose: be able to generate a clickable link to that node
        '''
        self.nodeWhereFound=Node

    def associateWTargetObj(self,myTargetObj):
        '''
        Link Class
        in this script, the target of an org mode link
        is often represented by a user defined object
        '''
        self.targetObj=myTargetObj
        #targetObjList is intended to record the various target objects this link references over the course of repairing it; it does not mean a link with wildcard * matching multiple files at once
        self.targetObjList.append(myTargetObj)  #most recent last

    def regenTextFromLinkAndDescription(self):
        '''
        Link Class
        suppose self.link and or self.description have been changed
        regen self.text
        '''

        #TODO current code does not consider the case where link initially has no brackets and a description is added

        if self.hasBrackets:
            if self.description:
                self.regenDescription()
                self.text='[['+self.link+']['+self.description+']]'
            else:
                self.text='[['+self.link+']]'
        else:
            self.text=self.link

    def regenDescription(self):
        '''
        Link Class
        LinkToLocalFile.regenDescription does things, but Link.regenDescription does not
        '''
        pass

class LinkToLocalFile(Link):
    '''
    a link in an org file, to another file on local disk
    this class is intended to be a base class; not intending for any instances to be in use
    Use subclass LinkToOrgFile for org file
    for all others use subclass LinkToNonOrgFile
    '''

    def __init__(self,text,inHeader,sourceFile,hasBrackets,regexForLink):
        '''
        LinkToLocalFile Class
        '''

        Link.__init__(self,text=text,inHeader=inHeader,sourceFile=sourceFile,hasBrackets=hasBrackets)

        self.regexForLink=regexForLink  #regex which identified link as a link to a local file; a compiled regex object; in [[link][description]], regexForLink applies to the link and not to the whole thing (text)
        self.matchObjForLink=regexForLink.match(self.link)

        self.preFilename=self.matchObjForLink.group('preFilename')  #named groups
        self.filename=self.matchObjForLink.group('filename')  #named groups
        self.postFilename=self.matchObjForLink.group('postFilename')  #named groups

        if self.filename != '/':  # if filename is not '/', which is root of filesystem
            #get rid of trailing slash; link should work just the same without it
            if self.filename.endswith('/'):
                self.filename=self.filename.rstrip('/')
                self.link=self.preFilename+self.filename+self.postFilename

                self.regenTextFromLinkAndDescription()

    def initTargetFile(self):
        '''
        LinkToLocalFile Class
        instantiating self.targetObj cleans up some filename issues,
        so need to regen self.link, self.text
        '''

        #TODO warning: this method is overwritten in LinkToOrgFile; use dive into python techniques to allow inheritance instead

        Link.associateWTargetObj(self,self.targetClassObj(self.filename,self.inHeader))  #target object is instantiated here
        self.originalTargetObj=self.targetObj
        self.__regenOnChangedFilenameAP()

    #head
    def testIfWorking(self):
        '''
        LinkToLocalFile Class
        test if this link would work in org mode
        i.e. if you clicked on it in org mode, would it bring up the target
        '''

        if self.targetObj.testIfExists():  #TODO this assumes all symlinks have been replaced with their targets
            return True
        else:
            return False

    #head  fixing broken link
    def regenDescription(self):
        '''LinkToLocalFile
        a first problem: a link is repaired and there was a description and it was
        the old filename; need to come up with new description because old description no longer makes sense

        a second problem: visible text (description) can get too long; shorten it if possible
        '''
        try:
            fileB=self.targetObj
        except AttributeError:
            return None

        if self.description:
            try:
                oldFileB=self.originalTargetObj
            except AttributeError:
                return None

            if fileB.filenameAP != oldFileB.filenameAP:
                filenameAPChanged=True
            else:
                filenameAPChanged=False

            if os.path.basename(fileB.filenameAP) != os.path.basename(oldFileB.filenameAP):
                basenameChanged=True
            else:
                basenameChanged=False

            if basenameChanged and (not filenameAPChanged):
                logging.error('Programming logic error: not possible for filenameAP to be unchanged but basename to be changed')

            #it is possible for filenameAP to change but basename to remain the same

            #making no changes to a very long description unless it has lost its meaning; assuming user intends it to be very long

            oldBasename=os.path.basename(oldFileB.filenameAP)

            if self.description==oldBasename:
                if basenameChanged:
                    self.description=os.path.basename(fileB.filenameAP)

                    if len(self.description)>maxLengthOfVisibleLinkText:
                        logging.warning('Basename %s is longer than max visible link text %s' % (os.path.basename(fileB.filenameAP),maxLengthOfVisibleLinkText))
                    return None
                else:
                    #description still makes sense, so leave it alone
                    return None

            if self.description==oldFileB.filenameAP:
                if filenameAPChanged:
                    if len(fileB.filenameAP)<=maxLengthOfVisibleLinkText:
                        self.description=fileB.filenameAP
                        return None

                    self.description=os.path.basename(fileB.filenameAP)
                    if len(self.description)>maxLengthOfVisibleLinkText:
                        logging.warning('Basename %s is longer than max visible link text %s' % (os.path.basename(fileB.filenameAP),maxLengthOfVisibleLinkText))
                    return None
                else:
                    #description still makes sense, so leave it alone
                    return None

            if self.description==os.path.basename(oldFileB.filenameAP):
                if basenameChanged:
                    if len(fileB.filenameAP)<=maxLengthOfVisibleLinkText:
                        self.description=fileB.filenameAP
                        return None

                    self.description=os.path.basename(fileB.filenameAP)        
                    if len(self.description)>maxLengthOfVisibleLinkText:
                        logging.warning('Basename %s is longer than max visible link text %s' % (os.path.basename(fileB.filenameAP),maxLengthOfVisibleLinkText))

                    return None
                else:
                    #description still makes sense, so leave it alone
                    return None

        #if there was no description, no need to add one

    def __regenOnChangedFilenameAP(self):
        '''
        LinkToLocalFile Class
        filenameAP refers to self.targetObj.filenameAP
        '''

        # note: child class will not be able to call this function since it starts with __
        self.filename=self.targetObj.filenameAP
        self.link=self.preFilename+self.filename+self.postFilename
        self.regenDescription()
        self.regenTextFromLinkAndDescription()

    def changeTargetObj(self,newFileObj):
        '''
        LinkToLocalFile Class
        '''

        assert not self.inHeader, 'unwanted operation on link in header'

        self.targetObj=newFileObj
        self.targetObjList.append(newFileObj) #most recent last
        #in the following, filenameAP refers to self.targetObj.filenameAP:
        self.__regenOnChangedFilenameAP()  #TODO does __ cause trouble with child classes using changeTargetObj?
        self.testIfWorking()

    #head
    def attemptRepairViaBasenameMatchOnDisk(self,basenameToUse=None,transform1=False):
        '''
        LinkToLocalFile Class
        simple repair attempt: assume file was moved but basename was unchanged
        choose the most recently-modified file with matching basename
        '''

        assert not self.inHeader, 'unwanted operation for link in header'

        fileB=self.targetObj

        assert not fileB.exists, 'link with target %s is working; expected broken link' % fileB.filenameAP

        # originalFileB=self.originalTargetObj

        if not basenameToUse:
            basenameB=os.path.basename(fileB.filenameAP)
        else:
            basenameB=basenameToUse

        if not transform1:
            logging.debug('attempting repair of %s by looking for the basename %s via bash find' % (fileB.filenameAP,basenameB))
        else:
            #http://stackoverflow.com/questions/11768070/transform-url-string-into-normal-string-in-python-20-to-space-etc
            filenameAP2=urllib2.unquote(fileB.filenameAP)
            basenameB=os.path.basename(filenameAP2)
            logging.debug('attempting repair of %s by first transforming it to %s, and then looking for the basename %s via bash find' % (fileB.filenameAP,filenameAP2,basenameB))

        if os.path.splitext(basenameB)[-1]:  #file has a file extension e.g. .org
            filenameAPMatchList=find_all_name_matches_via_bash(basenameB)  #requires linux and bash shell; this will not find directories
        else:  #there is no file extension; assume fileB is a directory
            filenameAPMatchList=find_all_name_matches_via_bash_for_directories(basenameB)  #requires linux and bash shell; this finds directories

        if filenameAPMatchList:
            if len(filenameAPMatchList)>1:
                logging.debug('%s matches found for basename %s (LinkToLocalFile.attemptRepairViaBasenameMatchOnDisk)' % (len(filenameAPMatchList),basenameB))
                logging.debug('Choosing %s to repair %s based on latest modification time' % (filenameAPMatchList[-1],fileB.filenameAP))
            else:
                logging.debug('Choosing %s to repair %s' % (filenameAPMatchList[-1],fileB.filenameAP))
            foundFilenameAP=filenameAPMatchList[-1]  #choose one with most recent modification time
        else:
            # logging.debug('no replacement found for %s via walking files on disk and looking for name match' % fileB.filenameAP)
            logging.debug('no replacement found for %s via looking for %s with bash find' % (fileB.filenameAP,basenameB))

            return None

        foundFile=fileB.__class__(foundFilenameAP,False)

        if self.__class__.__name__=='LinkToOrgFile':
            foundFile.uniqueIDFromHeader=fileB.uniqueIDFromHeader
        foundFile.inHeader=fileB.inHeader

        return self.finishRepairViaFoundFile(foundFile,'attemptRepairViaBasenameMatchOnDisk',self.myFilesTable.lookupID_UsingName)

    def attemptRepairViaPastUserRepairs(self):
        '''
        LinkToLocalFile Class
        a dictionary is saved to csv file on disk
        it contains previous link repairs performed interactively with user
        '''

        assert not self.inHeader, 'unwanted operation for link in header'

        fileB=self.targetObj

        assert not fileB.exists, 'link with target %s is working; expected broken link' % fileB.filenameAP

        # originalFileB=self.originalTargetObj

        if fileB.filenameAP not in pastInteractiveRepairs.keys():
            logging.debug('Cannot repair %s via dictionary of previous user interactive repairs' % fileB.filenameAP)
            return None

        logging.debug('%s is found in keys of dictionary of previous user interactive repairs' % fileB.filenameAP)
        foundFilenameAP=pastInteractiveRepairs[fileB.filenameAP]

        assert foundFilenameAP != 'UserChoseToSkipRepairingThis', 'Program logic error: should have weeded out this link as user chose to skip repairing it'

        foundFile=fileB.__class__(foundFilenameAP,False)

        if not foundFile.exists:
            logging.debug('Cannot repair %s via dictionary of previous user interactive repairs since matching entry %s does not exist on disk' % (fileB.filenameAP,foundFile.filenameAP))
            pastInteractiveRepairs.pop(fileB.filenameAP)
            return None

        if self.__class__.__name__=='LinkToOrgFile':
            foundFile.uniqueIDFromHeader=fileB.uniqueIDFromHeader
        foundFile.inHeader=fileB.inHeader

        return self.finishRepairViaFoundFile(foundFile,'attemptRepairViaPastUserRepairs',self.myFilesTable.lookupID_UsingName)

    #head
    def attemptRepairViaInteractingWithUser(self):
        '''
        as a last resort, interact with user in console
        to either attempt repair or leave link as-is
        '''

        assert not self.inHeader, 'unwanted operation for link in header'

        fileA=self.sourceFile

        fileB=self.targetObj

        basenameB=os.path.basename(fileB.filenameAP)

        assert not fileB.exists, 'link with target %s is working; expected broken link' % fileB.filenameAP

        if fileB.filenameAP.endswith('.org'):
            assert not fileB.uniqueID, 'Missing file: cannot have looked inside it for unique ID'
            assert not fileB.uniqueIDFromHeader, 'When unique ID is known from header, attemptRepairViaInteractingWithUser should not be performed'
            assert not fileB.uniqueIDFromDatabase, 'Missing file with database entry having unique ID: attemptRepairViaInteractingWithUser should not be performed'
        # originalFileB=self.originalTargetObj

        logging.debug('attempting repair of %s via interacting with user in console' % fileB.filenameAP)

        numOfRemainingBrokenLinks=len([a for a in fileA.linksToNonOrgFilesList if not a.targetObj.exists])+len([a for a in fileA.linksToOrgFilesList if not a.targetObj.exists])

        #obtaining lock is required when feature to quit spidering on hitting enter key is enabled
        #20160912 pudb appears to still work; checked with 20160912ThreadingExample04.py
        with keyboardInputLock:
            menu1='''
            Now in mode for interactively fixing links in org file %s.
            Automatic routines have failed to fix these links.
            There are %s broken links remaining in org file %s.

            Broken link is %s.

            Enter what to do next:
            1) skip manually fixing this link
            2) skip manually fixing all links in org file %s
            3) quit processing this file and make no changes to it.  if you are spidering, this will end spidering run.
            
            Or try to fix the link:
            Enter more than one character to provide a pattern to search for file on disk by name
            example entry to repair a broken link to an org file: *unix*org
            ''' % (fileA.filenameAP,numOfRemainingBrokenLinks,fileA.filenameAP,fileB.filenameAP,fileA.filenameAP)

            maxNCandidates=25

            while True:
                userChoice1=raw_input(menu1)
                if userChoice1=='1':  #skip repair of this link
                    logging.debug('User chose to skip manual repair of %s' % fileB.filenameAP)
                    pastInteractiveRepairs[fileB.filenameAP]='UserChoseToSkipRepairingThis'
                    return None
                elif userChoice1=='2':  #skip repair of all outward links of org file
                    fileA.userManuallyFixesMyOutgoingLinks=False
                    logging.debug('User chose to skip manual repair of all broken links in %s' % fileA.filenameAP)
                    return None
                elif userChoice1=='3':
                    logging.info('User chose to quit spidering while manually repairing link %s in %s' % (fileB.filenameAP,fileA.filenameAP))
                    return 'Quit'
                elif fileB.filenameAP.endswith('.org') and not (userChoice1.endswith('*org') or userChoice1.endswith('.org')):
                    print 'For repairing a broken link to .org file, please provide a search term ending in *org or .org\n'
                    continue  #show user menu1 again
                elif len(userChoice1)>1:  #user entered a search term for repair

                    if os.path.splitext(basenameB)[-1]:  #file has a file extension e.g. .org
                        repairCandidates=find_all_name_matches_via_bash(userChoice1)  #requires linux and bash shell; this will not find directories
                    else:  #there is no file extension; assume fileB is a directory
                        repairCandidates=find_all_name_matches_via_bash_for_directories(userChoice1)  #requires linux and bash shell; this finds directories

                    if not repairCandidates:
                        print 'No matches found for search term %s' % userChoice1
                        logging.debug('No matches found for search term %s in manual repair attempt of %s' % (userChoice1,fileB.filenameAP))
                        continue  #show user menu1 again

                    #eliminate wrong hits
                    if fileB.filenameAP.endswith('.org'):
                        #knock out matches like .organic, .organism, etc
                        repairCandidates2=[a for a in repairCandidates if a.endswith('.org')]
                    else:
                        repairCandidates2=repairCandidates

                    # repairCandidates3=[OrgFile(a,False) for a in repairCandidates2]
                    repairCandidates3=[fileB.__class__(a,False) for a in repairCandidates2]  #list of file objects corresponding to list of filenameAPs

                    if fileB.filenameAP.endswith('.org'):
                        [a.lookInsideForUniqueID for a in repairCandidates3]

                        onesWUniqueIDs=[a for a in repairCandidates3 if a.uniqueID]

                        if onesWUniqueIDs:
                            messg1='%s of %s remaining viable matches contain a unique ID and are therefore discarded' % (len(onesWUniqueIDs),len(repairCandidates2))
                            print messg1
                            logging.debug(messg1)
                            repairCandidates4=[a for a in repairCandidates3 if not a.uniqueID]
                        else:
                            repairCandidates4=repairCandidates3
                    else:
                        repairCandidates4=repairCandidates3

                    #throw out matches which can be found in database; oops this seems to be too restrictive
                    # matchesInDatabase=[a for a in repairCandidates4 if self.myFilesTable.lookupID_UsingName(a)]
                    # if matchesInDatabase:
                    #     messg1='%s of %s remaining viable matches are found in database by name and are therefore discarded' % (len(matchesInDatabase),len(repairCandidates4))
                    #     print messg1
                    #     logging.debug(messg1)

                    #     repairCandidates5=[a for a in repairCandidates4 if not a in matchesInDatabase]
                    # else:
                    #     repairCandidates5=repairCandidates4

                    #discard ones with repeat filenameAP; repeat filenameAP is due to symlinks and to how my file object classes are designed
                    filenameAPs4=[a.filenameAP for a in repairCandidates4]
                    # http://stackoverflow.com/questions/7961363/removing-duplicates-in-lists  answer by Richard Fredlund 20140605
                    repairCandidates5=[f1 for n,f1 in enumerate(repairCandidates4) if f1.filenameAP not in filenameAPs4[:n]]

                    if len(repairCandidates5)>maxNCandidates:
                        print 'Too many valid matches found for search term %s (%s found which exceeds allowable %s)' % (userChoice1,len(repairCandidates5),maxNCandidates)
                        logging.debug('Too many valid matches found for search term %s (%s found which exceeds allowable %s) in repair attempt of %s' % (userChoice1,len(repairCandidates),maxNCandidates,fileB.filenameAP))
                        continue  #show user menu1 again

                    print 'Now printing out the valid choices for repair of %s' % fileB.filenameAP

                    ret=user_chooses_element_from_list_or_rejects_all([a.filenameAP for a in repairCandidates5],nameOfElementInList='repair',doubleSpaced=True)
                    if 'None of the above' in ret[1]:
                        continue  #user did not like any repair choices; show user menu1 again
                    else:
                        print 'You chose %s\n' % ret[1]

                        fileForRepair=repairCandidates5[ret[0]]

                        #put successful user interactive repairs in a dictionary that is stored on disk with something other than sqlite database
                        pastInteractiveRepairs[fileB.filenameAP]=fileForRepair.filenameAP  #can assign a different value than already exists in dictionary; no problem
                            
                        return self.finishRepairViaFoundFile(fileForRepair,'attemptRepairViaInteractingWithUser',self.myFilesTable.lookupID_UsingName)

                else:
                    print 'Your reply %s was unusable because it is not 1, 2, or more than 1 character in length\n' % userChoice1
                    continue

    #head
    def attemptRepairUsingSymlinksTable(self):
        '''
        LinkToLocalFile Class
        you have a link to a broken symlink
        look in table symlinksOrg for a file that the broken symlink used to point to
        '''
        fileB=self.targetObj

        #for a missing file which needs repair, you will not know if it is a symlink or not
        # if not (fileB.isSymlink or fileB.changedFromSymlinkToNonSymlink):
        #     logging.debug('%s is not a symlink and was not changed from a symlink to a non symlink in this script; skipping %s.attemptRepairUsingSymlinksTable' % (fileB.filenameAP,self.__class__.__name__))
        #     return 'notASymlink'

        assert not self.inHeader, 'unwanted operation for link in header'

        originalFileB=self.originalTargetObj

        assert not fileB.exists, '%s exists' % fileB.filenameAP

        logging.debug('attempting repair of %s via table %s' % (fileB.filenameAP,self.symlinksTable.tableName))

        idB=self.symlinksTable.lookupTarget(fileB.originalFilenameAP)

        if not idB:
            logging.debug('no replacement found in table %s' % self.symlinksTable.tableName)
            return "noDatabaseRecordFound"

        databaseMatchingFile=self.myFilesTable.constructFileFromTable(idB)
        return self.finishRepairViaDatabaseMatchingFile(databaseMatchingFile,'attemptRepairUsingSymlinksTable')

    def attemptRepairUsingTablePreviousFilenames(self):
        '''
        LinkToLocalFile Class
        try to repair a link to a missing file or to a broken symlink
        using database table previousFilenames
        '''

        assert not self.inHeader, 'unwanted operation for link in header'

        fileB=self.targetObj

        originalFileB=self.originalTargetObj

        assert not fileB.exists, '%s exists' % fileB.filenameAP

        logging.debug('attempting repair of %s via table %s' % (fileB.filenameAP,self.previousFilenamesTable.tableName))

        idB=self.previousFilenamesTable.lookupUsing_OldName(fileB.filenameAP)

        if not idB:
            logging.debug('no replacement found in table %s for repair of %s' % (self.previousFilenamesTable.tableName,fileB.filenameAP))
            return "noDatabaseRecordFound"

        databaseMatchingFile=self.myFilesTable.constructFileFromTable(idB)

        return self.finishRepairViaDatabaseMatchingFile(databaseMatchingFile,'attemptRepairUsingTablePreviousFilenames')

    def attemptRepairViaCheckDatabaseForNameMatch(self):
        '''
        LinkToLocalFile Class
        '''

        assert not self.inHeader, 'unwanted operation for link in header'

        fileB=self.targetObj

        assert not fileB.exists, '%s exists' % fileB.filenameAP

        logging.debug('attempting repair of %s via checking database for name match' % fileB.filenameAP)

        idB=self.myFilesTable.lookupID_UsingName(fileB)

        if not idB:
            logging.debug('no replacement found in table %s' % self.myFilesTable.tableName)
            return "noDatabaseRecordFound"

        databaseMatchingFile=self.myFilesTable.constructFileFromTable(idB)
        return self.finishRepairViaDatabaseMatchingFile(databaseMatchingFile,'attemptRepairViaCheckDatabaseForNameMatch')

    #head
    def finishRepairViaDatabaseMatchingFile(self,databaseMatchingFile,callerName):
        '''LinkToLocalFile Class'''

        fileB=self.targetObj

        if self.__class__.__name__=='LinkToOrgFile':
            databaseMatchingFile.uniqueIDFromHeader=fileB.uniqueIDFromHeader
        databaseMatchingFile.inHeader=fileB.inHeader

        originalFileB=self.originalTargetObj

        if not 'attemptRepairUsingSymlinks' in callerName:
            if (originalFileB.isSymlink or originalFileB.changedFromSymlinkToNonSymlink):
                self.symlinksTable.addSymlink(originalFileB.originalFilenameAP,databaseMatchingFile)

        self.previousFilenamesTable.addRecord(databaseMatchingFile,originalFileB.filenameAP)

        if databaseMatchingFile.exists:

            self.changeTargetObj(databaseMatchingFile)
            fileB=self.targetObj

            if self.__class__.__name__=='LinkToOrgFile':
                fileB.lookInsideForUniqueID()
                fileB.checkConsistencyOfThreeUniqueIDDataItems()  #expecting unique ID inside to match unique ID in database

            self.testIfWorking()  #this marks the link as working as well as the file

            self.myFilesTable.syncTableToFile(fileB)
            self.myFilesTable.zeroOutNumFailedRepairAttempts(fileB)
            logging.debug('working replacement found via %s' % callerName)
            self.databaseHousekeepingForWorkingLink()
            fileB.repaired=True
            fileB.repairedVia=callerName
            return "repaired"

        else:
            self.changeTargetObj(databaseMatchingFile)

            fileB=self.targetObj
            #check for max repair attempts

            if fileB.checkMaxRepairAttempts():
                logging.debug('did not attempt repair of link %s in file %s because database shows number of failed repair attempts %s, which exceeds allowable %s' % (fileB.filenameAP,self.sourceFile.filenameAP,fileB.numFailedRepairsFromDatabase,maxFailedRepairAttempts))
                self.databaseHousekeepingForBrokenLink()
                return 'databaseShowsMaxRepairAttempts'

            logging.debug('replacement found in database, but it is missing on disk; further repair attempts required (LinkToOrgFile.%s)' % callerName)
            return "databaseRecordIsAMissingFile"

    def finishRepairViaFoundFile(self,foundFile,callerName,tableLookupFun):
        '''LinkToLocalFile Class
        '''

        originalFileB=self.originalTargetObj

        self.changeTargetObj(foundFile)
        fileB=self.targetObj

        if self.__class__.__name__=='LinkToOrgFile':
            fileB.lookInsideForUniqueID()
            fileB.checkConsistencyOfThreeUniqueIDDataItems()

        if originalFileB.myFilesTableID:
            oldID=originalFileB.myFilesTableID
        else:
            try:
                oldID=tableLookupFun(originalFileB)
            except:
                oldID=None

        id=tableLookupFun(fileB)

        if oldID:
            #purpose of this is to prevent repair from ending up in a new table entry when it should replace an old table entry
            fileB.myFilesTableID=oldID
            self.myFilesTable.syncTableToFile(fileB)
            self.myFilesTable.zeroOutNumFailedRepairAttempts(fileB)
        elif id:
            fileB.myFilesTableID=id
            self.myFilesTable.syncTableToFile(fileB)
            self.myFilesTable.zeroOutNumFailedRepairAttempts(fileB)
        else:
            self.myFilesTable.addFile(fileB)

        if self.__class__.__name__=='LinkToOrgFile':
            fileB.checkConsistencyOfThreeUniqueIDDataItems()  #expecting unique ID inside to match unique ID in database

        if (originalFileB.isSymlink or originalFileB.changedFromSymlinkToNonSymlink):
            self.symlinksTable.addSymlink(originalFileB.originalFilenameAP,fileB)

        self.previousFilenamesTable.addRecord(fileB,originalFileB.filenameAP)

        self.testIfWorking()  #this marks the link as working as well as the file

        logging.debug('working replacement %s found for %s (%s.%s)' % (fileB.filenameAP,originalFileB.filenameAP,self.__class__.__name__,callerName))

        self.databaseHousekeepingForWorkingLink()

        fileB.repaired=True
        fileB.repairedVia=callerName

        return "repaired"

    #head
    def databaseHousekeepingForBrokenLink(self):
        '''
        LinkToLocalFile Class
        '''

        assert not self.inHeader, 'unwanted operation for link in header'

        fileB=self.targetObj

        assert not fileB.exists, 'file %s exists' % fileB.filenameAP

        idB=fileB.myFilesTableID

        if not idB:
            idB=self.myFilesTable.findBestMatchForMissingFile(fileB)
        if idB:
            fileB.myFilesTableID=idB
            self.myFilesTable.syncTableToFile(fileB)
        else:
            self.myFilesTable.addFile(fileB)  #this sets fileB.myFilesTableID

        if (fileB.isSymlink or fileB.changedFromSymlinkToNonSymlink):
            self.symlinksTable.addSymlink(fileB.originalFilenameAP,fileB)

        if self.__class__.__name__=='LinkToOrgFile':
            fileB.checkConsistencyOfThreeUniqueIDDataItems()

        self.linksTable.addLink(self.sourceFile,self.targetObj)
        self.linksTable.updateLinkStatus(self.sourceFile,self.targetObj)

    #head
    def giveUpOnRepairing(self):
        '''LinkToLocalFile
        some housekeeping tasks when giving up on repairing a link
        '''
        fileB=self.targetObj
        fileB.triedAndFailedToRepair=True  #TODO assumes a repair attempt was made in this run
        self.databaseHousekeepingForBrokenLink()
        fileB.myFilesTable.incrNumFailedRepairAttempts(fileB)

class LinkToNonOrgFile(LinkToLocalFile):
    '''
    a link in an org file, to another file (which is not org) on local disk
    '''

    #TODO update for brackets vs no brackets as in LinkToOrgFile

    # a dictionary of compiled regex objects; link is [[link][description]]

    linkRegexesBrackets={'file:anyFilename::anything or file+sys:anyFilename::anything or file+emacs:anyFilename::anything or docview:anyFilename::anything':re.compile(r'^(?P<preFilename>(?:file(?:(?:[+]sys)|(?:[+]emacs))?:)|(?:docview:))(?P<filename>[^@*]+?)(?P<postFilename>::.+)$')}
    linkRegexesBrackets['/anyFilename::anything  or  ./anyFilename::anything  or  ~/anyFilename::anything']=re.compile(r'^(?P<preFilename>)(?P<filename>[.~]?[/][^@*]+?)(?P<postFilename>::.+)$')
    linkRegexesBrackets['file:anyFilename or file+sys:anyFilename or file+emacs:anyFilename or docview:anyFilename']=re.compile(r'^(?P<preFilename>(?:file(?:(?:[+]sys)|(?:[+]emacs))?:)|(?:docview:))(?P<filename>[^@*]+$)(?P<postFilename>)')
    linkRegexesBrackets['/anyFilename  or  ./anyFilename  or  ~/anyFilename']=re.compile(r'^(?P<preFilename>)(?P<filename>[.~]?[/][^@*]+$)(?P<postFilename>)')

    linkRegexesNoBrackets={'file:anyFilename::anything or file+sys:anyFilename::anything or file+emacs:anyFilename::anything or docview:anyFilename::anything':re.compile(r'^(?P<preFilename>(?:file(?:(?:[+]sys)|(?:[+]emacs))?:)|(?:docview:))(?P<filename>[^@*]+?)(?P<postFilename>::.+)$')}
    linkRegexesNoBrackets['file:anyFilename or file+sys:anyFilename or file+emacs:anyFilename or docview:anyFilename']=re.compile(r'^(?P<preFilename>(?:file(?:(?:[+]sys)|(?:[+]emacs))?:)|(?:docview:))(?P<filename>[^@*]+$)(?P<postFilename>)')

    def __init__(self,text,inHeader,sourceFile,hasBrackets,regexForLink):
        '''
        LinkToNonOrgFile Class
        '''
        LinkToLocalFile.__init__(self,text=text,inHeader=inHeader,sourceFile=sourceFile,hasBrackets=hasBrackets,regexForLink=regexForLink)

        self.targetClassObj=NonOrgFile

        self.myFilesTable=db1.myNonOrgFilesTable
        self.filenameAPsTable=db1.filenameAPsNonOrgTable
        self.pathToBasenameTable=db1.pathToBasenameNonOrgTable
        self.basenameTable=db1.basenameNonOrgTable
        self.symlinksTable=db1.symlinksNonOrgTable
        self.linksTable=db1.linksToNonOrgTable
        self.previousFilenamesTable=db1.previousFilenamesNonOrgTable

    #head
    def databaseHousekeepingForWorkingLink(self):
        '''
        LinkToNonOrgFile Class
        '''

        assert not self.inHeader, 'unwanted operation for link in header'

        fileB=self.targetObj

        assert fileB.exists, 'file does not exist'

        idB=fileB.myFilesTableID

        if not idB:
            idB=self.myFilesTable.lookupID_UsingName(fileB)

        if idB:
            fileB.myFilesTableID=idB
            self.myFilesTable.syncTableToFile(fileB)
        else:
            self.myFilesTable.addFile(fileB)  #this sets fileB.myFilesTableID

        if (fileB.isSymlink or fileB.changedFromSymlinkToNonSymlink):
            self.symlinksTable.addSymlink(fileB.originalFilenameAP,fileB)

        self.myFilesTable.zeroOutNumFailedRepairAttempts(fileB)  #this field should already have been zero

        self.linksTable.addLink(self.sourceFile,self.targetObj)
        self.linksTable.updateLinkStatus(self.sourceFile,self.targetObj)

class LinkToOrgFile(LinkToLocalFile):
    '''a link in an org file, to another org file on local disk'''

    # a dictionary of compiled regex objects; link is [[link][description]]
    #using dictionary instead of list to make code easier to maintain
    #key is really long string but is descriptive

    #use 20160921TestAFewLinks.org to try out links in org mode
    #TODO you could also have blacklist regex: if a match, this is not a clickable link in org mode
    linkRegexesBrackets={'file:anyFilename.org::anything or file+sys:anyFilename.org::anything or file+emacs:anyFilename.org::anything or docview:anyFilename.org::anything':re.compile(r'^(?P<preFilename>(?:file(?:(?:[+]sys)|(?:[+]emacs))?:)|(?:docview:))(?P<filename>[^@*]+?[.]org)(?P<postFilename>::.+)$')}
    linkRegexesBrackets['/anyFilename.org::anything  or  ./anyFilename.org::anything  or  ~/anyFilename.org::anything']=re.compile(r'^(?P<preFilename>)(?P<filename>[.~]?[/][^@*]+?[.]org)(?P<postFilename>::.+)$')
    linkRegexesBrackets['file:anyFilename.org or file+sys:anyFilename.org or file+emacs:anyFilename.org or docview:anyFilename.org']=re.compile(r'^(?P<preFilename>(?:file(?:(?:[+]sys)|(?:[+]emacs))?:)|(?:docview:))(?P<filename>[^@*]+?[.]org$)(?P<postFilename>)')
    linkRegexesBrackets['/anyFilename.org  or  ./anyFilename.org  or  ~/anyFilename.org']=re.compile(r'^(?P<preFilename>)(?P<filename>[.~]?[/][^@*]+?[.]org$)(?P<postFilename>)')

    #TODO if no brackets, cannot have spaces; log an error
    linkRegexesNoBrackets={'file:anyFilename.org::anything or file+sys:anyFilename.org::anything or file+emacs:anyFilename.org::anything or docview:anyFilename.org::anything':re.compile(r'^(?P<preFilename>(?:file(?:(?:[+]sys)|(?:[+]emacs))?:)|(?:docview:))(?P<filename>[^@*]+?[.]org)(?P<postFilename>::.+)$')}
    linkRegexesNoBrackets['file:anyFilename.org or file+sys:anyFilename.org or file+emacs:anyFilename.org or docview:anyFilename.org']=re.compile(r'^(?P<preFilename>(?:file(?:(?:[+]sys)|(?:[+]emacs))?:)|(?:docview:))(?P<filename>[^@*]+?[.]org$)(?P<postFilename>)')

    #unique ID in header of self.sourceFile pertaining to this link is written differently than unique ID in status section of self.sourceFile
    #this makes it easy to find unique ID of an org file without making a full representation of it in this script
    myUniqueIDRegex=re.compile(r'#LinkUniqueID(?P<uniqueID>\d{4}-((0[1-9])|(1[0-2]))-((0[1-9])|([1-2][0-9])|(3[0-1]))_((0[1-9])|(1[0-9])|(2[0-4]))-((0[0-9])|([1-5][0-9]))-((0[0-9])|([1-5][0-9]))-\d{4})')

    def __init__(self,text,inHeader,sourceFile,hasBrackets,regexForLink):
        '''LinkToOrgFileClass
        sourceFile is the org file where link resides
        '''
        LinkToLocalFile.__init__(self,text=text,inHeader=inHeader,sourceFile=sourceFile,hasBrackets=hasBrackets,regexForLink=regexForLink)

        self.targetClassObj=OrgFile

        self.myFilesTable=db1.myOrgFilesTable
        self.filenameAPsTable=db1.filenameAPsOrgTable
        self.pathToBasenameTable=db1.pathToBasenameOrgTable
        self.basenameTable=db1.basenameOrgTable
        self.symlinksTable=db1.symlinksOrgTable
        self.linksTable=db1.linksToOrgTable
        self.previousFilenamesTable=db1.previousFilenamesOrgTable

    #head
    def attemptRepairByAddingMain(self):
        '''
        LinkToOrgFile Class
        attempt repair of broken link by adding Main to basename (name.org > nameMain.org)
        '''

        assert not self.inHeader, 'unwanted operation for link in header'

        fileB=self.targetObj

        assert not fileB.exists, 'link with target %s is working; expected broken link' % fileB.filenameAP

        # originalFileB=self.originalTargetObj

        logging.debug('attempting repair of %s by adding Main to basename (name.org > nameMain.org)' % fileB.filenameAP)

        basename1=os.path.basename(fileB.filenameAP)
        #.replace won't change basename1
        newBasename1=basename1.replace('.org','Main.org')

        filenameAPMatchList=find_all_name_matches_via_bash(newBasename1)  #requires linux

        if filenameAPMatchList:
            if len(filenameAPMatchList)>1:
                logging.warning('%s matches on disk for %s (LinkToOrgFile.attemptRepairByAddingMain)' % (len(filenameAPMatchList),newBasename1))
            foundFilenameAP=filenameAPMatchList[-1]  #choose one with most recent modification time
        else:
            # logging.debug('no replacement found for %s via walking files on disk and looking for name match' % fileB.filenameAP)
            logging.debug('no replacement found for %s via LinkToOrgFile.attemptRepairByAddingMain' % fileB.filenameAP)

            return None

        foundFile=OrgFile(foundFilenameAP,False)

        foundFile.uniqueIDFromHeader=fileB.uniqueIDFromHeader
        foundFile.inHeader=fileB.inHeader

        return self.finishRepairViaFoundFile(foundFile,'attemptRepairByAddingMain',self.myFilesTable.lookupID_UsingName)

    def attemptRepairByRemovingMain(self):
        '''
        LinkToOrgFile Class
        attempt repair of broken link by removing Main from basename (nameMain.org > name.org)
        '''

        assert not self.inHeader, 'unwanted operation for link in header'

        fileB=self.targetObj

        assert not fileB.exists, 'link with target %s is working; expected broken link' % fileB.filenameAP

        # originalFileB=self.originalTargetObj

        basename1=os.path.basename(fileB.filenameAP)

        if not basename1.endswith('Main.org'):
            return None

        logging.debug('attempting repair of %s by removing Main from basename (nameMain.org > name.org)' % fileB.filenameAP)

        #.replace won't change basename1
        newBasename1=basename1.replace('Main.org','.org')

        filenameAPMatchList=find_all_name_matches_via_bash(newBasename1)  #requires linux and bash shell

        if filenameAPMatchList:
            if len(filenameAPMatchList)>1:
                logging.warning('%s matches on disk for %s (LinkToOrgFile.attemptRepairByRemovingMain)' % (len(filenameAPMatchList),newBasename1))
            foundFilenameAP=filenameAPMatchList[-1]  #choose one with most recent modification time
        else:
            logging.debug('no replacement found for %s via LinkToOrgFile.attemptRepairByRemovingMain' % fileB.filenameAP)

            return None

        foundFile=OrgFile(foundFilenameAP,False)

        foundFile.uniqueIDFromHeader=fileB.uniqueIDFromHeader
        foundFile.inHeader=fileB.inHeader

        return self.finishRepairViaFoundFile(foundFile,'attemptRepairByRemovingMain',self.myFilesTable.lookupID_UsingName)

    #head
    def attemptRepairViaExpectedUniqueIDAndBashFind(self,expectedUniqueIDAttr='uniqueID',myName='attemptRepairViaExpectedUniqueIDAndBashFind'):
        '''
        LinkToOrgFile Class
        with list of files with same basename returned by bash find command, look inside each one and check if unique ID matches expected unique ID
        '''

        assert expectedUniqueIDAttr in ('uniqueID','uniqueIDFromHeader','uniqueIDFromDatabase'), 'unknown expectedUniqueIDAttr'

        assert not self.inHeader, 'unwanted operation for link in header'

        fileB=self.targetObj

        expectedUniqueID=getattr(fileB,expectedUniqueIDAttr)

        assert expectedUniqueID, '%s is missing %s' % (fileB.filenameAP,expectedUniqueIDAttr)

        assert not fileB.exists, 'link with target %s is working; expected broken link' % fileB.filenameAP

        logging.debug('attempting repair of %s by getting list of files with same basename via bash find, and looking inside them for desired unique ID %s' % (fileB.filenameAP,expectedUniqueID))

        filenameAPMatchList=find_all_name_matches_via_bash(os.path.basename(fileB.filenameAP))  #requires linux and bash shell

        if not filenameAPMatchList:
            logging.debug('for %s, no files found on disk with same basename (linkB.attemptRepairViaExpectedUniqueIDAndBashFind)' % fileB.filenameAP)
            return None

        fileObjList=[OrgFile(a,False) for a in filenameAPMatchList]

        for orgFile in fileObjList:
            orgFile.lookInsideForUniqueID()
            if orgFile.uniqueID and orgFile.uniqueID==expectedUniqueID:
                return self.finishRepairViaFoundFile(orgFile,myName,db1.myOrgFilesTable.lookupID_UsingUniqueID)

        logging.debug('for %s, %s files were found on disk with same basename, but none contained expected unique ID %s (linkB.attemptRepairViaExpectedUniqueIDAndBashFind)' % (fileB.filenameAP,len(filenameAPMatchList),expectedUniqueID))

        return None

    def attemptRepairViaUniqueIDFromHeaderAndBashFind(self):
        '''
        LinkToOrgFile Class
        '''

        return self.attemptRepairViaExpectedUniqueIDAndBashFind('uniqueIDFromHeader','attemptRepairViaUniqueIDFromHeaderAndBashFind')

    def attemptRepairViaUniqueIDFromDatabaseAndBashFind(self):
        '''
        LinkToOrgFile Class
        '''

        return self.attemptRepairViaExpectedUniqueIDAndBashFind('uniqueIDFromDatabase','attemptRepairViaUniqueIDFromDatabaseAndBashFind')

    #head
    def attemptRepairUsingUniqueIDFromHeaderAndDatabase(self):
        '''
        LinkToOrgFile Class
        use unique ID from header to go into database and look for a working replacement
        '''

        assert not self.inHeader, 'unwanted operation for link in header'

        fileB=self.targetObj

        logging.debug('attempting repair of %s via unique ID from header and database' % fileB.filenameAP)

        assert not fileB.exists, 'link target %s exists' % fileB.filenameAP

        assert fileB.uniqueIDFromHeader, 'missing unique ID from header'

        idB=db1.myOrgFilesTable.lookupID_UsingUniqueIDFromHeader(fileB)

        #this is too restrictive; if database is lost, script will error out here
        # assert idB, 'unique ID from header does not lead to record in table myOrgFiles (LinkToOrgFile.attemptRepairUsingUniqueIDFromHeaderAndDatabase)'

        if not idB:
            return "noDatabaseRecordFound"

        databaseMatchingFile=db1.myOrgFilesTable.constructFileFromTable(idB)

        return self.finishRepairViaDatabaseMatchingFile(databaseMatchingFile,'attemptRepairUsingUniqueIDFromHeaderAndDatabase')

    #head
    def attemptRepairByLookingInsideFilesForUniqueID(self,expectedUniqueID):
        '''
        LinkToOrgFile Class
        repair a broken link by
        walking filesystem, opening files ending in .org and looking inside for a desired uniqueID
        save time by looking in database and only opening up files that are not already in database
        '''

        assert not self.inHeader, 'unwanted operation for link in header'

        fileB=self.targetObj

        assert not fileB.exists, '%s exists' % fileB.filenameAP

        originalFileB=self.originalTargetObj

        logging.debug('attempting repair of %s by walking files on disk and looking inside them for unique ID %s' % (fileB.filenameAP,expectedUniqueID))

        newOrgFile=walk_org_files_looking_for_unique_id_match(expectedUniqueID,fileB.filenameAP)

        if not newOrgFile:
            logging.debug('no replacement found for %s via walking files on disk and looking inside for unique ID (LinkToOrgFile.attemptRepairByLookingInsideFilesForUniqueID)' % fileB.filenameAP)
            return None

        return self.finishRepairViaFoundFile(newOrgFile,'attemptRepairByLookingInsideFilesForUniqueID',db1.myOrgFilesTable.lookupID_UsingUniqueID)

    #head
    def databaseHousekeepingForWorkingLink(self):
        '''
        LinkToOrgFile Class
        '''

        assert not self.inHeader, 'unwanted operation for link in header'

        fileB=self.targetObj

        assert fileB.exists, 'file does not exist'

        if not fileB.lookedInsideForUniqueID:
            fileB.lookInsideForUniqueID()

        fileB.checkConsistencyOfThreeUniqueIDDataItems()

        idB=fileB.myFilesTableID

        if not idB and fileB.uniqueID and not fileB.insertedUniqueID:  #if fileB contains a unique ID and this script did not just insert it
            idB=db1.myOrgFilesTable.findBestMatchForExistingFileUsingUniqueID(fileB)
        if not idB:
            idB=db1.myOrgFilesTable.lookupID_UsingName(fileB)

        if idB:
            fileB.myFilesTableID=idB
            db1.myOrgFilesTable.syncTableToFile(fileB)
        else:
            db1.myOrgFilesTable.addFile(fileB)  #this sets fileB.myFilesTableID

        if (fileB.isSymlink or fileB.changedFromSymlinkToNonSymlink):
            db1.symlinksOrgTable.addSymlink(fileB.originalFilenameAP,fileB)

        fileB.checkConsistencyOfThreeUniqueIDDataItems()
        db1.myOrgFilesTable.zeroOutNumFailedRepairAttempts(fileB)  #this field should already have been zero

        db1.linksToOrgTable.addLink(self.sourceFile,self.targetObj)
        db1.linksToOrgTable.updateLinkStatus(self.sourceFile,self.targetObj)

#head  Class for a node in an org file
class Node():
    '''
    Node Class
    input lines1 is the list of lines of this node and its descendants
    '''

    headerText1='* machine-generated indices;  READ ONLY'

    def __init__(self,lines,sourceFile,parent=None):
        '''Node Class'''

        #lines is the list of lines for this node and its descendants; this sets up a recursive scheme
        self.lines=lines  #see self.myLines below
        self.sourceFile=sourceFile

        assert parent==None or isinstance(parent,Node), 'parent of Node must be either None or a Node'

        self.parent=parent

        self.inHeader=False  #this node is in machine-generated header; don't want database, logging performed on header material

        if parent and parent.inHeader:
            self.inHeader=True
        else:
            if lines[0].startswith(Node.headerText1):
                self.inHeader=True

        #self.level is the number of asterisks at start of first line of a node

        self.level=get_asterisk_level(lines[0])
        assert self.level >= 1, 'a node must begin with at least one asterisk'

        self.myLines,self.descendantLines=separate_parent_lines_descendant_lines(lines)

        #recursive scheme in action
        if self.descendantLines:
            self.childNodeList=list_of_child_nodes_from_lines(lines=self.descendantLines,sourceFile=self.sourceFile,parent=self)
        else:
            self.childNodeList=[]

        self.uniqueID=None

        '''Node Class'''

        self.makeTagList()

        #self.myLines[1:] are the blurb of a Node; will evaluate to empty list if myLines is just one line
        self.blurb=self.myLines[1:]

        #initialize several lists of links of interest
        self.linksToOrgFiles=[]
        self.linksToNonOrgFiles=[]

        #make a dictionary d1 to connect link regexes to lists of links
        #TODO would look cleaner to have class as key instead of link regex, but quick google search suggests accomplishing this is more trouble than it's worth?
        d1Brackets={a:self.linksToOrgFiles for a in LinkToOrgFile.linkRegexesBrackets.values()}  #dictionary comprehension
        d2Brackets={a:self.linksToNonOrgFiles for a in LinkToNonOrgFile.linkRegexesBrackets.values()}  #dictionary comprehension
        d1Brackets.update(d2Brackets)

        d1NoBrackets={a:self.linksToOrgFiles for a in LinkToOrgFile.linkRegexesNoBrackets.values()}  #dictionary comprehension
        d2NoBrackets={a:self.linksToNonOrgFiles for a in LinkToNonOrgFile.linkRegexesNoBrackets.values()}  #dictionary comprehension
        d1NoBrackets.update(d2NoBrackets)

        self.lineLists=[]  #a list for each line in self.myLines
        count=0
        for line in self.myLines:
            # logging.debug('Node.__init__: processing line %s' % line)
            if count>maxLinesInANodeToAnalyze:
                # do not want script hanging forever on very long blurbs where author of org file has pasted in arbitrary raw text that might confuse this script and make it hang
                # TODO do not want to split line on ' ' since that could mess up tabs or other stuff?
                self.lineLists.append([line])
                count+=1
                continue

            lineList1=line_to_list1(line)  # ['some text ','[[a link with brackets]]',' more text ','[[another link with brackets][description]]','.']; see orgFixLinksTests.py

            lineList2=[]
            for piece in lineList1:
                if Link.orgLinkWBracketsRegexNC.match(piece):  #piece is [[link]] or [[link][description]]
                    link1,description=text_to_link_and_description_double_brackets(piece)

                    link=remove_tilde_from_org_link(link1)

                    piece2=text_from_link_and_description(link,description,hasBrackets=True)

                    #based on which regex matches link, create a link object and add it to lineList2
                    matchingRegex,matchObj,matchingClass=find_best_regex_match_for_text(link,hasBrackets=True)

                    if matchingRegex: #if there is a match
                        lineList2.append(matchingClass(text=piece2,inHeader=self.inHeader,sourceFile=self.sourceFile,hasBrackets=True,regexForLink=matchingRegex))  #creating instance of e.g. LinkToOrgFile
                        lineList2[-1].associateWNode(self)
                        d1Brackets[matchingRegex].append(lineList2[-1])  #d1Brackets[matchingRegex] is the appropriate self.listOfLinks
                        lineList2[-1].initTargetFile()  #create instance of target of this link
                        lineList2[-1].testIfWorking()
                        continue  #go to next piece in line
                    else:
                        lineList2.append(piece)  #since link does not match any regex, leave this piece as text TODO does this cause any issue in regenAfterLinkUpdates?
                        continue  #go to next piece in line
                else:  #piece does not include [[link]] or [[link][description]], but might include a link without brackets
                    pieceList=split_on_non_whitespace_keep_everything(piece)
                    for each1 in pieceList:  #here we are looking for links without brackets
                        matchingRegex,matchObj,matchingClass=find_best_regex_match_for_text(each1,hasBrackets=False)

                        if matchingRegex: #if there is a match

                            if each1.endswith('.org~'):
                                link1=remove_tilde_from_org_link(each1)
                                matchingRegex,matchObj,matchingClass=find_best_regex_match_for_text(link1,hasBrackets=False)
                            else:
                                link1=each1

                            foundLink=matchingClass(text=link1,inHeader=self.inHeader,sourceFile=self.sourceFile,hasBrackets=False,regexForLink=matchingRegex)
                            lineList2.append(foundLink)
                            foundLink.associateWNode(self)  # assuming this will update the object in lineList2
                            d1NoBrackets[matchingRegex].append(foundLink)  #d1NoBrackets[matchingRegex] is the appropriate self.listOfLinks
                            foundLink.initTargetFile()  #create instance of target of this link
                            foundLink.testIfWorking()
                        else:
                            lineList2.append(each1)
            self.lineLists.append(lineList2)
            count+=1
    #head
    def regenAfterLinkUpdates(self):
        '''
        Node Class
        after link objects are updated/revised, regeneration is required
        '''

        assert not self.inHeader, 'unwanted method call on node in machine-generated header'

        listOfStringsForEachLine=[]
        for lineList in self.lineLists:
            list1=[]  #list of strings that make up this line of text
            for item in lineList:
                #item is either a string or an instance of a Link or one of its descendant classes
                if isinstance(item,types.StringType):
                    list1.append(item)
                else:
                    list1.append(item.text)
            listOfStringsForEachLine.append(list1)

        self.myLines=[''.join(a) for a in listOfStringsForEachLine]  #self.myLines is regenerated

        # TODO I don't think self.descendantLines is getting regenerated from self.linelists.
        # TODO is it necessary to get this working in this script?
        # TODO is it desirable to recursively regenerate all the descendant nodes?  maybe just wanted to regen self?
        if self.descendantLines:
            self.lines=self.myLines+self.descendantLines
        else:
            self.lines=self.myLines
        self.blurb=self.myLines[1:]
    #head
    def makeTagList(self):
        '''
        form list of tags
        list of tags, which can only be found on self.myLines[0]
        because a blurb cannot have tags in org mode
        '''
        self.tags=[]

        if self.myLines[0].split()[-1].startswith(':') and self.myLines[0].split()[-1].endswith(':'): 
            #self.tags is list of strings
            self.tags=self.myLines[0].split()[-1].split(':')[1:-1]

        if self.tags:
            if [a for a in self.tags if a.isupper()]:  #if any tags are all uppercase
                #change tags that are all uppercase to all lowercase
                tags2=[all_upper_to_all_lowercase(a) for a in self.tags]
                self.tags=tags2

                b=self.myLines[0].split()
                c=':'+':'.join(tags2)+':'
                self.myLines[0]=' '.join(b[:-1]+[c,'\n'])

    #head
    def findUniqueID(self,uniqueIDRegexObj):
        '''
        Node Class
        a unique ID for an outgoing link in an org file is found in a node, in the first line of the blurb
        '''

        if self.blurb:
            a=uniqueIDRegexObj.search(self.blurb[0])
            if a:
                self.uniqueID=a.group('uniqueID')

    def addUniqueID(self,uniqueIDLine):
        '''
        Node Class
        this is for adding unique ID to status node of file A
        this is for adding unique ID to header
        uniqueIDLine for status node looks like: #MyUniqueID2016-12-25_23-59-59-1234 
        uniqueIDLine for header looks like: #LinkUniqueID2016-12-25_23-59-59-1234 
        '''

        assert not self.uniqueID, 'node already has a unique ID'

        #throw an error if uniqueIDLine does not match one of LinkToOrgFile.myUniqueIDRegex, OrgFile.myUniqueIDRegex
        matchObjList=[LinkToOrgFile.myUniqueIDRegex.match(uniqueIDLine),OrgFile.myUniqueIDRegex.match(uniqueIDLine)]  #first is unique ID for header; second is uniqueID for status node
        matches=[a for a in matchObjList if a]
        assert len(matches)==1,'%s does not match exactly one of LinkToOrgFile.myUniqueIDRegex, OrgFile.myUniqueIDRegex' % uniqueIDLine

        matchObj=matches[0]
        uniqueIDInLine=matchObj.group('uniqueID')

        #TODO if this method operates on a header node, why is the following here?
        # assert not self.inHeader, 'unwanted method call on node from link found in machine-generated header'

        #TODO seems like good idea to check that node is a status node?  or a header node?  raise error or log an error if not.

        self.lines.insert(1,uniqueIDLine)
        #TODO do not understand why unit test indicates the following line must be commented out; checked in orgFixLinksTests that separate_parent_lines_descendant_lines does not automatically update when a new line is added
        # self.myLines.insert(1,uniqueIDLine)
        self.blurb.insert(0,uniqueIDLine)
        self.lineLists.insert(1,split_on_non_whitespace_keep_everything(uniqueIDLine))
        self.uniqueID=uniqueIDInLine

#head  Classes for files on local disk
class LocalFile():
    def __init__(self,filename1,inHeader,myFilesTable,symlinksTable,previousFilenamesTable,leaveAsSymlink=False):
        '''LocalFile Class
        this is a parent class; script is expected to use only the child classes NonOrgFile, OrgFile
        input leaveAsSymlink is for test purposes only
        '''

        #seeing problems in ipython with ~ character and filenames
        # http://stackoverflow.com/questions/2313053/python-how-to-access-linux-paths
        if filename1.startswith('~'):
            filename1=os.path.expanduser(filename1)

        self.originalFilename=filename1
        logging.debug('original filename is %s' % self.originalFilename)
        self.inHeader=inHeader

        self.myFilesTable=myFilesTable
        self.symlinksTable=symlinksTable
        self.previousFilenamesTable=previousFilenamesTable

        self.leaveAsSymlink=leaveAsSymlink

        #TODO want to turn off logging for files in header, but need to test that this code is actually working; is commented out for now
        if self.inHeader:
            pass
            #turn_off_logging()
        else:
            pass
            #turn_logging_back_on_at_initial_level()

        self.changedFromSymlinkToNonSymlink=False #initialize

        #TODO why is this commented out?  is it because filename1 is not necessarily absolute path, so path1 might be unusable?
        #in many cases, this script is analyzing org files that have been moved, so a relative link in such an org file will no longer make sense
        #TODO why not write a test in orgFixLinksTests that figures out what is going on
        # path1=os.path.split(filename1)[0]
        # folder1=os.getcwd()
        # os.chdir(path1)

        #caution this command wrecks filename if current working directory is not the folder where file is
        self.filenameAP=os.path.abspath(filename1)
        self.originalFilenameAP=self.filenameAP
        logging.debug('original filenameAP is %s' % self.filenameAP)  
        # os.chdir(folder1)

        #the following deals with: self.exists, self.isSymlink, self.targetFilenameAP, self.targetExists, self.orgLinkToMeWouldWork
        #and self.isBrokenSymlink
        self.testIfExistsSymlinkVersion()

        self.originalTargetFilenameAP=self.targetFilenameAP
        logging.debug('original targetFilenameAP is %s' % self.targetFilenameAP)  

        if not leaveAsSymlink:
            #to simplify this script, replace symlinks with their targets
            self.changeFromSymlinkToNonSymlink()

        self.simpleClickableLink='file:'+self.filenameAP  #simple clickable link in org mode

        #initialize:
        self.triedAndFailedToRepair=False  #this flag says all repairs have been attempted
        self.repaired=False  #repair was attempted and succeeded
        self.repairedVia=None  #name of method used to repair broken link to this file; string or None
        self.numFailedRepairsFromDatabase=None

        self.addedToDatabase=False  #did script just add this file to the database?
        self.myFilesTableID=None

    #head
    def testIfExists(self):
        '''LocalFile Class
        use this function when ignoring symlinks and just working with the file itself in case of non-symlink and missing file,
        and target of symlink when symlink is not broken
        '''

        if self.inHeader:
            #turn_off_logging()
            pass

        self.exists=os.path.exists(self.filenameAP)
        logging.debug('os.path.exists returns %s for self.filenameAP of %s' % (self.exists,self.filenameAP))

        #turn_logging_back_on_at_initial_level()

        return self.exists

    def testIfExistsSymlinkVersion(self):
        '''LocalFile Class
        this function can deal with both symlinks and non-symlinks
        my definition of exists is a little different than os.path.exists
        if a symlink is broken, it can still be said to exist even though its target is missing
        '''

        if self.inHeader:
            #turn_off_logging()
            pass

        #only use this function at certain times; see scheme for working with symlinks
        assert not self.changedFromSymlinkToNonSymlink, 'do not use this function once changed from symlink to non-symlink'

        logging.debug('Carrying out LocalFile.testIfExistsSymlinkVersion on %s' % self.filenameAP)

        #initialize; None means unknown or not applicable
        self.targetFilenameAP=None
        self.targetExists=None
        self.isSymlink=None
        self.isBrokenSymlink=None

        if os.path.exists(self.filenameAP):
            self.exists=True
            logging.debug('%s exists (os.path.exists)' % self.filenameAP)
            if os.path.islink(self.filenameAP):
                logging.debug('%s is a symlink' % self.filenameAP)
                self.isSymlink=True
                self.targetFilenameAP=os.path.realpath(self.filenameAP)
                logging.debug('%s is symlink target (os.path.realpath)' % self.targetFilenameAP)
                if os.path.exists(self.targetFilenameAP):
                    self.targetExists=True
                    logging.debug('symlink target %s exists (os.path.exists)' % self.targetFilenameAP)
                else:
                    self.targetExists=False
                    logging.debug('symlink target %s does not exist (os.path.exists)' % self.targetFilenameAP)
            else:
                self.isSymlink=False
                logging.debug('%s is not a symlink' % self.filenameAP)
                # self.targetFilenameAP=self.filenameAP  #a convention used in this script
                # self.targetExists=True  #would rather have a value of None for an existing file which is not a symlink
        else:
            #either the file is missing, or it is a broken symlink
            if os.path.islink(self.filenameAP):
                #file must be a broken symlink
                self.isSymlink=True
                self.exists=True
                self.targetExists=False
                #a broken symlink still contains the name of its target
                self.targetFilenameAP=os.path.realpath(self.filenameAP)
                logging.debug('%s is a symlink that is found on disk, with a missing target %s; self.exists is set to %s' % (self.filenameAP,self.targetFilenameAP,self.exists))
            else:
                logging.debug('%s is missing; cannot tell if it is a symlink or not' % self.filenameAP)
                self.exists=False

        if self.isSymlink:
            if self.targetExists:
                self.isBrokenSymlink=False
            else:
                self.isBrokenSymlink=True
        elif self.exists:
            self.isBrokenSymlink=False
        else:
            #it is unknown if a missing file is a symlink or not, so leave self.isBrokenSymlink at default value of None
            pass

        #turn_logging_back_on_at_initial_level()

        return self.exists

    #head
    def readLines(self):

        f1=open(self.filenameAP,'r')
 
        self.oldLines=f1.readlines()
        f1.close()

    #head
    def changeFromSymlinkToNonSymlink(self):
        '''LocalFile Class'''

        if self.leaveAsSymlink:
            logging.warning('Changing %s from symlink to non symlink despite self.leaveAsSymlink being set to True' % self.filenameAP)

        if self.inHeader:
            #turn_off_logging()
            pass

        if self.exists and self.isSymlink:  #cannot tell if a missing file is a symlink or not
            logging.debug('changing %s from symlink to non-symlink' % self.filenameAP)
            self.filenameAP=os.path.realpath(self.targetFilenameAP)  #want to be able to use the same code for all cases; TODO what if file was a symlink pointing to a symlink?
            logging.debug('self.filenameAP becomes %s, which was the symlink target' % self.filenameAP)
            self.changedFromSymlinkToNonSymlink=True

            self.isSymlink=False  #TODO what if file was a symlink pointing to a symlink?

            #TODO what if file was a symlink pointing to a symlink?
            # self.isBrokenSymlink=False #file is not a symlink; was changed to its target
            # self.targetFilenameAP=None  #a non-symlink has no target; inapplicable
            # self.targetExists=None  #a non-symlink has no target; inapplicable
            del self.isBrokenSymlink
            del self.targetFilenameAP
            del self.targetExists

            self.simpleClickableLink='file:'+self.filenameAP  #simple clickable link in org mode

            self.testIfExists()

        #turn_logging_back_on_at_initial_level()

    def changeBackToSymlink(self):
        '''LocalFile Class'''
        #TODO go back to file as a symlink
        #see accompanying org file for this project

        #TODO assert not self.leaveAsSymlink

        assert self.changedFromSymlinkToNonSymlink, 'file was not changed from symlink to non symlink'

        if self.inHeader:
            #turn_off_logging()
            pass

        #TODO fill in
        # self.testIfExistsSymlinkVersion()

        #turn_logging_back_on_at_initial_level()

    #head
    def checkMaxRepairAttempts(self):
        '''
        LocalFile Class
        '''

        assert not self.inHeader, 'unwanted method call on file from link in machine-generated header'

        assert self.myFilesTableID, 'cannot check number of failed repair attempts for %s because have not found it in table myOrgFiles' % self.filenameAP

        self.numFailedRepairsFromDatabase=self.myFilesTable.lookupNumFailedRepairAttemptsByID(self.myFilesTableID)

        assert (type(self.numFailedRepairsFromDatabase)==int and self.numFailedRepairsFromDatabase>=0), 'lookup in table myOrgFiles for %s gives %s, which is invalid value' % (self.filenameAP,self.numFailedRepairsFromDatabase)

        if self.numFailedRepairsFromDatabase>=maxFailedRepairAttempts:  #have repair attempts been maxed out
            logging.debug('number of failed repair attempts %s is greater than or equal to allowable %s for %s at id %s in table %s' % (self.numFailedRepairsFromDatabase,maxFailedRepairAttempts,self.filenameAP,self.myFilesTableID,self.myFilesTable.tableName))
            return True
        else:
            logging.debug('number of failed repair attempts %s is less than allowable %s for %s at id %s in table %s' % (self.numFailedRepairsFromDatabase,maxFailedRepairAttempts,self.filenameAP,self.myFilesTableID,self.myFilesTable.tableName))
            return False

    #head
    def changeToMyDirectory(self):
        '''
        LocalFile Class
        '''
        myDir=os.path.split(self.filenameAP)[0]
        os.chdir(myDir)
        return myDir

class NonOrgFile(LocalFile):
    def __init__(self,filename1,inHeader,leaveAsSymlink=False):
        '''input leaveAsSymlink is for test purposes only'''
        LocalFile.__init__(self,filename1,inHeader,db1.myNonOrgFilesTable,db1.symlinksNonOrgTable,db1.previousFilenamesNonOrgTable,leaveAsSymlink=leaveAsSymlink)

        if not self.inHeader:
            db1.addFilenameToThreeNonOrgTables(self.filenameAP)
            db1.addFilenameToThreeNonOrgTables(self.originalFilenameAP)
            db1.addFilenameToThreeNonOrgTables(self.originalTargetFilenameAP)

        #turn_logging_back_on_at_initial_level()

class OrgFile(LocalFile):
    #regex for finding unique ID in an org file; uses group named uniqueID
    #this unique ID is found only in blurb of mainline node having text status and level of 1 (one asterisk)
    myUniqueIDRegex=re.compile(r'#MyUniqueID(?P<uniqueID>\d{4}-((0[1-9])|(1[0-2]))-((0[1-9])|([1-2][0-9])|(3[0-1]))_((0[1-9])|(1[0-9])|(2[0-4]))-((0[0-9])|([1-5][0-9]))-((0[0-9])|([1-5][0-9]))-\d{4})')

    def __init__(self,filename1,inHeader,leaveAsSymlink=False):
        '''
        OrgFile Class
        initialize this object with minimal attributes.
        createFullRepresentation is for org files that are to be rewritten.
        input leaveAsSymlink is for test purposes only
        '''

        # logging.debug('Creating OrgFile instance with filename %s' % filename1)

        LocalFile.__init__(self,filename1,inHeader,db1.myOrgFilesTable,db1.symlinksOrgTable,db1.previousFilenamesOrgTable,leaveAsSymlink=leaveAsSymlink)

        if not self.inHeader:
            db1.addFilenameToThreeOrgTables(self.filenameAP)
            db1.addFilenameToThreeOrgTables(self.originalFilenameAP)
            db1.addFilenameToThreeOrgTables(self.originalTargetFilenameAP)

        self.leaveAsSymlink=leaveAsSymlink

        self.fullRepresentation=False

        self.uniqueID=None  #unique ID inside this file
        self.uniqueIDFromHeader=None  #header node in another org file indicates this file should have this unique ID
        self.uniqueIDFromDatabase=None  #a database lookup indicates this file should have this unique ID

        #in this run, has script looked inside this file for a unique ID?
        self.lookedInsideForUniqueID=False

        #in this run, has script added unique ID to this file (only done when file does not already contain one)?
        self.insertedUniqueID=False

        self.userManuallyFixesMyOutgoingLinks=True  #when True, user is prompted by script to manually fix outgoing links

        self.recentlyFullyAnalyzed=None  #unknown; a database lookup will determine if this org file was recently analyzed

        #outgoing links
        #list of objects; order of list is same order as links appear in file
        #these lists are for body nodes, not for machine-generated header node
        self.linksToOrgFilesList=[]
        self.linksToNonOrgFilesList=[]

        self.tagList=[]

        self.orgFilesThatLinkToMe=[]

        #turn_logging_back_on_at_initial_level()

    def endsInDotOrg(self):
        return os.path.splitext(self.filenameAP)[-1] == '.org' 

    #head
    def createFullRepresentation(self):
        '''
        OrgFile Class
        represent org file as list of Node objects
        this function is called once for a particular OrgFile instance.  do not use it more than once.
        Need a full representation of an org file being rewritten/revised.
        Do not necessarily need a full representation of org files being linked to but not rewritten.         
        '''

        assert not self.inHeader, 'unwanted method call on file from link in machine-generated header'
        assert self.exists, '%s does not exist; cannot create full representation' % self.filenameAP

        logging.debug('creating full representation of %s' % self.filenameAP)

        self.readLines()

        self.createNodeRepresentation()

        #this will recursively walk the body mainline Nodes and their descendant Nodes
        #and add node links and tags to my lists
        self.traverseNodesToFillLists(self.bodyMainlineNodes)

        logging.debug('finished creating full representation of %s' % self.filenameAP)
        logging.info('Initial state of links')
        logging.info('%s has %s outgoing links to org files, of which %s are initially broken' % (self.filenameAP,len(self.linksToOrgFilesList),len([a for a in self.linksToOrgFilesList if not a.targetObj.exists])))
        logging.info('%s has %s outgoing links to non-org files, of which %s are initially broken\n' % (self.filenameAP,len(self.linksToNonOrgFilesList),len([a for a in self.linksToNonOrgFilesList if not a.targetObj.exists])))
        self.fullRepresentation=True

        self.lookInsideForUniqueID()  #self.uniqueID could still be None

    #head
    def createNodeRepresentation(self):
        #list of Node objects representing mainline (* ) nodes
        #this recursively creates a representation of an org file as a tree-like structure of Node objects
        #each Node has a list of its own child Nodes
        #each Node may contain Links, which point to Files
        self.mainlineNodes=list_of_child_nodes_from_lines(self.oldLines,self)

        if not self.mainlineNodes:
            raise OrgFileLacksMainlineNodesError

        #is the first mainline node the machine-generated list of indices?
        #machine-generated means generated by this script.
        #only the header node and its descendants are machine-generated.
        #they must be processed differently.

        self.oldHeaderLines=[]
        self.oldBodyLines=[]

        headerText1=Node.headerText1
        if self.mainlineNodes[0].myLines[0].startswith(headerText1):
            # logging.debug('%s already has machine-generated header section' % self.filenameAP)
            self.oldLinesHaveHeader=True

            self.headerMainlineNode=self.mainlineNodes[0]
            self.bodyMainlineNodes=self.mainlineNodes[1:]

            traverse_nodes_to_recover_line_list(self.mainlineNodes[0],self.oldHeaderLines)
        else:
            # logging.debug('%s does not have machine-generated header section' % self.filenameAP)
            self.oldLinesHaveHeader=False
            self.headerMainlineNode=None
            # self.bodyMainlineNodes=self.mainlineNodes  #tricky python language behavior: a change to self.mainlineNodes can automatically happen to self.bodyMainlineNodes
            self.bodyMainlineNodes=self.mainlineNodes[:]

        traverse_nodes_to_recover_line_list(self.bodyMainlineNodes,self.oldBodyLines)

        #either identify the existing status node, or create one and insert it
        self.statusNode=None  #not a Boolean variable
        self.statusNode=traverse_nodes_to_reach_desired_node(self.bodyMainlineNodes,'status',maxLevel=1)

        if (not self.statusNode):
            self.statusNode=Node(['* status\n'],sourceFile=self)

            if self.headerMainlineNode:
                self.mainlineNodes.insert(1,self.statusNode)  #insert status node after header node
            else:
                self.mainlineNodes.insert(0,self.statusNode)
                # logging.debug('no status node detected for %s; inserted a new one' % self.filenameAP)
            self.bodyMainlineNodes.insert(0,self.statusNode)

    #head
    def traverseNodesToFillLists(self,nodeList1):
        ''' a function that enables
        a recursive walk of a tree of Nodes belonging to an OrgFile,
        for the purpose of populating lists of links belonging to the OrgFile.
        nodeList is intended to be a subset of the nodes of an OrgFile.
        '''
        
        nodeList=make_list_of(nodeList1)
        
        for aNode in nodeList:
            self.addNodeLinksAndTagsToMyLists(aNode)
            self.traverseNodesToFillLists(aNode.childNodeList)

    def addNodeLinksAndTagsToMyLists(self,aNode):
        '''
        OrgFile Class
        given a Node, add its links and tags to my lists
        '''

        assert not self.inHeader, 'unwanted method call on file from link in machine-generated header'

        self.linksToNonOrgFilesList.extend(aNode.linksToNonOrgFiles)
        self.linksToOrgFilesList.extend(aNode.linksToOrgFiles)
        self.tagList.extend(aNode.tags)

    #head
    def lookInsideForUniqueID(self):
        '''OrgFile Class'''

        assert not self.inHeader, 'unwanted method call on file from link in machine-generated header'

        self.uniqueID=None

        if self.fullRepresentation:
            if self.statusNode:
                self.statusNode.findUniqueID(OrgFile.myUniqueIDRegex)
                if self.statusNode.uniqueID:
                    self.uniqueID=self.statusNode.uniqueID
                    logging.debug('inspected status node of %s using full representation data structure and detected unique ID %s' % (self.filenameAP,self.uniqueID))
                else:
                    logging.debug('inspected status node of %s using full representation data structure and did not detect a unique ID' % self.filenameAP)
            else:
                logging.debug('%s does not have a status node; no unique ID found' % self.filenameAP)
        else:
            self.uniqueID=find_unique_id_inside_org_file(self.filenameAP)

        self.lookedInsideForUniqueID=True

        return self.uniqueID

    def generateAndInsertMyUniqueID(self):
        '''
        OrgFile Class
        must be consistent with Orgfile.myUniqueIDRegex, LinkToOrgFile.myUniqueIDRegex'''

        assert not self.inHeader, 'unwanted method call on file from link in machine-generated header'

        if self.uniqueID:
            logging.warning('call placed to generateAndInsertMyUniqueID for %s but uniqueID already set' % self.filenameAP)
        else:
            assert self.fullRepresentation, 'generateAndInsertMyUniqueID called for %s but createFullRepresentation was never carried out' % self.filenameAP

            self.uniqueID=datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'-'+rand_int_as_string(4)

            assert self.statusNode, 'generateAndInsertMyUniqueID called for %s but status node was never added' % self.filenameAP
            self.statusNode.addUniqueID('#MyUniqueID'+self.uniqueID+'\n')

            logging.debug('added unique ID %s to %s via full representation' % (self.uniqueID,self.filenameAP))
            self.insertedUniqueID=True

        #TODO write code to insert a unique ID into a file without a full node representation?  need to add it after a machine-generated header section
        #simple: just add a status node to the end of the file followed by the blurb line with unique ID

    #head
    def addUniqueIDsFromHeaderToOutgoingOrgLinkTargets(self):
        '''
        OrgFile Class
        add unique IDs stored in header nodes to target objects of link objects in body nodes
        '''

        #go into header node and descendants and get uniqueIDs 'on file' for links to org files
        #header node and descendants contain text with the unique IDs
        #add unique IDs to link objects, if link target is the same file

        assert not self.inHeader, 'unwanted method call on file from link in machine-generated header'

        if self.fullRepresentation and self.headerMainlineNode:  #if this OrgFile contains a machine-generated header node
            node0=traverse_nodes_to_reach_desired_node(self.headerMainlineNode,'list of links',maxLevel=2)
            #TODO is it an error if header does not have list of links?
            node1=traverse_nodes_to_reach_desired_node(node0,'outgoing links to org files',maxLevel=3)
            if node1:
                for child in node1.childNodeList:
                    #each child node should contain an outgoing link to an org file, optionally followed by a blurb with unique ID
                    if child.blurb:
                        headerLinkUniqueID=None
                        #regex search inside first line of blurb for uniqueID text
                        b=LinkToOrgFile.myUniqueIDRegex.search(child.blurb[0])
                        if b:
                            #in this case there should be one and only one link; an instance of LinkToOrgFile
                            assert child.linksToOrgFiles[0], 'malformed Node in header of %s; lacks LinkToOrgFile object' % self.filenameAP
                            assert len(child.linksToOrgFiles)==1, 'malformed Node in header of %s; wrong number of LinkToOrgFile objects' % self.filenameAP

                            headerLink=child.linksToOrgFiles[0]
                            headerLinkUniqueID=b.group('uniqueID')
                            #TODO was it desirable to assign unique ID to an attribute of headerLink target object?

                            #go through body node links and assign unique IDs on file
                            for link1 in self.linksToOrgFilesList:  #for each body node link to an org file
                                if link1.targetObj.filenameAP==headerLink.targetObj.filenameAP:
                                    link1.targetObj.uniqueIDFromHeader=headerLinkUniqueID
            else:
                pass
                #TODO is it an error if header does not have section of outgoing links to org files?

    def checkConsistencyOfThreeUniqueIDDataItems(self):
        '''
        OrgFile Class
        detect any disagreement between
        self.uniqueID, self.uniqueIDFromHeader, self.uniqueIDFromDatabase
        '''

        #TODO can go back to more strict assert structure
        #if use blacklist: list of org files that are exempt from consistency check

        assert not self.inHeader, 'unwanted method call on file from link in machine-generated header'

        if self.lookedInsideForUniqueID and self.uniqueID:
            if self.uniqueIDFromHeader:
                # assert self.uniqueIDFromHeader == self.uniqueID, 'unique ID from header does not match unique ID inside file'
                if self.uniqueIDFromHeader != self.uniqueID:
                    logging.warning('unique ID from header does not match unique ID inside file %s' % self.filenameAP)

            if self.uniqueIDFromDatabase:
                if self.uniqueIDFromDatabase == self.uniqueID:
                    pass
                elif self.insertedUniqueID:
                    logging.warning('unique ID in database does not match newly inserted unique ID in %s; changing database value to match what is inside file' % self.filenameAP)
                    db1.myOrgFilesTable.updateUniqueID(self)
                    self.uniqueIDFromDatabase=self.uniqueID
                else:
                    # assert self.uniqueIDFromDatabase == self.uniqueID, 'unique ID from database does not match unique ID inside file'
                    if self.uniqueIDFromDatabase != self.uniqueID:
                        logging.warning('unique ID from database does not match unique ID inside file %s' % self.filenameAP)

        if self.uniqueIDFromHeader and self.uniqueIDFromDatabase:
            # assert self.uniqueIDFromHeader == self.uniqueIDFromDatabase, 'unique ID from header does not match unique ID from database'
            if self.uniqueIDFromHeader != self.uniqueIDFromDatabase:
                logging.warning('unique ID from header does not match unique ID from database for file %s' % self.filenameAP)

        if self.lookedInsideForUniqueID and self.uniqueIDFromHeader:
            # assert self.uniqueID, 'there is a unique ID from header, but no unique ID inside file'
            if not self.uniqueID:
                logging.warning('there is a unique ID from header, but no unique ID inside file %s' % self.filenameAP)
            # assert self.uniqueID==self.uniqueIDFromHeader, 'mismatch: unique ID from header and unique ID inside file'
            if self.uniqueID != self.uniqueIDFromHeader:
                logging.warning('mismatch: unique ID from header and unique ID inside file %s' % self.filenameAP)

        if self.lookedInsideForUniqueID and self.uniqueIDFromDatabase:
            # assert self.uniqueID, 'there is a unique ID in database, but no unique ID inside file'
            if not self.uniqueID:
                logging.warning('there is a unique ID in database, but no unique ID inside file %s' % self.filenameAP)
            # assert self.uniqueID==self.uniqueIDFromDatabase, 'mismatch: unique ID from database and unique ID inside file'
            if self.uniqueID != self.uniqueIDFromDatabase:
                logging.warning('mismatch: unique ID from database and unique ID inside file %s' % self.filenameAP)

        # logging.debug('three unique ID parameters for %s have been found to be mutually consistent',self.filenameAP)

    #head
    def makeListOfOrgFilesThatLinkToMe(self):
        '''OrgFile class'''

        self.orgFilesThatLinkToMe=db1.linksToOrgTable.makeListOfFilesThatLinkToAFile(self)  #list of OrgFile objects

    def makeSetsOfLinksForHeader(self):
        '''
        OrgFile Class
        from lists of links, make sets of links
        must wait till links are repaired to make the sets, because sets are only strings and not user defined objects
        '''

        assert not self.inHeader, 'unwanted method call on file from link in machine-generated header'

        #sets of strings; don't believe python would know how to make a set of user-defined objects
        # self.setOfLinksToNonOrgFiles=set([a.targetObj.filenameAP for a in self.linksToNonOrgFilesList])
        self.setOfLinksToNonOrgFiles=set(['file:'+a.targetObj.filenameAP for a in self.linksToNonOrgFilesList])

        self.setOfLinksToOrgFiles=set(['file:'+a.targetObj.filenameAP for a in self.linksToOrgFilesList])

        self.setOfTags=set(self.tagList)

    def makeNewHeader(self):
        '''
        OrgFile Class
        make a new header node and its descendants
        '''

        assert not self.inHeader, 'unwanted method call on file from link in machine-generated header'

        self.makeSetsOfLinksForHeader()

        #generate a list of lines before creating Nodes

        headerLines=[Node.headerText1+'\n']

        headerLines.append('** list of links\n')

        headerLines.append('*** outgoing links to org files\n')
        if self.linksToOrgFilesList:
            for link1 in self.linksToOrgFilesList:
                if not link1.targetObj.exists:
                    headerLines.append('**** [['+link1.link+']]    :broken_link:\n')  #make sure link is clickable by adding brackets; also no need of description here
                else:
                    headerLines.append('**** [['+link1.link+']]\n')
                if link1.targetObj.uniqueID:
                    headerLines.append('#LinkUniqueID'+link1.targetObj.uniqueID+'\n')
                    #TODO since a unique ID is now in header, link1.targetObj.uniqueIDFromHeader could be set?

                # #child node with clickable link to node where link is found
                #stuck: was not getting this to work; quit on it
                # textForInternalLink=link1.genOrgInternalLinkToMyNode()
                # if textForInternalLink:
                #     headerLines.append('***** '+textForInternalLink+'\n')

        headerLines.append('*** incoming links from org files\n')
        if self.orgFilesThatLinkToMe:
            for orgFile1 in self.orgFilesThatLinkToMe:
                if not orgFile1.exists:
                    headerLines.append('**** '+orgFile1.simpleClickableLink+'    :broken_link:\n')
                else:
                    headerLines.append('**** '+orgFile1.simpleClickableLink+'\n')

        headerLines.append('*** links to local non-org files\n')
        if self.linksToNonOrgFilesList:
            for link1 in self.linksToNonOrgFilesList:
                if not link1.targetObj.exists:
                    headerLines.append('**** [['+link1.link+']]    :broken_link:\n')
                else:
                    headerLines.append('**** [['+link1.link+']]\n')


        headerLines.append('** sets of links\n')

        headerLines.append('*** outgoing links to org files\n')
        if self.setOfLinksToOrgFiles:
            for linkText in self.setOfLinksToOrgFiles:
                headerLines.append('**** '+linkText+'\n')

        headerLines.append('*** incoming links from org files\n')

        if self.orgFilesThatLinkToMe:
            listOfIncomingLinksFromOrgFiles=[a.simpleClickableLink for a in self.orgFilesThatLinkToMe]
            setOfIncomingLinksFromOrgFiles=set(listOfIncomingLinksFromOrgFiles)
        else:
            listOfIncomingLinksFromOrgFiles=None
            setOfIncomingLinksFromOrgFiles=None

        if setOfIncomingLinksFromOrgFiles:
            for linkText in setOfIncomingLinksFromOrgFiles:
                headerLines.append('**** '+linkText+'\n')

        headerLines.append('*** links to local non-org files\n')
        if self.setOfLinksToNonOrgFiles:
            for linkText in self.setOfLinksToNonOrgFiles:
                headerLines.append('**** '+linkText+'\n')

        headerLines.append('** list of tags\n')

        if self.tagList:
            for tag1 in self.tagList:
                headerLines.append('*** '+tag1+'\n')

        headerLines.append('** set of tags\n')

        if self.setOfTags:
            for tag1 in self.setOfTags:
                headerLines.append('*** '+tag1+'\n')

        self.numOfHeaderLines=len(headerLines)

        self.headerMainlineNode=list_of_child_nodes_from_lines(headerLines,self)[0]
        self.mainlineNodes=[self.headerMainlineNode]+self.bodyMainlineNodes  #if there was an original header, it is discarded

    def fullRepresentationToNewLines(self):
        '''
        OrgFile Class
        make a new set of lines for the org file after collection of nodes has been transformed
        '''
        assert not self.inHeader, 'unwanted method call on file from link in machine-generated header'

        assert self.fullRepresentation, 'have not first generated full representation of %s' % self.filenameAP

        assert self.headerMainlineNode, 'forgot to generate header for %s' % self.filenameAP

        self.newLines=[]
        #the following will recursively walk the tree of nodes, assembling line list
        traverse_nodes_to_recover_line_list(self.mainlineNodes,self.newLines)

        self.newLinesMinusHeader=[]
        traverse_nodes_to_recover_line_list(self.bodyMainlineNodes,self.newLinesMinusHeader)

    def sanityChecksBeforeRewriteFile(self):
        '''OrgFile Class'''

        assert not self.inHeader, 'unwanted method call on file from link in machine-generated header'

        if (len(self.newLines)-self.numOfHeaderLines)<len(self.oldBodyLines):
            return False
        else:
            return True

        if (len(self.newLinesMinusHeader)<len(self.oldBodyLines)):
            return False
        else:
            return True

    def rewriteFileFromNewLines(self,keepBackup=False):
        '''OrgFile Class'''

        assert not self.inHeader, 'unwanted method call on file from link in machine-generated header'

        if keepBackup:
            #this is pretty useless since the same .bak file will keep getting overwritten; need time-series backup but that seems expensive in terms of disk space
            shutil.copy2(self.filenameAP,self.filenameAP+'.bak')
            # logging.debug('Copied %s to %s as a backup' % (self.filenameAP,self.filenameAP+'.bak'))
        #this should overwrite existing file
        fp=open(self.filenameAP,'w')
        fp.writelines(self.newLines)
        fp.close()
        # logging.debug('Overwrote %s with new lines generated from full representation' % self.filenameAP)

    #head
    def useDatabaseToGetOutwardLinks(self):
        '''
        OrgFile class
        instead of creating full representation of this file, use database to populate lists of outgoing links
        '''

        assert self.myFilesTableID, '%s is not in database' % self.filenameAP

        orgFilesILinkTo=db1.linksToOrgTable.makeListOfFilesAFileLinksTo(self)  #list of OrgFile objects
        nonOrgFilesILinkTo=db1.linksToNonOrgTable.makeListOfFilesAFileLinksTo(self)  #list of OrgFile objects

        #turn these OrgFile, NonOrgFile instances into Link instances
        linkRegexesKey='file:anyFilename.org or file+sys:anyFilename.org or file+emacs:anyFilename.org or docview:anyFilename.org'
        if orgFilesILinkTo:
            self.linksToOrgFilesList=[LinkToOrgFile(text='file:'+a.filenameAP,inHeader=False,sourceFile=self,hasBrackets=False,regexForLink=LinkToOrgFile.linkRegexesNoBrackets[linkRegexesKey]) for a in orgFilesILinkTo]

            for link1 in self.linksToOrgFilesList:
                link1.initTargetFile()
                link1.testIfWorking()
        else:
            self.linksToOrgFilesList=[]

        linkRegexesKey='file:anyFilename or file+sys:anyFilename or file+emacs:anyFilename or docview:anyFilename'
        if nonOrgFilesILinkTo:
            self.linksToNonOrgFilesList=[LinkToNonOrgFile(text='file:'+a.filenameAP,inHeader=False,sourceFile=self,hasBrackets=False,regexForLink=LinkToNonOrgFile.linkRegexesNoBrackets[linkRegexesKey]) for a in nonOrgFilesILinkTo]

            for link1 in self.linksToNonOrgFilesList:
                link1.initTargetFile()
                link1.testIfWorking()
        else:
            self.linksToNonOrgFilesList=[]

#head FUNCTIONS
def all_upper_to_all_lowercase(a):
    if a.isupper():
        return a.lower()
    else:
        return a

def rand_int_as_string(N=4):
    '''return a N-digit random integer in the form of a string'''
    #spent a lot of time struggling in ipython trying to concoct a functional programming solution to this
    list1=map(lambda a:random.randint(0,9),range(0,N))
    list2=map(str,list1)
    return ''.join(list2)

#head
def get_asterisk_level(line):
    '''given a line, return the nunber of leading asterisks (org mode headline level)'''

    matchObj1=asteriskRegex.match(line)
    if matchObj1:
        return matchObj1.group('asterisks').count('*')
    else:
        #zero means there is no leading asterisk
        return 0

def get_base_asterisk_level(lines):
    '''given a list of lines, return the base asterisk level'''
    asteriskLevels=map(get_asterisk_level,lines)
    nonzeroAsteriskLevels=[a for a in asteriskLevels if a>0]
    if nonzeroAsteriskLevels:
        nonzeroAsteriskLevels.sort()
        return nonzeroAsteriskLevels[0]
    else:
        return 0

    # #now nonzeroAsteriskLevels is out of original order, so regen it
    # del nonzeroAsteriskLevels
    # nonzeroAsteriskLevels=[a for a in asteriskLevels if a>0]

#must develop stuff like this in ipython
def separate_parent_lines_descendant_lines(lines):
    '''given a list of lines, return a tuple
    first element in tuple is list of parent lines
    second element in tuple is list of descendant lines
    this is for turning a list of lines into a parent node and a list of child nodes
    lines are assumed to be a parent node followed by any descendant nodes
    this is part of a recursive scheme
    '''

    levels=map(get_asterisk_level,lines)
    upLevelIndices=[j for j,m in enumerate(levels) if m>levels[0]]
    if upLevelIndices:
        splitIndex=upLevelIndices[0]
        parentLines=lines[:splitIndex]
        descendantLines=lines[splitIndex:]
        return parentLines,descendantLines
    else:
        return lines,None

def list_of_child_nodes_from_lines(lines,sourceFile,parent=None):
    '''input: a list of lines which are the descendants of a parent (which can be None)
    input: parent is of class Node or it will be set to None
    return a list of Node objects which are the direct child Nodes of parent Node
    '''

    if (parent<>None) and (not isinstance(parent,Node)):
        logging.error('Parent must be either None or of type Node; parent is forced to None')
        parent=None

    childNodeList=[]

    childNodeAsteriskLevel=get_base_asterisk_level(lines)
    if childNodeAsteriskLevel==0:
        #no child nodes were found
        return []

    #use slicing to break the list of lines into a list of Node objects

    nodeStarts=[j for j,line in enumerate(lines) if line.lower().startswith('*'*childNodeAsteriskLevel+' ')]
    for j,m in enumerate(nodeStarts[:-1]):
        # print lines[m:nodeStarts[j+1]]
        # print '\n'
        childNodeList.append(Node(lines[m:nodeStarts[j+1]],sourceFile,parent))  #here's the recursion
    # print lines[nodeStarts[-1]:]
    childNodeList.append(Node(lines[nodeStarts[-1]:],sourceFile,parent))

    return childNodeList

#head
def line_to_list1(line):
    '''Generate a list from a line
    input:  'some text [[a link with brackets]] more text [[another link with brackets][description]]. \n'
    output:  ['some text','[[a link with brackets]]','more text','[[another link with brackets][description]]','. \n']
    this short operation is put in a function to facilitate unit testing
    '''

    return Link.orgLinkWBracketsRegexNC.split(line)

def text_to_link_and_description_double_brackets(text):
    '''text is [[link]] or [[link][description]]
    return link,description
    if no description, return link,None
    '''
    matchObj1=Link.orgLinkWBracketsRegex.match(text)
    assert matchObj1, 'misusing testToLinkAndDescription: %s does not match format [[link]] or [[link][description]]' % text
    link=matchObj1.group('link')
    assert link, 'link cannot be empty'
    description=matchObj1.group('description')
    return link,description

def text_from_link_and_description(link,description,hasBrackets):

    if description and (not hasBrackets):
        raise ValueError('Cannot form a link with non-empty description and no brackets')

    text=None
    if hasBrackets:
        if description:
            text='[['+link+']['+description+']]'
        else:
            text='[['+link+']]'
    else:
        text=link

    return text

def remove_tilde_from_org_link(linkText):
    #sometimes I goof up with tab completion in emacs, and make a link to a .org~ file instead of a .org

    #TODO rewrite with regular expressions
    if linkText.endswith('.org~'):
        tempLink=linkText.replace('.org~','.org',1)  #only replace the first occurrence; TODO this should instead be done with regular expressions
        if (not tempLink.endswith('.org~')):
            return tempLink
    return linkText

def split_on_non_whitespace_keep_everything(text):
    p4=re.compile(r'(\s+)')
    splitTextList=p4.split(text)
    retList=[a for a in splitTextList if a<>'']  #get rid of useless '' elements
    return retList

def find_best_regex_match_for_text(link,hasBrackets):
    '''function that permits Node to match a piece of text to a link class.
    Whether or not a link has brackets changes how org mode treats it
    no brackets: link
    has brackets: [[link]]
    has brackets: [[link][description]]
    '''

    matchingRegex=None
    matchObj=None
    matchingClass=None
    if hasBrackets:
        matches1=[(a,a.match(link)) for a in regexOrderedListBrackets] #list of tuples: (regex,match object)
    else:
        matches1=[(a,a.match(link)) for a in regexOrderedListNoBrackets] #list of tuples: (regex,match object)
    matches2=[z for z in matches1 if z[1]] #the tuples from matches1 where there is a match

    if matches2:  #if there are any matches
        matchingRegex,matchObj=matches2[0]  #the first match should be the desired one, according to ordering in regexOrderedList
        if hasBrackets:
            matchingClass=regexDictBrackets[matchingRegex]
        else:
            matchingClass=regexDictNoBrackets[matchingRegex]

    return matchingRegex,matchObj,matchingClass

#head
def make_list_of(someThing):

    if type(someThing) != types.ListType:
        tempList=[]
        tempList.append(someThing)
        return tempList
    else:
        return someThing

#head
def traverse_nodes_to_regen_after_link_updates(nodeList1):
    ''' a function that enables
    a recursive walk of tree of nodes
    for purpose of regenerating nodes after updating links
    '''

    nodeList=make_list_of(nodeList1)

    for aNode in nodeList:
        aNode.regenAfterLinkUpdates()
        traverse_nodes_to_regen_after_link_updates(aNode.childNodeList)

def traverse_nodes_to_recover_line_list(nodeList1,listOfLines):
    ''' a function that enables
    a recursive walk of tree of nodes
    for purpose of regenerating list of lines
    '''

    nodeList=make_list_of(nodeList1)

    for aNode in nodeList:
        listOfLines.extend(aNode.myLines)
        traverse_nodes_to_recover_line_list(aNode.childNodeList,listOfLines)

#head
def traverse_nodes_to_reach_desired_node(nodeList1,textToMatch,maxLevel=100):
    ''' a function that enables
    a recursive walk of tree of nodes
    for purpose of reaching a node whose first line contains textToMatch
    stops looking when it finds the first matching node
    will not go deeper in tree than maxLevel
    '''

    if maxLevel<1:
        maxLevel=1

    nodeList=make_list_of(nodeList1)

    for aNode in nodeList:
        if aNode.level>maxLevel:
            continue
        if textToMatch in aNode.myLines[0]:
            return aNode
        elif aNode.childNodeList:
            res1=traverse_nodes_to_reach_desired_node(aNode.childNodeList,textToMatch,maxLevel)
            if res1:
                return res1

#head
def set_up_logging(loggingLevel=None):
    global doNotLogAtOrBelow
    global logFilename

    logLevelsDict={None:None,'debug':logging.DEBUG,'info':logging.INFO,'warning':logging.WARNING,'error':logging.ERROR,'critical':logging.CRITICAL}
    try:
        doNotLogAtOrBelow=logLevelsDict[loggingLevel]
    except:
        doNotLogAtOrBelow=None

    #http://stackoverflow.com/questions/9135936/want-datetime-in-logfile-name
    # logFilename=datetime.datetime.now().strftime('%Y%m%d_%H%MOrgFixLinks.log')
    logFilename=os.path.join(os.getcwd(),datetime.datetime.now().strftime('%Y%m%d_%H%MOrgFixLinks.log'))

    print 'Log file is %s' % logFilename

    logging.basicConfig(filename=logFilename,filemode="w",level=logging.DEBUG,format='%(asctime)s - %(levelname)s - %(message)s')

    # logging.debug('is it working here?')

    logging.error=CallCounted(logging.error)
    logging.warning=CallCounted(logging.warning)

    # logging.debug('is it working here 2?')

    if doNotLogAtOrBelow:
        logging.disable(doNotLogAtOrBelow) #quickly disable logging below a chosen level; see sweigart

    # logging.debug('is it working here 3?')

def remove_old_logs(globPattern,N_to_keep=1):
    "Remove old .log files that match globPattern"

    # if N_to_keep<2:
    #     #keep at least 2 old logs since that's how this code figures out which thumb drive is up next
    #     N_to_keep=2

    try:
        prevLogL=None
        prevLogL=sorted(glob.iglob(globPattern),key=os.path.getctime)
        prevLogL.reverse()  #make sure logs are sorted newest to oldest DONE
        NOldLogs=len(prevLogL)

    except ValueError:
        logging.debug('No previous log file found (%s)' % globPattern)
        return None

    logsToDelete=prevLogL[N_to_keep:]

    if logsToDelete:
        for oldLog in logsToDelete:
            os.remove(oldLog)
            logging.debug('Deleted old log %s' % oldLog) 
    else:
        logging.debug('Number of old logs (%s) does not exceed %i; nothing deleted' % (NOldLogs,N_to_keep))

def turn_off_logging():
    '''
    http://stackoverflow.com/questions/5255657/how-can-i-disable-logging-while-running-unit-tests-in-python-django
    '''
    logging.disable(logging.CRITICAL)

def turn_logging_back_on_at_initial_level():
    '''
    http://stackoverflow.com/questions/5255657/how-can-i-disable-logging-while-running-unit-tests-in-python-django
    '''
    if doNotLogAtOrBelow:
        logging.disable(doNotLogAtOrBelow) #quickly disable logging below a chosen level; see sweigart
    else:
        logging.disable(logging.NOTSET)

#head
def walk_files_looking_for_name_match(nameAP):
    '''
    nameAP is absolute path filename
    '''

    # basenameToMatch=os.path.basename(nameAP)
    (pathRemainder,basenameToMatch)=os.path.split(nameAP)

    dirsVisitedBeforeAP=[]

    userFolderFilenameAP=os.path.expanduser('~')  # should evaluate to /home/userName

    while (pathRemainder != userFolderFilenameAP) and (pathRemainder != (userFolderFilenameAP+'/')):
        #last folder to walk should be Documents
        for (dirname, dirs, files) in os.walk(pathRemainder):
            dirsAP=[os.path.join(dirname,a) for a in dirs]
            for dir1 in dirsVisitedBeforeAP:
                if dir1 in dirsAP:
                    dirs.remove(os.path.split(dir1)[1])
            if 'env' in dirs:
                dirs.remove('env')  #don't visit env directories
            if 'venv' in dirs:
                dirs.remove('venv')  #don't visit venv directories
            if (basenameToMatch in files) or (basenameToMatch in dirs):
                return os.path.join(dirname,basenameToMatch)
            dirsVisitedBeforeAP.append(dirname)
        (pathRemainder,base1)=os.path.split(pathRemainder)

def walk_org_files_looking_for_unique_id_match(uniqueIDToMatch,oldNameAP):
    '''
    oldNameAP is used to choose a folder to start looking in
    '''

    (pathRemainder,basename1)=os.path.split(oldNameAP)

    dirsVisitedBeforeAP=[]

    userFolderFilenameAP=os.path.expanduser('~')  # should evaluate to /home/userName

    while (pathRemainder != userFolderFilenameAP) and (pathRemainder != (userFolderFilenameAP+'/')):
        #last folder to walk should be Documents
        for (dirname, dirs, files) in os.walk(pathRemainder):
            dirsAP=[os.path.join(dirname,a) for a in dirs]
            for dir1 in dirsVisitedBeforeAP:
                if dir1 in dirsAP:
                    dirs.remove(os.path.split(dir1)[1])
            if 'env' in dirs:
                dirs.remove('env')  #don't visit env directories
            if 'venv' in dirs:
                dirs.remove('venv')  #don't visit venv directories
            #select list of files that do not appear in database
            knownBasenamesInDirname=db1.myOrgFilesTable.lookupBasenamesInFolder(pathRemainder)  # a list; TODO could also get known symlink names and known previous filenames
            allBasenamesInDirnameThatAreOrg=[a for a in files if a.endswith('.org')]
            for name in allBasenamesInDirnameThatAreOrg:
                if (not knownBasenamesInDirname) or (name not in knownBasenamesInDirname):  #database does not have this basename in this folder
                    newOrgFile=OrgFile(os.path.join(dirname,name),False)
                    if newOrgFile.exists:  #if it was broken symlink, it will not exist
                        newOrgFile.lookInsideForUniqueID()
                        if newOrgFile.uniqueID and newOrgFile.uniqueID==uniqueIDToMatch:
                            return newOrgFile
                        else:
                            pass
                            #the following can make the database large and make debugging harder than needed TODO
                            # db1.myOrgFilesTable.addFile(newOrgFile)  #if adding file with same unique ID but different name than missing file name, will get UNIQUE contraint failure in database
            dirsVisitedBeforeAP.append(dirname)
        (pathRemainder,base1)=os.path.split(pathRemainder)

def find_all_name_matches_via_bash(textToMatch):
    '''
    my python effort walk_files_looking_for_name_match runs slowly
    use linux utilities to find files faster
    expecting this to return list of name matches
    sorted by last modified with most recent last

    luckily this works with an argument that has asterisks
    e.g. find_all_name_matches_via_bash('*inux*org')

    this one only finds files, not directories
    '''

    # assert basenameToMatch==os.path.basename(basenameToMatch), 'a basename was not entered; %s was entered' % basenameToMatch

    startFolder=os.path.join(os.path.expanduser('~'),'Documents')
    cmd1=['find',startFolder,'-not','-path','*/env/*','-not','-path','*/venv/*','-name',textToMatch,'-printf','%Ts\t%p\n']
    # http://stackoverflow.com/questions/4514751/pipe-subprocess-standard-output-to-a-variable
    out1=subprocess.check_output(cmd1)

    if not out1:
        logging.debug('no matches found for %s (find_all_name_matches_via_bash)' % textToMatch)
        return None

    resList=out1.split('\n')[:-1]
    resListOfLists=[a.split('\t') for a in resList]
    resListOfLists2=[[int(a[0]),a[1]] for a in resListOfLists]
    matchesOldestToNewest=sorted(resListOfLists2)  #sorted by modification time in seconds, ascending
    filenameAPsOldestToNewest=[a[1] for a in matchesOldestToNewest]
    return filenameAPsOldestToNewest

def find_all_name_matches_via_bash_for_directories(textToMatch):
    '''
    my python effort walk_files_looking_for_name_match runs slowly
    use linux utilities to find files faster
    expecting this to return list of name matches
    sorted by last modified with most recent last

    luckily this works with an argument that has asterisks
    e.g. find_all_name_matches_via_bash('*inux*org')

    this one only finds directories
    '''

    startFolder=os.path.join(os.path.expanduser('~'),'Documents')
    cmd1=['find',startFolder,'-not','-path','*/env/*','-not','-path','*/venv/*','-type','d','-name',textToMatch,'-printf','%Ts\t%p\n']
    out1=subprocess.check_output(cmd1)

    if not out1:
        logging.debug('no matches found for %s (find_all_name_matches_via_bash_for_directories)' % textToMatch)
        return None

    resList=out1.split('\n')[:-1]
    resListOfLists=[a.split('\t') for a in resList]
    resListOfLists2=[[int(a[0]),a[1]] for a in resListOfLists]
    matchesOldestToNewest=sorted(resListOfLists2)  #sorted by modification time in seconds, ascending
    filenameAPsOldestToNewest=[a[1] for a in matchesOldestToNewest]
    return filenameAPsOldestToNewest

#head
def set_up_database():
    global db1
    if os.path.exists(databaseName):  #if real run (not dry run) database file exists
        shutil.copyfile(databaseName,dryRunDatabaseName)
        logging.debug('Initializing dry run database to actual database: %s copied to %s' % (databaseName,dryRunDatabaseName))
    else:
        if os.path.exists(dryRunDatabaseName): 
            os.remove(dryRunDatabaseName)
            logging.debug('Starting with blank dry run database because no real run database file has been found: %s deleted' % dryRunDatabaseName)

    #global variable db1 instantiated here
    db1=Database1(dryRunDatabaseName)  #always starting with dry run database and only copy to real database if script completes with no errors
    db1.setUpOrgTables()
    db1.setUpNonOrgTables()

    logging.debug('Database set up; database file in use is %s' % dryRunDatabaseName)

def set_up_blank_database():
    global db1
    '''used for a separate test script'''

    if os.path.exists(dryRunDatabaseName): 
        os.remove(dryRunDatabaseName)

    #global variable db1 instantiated here
    db1=Database1(dryRunDatabaseName)  #always starting with dry run database and only copy to real database if script completes with no errors
    db1.setUpOrgTables()
    db1.setUpNonOrgTables()

    logging.debug('Database set up; database file in use is %s' % dryRunDatabaseName)

#head
def user_chooses_element_from_list_or_rejects_all(aList,nameOfElementInList='element',doubleSpaced=False):
    '''
    purpose: print out a numbered list and allow user to make a selection
    first item in list: none of the above
    '''
    aListForDisplay=[a for a in aList]
    aListForDisplay.insert(0,'None of the above!')
    while True:
        if doubleSpaced:
            for j1,f1 in enumerate(aListForDisplay):
                print '%s:  %s\n' % (j1,f1)
        else:
            for j1,f1 in enumerate(aListForDisplay):
                print '%s:  %s' % (j1,f1)

        userChoice=raw_input('Enter the number corresponding to the desired %s:' % nameOfElementInList)

        try:
            int(userChoice)
        except:
            print 'Please enter an integer; you entered %s\n' % userChoice

        if userChoice=='0':
            return None,'None of the above!'  #this does not correspond to an index in aList                
        elif int(userChoice) in range(1,len(aListForDisplay)):
            return int(userChoice)-1,aListForDisplay[int(userChoice)]
        else:
            print 'Please enter an integer in the correct range\n'
            continue

#head
def get_past_interactive_repairs_dict():
    '''
    when a user carries out an interactive repair of a broken link, repair data is stored on local disk.
    this function reads past repair data from local disk into a dictionary.
    this dictionary maps filenameAP of missing file to filenameAP of found file
    '''
    #oops: not having success with shelve module; change to csv file data storage
    # shelfFile=shelve.open('pastInteractiveRepairs.shelve')

    # #get the dictionary out of the shelved file, or else get an empty dictionary
    # try:
    #     return shelfFile['pastInteractiveRepairs']
    # except KeyError:
    #     return {}

    # shelfFile.close()
    try:
        f=open('pastInteractiveRepairs.csv','rt')
    except IOError:
        # logging.debug('No file of past interactive repairs found')
        return {}

    reader=csv.reader(f)
    pastRepairs={a[0]:a[1] for a in reader}  #dictionary comprehension
    f.close()
    return pastRepairs

def store_past_interactive_repairs():
    '''
    OOPS shelve module is crashing
    change to csv file data storage
    '''
    # shelfFile=shelve.open('pastInteractiveRepairs.shelve')

    # shelfFile['pastInteractiveRepairs']=pastInteractiveRepairs

    # shelfFile.close()

    f=open('pastInteractiveRepairs.csv','wt')

    writer=csv.writer(f)

    writer.writerows(pastInteractiveRepairs.items())

    f.close()

    logging.debug('Wrote data file %s of past interactive repairs' % 'pastInteractiveRepairs.csv')

#head
def print_and_log_traceback():
    print traceback.format_exc()
    [logging.error(a) for a in traceback.format_exc().strip().split('\n')]  #send traceback to log file, with each line logged separately so you can grep for them

#head
def find_unique_id_inside_org_file(filenameAP):
    '''go line by line through an org file and look for its unique ID'''
    
    inFile1=open(filenameAP,'r')

    logging.debug('a full representation of %s has not been made' % filenameAP)
    logging.debug('so, now stepping through every line of %s looking for unique ID' % filenameAP)

    foundStatusLine=False
    for line1 in inFile1:
        if foundStatusLine:
            b=OrgFile.myUniqueIDRegex.search(line1)
            inFile1.close()
            if b:
                logging.debug('found unique ID %s inside %s' % (b.group('uniqueID'),filenameAP))
                return b.group('uniqueID')
            else:
                logging.debug('%s has status node, but no unique ID' % filenameAP)
                return None

        if line1.startswith('* status'):
            foundStatusLine=True

    if foundStatusLine:
        logging.debug('%s has status node, but no unique ID' % filenameAP)
    else:
        logging.debug('%s has no status node' % filenameAP)

    inFile1.close()
    return None

#head
def clean_up_on_error_in_operate_on_fileA(fileA,err1,deleteOldLogs,isDryRun,showLog):
    '''
    goes with operate_on_fileA
    '''

    os.chdir(origFolder)
    logging.debug('Changed directory to %s' % origFolder)

    if deleteOldLogs:
        remove_old_logs('*OrgFixLinks.log')

    messg1='An exception happened while analyzing %s: %s' % (fileA.filenameAP,str(err1))
    messg2=messg1+'; see log file %s for details' % logFilename
    print messg2
    logging.error(messg1)

    print_and_log_traceback()

    db1.conn.commit()

    if showLog:
        cmd1='less '+logFilename
        with keyboardInputLock:
            subprocess.Popen(cmd1.split(),shell=False).wait()

def operate_on_fileA(filename,userFixesLinksManually=False,runDebugger=False,debuggerAlreadyRunning=False,isDryRun=False,showLog=False,repairLinks=True,keepBackup=True,deleteOldLogs=True,doLessIfRecentlyFullyAnalyzed=False):
    '''analyze a chosen org file
    try to repair its links
    rewrite the file
    notice that dry run database is not rolled back or deleted
    '''

    startTime=time.time()

    if not debuggerAlreadyRunning:
        if runDebugger:
            pudb.set_trace()
            debuggerAlreadyRunning=True

    try:
        fileA=OrgFile(filename,inHeader=False)

        logging.info('Now analyzing %s (operate_on_fileA)' % fileA.originalFilenameAP)

        fileA.testIfExists()  #version that goes with working with symlink target instead of symlink

        assert fileA.exists, '\nInitial org file to begin spidering, %s, does not exist; quitting\n' % fileA.filenameAP 
        
        assert fileA.endsInDotOrg(), '\nInput filename %s does not end with .org; quitting\n' % fileA.filenameAP

        dirNow=os.getcwd()

        if dirNow<>origFolder:
            logging.warning('Current working directory %s is not the expected %s' % (dirNow,origFolder))

        #need to change directory for relative links in org file to make sense
        fileADir=fileA.changeToMyDirectory()

        logging.debug('Changed directory from %s to %s' % (dirNow,fileADir))

        fileA.lookInsideForUniqueID()  #does not require full representation

        idA=None

        if fileA.uniqueID:
            idA=fileA.myFilesTable.findBestMatchForExistingFileUsingUniqueID(fileA)

        if not idA:
            idA=fileA.myFilesTable.lookupID_UsingName(fileA)

        if idA:
            fileA.myFilesTableID=idA
            fileA.uniqueIDFromDatabase=fileA.myFilesTable.lookupUniqueID_UsingID(idA)
            fileA.checkConsistencyOfThreeUniqueIDDataItems()

            if doLessIfRecentlyFullyAnalyzed:  #for files which have recently been fully-analyzed, do less; use info in database rather than fully analyzing file
                tLastFullyAnalyzed=fileA.myFilesTable.lookupTimeLastFullyAnalyzed_UsingID(idA)
                if tLastFullyAnalyzed:
                    dtSinceLastFullyAnalyzed=time.time()-tLastFullyAnalyzed
                if tLastFullyAnalyzed and (dtSinceLastFullyAnalyzed < secondsSinceFullyAnalyzedCutoff):
                    fileA.recentlyFullyAnalyzed=True
                    #query database for outgoing links of fileA, both org and non org
                    fileA.useDatabaseToGetOutwardLinks()
                    logging.debug('%s was recently fully analyzed, so getting outward links from database and not making full representation of this file' % fileA.filenameAP)
                    return fileA
                else:
                    fileA.recentlyFullyAnalyzed=False

    except Exception as err1:

        clean_up_on_error_in_operate_on_fileA(fileA,err1,deleteOldLogs,isDryRun,showLog)

        raise CannotInitiallyOperateOnOrgFileError("Could not complete initial steps in operating on %s" % filename)

    try:
        #the following should depict file as-received; it also looks inside for unique ID
        fileA.createFullRepresentation()

        if not fileA.uniqueID:
            fileA.generateAndInsertMyUniqueID()

    except Exception as err1:

        clean_up_on_error_in_operate_on_fileA(fileA,err1,deleteOldLogs,isDryRun,showLog)

        raise CannotMakeFullRepresentationError("Could not generate full representation of %s" % filename)

    try:
        # idA=None
        # if not fileA.insertedUniqueID:  #did not just insert a fresh unique ID in fileA
        #     idA=fileA.myFilesTable.findBestMatchForExistingFileUsingUniqueID(fileA)

        # if not idA:
        #     idA=fileA.myFilesTable.lookupID_UsingName(fileA)

        if idA:
            # fileA.myFilesTableID=idA
            # fileA.uniqueIDFromDatabase=fileA.myFilesTable.lookupUniqueID_UsingID(idA)
            # fileA.checkConsistencyOfThreeUniqueIDDataItems()
            fileA.myFilesTable.syncTableToFile(fileA)
            fileA.myFilesTable.updateTimeField(fileA,'tLastFullyAnalyzed')
        else:
            fileA.myFilesTable.addFile(fileA)
            if (fileA.isSymlink or fileA.changedFromSymlinkToNonSymlink):
                fileA.symlinksTable.addSymlink(fileA.originalFilenameAP,fileA)

    except Exception as err1:

        clean_up_on_error_in_operate_on_fileA(fileA,err1,deleteOldLogs,isDryRun,showLog)

        raise CannotReconcileFileWithDatabaseError("Could not reconcile %s with database" % fileA.filenameAP)

    #((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((
    try:
        #don't want old outward links from fileA in linksto table: wipe them out
        db1.linksToOrgTable.removeEntriesMatchingFromFile(fileA)
        db1.linksToNonOrgTable.removeEntriesMatchingFromFile(fileA)

        #now go through the list of outgoing links to org files
        fileA.addUniqueIDsFromHeaderToOutgoingOrgLinkTargets() #this adds unique ID from header node of fileA to target files of links

        # raise Exception("exception for test purposes")

        logging.debug('Now analyzing outward links to org files in %s' % fileA.filenameAP)

        linkBlacklistStrings=['/env/','/venv/','/PStuff/']

        DocumentsFoldernameAP=os.path.join(os.path.expanduser('~'),'Documents')

        #only want to fix links that point in Documents folder
        for linkB in [a for a in fileA.linksToOrgFilesList if (a.targetObj.filenameAP.startswith(DocumentsFoldernameAP) and not [b for b in linkBlacklistStrings if (b in a.targetObj.filenameAP)])]:  #for each outgoing link to an org file
            fileB=linkB.targetObj
            logging.debug('Now analyzing %s which is outward link from fileA %s' % (fileB.filenameAP,fileA.filenameAP))

            originalFileB=linkB.originalTargetObj
            linkB.testIfWorking()

            if fileB.exists:  #linkB is working
                linkB.databaseHousekeepingForWorkingLink()
                continue  #go on to next link

            if (not repairLinks):
                linkB.databaseHousekeepingForBrokenLink()
                continue

            if fileB.uniqueIDFromHeader:
                #look for unique ID from header in database
                aRetVal=linkB.attemptRepairUsingUniqueIDFromHeaderAndDatabase()
                fileB=linkB.targetObj
                if aRetVal=="repaired" or aRetVal=="databaseShowsMaxRepairAttempts": continue
                if aRetVal=="databaseRecordIsAMissingFile" or aRetVal=="noDatabaseRecordFound":
                    #use bash find to get list of files with same basename; look inside each one for unique ID from header
                    #idea is: file was moved to different folder, but basename was unchanged
                    aRetVal=linkB.attemptRepairViaUniqueIDFromHeaderAndBashFind()
                    fileB=linkB.targetObj
                    if aRetVal=="repaired": continue
                    if not aRetVal:  #find command did not find a file with same basename and containing desired unique ID
                        #now walk the files on disk and look inside each one for desired unique ID
                        aRetVal=linkB.attemptRepairByLookingInsideFilesForUniqueID(fileB.uniqueIDFromHeader)
                        if aRetVal=="repaired": continue
                        if not aRetVal:
                            linkB.giveUpOnRepairing()
                            continue
            if not fileB.uniqueIDFromHeader:
                #look for database entry with same filenameAP
                aRetVal=linkB.attemptRepairViaCheckDatabaseForNameMatch()
                fileB=linkB.targetObj
                if aRetVal=="repaired" or aRetVal=="databaseShowsMaxRepairAttempts": continue
                if aRetVal=="databaseRecordIsAMissingFile":
                    if fileB.uniqueIDFromDatabase:
                        aRetVal=linkB.attemptRepairViaUniqueIDFromDatabaseAndBashFind()
                        fileB=linkB.targetObj
                        if aRetVal=="repaired": continue
                        if not aRetVal:  #find command did not find a file with same basename and containing desired unique ID
                            #now walk the files on disk and look inside each one for desired unique ID
                            aRetVal=linkB.attemptRepairByLookingInsideFilesForUniqueID(fileB.uniqueIDFromDatabase)
                            fileB=linkB.targetObj
                            if aRetVal=="repaired": continue
                            if not aRetVal:
                                linkB.giveUpOnRepairing()
                                continue
                    else:  #file is in database by filenameAP and database has no unique ID
                        # attempt to repair via bash find and same basename; take most recently modified
                        aRetVal=linkB.attemptRepairViaBasenameMatchOnDisk()
                        fileB=linkB.targetObj
                        if aRetVal=="repaired": continue
 
                        #try changing basename from name.org to nameMain.org
                        aRetVal=linkB.attemptRepairByAddingMain()
                        fileB=linkB.targetObj
                        if aRetVal=="repaired": continue

                        if fileB.filenameAP.endswith('Main.org'):
                            aRetVal=linkB.attemptRepairByRemovingMain()
                            fileB=linkB.targetObj
                            if aRetVal=="repaired": continue

                #look for database entry with same basename
                #skip; seems like too loose of a match

                #try table previousFilenamesOrg
                aRetVal=linkB.attemptRepairUsingTablePreviousFilenames()
                fileB=linkB.targetObj
                if aRetVal=="repaired" or aRetVal=="databaseShowsMaxRepairAttempts": continue
                if aRetVal=="databaseRecordIsAMissingFile":
                    #is there a unique ID in database?
                    if fileB.uniqueIDFromDatabase:
                        aRetVal=linkB.attemptRepairViaExpectedUniqueIDAndBashFind(fileB.uniqueIDFromDatabase)
                        fileB=linkB.targetObj
                        if aRetVal=="repaired": continue
                        if not aRetVal:  #find command did not find a file with same basename and containing desired unique ID
                            #now walk the files on disk and look inside each one for desired unique ID
                            aRetVal=linkB.attemptRepairByLookingInsideFilesForUniqueID(fileB.uniqueIDFromDatabase)
                            fileB=linkB.targetObj
                            if aRetVal=="repaired": continue
                            if not aRetVal:
                                linkB.giveUpOnRepairing()
                                continue
                    else:  #database entry has no unique ID
                        #attempt to repair via bash find and same basename; take most recently modified
                        aRetVal=linkB.attemptRepairViaBasenameMatchOnDisk()
                        fileB=linkB.targetObj
                        if aRetVal=="repaired": continue

                        #try changing basename from name.org to nameMain.org
                        aRetVal=linkB.attemptRepairByAddingMain()
                        fileB=linkB.targetObj
                        if aRetVal=="repaired": continue

                        if fileB.filenameAP.endswith('Main.org'):
                            aRetVal=linkB.attemptRepairByRemovingMain()
                            fileB=linkB.targetObj
                            if aRetVal=="repaired": continue

                #try table symlinksOrg
                aRetVal=linkB.attemptRepairUsingSymlinksTable()
                fileB=linkB.targetObj
                if aRetVal=="repaired" or aRetVal=="databaseShowsMaxRepairAttempts": continue
                if aRetVal=="databaseRecordIsAMissingFile":
                    #is there a unique ID in database?
                    if fileB.uniqueIDFromDatabase:
                        aRetVal=linkB.attemptRepairViaExpectedUniqueIDAndBashFind(fileB.uniqueIDFromDatabase)
                        fileB=linkB.targetObj
                        if aRetVal=="repaired": continue
                        if not aRetVal:  #find command did not find a file with same basename and containing desired unique ID
                            #now walk the files on disk and look inside each one for desired unique ID
                            aRetVal=linkB.attemptRepairByLookingInsideFilesForUniqueID(fileB.uniqueIDFromDatabase)
                            fileB=linkB.targetObj
                            if aRetVal=="repaired": continue
                            if not aRetVal:
                                linkB.giveUpOnRepairing()
                                continue
                    else:  #database entry has no unique ID
                        #attempt to repair via bash find and same basename; take most recently modified
                        aRetVal=linkB.attemptRepairViaBasenameMatchOnDisk()
                        fileB=linkB.targetObj
                        if aRetVal=="repaired": continue

                        #try changing basename from name.org to nameMain.org
                        aRetVal=linkB.attemptRepairByAddingMain()
                        fileB=linkB.targetObj
                        if aRetVal=="repaired": continue

                        if fileB.filenameAP.endswith('Main.org'):
                            aRetVal=linkB.attemptRepairByRemovingMain()
                            fileB=linkB.targetObj
                            if aRetVal=="repaired": continue

                #try using bash find to look for basename match on disk
                aRetVal=linkB.attemptRepairViaBasenameMatchOnDisk()
                fileB=linkB.targetObj
                if aRetVal=="repaired": continue

                #try changing basename from name.org to nameMain.org
                aRetVal=linkB.attemptRepairByAddingMain()
                fileB=linkB.targetObj
                if aRetVal=="repaired": continue

                if fileB.filenameAP.endswith('Main.org'):
                    aRetVal=linkB.attemptRepairByRemovingMain()
                    fileB=linkB.targetObj
                    if aRetVal=="repaired": continue

                try:
                    if pastInteractiveRepairs[fileB.filenameAP]=='UserChoseToSkipRepairingThis':
                        logging.debug('Dictionary of past interactive repairs identifies %s as a link you skipped manually repairing in the past; skip repairing it' % fileB.filenameAP)
                        linkB.giveUpOnRepairing()
                        continue
                except KeyError:
                    pass

                aRetVal=linkB.attemptRepairViaPastUserRepairs()
                fileB=linkB.targetObj
                if aRetVal=="repaired": continue

                if userFixesLinksManually and fileA.userManuallyFixesMyOutgoingLinks:
                    aRetVal=linkB.attemptRepairViaInteractingWithUser()
                    if aRetVal=='Quit':
                        os.chdir(origFolder)
                        logging.debug('Changed directory to %s' % origFolder)

                        if deleteOldLogs:
                            remove_old_logs('*OrgFixLinks.log')

                        db1.conn.commit()
                        # db1.cur.close()

                        if not isDryRun:
                            shutil.copy2(dryRunDatabaseName,databaseName)
                            logging.debug('Real run not dry run: Copied %s to %s' % (dryRunDatabaseName,databaseName))

                        if showLog:
                            cmd1='less '+logFilename
                            with keyboardInputLock:
                                subprocess.Popen(cmd1.split(),shell=False).wait()

                        return 'Quit'

                    fileB=linkB.targetObj
                    if aRetVal=="repaired": continue

                linkB.giveUpOnRepairing()
                continue





        #NON ORG

        #below is the second section for non org
        #now go through the list of outgoing links to non-org files

        logging.debug('Now analyzing outward links to non org files in %s' % fileA.filenameAP)

        for linkB in [a for a in fileA.linksToNonOrgFilesList if (a.targetObj.filenameAP.startswith(DocumentsFoldernameAP) and not [b for b in linkBlacklistStrings if (b in a.targetObj.filenameAP)])]:  #for each outgoing link to a non org file
            fileB=linkB.targetObj
            logging.debug('Now analyzing %s which is outward link from fileA %s' % (fileB.filenameAP,fileA.filenameAP))
            originalFileB=linkB.originalTargetObj
            linkB.testIfWorking()

            if fileB.exists:  #linkB is working
                linkB.databaseHousekeepingForWorkingLink()
                continue  #go on to next link

            if (not repairLinks):
                linkB.databaseHousekeepingForBrokenLink()
                continue

            #look for database entry with same filenameAP
            aRetVal=linkB.attemptRepairViaCheckDatabaseForNameMatch()
            fileB=linkB.targetObj
            if aRetVal=="repaired" or aRetVal=="databaseShowsMaxRepairAttempts": continue
            if aRetVal=="databaseRecordIsAMissingFile":
                #attempt to repair via bash find and same basename; take most recently modified
                if '%20' in fileB.filenameAP:
                    #http://stackoverflow.com/questions/11768070/transform-url-string-into-normal-string-in-python-20-to-space-etc
                    aRetVal=linkB.attemptRepairViaBasenameMatchOnDisk(transform1=True)
                    fileB=linkB.targetObj
                    if aRetVal=="repaired": continue

                aRetVal=linkB.attemptRepairViaBasenameMatchOnDisk()
                fileB=linkB.targetObj
                if aRetVal=="repaired": continue

            #look for database entry with same basename
            #skip; seems like too loose of a match

            #try table previousFilenamesNonOrg
            aRetVal=linkB.attemptRepairUsingTablePreviousFilenames()
            fileB=linkB.targetObj
            if aRetVal=="repaired" or aRetVal=="databaseShowsMaxRepairAttempts": continue
            if aRetVal=="databaseRecordIsAMissingFile":
                #attempt to repair via bash find and same basename; take most recently modified

                if '%20' in fileB.filenameAP:
                    #http://stackoverflow.com/questions/11768070/transform-url-string-into-normal-string-in-python-20-to-space-etc
                    aRetVal=linkB.attemptRepairViaBasenameMatchOnDisk(transform1=True)
                    fileB=linkB.targetObj
                    if aRetVal=="repaired": continue

                aRetVal=linkB.attemptRepairViaBasenameMatchOnDisk()
                fileB=linkB.targetObj
                if aRetVal=="repaired": continue

            #try table symlinksNonOrg
            aRetVal=linkB.attemptRepairUsingSymlinksTable()
            fileB=linkB.targetObj
            if aRetVal=="repaired" or aRetVal=="databaseShowsMaxRepairAttempts": continue
            if aRetVal=="databaseRecordIsAMissingFile":
                #attempt to repair via bash find and same basename; take most recently modified

                if '%20' in fileB.filenameAP:
                    #http://stackoverflow.com/questions/11768070/transform-url-string-into-normal-string-in-python-20-to-space-etc
                    aRetVal=linkB.attemptRepairViaBasenameMatchOnDisk(transform1=True)
                    fileB=linkB.targetObj
                    if aRetVal=="repaired": continue

                aRetVal=linkB.attemptRepairViaBasenameMatchOnDisk()
                fileB=linkB.targetObj
                if aRetVal=="repaired": continue

            #try using bash find to look for basename match on disk

            if '%20' in fileB.filenameAP:
                #http://stackoverflow.com/questions/11768070/transform-url-string-into-normal-string-in-python-20-to-space-etc
                aRetVal=linkB.attemptRepairViaBasenameMatchOnDisk(transform1=True)
                fileB=linkB.targetObj
                if aRetVal=="repaired": continue

            aRetVal=linkB.attemptRepairViaBasenameMatchOnDisk()
            fileB=linkB.targetObj
            if aRetVal=="repaired": continue

            try:
                if pastInteractiveRepairs[fileB.filenameAP]=='UserChoseToSkipRepairingThis':
                    logging.debug('Dictionary of past interactive repairs identifies %s as a link you skipped manually repairing in the past; skip repairing it' % fileB.filenameAP)
                    linkB.giveUpOnRepairing()
                    continue
            except KeyError:
                pass

            aRetVal=linkB.attemptRepairViaPastUserRepairs()
            fileB=linkB.targetObj
            if aRetVal=="repaired": continue

            if userFixesLinksManually and fileA.userManuallyFixesMyOutgoingLinks:
                aRetVal=linkB.attemptRepairViaInteractingWithUser()
                if aRetVal=='Quit':
                    os.chdir(origFolder)
                    logging.debug('Changed directory to %s' % origFolder)

                    if deleteOldLogs:
                        remove_old_logs('*OrgFixLinks.log')

                    db1.conn.commit()
                    # db1.cur.close()

                    if not isDryRun:
                        shutil.copy2(dryRunDatabaseName,databaseName)
                        logging.debug('Real run not dry run: Copied %s to %s' % (dryRunDatabaseName,databaseName))

                    if showLog:
                        cmd1='less '+logFilename
                        with keyboardInputLock:
                            subprocess.Popen(cmd1.split(),shell=False).wait()

                    return 'Quit'
                fileB=linkB.targetObj
                if aRetVal=="repaired": continue

            linkB.giveUpOnRepairing()
            continue

    except Exception as err1:

        clean_up_on_error_in_operate_on_fileA(fileA,err1,deleteOldLogs,isDryRun,showLog)

        raise CannotProcessOutgoingLinksError("Could not process outgoing links of %s" % filename)

    try:
        # raise Exception("exception for test purposes")

        traverse_nodes_to_regen_after_link_updates(fileA.bodyMainlineNodes)

        fileA.makeListOfOrgFilesThatLinkToMe()
        fileA.makeNewHeader()
        fileA.fullRepresentationToNewLines()
        assert fileA.sanityChecksBeforeRewriteFile(), 'sanity checks failed for rewrite of %s' % fileA.filenameAP
    except Exception as err1:

        clean_up_on_error_in_operate_on_fileA(fileA,err1,deleteOldLogs,isDryRun,showLog)

        raise CannotRegenerateFileError("Could not regenerate %s from full representation" % filename)

    if not isDryRun:
        fileA.rewriteFileFromNewLines(keepBackup=keepBackup)
    else:
        #for dry run, want to be able to look at rewritten file, and then revert it to original
        fileA.rewriteFileFromNewLines(keepBackup=True)

    os.chdir(origFolder)
    logging.debug('Changed directory to %s' % origFolder)

    if deleteOldLogs:
        remove_old_logs('*OrgFixLinks.log')

    db1.conn.commit()
    # db1.cur.close()

    if not isDryRun:
        shutil.copy2(dryRunDatabaseName,databaseName)
        logging.debug('Real run not dry run: Copied %s to %s' % (dryRunDatabaseName,databaseName))

    logging.info('Final state of links')
    logging.info('%s has %s outgoing links to org files, of which: %s were initially broken and have been repaired, and %s remain broken' % (fileA.filenameAP,len(fileA.linksToOrgFilesList),len([a for a in fileA.linksToOrgFilesList if a.targetObj.repaired]),len([a for a in fileA.linksToOrgFilesList if not a.targetObj.exists])))
    logging.info('%s has %s outgoing links to non-org files, of which: %s were initially broken and have been repaired, and %s remain broken\n' % (fileA.filenameAP,len(fileA.linksToNonOrgFilesList),len([a for a in fileA.linksToNonOrgFilesList if a.targetObj.repaired]),len([a for a in fileA.linksToNonOrgFilesList if not a.targetObj.exists])))

    if showLog:
        #this gives you time to inspect rewritten org file before it gets reverted to original in a dry run
        cmd1='less '+logFilename
        with keyboardInputLock:
            subprocess.Popen(cmd1.split(),shell=False).wait()

    endTime=time.time()
    logging.debug('Analyzed %s in %s seconds' % (filename,endTime-startTime))

    if isDryRun:
        os.rename(fileA.filenameAP+'.bak',fileA.filenameAP)  #replace the rewritten file with original
        logging.debug('Dry run: moved %s to %s' % (fileA.filenameAP+'.bak',fileA.filenameAP))

    return fileA

#head
def user_says_stop_spidering(eStopSpidering):
    # logging.debug('waiting for user to type anything followed by enter key')
    # raw_input()  #this will hang around forever until you hit return; hitting ctrl-C will raise KeyboardInterrupt
    # e1.set()

    print 'Hitting enter key will stop spidering\n'

    while True:
        with keyboardInputLock:
            # http://stackoverflow.com/questions/1335507/keyboard-input-with-timeout-in-python
            i, o, e = select.select( [sys.stdin], [], [], 2)  #waits 2 seconds for user input

            if (i):
                logging.debug('user typed %s and spidering will be stopped' % sys.stdin.readline().strip())
                eStopSpidering.set()
                logging.debug('flag set to stop spidering')
                return None

        time.sleep(.1)  #I need to pause while lock is released to give time for spider to acquire lock

def clean_up_before_ending_spidering_run(isDryRun,messg1=None):

    if messg1:
        logging.debug(messg1)

    store_past_interactive_repairs()

def spider_starting_w_fileA(filename,maxTime=None,maxN=None,hitReturnToStop=True,userFixesLinksManually=False,runDebugger=False,debuggerAlreadyRunning=False,isDryRun=False,showLog=False,repairLinks=True,keepBackup=True,deleteOldLogs=True,skipIfRecentlySpidered=False):
    '''
    start spidering org files on local disk, beginning with filename.
    filename needs to be absolute path
    '''

    if runDebugger:
        hitReturnToStop=False
        if not debuggerAlreadyRunning:
            pudb.set_trace()
            debuggerAlreadyRunning=True

    filesSpidered=[]

    messg1='Beginning a spidering run at %s' % filename
    print messg1
    logging.info(messg1)

    try:
        fileA=operate_on_fileA(filename=filename,userFixesLinksManually=userFixesLinksManually,runDebugger=runDebugger,debuggerAlreadyRunning=debuggerAlreadyRunning,isDryRun=isDryRun,showLog=showLog,repairLinks=repairLinks,keepBackup=keepBackup,deleteOldLogs=deleteOldLogs,doLessIfRecentlyFullyAnalyzed=skipIfRecentlySpidered)
        if fileA=='Quit':
            messg1='User quit during processing of %s; quitting spidering' % filename

            clean_up_before_ending_spidering_run(isDryRun,messg1=messg1)

            return 'Quit'

    except Exception as err:
        print 'An exception happened: %s' % str(err)
        logging.error('An exception happened: %s' % str(err))
        logging.info('Stopping spidering because of error in analyzing the first file in a spidering run: %s' % filename)

        print_and_log_traceback()

        clean_up_before_ending_spidering_run(isDryRun)

        return None

    filesSpidered.append(fileA)  #files you have already spidered this session

    filesToSpider=[a.targetObj for a in fileA.linksToOrgFilesList if (a.targetObj.exists and (a.targetObj not in filesSpidered))]

    spiderTime=time.time()-globalStartTime

    if hitReturnToStop:
        stopSpideringEvent=threading.Event()

        stopSpideringThread=threading.Thread(name='stopSpidering',target=user_says_stop_spidering,args=(stopSpideringEvent,))
        stopSpideringThread.setDaemon(True)
        stopSpideringThread.start()

    while ((maxN and len(filesSpidered)<=maxN) and (maxTime and spiderTime<=maxTime) and len(filesToSpider)>0):
        if hitReturnToStop and stopSpideringEvent.isSet():
            messg1='Spidering was stopped because user hit return key'
            print messg1
            logging.debug(messg1)
            break

        filename=filesToSpider[0].filenameAP

        if filename in [a.filenameAP for a in filesSpidered]:
            #already spidered this one this session
            filesToSpider.pop(0) #remove the first item in the list
            spiderTime=time.time()-globalStartTime
            continue

        rjustN=25  #right justification setting
        messg1List=['Continuing to spider at %s' % filename]+['time = %.2f' % spiderTime]+['max time = %s' % maxTime]+['fileCount = %s' % len(filesSpidered)]
        messg1List+=['max fileCount = %s' % maxN]+['queue to spider = %s' % len(filesToSpider)]
        messg1L2=[a.rjust(rjustN) for a in messg1List]
        messg1L2[0]=messg1L2[0].rjust(140)  #first one is extra long
        messg1=''.join(messg1L2)
        logging.info('   '.join(messg1List))
        if hitReturnToStop:
            print messg1
            print 'Type anything followed by enter key to quit'
        else:
            print messg1

        try:
            fileA=operate_on_fileA(filename=filename,userFixesLinksManually=userFixesLinksManually,runDebugger=runDebugger,debuggerAlreadyRunning=debuggerAlreadyRunning,isDryRun=isDryRun,showLog=showLog,repairLinks=repairLinks,keepBackup=keepBackup,deleteOldLogs=deleteOldLogs,doLessIfRecentlyFullyAnalyzed=skipIfRecentlySpidered)
            if fileA=='Quit':
                messg1='User quit during processing of %s; quitting spidering' % filename

                clean_up_before_ending_spidering_run(isDryRun,messg1=messg1)

                return 'Quit'

        except Exception as err:
            print 'An exception happened: %s' % str(err)
            logging.error('An exception happened: %s' % str(err))

            print_and_log_traceback()

            logging.warning('Choosing to continue spidering despite error in analyzing %s' % filename)
            print 'Warning: choosing to continue spidering despite error in analyzing %s' % filename
            fileA=OrgFile(filename,inHeader=False)

        filesSpidered.append(fileA)
        filesToSpider.pop(0) #remove the first item in the list

        filesSpideredFilenameAPs=[a.filenameAP for a in filesSpidered]

        if len(fileA.linksToOrgFilesList)==1:
            fileB=fileA.linksToOrgFilesList[0].targetObj
            if fileB.exists and (fileB.filenameAP not in filesSpideredFilenameAPs):
                filesToSpider.append(fileB)
        elif len(fileA.linksToOrgFilesList)>1:
            filesToSpider.extend([a.targetObj for a in fileA.linksToOrgFilesList if (a.targetObj.exists and (a.targetObj.filenameAP not in filesSpideredFilenameAPs))])

        spiderTime=time.time()-globalStartTime


    if maxN and len(filesSpidered)>maxN:
        messg1='Spidering was stopped because files spidered exceeded maximum allowable'
        print messg1
        logging.debug(messg1)
    elif maxTime and spiderTime>maxTime:
        messg1='Spidering was stopped because spidering time exceeded maximum allowable'
        print messg1
        logging.debug(messg1)

    clean_up_before_ending_spidering_run(isDryRun,messg1='Completed spidering run')

#head
def get_list_of_all_repairable_org_files():
    '''
    spider routine queue can run dry
    instead of spidering, get a list of all org files on disc that I would want to repair
    '''

    dirsVisitedBeforeAP=[]
    allOrgFilenamesAP=[]

    DocumentsFoldernameAP=os.path.join(os.path.expanduser('~'),'Documents')

    for (dirname, dirs, files) in os.walk(DocumentsFoldernameAP):
        dirsAP=[os.path.join(dirname,a) for a in dirs]
        for dir1 in dirsVisitedBeforeAP:
            if dir1 in dirsAP:
                dirs.remove(os.path.split(dir1)[1])
        if 'env' in dirs:
            dirs.remove('env')  #don't visit env directories
        if 'venv' in dirs:
            dirs.remove('venv')  #don't visit venv directories

        allBasenamesInDirnameThatAreOrg=[a for a in files if a.endswith('.org')]
        allFilenameAPInDirnameThatAreOrg=[os.path.join(dirname,a) for a in allBasenamesInDirnameThatAreOrg]
        allOrgFilenamesAP.extend(allFilenameAPInDirnameThatAreOrg)
        dirsVisitedBeforeAP.append(dirname)

    return allOrgFilenamesAP

def operate_on_all_org_files(maxTime=None,maxN=None,hitReturnToStop=True,userFixesLinksManually=False,runDebugger=False,debuggerAlreadyRunning=False,isDryRun=False,showLog=False,repairLinks=True,keepBackup=True,deleteOldLogs=True,skipIfRecentlySpidered=False):
    '''
    this one does not spider; it just walks every org file
    practically: skipIfRecentlySpidered input should be set to True
    '''

    logging.info('Now operating on all org files on disc')

    if runDebugger and not debuggerAlreadyRunning:
        pudb.set_trace()

    if hitReturnToStop and runDebugger:
        runDebugger=False
        logging.warning('In spidering, you have enabled feature: hit return to stop spidering.  You also turned on debugger.  Debugger pudb cannot handle multithreading, so it cannot be turned on')

    filesToWalk=get_list_of_all_repairable_org_files()
    NFilesToWalk=len(filesToWalk)
    logging.debug('%s total org files found to walk (operate_on_all_org_files)' % NFilesToWalk)
    count=0

    spiderTime=time.time()-globalStartTime

    if hitReturnToStop:
        stopSpideringEvent=threading.Event()

        stopSpideringThread=threading.Thread(name='stopSpidering',target=user_says_stop_spidering,args=(stopSpideringEvent,))
        stopSpideringThread.setDaemon(True)
        stopSpideringThread.start()

    for filename in filesToWalk:
        if ((maxN and count>maxN) or (maxTime and spiderTime>maxTime)):
            break

        if hitReturnToStop and stopSpideringEvent.isSet():
            messg1='Spidering was stopped because user hit return key'
            print messg1
            logging.debug(messg1)
            break

        count+=1

        rjustN=25  #right justification setting
        messg1List=['Continuing to walk %s org files at %s' % (NFilesToWalk,filename)]+['time = %.2f' % spiderTime]+['max time = %s' % maxTime]+['fileCount = %s' % count]
        messg1List+=['max fileCount = %s' % maxN]+['queue to spider = %s' % (NFilesToWalk-count)]
        messg1L2=[a.rjust(rjustN) for a in messg1List]
        messg1L2[0]=messg1L2[0].rjust(140)  #first one is extra long
        messg1=''.join(messg1L2)
        logging.info('   '.join(messg1List))
        if hitReturnToStop:
            print messg1
            print 'Type anything followed by enter key to quit'
        else:
            print messg1

        try:
            fileA=operate_on_fileA(filename=filename,userFixesLinksManually=userFixesLinksManually,runDebugger=runDebugger,debuggerAlreadyRunning=debuggerAlreadyRunning,isDryRun=isDryRun,showLog=showLog,repairLinks=repairLinks,keepBackup=keepBackup,deleteOldLogs=deleteOldLogs,doLessIfRecentlyFullyAnalyzed=skipIfRecentlySpidered)
            if fileA=='Quit':
                messg1='User quit during processing of %s; quitting spidering' % filename

                clean_up_before_ending_spidering_run(isDryRun,messg1=messg1)

                return 'Quit'

        except Exception as err:
            print 'An exception happened: %s' % str(err)
            logging.error('An exception happened: %s' % str(err))

            print_and_log_traceback()

            logging.warning('Choosing to continue spidering despite error in analyzing %s' % filename)
            print 'Warning: choosing to continue spidering despite error in analyzing %s' % filename

        spiderTime=time.time()-globalStartTime

    if maxN and count>maxN:
        messg1='Spidering was stopped because files spidered exceeded maximum allowable'
        print messg1
        logging.debug(messg1)
    elif maxTime and spiderTime>maxTime:
        messg1='Spidering was stopped because spidering time exceeded maximum allowable'
        print messg1
        logging.debug(messg1)

    clean_up_before_ending_spidering_run(isDryRun,messg1='Completed spidering run')

#head
def make_regex_dicts():
    '''
    a regexDict is a dictionary where key is compiled regex and value is class that compiled regex belongs to
    purpose: matching a link in [[link][description]] to class
    '''
    regexDict1Brackets={a:LinkToOrgFile for a in LinkToOrgFile.linkRegexesBrackets.values()}  #dictionary comprehension
    regexDict2Brackets={a:LinkToNonOrgFile for a in LinkToNonOrgFile.linkRegexesBrackets.values()}
    #http://stackoverflow.com/questions/38987/how-to-merge-two-python-dictionaries-in-a-single-expression
    regexDict1Brackets.update(regexDict2Brackets)

    regexDict1NoBrackets={a:LinkToOrgFile for a in LinkToOrgFile.linkRegexesNoBrackets.values()}  #dictionary comprehension
    regexDict2NoBrackets={a:LinkToNonOrgFile for a in LinkToNonOrgFile.linkRegexesNoBrackets.values()}
    #http://stackoverflow.com/questions/38987/how-to-merge-two-python-dictionaries-in-a-single-expression
    regexDict1NoBrackets.update(regexDict2NoBrackets)

    return regexDict1Brackets,regexDict1NoBrackets

def make_regex_ordered_lists():
    '''
    lists of compiled regex for identifying class of link; has particular order for identifying link in [[link][description]]
    '''

    rOLB=[LinkToOrgFile.linkRegexesBrackets['file:anyFilename.org::anything or file+sys:anyFilename.org::anything or file+emacs:anyFilename.org::anything or docview:anyFilename.org::anything']]
    rOLB.append(LinkToOrgFile.linkRegexesBrackets['/anyFilename.org::anything  or  ./anyFilename.org::anything  or  ~/anyFilename.org::anything'])
    rOLB.append(LinkToNonOrgFile.linkRegexesBrackets['file:anyFilename::anything or file+sys:anyFilename::anything or file+emacs:anyFilename::anything or docview:anyFilename::anything'])
    rOLB.append(LinkToNonOrgFile.linkRegexesBrackets['/anyFilename::anything  or  ./anyFilename::anything  or  ~/anyFilename::anything'])

    rOLB.append(LinkToOrgFile.linkRegexesBrackets['file:anyFilename.org or file+sys:anyFilename.org or file+emacs:anyFilename.org or docview:anyFilename.org'])
    rOLB.append(LinkToOrgFile.linkRegexesBrackets['/anyFilename.org  or  ./anyFilename.org  or  ~/anyFilename.org'])
    rOLB.append(LinkToNonOrgFile.linkRegexesBrackets['file:anyFilename or file+sys:anyFilename or file+emacs:anyFilename or docview:anyFilename'])
    rOLB.append(LinkToNonOrgFile.linkRegexesBrackets['/anyFilename  or  ./anyFilename  or  ~/anyFilename'])

    rOLNB=[LinkToOrgFile.linkRegexesNoBrackets['file:anyFilename.org::anything or file+sys:anyFilename.org::anything or file+emacs:anyFilename.org::anything or docview:anyFilename.org::anything']]
    rOLNB.append(LinkToNonOrgFile.linkRegexesNoBrackets['file:anyFilename::anything or file+sys:anyFilename::anything or file+emacs:anyFilename::anything or docview:anyFilename::anything'])

    rOLNB.append(LinkToOrgFile.linkRegexesNoBrackets['file:anyFilename.org or file+sys:anyFilename.org or file+emacs:anyFilename.org or docview:anyFilename.org'])
    rOLNB.append(LinkToNonOrgFile.linkRegexesNoBrackets['file:anyFilename or file+sys:anyFilename or file+emacs:anyFilename or docview:anyFilename'])

    return rOLB,rOLNB

#head
def usage():

    messg1='''
    flags with no input argument:
    -h, --help: show this help blurb
    -u, --userFixesLinks: when automatic link repair fails and it makes sense to do so, prompt user to fix broken links manually (menu-driven)
    -n, --noSpideringStopViaKeystroke: normally spidering can be stopped via typing anything then hitting enter key; -n disables this.  also set by -d.
    -d, --debug:  run script in pudb.  additionally sets -n.
    -D, --dryRun:  make no changes to org files on disk.  make a copy of database and make changes to the copy.
    -l, --showLog:  use pager less to display log file after operating on each org file; this gives you time to inspect a rewritten org file in dry run mode before it's reverted to original
    -b, --noBackup: do not make .bak copy of each org file before replacing it on disk
    -q, --quickMode: when a file has been recently spidered, just look up outward links in database and move to next file to spider, rather than making full representation, repairing links, etc;  intention is to speed things up

    flags that require input argument:
    -f, --inputFile:  supply a file to begin spidering; if no -f, all org files in /home/username/Documents are walked
    -L, --loggingLevel:  logging to take place above this level.  valid inputs: None, debug, info, warning, error, critical;  default value None
    -N, --maxFilesToSpider:  max number of files to spider, an integer
    -t, --maxTimeToSpider: max time to spend spidering (seconds)

    python -O:  -O flag turns off assert statements in the script orgFixLinks.py.  Assert statements identify associated preconfigured error conditions.  Suppressing them via -O flag speeds up script execution.

    example call:
    python -O orgFixLinks.py -uD -f /home/userName/Documents/myOrgFilename.org -N 20 -t 300

    a separate script that carries out some automated tests of this script is orgFixLinksTests.py
    '''
    print messg1

#head module-level stuff that will always execute even when this module is imported by another script/module
databaseName=os.path.join(os.getcwd(),'orgFiles.sqlite')  #'real run' database
dryRunDatabaseName=os.path.join(os.getcwd(),'orgFilesDryRunCopy.sqlite') #dry run database
#head
globalStartTime=time.time()
#head
keyboardInputLock=threading.Lock()
#head
origFolder=os.getcwd()
#head
pastInteractiveRepairs=get_past_interactive_repairs_dict()  # a dictionary for storing past interactive repairs of broken links
#head
asteriskRegex=re.compile('(?P<asterisks>^\*+) ')

#list of compiled regex for identifying class of link; has particular order for identifying link in [[link][description]]
regexOrderedListBrackets,regexOrderedListNoBrackets=make_regex_ordered_lists()

#dictionary that matches compiled regex in regexOrderedListBrackets/regexOrderedListNoBrackets to class it belongs to
regexDictBrackets,regexDictNoBrackets=make_regex_dicts()

maxFailedRepairAttempts=10  #setting
maxLinesInANodeToAnalyze=1000  #setting  idea is that sometimes a user will paste large blocks of text in a node blurb, and script can hang forever trying to make sense of long chunks of text that do not look like org file material
# only purpose is to avoid errors where this script reacts improperly to a line of text.
# if set too small, will not be able to get uniqueIDs in header when header contains many links
secondsSinceFullyAnalyzedCutoff=2*24*60*60  #setting elapsed seconds since org file last fully analyzed; cutoff to be considered recently analyzed  24 hr/day * 60 min/hr * 60 sec/min
maxLengthOfVisibleLinkText=5  #setting that affects length of visible text (length of description in [[link][description]]) in a link to a local file

#head
if __name__ <> "__main__":
    #want to be able to import things from this module for testing, without logging taking place
    logging.disable(logging.CRITICAL)  #disables all logging messages; see sweigart

    set_up_blank_database()

#head MAIN
if __name__=="__main__":

    #initialize variables that could be changed via command line inputs
    fileA1=None
    isDryRun=False
    showLog=False
    runDebugger=False
    debuggerAlreadyRunning=False
    loggingLevel=None  #log at all levels by default
    maxN=10000
    maxTime=100000.0
    hitReturnToStop=True
    userFixesLinksManually=False
    keepBackup=True
    skipIfRecentlySpidered=False
    # ---------------------------------------------------------
    #process command line inputs
    #dive into python 10.6
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hundDlbqf:L:N:t:", ["help","userFixesLinks","noSpideringStopViaKeystroke","debug","dryRun","showLog","noBackup","quickMode","file=","loggingLevel=","maxFilesToSpider=","maxTimeToSpider="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt,arg in opts:
        if opt in ("-h","--help"):
            usage()
            sys.exit()

        elif opt in ("-u","--userFixesLinks"):
            userFixesLinksManually=True

        elif opt in ("-n","--noSpideringStopViaKeystroke"):
            hitReturnToStop=False

        elif opt in ("-d","--debug"):
            runDebugger=True
            hitReturnToStop=False
            # logging.debug('Command line flag said to run the debugger (pudb) so turning off feature to hit return to stop spidering')

        elif opt in ("-D","--dryRun"):
            isDryRun=True
            #dry run: after script finishes, all org files on disk remain unchanged
            #dry run: a copy of database is made and changes are made to the copy, not to the original
            #of limited usefulness since can't keep a test sequence going; just use it at a point where script is known to crash; I guess you can alternate between dry run and full run and step forward that way

        elif opt in ("-l","--showLog"):
            #display log via less at end of run
            showLog=True

        elif opt in ("-b","--noBackup"):
            #keepBackup=True means: before modifying an org file on disk, copy it to .bak
            keepBackup=False

        elif opt in ("-q","--quickMode"):
            #for a file which was recently spidered, use database instead of making a full representation of file and attempting link repair
            skipIfRecentlySpidered=True

        elif opt in ("-f","--file"):
            #user has supplied an org file to begin spidering
            fileA1=arg

        elif opt in ("-L","--loggingLevel"):
            #user has supplied a logging level; logging will take place above this level
            loggingLevel=arg

        elif opt in ("-N","--maxFilesToSpider"):
            #user selects max number of files to spider
            try:
                maxN=int(arg)
            except:
                print 'Quitting: command line input %s for maxFilesToSpider does not evaluate to an integer.\n' % arg
                sys.exit()

            if maxN<1:
                print 'Quitting: command line input %s for maxFilesToSpider is not a positive integer.\n' % arg
                sys.exit()

        elif opt in ("-t","--maxTimeToSpider"):
            #user selects max time to spend spidering
            try:
                maxTime=float(arg)
            except:
                print 'Quitting: command line input %s for maxTimeToSpider does not evaluate to a floating point number.\n' % arg
                sys.exit()

            if maxTime<=0:
                print 'Quitting: command line input %s for maxTimeToSpider is not a positive number.\n' % arg
                sys.exit()

    # ---------------------------------------------------------

    if runDebugger:
        pudb.set_trace()
        debuggerAlreadyRunning=True

    set_up_logging(loggingLevel)

    set_up_database()

    if fileA1:  #user has supplied a file to start spidering with via command line
        spider_starting_w_fileA(filename=fileA1,maxTime=maxTime,maxN=maxN,hitReturnToStop=hitReturnToStop,userFixesLinksManually=userFixesLinksManually,runDebugger=runDebugger,debuggerAlreadyRunning=debuggerAlreadyRunning,isDryRun=isDryRun,showLog=showLog,keepBackup=keepBackup,skipIfRecentlySpidered=skipIfRecentlySpidered)

    else: #user did not specify a file to start with; just walk all org files
        operate_on_all_org_files(maxTime=maxTime,maxN=maxN,hitReturnToStop=hitReturnToStop,userFixesLinksManually=userFixesLinksManually,runDebugger=runDebugger,debuggerAlreadyRunning=debuggerAlreadyRunning,isDryRun=isDryRun,showLog=showLog,keepBackup=keepBackup,skipIfRecentlySpidered=skipIfRecentlySpidered)

    print 'Run completed: log file %s contains %s errors and %s warnings\n' % (logFilename,logging.error.counter,logging.warning.counter)
    db1.cur.close()
#head

