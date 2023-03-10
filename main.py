from tika import parser
import spacy
import re
import os
from spacy.matcher import Matcher # to detect sequences of tokens
from spacy.matcher import PhraseMatcher # for matching sequences of tokens
from nltk.corpus import stopwords #contains a collection of nlp words

# load pre-trained model
nlp = spacy.load('en_core_web_sm')

""" 
   This code snippet is used to read the skills.txt file and store it in the list, skill.
   Then, a PhraseMatcher object, skillsmatcher is created which is used to match the phrases.
   The patterns are created using the make_doc function of the nlp object.
   The skillsmatcher is initialized with the list of patterns created. Finally, the name, "Skills" is given to the matcher.
"""
base_path = os.path.dirname(__file__)
file = os.path.join(base_path,"skills.txt")
file = open(file, "r", encoding='utf-8')
skill = [line.strip().lower() for line in file]
skillsmatcher = PhraseMatcher(nlp.vocab)
patterns = [nlp.make_doc(text) for text in skill if len(nlp.make_doc(text)) < 10]
skillsmatcher.add("Skills", None, *patterns)

# initialize matcher with a vocab
matcher = Matcher(nlp.vocab)

####################-- Extract data --####################

def extract_data(file_path):
    file_data = parser.from_file(file_path)
    resume_text = file_data['content']
    return resume_text

####################--Extract Name --####################

def extract_name(resume_text):
    nlp_text = nlp(resume_text)
    
    # First name and Last name1 are always Proper Nouns
    pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
    
    matcher.add('NAME', [pattern], on_match = None)
    
    matches = matcher(nlp_text)
    
    for match_id, start, end in matches:
        span = nlp_text[start:end]
        return span.text

####################-- Extract Email --####################    

def get_email_addresses(string):
    r = re.compile(r'[\w\.-]+@[\w\.-]+')
    return r.findall(string)
    
####################--Extract Mobile number --####################

def get_phone_numbers(string):
    r = re.compile(r'(\d{3}[-\.\s]++\d{3}[-\.\s]\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]++\d{4}|\d{3}[-\.\s]++\d{4})')
    phone_numbers = r.findall(string)
    return [re.sub(r'\D', '', num) for num in phone_numbers]

####################--Extract Skills --####################

def extract_skills(text):

        skills = []

        __nlp = nlp(text.lower())
        # Only run nlp.make_doc to speed things up

        matches = skillsmatcher(__nlp)
        for match_id, start, end in matches:
            span = __nlp[start:end]
            skills.append(span.text)
        skills = list(set(skills))
        return skills

####################--Extract Education --####################

# Grad all general stop words
STOPWORDS = set(stopwords.words('english'))

# Education Degrees
EDUCATION = [
            'BE', 'BSc','B.E.', 'B.E', 'BS', 'B.S', 
            'ME', 'M.E', 'M.E.', 'MS', 'M.S', 
            'BTECH', 'B.TECH', 'M.TECH', 'MTECH', 
            'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII','BA',
    
        ]

def extract_education(resume_text):
    nlp_text = nlp(resume_text)

    # Sentence Tokenizer
    nlp_text = [sent.text.strip() for sent in nlp_text.sents]

    edu = {}
    # Extract education degree
    for index, text in enumerate(nlp_text):
        for tex in text.split():
            # Replace all special symbols
            tex = re.sub(r'[?|$|.|!|,]', r'', tex) # update ?,$,.,!,',' with blank space
            if tex.upper() in EDUCATION and tex not in STOPWORDS:
                edu[tex] = text + nlp_text[index]

    education = []
    for key in edu.keys():
        year = re.search(re.compile(r'(((20|19)(\d{2})))'), edu[key])
        if year:
            education.append((key, ''.join(year[0])))
        else:
            education.append(key)
    return education

####################--Extract School/ University --####################

def extract_university(resume_text):
    sub_patterns = ['[A-Z][a-z]* University','[A-Z][a-z]* Educational Institute',
                    'Institute [A-Za-zÀ-ȕ]* [A-Za-zÀ-ȕ]*', 
                    'University *[A-Za-zÀ-ȕ] [A-Za-zÀ-ȕ]*',
                    '[A-Za-zÀ-ȕ]* School', 
                    '[A-Za-zÀ-ȕ]* [A-Za-zÀ-ȕ]* [A-Za-zÀ-ȕ]* School'

                ]
    pattern = '({})'.format('|'.join(sub_patterns))
    matches = re.findall(pattern, resume_text)
    return matches
####################--Extract Company --####################

def extract_company(resume_text):
    sub_patterns = ['[A-Z][a-z]* [A-Z][a-z]* Private Limited','[A-Z][a-z]* [A-Z][a-z]* Pvt. Ltd.','[A-Z][a-z]* [A-Z][a-z]* Inc.', '[A-Z][a-z]* LLC',
                    ]
    pattern = '({})'.format('|'.join(sub_patterns))
    Exp = re.findall(pattern, resume_text)

####################--Extract Work Experience --####################

def extract_work_experience(resume_text):
    
    # Define the regular expression patterns to match work experience
    patterns = [
        r'(?:Employment|Work|Experience)[\s\w\d\-\(\)]+?:(.*?)\n',
        r'(?:Employment|Work|Experience)[\s\w\d\-\(\)]+?\n(.*?)\n\n',
        r'(?:Employment|Work|Experience)[\s\w\d\-\(\)]+?\n(.*?)\n',
        r'(?:Work|Experience)[\s\w\d\-\(\)]+?:\n(.*?)\n\n',
        r'(?:Work|Experience)[\s\w\d\-\(\)]+?:\n(.*?)\n',
        r'(?<=Experience)[\s\w\d\-\(\)]+?(\d{4}\s-\s\d{4}|\d{2}/\d{4}\s-\s\d{2}/\d{4})[\s\w\d\-\(\)]+?\n(.*?)\n\n',
        r'(?<=Experience)[\s\w\d\-\(\)]+?(\d{4}\s-\s\d{4}|\d{2}/\d{4}\s-\s\d{2}/\d{4})[\s\w\d\-\(\)]+?\n(.*?)\n',
    ]

    # Match the regular expression patterns on the resume text
    work_experience = []
    for pattern in patterns:
        matches = re.findall(pattern, resume_text, re.DOTALL | re.IGNORECASE)
        if matches:
            work_experience.extend(matches)
    # print(work_experience)
    return work_experience

####################--Extract all data --####################

def resume_data(resume_file):

    # Extract text from the resume file
    resume_text = extract_data(resume_file)

    # Extract name, email, and phone number
    name = extract_name(resume_text)
    try:
        first_name, last_name = name.split(" ")
    except ValueError:
        first_name = name
        last_name = None

    email = get_email_addresses(resume_text)
    phone = get_phone_numbers(resume_text)

    # Extract skills, education, company, and experience
    skills = extract_skills(resume_text)
    education = extract_education(resume_text)
    company = extract_company(resume_text)
    experience = extract_work_experience(resume_text)

    # Print extracted information

    ##################################################
    return {
            "first_name": first_name,
            "last_name": last_name,
            "email": str(email),
            "mobile": str(phone),
            "experience_details":str(experience),
            "educational_details" : str(education),
            "skills": str(skills),
        }
   
    

