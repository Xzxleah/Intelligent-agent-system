#!/usr/bin/env python
# coding: utf-8

# In[39]:


import spacy
import glob
import re
import string
import socket
import csv, rdflib, urllib.parse
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import FOAF, RDF, RDFS, OWL, XSD
from urllib.parse import urlencode, parse_qsl, urljoin, urlparse


lecture = csv.DictReader(open('6721_Lectures.csv'))
slide_topic_g = Graph()

focu = Namespace('http://focu.io/schema#')
focudata = Namespace('http://focu.io/data#')
dbo = Namespace('http://dbpedia.org/ontology/')
dbpedia = Namespace('http://dbpedia.org/resource/')
dbp = Namespace('http://dbpedia.org/property/')
wd = Namespace('http://www.wikidata.org/entity/')
schema = Namespace('http://schema.org/')

slide_topic_g.bind('foaf', FOAF)
slide_topic_g.bind('rdfs', RDFS)
slide_topic_g.bind('rdf', RDF)
slide_topic_g.bind('owl', OWL)
slide_topic_g.bind('xsd', XSD)
slide_topic_g.bind('focu', focu)
slide_topic_g.bind('focudata', focudata)
slide_topic_g.bind('dbo', dbo)
slide_topic_g.bind('dbpedia', dbpedia)
slide_topic_g.bind('dbp', dbp)
slide_topic_g.bind('wd', wd)
slide_topic_g.bind('schema', schema)


nlp = spacy.load("en_core_web_sm")
nlp.add_pipe('dbpedia_spotlight')

website = 'http://'
website1 = 'https://'
    

#slide = URIRef(focudata+'GCS_165_lecture01')
#path = 'file:///C:/unibot/COMP474_6741/Slide_Plain/slides01.txt'.replace('file:///', '')
for row in lecture:
    row = dict(row)
    
    slide = URIRef(focudata+row['Slides'])
    # get slide related topics
    path = row['Slide_Plain'].replace('file:///', '')
    #print(path)
    for slide_file in glob.glob(path):
        entity_list = []
        url_list = []
        with open(slide_file, encoding='utf-8', errors='ignore') as file_in:
            text = file_in.read()
            lines = text.split('\n')
            for line in lines:
                if line.strip():
                    if (line.__contains__(website)):
                        continue
                    elif (line.__contains__(website1)):
                        continue
                    else:
                        #print(line)
                        if len(line) != 0:
                            doc = nlp(line)
                            for ent in doc.ents:
                                entity = ent.text
                                regex_sub = re.sub(r"[•,‘’;@#?!&$%^*]+", ' ', entity)
                                cleaned_text = re.sub(r"\s+", '_', regex_sub).strip()
                                entity = cleaned_text.replace('-', '_').replace('(', '').replace(')','')
                                #print([(ent.text, ent.kb_id_, score)]) 
                                if entity not in entity_list:
                                    entity_list.append(entity)                       
                                    if ent.label_ == 'DBPEDIA_ENT':
                                        score = ent._.dbpedia_raw_result['@similarityScore']
                                        if score > str(0.85):
                                            #print([(ent.text, ent.kb_id_, score)])
                                            url = ent.kb_id_.replace('(', '').replace(')','')
                                            if url not in url_list:
                                                url_list.append(url)
                                                doc_token = nlp(entity)
                                                flag = 'false'
                                                for token in doc_token:
                                                    if token.pos_ == 'NOUN' or  token.pos_== 'PROPN':
                                                        flag = 'true'
                                                if flag == 'true': 
                                                    fullurl = urllib.parse.quote(URIRef(focudata+entity), safe="%/:=&?~#+!$,;'@()*[]")
                                                    topic = URIRef(fullurl)
                                                    #print(URIRef(focudata+ent.text))
                                                    #print(topic)
                                                    slide_topic_g.add((slide, focu['introduce'], topic))
                                                    # add each topic detailed info
                                                    slide_topic_g.add((topic, RDF.type, focu['Topic']))
                                                    slide_topic_g.add((topic, RDFS.label, Literal(ent.text, datatype=XSD.string)))
                                                    slide_topic_g.add((topic, OWL.sameAs, URIRef(url)))
                                                                    
