import streamlit as st
from openai import OpenAI
import os
import json
from api_key import api_key
import tiktoken  # For token counting
import time  # For rate limiting
from rapidfuzz import fuzz
import spacy
import numpy as np

# Set your OpenAI API key
client = OpenAI(api_key=api_key)

# Initialize tokenizer for a compatible model, e.g., gpt-3.5-turbo
tokenizer = tiktoken.get_encoding("cl100k_base")

# Load spaCy model for semantic similarity
nlp = spacy.load('en_core_web_md')

# Function to read a JSON file
def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Function to read all JSON files from a folder
def read_all_json_files(folder_path):
    documents = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path) and file_name.endswith(".json"):
            documents.append(read_json_file(file_path))
    return documents

# Function to filter documents using fuzzy matching
def filter_documents_by_keyword(documents, keyword, threshold=70):
    filtered_documents = []
    keyword_lower = keyword.lower()

    for doc in documents:
        doc_str = json.dumps(doc).lower()
        # Check if there's a match above the threshold
        if fuzz.partial_ratio(doc_str, keyword_lower) >= threshold:
            filtered_documents.append(doc)
    
    return filtered_documents

# Function to chunk the documents based on token length
def chunk_documents(documents, max_tokens=3000):
    chunks = []
    current_chunk = []
    current_tokens = 0

    for doc in documents:
        doc_str = json.dumps(doc)
        doc_tokens = len(tokenizer.encode(doc_str))

        if current_tokens + doc_tokens > max_tokens:
            chunks.append(current_chunk)
            current_chunk = [doc]
            current_tokens = doc_tokens
        else:
            current_chunk.append(doc)
            current_tokens += doc_tokens

    if current_chunk:
        chunks.append(current_chunk)
        
    return chunks

# Function to get a response from OpenAI API
def get_openai_response(documents_chunk, question):
    documents_str = "\n\n".join([json.dumps(doc) for doc in documents_chunk])
    prompt = (
        f"Here are several documents:\n\n{documents_str}\n\n"
        f"Given these documents, answer the following question in detail. "
        f"Please identify any document that supports the answer, even if the support is indirect or based on related concepts, and summarize the relevant content.\n"
        f"Question: {question}"
    )
    system_msg = "You are a helpful assistant that reads and summarizes JSON documents."

    try:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt},
            ],
            max_tokens=4096
        )
        response_text = completion.choices[0].message.content.strip()
        return response_text
    except Exception as e:
        return f"Error: {str(e)}"

# Function to compute semantic similarity
def get_semantic_similarity(texts):
    vectors = np.array([nlp(text).vector for text in texts])
    similarity_matrix = np.dot(vectors, vectors.T) / (np.linalg.norm(vectors, axis=1)[:, None] * np.linalg.norm(vectors, axis=1))
    return similarity_matrix

# Function to combine similar answers
def combine_similar_answers(answers, threshold=0.7):
    vectors = np.array([nlp(answer).vector for answer in answers])
    similarity_matrix = get_semantic_similarity(answers)
    
    combined_answers = []
    visited = set()
    for i in range(len(answers)):
        if i not in visited:
            similar_indices = set(np.where(similarity_matrix[i] > threshold)[0])
            visited.update(similar_indices)
            combined_answers.append(answers[i])

    return "\n\n".join(combined_answers)

st.title("Water Management Research Assistant")

# Allow users to input folder path dynamically
folder_path = st.text_input("Enter the folder path for JSON documents", value=r'update with your folder name that contains the JSON files')

if folder_path and os.path.exists(folder_path):
    documents = read_all_json_files(folder_path)
    question = st.text_input("Ask a question about the documents")
    
    if st.button("Get Answer"):
        if question:
            keyword_filtered_docs = filter_documents_by_keyword(documents, question)
            
            if keyword_filtered_docs:
                document_chunks = chunk_documents(keyword_filtered_docs)
                answers = []
                for chunk in document_chunks:
                    answer = get_openai_response(chunk, question)
                    answers.append(answer)
                    time.sleep(1)  # Adjust this delay as necessary
                
                # Combine and process the responses to eliminate repetition
                combined_answer = combine_similar_answers(answers)
                if "None of the provided documents" in combined_answer:
                    combined_answer = "It appears that most documents do not directly mention chlorine. However, here are the details:\n\n" + combined_answer

                st.text_area("Answer", combined_answer, height=200)
            else:
                # If no documents match, fall back to using all documents
                st.write("searching...")
                document_chunks = chunk_documents(documents)
                answers = []
                for chunk in document_chunks:
                    answer = get_openai_response(chunk, question)
                    answers.append(answer)
                    time.sleep(1)
                
                # Combine and process the responses
                combined_answer = combine_similar_answers(answers)
                st.text_area("Answer", combined_answer, height=200)
        else:
            st.write("Please provide a question.")
else:
    st.write("Please provide a valid folder path.")
