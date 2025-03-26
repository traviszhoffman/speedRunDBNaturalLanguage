import os
import json
import time
import sqlite3
import openai
from datetime import datetime
import streamlit as st

# Load configuration from config.json
def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("config.json file not found. Please create one with your API keys.")
        return None
    except json.JSONDecodeError:
        st.error("Invalid JSON in config.json file.")
        return None

# Initialize clients with config
config = load_config()
if config:
    # Configure OpenAI client
    client = openai.OpenAI(api_key=config.get("OPENAI_API_KEY"))
else:
    client = None

# SQLite database path
DB_PATH = "speedrun_database.db"

# Database schema definition for context
DB_SCHEMA = """
-- Create Games Table
CREATE TABLE games (
    game_id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    platform TEXT NOT NULL,
    genre TEXT,
    release_date DATE
);

-- Create Categories Table
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES games(game_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    world_record_time NUMERIC(10, 3),  -- Stored in seconds with millisecond precision
    world_record_holder TEXT
);

-- Create Runs Table
CREATE TABLE runs (
    run_id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES games(game_id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(category_id) ON DELETE CASCADE,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    completion_time NUMERIC(10, 3) NOT NULL,  -- Stored in seconds with millisecond precision
    is_personal_best BOOLEAN DEFAULT FALSE,
    notes TEXT
);

-- Create an index for faster queries on personal bests
CREATE INDEX idx_personal_best ON runs(game_id, category_id, is_personal_best);

-- Optional: Create a view for easy retrieval of personal bests
CREATE VIEW personal_bests AS
SELECT 
    r.run_id,
    g.title AS game_title,
    g.platform,
    c.name AS category_name,
    r.completion_time,
    r.date,
    r.notes,
    c.world_record_time,
    c.world_record_holder,
    (r.completion_time - c.world_record_time) AS time_difference
FROM 
    runs r
JOIN 
    games g ON r.game_id = g.game_id
JOIN 
    categories c ON r.category_id = c.category_id
WHERE 
    r.is_personal_best = TRUE;
"""

# Sample NLQ-SQL pairs for few-shot prompting
FEW_SHOT_EXAMPLES = [
    {
        "question": "What are my personal best times for Super Mario 64?",
        "sql": """
        SELECT g.title, c.name AS category, r.completion_time
        FROM runs r
        JOIN games g ON r.game_id = g.game_id
        JOIN categories c ON r.category_id = c.category_id
        WHERE g.title = 'Super Mario 64' AND r.is_personal_best = 1
        """
    },
    {
        "question": "How close am I to the world record for Hollow Knight Any%?",
        "sql": """
        SELECT g.title, c.name, r.completion_time, c.world_record_time, 
               (r.completion_time - c.world_record_time) AS time_difference
        FROM runs r
        JOIN games g ON r.game_id = g.game_id
        JOIN categories c ON r.category_id = c.category_id
        WHERE g.title = 'Hollow Knight' AND c.name = 'Any%' AND r.is_personal_best = 1
        """
    },
    {
        "question": "Which game do I have the most categories for?",
        "sql": """
        SELECT g.title, COUNT(c.category_id) AS category_count
        FROM games g
        JOIN categories c ON g.game_id = c.game_id
        GROUP BY g.title
        ORDER BY category_count DESC
        LIMIT 1
        """
    }
]

# Sample questions for the user to choose from
SAMPLE_QUESTIONS = [
    "What are my personal best times for Super Mario 64?",
    "Which game has the most speedrun attempts?",
    "How close am I to the world record for Hollow Knight Any%?",
    "What's my best category in Dark Souls?",
    "When was my last Celeste run?",
    "Which game do I have the most categories for?",
    "What's the average completion time for my Metroid Dread runs?",
    "How many runs did I do in 2023?",
    "What's my fastest speedrun ever?",
    "Which games have I completed in under 30 minutes?"
]

