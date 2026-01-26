from pydantic import BaseModel, Field
from typing import List, Optional

class IncomeItem(BaseModel):
    source: str
    amount: float

class ExpenseItem(BaseModel):
    name: str
    amount: float
    category: Optional[str] = None

class UserFinanceInput(BaseModel):
    user_id: str
    name: Optional[str] = None
    incomes: List[IncomeItem]
    expenses: List[ExpenseItem]
    savings_goal: Optional[float] = None
    debt_payoff_plan: Optional[str] = None
    notes: Optional[str] = None

class PlanRequest(BaseModel):
    user_id: str
    months: int = Field(default=6, ge=1, le=60)

class CreativeRequest(BaseModel):
    user_id: str
    tone: Optional[str] = "friendly"
    format: Optional[str] = "letter"
