import json
import os, getpass
from typing import Any
from langchain import hub
from datetime import datetime
from sqlalchemy import inspect
from pydantic import BaseModel, Field
from NLPAgent.constants import database_schema
from langchain_core.messages import HumanMessage
from typing_extensions import Annotated, TypedDict
from langgraph.graph import START, StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_community.utilities import SQLDatabase
from langchain_core.runnables.config import RunnableConfig

def _set_env(var: str):
    if not os.environ.get(var):
        # os.environ[var] = getpass.getpass(f"{var}: ")
        os.environ[var] = "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"

_set_env("NVIDIA_API_KEY")

model = ChatNVIDIA(model="meta/llama-3.3-70b-instruct")
db = SQLDatabase.from_uri("postgresql://anc2:admin@localhost:5432/finycsdb")
query_prompt_template = hub.pull("langchain-ai/sql-query-system-prompt")

# print("FINYCS DB==>", query_prompt_template)

# state definition
class State(TypedDict):
    user_query: str
    sql_query: str
    sql_query_result: str
    query_rows: list
    attempts: int
    relevance: str
    sql_error: bool
    readable_resp: Any
    chart_type: str
    output_format: str
    formatted_chart_data : Any
    current_user: str
    current_business: int

def get_database_schema(db):
    """
    Returns a detailed database schema representation.
    
    Args:
        db: SQLDatabase instance
    
    Returns:
        str: A string representation of the database schema
    """

    inspector = inspect(db._engine)
    
    schema = ""
    for table_name in inspector.get_table_names():
        schema += f"Table: {table_name}\n"
        
        # Get columns
        for column in inspector.get_columns(table_name):
            col_name = column["name"]
            col_type = str(column["type"])
            
            # Check if it's a primary key
            pk_constraint = inspector.get_pk_constraint(table_name)
            if pk_constraint and col_name in pk_constraint.get('constrained_columns', []):
                col_type += ", Primary Key"
            
            # Check for foreign keys
            fk_constraints = inspector.get_foreign_keys(table_name)
            for fk in fk_constraints:
                if col_name in fk.get('constrained_columns', []):
                    referred_table = fk.get('referred_table')
                    referred_columns = fk.get('referred_columns')
                    if referred_table and referred_columns:
                        col_type += f", Foreign Key to {referred_table}.{referred_columns[0]}"
            
            schema += f"- {col_name}: {col_type}\n"
        
        schema += "\n"
    
    print("Retrieved detailed database schema.")
    return schema

# Node 1: Get Current User
class GetCurrentUser(BaseModel):
    current_user: str = Field(
        description="The name of the current user based on the provided user ID."
    )

def get_current_user(state:State, config: RunnableConfig):
    print("Retrieving the current user based on user ID.")
    user_id = config["configurable"].get("current_user_id", None)
    user_id = 5
    if not user_id:
        state["current_user"] = "User not found"
        print("No user ID provided in the configuration.")
        return state
    # Execute SQL to get user info
    try:
        query = f"SELECT name FROM numbers_app_user WHERE id = {user_id}"
        result = db.run(query)
        
        if result and result.strip():
            state["current_user"] = result.strip()
            state["current_business"] = 198
            print(f"Current user set to: {state['current_user']}")
        else:
            state["current_user"] = "User not found"
            print("User not found in the database.")
    except Exception as e:
        state["current_user"] = "Error retrieving user"
        print(f"Error retrieving user: {str(e)}")
    
    return state

# Node 1: Check Relevance
class RelevanceOutput(BaseModel):
    """Determines if the query is relevant to the database schema."""
    relevance: str = Field(
        description="Indicates whether the question is related to the database schema. 'relevant' or 'not_relevant'."
    )

