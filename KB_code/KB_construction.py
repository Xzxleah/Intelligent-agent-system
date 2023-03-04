#!/usr/bin/env python
# coding: utf-8

import csv, rdflib, urllib.parse
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import FOAF, RDF, RDFS, OWL, XSD
from urllib.parse import urlencode, parse_qsl, urljoin, urlparse

# import course data from open csv file.
course_g = Graph()
lecture_g = Graph()
student_g = Graph()
data = Graph()

focu = Namespace('http://focu.io/schema#')
focudata = Namespace('http://focu.io/data#')
dbo = Namespace('http://dbpedia.org/ontology/')
dbpedia = Namespace('http://dbpedia.org/resource/')
dbp = Namespace('http://dbpedia.org/property/')
wd = Namespace('http://www.wikidata.org/entity/')
schema = Namespace('http://schema.org/')

course_g.bind('foaf', FOAF)
course_g.bind('rdfs', RDFS)
course_g.bind('rdf', RDF)
course_g.bind('owl', OWL)
course_g.bind('xsd', XSD)
course_g.bind('focu', focu)
course_g.bind('focudata', focudata)
course_g.bind('dbo', dbo)
course_g.bind('dbpedia', dbpedia)
course_g.bind('dbp', dbp)
course_g.bind('wd', wd)
course_g.bind('schema', schema)

lecture_g.bind('foaf', FOAF)
lecture_g.bind('rdfs', RDFS)
lecture_g.bind('rdf', RDF)
lecture_g.bind('owl', OWL)
lecture_g.bind('xsd', XSD)
lecture_g.bind('focu', focu)
lecture_g.bind('focudata', focudata)
lecture_g.bind('dbo', dbo)
lecture_g.bind('dbpedia', dbpedia)
lecture_g.bind('dbp', dbp)
lecture_g.bind('wd', wd)
lecture_g.bind('schema', schema)

student_g.bind('foaf', FOAF)
student_g.bind('rdfs', RDFS)
student_g.bind('rdf', RDF)
student_g.bind('owl', OWL)
student_g.bind('xsd', XSD)
student_g.bind('focu', focu)
student_g.bind('focudata', focudata)
student_g.bind('dbo', dbo)
student_g.bind('dbpedia', dbpedia)
student_g.bind('dbp', dbp)
student_g.bind('wd', wd)
student_g.bind('schema', schema)

course_file = csv.DictReader(open('Course_CATALOG.csv'))
# import Lecture data from csv file
IS_file = csv.DictReader(open('6741_Lectures.csv'))
AI_file = csv.DictReader(open('6721_Lectures.csv'))
# import students data from csv file
student_file = csv.DictReader(open('student_data.csv'))
taken_file = csv.DictReader(open('student_taken_data.csv'))

# add course outline for COMP6741 & COMP6721
IS_uri = 'file:///C:/unibot/COMP474_6741/course_outline_comp474_6741_w2022.pdf'
AI_uri = 'file:///C:/unibot/COMP6721/outline.pdf'

# add University data
concordia = URIRef(focudata+'concordia')
about_concordia = "Concordia University is an English-language public comprehensive research universitylocated in Montreal, Quebec, Canada."
course_g.add((concordia, RDF.type, focu['University']))
course_g.add((concordia, FOAF.homepage, URIRef('https://www.concordia.ca/')))
course_g.add((concordia, RDFS.label, Literal('Concordia University', lang = "en")))
course_g.add((concordia, RDFS.label, Literal('Université Concordia', lang = "fr")))
course_g.add((concordia, RDFS.comment, Literal(about_concordia, lang = "en")))
course_g.add((concordia, OWL.sameAs, dbpedia.Concordia_University))
course_g.add((concordia, RDFS.seeAlso, dbpedia.Concordia_University))
course_g.add((concordia, OWL.sameAs, wd.Q326342))
course_g.add((concordia, RDFS.seeAlso, wd.Q326342))
    
