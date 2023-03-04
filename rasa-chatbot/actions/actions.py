# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import json
import requests

fuseki_server = 'http://localhost:3030/test/sparql'


# Question 1,what is course COMP 6741 about?
class ActionCourseInfo(Action):

    def name(self) -> Text:
        return "action_course_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        course_subject = tracker.slots['course_subject'].upper()
        course_code = tracker.slots['course_code']
        query_var = """
                PREFIX focu: <http://focu.io/schema#>
                PREFIX schema: <http://schema.org/>
                SELECT ?description
                WHERE {
                  ?course focu:has_subject "%s".
                  ?course schema:courseCode "%s".
                  ?course schema:description ?description.
                }"""

        response = requests.post(fuseki_server, data={'query': query_var % (course_subject, course_code)})
        res = response.json()
        description = "Sorry, I did not find this course for you."
        for row in res['results']['bindings']:
            description = row['description']['value']
        dispatcher.utter_message(text=description)

        return []


# Question 2,which topics are Bo Wang competent in?
class ActionStudentCompetency(Action):

    def name(self) -> Text:
        return "action_student_competency"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        student_name = str(tracker.slots['student'])
        if len(student_name.split()) <= 1:
            dispatcher.utter_message(text="Please enter student's full name, separate with a space.")
        else:
            student_last = student_name.split()[1].capitalize()
            student_first = student_name.split()[0].capitalize()
            query_var = """
                PREFIX focu: <http://focu.io/schema#>
                PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                SELECT DISTINCT ?label ?link
                WHERE {
                  ?student foaf:givenName "%s"@en.
                  ?student foaf:familyName "%s"@en.
                  ?student focu:has_taken ?course_take.
                  ?course_take focu:is_course ?course.
                  ?course_take focu:has_grade ?grade.
                  ?lecture focu:in_course ?course.
                  ?lecture focu:has_content ?content.
                  ?content focu:introduce ?topic.
                  ?topic rdfs:label ?label.
                  ?topic owl:sameAs|rdfs:seeAlso ?link.
                  FILTER (?grade = "A" || ?grade = "A+" || ?grade = "A-" || ?grade = "B" || ?grade = "B+" || ?grade = "B-" || ?grade = "C" || ?grade = "C+") . 
                }"""
            response = requests.post(fuseki_server, data={'query': query_var % (student_first, student_last)})
            res = response.json()
            if len(res['results']['bindings']) == 0:
                dispatcher.utter_message(text="Sorry, I did not find anything for this student.")
            else:
                dispatcher.utter_message(text="Here are the topics " + student_name + " competent in.")
                for row in res['results']['bindings']:
                    description = row['label']['value'] + ": " + row['link']['value']
                    dispatcher.utter_message(text=description)

        return []

# Question 3,which course teaches knowledge graph?
class ActionCourseFromTopic(Action):

    def name(self) -> Text:
        return "action_course_from_topic"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        topic = str(tracker.slots['topic']).lower()
        query_var = """
            PREFIX focu: <http://focu.io/schema#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX schema: <http://schema.org/>
            SELECT DISTINCT ?name (Count(?name) as ?total) ?course_subject ?course_code
            WHERE {
              ?course focu:has_subject ?course_subject.
              ?course schema:courseCode ?course_code.  
              ?course schema:name ?name.
              ?lecture focu:in_course ?course.
              ?lecture focu:has_content ?content.
              ?content focu:introduce ?topic.
              ?topic rdfs:label ?topic_label.
              FILTER (lcase(str(?topic_label)) = "%s").
            }
            GROUP BY ?name ?course_subject ?course_code
            ORDER BY DESC (?total)"""
        response = requests.post(fuseki_server, data={'query': query_var % topic})
        res = response.json()
        if len(res['results']['bindings']) == 0:
            dispatcher.utter_message(text="Sorry, I did not find any course for this topic.")
        else:
            for row in res['results']['bindings']:
                course = row['course_subject']['value']+row['course_code']['value'] + " " +row['name']['value'] + " introduces " + row['total']['value'] + " times"
                dispatcher.utter_message(text=course)

        return []

