# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 09:28:20 2013

@author: hok1
"""

import HTMLParser
import csv
import urllib
import sys

tasksfileheader = ['SOC6', 'SOC8', 'Tasks']
soc2010nametasksheader = ['SOC6', 'SOC8', 'Names', 'Tasks']

onet_homepage = 'http://www.onetonline.org/find/family?f=0&g=Go'
onet_root = 'http://www.onetonline.org'

class ONetHomepageSOCLinkParser(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.currentcode = ""
        self.toreadSOC = False
        self.toreadlink = False
        self.socdict = {}
    
    def handle_starttag(self, tag, attrs):
        if tag=='td':        
            for attr in attrs:
                if attr==('class', 'reportrtd'):
                    self.toreadSOC = True
                if attr==('class', 'report2ed'):
                    self.toreadlink = True
        if tag=='a':
            if self.toreadlink:
                for attr in attrs:
                    if attr[0] == 'href':
                        self.socdict[self.currentcode] = attr[1]
                
    def handle_endtag(self, tag):
        self.toreadSOC = False
        self.toreadlink = False

    def handle_data(self, data):
        if self.toreadSOC:
            self.currentcode = data
            self.toreadSOC = False
            
class JobTasksParser(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.toreadtask = False
        self.tasklist = []
        
    def handle_starttag(self, tag, attrs):
        if tag=='li':
            for attr in attrs:
                if attr==('class', 'task'):
                    self.toreadtask = True
                    
    def handle_endtag(self, tag):
        if tag=='li':
            self.toreadtask = False
            
    def handle_data(self, data):
        if self.toreadtask:
            self.tasklist.append(data)
            self.toreadtask = False

def get_all_soc8_links():
    linkParser = ONetHomepageSOCLinkParser()
    frootpage = urllib.urlopen(onet_homepage)
    linkParser.feed(frootpage.read())
    return linkParser.socdict    
 
def retrieve_all_tasks(filename):
    print 'Parsing the link from the root page: ', onet_homepage
    soclinkdict = get_all_soc8_links()
    
    print 'Opening the file ', filename
    fout = open(filename, 'wb')
    writer = csv.writer(fout)
    writer.writerow(tasksfileheader)
    
    print 'Parsing tasks...'
    for soc8 in soclinkdict:
        print '\tParsing tasks for ', soc8
        soc6 = soc8[0:7]
        tasksParser = JobTasksParser()
        fjobpage = urllib.urlopen(onet_root+soclinkdict[soc8])
        tasksParser.feed(fjobpage.read())
        tasks = tasksParser.tasklist
        writer.writerow([soc6, soc8]+tasks)
        
    print 'Closing the file'
    fout.close()

def retrieve_soc2010_names(filename):
    soc6dict = {}
    fin = open(filename)
    for line in fin:
        soc6 = line[0:7]
        title = line[8:]
        soc6dict[soc6] = {'name': title, 'subgroups': {}}
    fin.close()
    return soc6dict

def combine_soc2010_names_tasks(soc6dict, filename):
    print 'Parsing the link from the root page: ', onet_homepage
    soclinkdict = get_all_soc8_links()

    print 'Parsing tasks...'
    for soc8 in soclinkdict:
        soc6 = soc8[0:7]
        print '\tParsing tasks for ', soc8
        tasksParser = JobTasksParser()
        fjobpage = urllib.urlopen(onet_root+soclinkdict[soc8])
        tasksParser.feed(fjobpage.read())
        tasks = tasksParser.tasklist
        soc6dict[soc6]['subgroups'][soc8] = tasks
    
    print 'Opening the file ', filename
    fout = open(filename, 'wb')
    writer = csv.writer(fout)
    writer.writerow(soc2010nametasksheader)
        
    print 'Writing to file: ', filename
    for soc6 in sorted(soc6dict.keys()):
        name = soc6dict[soc6]['name']
        for soc8 in sorted(soc6dict[soc6]['subgroups'].keys()):
            tasks = soc6dict[soc6]['subgroups'][soc8]
            writer.writerow([soc6, soc8, name]+tasks)
        
    print 'Closing the file'
    fout.close()
    
if __name__ == '__main__':
    args = sys.argv
    if len(args) >= 3:
        todo = args[1]
        filename = args[2]
        if todo == 'scrape':
            retrieve_all_tasks(filename)
        elif todo == 'combine':
            soc6dict = retrieve_soc2010_names('SOC2010_names.txt')
            combine_soc2010_names_tasks(soc6dict, filename)
