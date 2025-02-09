import sqlite3
import spacy
import re
import streamlit as st
from fuzzywuzzy import process
import pandas as pd

# Load spaCy English NLP model
nlp = spacy.load("en_core_web_sm")

# Streamlit UI
st.set_page_config(page_title="NLP SQLite Chat Assistant", layout="wide")

st.title("📊 NLP-Driven SQL Chat Assistant")
st.markdown("Ask queries about employees, departments, salaries, and more!")

# Sidebar for file upload
st.sidebar.header("📂 Upload SQLite Database")
db_file = st.sidebar.file_uploader("Upload your SQLite database (.db)", type=["db"])

if db_file:
    # Save the uploaded file to a local path
    db_path = "uploaded_db.db"
    with open(db_path, "wb") as f:
        f.write(db_file.getbuffer())

    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch valid department names
    cursor.execute("SELECT Name FROM Departments;")
    valid_departments = [row[0] for row in cursor.fetchall()]
    
    def get_closest_department(dept_name):
        """Find the closest matching department name from the database using fuzzy matching."""
        if not dept_name or not valid_departments:
            return None
        match, score = process.extractOne(dept_name, valid_departments)
        return match if score > 70 else None  # Accept only high-confidence matches

    def extract_entities(user_input):
        """Extract key entities (departments, dates, numbers) from the query."""
        doc = nlp(user_input)
        entities = {"department": None, "date": None}

        for token in doc:
            matched_dept = get_closest_department(token.text)
            if matched_dept:
                entities["department"] = matched_dept

        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", user_input)
        if date_match:
            entities["date"] = date_match.group(1)

        return entities

    def process_query(user_input):
        """Process the query and generate SQL."""
        entities = extract_entities(user_input)
        department = entities["department"]
        date = entities["date"]

        user_input = user_input.lower()

        if "manager" in user_input:
            if department:
                sql_query = f"SELECT Manager FROM Departments WHERE Name='{department}';"
            else:
                return "⚠️ Please specify a valid department."

        elif "employees" in user_input and "department" in user_input:
            if department:
                sql_query = f"SELECT * FROM Employees WHERE Department='{department}';"
            else:
                return "⚠️ Please specify a valid department."

        elif "hired after" in user_input:
            if date:
                sql_query = f"SELECT * FROM Employees WHERE Hire_Date > '{date}';"
            else:
                return "⚠️ Please provide a valid date (YYYY-MM-DD)."

        elif "total salary" in user_input:
            if department:
                sql_query = f"SELECT SUM(Salary) FROM Employees WHERE Department='{department}';"
            else:
                return "⚠️ Please specify a valid department."

        elif "highest salary" in user_input:
            sql_query = "SELECT Name, Salary FROM Employees ORDER BY Salary DESC LIMIT 1;"

        elif "lowest salary" in user_input:
            sql_query = "SELECT Name, Salary FROM Employees ORDER BY Salary ASC LIMIT 1;"

        elif "average salary" in user_input:
            sql_query = "SELECT AVG(Salary) FROM Employees;"

        else:
            return "⚠️ I don't understand your query. Try asking about employees, managers, or salaries."

        cursor.execute(sql_query)
        result = cursor.fetchall()

        if not result:
            return "🔍 No results found."

        return format_result(result)

    def format_result(result):
        """Format SQL query results for display."""
        df = pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])
        return df

    # User input for queries
    user_query = st.text_input("💬 Ask a question:", placeholder="Who is the manager of Engineering?")

    if st.button("🔎 Search"):
        if user_query:
            result = process_query(user_query)
            if isinstance(result, pd.DataFrame):
                st.dataframe(result)
            else:
                st.warning(result)

    # Close connection
    conn.close()

else:
    st.info("📌 Please upload a valid SQLite database file to proceed.")