for row in course_file:
    # convert it from an OrderedDict to a regular dict
    row = dict(row)

    course_key = URIRef(focudata+row['Key'])
    website = row['Website']
    level = row['Level']
    course_name = row['Title']
    
    course_g.add((course_key, RDF.type, focu['Course']))
    course_g.add((course_key, focu['at_university'], focudata['concordia']))
    course_g.add((course_key, schema.name, Literal(course_name, datatype=XSD.string)))
    course_g.add((course_key, focu['has_subject'], Literal(row['Course code'], datatype=XSD.string)))
    course_g.add((course_key, schema.courseCode, Literal(row['Course number'], datatype=XSD.string)))
    course_g.add((course_key, schema.description, Literal(row['Description'], datatype=XSD.string)))
    
    if (course_name == 'Intelligent Systems'):
        IS_course = course_key
        IS_descr = "Knowledge representation and reasoning. Uncertainty and conflict resolution. Design of intelligent systems. Grammar-based, rule-based, and blackboard architectures. A project is required. Laboratory:two hours per week"
        course_g.set((course_key, schema.description, Literal(IS_descr, datatype=XSD.string)))
        course_g.add((course_key, focu['has_outline'], URIRef(IS_uri)))
   
    if (course_name == 'Introduction to Artificial Intelligence'):
        AI_course = course_key
        AI_descr = "The course covers heuristic and adversarial searches for concrete applications. It then discusses automated reasoning, advanced knowledge representation and dealing with uncertainty for Artificial Intelligence applications. Finally, it introduces autoencoders, recurrent neural networks and sequence to sequence models. A project is required. "
        course_g.set((course_key, schema.description, Literal(AI_descr, datatype=XSD.string)))
        course_g.add((course_key, focu['has_outline'], URIRef(AI_uri)))
     
    if (level == 'Graduate'):
        course_g.add((course_key, schema.numberOfCredits, Literal(4, datatype=XSD.integer)))
    else:
        course_g.add((course_key, schema.numberOfCredits, Literal(3, datatype=XSD.integer)))
        
    if (len(website) != 0):
        fullurl = urllib.parse.quote(website, safe="%/:=&?~#+!$,;'@()*[]")
        course_g.add((course_key, RDFS.seeAlso, URIRef(fullurl)))

for row in IS_file:
    row = dict(row)
    
    lecture_key = URIRef(focudata+row['Lecture'])
    topic = URIRef(focudata+row['Topic'])
    slide = URIRef(focudata+row['Slides'])
    
    lecture_g.add((lecture_key, focu['in_course'], IS_course))
    lecture_g.add((lecture_key, RDF.type, focu['Lecture']))
    lecture_g.add((lecture_key, focu['lecture_number'], Literal(row['Lecture_num'], datatype=XSD.integer)))
    lecture_g.add((lecture_key, focu['lecture_name'], Literal(row['Lecture_name'], datatype=XSD.string)))
    lecture_g.add((lecture_key, focu['introduce'], topic))
    
    # add Topic detailed data
    topic_uri = URIRef(dbpedia+row['topic_link'])
    lecture_g.add((topic, RDF.type, focu['Topic']))
    lecture_g.add((topic, RDFS.label, Literal(row['topic_label'], datatype=XSD.string)))
    lecture_g.add((topic, OWL.sameAs, topic_uri))
    
    # add Lecture content - slides data
    lecture_g.add((lecture_key, focu['has_content'], slide))
    # add slide detailed data
    lecture_g.add((slide, RDF.type, focu['slides']))
    lecture_g.add((slide, RDFS.label, Literal(row['Slide_name'], datatype=XSD.string)))
    lecture_g.add((slide, RDFS.seeAlso, URIRef(row['Slides_URI'])))
    
    # add Lecture content - worksheet data
    if (len(row['Worksheets']) != 0):
        worksheet = URIRef(focudata+row['Worksheets'])
        lecture_g.add((lecture_key, focu['has_content'], worksheet))
        # add worksheet detailed data
        lecture_g.add((worksheet, RDF.type, focu['worksheets']))
        lecture_g.add((worksheet, RDFS.label, Literal(row['Worksheet_name'], datatype=XSD.string)))
        lecture_g.add((worksheet, RDFS.seeAlso, URIRef(row['Worksheet_URI'])))
    
    # add Lecture content - lab data
    if (len(row['Labs']) != 0):
        lab = URIRef(focudata+row['Labs'])
        lecture_g.add((lecture_key, focu['has_content'], lab))
        # add lab detailed data
        lecture_g.add((lab, RDF.type, focu['labs']))
        lecture_g.add((lab, RDFS.label, Literal(row['Lab_name'], datatype=XSD.string)))
        lecture_g.add((lab, RDFS.seeAlso, URIRef(row['Lab_URI'])))
    
    # add Lecture content - reading data
    if (len(row['Readings']) != 0):
        reading = URIRef(focudata+row['Readings'])
        lecture_g.add((lecture_key, focu['has_content'], reading))
        # add reading detailed data
        lecture_g.add((reading, RDF.type, focu['readings']))
        # split URI if there are several of them
        for link in row['Reading_URI'].split(';'):
            link = urllib.parse.quote(link, safe="%/:=&?~#+!$,;'@()*[]")
            lecture_g.add((reading, RDFS.seeAlso, URIRef(link)))
        
    # add Lecture content - material data
    if (len(row['Additional_materials']) != 0):
        material = URIRef(focudata+row['Additional_materials'])
        lecture_g.add((lecture_key, focu['has_content'], material))
        # add material detailed data
        lecture_g.add((material, RDF.type, focu['materials']))
        # split URI if there are several of them
        for link in row['Material_URI'].split(';'):
            link = urllib.parse.quote(link, safe="%/:=&?~#+!$,;'@()*[]")
            lecture_g.add((material, RDFS.seeAlso, URIRef(link)))

