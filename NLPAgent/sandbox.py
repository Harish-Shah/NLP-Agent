import os, getpass
from pydantic import BaseModel, Field
from NLPAgent.constants import database_schema
from typing_extensions import Annotated, TypedDict
from langgraph.graph import START, StateGraph, END
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import HumanMessage
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_openai import ChatOpenAI
from sqlalchemy import inspect
from typing import List

def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = "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"
        # os.environ[var] = "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"
        

_set_env("NVIDIA_API_KEY")
# _set_env("OPENAI_API_KEY")

model = ChatNVIDIA(model="meta/llama-3.3-70b-instruct")
# model = ChatOpenAI(openai_api_key=os.environ["OPENAI_API_KEY"], temperature=0.7, model="gpt-4o")

db = SQLDatabase.from_uri("postgresql://anc2:admin@localhost:5432/finycsdb")


class State(TypedDict):
    llm_resp: str
    user_query: str
    query_list: List[str]


class SubQuery(BaseModel):
    question: str = Field(description="A simplified sub-question derived from the original complex question.")
    query: str = Field(description="Syntactically valid SQL query that answers the sub-question.")

class DecompositionResponse(BaseModel):
    decomposition: List[SubQuery]
    integration_plan: str

def decompose_and_generate_sql_queries(state: State):
    """Break down a complex question into sub-questions and generate individual SQL queries for each."""
    print("Decomposing complex question and generating sub-queries...")

    messages = [
    HumanMessage(content=f"""
        # SQL Query Generator for Complex Questions

        ## Your Role and Purpose
        You are a powerful AI that helps generate SQL queries from complex user questions.
        Your task is to analyze complex user questions, break them down into atomic sub-questions, and generate SQL queries that collectively answer the original question. You are an essential component of a LangGraph agent designed for database interaction.

        ## User Context
        IMPORTANT: The current user is 'Ajay Pal' with user id 5 and the current business ID is 198.
        Always scope your query to this specific user and business where applicable by adding appropriate WHERE clauses that filter for both the current user's data and the current business.

        Pay attention to use only the column names that you can see in the schema description. Be careful to not query for 
        columns that do not exist. Also, pay attention to which column is in which table.
        
        ## Available Database Information
        Schema: {database_schema}

        ## User Question
        {state['user_query']}

        ## Process Flow

        ### 1. Question Analysis
        - Carefully read the user's question
        - Identify all distinct information needs within the question
        - Determine which database tables and relationships are relevant

        ### 2. Question Decomposition
        - Break down the complex question into smaller, atomic sub-questions
        - Ensure each sub-question can be answered with a single SQL query
        - Preserve the logical relationships between sub-questions
        - Number each sub-question for clear reference
        - Only split the question if it truly requires multiple queries to answer completely.
        - If the question is already atomic, return it as the only sub-question.

        ### 3. SQL Query Generation
        - For each sub-question, generate a precise SQL query
        - Ensure queries follow best practices for performance and readability
        - Include clear comments explaining the purpose of each query component
        - Validate that the column names and table references match the schema exactly

        ### 4. Result Integration Strategy
        - Explain how the results from each query should be combined to answer the original question
        - Specify any client-side processing needed to merge or transform query results
        - Indicate if any intermediate calculations are required between queries

        ## Database Guidelines

        ### Foreign Key Validation
           - **Check all foreign key constraints** against the schema and ensure correct joins.  
           - If a direct foreign key does not exist, determine the correct table **through inferred relationships**:
           - For financial transactions, **determine account type from parent_account table** (`INCOME`, `EXPENSE`) using:  
             - For financial transactions, **determine account type** (`INCOME`, `EXPENSE`) using:  
               `numbers_app_transaction.business_account → numbers_app_chartofaccount.account → numbers_app_parentaccount.account_type`.  
             - If querying business details, **link through** `numbers_app_business.id`.  
             - Use numbers_app_journalentry.transaction_date for filtering transactions by financial year.
             - If filtering by **business name**, use `'legal_name'` instead of business_id.  
           - Fields ending in `_id` (e.g., `party_id`) **should be referenced as `.id`**.  
           - Foreign key fields not ending with _id you have to add _id for that foreign key field.

        ### Query Optimization
        - Ensure the query follows best practices for performance and accuracy
        - Avoid unnecessary subqueries or redundant joins
        - Use indexed columns where possible to optimize filtering
        - Include both user and business filters when applicable: `WHERE user_id = X AND business_id = Y`
        - For general queries, limit results to 10 unless the user specifies otherwise
        - Do NOT use LIMIT when retrieving full-year data or monthly breakdowns

        ### Additional Query Conditions for Financial Data:
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
        5. Group results by month (`date_trunc('month', transaction_date)`) and order them in ascending order.
        6. The query should be optimized for performance and avoid unnecessary joins.
        7. Query should consider company_name instead of name form numbers_app_party table

        ### Fiscal Year Handling (Country-Specific):
        - The fiscal year **varies by country**. The current and previous fiscal years should be determined dynamically from the `numbers_app_fiscalyear` table.
        - The `numbers_app_fiscalyear` table stores fiscal year data as `month_range` for each `business_id`.
        - **Determine the fiscal year dynamically** based on today’s date and retrieve the start and end dates from `numbers_app_fiscalyear` for the given business.
        - **Example for India (April - March Fiscal Year):**
          - If the query is about the **current fiscal year**, filter data from `2024-04-01` to `2025-03-31`.
          - If the query is about the **previous fiscal year**, filter data from `2023-04-01` to `2024-03-31`.
        - Use `numbers_app_journalentry.transaction_date` to filter transactions within the fiscal year.
        - When the query involves a fiscal year, ensure **all 12 monthly records** are retrieved.
        - While querying for results related to year remove the Limit 10 to fetch all month records.

        ## Output Format
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

        ## Example

        ### User Question
        "What are the income and expenses of the previous fiscal year by month for my business?"

        ### Output
        {{
          "decomposition": [
            {{
              "id": 1,
              "sub_question": "What is the total income by month for my business for the last fiscal year?",
              "sql_query": "select extract(month from je.transaction_date) as month, SUM(case when t.transaction_type = 'CREDIT' then t.amount else -t.amount end) as total_income from numbers_app_journalentry je join numbers_app_transaction t on je.id = t.journal_entry_id join numbers_app_chartofaccount coa on t.business_account_id = coa.id join numbers_app_account acc on coa.account_id = acc.id join numbers_app_parentaccount pa on acc.parent_account_id = pa.id where pa.account_type = 'INCOME' and je.business_id = 198 and je.created_by_id = 5 and extract(year from je.transaction_date) = extract(year from NOW()) - 1 group by extract(month from je.transaction_date) order by month asc;"
            }},
            {{
              "id": 2,
              "sub_question": "What is the total expenses by month for my business for the last fiscal year?",
              "sql_query": "select extract(month from je.transaction_date) as month, SUM(case when t.transaction_type = 'DEBIT' then t.amount else -t.amount end) as total_expenses from numbers_app_journalentry je join numbers_app_transaction t on je.id = t.journal_entry_id join numbers_app_chartofaccount coa on t.business_account_id = coa.id join numbers_app_account acc on coa.account_id = acc.id join numbers_app_parentaccount pa on acc.parent_account_id = pa.id where pa.account_type = 'EXPENSE' and je.business_id = 198 and je.created_by_id = 5 and extract(year from je.transaction_date) = extract(year from NOW()) - 1 group by extract(month from je.transaction_date) order by month asc;"
            }}
          ],
          "integration_plan": "To combine the income and expenses for the previous year, join the results on the 'month' field. You can Union the two queries as follows to get the income and expense for the business"
        }}

        ## Remember
        - Each sub-question should be answerable with a single SQL query
        - Ensure proper handling of JOINs when data spans multiple tables
        - Consider performance implications for large datasets
        - Account for potential NULL values and edge cases
        - Use appropriate aggregation functions when needed
        - Follow SQL best practices for the specific database system in use

        Your role is to decompose questions and generate SQL queries, not to execute them or produce final answers. Focus on generating correct, efficient queries that another component will execute.
        
        Check and make sure that all guidelines have been followed.
    """)
    ]

    structured_llm = model.with_structured_output(DecompositionResponse)
    result = structured_llm.invoke(messages)
    state["query_list"] =  [r.query for r in result.decomposition]
    print(f"Decomposition Result: {result.decomposition}")
    # result = model.invoke("What is AI?")
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
    
    print(f"\nOriginal Query: {final_state['llm_resp'].decomposition}")
    print(f"Query List: {final_state['query_list']}")
    
    for query in final_state["llm_resp"].decomposition:
        print(f"\nSub-Question: {query.question}")
        print(f"SQL Query: {query.query}")
    
    return final_state

# sample_query = "how my sales in distributed across different customers?"
# sample_query = "what is total number of invoices created?"
sample_query = "What is the total revenue by client for the last quarter?"
# sample_query = "What are the income and expenses of the previous fiscal year by month for my business?"
# sample_query = "Which clients had the highest total revenue last quarter but also have outstanding invoices that are more than 60 days overdue?"
# sample_query = "What is the total revenue by client for the last quarter?"
# sample_query = "what are the invoices created in January?"
sample_query = "what are the top customers product wise?"

run_query(sample_query)
