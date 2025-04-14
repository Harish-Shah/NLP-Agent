from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from NLPAgent.formattedCode import run_query
from typing import List, Any, Optional
import traceback

app = FastAPI()

# Enable CORS (same as Flask's `CORS(app)`)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and tokenizer
model_id = "defog/sqlcoder-7b-2"

print("Loading model...")
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto"
)

pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=512,
    temperature=0.2
)

print("Model loaded and ready!")

# Request model
class QueryRequest(BaseModel):
    query: str

# Response model (optional for stricter typing)
class QueryResponse(BaseModel):
    output_format: Optional[str]
    chart_type: Optional[str]
    readable_resp: Optional[str]
    formatted_chart_data: List[Any]
    
# Input format
class PromptRequest(BaseModel):
    prompt: str

# API route
@app.post("/api/financial-query", response_model=QueryResponse)
async def financial_query(payload: QueryRequest):
    print(traceback.format_exc())  # Full error trace in your server logs
    try:
        result = run_query(payload.query)
        return {
            "output_format": result.get("output_format"),
            "chart_type": result.get("chart_type"),
            "readable_resp": result.get("readable_resp"),
            "formatted_chart_data": result.get("query_rows", [])
        }
    except Exception as e:
        return {
            "output_format": None,
            "chart_type": None,
            "readable_resp": f"Error: {str(e)}",
            "formatted_chart_data": []
        }

