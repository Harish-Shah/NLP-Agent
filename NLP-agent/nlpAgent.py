import os, getpass
from langchain import hub
from sqlalchemy import inspect
from pydantic import BaseModel, Field
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
# db = SQLDatabase.from_uri("postgresql://anc:admin@localhost:5432/gid_db")
# db = SQLDatabase.from_uri("postgresql://numbers_admin:admin@192.168.1.13:5431/postgres")
db = SQLDatabase.from_uri("postgresql://anc2:admin@localhost:5432/finycsdb")
query_prompt_template = hub.pull("langchain-ai/sql-query-system-prompt")

# print("FINYCS DB==>", db.get_table_info())

# state definition
class State(TypedDict):
    user_query: str
    sql_query: str
    sql_query_result: str
    query_rows: list
    attempts: int
    relevance: str
    sql_error: bool
    readable_resp: str

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
    user_id = 28
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
    """Check if the user query is relevant to the database schema."""
    print(f"Checking relevance of the question: {state['user_query']}")
    detailed_schema = get_database_schema(db)

    messages = [
        HumanMessage(content=f"""
        You are an assistant that determines whether a given question is related to the following database schema.

        Schema:
        {detailed_schema}

        Question: {state['user_query']}
        
        Respond with only "relevant" or "not_relevant".
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
    print(f"Converting question to SQL: {state['user_query']}")
    detailed_schema = get_database_schema(db)

    prompt = query_prompt_template.invoke(
        {
            "dialect": db.dialect,
            "top_k": 10,
            "table_info": detailed_schema,
            "input": state['user_query'],
        }
    )
    structured_llm = model.with_structured_output(QueryOutput)
    result = structured_llm.invoke(prompt)
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
            # For simplicity, we're storing the string result
            # In a production system, you might want to parse this into rows
            state["sql_query_result"] = result
            state["query_rows"] = [{"result": result}]
            
        state["sql_error"] = False
        print("SQL query executed successfully.")
        
    except Exception as e:
        state["sql_query_result"] = f"Error executing query: {str(e)}"
        state["sql_error"] = True
        print(f"Error executing SQL query: {str(e)}")
    
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
        User query: {state["user_query"]}
        
        SQL query used: {state["sql_query"]}
        
        Query result: {state["sql_query_result"]}
        
        Please generate a clear, concise response that answers the user's original question based on the SQL query results.
        Make it friendly and informative.
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
        return "generate_readable_resp"
    else:
        return "regenerate_query"

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
        "generate_readable_resp": "generate_readable_resp",
        "regenerate_query": "regenerate_query",
    },
)

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

# sample_query = "which employee has created most number of tasks?"
# sample_query = "which task has taken most time to be completed?"
# sample_query = "how many tasks are done by the employees?"
# sample_query = "which user has created most number of tasks?."
# sample_query = "what was the total sales of the user named Ajay pal last month ?."
# sample_query = "what was the total number of invoices of the user named Ajay pal last month ?."
# sample_query = "what is the name of the user who has user id 28 ?."
sample_query = "print the row storing the data of the user named Ajay Pal ?."


run_query(sample_query)


