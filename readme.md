# Speedrun Database Query Application

This application allows users to query a speedrun database using natural language questions. It converts these questions to SQL queries and returns the results in a human-readable format.

## Features

- SQLite database for storing speedrun data
- Natural language to SQL conversion using OpenAI's API
- Two prompting methods:
  - **Zero-shot prompting**: Evaluates the model's capability to directly infer NLQ-SQL relationships without examples
  - **Single-domain few-shot prompting**: Uses in-domain demonstration examples for better performance
- Interactive Streamlit web interface

## Setup Instructions

1. **Install the required packages**:
   ```
   pip install streamlit openai sqlite3
   ```

2. **Create a config.json file** with your OpenAI API key:
   ```json
   {
       "OPENAI_API_KEY": "your-openai-api-key-here"
   }
   ```

3. **Prepare the SQL files**:
   - Make sure `setup.sql` and `seedData.sql` are in the same directory as the Python script

4. **Run the application**:
   ```
   streamlit run speedrun-query-app-sqlite.py
   ```

## How to Use

1. Select whether you want to type your own question or choose from sample questions
2. Select the prompting method:
   - **Zero-shot prompting**: No examples provided to the model
   - **Single-domain few-shot prompting**: Uses domain-specific examples
3. Click "Ask" to process your question
4. View the answer and explore the technical details

## Customizing Few-Shot Examples

You can customize the few-shot examples by modifying the `FEW_SHOT_EXAMPLES` list in the Python code. Each example should include a `question` and its corresponding `sql` query.

## Database Schema

The application uses a simple database schema for tracking speedruns:

- **games**: Information about games (title, platform, genre, release date)
- **categories**: Different speedrun categories for each game (Any%, 100%, etc.)
- **runs**: Individual speedrun attempts with completion times
- **personal_bests**: A view that shows all personal best runs

## Files

- `speedrun-query-app-sqlite.py`: Main application code
- `setup.sql`: SQL script for creating the database schema
- `seedData.sql`: SQL script for seeding the database with initial data
- `config.json`: Configuration file for API keys
- `speedrun_database.db`: SQLite database file (created when running the app)