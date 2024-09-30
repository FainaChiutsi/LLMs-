# LLMs-
Use of LLMs for text extraction, Knowledge graph and Streamlit UI
1.	Set Up the Environment
•	Make sure you have Python, Neo4j, and an OpenAI API key.
2.	Process the Documents
•	Run the doc_brief Python code to extract the document metadata into JSON files. These files should include details like document names, authors, keywords, etc.
•	Place the JSON files in a directory specified in the project for processing.
      3. Build the Knowledge Graph
•	Run the knowledge graph script next, which connects to Neo4j, creates nodes for each document and its related entities, and generates relationships using OpenAI.
     4. Visualize the Graph
•	Run the Streamlit_app script last. This launches the Streamlit web app to visualize and explore the knowledge graph. The app will allow you to search and interact with the nodes and relationships in the graph.
     5. Querying the Streamlit app based on JSON file information
•	Run the script named interface as an alternative way to query the Streamlit user interface.