def get_db_connection():
    """Create and return a connection to the SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

def setup_database():
    """
    Setup the database schema and seed it with initial data
    """
    try:
        # Check if the database file exists
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)  # Remove existing database for fresh setup
        
        # Create a new database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Read SQL files
        with open('setup-sqlite.sql', 'r') as f:
            setup_sql = f.read()
        
        with open('seeddata-sqlite.sql', 'r') as f:
            seed_sql = f.read()
        
        # Execute setup SQL (schema creation)
        # Split by semicolons and execute each statement
        for statement in setup_sql.split(';'):
            if statement.strip():
                cursor.execute(statement)
        
        # Execute seed SQL (data insertion)
        for statement in seed_sql.split(';'):
            if statement.strip():
                cursor.execute(statement)
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error setting up database: {e}")
        return False

def format_time(seconds):
    """
    Format seconds into a human-readable time format (HH:MM:SS.ms)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds_remainder = seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds_remainder:.3f}s"
    elif minutes > 0:
        return f"{minutes}m {seconds_remainder:.3f}s"
    else:
        return f"{seconds_remainder:.3f}s"

def natural_language_to_sql_zero_shot(question):
    """
    Convert a natural language question to a SQL query using OpenAI without examples (zero-shot)
    """
    system_prompt = f"""
    You are an AI assistant that converts natural language questions to SQL queries.
    {DB_SCHEMA}
    
    Rules:
    1. Generate ONLY the SQL query without any explanations or markdown formatting
    2. Use standard SQLite syntax
    3. Include appropriate JOINs when needed
    4. Make sure column and table names match exactly with the schema
    5. If times need to be formatted for display, leave that to the application
    6. If the question is ambiguous, make a reasonable assumption
    7. If the query cannot be answered with the given schema, return "Cannot answer this query with the available schema"
    8. Use 1 and 0 for boolean values instead of TRUE and FALSE
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0
        )
        sql_query = response.choices[0].message.content.strip()
        return sql_query
    except Exception as e:
        print(f"Error generating SQL: {e}")
        return None

def natural_language_to_sql_few_shot(question):
    """
    Convert a natural language question to a SQL query using OpenAI with few-shot examples
    """
    # Create few-shot examples format
    examples_text = ""
    for example in FEW_SHOT_EXAMPLES:
        examples_text += f"Question: {example['question']}\nSQL: {example['sql']}\n\n"
    
    system_prompt = f"""
    You are an AI assistant that converts natural language questions to SQL queries.
    {DB_SCHEMA}
    
    Here are some examples of questions and their corresponding SQL queries:
    
    {examples_text}
    
    Rules:
    1. Generate ONLY the SQL query without any explanations or markdown formatting
    2. Use standard SQLite syntax
    3. Include appropriate JOINs when needed
    4. Make sure column and table names match exactly with the schema
    5. If times need to be formatted for display, leave that to the application
    6. If the question is ambiguous, make a reasonable assumption 
    7. If the query cannot be answered with the given schema, return "Cannot answer this query with the available schema"
    8. Use 1 and 0 for boolean values instead of TRUE and FALSE
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0
        )
        sql_query = response.choices[0].message.content.strip()
        return sql_query
    except Exception as e:
        print(f"Error generating SQL: {e}")
        return None

def execute_sql(sql_query):
    """
    Execute a SQL query against the SQLite database
    """
    try:
        # For security, we should check if the query is read-only
        if any(keyword in sql_query.lower() for keyword in ['insert', 'update', 'delete', 'drop', 'alter', 'create']):
            return None, "Only SELECT queries are allowed"
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Execute the query
        cursor.execute(sql_query)
        
        # Fetch the results as dictionaries
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results, None
    except Exception as e:
        print(f"Error executing SQL: {e}")
        return None, str(e)

