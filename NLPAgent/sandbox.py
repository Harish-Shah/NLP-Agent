import torch
import os, getpass
from langchain import hub
from sqlalchemy import inspect
from pydantic import BaseModel, Field
from NLPAgent.constants import database_schema
from typing_extensions import Annotated, TypedDict
from langgraph.graph import START, StateGraph, END
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_community.utilities import SQLDatabase
from langchain_core.runnables.config import RunnableConfig
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline


hf_token = "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"

model_id = "defog/sqlcoder-1.3b"
tokenizer = AutoTokenizer.from_pretrained(model_id, use_auth_token=hf_token)

sql_model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float32,
    device_map={"": "cpu"},
    use_auth_token=hf_token  # pass it here too
)


pipe = pipeline(
    "text-generation",
    model=sql_model,
    tokenizer=tokenizer,
    max_new_tokens=512,
    temperature=0.2,
    device=-1
)

db = SQLDatabase.from_uri("postgresql://anc2:admin@localhost:5432/finycsdb")


question = "What is the total transaction amount for in the last 30 days?"

full_prompt = f"""### Postgres SQL tables, with their properties:
{database_schema}

### A query to answer: {question}
SELECT"""


result = pipe(full_prompt)[0]["generated_text"]
generated_sql = "SELECT" + result.split("SELECT", 1)[-1]
print("generated_sql ==>", generated_sql)
