import json
import os
from py2neo import Graph, Node, Relationship
import openai
from api_key import api_key

# OpenAI API key
openai.api_key = api_key

# Neo4j connection
graph = Graph("neo4j account uri", auth=("neo4j user", "your neo4j password"))

# Function to validate a single property
def is_valid_property(value):
    invalid_values = {"null", "not available", "na", "n/a", "none", "", None}
    return value and value.strip().lower() not in invalid_values and len(value.strip()) > 1

# Function to validate all properties in a dictionary
def is_valid_properties(properties):
    return bool(properties) and all(
        is_valid_property(v)
        for v in properties.values()
    )

# Function to create or retrieve a node
def get_or_create_node(label, properties):
    if not is_valid_properties(properties):
        return None
    node = Node(label, **properties)
    existing_node = graph.nodes.match(label, **properties).first()
    if existing_node:
        return existing_node
    else:
        graph.create(node)
        return node

# Function to create a relationship
def create_relationship(node1, node2, relationship_type):
    if node1 and node2:
        relationship = Relationship(node1, relationship_type, node2)
        graph.create(relationship)

# Function to generate relationships using OpenAI
def generate_relationship(node1_label, node1_props, node2_label, node2_props):
    system_msg = "You are an assistant that helps in creating knowledge graph relationships. Your task is to suggest a relationship type between two entities based on their properties. Only use the relationship types provided in the list below."
    prompt = f"""
    Given the following two entities:
    1. {node1_label} with properties {node1_props}
    2. {node2_label} with properties {node2_props}

    Choose a relationship type from the following list that best describes the relationship between these entities:
    - "SHARES_SKILL_WITH"
    - "SHARES_CLIENT_WITH"
    - "SHARES_PROJECT_WITH"
    - "SHARES_AUTHOR_WITH"
    - "SHARES_KEYWORD_WITH"
    - "SHARES_WATER_SOURCE_WITH"
    - "SHARES_WATER_QUALITY_PARAMETER_WITH"
    - "SHARES_MEASUREMENT_WITH"
    - "SHARES_STANDARD_WITH"
    - "SHARES_WATER_USAGE_WITH"
    - "SHARES_POLLUTANT_WITH"
    - "SHARES_IMPACT_WITH"
    - "SHARES_MITIGATION_MEASURE_WITH"
    - "SHARES_HYDROLOGICAL_DATA_WITH"
    - "SHARES_REGULATORY_INFO_WITH"
    - "SHARES_TECHNOLOGICAL_INFO_WITH"
    - "SHARES_GEOGRAPHIC_INFO_WITH"
    - "SHARES_MAP_AND_DIAGRAM_WITH"
    - "SHARES_STATISTICAL_AND_ANALYTICAL_DATA_WITH"
    - "SHARES_REGULATORY_INSTITUTION_WITH"
    - "SHARES_LOCATION_WITH"
    - "SHARES_SURFACE_WATER_WITH"
    - "SHARES_GROUNDWATER_WITH"
    - "SHARES_AQUIFER_WITH"
    - "SHARES_WATERSHED_WITH"
    - "SHARES_RIVER_WITH"
    - "SHARES_LAKE_WITH"
    - "SHARES_WETLAND_WITH"
    - "SHARES_RESERVOIR_WITH"
    """

    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt},
        ],
        max_tokens=30,  # Shorter max tokens since we expect a short response
        temperature=0.0,  # Lower temperature for more deterministic responses
    )

    relationship_type = completion.choices[0].message.content.strip()
    # Ensure the response is a valid relationship type
    if relationship_type not in [
        "SHARES_SKILL_WITH",
        "SHARES_CLIENT_WITH",
        "SHARES_PROJECT_WITH",
        "SHARES_AUTHOR_WITH",
        "SHARES_KEYWORD_WITH",
        "SHARES_WATER_SOURCE_WITH",
        "SHARES_WATER_QUALITY_PARAMETER_WITH",
        "SHARES_MEASUREMENT_WITH",
        "SHARES_STANDARD_WITH",
        "SHARES_WATER_USAGE_WITH",
        "SHARES_POLLUTANT_WITH",
        "SHARES_IMPACT_WITH",
        "SHARES_MITIGATION_MEASURE_WITH",
        "SHARES_HYDROLOGICAL_DATA_WITH",
        "SHARES_REGULATORY_INFO_WITH",
        "SHARES_TECHNOLOGICAL_INFO_WITH",
        "SHARES_GEOGRAPHIC_INFO_WITH",
        "SHARES_MAP_AND_DIAGRAM_WITH",
        "SHARES_STATISTICAL_AND_ANALYTICAL_DATA_WITH",
        "SHARES_REGULATORY_INSTITUTION_WITH",
        "SHARES_LOCATION_WITH",
        "SHARES_SURFACE_WATER_WITH",
        "SHARES_GROUNDWATER_WITH",
        "SHARES_AQUIFER_WITH",
        "SHARES_WATERSHED_WITH",
        "SHARES_RIVER_WITH",
        "SHARES_LAKE_WITH",
        "SHARES_WETLAND_WITH",
        "SHARES_RESERVOIR_WITH"
    ]:
        relationship_type = None  # Or handle it differently, such as logging an error

    return relationship_type