slide_topic_g.serialize(destination='6721slide_topic_graph.ttl', format='turtle')


# In[35]:


import spacy
import glob
import re
import string
import socket
import csv, rdflib, urllib.parse
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import FOAF, RDF, RDFS, OWL, XSD
from urllib.parse import urlencode, parse_qsl, urljoin, urlparse


lecture = csv.DictReader(open('6721_Lectures.csv'))
lab_topic_g = Graph()

focu = Namespace('http://focu.io/schema#')
focudata = Namespace('http://focu.io/data#')
dbo = Namespace('http://dbpedia.org/ontology/')
dbpedia = Namespace('http://dbpedia.org/resource/')
dbp = Namespace('http://dbpedia.org/property/')
wd = Namespace('http://www.wikidata.org/entity/')
schema = Namespace('http://schema.org/')

lab_topic_g.bind('foaf', FOAF)
lab_topic_g.bind('rdfs', RDFS)
lab_topic_g.bind('rdf', RDF)
lab_topic_g.bind('owl', OWL)
lab_topic_g.bind('xsd', XSD)
lab_topic_g.bind('focu', focu)
lab_topic_g.bind('focudata', focudata)
lab_topic_g.bind('dbo', dbo)
lab_topic_g.bind('dbpedia', dbpedia)
lab_topic_g.bind('dbp', dbp)
lab_topic_g.bind('wd', wd)
lab_topic_g.bind('schema', schema)

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe('dbpedia_spotlight', config={'confidence': 0.4, 'overwrite_ents':False})

website = 'http://'
website1 = 'https://'
    
for row in lecture:
    row = dict(row)
    
    lab = URIRef(focudata+row['Labs'])
    # get slide related topics
    path = row['Lab_Plain'].replace('file:///', '')
    
    for lab_file in glob.glob(path):
        entity_list = []
        url_list = []
        with open(lab_file, encoding='utf-8', errors='ignore') as file_in:
            text = file_in.read()
            lines = text.split('\n')
            for line in lines:
                if line.strip():
                    if (line.__contains__(website)):
                        continue
                    elif (line.__contains__(website1)):
                        continue
                    else:
                        #print(line)
                        doc = nlp(line)
                        for ent in doc.ents:
                            entity = ent.text
                            regex_sub = re.sub(r"[•,‘’;@#?!&$%^*]+", ' ', entity)
                            cleaned_text = re.sub(r"\s+", '_', regex_sub).strip()
                            entity = cleaned_text.replace('-', '_').replace('(', '').replace(')','')
                            #print([(ent.text, ent.kb_id_, score)]) 
                            if entity not in entity_list:
                                entity_list.append(entity)                       
                                if ent.label_ == 'DBPEDIA_ENT':
                                    score = ent._.dbpedia_raw_result['@similarityScore']
                                    if score > str(0.85):
                                        #print([(ent.text, ent.kb_id_, score)])
                                        url = ent.kb_id_.replace('(', '').replace(')','')
                                        if url not in url_list:
                                            url_list.append(url)
                                            doc_token = nlp(entity)
                                            flag = 'false'
                                            for token in doc_token:
                                                if token.pos_ == 'NOUN' or  token.pos_== 'PROPN':
                                                    flag = 'true'
                                            if flag == 'true': 
                                                fullurl = urllib.parse.quote(URIRef(focudata+entity), safe="%/:=&?~#+!$,;'@()*[]")
                                                topic = URIRef(fullurl)
                                                #print(URIRef(focudata+ent.text))
                                                #print(topic)
                                                lab_topic_g.add((lab, focu['introduce'], topic))
                                                # add each topic detailed info
                                                lab_topic_g.add((topic, RDF.type, focu['Topic']))
                                                lab_topic_g.add((topic, RDFS.label, Literal(ent.text, datatype=XSD.string)))
                                                lab_topic_g.add((topic, OWL.sameAs, URIRef(url)))
                                        



lab_topic_g.serialize(destination='6721lab_topic_graph.ttl', format='turtle')


# In[34]:


import spacy
import glob
import re
import string
import socket
import csv, rdflib, urllib.parse
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import FOAF, RDF, RDFS, OWL, XSD
from urllib.parse import urlencode, parse_qsl, urljoin, urlparse


