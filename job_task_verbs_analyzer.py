# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 16:25:13 2013

@author: hok1
"""

import csv
import nltk
from operator import add

def get_soc_tasks_list(filename):
    fin = open(filename, 'rb')
    reader = csv.reader(fin, delimiter='\t')
    reader.next()
    
    soc_list = []    
    
    for line in reader:
        jobclass = {}
        jobclass['soc6'] = line[0]
        jobclass['soc8'] = line[1]
        jobclass['name'] = line[2]
        if len(line) > 3:
            jobclass['tasks'] = line[3:]
        else:
            jobclass['tasks'] = []
        soc_list.append(jobclass)
        
    fin.close()
    
    return sorted(soc_list, key=lambda item: item['soc8'])
    
def get_verbs(soc_task_list):
    for jobclass in soc_task_list:
        jobclass['verbs'] = []
        for task_descp in jobclass['tasks']:
            pos_sen = nltk.pos_tag(["I"]+task_descp.split(" "))
            jobclass['verbs'] += map(lambda item: item[0].lower(), 
                                     filter(lambda item: item[1] in ['VB', 'VBP', 'VBZ'],
                                            pos_sen))
    return soc_task_list
    
def get_verbs_count(soc_task_list):
    verbs = reduce(add, map(lambda item: item['verbs'], soc_task_list))
    verbset = set(verbs)
    verbs_count = {}
    for verb in verbset:
        verbs_count[verb] = len(filter(lambda word: word==verb, verbs))
    return verbs_count
    
if __name__ == '__main__':
    filename = 'soc2010_tasks.txt'
    soctasks = get_verbs(get_soc_tasks_list(filename))
    verbs_count = get_verbs_count(soctasks)
    
    fout = open('verb_count.csv', 'wb')
    writer = csv.writer(fout)
    writer.write(['verb', 'freq'])
    for verb, freq in sorted(verbs_count.items(),
                             key=lambda item: item[1], reverse=True):
        writer.write([verb, freq])
    fout.close()
