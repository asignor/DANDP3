# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 12:45:06 2016
Programming exercise 1 as part of P3 of Udacity DAND nanodegree
@author: Anna

"""
import xml.etree.cElementTree as ET


"""
Your task is to use the iterative parsing to process the map file and
find out not only what tags are there, but also how many, to get the
feeling on how much of which data you can expect to have in the map.
Fill out the count_tags function. It should return a dictionary with the 
tag name as the key and number of times this tag can be encountered in 
the map as value.

Note that your code will be tested with a different data file than the 'example.osm'
"""

def count_tags(filename):
    tagdict = {}
    
    for t in ET.iterparse(filename): #tuple (event, element) store in traverser t
        element =  t[1]              #isolates element
        if element.tag in tagdict:
            tagdict[element.tag] += 1 #if tag in dict, add 1 to value
        else:
            tagdict[element.tag] = 1  #if tag not in dict, create key and assign value 1

    return (tagdict)

