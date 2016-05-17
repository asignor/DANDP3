# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 12:45:06 2016
Programming exercise 4 as part of P3 of Udacity DAND nanodegree
@author: Anna

"""

import xml.etree.cElementTree as ET
from collections import defaultdict
import re

"""
Your task in this exercise has two steps:

- audit the OSMFILE and change the variable 'mapping' to reflect the changes needed to fix 
    the unexpected street types to the appropriate ones in the expected list.
    You have to add mappings only for the actual problems you find in this OSMFILE,
    not a generalized solution, since that may and will depend on the particular area you are auditing.
- write the update_name function, to actually fix the street name.
    The function takes a string with street name as an argument and should return the fixed name
    We have provided a simple test so that you see what exactly is expected
"""

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

# UPDATE THIS VARIABLE
mapping = { 'St': 'Street',
            'St.': 'Street',
            'AVE' : 'Avenue',
            'AVE.' : 'Avenue',
            'Av.' : 'Avenue',
            'Ave.' : 'Avenue',
            'Ave' : 'Avenue',
            'Blvd' : 'Boulevard',
            'Blvd.' : 'Boulevard',
            'BLVD' : 'Boulevard',
            'BLVD.' : 'Boulevard',
            'Dr' : 'Drive',
            'Dr.' : 'Drive',
            'DR.' : 'Drive',
            'DR' : 'Drive',
            'Ct.' : 'Court',
            'Ct' : 'Court',
            'CT.' : 'Court',
            'CT' : 'Court',
            'PL' : 'Place',
            'Pl' : 'Place',
            'Pl..' : 'Place',
            'PL..' : 'Place',
            'LN' : 'Lane',
            'Ln' : 'Lane',
            'LN.' : 'Lane',
            'Ln.' : 'Lane',
            'PKWY' : 'Parkway',
            'Pkwy' : 'Parkway',
            'PKWY.' : 'Parkway',
            'Pkwy.' : 'Parkway',
            'Ter' : 'Terrace',
            'ROW' : 'Row',
            'Rd.' : 'Road',
            'Rd' : 'Road',
            'RD.' : 'Road',
            'RD' : 'Road',
            }


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
            


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


def update_name(name, mapping):
    words = name.split() #split string in n words
    n = len(words) - 1 #find n
    last_word = words[n] #isolate last word
    if last_word in mapping:
        words[n] = mapping[words[n]]        
        return ' '.join(words)
    else: return name

test1 = 'West Lexington St.'
test2 = 'Baldwin Rd'

print update_name(test1, mapping), update_name(test2, mapping)