def check_relevance(state: State):
    """Check if the user query is relevant to the database schema and ensures it is a read-only query."""
    print(f"Checking relevance of the question: {state['user_query']}")
    # detailed_schema = get_database_schema(db)
    detailed_schema = database_schema

    messages = [
        HumanMessage(content=f"""
        You are an assistant that determines whether a given question is related to the following database schema and ensures it is a read-only query.

        **Schema:**
        {detailed_schema}

        **Question:** {state['user_query']}
        
        **Rules:**
        1. If the question requires retrieving data (e.g., SELECT queries for viewing records), respond with **"relevant"**.
        2. If the question suggests modifying the database (e.g., inserting, updating, deleting, or altering data), respond with **"non_relevant"**.
        3. If the intent of the question is unclear but hints at data manipulation, assume it is **"non_relevant"**.

        **Examples:**
        - "What was my revenue last quarter?" → **relevant**
        - "How many sales did I make last month?" → **relevant**
        - "Delete my last invoice." → **non_relevant**
        - "Update my revenue data for Q1." → **non_relevant**
        - "Insert a new transaction for $500." → **non_relevant**

        **Respond with ONLY "relevant" or "non_relevant" and nothing else.**
        """)
    ]

    structured_llm = model.with_structured_output(RelevanceOutput)
    result = structured_llm.invoke(messages)
    state["relevance"] = result.relevance
    print(f"Relevance determined: {state['relevance']}")

    # Initialize attempts counter
    state["attempts"] = 0
    state["sql_error"] = False
    state["query_rows"] = []
    
    return state


# Node 2: Generate SQL Query
class QueryOutput(BaseModel):
    """Generated SQL query."""
    query: str = Field(..., description="Syntactically valid SQL query.")

