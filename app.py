import streamlit as st
import sqlite3
import spacy
import re
from fuzzywuzzy import process
from io import BytesIO

# Load spaCy English NLP model
nlp = spacy.load("en_core_web_sm")

def get_valid_departments(cursor):
    """Fetch valid department names from the database."""
    cursor.execute("SELECT Name FROM Departments;")
    return [row[0] for row in cursor.fetchall()]

def get_closest_department(dept_name, valid_departments):
    """Find the closest matching department name using fuzzy matching."""
    if not dept_name:
        return None
    match, score = process.extractOne(dept_name, valid_departments)
    return match if score > 70 else None

def extract_entities(user_input, valid_departments):
    """Extract key entities (departments, dates) from the query."""
    doc = nlp(user_input)
    entities = {"department": None, "date": None}
    
    for token in doc:
        matched_dept = get_closest_department(token.text, valid_departments)
        if matched_dept:
            entities["department"] = matched_dept
    
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", user_input)
    if date_match:
        entities["date"] = date_match.group(1)
    
    return entities

def process_query(user_input, cursor, valid_departments):
    """Convert natural language query into SQL and fetch results."""
    entities = extract_entities(user_input, valid_departments)
    department, date = entities["department"], entities["date"]
    user_input = user_input.lower()
    
    if "manager" in user_input:
        sql_query = f"SELECT Manager FROM Departments WHERE Name='{department}';" if department else "Please specify a valid department."
    elif "employees" in user_input and "department" in user_input:
        sql_query = f"SELECT * FROM Employees WHERE Department='{department}';" if department else "Please specify a valid department."
    elif "hired after" in user_input:
        sql_query = f"SELECT * FROM Employees WHERE Hire_Date > '{date}';" if date else "Please provide a valid date (YYYY-MM-DD)."
    elif "total salary" in user_input:
        sql_query = f"SELECT SUM(Salary) FROM Employees WHERE Department='{department}';" if department else "Please specify a valid department."
    elif "highest salary" in user_input:
        sql_query = "SELECT Name, Salary FROM Employees ORDER BY Salary DESC LIMIT 1;"
    elif "lowest salary" in user_input:
        sql_query = "SELECT Name, Salary FROM Employees ORDER BY Salary ASC LIMIT 1;"
    elif "average salary" in user_input:
        sql_query = "SELECT AVG(Salary) FROM Employees;"
    else:
        return "I'm sorry, I don't understand your query."
    
    cursor.execute(sql_query)
    result = cursor.fetchall()
    return format_result(result) if result else "No results found."

def format_result(result):
    return "\n".join([str(row) for row in result])

# Streamlit UI
st.title("SQLite NLP Chat Assistant")
uploaded_file = st.file_uploader("Upload your SQLite Database", type=["db"]) 

if uploaded_file:
    db_path = "temp.db"
    with open(db_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    valid_departments = get_valid_departments(cursor)
    
    user_query = st.text_input("Enter your query:")
    if st.button("Ask") and user_query:
        response = process_query(user_query, cursor, valid_departments)
        st.text_area("Response:", response, height=200)
    
    conn.close()
