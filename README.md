# NLP-Enhanced SQLite Chat Assistant

## Overview
--------

This project is a natural language processing (NLP)-powered chat assistant that interacts with an SQLite database to answer user queries. The assistant converts natural language queries into SQL statements and retrieves relevant data from a company database containing employee and department information.

## Features
--------

*   Accepts natural language queries.
    
*   Converts queries into SQL statements dynamically.
    
*   Supports fuzzy matching for department names to handle typos.
    
*   Handles date-based filtering for employee records.
    
*   Provides clear, formatted responses.
    

## Supported Queries
-----------------

The assistant supports queries such as:

*   "Who is the manager of the Engineering department?"
    
*   "Show me all employees in the Sales department."
    
*   "List all employees hired after 2021-01-01."
    
*   "What is the total salary expense for the Marketing department?"
    
*   "Which employee has the highest salary?"
    
*   "What is the average salary of all employees?"
    

## Technologies Used
-----------------

*   Python
    
*   SQLite
    
*   spaCy (for NLP)
    
*   FuzzyWuzzy (for fuzzy matching)
    

## How It Works
------------

1.  **User Input:** The user enters a query in natural language.
    
2.  **Entity Extraction:** The assistant extracts relevant entities (departments, dates, numeric values) using spaCy and regex.
    
3.  **Fuzzy Matching:** If a department name is slightly misspelled, fuzzy matching corrects it.
    
4.  **SQL Query Generation:** The extracted information is mapped to an SQL query.
    
5.  **Database Query Execution:** The query is executed against the SQLite database.
    
6.  **Response Generation:** The results are formatted and presented to the user.
    

Steps to Run the Project Locally
--------------------------------

### 1\. Clone the Repository
`   git clone https://github.com/vinu0404/Chat_with_database_without_LLM.git   `

### 2\. Ensure SQLite Database Exists

Make sure the company.db database file is in the project directory. If not, create and  it:
```
import sqlite3

# Create a connection to the SQLite database in Colab
db_path = "company.db"  
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create Departments Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Departments (
    ID INTEGER PRIMARY KEY,
    Name TEXT UNIQUE NOT NULL,
    Manager TEXT NOT NULL
);
""")

# Create Employees Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Employees (
    ID INTEGER PRIMARY KEY,
    Name TEXT NOT NULL,
    Department TEXT NOT NULL,
    Salary INTEGER NOT NULL,
    Hire_Date TEXT NOT NULL,
    FOREIGN KEY (Department) REFERENCES Departments(Name)
);
""")

# Insert sample data
departments_data = [
    (1, "Sales", "Alice"),
    (2, "Engineering", "Bob"),
    (3, "Marketing", "Charlie")
]

employees_data = [
    (1, "Alice", "Sales", 50000, "2021-01-15"),
    (2, "Bob", "Engineering", 70000, "2020-06-10"),
    (3, "Charlie", "Marketing", 60000, "2022-03-20")
]

# Insert data into Departments
cursor.executemany("INSERT OR IGNORE INTO Departments (ID, Name, Manager) VALUES (?, ?, ?)", departments_data)

# Insert data into Employees
cursor.executemany("INSERT OR IGNORE INTO Employees (ID, Name, Department, Salary, Hire_Date) VALUES (?, ?, ?, ?, ?)", employees_data)

# Commit and close
conn.commit()
conn.close()

print("Database created successfully with sample data ")

```



### Known Limitations


    
*   Queries with complex sentence structures might not be understood.
    
*   Limited to predefined query types.
    

## Suggestions for Improvement
    
*   Expand support for more query types.
    
*   Integrate with a web-based UI using Streamlit.
    