lecture = csv.DictReader(open('6721_Lectures.csv'))
worksheet_topic_g = Graph()

focu = Namespace('http://focu.io/schema#')
focudata = Namespace('http://focu.io/data#')
dbo = Namespace('http://dbpedia.org/ontology/')
dbpedia = Namespace('http://dbpedia.org/resource/')
dbp = Namespace('http://dbpedia.org/property/')
wd = Namespace('http://www.wikidata.org/entity/')
schema = Namespace('http://schema.org/')

worksheet_topic_g.bind('foaf', FOAF)
worksheet_topic_g.bind('rdfs', RDFS)
worksheet_topic_g.bind('rdf', RDF)
worksheet_topic_g.bind('owl', OWL)
worksheet_topic_g.bind('xsd', XSD)
worksheet_topic_g.bind('focu', focu)
worksheet_topic_g.bind('focudata', focudata)
worksheet_topic_g.bind('dbo', dbo)
worksheet_topic_g.bind('dbpedia', dbpedia)
worksheet_topic_g.bind('dbp', dbp)
worksheet_topic_g.bind('wd', wd)
worksheet_topic_g.bind('schema', schema)

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe('dbpedia_spotlight', config={'confidence': 0.4, 'overwrite_ents':False})

website = 'http://'
website1 = 'https://'
    
for row in lecture:
    row = dict(row)
    
    worksheet = URIRef(focudata+row['Worksheets'])
    # get slide related topics
    path = row['Worksheet_Plain'].replace('file:///', '')
    for worksheet_file in glob.glob(path):
        entity_list = []
        url_list = []
        with open(worksheet_file, encoding='utf-8', errors='ignore') as file_in:
            text = file_in.read()
            lines = text.split('\n')
            for line in lines:
                if line.strip():
                    if (line.__contains__(website)):
                        continue
                    elif (line.__contains__(website1)):
                        continue
                    else:
                        #print(line)
                        doc = nlp(line)
                        for ent in doc.ents:
                            entity = ent.text
                            regex_sub = re.sub(r"[•,‘’;@#?!&$%^*]+", ' ', entity)
                            cleaned_text = re.sub(r"\s+", '_', regex_sub).strip()
                            entity = cleaned_text.replace('-', '_').replace('(', '').replace(')','')
                            #print([(ent.text, ent.kb_id_, score)]) 
                            if entity not in entity_list:
                                entity_list.append(entity)                       
                                if ent.label_ == 'DBPEDIA_ENT':
                                    score = ent._.dbpedia_raw_result['@similarityScore']
                                    if score > str(0.85):
                                        #print([(ent.text, ent.kb_id_, score)])
                                        url = ent.kb_id_.replace('(', '').replace(')','')
                                        if url not in url_list:
                                            url_list.append(url)
                                            doc_token = nlp(entity)
                                            flag = 'false'
                                            for token in doc_token:
                                                if token.pos_ == 'NOUN' or  token.pos_== 'PROPN':
                                                    flag = 'true'            
                                            if flag == 'true':
                                                fullurl = urllib.parse.quote(URIRef(focudata+entity), safe="%/:=&?~#+!$,;'@()*[]")
                                                topic = URIRef(fullurl)
                                                #print(URIRef(focudata+ent.text))
                                                 #print(topic)
                                                worksheet_topic_g.add((worksheet, focu['introduce'], topic))
                                                 # add each topic detailed info
                                                worksheet_topic_g.add((topic, RDF.type, focu['Topic']))
                                                worksheet_topic_g.add((topic, RDFS.label, Literal(ent.text, datatype=XSD.string)))
                                                worksheet_topic_g.add((topic, OWL.sameAs, URIRef(url)))
                                                        
worksheet_topic_g.serialize(destination='6721worksheet_topic_graph.ttl', format='turtle')


# In[30]:


import spacy
import glob
import re
import string
import socket
import csv, rdflib, urllib.parse
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import FOAF, RDF, RDFS, OWL, XSD
from urllib.parse import urlencode, parse_qsl, urljoin, urlparse


