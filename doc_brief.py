import os
import PyPDF2
import json
from openai import OpenAI
from api_key import api_key  # Ensure you have your API key imported properly

# Function to extract text from PDF using PdfReader 
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = ''
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Define system role
system_role = 'You are an assistant designed to output JSON with background of geologist and hydrologist, who can also read and translate Dutch research literature.'

# Directory containing PDF files
pdf_directory = r'Update with your directory path'  

# Directory to save JSON files in the same directory as the Python code
script_directory = os.path.dirname(__file__)
json_directory = os.path.join(script_directory, 'doc_Final')
os.makedirs(json_directory, exist_ok=True)

# List all PDF files in the directory
pdf_paths = [os.path.join(pdf_directory, file) for file in os.listdir(pdf_directory) if file.endswith('.pdf')]

# Iterate through each PDF
for pdf_path in pdf_paths:
    print(f"Processing document: {pdf_path}")

    # Extract text from PDF using the updated function
    pdf_text = extract_text_from_pdf(pdf_path)

    # Define user message template with Dutch text and English instruction
    user_msg = f'''Please summarize the following text in English:
                Please extract the following details and present them in the structure provided. 
                Do this for every document and present the output in a JSON file. Create a different JSON file for each document:\n\n
                
               " Document Name: The full title or name of the document as writen on it.",
               " Authors: List the names of the authours",
               " Publication Date",
               " Keywords: List the keywords",
               " Water Quality Parameters (e.g., pH, turbidity, dissolved oxygen, conductivity): List them",
               " Measurements (e.g., specific measurements or data points): List them",
               " Standards and Guidelines (e.g., EPA, WHO standards): List them",
               " Sources of Water (e.g., rivers, lakes, groundwater): List them",
               " Water Usage (e.g., agriculture, drinking water, industrial use): list names of usage",
              " Pollutants: List the names",
              " Impact on Ecosystems: List the impacts",
              " Mitigation Measures: List the measures",
              " Hydrological Data (e.g., flow rates, rainfall data, water levels): List the data",
              " Regulatory and Policy Information: List the information",
              " Technological and Methodological Information (e.g., water treatment or purification technologies): List them",
              " Geographic Information: List them",
              " Statistical and Analytical Data (e.g., trends in water quality or usage): List them",
              " Regulatory Institutions: List them",
              " Locations: List the names of cities, do not include names of countries",
              " Skills:list skills names used on projects",
              " Clients:list Clients names served by a project, include stakeholder names",
              " Projects:list Summarized project names, strategy names, or approach names",
              " Surface Water: list Key information",
              " Groundwater: list Key information",
              " Aquifers: list Key information",
              " Watersheds: list Key information",
              " Rivers: list Key information",
              " Lakes: list Key information",
              " Wetlands: list Key information",
              " Reservoirs: list Key information",
            
        list in a JSON format with keys of 
               " Document Name",
               " Authors",
               " Publication Date",
               " Keywords",
               " Water Quality Parameters",
               " Measurements",
               " Standards and Guidelines",
               " Sources of Water",
               " Water Usage",
              " Pollutants",
              " Impact on Ecosystems",
              " Mitigation Measures",
              " Hydrological Data",
              " Regulatory and Policy Information",
              " Technological and Methodological Information",
              " Geographic Information",
              " Statistical and Analytical Data",
              " Regulatory Institutions",
              " Locations",
              " Skills",
              " Clients",
              " Projects",
              " Surface Water",
              " Groundwater",
              " Aquifers",
              " Watersheds",
              " Rivers",
              " Lakes",
              " Wetlands",
              " Reservoirs",
        If no relevant information is found, write NA in the JSON file, do not write any other similar words such as Not Avalaible e.t.c.
        {pdf_text[:15000]}'''  # Limit to 15000 characters due to API constraints

    # Make a call to the OpenAI API
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        response_format={"type": "json_object"},
        max_tokens=500,
        messages=[
            {"role": "system", "content": system_role},
            {"role": "user", "content": user_msg}
        ]
    )

    # Process the API response
    try:
        api_response = json.loads(completion.choices[0].message.content)
        
        # Create a filename based on the PDF file name
        json_filename = os.path.join(json_directory, os.path.basename(pdf_path).replace('.pdf', '.json'))
        
        # Save the JSON data to a file
        with open(json_filename, 'w') as json_file:
            json.dump(api_response, json_file, indent=4)
            print(f"API response saved to: {json_filename}")

    except json.JSONDecodeError:
        print("Error: Unable to parse API response as JSON.")
        print("API Response Content:")
        print(completion.choices[0].message.content)
        # Handle the error gracefully, such as logging or retrying the API call

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        # Handle other exceptions as needed

print("Processing complete.")
