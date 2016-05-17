# -*- coding: utf-8 -*-
"""
This code is part of a project in the Udacity Data Analyst Nanodegree
DANDP3 - Wrangling Data from OSM using MongoDB
Anna Signor
Created on Thu Apr 28 16:09:46 2016

@author: Anna
"""

"""https://discussions.udacity.com/t/reducing-memory-footprint-when-processing-large-datasets-in-xml/37571/3"""
"""http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
   https://discussions.udacity.com/t/how-to-provide-sample-data-for-the-final-project/7118/13"""
"""https://discussions.udacity.com/t/valueerror-i-o-operation-on-closed-file/167469/6"""
"""https://discussions.udacity.com/t/keep-attr-atrr-atrr-formatted-data/166864/14"""
"""https://discussions.udacity.com/t/i-have-an-adequate-update-name-to-improve-street-names-not-sure-how-to-use-it/166569/5"""    

#%%


import xml.etree.cElementTree as ET  
import re
import codecs
import json
import pprint


def count_tags(filename):
    """create a dctionary with all the tags in a certain XML file"""
    tagdict = {}
    
    for t in ET.iterparse(filename): #tuple (event, element) store in traverser t
        element =  t[1]              #isolates element
        if element.tag in tagdict:
            tagdict[element.tag] += 1 #if tag in dict, add 1 to value
        else:
            tagdict[element.tag] = 1  #if tag not in dict, create key and assign value 1

    return (tagdict)      

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def is_street_name(element):
    """Modified version of is_street_name from PE."""
    words = element.attrib['k'].split(':')
    verdict = 'street' in words
    return (verdict)

def audit(osmfile):
    """takes an OSM XML file, returns a dictionary containing all the street types (e.g. 
    Av., Avenue S. St, etc.) as keys and their occurrence as values."""
    osm_file = open(osmfile, "r")
    street_types = {}
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    #print tag.tag, tag.attrib
                    tipo = tag.attrib['v'].split()[0] #this is getting the first word
                    if tipo in street_types:
                        street_types[tipo] += 1
                    if tipo not in street_types:
                        street_types[tipo] = 1
    osm_file.close()
    return street_types

"""Mapping words to proper street types."""
mapping = {'avenida':'Avenida',
           u'Al.': 'Alameda',
           'Rue': 'Rua',
           u'Av.': 'Avenida',
           u'Av': 'Avenida',
           'RUa': 'Rua',
           'R': 'Rua',
           'Acost.': 'Acostamento',
           'RUA': 'Rua',
           'rua' : 'Rua',
           'R.' : 'Rua',
           'AC': 'Acesso',
           'estrada' : 'Estrada',
           'travessa' : 'Travessa'           
           }

def update_name_BR(name, mapping):
    """takes a street name and a dictionary and updates the street type 
    to conform with a standard (e.g. 'R.', 'RUa', 'Rue' and rua will
    all become 'Rua'). See 'mapping' variable above."""
    words = name.split() #split string in n words
    first_word = words[0] #isolate first word
    if first_word in mapping:
        words[0] = mapping[words[0]]        
        return ' '.join(words)
    else: return name

"""The set below has all the acceptable street types that occur in the map.
The information was obtained using the audit function."""
good_types = set(['Acostamento', 
                  u'Pra\xe7a', 
                  'Alameda', 
                  'Viela', 
                  'Estrada', 
                  'Rua', 
                  'Acesso', 
                  'Parque', 
                  'Largo', 
                  'Via', 
                  'Marginal', 
                  'Rodovia', 
                  'Corredor', 
                  'Viaduto', 
                  'Travessa', 
                  'Pateo', 
                  'Avenida', 
                  'Passagem',
                  u'Complexo Vi\xe1rio'])
                  

"""The dictionary below was bilt manually to address the issue of street names
missing the street types. All the cases where the type was missing (30 or so) were
analysed manually using search engines and the cases where the type was not 
'Rua' are mapped below. """
mapping2 = {u'1\xaa Travessa da Estrada do Morro Grande' : '',
            'Alfonso Bovero' : 'Avenida',
            u'N\xedvia Maria Dombi' : 'Travessa'
            }

good_tuple = tuple(good_types)

def improve_name_BR(name):
    """Takes a street name from sao paulo and returns improved name, designed
    to fix problems encountered in the names"""
    words = name.split() 
    ###split string in n words    
    if name.startswith(good_tuple):
        return name
        ### if name is okay, return name (do nothing)
    elif words[0] in mapping:
        words[0] = mapping[words[0]]        
        return ' '.join(words)
        ### if type is mispelled or miscased, update 1st word of name and return joined string
    elif name in mapping2:
        return mapping2[name] + ' ' + name
        ### if name is one of the odd cases but not needing word 'Rua', use mapping2 to fix 
        ### (this is a hard code manually created)
    else:
        return 'Rua' + ' ' + name
        ### the cases left are the ones where the word 'Rua' was left out


