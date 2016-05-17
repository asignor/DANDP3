# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 12:45:06 2016
Programming exercise 5 as part of P3 of Udacity DAND nanodegree
@author: Anna

"""
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json

"""
Your task is to wrangle the data and transform the shape of the data
into the model we mentioned earlier. The output should be a list of dictionaries
that look like this:

{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}

You have to complete the function 'shape_element'.
We have provided a function that will parse the map file, and call the function with the element
as an argument. You should return a dictionary, containing the shaped data for that element.
We have also provided a way to save the data in a file, so that you could use
mongoimport later on to import the shaped data into MongoDB. 

Note that in this exercise we do not use the 'update street name' procedures
you worked on in the previous exercise. If you are using this code in your final
project, you are strongly encouraged to use the code from previous exercise to 
update the street names before you save them to JSON. 

In particular the following things should be done:
DONE: you should process only 2 types of top level tags: "node" and "way"
DONE: all attributes of "node" and "way" should be turned into regular key/value pairs, except:
    done: attributes in the CREATED array should be added under a key "created"
    done: attributes for latitude and longitude should be added to a "pos" array,
      for use in geospacial indexing. Make sure the values inside "pos" array are floats
      and not strings. 
- if the second level tag "k" value contains problematic characters, it should be ignored
- if the second level tag "k" value starts with "addr:", it should be added to a dictionary "address"
- if the second level tag "k" value does not start with "addr:", but contains ":", you can
  process it in a way that you feel is best. For example, you might split it into a two-level
  dictionary like with "addr:", or otherwise convert the ":" to create a valid key.
- if there is a second ":" that separates the type/direction of a street,
  the tag should be ignored, for example:

<tag k="addr:housenumber" v="5158"/>
<tag k="addr:street" v="North Lincoln Avenue"/>
<tag k="addr:street:name" v="Lincoln"/>
<tag k="addr:street:prefix" v="North"/>
<tag k="addr:street:type" v="Avenue"/>
<tag k="amenity" v="pharmacy"/>

  should be turned into:

{...
"address": {
    "housenumber": 5158,
    "street": "North Lincoln Avenue"
}
"amenity": "pharmacy",
...
}

DONE: for "way" specifically:

  <nd ref="305896090"/>
  <nd ref="1719825889"/>

should be turned into
"node_refs": ["305896090", "1719825889"]
"""

creation_attributes = set(['version', 'changeset', 'timestamp', 'user', 'uid'])
coordinates_attributes = set(['lat', 'lon'])
address_attributes = set(['housenumber', 'postcode', 'street'])

problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def shape_element(element):
    current_node = {}
    current_node['type'] = element.tag
    if element.tag == 'node' or element.tag == 'way' :
        ###executes specific sntructions for 'way'        
        if element.tag == 'way':
            current_node['node_refs'] = []
            for child in element:
                if child.tag == 'nd':
                    current_node['node_refs'].append(child.attrib['ref'])
        ####populate 'created'
        current_node['created'] = {}
        for att in creation_attributes: 
            current_node['created'][att] = element.attrib[att]
        ###make coord. into floats, store in list as a value for 'pos' key
        try:
            lat = float(element.attrib['lat'])  
            lon = float(element.attrib['lon'])      
            current_node['pos'] = [lat, lon]      
        except:
            print element.tag, element.attrib #it seems for now this only prints 
                                            ###instances containig no coord information
                                            ##if this remains the case for the whole file
                                            ###change to pass
        ###populate 'adress'
        ###(this is the doozy)
        current_node['address'] = {}       
        #loop over <tag ---\> elements        
        for tag in element:
            if tag.tag == 'tag':
                if re.search(problemchars, tag.attrib['k']):
                    continue
                else:
                    words = tag.attrib['k'].split(':') #split string in n words at ':'
                    n = len(words)                   
                    if n == 1:
                        current_node[tag.attrib['k']] = tag.attrib['v'] #if no ':' throw in main dic                   
                    elif (words[0] == 'addr') and (n == 2): #if format 'addr:attribute'
                        print '*************************************************'
                        address_key = words[1] #gets proper key ('street' or 'housenumber')
                        current_node['address'][address_key] = tag.attrib['v']
                    elif n > 2:
                            continue
        ###if 'address' is still an empty dic, delete
        if current_node['address'] == {}:
             del current_node['address'] 
        
        ###populate all other attribute:value pairs
        prev_attributes = creation_attributes | coordinates_attributes |address_attributes
        for key in element.attrib:
            if key not in prev_attributes:
                current_node[key] = element.attrib[key]
            else: 
                pass #do I need something here?
                
        return current_node
    else:
        return None
        
def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

pprint.pprint(process_map('C:/Udacity/my_hood.osm', True))