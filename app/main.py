from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.schemas import UserFinanceInput, PlanRequest, CreativeRequest
from app.vectorstore import SimpleVectorStore
from app import llm
from app import db as appdb
from typing import Dict, List
import os


app = FastAPI(title="Budget Buddy")

# Persistence paths
DATA_DIR = os.environ.get("BUDGETBUDDY_DATA_DIR", "data")
DB_PATH = os.path.join(DATA_DIR, "db.sqlite")
INDEX_DIR = os.path.join(DATA_DIR, "vectorstore")

# Ensure data dir and DB
os.makedirs(DATA_DIR, exist_ok=True)
appdb.init_db(DB_PATH)

# initialize vector store and load persisted index if present
vector_store = SimpleVectorStore()
try:
    vector_store.load(INDEX_DIR)
except Exception:
    # ignore if load fails
    pass


@app.post("/ingest")
def ingest(fin: UserFinanceInput):
    # Create a simple textual summary to store in the vector DB
    doc_lines = [f"User: {fin.user_id}"]
    total_income = sum(i.amount for i in fin.incomes)
    total_exp = sum(e.amount for e in fin.expenses)
    doc_lines.append(f"Total income: {total_income}")
    doc_lines.append(f"Total expenses: {total_exp}")
    if fin.savings_goal:
        doc_lines.append(f"Savings goal: {fin.savings_goal}")
    if fin.debt_payoff_plan:
        doc_lines.append(f"Debt plan: {fin.debt_payoff_plan}")
    doc_lines.append("Incomes:")
    for i in fin.incomes:
        doc_lines.append(f"- {i.source}: {i.amount}")
    doc_lines.append("Expenses:")
    for e in fin.expenses:
        doc_lines.append(f"- {e.name} ({e.category or 'uncategorized'}): {e.amount}")
    if fin.notes:
        doc_lines.append("Notes:")
        doc_lines.append(fin.notes)

    doc_text = "\n".join(doc_lines)
    metadata = {
        "user_id": fin.user_id,
        "text": doc_text,
        "total_income": total_income,
        "total_expenses": total_exp,
        "savings_goal": fin.savings_goal,
    }

    # persist to sqlite
    appdb.save_doc(DB_PATH, metadata)

    # add to vector store and persist index
    vector_store.add_documents([doc_text], [metadata])
    try:
        vector_store.save(INDEX_DIR)
    except Exception:
        pass

    return {"status": "ok", "message": "ingested", "user_id": fin.user_id}


@app.post("/plan")
def plan(req: PlanRequest):
    docs = appdb.get_docs_by_user(DB_PATH, req.user_id)
    if not docs:
        raise HTTPException(status_code=404, detail="User data not found. Please POST /ingest first.")
    # Build context from stored docs
    context = "\n---\n".join(d['text'] for d in docs)
    plan_text = llm.generate_budget_from_context(context, months=req.months)
    return {"user_id": req.user_id, "months": req.months, "plan": plan_text}


@app.post("/creative")
def creative(req: CreativeRequest):
    docs = appdb.get_docs_by_user(DB_PATH, req.user_id)
    if not docs:
        raise HTTPException(status_code=404, detail="User data not found. Please POST /ingest first.")
    context = "\n---\n".join(d['text'] for d in docs)
    creative_text = llm.generate_creative_summary(context, tone=req.tone, fmt=req.format)
    return {"user_id": req.user_id, "creative": creative_text}


@app.get("/users")
def list_users():
    users = appdb.list_users(DB_PATH)
    return {"users": users}


@app.get("/users/{user_id}/docs")
def get_user_docs(user_id: str):
    docs = appdb.get_docs_by_user(DB_PATH, user_id)
    return {"user_id": user_id, "docs": docs}