def generate_sql_query(state: State):
    """Generate SQL query to fetch information."""
    # print(f"Converting question to SQL for user '{state['current_user']}' and business ID '{state['current_business']}': {state['user_query']}")
    # detailed_schema = get_database_schema(db)
    detailed_schema = database_schema
    
    # Modify the prompt to include both user and business context
    messages = [
        HumanMessage(content=f"""
        You are an intelligent SQL query generator and validator. Provided database schema belongs to financial accounting.
        Given an input question, create a syntactically correct {db.dialect} query to run to help find the answer.

        IMPORTANT: The current user is '{state['current_user']}' with user id 5 ignore the brackets and store only 
        the user name to make it suitable to use in further sql queries and the current business ID is 
        {state['current_business']}.
        Always scope your query to this specific user and business where applicable by adding appropriate WHERE clauses 
        that filter for both the current user's data and the current business.
        
        Unless the user specifies in their question a specific number of examples they wish to obtain, always limit your query 
        to at most {10} results. You can order the results by a relevant column to return the most interesting examples in the database.
        
        Never query for all the columns from a specific table, only ask for the few relevant columns given the question.
        
        Pay attention to use only the column names that you can see in the schema description. Be careful to not query for 
        columns that do not exist. Also, pay attention to which column is in which table.
        
        **Foreign Key Validation:**
           - **Check all foreign key constraints** against the schema and ensure correct joins.  
           - If a direct foreign key does not exist, determine the correct table **through inferred relationships**:
           - For financial transactions, **determine account type from parent_account table** (`INCOME`, `EXPENSE`) using:  
             - For financial transactions, **determine account type** (`INCOME`, `EXPENSE`) using:  
               `numbers_app_transaction.business_account → numbers_app_chartofaccount.account → numbers_app_parentaccount.account_type`.  
             - If querying business details, **link through** `numbers_app_business.id`.  
             - Use numbers_app_journalentry.transaction_date for filtering by financial year.
             - If filtering by **business name**, use `'legal_name'` instead of business_id.  
           - Fields ending in `_id` (e.g., `party_id`) **should be referenced as `.id`**.  
           - Foreign key fields not ending with _id you have to add _id for that foreign key field.
           
        **Query Optimization:**  
           - Ensure the query follows best practices for performance and accuracy.  
           - Avoid unnecessary subqueries or redundant joins.  
           - Use indexed columns where possible to optimize filtering.  
           
        **Additional Query Conditions for Financial Data:**
            1. Start from the `numbers_app_parentaccount` table to filter transactions based on `account_type`.
            2. Join `numbers_app_account`, `numbers_app_chartofaccount`, and `numbers_app_transaction` to link transactions to their respective accounts.
            3. Classify transactions as follows:
               - **Income Calculation:**
                 - Transactions where `account_type = 'INCOME'`:
                   - **Positive Value:** `transaction_type = 'CREDIT'`
                   - **Negative Value:** `transaction_type = 'DEBIT'` (subtract from total income)
               - **Expense Calculation:**
                 - Transactions where `account_type = 'EXPENSE'`:
                   - **Positive Value:** `transaction_type = 'DEBIT'`
                   - **Negative Value:** `transaction_type = 'CREDIT'` (subtract from total expenses)
            4. Filter transactions for the previous fiscal year using `date_trunc('year', NOW() - INTERVAL '1 year')`.
            5. Group results by month (`date_trunc('month', transaction_date)`) and order them in descending order.
            6. The query should be optimized for performance and avoid unnecessary joins.
            
        **Fiscal Year Handling (Country-Specific):**
            - The fiscal year **varies by country**. The current and previous fiscal years should be determined dynamically from the `numbers_app_fiscalyear` table.
            - The `numbers_app_fiscalyear` table stores fiscal year data as `month_range` for each `business_id`.
            - **Determine the fiscal year dynamically** based on today's date and retrieve the start and end dates from `numbers_app_fiscalyear` for the given business.
            - **Example for India (April - March Fiscal Year):**
              - If the query is about the **current fiscal year**, filter data from `2024-04-01` to `2025-03-31`.
              - If the query is about the **previous fiscal year**, filter data from `2023-04-01` to `2024-03-31`.
            - Use `numbers_app_journalentry.transaction_date` to filter transactions within the fiscal year.
            - When the query involves a fiscal year, ensure **exactly 12 monthly records** are retrieved.
           
        **Output Type Handling:**
             - If the user's question requires a **chart-based output**, structure the SQL response accordingly.
             - **Output Type: 'bar_chart'**
               - On SQL query execution, **generate the response in JSON format**.
               - Example output structure:
                 ```
                 [
                     {{ "income": income_amount, 
                        "expense": expense_amount, 
                        "start_date": month_name_and_year 
                     }},
                     ...
                 ]
                 ```
               - Ensure the response correctly **aggregates income and expense data** by month.
               - `start_date` should be formatted as `Month Year` (e.g., `"April 2024"`).
        When both user and business filters are applicable, make sure to include both conditions 
        (e.g., "WHERE user_id = X AND business_id = Y").
        
        Database Schema:
        {detailed_schema}
        
        User Question: {state['user_query']}
        """)
    ]
    
    structured_llm = model.with_structured_output(QueryOutput)
    result = structured_llm.invoke(messages)
    print("QUERY RESULT=====>",result)
    state["sql_query"] = result.query
    print(f"Generated SQL query: {state['sql_query']}")
    return state


# Node 3: Execute SQL Query
def execute_sql_query(state: State):
    """Execute the generated SQL query and store results."""
    sql_query = state["sql_query"].strip()
    print(f"Executing SQL query: {sql_query}")
    
    try:
        # Execute the query
        result = db.run(sql_query)
        # Parse the result to determine if it's empty
        if not result or result.strip() == "":
            state["query_rows"] = []
            state["sql_query_result"] = "No results found."
        else:
            state["sql_query_result"] = result
            state["query_rows"] = [{"result": result}]
            
        state["sql_error"] = False
        print("SQL query executed successfully.")
        
    except Exception as e:
        state["sql_query_result"] = f"Error executing query: {str(e)}"
        state["sql_error"] = True
        print(f"Error executing SQL query: {str(e)}")
    
    return state

class OutputFormat(BaseModel):
    """Determines what should be the output type for the user question."""
    output_format: str
    