# Question 4,which topics are covered in COMP 6741?
class ActionTopicFromCourse(Action):

    def name(self) -> Text:
        return "action_topic_from_course"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        course_subject = tracker.slots['course_subject'].upper()
        course_code = tracker.slots['course_code']
        query_var = """
            PREFIX focu: <http://focu.io/schema#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX schema: <http://schema.org/>
            SELECT DISTINCT ?label ?link ?content_label ?content_link
            WHERE {
              ?course focu:has_subject "%s".
              ?course schema:courseCode "%s".
              ?lecture focu:in_course ?course.
              ?lecture focu:has_content ?content.
              ?content rdfs:label ?content_label.
              ?content owl:sameAs|rdfs:seeAlso ?content_link.
      		  ?content focu:introduce ?topic.
              ?topic rdfs:label ?label.
              ?topic owl:sameAs|rdfs:seeAlso ?link.
            }"""
        response = requests.post(fuseki_server, data={'query': query_var % (course_subject,course_code)})
        res = response.json()
        if len(res['results']['bindings']) == 0:
            dispatcher.utter_message(text="Sorry, I did not find anything for this course.")
        else:
            for row in res['results']['bindings']:
                topic = row['label']['value'] + ": " + row['link']['value'] + " in " + row['content_label']['value'] + ": " + row['content_link']['value']
                dispatcher.utter_message(text=topic)

        return []

# Question 5,what is Bo Wang’s Email?
class ActionStudentEmail(Action):

    def name(self) -> Text:
        return "action_student_email"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        student_name = str(tracker.slots['student'])
        if len(student_name.split()) <= 1:
            dispatcher.utter_message(text="Please enter student's full name, separate with a space.")
        else:
            student_last = student_name.split()[1].capitalize()
            student_first = student_name.split()[0].capitalize()
            query_var = """
                        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                        SELECT ?email
                        WHERE {
                            ?student foaf:givenName "%s"@en.
                            ?student foaf:familyName "%s"@en.
                            ?student foaf:mbox ?email.
                        }"""
            response = requests.post(fuseki_server, data={'query': query_var % (student_first, student_last)})
            res = response.json()
            if len(res['results']['bindings']) == 0:
                dispatcher.utter_message(text="Sorry, I did not find an email for this student.")
            else:
                for row in res['results']['bindings']:
                    email = student_name + "'s email is " + row['email']['value']
                    dispatcher.utter_message(text=email)

        return []
# Question 6,what are the suggested readings for COMP 6741?
class ActionCourseReading(Action):

    def name(self) -> Text:
        return "action_course_reading"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        course_subject = tracker.slots['course_subject'].upper()
        course_code = tracker.slots['course_code']
        query_var = """
            PREFIX focu: <http://focu.io/schema#>
            PREFIX schema: <http://schema.org/>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?link
            WHERE {
              ?course focu:has_subject "%s".
              ?course schema:courseCode "%s".
              ?lecture focu:in_course ?course.
              ?lecture focu:has_content ?reading.
              ?reading a focu:readings.
              ?reading owl:sameAs|rdfs:seeAlso ?link.
            }"""
        response = requests.post(fuseki_server, data={'query': query_var % (course_subject,course_code)})
        res = response.json()
        if len(res['results']['bindings']) == 0:
            dispatcher.utter_message(text="Sorry, I did not find any reading for this course.")
        else:
            dispatcher.utter_message(text="Here are the suggested reading's URL:")
            for row in res['results']['bindings']:
                reading = row['link']['value']
                dispatcher.utter_message(text=reading)

        return []

# Question 7,how many credits Bo Wang gained at Concordia?
class ActionStudentCredit(Action):

    def name(self) -> Text:
        return "action_student_credit"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        student_name = str(tracker.slots['student'])
        university = tracker.slots['university'].capitalize()
        if len(student_name.split()) <= 1:
            dispatcher.utter_message(text="Please enter student's full name, separate with a space.")
        else:
            student_last = student_name.split()[1].capitalize()
            student_first = student_name.split()[0].capitalize()
            query_var = """
                        PREFIX focu: <http://focu.io/schema#>
                        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                        PREFIX schema: <http://schema.org/>
                        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        SELECT (SUM(xsd:integer(?credit)) as ?total)
                        WHERE {
                          ?uni rdfs:label "%s University"@en.
                          ?student foaf:givenName "%s"@en.
                          ?student foaf:familyName "%s"@en.
                          ?student focu:has_taken ?course_take.
                          ?course_take focu:is_course ?course.
                          ?course_take focu:has_grade ?grade.
                          ?course focu:at_university ?uni.
                          ?course schema:numberOfCredits ?credit.
                          FILTER (?grade = "A" || ?grade = "A+" || ?grade = "A-" || ?grade = "B" || ?grade = "B+" || ?grade = "B-" || ?grade = "C" || ?grade = "C+") . 
                        }"""
            response = requests.post(fuseki_server, data={'query': query_var % (university, student_first, student_last)})
            res = response.json()
            for row in res['results']['bindings']:
                answer = student_name + " gained " + row['total']['value']+" credits"
                dispatcher.utter_message(text=answer)

        return []
