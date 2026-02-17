"""
BudgetBuddy Backend - Main FastAPI Application
Graduate-level LLM Course Project
"""

from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import os
from dotenv import load_dotenv

# Import custom modules
from llm_pipeline import LLMPipeline
from function_calling import FunctionCallingSystem
from receipt_parser import ReceiptParser
from cost_of_living import CostOfLivingAPI
from database import DatabaseClient
from auth import AuthManager

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="BudgetBuddy API",
    description="LLM-powered expense tracking backend",
    version="1.0.0"
)

# CORS Configuration (allows frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
llm_pipeline = LLMPipeline()
function_system = FunctionCallingSystem()
receipt_parser = ReceiptParser()
col_api = CostOfLivingAPI()
db = DatabaseClient()
auth_manager = AuthManager()

# ============================================
# PYDANTIC MODELS
# ============================================

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)

class LoginResponse(BaseModel):
    user_id: str
    username: str
    token: str
    display_name: Optional[str] = None

class ExpenseCreate(BaseModel):
    amount: float = Field(..., gt=0)
    category: str
    description: Optional[str] = ""
    date: str  # ISO format date

    @validator('category')
    def validate_category(cls, v):
        valid_categories = [
            'Food', 'Transportation', 'Entertainment', 
            'Shopping', 'Bills', 'Healthcare', 'Education', 'Other'
        ]
        if v not in valid_categories:
            raise ValueError(f'Category must be one of {valid_categories}')
        return v

class ExpenseResponse(BaseModel):
    id: str
    user_id: str
    amount: float
    category: str
    description: str
    date: str
    created_at: str

class NaturalLanguageInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)

class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    city: Optional[str] = None
    context: Optional[Dict[str, Any]] = {}

class BudgetCreate(BaseModel):
    monthly_limit: float = Field(..., gt=0)
    category: Optional[str] = None
    month: Optional[str] = None  # YYYY-MM format

# ============================================
# HEALTH CHECK
# ============================================

@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "healthy",
        "service": "BudgetBuddy API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "components": {
            "database": await db.health_check(),
            "llm": llm_pipeline.health_check(),
            "col_api": col_api.health_check()
        }
    }

