# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 12:45:06 2016
Programming exercise 3 as part of P3 of Udacity DAND nanodegree
@author: Anna

"""
import xml.etree.cElementTree as ET
"""
Your task is to explore the data a bit more.
The first task is a fun one - find out how many unique users
have contributed to the map in this particular area!

The function process_map should return a set of unique user IDs ("uid")
"""

def process_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        if 'changeset' in element.attrib:
            users.add(element.attrib['user'])

    return users