# Question 8,how many lectures are in COMP 6741?
class ActionCourseLectureCount(Action):

    def name(self) -> Text:
        return "action_course_lecture_count"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        course_subject = tracker.slots['course_subject'].upper()
        course_code = tracker.slots['course_code']
        query_var = """
            PREFIX focu: <http://focu.io/schema#>
            PREFIX schema: <http://schema.org/>
            SELECT (count(?lecture) as ?total)
            WHERE {
              ?course focu:has_subject "%s".
              ?course schema:courseCode "%s".
              ?lecture focu:in_course ?course.
            }"""
        response = requests.post(fuseki_server, data={'query': query_var % (course_subject, course_code)})
        res = response.json()
        if len(res['results']['bindings']) == 0:
            dispatcher.utter_message(text="Sorry, I did not find this course.")
        else:
            for row in res['results']['bindings']:
                answer = course_subject + course_code + " contains " + row['total']['value']+" lectures"
                dispatcher.utter_message(text=answer)

        return []
# Question 9,how many courses did Bo Wang attend at Concordia?
class ActionStudentAttend(Action):

    def name(self) -> Text:
        return "action_student_attend"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        student_name = str(tracker.slots['student'])
        university = tracker.slots['university'].capitalize()
        if len(student_name.split()) <= 1:
            dispatcher.utter_message(text="Please enter student's full name, separate with a space.")
        else:
            student_last = student_name.split()[1].capitalize()
            student_first = student_name.split()[0].capitalize()
            query_var = """
                        PREFIX focu: <http://focu.io/schema#>
                        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        SELECT (Count(?course) as ?total)
                        WHERE {
                          ?uni rdfs:label "%s University"@en.
                          ?student foaf:givenName "%s"@en.
                          ?student foaf:familyName "%s"@en.
                          ?student focu:has_taken ?course_take.
                          ?course_take focu:is_course ?course.
                          ?course focu:at_university ?uni.
                        }"""
            response = requests.post(fuseki_server, data={'query': query_var % (university, student_first, student_last)})
            res = response.json()
            for row in res['results']['bindings']:
                answer = student_name + " attended " + row['total']['value']+" courses"
                dispatcher.utter_message(text=answer)

        return []
# Question 10,how many credits is COMP 6741 worth?
class ActionCourseCredit(Action):

    def name(self) -> Text:
        return "action_course_credit"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        course_subject = tracker.slots['course_subject'].upper()
        course_code = tracker.slots['course_code']
        query_var = """
            PREFIX focu: <http://focu.io/schema#>
            PREFIX schema: <http://schema.org/>
            SELECT ?credit
            WHERE {
              ?course focu:has_subject "%s".
              ?course schema:courseCode "%s".
              ?course schema:numberOfCredits ?credit.
            }"""
        response = requests.post(fuseki_server, data={'query': query_var % (course_subject, course_code)})
        res = response.json()
        if len(res['results']['bindings']) == 0:
            dispatcher.utter_message(text="Sorry, I did not find this course.")
        else:
            for row in res['results']['bindings']:
                answer = course_subject + course_code + " is worth " + row['credit']['value']+" credits"
                dispatcher.utter_message(text=answer)

        return []