creation_attributes = set(['version', 'changeset', 'timestamp', 'user', 'uid'])
coordinates_attributes = set(['lat', 'lon'])
#address_attributes = set(['housenumber', 'postcode', 'street'])

problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def smarter_nestify(l, record):
    """adapted from: 
    http://stackoverflow.com/questions/37014500/how-to-use-recursion-to-nest-dictionaries-while-integrating-with-existing-record
    """
    if len(l) == 2:
        key = l[0]
        value = l[1]
        return {key: value}
    else:
        key = l[0]
        record[key] = smarter_nestify(l[1:], record.get(key, {}))                
        return record
#%%
def shape_CEP(record):
    """Takes a brazilian CEP as a string and returns isself if CEP is correctly formatted, 
    formats properly if missing the '-' and returns none otherwise."""
    record = record.strip('CEP')
    record = record.strip()
    proper_CEP = '^([0-9]){5}([-])([0-9]){3}$'
    bad_dash = '^([0-9]){5}([.\s])([0-9]){3}$'
    dash_and_spaces = '^([0-9]){5}([\s][-][\s])([0-9]){3}$'     
    no_dash = '^([0-9]){8}$'
    if re.match(proper_CEP, record):
        return record
        #if CEP is properly formatted, return itself
    elif re.match(no_dash, record):
        return record[:5] + '-' + record[5:]
    elif re.match(bad_dash, record):
        return record[:5] + '-' + record[6:]
    elif re.match(dash_and_spaces, record):
        return record[:5] + '-' + record[8:]
    else:
        return None        
#%%
"""This cell contains tests ran to prof shape_CEP. Cases were harvested from actual dataset by printing
rejected postcodes to ensure all salvageable data is being used and all unusable data is being discarded."""        
print shape_CEP('09890-1 09890-080 00'), 'expected None'
print shape_CEP('Igreja Presbiteriana Vila Gustavo'), 'expected None'
print shape_CEP('99132860153'), 'expected None'
print shape_CEP('09171 - 430'), 'expected 09171-430'
print shape_CEP('CEP 03032-030'), 'expected 03032-030'
print shape_CEP('010196-200'), 'expected None'
print shape_CEP('0454-000'), 'expected None'
print shape_CEP('12.216-540'), 'expected None'
print shape_CEP('12216540'), 'expected 12216-540'
print shape_CEP('09380-310'), 'expected 09380-310'
print shape_CEP('09991-060'), 'expected 09991-060'
print shape_CEP('02213.070'), 'expected 02213-070'     
#%%        
postcodes = set() 
 
def shape_element(element):    
    current_node = {}
    current_node['data_prim'] = element.tag #stands for 'data primitive'
    #above line was causing issues when using 'type' as a key
    # ref: https://discussions.udacity.com/t/problem-cleaning-my-osm-dataset/35085/2
    if element.tag == 'node' or element.tag == 'way' or element.tag == 'relation':
    
        ###execute specific sntructions for 'way'        
        if element.tag == 'way':
            current_node['node_refs'] = []
            for child in element:
                if child.tag == 'nd':
                    current_node['node_refs'].append(child.attrib['ref'])                   
        
        ####populate 'created'
        current_node['created'] = {}
        for att in creation_attributes: 
            if att == 'version':
                current_node['created'][att] = int(element.attrib[att])
            else:
                current_node['created'][att] = element.attrib[att]
        
        ###make coord. into floats, store in list as a value for 'pos' key
        lat = float(element.attrib.get('lat', '0'))  
        lon = float(element.attrib.get('lon', '0'))      
        if (lat and lon):        
            current_node['pos'] = [lat, lon]     
        
        ###populate all other attribute:value pairs inside <node---/>
        ### <way---/> or <relation---/>
        prev_attributes = creation_attributes | coordinates_attributes
        for key in element.attrib:
            if key not in prev_attributes:                
                current_node[key] = element.attrib[key]
                
        ###populate 'adress'
        ###and parse other <tag ---\> elements
        current_node['address'] = {}        
        ###loop over <tag ---\> elements        
        for tag in element:
            if tag.tag == 'tag':
                if re.search(problemchars, tag.attrib['k']):
                    continue
                else:
                    words = tag.attrib['k'].split(':') #split string in n words at ':'
                    n = len(words)
                    val = tag.attrib['v']
                    if n == 1:
                        if tag.attrib['k'] == 'lanes':
                            current_node['numberlanes'] = tag.attrib['v']
                            #special case: can't use word 'lanes' as a key
                        else:
                            current_node[tag.attrib['k']] = tag.attrib['v'] 
                        #if no ':' place directly in in main dictionary for document, key 'k' and value 'v'
                    elif (words[0] == 'addr') and (n == 2): #if format 'addr:attribute'
                        address_key = words[1] #gets proper key (e.g.'street' or 'housenumber')
                        current_node['address'][address_key] = tag.attrib['v']
                    else:
                        if len(words) > 1 and words[0] in current_node and type(current_node[words[0]]):
                            #add '--' to key when there is a conflict between a colonated and a simple key
                            new_key = words[0] + '--'
                            words = [new_key] + words[1:]
                        lista = words + [val]
                        current_node = smarter_nestify(lista, current_node)
                         
        if ('street' in current_node['address']):
            current_node['address']['street'] = improve_name_BR(current_node['address']['street'])
        if ('postcode' in current_node['address']):
            current_node['address']['postcode'] = shape_CEP(current_node['address']['postcode'])

        ###if 'address' is still an empty dictionary, delete
        if current_node['address'] == {}:
             del current_node['address']   
                
        return current_node
                
    else:
        return None