def determine_output_format(state: State):
    """Determine if the response should be in text or graph format."""
    print(f"Determining output format for: {state['user_query']}")

    messages = [
        HumanMessage(content=f"""
        You are an assistant that determines whether the output format for a given question should be **text** or **graph**.
        Question: {state["user_query"]}
        
        **Rules:**
        1. If the question asks for a **trend, comparison, growth rate, distribution, or any form of analytical insights**, respond with **"graph"**.
        2. If the question asks for a **single value, a count, a straightforward metric, or a direct lookup**, respond with **"text"**.
        3. Assume the user expects an easily interpretable response in the most suitable format.
        
        **Examples:**
        - "What is sales growth for the last 3 months?" → **graph**
        - "Compare revenue of Q1 and Q2 this year." → **graph**
        - "Show me the trend of expenses in the last 6 months." → **graph**
        - "How many invoices were created last month?" → **text**
        - "What was my total revenue last quarter?" → **text**
        - "How many transactions were recorded today?" → **text**

        **Respond with ONLY "graph" or "text" and nothing else.**
        """)
    ]

    structured_llm = model.with_structured_output(OutputFormat)
    result = structured_llm.invoke(messages)
    state["output_format"] = result.output_format
    print(f"Output format determined: {state['output_format']}")

    return state

class ChartType(BaseModel):
    chart_type: str

def determine_chart_type(state: State):
    """Determine the most appropriate chart type based on the query intent."""
    print(f"Determining chart type for: {state['user_query']}")

    messages = [
        HumanMessage(content=f"""
        You are an assistant that determines the best **chart type** for visualizing financial data based on a given question.
        
        Question: {state["user_query"]}

        **Rules:**
        - **Line Chart** → For trends over time (e.g., "Show sales trend for the last 6 months").
        - **Bar Chart** → For comparisons across categories (e.g., "Compare revenue of Q1, Q2, Q3").
        - **Pie Chart** → For distribution of a whole (e.g., "What is the percentage of expenses by category?").
        
        **Examples:**
        - "What is sales growth for the last 3 months?" → **line_chart**
        - "Compare revenue of Q1 and Q2 this year." → **bar_chart**
        - "Show me expense breakdown by category." → **pie_chart**

        **Respond with ONLY "line_chart", "bar_chart", or "pie_chart".**
        """)
    ]

    structured_llm = model.with_structured_output(ChartType)
    result = structured_llm.invoke(messages)
    state["chart_type"] = result.chart_type
    print(f"Chart type determined ===>: {state['chart_type']}")

    return state


# TODO: remove unecessary data. 
# add a period field to show the range of the data. 
# add name field as the data point name.
# store the result to show in a key called barChartData
# returns all data wrapped in a list
def format_chart_data(state: State):
    """Use LLM to format the query result into the required structure."""
    
    print(f"Formatting query result using LLM for output type: {state['output_format']}")
    print(state["query_rows"])
    messages = [
        HumanMessage(content=f"""
        You are an assistant that formats financial query results into the appropriate output format.
        
        **User Query:** {state["user_query"]}
        **Output Format:** {state["output_format"]}
        
        **Instructions:**
        - If the output format is **"text"**, return the result as a simple, human-readable string.
        - If the output format is **"graph"**, structure the response as a JSON list where:
          - Each entry represents a time period (e.g., month, quarter, or year).
          - Fields:
            - `"result"`: The numerical result (formatted as a string with two decimal places).
            - `"tooltip"`: Provide any additional helpful information (or `null` if not needed).
            - `"from_date"`: The start date of the period in `YYYY-MM-DDTHH:MM:SS` format.
            - `"to_date"`: The end date of the period in `YYYY-MM-DDTHH:MM:SS` format.
            - `"period"`: based on the from_date and to_date choose an appropriate name
        
        **Examples:**
        - If asked "What is sales growth for the last 3 months?", the response should be:
          ```json
          [
              {{"result": "3451687.00", "tooltip": null, "from_date": "2024-04-01T00:00:00", "to_date": "2024-04-30T00:00:00","period": "Jan 2024"}},
              {{"result": "2469717.00", "tooltip": null, "from_date": "2024-05-01T00:00:00", "to_date": "2024-05-31T00:00:00","period": "Feb 2024"}},
              {{"result": "2897087.00", "tooltip": null, "from_date": "2024-06-01T00:00:00", "to_date": "2024-06-30T00:00:00","period": "March 2024"}}
          ]
          ```
        - If asked "How many invoices were created last month?", return a simple string:
          `"There were 325 invoices created in February 2025."`
        
        **Query Result:**
        ```json
        {state["query_rows"]}
        ```
        
        **Generate ONLY the formatted output. Do NOT include explanations.**
        """)
    ]

    # structured_llm = model.with_structured_output(dict)  # Ensure output is JSON
    result = model.invoke(messages)

    # Store formatted output in state
    state["readable_resp"] = result
    print("Formatted output successfully stored.")

    return state