# ============================================
# AUTHENTICATION
# ============================================

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Username-only login (no password)
    Creates user if doesn't exist
    """
    try:
        user = await auth_manager.login_or_create(request.username)
        return LoginResponse(**user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/auth/verify")
async def verify_token(token: str):
    """Verify JWT token validity"""
    try:
        user = await auth_manager.verify_token(token)
        return {"valid": True, "user": user}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

# ============================================
# EXPENSE MANAGEMENT
# ============================================

@app.post("/api/expenses", response_model=ExpenseResponse)
async def create_expense(
    expense: ExpenseCreate,
    user_id: str = Depends(auth_manager.get_current_user)
):
    """Manually add an expense"""
    try:
        result = await db.create_expense(user_id, expense.dict())
        return ExpenseResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/expenses")
async def get_expenses(
    user_id: str = Depends(auth_manager.get_current_user),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 100
):
    """Get user's expenses with optional filters"""
    try:
        expenses = await db.get_expenses(
            user_id, 
            start_date=start_date,
            end_date=end_date,
            category=category,
            limit=limit
        )
        return {"expenses": expenses, "count": len(expenses)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/expenses/{expense_id}")
async def delete_expense(
    expense_id: str,
    user_id: str = Depends(auth_manager.get_current_user)
):
    """Delete an expense"""
    try:
        await db.delete_expense(user_id, expense_id)
        return {"success": True, "message": "Expense deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# NATURAL LANGUAGE PROCESSING
# ============================================

@app.post("/api/parse-expense")
async def parse_expense_natural_language(
    input_data: NaturalLanguageInput,
    user_id: str = Depends(auth_manager.get_current_user)
):
    """
    Parse natural language to expense data
    Uses two-LLM pipeline
    """
    try:
        # LLM Pipeline: Extract → Normalize → Validate
        parsed_data = await llm_pipeline.parse_expense(input_data.text)
        
        return {
            "success": True,
            "parsed_data": parsed_data,
            "message": "Expense parsed successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=422, 
            detail=f"Failed to parse expense: {str(e)}"
        )

# ============================================
# RECEIPT PARSING (VISION)
# ============================================

@app.post("/api/parse-receipt")
async def parse_receipt(
    file: UploadFile = File(...),
    user_id: str = Depends(auth_manager.get_current_user)
):
    """
    Parse receipt image using Gemini Vision
    Extracts structured expense data
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(400, "File must be an image")
        
        # Read image
        image_data = await file.read()
        
        # Parse receipt using Vision LLM
        parsed_data = await receipt_parser.parse_receipt(image_data)
        
        return {
            "success": True,
            "parsed_data": parsed_data,
            "message": "Receipt parsed successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Failed to parse receipt: {str(e)}"
        )

# ============================================
# FUNCTION CALLING
# ============================================

@app.post("/api/function-call")
async def handle_function_call(
    message: str,
    user_id: str = Depends(auth_manager.get_current_user)
):
    """
    Process function calling from LLM
    Supports: add_expense, set_budget, query_expenses
    """
    try:
        result = await function_system.execute(message, user_id)
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Function call failed: {str(e)}"
        )

# ============================================
# BUDGET MANAGEMENT
# ============================================

@app.post("/api/budgets")
async def create_budget(
    budget: BudgetCreate,
    user_id: str = Depends(auth_manager.get_current_user)
):
    """Set a budget for a category"""
    try:
        result = await db.create_budget(user_id, budget.dict())
        return {"success": True, "budget": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/budgets")
async def get_budgets(
    user_id: str = Depends(auth_manager.get_current_user),
    month: Optional[str] = None
):
    """Get user's budgets"""
    try:
        budgets = await db.get_budgets(user_id, month=month)
        return {"budgets": budgets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/budget-comparison")
async def get_budget_comparison(
    user_id: str = Depends(auth_manager.get_current_user),
    month: Optional[str] = None
):
    """Get budget vs actual spending comparison"""
    try:
        comparison = await db.get_budget_comparison(user_id, month=month)
        return {"comparison": comparison}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# CALENDAR
# ============================================

@app.get("/api/calendar")
async def get_calendar_entries(
    user_id: str = Depends(auth_manager.get_current_user),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get calendar entries with expenses"""
    try:
        entries = await db.get_calendar_entries(
            user_id,
            start_date=start_date,
            end_date=end_date
        )
        return {"entries": entries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# CHATBOT
# ============================================

@app.post("/api/chat")
async def chat_with_buddy(
    chat_data: ChatMessage,
    user_id: str = Depends(auth_manager.get_current_user)
):
    """
    Smart Money Avatar Chatbot
    City-aware, context-aware responses
    """
    try:
        # Get user context
        user_context = await db.get_user_context(user_id)
        
        # Get cost of living data if city provided
        col_data = None
        if chat_data.city:
            col_data = await col_api.get_city_data(chat_data.city)
        
        # Generate response using LLM
        response = await llm_pipeline.chat_response(
            message=chat_data.message,
            user_context=user_context,
            col_data=col_data,
            chat_context=chat_data.context
        )
        
        # Save chat history
        await db.save_chat_message(user_id, chat_data.message, "user")
        await db.save_chat_message(user_id, response, "assistant")
        
        return {
            "response": response,
            "context": {
                "city": chat_data.city,
                "col_data": col_data
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# COST OF LIVING
# ============================================

@app.get("/api/cost-of-living/{city}")
async def get_cost_of_living(city: str):
    """Get cost of living data for a city"""
    try:
        data = await col_api.get_city_data(city)
        return {
            "city": city,
            "data": data,
            "cached": data.get("cached", False)
        }
    except Exception as e:
        # Graceful degradation
        return {
            "city": city,
            "data": None,
            "error": "Data temporarily unavailable",
            "message": str(e)
        }

@app.get("/api/cities")
async def get_cities():
    """Get list of supported cities"""
    return {
        "cities": col_api.get_supported_cities()
    }

# ============================================
# INSIGHTS & ANALYTICS
# ============================================

@app.get("/api/insights")
async def get_insights(
    user_id: str = Depends(auth_manager.get_current_user)
):
    """
    Get AI-generated insights about spending patterns
    """
    try:
        # Get user data
        user_context = await db.get_user_context(user_id)
        
        # Generate insights using LLM
        insights = await llm_pipeline.generate_insights(user_context)
        
        return {
            "insights": insights,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# ERROR HANDLERS
# ============================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

# ============================================
# STARTUP & SHUTDOWN
# ============================================

@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup"""
    print(">> BudgetBuddy API starting...")
    await db.connect()
    print(">> Database connected")
    print(">> LLM pipeline initialized")
    print(f">> Server ready on port {os.getenv('PORT', 8000)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    print(">> BudgetBuddy API shutting down...")
    await db.disconnect()
    print(">> Cleanup complete")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