def old_process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
            
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")


"""create main json file"""
old_process_map('C:\Udacity\DANDP3\sao_paulo_brazil.osm', False)
print 'DONE'

#%%    
"""map was processed and imported into a MongoDB named my_osm, collection cme"""

#%%
"""Connect with database and run queries."""
from pymongo import MongoClient
import pprint

client = MongoClient()
db = client


#%%
###see one document
sp = db.my_osm.cme
pprint.pprint(sp.find_one())
#%%
sp.drop()
#%%
### number of relations
qu = {"data_prim" : "relation"}

relations = sp.find(qu)
count = 0
for r in relations:
    pprint.pprint(r)
    count +=1
print '\n there are {} relations'.format(count)

#%%
### number of unique user ids
cursor = sp.aggregate([{'$group':{'_id': '$created.uid'}}])
unique_ids = []
for c in cursor:
    unique_ids.append(c)
print unique_ids, '\n', len(unique_ids)

#%%
### the highest number of times a document was edited
versions = sp.distinct('created.version')
print versions, max(versions)

#%%
### the document that was edited the most
cursor = sp.find({'created.version' : 445})
for c in cursor:
    pprint.pprint(c)
#%%
### investigate street names starting with *
good = list(good_types)                  
expression = '|'.join(good)

def street_starts_with(letters):
    """takes a string and returns a regex string to be used with operator
    $regex to query sp collections for streets starting with the string"""
    a = ['Acostamento', 
         u'Pra\xe7a', 
         'Alameda', 
         'Viela', 
         'Estrada', 
         'Rua', 
         'Acesso', 
         'Parque', 
         'Largo', 
         'Via', 
         'Marginal', 
         'Rodovia', 
         'Corredor', 
         'Viaduto', 
         'Travessa', 
         'Pateo', 
         'Avenida', 
         'Passagem',
         u'Complexo Vi\xe1rio']
    expression = '|'.join(a)
    return '^'+'(' + expression + ')' + ' ' + letters

#%%
### street names that contain a high military rank

""" from wikipedia, these are the ranks: Almirante	Marechal	Marechal do Ar
Almirante de Esquadra	General de Exército	Tenente Brigadeiro do Ar
Vice Almirante	General de Divisão	Major Brigadeiro
Contra Almirante	General de Brigada	Brigadeiro
Capitão de Mar e Guerra	Coronel	Coronel
Capitão de Fragata	Tenente Coronel	Tenente Coronel
Capitão de Corveta	Major	Major
Capitão Tenente	Capitão	Capitão """

military_ranks = ['Almirante',
                  'Marechal',
                  'Marechal',
                  'General',
                  'Tenente',
                  'Brigadeiro',
                  'Major',
                  'Contra Almirante',
                  u'Capitão']

nomes = {}
for rank in military_ranks:
    
    result =  sp.find({"address.street": {"$regex": street_starts_with(rank)}}, {'address': 1, 'type' : 1, '_id' : 0})
        
    nomes[rank] =  result.count()
    
print nomes, "\n TOTAL:", len(nomes)

pprint.pprint(nomes)
soma = 0
for k in nomes:
    soma += nomes[k]
print 'TOTAL:', soma