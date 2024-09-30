import streamlit as st
from neo4j import GraphDatabase
import json
from openai import OpenAI
from api_key import api_key  # Importing your API key from api_key.py

# Neo4j configuration
neo4j_uri = "update with your neo4j uri"
neo4j_user = "update with neo4j user"
neo4j_password = "update with your neo4j password"

# Connect to Neo4j
driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Function to execute Cypher queries
def execute_query(query):
    with driver.session() as session:
        result = session.run(query)
        records = [record.data() for record in result]
        return records

# Function to call OpenAI API to convert natural language to Cypher query
def natural_language_to_cypher(natural_language_query):
    system_msg = "You are a helpful assistant that converts natural language to Cypher queries."
    prompt = f"Convert the following natural language question to a Cypher query:\n\n{natural_language_query}"
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt},
        ],
        max_tokens=150,
        temperature=0.5,
    )
    cypher_query = completion.choices[0].message.content
    return cypher_query.strip()

# Function to call OpenAI API to convert Cypher results to natural language
def cypher_results_to_natural_language(cypher_results):
    system_msg = "You are a helpful assistant that converts Cypher query results to natural language summaries."
    prompt = f"Summarize the following Cypher query results in natural language:\n\n{json.dumps(cypher_results)}"
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt},
        ],
        max_tokens=150,
        temperature=0.5,
    )
    natural_language_summary = completion.choices[0].message.content
    return natural_language_summary.strip()

# Streamlit UI
def main():
    st.title('Natural Language Query Interface for Neo4j')

    # Input field for natural language query
    natural_language_query = st.text_area('Enter your question:', '')

    if st.button('Ask'):
        with st.spinner('Converting natural language to Cypher query...'):
            cypher_query = natural_language_to_cypher(natural_language_query)
            st.text(f"Cypher Query: {cypher_query}")

        with st.spinner('Executing Cypher query...'):
            cypher_results = execute_query(cypher_query)
            st.json(cypher_results)

        with st.spinner('Converting results to natural language...'):
            natural_language_summary = cypher_results_to_natural_language(cypher_results)
            st.text(f"Answer: {natural_language_summary}")

if __name__ == '__main__':
    main()