lecture = csv.DictReader(open('6721_Lectures.csv'))
reading_topic_g = Graph()

focu = Namespace('http://focu.io/schema#')
focudata = Namespace('http://focu.io/data#')
dbo = Namespace('http://dbpedia.org/ontology/')
dbpedia = Namespace('http://dbpedia.org/resource/')
dbp = Namespace('http://dbpedia.org/property/')
wd = Namespace('http://www.wikidata.org/entity/')
schema = Namespace('http://schema.org/')

reading_topic_g.bind('foaf', FOAF)
reading_topic_g.bind('rdfs', RDFS)
reading_topic_g.bind('rdf', RDF)
reading_topic_g.bind('owl', OWL)
reading_topic_g.bind('xsd', XSD)
reading_topic_g.bind('focu', focu)
reading_topic_g.bind('focudata', focudata)
reading_topic_g.bind('dbo', dbo)
reading_topic_g.bind('dbpedia', dbpedia)
reading_topic_g.bind('dbp', dbp)
reading_topic_g.bind('wd', wd)
reading_topic_g.bind('schema', schema)

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe('dbpedia_spotlight', config={'confidence': 0.4, 'overwrite_ents':False})

website = 'http://'
website1 = 'https://'
    
for row in lecture:
    row = dict(row)
    if (len(row['Readings']) != 0):
        reading = URIRef(focudata+row['Readings'])
        # print(reading)
        if (len(row['Reading_Plain']) != 0):
            for directory in row['Reading_Plain'].split(';'):
                path = directory.replace('file:///', '')
                # print(path)
                for reading_file in glob.glob(path):
                    entity_list = []
                    url_list = []
                    with open(reading_file, encoding='utf-8', errors='ignore') as file_in:
                        text = file_in.read()
                        lines = text.split('\n')
                        for line in lines:
                            if line.strip():
                                if (line.__contains__(website)):
                                    continue
                                elif (line.__contains__(website1)):
                                    continue
                                else:
                                    #print(line)
                                    doc = nlp(line)
                                    for ent in doc.ents:
                                        entity = ent.text
                                        #print([(ent.text, ent.kb_id_, score)]) 
                                        regex_sub = re.sub(r"[•,‘’;@#?!&$%^*]+", ' ', entity)
                                        cleaned_text = re.sub(r"\s+", '_', regex_sub).strip()
                                        entity = cleaned_text.replace('-', '_').replace('(', '').replace(')','')
                                        if entity not in entity_list:
                                            entity_list.append(entity)                       
                                            if ent.label_ == 'DBPEDIA_ENT':
                                                score = ent._.dbpedia_raw_result['@similarityScore']
                                                if score > str(0.85):
                                                    #print([(ent.text, ent.kb_id_, score)])
                                                    url = ent.kb_id_.replace('(', '').replace(')','')
                                                    if url not in url_list:
                                                        url_list.append(url)
                                                        doc_token = nlp(entity)
                                                        flag = 'false'
                                                        for token in doc_token:
                                                            if token.pos_ == 'NOUN' or  token.pos_== 'PROPN':
                                                                flag = 'true'
                                                        if flag == 'true': 
                                                            #print([(ent.text, ent.kb_id_, score)])
                                                            fullurl = urllib.parse.quote(URIRef(focudata+entity), safe="%/:=&?~#+!$,;'@()*[]")
                                                            topic = URIRef(fullurl)
                                                            #print(URIRef(focudata+ent.text))
                                                            #print(topic)
                                                            reading_topic_g.add((reading, focu['introduce'], topic))
                                                            # add each topic detailed info
                                                            reading_topic_g.add((topic, RDF.type, focu['Topic']))
                                                            reading_topic_g.add((topic, RDFS.label, Literal(ent.text, datatype=XSD.string)))
                                                            reading_topic_g.add((topic, OWL.sameAs, URIRef(url)))
                
                                    
reading_topic_g.serialize(destination='6721reading_topic_graph.ttl', format='ttl')


# In[33]:


import spacy
import glob
import re
import string
import socket
import csv, rdflib, urllib.parse
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import FOAF, RDF, RDFS, OWL, XSD
from urllib.parse import urlencode, parse_qsl, urljoin, urlparse