for row in AI_file:
    row = dict(row)
    
    lecture_key = URIRef(focudata+row['Lecture'])
    topic = URIRef(focudata+row['Topic'])
    slide = URIRef(focudata+row['Slides'])
    
    lecture_g.add((lecture_key, RDF.type, focu['Lecture']))
    lecture_g.add((lecture_key, focu['in_course'], AI_course))
    lecture_g.add((lecture_key, focu['lecture_number'], Literal(row['Lecture_num'], datatype=XSD.integer)))
    lecture_g.add((lecture_key, focu['lecture_name'], Literal(row['Lecture_name'], datatype=XSD.string)))
    lecture_g.add((lecture_key, focu['introduce'], topic))
    
    # add Topic detailed data
    topic_uri = URIRef(dbpedia+row['topic_link'])
    lecture_g.add((topic, RDF.type, focu['Topic']))
    lecture_g.add((topic, RDFS.label, Literal(row['topic_label'], datatype=XSD.string)))
    lecture_g.add((topic, OWL.sameAs, topic_uri))
    
    # add Lecture content - slides data
    lecture_g.add((lecture_key, focu['has_content'], slide))
    # add slide detailed data
    lecture_g.add((slide, RDF.type, focu['slides']))
    lecture_g.add((slide, RDFS.label, Literal(row['Slide_name'], datatype=XSD.string)))
    lecture_g.add((slide, RDFS.seeAlso, URIRef(row['Slides_URI'])))
    
    # add Lecture content - worksheet data
    if (len(row['Worksheets']) != 0):
        worksheet = URIRef(focudata+row['Worksheets'])
        lecture_g.add((lecture_key, focu['has_content'], worksheet))
        # add worksheet detailed data
        lecture_g.add((worksheet, RDF.type, focu['worksheets']))
        lecture_g.add((worksheet, RDFS.label, Literal(row['Worksheet_name'], datatype=XSD.string)))
        lecture_g.add((worksheet, RDFS.seeAlso, URIRef(row['Worksheet_URI'])))
    
    # add Lecture content - lab data
    if (len(row['Labs']) != 0):
        lab = URIRef(focudata+row['Labs'])
        lecture_g.add((lecture_key, focu['has_content'], lab))
        # add lab detailed data
        lecture_g.add((lab, RDF.type, focu['labs']))
        lecture_g.add((lab, RDFS.label, Literal(row['Lab_name'], datatype=XSD.string)))
        lecture_g.add((lab, RDFS.seeAlso, URIRef(row['Lab_URI'])))
    
    # add Lecture content - reading data
    if (len(row['Readings']) != 0):
        reading = URIRef(focudata+row['Readings'])
        lecture_g.add((lecture_key, focu['has_content'], reading))
        # add reading detailed data
        lecture_g.add((reading, RDF.type, focu['readings']))
        # split URI if there are several of them
        for link in row['Reading_URI'].split(';'):
            link = urllib.parse.quote(link, safe="%/:=&?~#+!$,;'@()*[]")
            lecture_g.add((reading, RDFS.seeAlso, URIRef(link)))
        
    # add Lecture content - material data
    if (len(row['Additional_materials']) != 0):
        material = URIRef(focudata+row['Additional_materials'])
        lecture_g.add((lecture_key, focu['has_content'], material))
        # add material detailed data
        lecture_g.add((material, RDF.type, focu['materials']))
        # split URI if there are several of them
        for link in row['Material_URI'].split(';'):
            link = urllib.parse.quote(link, safe="%/:=&?~#+!$,;'@()*[]")
            lecture_g.add((material, RDFS.seeAlso, URIRef(link)))
        
for row in student_file:
    row = dict(row)
    
    student = URIRef(focudata+row['student_key'])
    
    student_g.add((student, RDF.type, focu['Student']))
    student_g.add((student, FOAF.givenName, Literal(row['student_givenName'], lang = "en")))
    student_g.add((student, FOAF.familyName, Literal(row['student_familyName'], lang = "en")))
    student_g.add((student, focu['studies_at'], concordia))
    student_g.add((student, focu['studentId'], Literal(row['studentID'])))
    student_g.add((student, FOAF.mbox, Literal(row['student_mbox'], datatype=XSD.string)))
    for taken in row['take_course'].split(';'):
        student_g.add((student, focu['has_taken'], URIRef(focudata+taken)))
for row in taken_file:
    row = dict(row)
    
    taken_key = URIRef(focudata+row['taken_key'])
    student_g.add((taken_key, RDF.type, focu['Course_Taken']))
    student_g.add((taken_key, focu['is_course'], URIRef(focudata+row['taken_course'])))
    student_g.add((taken_key, focu['has_grade'], Literal(row['taken_grade'])))
    student_g.add((taken_key, focu['in_semester'], Literal(row['taken_semester'])))
        
        
#course_g.serialize(destination='course_graph.ttl', format='turtle')            
#lecture_g.serialize(destination='lecture_graph.ttl', format='turtle')
#student_g.serialize(destination='student_graph.ttl', format='turtle')

data = course_g + lecture_g + student_g
data.serialize(destination='knowledge_base.nt', format='nt')