def sql_result_to_natural_language(question, sql_query, result):
    """
    Convert SQL results to natural language answer using OpenAI
    """
    # Convert result to string representation
    result_str = json.dumps(result, default=str)
    
    system_prompt = """
    You are an AI assistant that converts SQL query results to natural language answers.
    Please provide a clear, conversational response that answers the user's question based on the data.
    Format any time values in a human-readable format (e.g., 3600 seconds as "1 hour").
    Keep your response concise but informative.
    """
    
    user_prompt = f"""
    Original question: {question}
    SQL query used: {sql_query}
    Query results: {result_str}
    
    Please provide a natural language answer to the original question based on these results.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating natural language response: {e}")
        return f"Error interpreting results: {e}"

def handle_query(user_question, prompting_type="zero-shot"):
    """
    Process a user question from start to finish
    """
    # Step 1: Convert natural language to SQL based on prompting type
    if prompting_type == "few-shot":
        sql_query = natural_language_to_sql_few_shot(user_question)
    else:  # zero-shot
        sql_query = natural_language_to_sql_zero_shot(user_question)
        
    if not sql_query or sql_query == "Cannot answer this query with the available schema":
        return {
            "answer": "I'm sorry, I couldn't generate a valid SQL query for that question.",
            "sql": None,
            "data": None
        }
    
    # Step 2: Execute SQL
    result, error = execute_sql(sql_query)
    if error:
        return {
            "answer": f"Error executing query: {error}",
            "sql": sql_query,
            "data": None
        }
    
    # Step 3: Convert results to natural language
    if not result or len(result) == 0:
        answer = "I didn't find any data matching your question."
    else:
        answer = sql_result_to_natural_language(user_question, sql_query, result)
    
    return {
        "answer": answer,
        "sql": sql_query,
        "data": result
    }

# Streamlit UI
def main():
    st.set_page_config(
        page_title="Speedrun Database Assistant",
        page_icon="🎮",
        layout="wide"
    )
    
    st.title("🎮 Speedrun Database Assistant")
    st.subheader("Ask questions about your speedruns in plain English")
    
    # Check if config is loaded
    if not config:
        st.error("Please create a config.json file with the following structure:")
        st.code("""{
    "OPENAI_API_KEY": "your-openai-api-key"
}""", language="json")
        st.stop()
    
    # Initialize the database on first run
    if 'db_initialized' not in st.session_state:
        with st.spinner("Setting up the SQLite database..."):
            success = setup_database()
            if success:
                st.session_state.db_initialized = True
                st.success("Database setup complete!")
            else:
                st.error("Database setup failed. Check your database configuration.")
    
    # Query input options
    query_option = st.radio(
        "How would you like to ask your question?",
        ["Type your own question", "Choose from sample questions"]
    )
    
    if query_option == "Choose from sample questions":
        user_question = st.selectbox("Select a question:", SAMPLE_QUESTIONS)
    else:
        user_question = st.text_input("Ask a question about your speedruns:", "")
    
    # Choose prompting method
    prompting_method = st.radio(
        "Prompting method:",
        ["Zero-shot prompting", "Single-domain few-shot prompting"]
    )
    
    # Process the query when the button is clicked
    if st.button("Ask") and user_question:
        with st.spinner("Processing your question..."):
            start_time = time.time()
            
            if prompting_method == "Zero-shot prompting":
                result = handle_query(user_question, prompting_type="zero-shot")
            else:
                result = handle_query(user_question, prompting_type="few-shot")
            
            processing_time = time.time() - start_time
        
        # Display the answer
        st.markdown("### Answer")
        st.markdown(result["answer"])
        
        # Show the technical details in an expandable section
        with st.expander("Technical Details"):
            st.markdown(f"**Processing Time:** {processing_time:.2f} seconds")
            
            st.markdown("**SQL Query:**")
            st.code(result["sql"], language="sql")
            
            if result["data"]:
                st.markdown("**Raw Results:**")
                st.json(result["data"])
                
                # Convert to DataFrame for better visualization
                import pandas as pd
                if len(result["data"]) > 0:
                    df = pd.DataFrame(result["data"])
                    st.markdown("**Results Table:**")
                    st.dataframe(df)

if __name__ == "__main__":
    main()