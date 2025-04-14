import ai21
import os, getpass
from pydantic import BaseModel, Field
from NLPAgent.constants import database_schema
from typing_extensions import Annotated, TypedDict
from langgraph.graph import START, StateGraph, END
from langchain_community.utilities import SQLDatabase
from langchain_core.runnables.config import RunnableConfig
from langchain_core.messages import HumanMessage
from langchain_ai21 import ChatAI21
from ai21 import AI21Client
from ai21.models.chat import ChatMessage


def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = "tv0H2dEm6Ws1RElLsgklBbvqP2GONz2r"
        

_set_env("AI21_API_KEY")

client = AI21Client(api_key=os.getenv('tv0H2dEm6Ws1RElLsgklBbvqP2GONz2r'))
model = ChatAI21(model="jamba-large", temperature=0.2)

db = SQLDatabase.from_uri("postgresql://anc2:admin@localhost:5432/finycsdb")


class State(TypedDict):
    sql_query: str
    user_query: str
    current_user: str
    current_business : int


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
        else:
            state["current_user"] = "User not found"
            print("User not found in the database.")
    except Exception as e:
        state["current_user"] = "Error retrieving user"
        print(f"Error retrieving user: {str(e)}")
    
    return state

def generate_sql_query(state: State):
    
    prompt = f"""
        You are an intelligent SQL query generator and validator. Provided database schema belongs to financial accounting.
        Given an input question, create a syntactically correct {db.dialect} query to run to help find the answer.

        IMPORTANT: The current user is '{state['current_user']}' with user id 5 ignore the brackets and store only 
        the user name to make it suitable to use in further sql queries and the current business ID is 
        {state['current_business']}.
        Always scope your query to this specific user and business where applicable by adding appropriate WHERE clauses 
        that filter for both the current user's data and the current business.
        

        
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
             - Use numbers_app_journalentry.transaction_date for filtering transactions by financial year.
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
            7. Query should consider company_name instead of name form numbers_app_party table
            
        **Fiscal Year Handling (Country-Specific):**
            - The fiscal year **varies by country**. The current and previous fiscal years should be determined dynamically from the `numbers_app_fiscalyear` table.
            - The `numbers_app_fiscalyear` table stores fiscal year data as `month_range` for each `business_id`.
            - **Determine the fiscal year dynamically** based on today’s date and retrieve the start and end dates from `numbers_app_fiscalyear` for the given business.
            - **Example for India (April - March Fiscal Year):**
              - If the query is about the **current fiscal year**, filter data from `2024-04-01` to `2025-03-31`.
              - If the query is about the **previous fiscal year**, filter data from `2023-04-01` to `2024-03-31`.
            - Use `numbers_app_journalentry.transaction_date` to filter transactions within the fiscal year.
            - When the query involves a fiscal year, ensure **all 12 monthly records** are retrieved.
            - While querying for results related to year remove the Limit 10 to fetch all month records.
           
        
        When both user and business filters are applicable, make sure to include both conditions 
        (e.g., "WHERE user_id = X AND business_id = Y").
        
        ### Database Schema:
        {database_schema} ###
        
        User Question: {state['user_query']}
        """
    
    response = client.chat.completions.create(
        model="jamba-large",
        prompt=prompt,
        temperature=0.2,
        max_tokens=500,
        messages=[ChatMessage(role='user', content=prompt)]
    )
    print("Raw response =>", response)

    response_text = response.choices[0].message.content.strip()

    if response_text.startswith("```sql") or response_text.startswith("```SQL"):
        lines = response_text.splitlines()
        sql_lines = [line for line in lines if not line.strip().lower().startswith("```")]
        cleaned_sql = "\n".join(sql_lines).strip()
    else:
        # use raw text as-is
        cleaned_sql = response_text

    # in case nothing was parsed
    if not cleaned_sql:
        cleaned_sql = "-- could not extract SQL query"

    state["sql_query"] = cleaned_sql
    # print(f"Generated SQL query:\n{state['sql_query']}")
    return state


workflow = StateGraph(State)

# Add nodes
workflow.add_node("get_current_user", get_current_user)
workflow.add_node("generate_sql_query", generate_sql_query)

workflow.add_edge(START, "get_current_user")
workflow.add_edge("get_current_user", "generate_sql_query")
workflow.add_edge("generate_sql_query", END)

graph = workflow.compile()


def run_query(user_query):
    """Run a query through the agent."""
    initial_state = State(user_query=user_query)
    final_state = graph.invoke(initial_state)
    
    print(f"\nOriginal Query: {user_query}")
    
    if 'sql_query' in final_state:
        print(f"\nGenerated SQL: {final_state['sql_query']}")
    
    return final_state

sample_query = "What are the income and expenses of the previous year by month for my business?"

# sample_query = "What is number of invoices created month by month in previous year for my business?"

run_query(sample_query)