# Path to your JSON files
doc_brief_folder = r'update with path to your JSON files'

# Process JSON files in doc_brief_folder
for filename in os.listdir(doc_brief_folder):
    if filename.endswith(".json"):
        with open(os.path.join(doc_brief_folder, filename)) as f:
            data = json.load(f)
            document_name = data.get("Document Name")
            authors = data.get("Authors", [])
            keywords = data.get("Keywords", [])
            sources_of_water = data.get("Sources of Water", [])
            publication_date = data.get("Publication Date")
            water_quality_params = data.get("Water Quality Parameters", [])
            measurements = data.get("Measurements", [])
            standards_and_guidelines = data.get("Standards and Guidelines", [])
            water_usage = data.get("Water Usage", [])
            pollutants = data.get("Pollutants", [])
            impact_on_ecosystems = data.get("Impact on Ecosystems", [])
            mitigation_measures = data.get("Mitigation Measures", [])
            hydrological_data = data.get("Hydrological Data", [])
            regulatory_and_policy_info = data.get("Regulatory and Policy Information", [])
            technological_info = data.get("Technological and Methodological Information", [])
            geographic_info = data.get("Geographic Information", [])
            maps_and_diagrams = data.get("Maps and Diagrams", [])
            statistical_and_analytical_data = data.get("Statistical and Analytical Data", [])
            regulatory_institutions = data.get("Regulatory Institutions", [])
            locations = data.get("Locations", [])
            skills = data.get("Skills", [])
            clients = data.get("Clients", [])
            projects = data.get("Projects", [])
            surface_water = data.get("Surface Water", [])
            groundwater = data.get("Groundwater", [])
            aquifers = data.get("Aquifers", [])
            watersheds = data.get("Watersheds", [])
            rivers = data.get("Rivers", [])
            lakes = data.get("Lakes", [])
            wetlands = data.get("Wetlands", [])
            reservoirs = data.get("Reservoirs", [])

            doc_node = get_or_create_node("Document", {"name": document_name})

            # Create nodes and relationships for each entity type
            for label, items in [
                ("Author", authors),
                ("Keyword", keywords),
                ("WaterSource", sources_of_water),
                ("WaterQualityParameter", water_quality_params),
                ("Measurement", measurements),
                ("Standard", standards_and_guidelines),
                ("WaterUsage", water_usage),
                ("Pollutant", pollutants),
                ("ImpactOnEcosystem", impact_on_ecosystems),
                ("MitigationMeasure", mitigation_measures),
                ("HydrologicalData", hydrological_data),
                ("RegulatoryAndPolicyInformation", regulatory_and_policy_info),
                ("TechnologicalInformation", technological_info),
                ("GeographicInformation", geographic_info),
                ("MapAndDiagram", maps_and_diagrams),
                ("StatisticalAndAnalyticalData", statistical_and_analytical_data),
                ("RegulatoryInstitution", regulatory_institutions),
                ("Location", locations),
                ("Skill", skills),
                ("Client", clients),
                ("Project", projects),
                ("SurfaceWater", surface_water),
                ("Groundwater", groundwater),
                ("Aquifer", aquifers),
                ("Watershed", watersheds),
                ("River", rivers),
                ("Lake", lakes),
                ("Wetland", wetlands),
                ("Reservoir", reservoirs)
            ]:
                for item in items:
                    node = get_or_create_node(label, {"name": item.strip()})
                    if node:
                        # Generate relationship type using OpenAI
                        relationship_type = generate_relationship("Document", {"name": document_name}, label, {"name": item.strip()})
                        if relationship_type:
                            create_relationship(doc_node, node, relationship_type)

            if is_valid_property(publication_date):
                pub_date_node = get_or_create_node("PublicationDate", {"date": publication_date})
                if pub_date_node:
                    create_relationship(doc_node, pub_date_node, "PUBLISHED_ON")

print("Graph successfully populated with nodes and AI-generated relationships.")
