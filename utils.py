import re
import zipfile
import os
import numpy as np
import spacy
import docx2txt
from PyPDF2 import PdfReader
from spacy.cli import download


nlp = spacy.load("en_core_web_sm")

def read_pdf_text(uploaded_file):
    pdf_reader = PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def read_docx_text(uploaded_file):
    return docx2txt.process(uploaded_file)

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text

def tokenize(text):
    return text.split()

def compute_cosine_similarity(vector1, vector2):
    dot_product = np.dot(vector1, vector2)
    norm1 = np.linalg.norm(vector1)
    norm2 = np.linalg.norm(vector2)
    similarity = dot_product / (norm1 * norm2)
    return similarity

def custom_matching_percentage(job_description, resume_texts):
    job_description = preprocess_text(job_description)
    job_desc_tokens = tokenize(job_description)
    
    vocabulary = set(job_desc_tokens)
    for resume_text in resume_texts:
        resume_text = preprocess_text(resume_text)
        resume_tokens = tokenize(resume_text)
        vocabulary.update(resume_tokens)
    
    job_desc_vector = np.array([job_desc_tokens.count(word) for word in vocabulary])
    resume_vectors = []
    for resume_text in resume_texts:
        resume_text = preprocess_text(resume_text)
        resume_tokens = tokenize(resume_text)
        resume_vector = np.array([resume_tokens.count(word) for word in vocabulary])
        resume_vectors.append(resume_vector)
    
    similarities = []
    for resume_vector in resume_vectors:
        similarity = compute_cosine_similarity(job_desc_vector, resume_vector)
        similarities.append(similarity)
    
    similarities = np.array(similarities) * 100
    return similarities

def extract_entities_keywords(text):
    doc = nlp(text)
    entities = [ent.text for ent in doc.ents]
    keywords = [token.text for token in doc if not token.is_stop and token.is_alpha]
    return entities, keywords

def generate_feedback(job_description, resumes):
    feedback = {}
    job_entities, job_keywords = extract_entities_keywords(job_description)
    
    for resume_name, resume_text in resumes.items():
        resume_entities, resume_keywords = extract_entities_keywords(resume_text)
        
        missing_entities = [entity for entity in job_entities if entity not in resume_entities]
        missing_keywords = [keyword for keyword in job_keywords if keyword not in resume_keywords]
        
        feedback[resume_name] = {
            "missing_entities": missing_entities,
            "missing_keywords": missing_keywords
        }
    
    return feedback
