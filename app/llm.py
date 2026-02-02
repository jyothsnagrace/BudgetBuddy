import os
from typing import List
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# try to import openai if available
try:
    import openai
    if OPENAI_API_KEY:
        openai.api_key = OPENAI_API_KEY
except Exception:
    openai = None


def _load_system_prompt(path: str = "prompts/system_prompt.txt") -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "You are a helpful assistant that creates clear budget plans."


SYSTEM_PROMPT = _load_system_prompt()


def _call_openai_chat(messages: List[dict], model: str = OPENAI_MODEL, temperature: float = 0.4):
    if openai is None or OPENAI_API_KEY is None:
        raise RuntimeError("OpenAI library or API key not available")
    # Basic chat call
    resp = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=800,
    )
    return resp["choices"][0]["message"]["content"]


def _call_openai_chat_with_functions(messages: List[dict], functions: List[dict], model: str = OPENAI_MODEL, temperature: float = 0.4):
    if openai is None or OPENAI_API_KEY is None:
        raise RuntimeError("OpenAI library or API key not available")
    resp = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=800,
        functions=functions,
        function_call="auto",
    )
    choice = resp["choices"][0]
    message = choice["message"]
    # If assistant called a function, return function call data
    if message.get("function_call"):
        return {
            "role": message.get("role"),
            "function_call": message.get("function_call"),
            "raw": resp,
        }
    return {"role": message.get("role"), "content": message.get("content"), "raw": resp}


def generate_budget_from_context(context: str, months: int = 6) -> str:
    """Generate a budget plan given a textual context describing the user's finances."""
    # Try to request a structured JSON plan from the model.
    schema = '{"monthly": [{"month": 1, "income": 0.0, "expenses": 0.0, "savings": 0.0}], "top_actions": ["string"], "risks": ["string"]}'
    user_content = (
        "Here is the user's financial context:\n"
        f"{context}\n"
        f"Please generate a {months}-month budget plan as JSON following this schema: {schema}. Return only valid JSON."
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    # Define a function schema for structured budget output
    functions = [
        {
            "name": "return_budget",
            "description": "Return a structured budget plan as JSON matching the schema",
            "parameters": {
                "type": "object",
                "properties": {
                    "monthly": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "month": {"type": "integer"},
                                "income": {"type": "number"},
                                "expenses": {"type": "number"},
                                "savings": {"type": "number"}
                            },
                            "required": ["month", "income", "expenses", "savings"]
                        }
                    },
                    "top_actions": {"type": "array", "items": {"type": "string"}},
                    "risks": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["monthly", "top_actions", "risks"]
            }
        }
    ]

    # Attempt function-calling route first
    try:
        resp = _call_openai_chat_with_functions(messages, functions)
        # If function call present, parse the arguments
        if resp.get("function_call"):
            args_text = resp["function_call"].get("arguments")
            # arguments may be a JSON string
            try:
                import json as _json
                parsed = _json.loads(args_text)
                return _json.dumps(parsed, indent=2)
            except Exception:
                # if parsing fails, return raw arguments
                return args_text
        # otherwise return the content
        if resp.get("content"):
            return resp.get("content")
    except Exception:
        # Fallback: simple heuristic structured plan
        # Try to extract totals from context
        total_income = None
        total_expenses = None
        savings_goal = None
        for line in context.splitlines():
            if line.lower().startswith('total income:'):
                try:
                    total_income = float(line.split(':', 1)[1].strip())
                except Exception:
                    pass
            if line.lower().startswith('total expenses:'):
                try:
                    total_expenses = float(line.split(':', 1)[1].strip())
                except Exception:
                    pass
            if line.lower().startswith('savings goal:'):
                try:
                    savings_goal = float(line.split(':', 1)[1].strip())
                except Exception:
                    pass

        available = None
        if total_income is not None and total_expenses is not None:
            available = max(0.0, total_income - total_expenses)

        monthly = []
        for m in range(1, months + 1):
            inc = total_income or 0.0
            exp = total_expenses or 0.0
            save = 0.0
            if savings_goal and months > 0:
                save = round(savings_goal / months, 2)
            elif available:
                save = round(available * 0.2, 2)
            monthly.append({"month": m, "income": inc, "expenses": exp, "savings": save})

        top_actions = [
            "Track expenses weekly and categorize them.",
            "Automate at least 20% of available cash into savings.",
            "Prioritize paying extra on high-interest debt."
        ]
        risks = []
        if total_expenses is not None and total_income is not None and total_expenses > total_income:
            risks.append("Monthly expenses exceed income — consider immediate expense reductions.")
        if savings_goal and (savings_goal > (available or 0.0) * months * 1.5):
            risks.append("Savings goal may be aggressive relative to current surplus.")

        structured = {"monthly": monthly, "top_actions": top_actions, "risks": risks}
        # Return a human-friendly formatted version
    import json
    return json.dumps(structured, indent=2)


def generate_creative_summary(context: str, tone: str = "friendly", fmt: str = "letter") -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Create a {tone} {fmt} summarizing this plan for the user:\n{context}"}
    ]
    try:
        return _call_openai_chat(messages)
    except Exception:
        return f"(Fallback) Dear user, here's a short summary of your plan:\n{context[:500]}"


def generate_budget_structured(context: str, months: int = 6) -> dict:
    """Return a parsed structured budget (dict). Attempts to call the model for JSON,
    otherwise uses the local heuristic parser above."""
    import json
    txt = generate_budget_from_context(context, months=months)
    try:
        return json.loads(txt)
    except Exception:
        # If parse fails, return a best-effort structure
        try:
            # If txt already looks like JSON-like but has extra text, try to find first brace
            start = txt.find('{')
            if start != -1:
                return json.loads(txt[start:])
        except Exception:
            pass
        # Fallback: build from the heuristic again
        # Re-run fallback branch by forcing exception in _call_openai_chat path is non-trivial; so parse heuristic directly
        # We'll attempt the same totals extraction used earlier
        out = {
            "monthly": [],
            "top_actions": [
                "Track expenses weekly and categorize them.",
                "Automate at least 20% of available cash into savings.",
                "Prioritize paying extra on high-interest debt."
            ],
            "risks": []
        }
        return out