# Question 11,which topics are covered in Lab #4 of COMP 6721?
class ActionTopicFromContent(Action):

    def name(self) -> Text:
        return "action_topic_from_content"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        get_content = True
        course_subject = tracker.slots['course_subject'].upper()
        course_code = tracker.slots['course_code']
        content = tracker.slots['content'].lower()
        if content.find("lab") >= 0:
            if content.find("#") >= 0:
                lab = "lab" + content[content.index("#") + 1:].zfill(2)
            else:
                lab = "lab" + content[-2:]
            query_var = """
                PREFIX focu: <http://focu.io/schema#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                PREFIX schema: <http://schema.org/>
                SELECT ?label ?link
                WHERE {
                  ?course focu:has_subject "%s".
                  ?course schema:courseCode "%s".
                  ?lecture focu:in_course ?course.
                  ?lecture focu:has_content ?content.
                  ?content a focu:labs.
                  ?content rdfs:label "%s".	
                  ?content focu:introduce ?topic.
                  ?topic rdfs:label ?label.
                  ?topic owl:sameAs|rdfs:seeAlso ?link.
                }"""
            response = requests.post(fuseki_server, data={'query': query_var % (course_subject, course_code, lab)})
        elif content.find("worksheet") >= 0:
            if content.find("#") >= 0:
                worksheet = "worksheet" + content[content.index("#") + 1:].zfill(2)
            else:
                worksheet = "worksheet" + content[-2:]
            query_var = """
                PREFIX focu: <http://focu.io/schema#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                PREFIX schema: <http://schema.org/>
                SELECT ?label ?link
                WHERE {
                  ?course focu:has_subject "%s".
                  ?course schema:courseCode "%s".
                  ?lecture focu:in_course ?course.
                  ?lecture focu:has_content ?content.
                  ?content a focu:worksheets.
                  ?content rdfs:label "%s".	
                  ?content focu:introduce ?topic.
                  ?topic rdfs:label ?label.
                  ?topic owl:sameAs|rdfs:seeAlso ?link.
                }"""
            response = requests.post(fuseki_server,
                                     data={'query': query_var % (course_subject, course_code, worksheet)})
        elif content.find("slide") >= 0:
            if content.find("#") >= 0:
                slide = "slide" + content[content.index("#") + 1:].zfill(2)
            else:
                slide = "slide" + content[-2:]
            query_var = """
                PREFIX focu: <http://focu.io/schema#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                PREFIX schema: <http://schema.org/>
                SELECT ?label ?link
                WHERE {
                  ?course focu:has_subject "%s".
                  ?course schema:courseCode "%s".
                  ?lecture focu:in_course ?course.
                  ?lecture focu:has_content ?content.
                  ?content a focu:slides.
                  ?content rdfs:label "%s".	
                  ?content focu:introduce ?topic.
                  ?topic rdfs:label ?label.
                  ?topic owl:sameAs|rdfs:seeAlso ?link.
                }"""
            response = requests.post(fuseki_server, data={'query': query_var % (course_subject, course_code, slide)})
        else:
            get_content = False

        if get_content:
            res = response.json()
            if len(res['results']['bindings']) == 0:
                dispatcher.utter_message(text="Sorry, I did not find anything for this course content.")
            else:
                for row in res['results']['bindings']:
                    topic = row['label']['value'] + ": " + row['link']['value']
                    dispatcher.utter_message(text=topic)
        else:
            dispatcher.utter_message(text="Sorry, I did not find anything for this course content.")

        return []

# Question 12,Can you list all related course content for knowledge graph?
class ActionContentFromTopic(Action):

    def name(self) -> Text:
        return "action_content_from_topic"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        topic = str(tracker.slots['topic']).lower()
        query_var = """
            PREFIX focu: <http://focu.io/schema#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX schema: <http://schema.org/>
            SELECT DISTINCT ?topic_label ?course_subject ?course_code ?lecture_number ?content_label ?link
            WHERE {
              ?course focu:has_subject ?course_subject.
              ?course schema:courseCode ?course_code.
              ?lecture focu:in_course ?course.
  			  ?lecture focu:lecture_number ?lecture_number.	
              ?lecture focu:has_content ?content.
  			  optional {?content rdfs:label ?content_label. }.
              ?content focu:introduce ?topic.
              ?content owl:sameAs|rdfs:seeAlso ?link.
              ?topic rdfs:label ?topic_label.
              FILTER (lcase(str(?topic_label)) = "%s").
            }"""
        response = requests.post(fuseki_server, data={'query': query_var % topic})
        res = response.json()
        if len(res['results']['bindings']) == 0:
            dispatcher.utter_message(text="Sorry, I did not find any course for this topic.")
        else:
            for row in res['results']['bindings']:
                if "content_label" in row:
                    content_label = row['content_label']['value']
                else:
                    content_label = "other material"
                course = topic + " is covered in " + row['course_subject']['value']+row['course_code']['value'] + \
                         "->lecture" + row['lecture_number']['value'] + "->" + content_label + \
                         "->" + row['link']['value']
                dispatcher.utter_message(text=course)

        return []

# Question 13,how many triples in total?
class ActionTotalTriple(Action):

    def name(self) -> Text:
        return "action_total_triple"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        query_var = """
            SELECT (Count(?s) as ?total)
            WHERE {
              ?s ?p ?o.
            }"""
        response = requests.post(fuseki_server, data={'query': query_var})
        res = response.json()
        for row in res['results']['bindings']:
            answer = "there are totally " + row['total']['value']+" triples"
            dispatcher.utter_message(text=answer)

        return []
# Question 14,how many courses in total?
class ActionCourseTotal(Action):

    def name(self) -> Text:
        return "action_course_total"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        query_var = """
            PREFIX focu: <http://focu.io/schema#>
            SELECT (Count(?s) as ?total)
            WHERE {
              ?s a focu:Course.
            }"""
        response = requests.post(fuseki_server, data={'query': query_var})
        res = response.json()
        for row in res['results']['bindings']:
            answer = "there are totally " + row['total']['value']+" courses"
            dispatcher.utter_message(text=answer)

        return []