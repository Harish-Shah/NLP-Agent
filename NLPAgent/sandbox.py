import os, getpass
from pydantic import BaseModel, Field
from NLPAgent.constants import database_schema
from typing_extensions import Annotated, TypedDict
from langgraph.graph import START, StateGraph, END
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import HumanMessage
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from sqlalchemy import inspect
from typing import List

def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = "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"
        

_set_env("NVIDIA_API_KEY")

model = ChatNVIDIA(model="meta/llama-3.3-70b-instruct")

db = SQLDatabase.from_uri("postgresql://anc2:admin@localhost:5432/finycsdb")


class State(TypedDict):
    llm_resp: str
    user_query: str


class SubQuery(BaseModel):
    question: str = Field(description="A simplified sub-question derived from the original complex question.")
    query: str = Field(description="SQL query that answers the sub-question.")

class DecompositionResponse(BaseModel):
    decomposition: List[SubQuery]
    integration_plan: str

def decompose_and_generate_sql_queries(state: State):
    """Break down a complex question into sub-questions and generate individual SQL queries for each."""
    print("Decomposing complex question and generating sub-queries...")

    messages = [
    HumanMessage(content=f"""
        You are a powerful AI that helps generate SQL queries from complex user questions.
        Your task is to analyze complex user questions, break them down into atomic sub-questions, and generate SQL queries that collectively answer the original question. You are an essential component of a LangGraph agent designed for database interaction.
        Available Database Information
        Schema: {database_schema}

        User Question: {state['user_query']}

        Process Steps
        1. Question Analysis

        Carefully read the user's question
        Identify all distinct information needs within the question
        Determine which database tables and relationships are relevant

        2. Question Decomposition

        Break down the complex question into smaller, atomic sub-questions
        Ensure each sub-question can be answered with a single SQL query
        Preserve the logical relationships between sub-questions
        Number each sub-question for clear reference

        3. SQL Query Generation

        For each sub-question, generate a precise SQL query
        Ensure queries follow best practices for performance and readability
        Include clear comments explaining the purpose of each query component
        Validate that the column names and table references match the schema exactly

        4. Result Integration Strategy

        Explain how the results from each query should be combined to answer the original question
        Specify any client-side processing needed to merge or transform query results
        Indicate if any intermediate calculations are required between queries
        
        Output Format
        Return a JSON object with the following structure:
        {{
            "decomposition": [
                {{
                    "id": 1,
                    "sub_question": "First atomic sub-question",
                    "sql_query": "SQL query for first sub-question",
                    "explanation": "Brief explanation of what this query retrieves and why"
                }},
                {{
                    "id": 2,
                    "sub_question": "Second atomic sub-question",
                    "sql_query": "SQL query for second sub-question",
                    "explanation": "Brief explanation of what this query retrieves and why"
                }}
            ],
            "integration_plan": "Step-by-step explanation of how to combine results to answer the original question"
        }}
        
        Example
        User Question
        "Which clients had the highest total revenue last quarter but also have outstanding invoices that are more than 60 days overdue?"
        Output
        {{
            "decomposition": [
                {{
                    "id": 1,
                    "sub_question": "What is the total revenue by client for the last quarter?",
                    "sql_query": "SELECT client_id, c.company_name, SUM(i.amount) AS total_revenue FROM invoices i JOIN clients c ON i.client_id = c.id WHERE i.issue_date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 3 MONTH) AND CURRENT_DATE() AND i.status = 'paid' GROUP BY client_id, c.company_name ORDER BY total_revenue DESC;",
                    "explanation": "Calculates the total paid invoice amounts for each client during the last three months, ordered from highest to lowest revenue"
                }},
                {{
                    "id": 2,
                    "sub_question": "Which clients have invoices that are more than 60 days overdue?",
                    "sql_query": "SELECT DISTINCT i.client_id, c.company_name FROM invoices i JOIN clients c ON i.client_id = c.id WHERE i.status = 'unpaid' AND i.due_date < DATE_SUB(CURRENT_DATE(), INTERVAL 60 DAY);",
                    "explanation": "Identifies clients who have at least one unpaid invoice with a due date more than 60 days in the past"
                }}
            ],
            "integration_plan": "1. Execute the first query to get clients ranked by revenue for the last quarter. 2. Execute the second query to get clients with overdue invoices. 3. Join these results on client_id to find clients that appear in both lists. 4. Return these clients with their revenue figures and details about their overdue invoices, ordering by revenue to highlight high-value clients with payment issues."
        }}
        
        Important Considerations

        Each sub-question should be answerable with a single SQL query
        Ensure proper handling of JOINs when data spans multiple tables
        Consider performance implications for large datasets
        Account for potential NULL values and edge cases
        Use appropriate aggregation functions when needed
        Follow SQL best practices for the specific database system in use

        Remember that your role is to decompose questions and generate SQL queries, not to execute them or produce final answers. Focus on generating correct, efficient queries that another component will execute.
    """)
]

    structured_llm = model.with_structured_output(DecompositionResponse)
    result = structured_llm.invoke(messages)
    print(f"LLM Response ===> {result}")
    state["llm_resp"] = result
    print("Successfully decomposed and generated sub-queries.")
    return state


workflow = StateGraph(State)

# Add nodes
workflow.add_node("decompose_and_generate_sql_queries", decompose_and_generate_sql_queries)

workflow.add_edge(START, "decompose_and_generate_sql_queries")
workflow.add_edge("decompose_and_generate_sql_queries", END)

graph = workflow.compile()


def run_query(user_query):
    """Run a query through the agent."""
    initial_state = State(user_query=user_query)
    final_state = graph.invoke(initial_state)
    
    print(f"\nOriginal Query: {final_state}")
    
    # if 'llm_resp' in final_state:
    #     print(f"\nGenerated SQL: {final_state['llm_resp']}")
    
    # return final_state

# sample_query = "what is fiscal year in the context of the provided schema.what will be the current fiscal year for India"
# sample_query = "which tables have foreign key relations with the table numbers_app_invoiceitems?"
# sample_query = "What is sales and how relationships are maintained in the schema for sales calculation? write a query for getting total sales."
# sample_query = "what does CREDIT and DEBIT mean in a invoice?write a query to fetch invoice created in last 3 months for business with id 198."
sample_query = "What is income in the sense of this schema and how relationships are maintained in the schema for income calculation? write a SQL query for getting total in the previous month for business with 198."
# sample_query = "What is expense in the sense of this schema and how relationships are maintained in the schema for expense calculation? write a SQL query for getting total in the previous month for business with 198."
# sample_query = "What is cashflow in the sense of this schema and how relationships are maintained in the schema for cashflow calculation? write a SQL query for getting total in the previous month for business with 198."



run_query(sample_query)
