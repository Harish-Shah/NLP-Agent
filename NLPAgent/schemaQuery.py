import os, getpass
from pydantic import BaseModel, Field
from NLPAgent.constants import database_schema
from typing_extensions import Annotated, TypedDict
from langgraph.graph import START, StateGraph, END
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import HumanMessage
from ai21.models.chat import ChatMessage
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from sqlalchemy import inspect


def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = "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"
        

_set_env("NVIDIA_API_KEY")

model = ChatNVIDIA(model="meta/llama-3.3-70b-instruct")

db = SQLDatabase.from_uri("postgresql://anc2:admin@localhost:5432/finycsdb")


class State(TypedDict):
    llm_resp: str
    user_query: str


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

def query_over_schema(state: State):
    # detailed_schema = get_database_schema(db)
    messages = [
        HumanMessage(content=f""" 
        You are a highly skilled Database Schema Analyst with expertise in relational database design and financial accounting systems.

        Your task is to analyze the following database schema and answer the user's question specifically related to the schema, such as:
        - Identifying tables or columns related to a specific concept
        - Describing foreign key relationships
        - Explaining dependencies between tables
        - Suggesting which tables might be useful for a given topic

        ### Schema Context:
        This schema is designed for a **financial accounting system**. It contains JSON metadata with tables, their columns, foreign key relations, and human-readable descriptions.

        Always refer to descriptions and foreign key mappings when answering.

        ---

        ### Database Schema:
        ```json
        {database_schema}
        User Question: {state['user_query']}
        
        Answers all question in the context of this Schema only
                     """)
    ]
    
    result = model.invoke(messages)
    print("RESULT ===>",result.content)
    state["llm_resp"] = result.content


workflow = StateGraph(State)

# Add nodes
workflow.add_node("query_over_schema", query_over_schema)

workflow.add_edge(START, "query_over_schema")
workflow.add_edge("query_over_schema", END)

graph = workflow.compile()


def run_query(user_query):
    """Run a query through the agent."""
    initial_state = State(user_query=user_query)
    final_state = graph.invoke(initial_state)
    
    # print(f"\nOriginal Query: {final_state}")
    
    if 'llm_resp' in final_state:
        print(f"\nGenerated SQL: {final_state['llm_resp']}")
    
    return final_state

# sample_query = "what is fiscal year in the context of the provided schema.what will be the current fiscal year for India"
# sample_query = "which tables have foreign key relations with the table numbers_app_invoiceitems?"
# sample_query = "What is sales and how relationships are maintained in the schema for sales calculation? write a query for getting total sales."
# sample_query = "what does CREDIT and DEBIT mean in a invoice?write a query to fetch invoice created in last 3 months for business with id 198."
sample_query = "What is income in the sense of this schema and how relationships are maintained in the schema for income calculation? write a SQL query for getting total in the previous month for business with 198."
# sample_query = "What is expense in the sense of this schema and how relationships are maintained in the schema for expense calculation? write a SQL query for getting total in the previous month for business with 198."
# sample_query = "What is cashflow in the sense of this schema and how relationships are maintained in the schema for cashflow calculation? write a SQL query for getting total in the previous month for business with 198."



run_query(sample_query)