lecture = csv.DictReader(open('6721_Lectures.csv'))
material_topic_g = Graph()

focu = Namespace('http://focu.io/schema#')
focudata = Namespace('http://focu.io/data#')
dbo = Namespace('http://dbpedia.org/ontology/')
dbpedia = Namespace('http://dbpedia.org/resource/')
dbp = Namespace('http://dbpedia.org/property/')
wd = Namespace('http://www.wikidata.org/entity/')
schema = Namespace('http://schema.org/')

material_topic_g.bind('foaf', FOAF)
material_topic_g.bind('rdfs', RDFS)
material_topic_g.bind('rdf', RDF)
material_topic_g.bind('owl', OWL)
material_topic_g.bind('xsd', XSD)
material_topic_g.bind('focu', focu)
material_topic_g.bind('focudata', focudata)
material_topic_g.bind('dbo', dbo)
material_topic_g.bind('dbpedia', dbpedia)
material_topic_g.bind('dbp', dbp)
material_topic_g.bind('wd', wd)
material_topic_g.bind('schema', schema)

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe('dbpedia_spotlight', config={'confidence': 0.4, 'overwrite_ents':False})

website = 'http://'
website1 = 'https://'
    
for row in lecture:
    row = dict(row)
    if (len(row['Additional_materials']) != 0):
        material = URIRef(focudata+row['Additional_materials'])
        #print(material)
        if (len(row['Material_Plain']) != 0):
            for line in row['Material_Plain'].split(';'):
                #print(line)
                doc = nlp(line)
                entity_list = []
                url_list = []
                for ent in doc.ents:
                    entity = ent.text
                    regex_sub = re.sub(r"[•,‘’;@#?!&$%^*]+", ' ', entity)
                    cleaned_text = re.sub(r"\s+", '_', regex_sub).strip()
                    entity = cleaned_text.replace('-', '_').replace('(', '').replace(')','')
                    #print([(ent.text, ent.kb_id_, score)]) 
                    if entity not in entity_list:
                        entity_list.append(entity)                       
                        if ent.label_ == 'DBPEDIA_ENT':
                            score = ent._.dbpedia_raw_result['@similarityScore']
                            if score > str(0.8):
                                #print([(ent.text, ent.kb_id_, score)])
                                url = ent.kb_id_.replace('(', '').replace(')','')
                                if url not in url_list:
                                    url_list.append(url)
                                    fullurl = urllib.parse.quote(URIRef(focudata+entity), safe="%/:=&?~#+!$,;'@()*[]")
                                    topic = URIRef(fullurl)
                                    #print(URIRef(focudata+ent.text))
                                    #print(topic)
                                    material_topic_g.add((material, focu['introduce'], topic))
                                    # add each topic detailed info
                                    material_topic_g.add((topic, RDF.type, focu['Topic']))
                                    material_topic_g.add((topic, RDFS.label, Literal(ent.text, datatype=XSD.string)))
                                    material_topic_g.add((topic, OWL.sameAs, URIRef(url)))    
                                    
material_topic_g.serialize(destination='6721material_topic_graph.ttl', format='turtle')


# In[40]:


import spacy
import glob
import re
import string
import socket
import csv, rdflib, urllib.parse
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import FOAF, RDF, RDFS, OWL, XSD
from urllib.parse import urlencode, parse_qsl, urljoin, urlparse

new_g = Graph()
slide_topic = Graph()
worksheet_topic= Graph()
material_topic= Graph()
reading_topic = Graph()
lab_topic = Graph()

new_g.parse('lecture_graph.ttl', format='ttl')
slide_topic.parse('6721slide_topic_graph.ttl', format='ttl')
worksheet_topic.parse('6721worksheet_topic_graph.ttl', format='ttl')
material_topic.parse('6721material_topic_graph.ttl', format='ttl')
reading_topic.parse('6721reading_topic_graph.ttl', format='ttl')
lab_topic.parse('6721lab_topic_graph.ttl', format='ttl')

new_g += slide_topic + worksheet_topic + material_topic + reading_topic + lab_topic

new_g.serialize(destination='6721withTopic_graph.ttl', format='ttl')