# Node 4: Generate Funny Response (for irrelevant questions)
def generate_funny_response(state: State):
    """Generate a playful response for irrelevant questions."""
    print("Generating a funny response for an unrelated question.")
    
    messages = [
        HumanMessage(content="""
        You are a charming and funny assistant who responds in a playful manner.
        
        I can't help with that database query, as it doesn't seem related to our database schema.
        Please provide a friendly, humorous response encouraging the user to ask database-related questions instead.
        Make it brief and charming.
        """)
    ]
    
    response = model.invoke(messages)
    state["readable_resp"] = response.content
    print("Generated funny response.")
    
    return state

# Node 5: Regenerate Query
class RewrittenQuestion(BaseModel):
    """Rewritten version of the original question."""
    question: str = Field(description="The rewritten question to generate a better SQL query.")

def regenerate_query(state: State):
    """Rewrite the question to generate a better SQL query."""
    print("Regenerating the SQL query by rewriting the question.")
    
    messages = [
        HumanMessage(content=f"""
        You are an assistant that reformulates an original question to enable more precise SQL queries.
        
        Original Question: {state['user_query']}
        Error with previous query: {state['sql_query_result']}
        
        Reformulate the question to enable more precise SQL queries, ensuring all necessary details are preserved.
        Focus on fixing the specific error encountered.
        """)
    ]
    
    structured_llm = model.with_structured_output(RewrittenQuestion)
    result = structured_llm.invoke(messages)
    
    state["user_query"] = result.question
    state["attempts"] += 1
    print(f"Rewritten question (attempt {state['attempts']}): {state['user_query']}")
    
    return state

# Node 6: Generate Readable Response
def generate_readable_resp(state: State):
    """Generate a human-readable response based on the SQL query results."""
    print("Generating a human-readable answer.")
    
    messages = [
        HumanMessage(content=f"""
        You are a helpful assistant that converts SQL query results into clear, natural language responses.
        Start the response with a friendly greeting that includes the user's name.
        
        Current user: {state["current_user"]}
        User query: {state["user_query"]}
        SQL query used: {state["sql_query"]}
        Query result: {state["sql_query_result"]}
        
        Please generate a clear, concise response that answers the user's original question based on the SQL query results.
        Start with "Hello {state["current_user"]}," and then provide the requested information in a friendly manner.ignore the brackets and show only the user name.
        dont give sensitive info like business id or user id in the response
        """)
    ]
    
    response = model.invoke(messages)
    state["readable_resp"] = response.content
    print("Generated human-readable answer.")
    
    return state

# Node 7: Max Attempts Reached
def end_max_iterations(state: State):
    """Handle case when maximum attempts are reached."""
    print("Maximum attempts reached. Ending the workflow.")
    
    messages = [
        HumanMessage(content=f"""
        The system has tried multiple times to answer the following question but keeps encountering errors:
        
        Question: {state["user_query"]}
        
        Latest error: {state["sql_query_result"]}
        
        Please generate a polite message explaining that we couldn't process their request after multiple attempts.
        Suggest that they try rephrasing their question to be more specific about the database tables they want to query.
        """)
    ]
    
    response = model.invoke(messages)
    state["readable_resp"] = response.content
    
    return state

