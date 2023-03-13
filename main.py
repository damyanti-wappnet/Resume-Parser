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
# to call all the vocabulary of the NLP and pass it into the Matcher() constructor. 
matcher = Matcher(nlp.vocab)

####################-- Extract data --####################
# Function created to extract data from resume using from_file() method of Tika library

def extract_data(file_path):
    file_data = parser.from_file(file_path)
    resume_text = file_data['content']
    return resume_text

####################--Extract Name --####################
# function created to extract first name and last name 
def extract_name(resume_text):
     
    # Pass text as parameter to the matcher
    nlp_text = nlp(resume_text)
    
    # First name and Last name1 are always Proper Nouns
    pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
    
    #add pattern to matcher that will used to find the pattern in text
    matcher.add('NAME', [pattern], on_match = None)
    
    #to call all the vocabulary of the NLP and pass text into the Matcher() constructor.
    matches = matcher(nlp_text)

    #Return all matched text
    for match_id, start, end in matches:
        span = nlp_text[start:end]
        return span.text

####################-- Extract Email --####################    
# function created to extract email address

def get_email_addresses(string):

    #regular expression to match e-mail
    r = re.compile(r'[\w\.-]+@[\w\.-]+')
    return r.findall(string)
    
####################--Extract Mobile number --####################

def get_phone_numbers(resume_text):

    # Define the regular expression pattern to match mobile phone numbers
    pattern = r'\b(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4})\b'

    # Search for all matches in the resume text
    matches = re.findall(pattern, resume_text)

    # Remove any non-numeric characters from the phone numbers
    matches = [re.sub(r'\D', '', match) for match in matches]

    # Filter out any phone numbers that are less than 10 digits long
    matches = [match for match in matches if len(match) >= 10]

    # Return the list of phone numbers
    return matches

####################--Extract Skills --####################
# function created to extract skills 

def extract_skills(text):

        skills = []

        # convert text in lower case and store it
        __nlp = nlp(text.lower())

        #load text in skillmatcher which is used to match the phrases.
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
            'BE', 'BSc','B.E.', 'B.E', 'BS', 'B.S', 'BEng','MEng','BArch','MArch','MBA','BBA',
            'ME', 'M.E', 'M.E.', 'MS', 'M.S', 'BCA','MCA','BEd','MEd','BFA','MFA','LLB','LLM','BPharm','MPharm',
            'BTECH', 'B.TECH', 'M.TECH', 'MTECH', 'BCom','MCom','BHMS', 'MHMS', 'BDS', 'MDS', 'BVSc', 'MVSc','MBBS',
            'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII','BA','MD', 'Ph.D','12th', '10th',
    
        ]

#function created to extract educatin from resume
def extract_education(resume_text):

    #load text in npl_text variable
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

    #extract year of degree
    education = []
    for key in edu.keys():
        year = re.search(re.compile(r'(((20|19)(\d{2})))'), edu[key])
        if year:
            education.append((key, ''.join(year[0])))
        else:
            education.append(key)
    return education

####################--Extract School/ University --####################
# function created to extract university or College from resume

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
    sub_patterns = ['[A-Z][a-z]* [A-Z][a-z]* Private Limited','[A-Z][a-z]* [A-Z][a-z]* Pvt. Ltd.','[A-Z][a-z]* [A-Z][a-z]* Inc.', '[A-Z][a-z]* LLC','[A-Z][a-z]* System',
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
            work_experience = [re.sub(r'[\n, ]+', ' ', item).strip() for item in work_experience]
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
    clg = extract_university(resume_text)
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
   
    