# Router functions
def relevance_router(state: State):
    """Route based on query relevance."""
    if state["relevance"].lower() == "relevant":
        return "generate_sql_query"
    else:
        return "generate_funny_response"

def execute_sql_router(state: State):
    """Route based on SQL execution result."""
    if not state.get("sql_error", False):
        return "determine_output_format"
    else:
        return "regenerate_query"

def output_format_router(state: State):
    """Route based on output format type."""
    if state["output_format"].lower() == "graph":
        return "determine_chart_type"
    else:
        return "generate_readable_resp"

def check_attempts_router(state: State):
    """Route based on number of attempts."""
    if state["attempts"] < 3:
        return "generate_sql_query"
    else:
        return "end_max_iterations"

# Defining workflow
workflow = StateGraph(State)

# Add nodes
workflow.add_node("get_current_user", get_current_user)
workflow.add_node("check_relevance", check_relevance)
workflow.add_node("generate_sql_query", generate_sql_query)
workflow.add_node("execute_sql_query", execute_sql_query)
workflow.add_node("determine_output_format", determine_output_format)
workflow.add_node("determine_chart_type", determine_chart_type)
workflow.add_node("format_chart_data", format_chart_data)
workflow.add_node("generate_readable_resp", generate_readable_resp)
workflow.add_node("regenerate_query", regenerate_query)
workflow.add_node("generate_funny_response", generate_funny_response)
workflow.add_node("end_max_iterations", end_max_iterations)

# Add edges
workflow.add_edge(START, "get_current_user")
workflow.add_edge("get_current_user", "check_relevance")

# Conditional routing after relevance check
workflow.add_conditional_edges(
    "check_relevance",
    relevance_router,
    {
        "generate_sql_query": "generate_sql_query",
        "generate_funny_response": "generate_funny_response",
    },
)

workflow.add_edge("generate_sql_query", "execute_sql_query")

# Conditional routing after SQL execution
workflow.add_conditional_edges(
    "execute_sql_query",
    execute_sql_router,
    {
        "determine_output_format": "determine_output_format",
        "regenerate_query": "regenerate_query",
    },
)

# Conditional routing after determining output format
workflow.add_conditional_edges(
    "determine_output_format",
    output_format_router,
    {
        "generate_readable_resp": "generate_readable_resp",
        "determine_chart_type": "determine_chart_type",
    },
)

workflow.add_edge("determine_chart_type", "format_chart_data")

# Conditional routing after query regeneration
workflow.add_conditional_edges(
    "regenerate_query",
    check_attempts_router,
    {
        "generate_sql_query": "generate_sql_query",
        "end_max_iterations": "end_max_iterations",
    },
)

# Final edges to END
workflow.add_edge("generate_readable_resp", END)
workflow.add_edge("generate_funny_response", END)
workflow.add_edge("end_max_iterations", END)
workflow.add_edge("format_chart_data", END)

# Compile the graph
graph = workflow.compile()

# Example usage
def run_query(user_query):
    """Run a query through the agent."""
    initial_state = State(user_query=user_query)
    final_state = graph.invoke(initial_state)
    
    print(f"\nOriginal Query: {user_query}")
    print(f"\nQuery Relevance: {final_state.get('relevance', 'Not checked')}")
    print(f"\nNumber of Attempts: {final_state.get('attempts', 0)}")
    
    if 'sql_query' in final_state:
        print(f"\nGenerated SQL: {final_state['sql_query']}")
        print(f"\nSQL Result: {final_state['sql_query_result']}")
    
    print(f"\nFinal Response: {final_state['readable_resp']}")
    
    return final_state

sample_query = "What are the income and expensses of the current fiscal year by month for my business?"
# sample_query = "What is number of invoices created month by month in previous year for my business?"

run_query(sample_query)


