# BudgetBuddy - System Architecture

## 📐 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Vite)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ SpendingForm │  │  BudgetBuddy │  │  Auth Screen │     │
│  │ (3 Methods)  │  │   Chatbot    │  │  (Username)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Python)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              LLM Pipeline Layer                      │  │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────────┐  │  │
│  │  │  LLM #1    │→ │   LLM #2   │→ │  Validator   │  │  │
│  │  │ (Extract)  │  │(Normalize) │  │ (JSON Schema)│  │  │
│  │  └────────────┘  └────────────┘  └──────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Function Calling System                    │  │
│  │  - add_expense()     - set_budget()                  │  │
│  │  - query_expenses()  - get_insights()                │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Vision Processing                        │  │
│  │  - Receipt OCR (Gemini Vision)                       │  │
│  │  - Text Extraction                                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│   Supabase Database      │  │   External APIs          │
│  - users                 │  │  - Cost of Living API    │
│  - expenses              │  │  - RapidAPI (COL Data)   │
│  - budgets               │  │                          │
│  - calendar_entries      │  │                          │
└──────────────────────────┘  └──────────────────────────┘
```

## 🔐 Authentication Flow

1. **Username-Only Login**
   - No password required (lightweight)
   - Username stored in Supabase `users` table
   - Session persisted in localStorage
   - JWT token for API requests

## 📝 SpendingForm - Three Input Methods

### Method 1: Quick Add (Natural Language)
```
User types: "Lunch at Chipotle $15"
    ↓
LLM Pipeline extracts:
    {
      "amount": 15.0,
      "category": "Food",
      "description": "Lunch at Chipotle",
      "date": "2026-02-17"
    }
    ↓
Auto-switch to Manual Entry tab (pre-filled)
```

### Method 2: Receipt Photo
```
User uploads receipt image
    ↓
Gemini Vision API extracts text
    ↓
LLM Pipeline parses structured data
    ↓
Auto-fill Manual Entry form
```

### Method 3: Manual Entry
- Traditional form fields
- Default focused tab on page load
- Focus returns after "Parse & Fill"

## 🧠 Two-LLM Pipeline Design

### LLM #1: Extraction Agent
- **Model**: Gemini 1.5 Flash (free tier)
- **Task**: Extract raw structured data
- **Input**: Natural text or OCR output
- **Output**: JSON with fields

### LLM #2: Normalization Agent
- **Model**: Gemini 1.5 Flash
- **Task**: Clean, validate, categorize
- **Operations**:
  - Normalize categories to predefined list
  - Validate/parse dates
  - Clean amount formatting
  - Enhance descriptions
- **Output**: Clean, validated JSON

### JSON Schema Validation
```json
{
  "type": "object",
  "required": ["amount", "category", "date"],
  "properties": {
    "amount": {"type": "number", "minimum": 0},
    "category": {"enum": ["Food", "Transportation", "Entertainment", "Shopping", "Bills", "Healthcare", "Education", "Other"]},
    "description": {"type": "string", "maxLength": 200},
    "date": {"type": "string", "format": "date"}
  }
}
```

## 🗄️ Supabase Schema

### Table: users
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  username TEXT UNIQUE NOT NULL,
  display_name TEXT,
  selected_pet TEXT DEFAULT 'penguin',
  friendship_level INTEGER DEFAULT 1,
  last_activity TIMESTAMP DEFAULT NOW(),
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Table: expenses
```sql
CREATE TABLE expenses (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  amount DECIMAL(10, 2) NOT NULL,
  category TEXT NOT NULL,
  description TEXT,
  expense_date DATE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  metadata JSONB
);
```

### Table: budgets
```sql
CREATE TABLE budgets (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  monthly_limit DECIMAL(10, 2) NOT NULL,
  category TEXT,
  month DATE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, month, category)
);
```

### Table: calendar_entries
```sql
CREATE TABLE calendar_entries (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  expense_id UUID REFERENCES expenses(id) ON DELETE CASCADE,
  display_date DATE NOT NULL,
  label TEXT NOT NULL,
  category TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## 🌍 Cost-of-Living API Integration

### API: RapidAPI - Cost of Living Index
- **Endpoint**: `/cost-of-living/city`
- **Features**:
  - Search by city name
  - Return cost index, rent index, groceries index
  - Rate limiting: 500 requests/month (free tier)

### City Selector
- Dropdown with top 50 US cities
- Alphabetical ordering
- Type-to-search functionality
- Default: Geolocation-detected city
- Fallback: Manual selection

### Graceful Degradation
```python
try:
    col_data = fetch_cost_of_living(city)
except RateLimitError:
    col_data = cached_response
except APIError:
    col_data = {"message": "Data temporarily unavailable"}
```

## 🤖 Smart Money Avatar Chatbot

### Context-Aware System Prompt
```
You are {PET_NAME} the {PET_TYPE}, a friendly budgeting assistant.

User context:
- Location: {CITY}
- Budget: ${BUDGET}
- Spent: ${TOTAL_SPENT}
- Friendship Level: {LEVEL}

Respond based on:
1. User's spending patterns
2. Cost-of-living in {CITY}
3. Friendship level (casual → close friend)
4. Current mood (happy/worried/stressed)

Keep responses: Brief, cute, actionable
```

### Example Interactions
```
User: "Best budget restaurant in Seattle?"
Avatar: "🐧 Cappy's Pizza on Capitol Hill! $8-12/meal, 
         locals love it! Want directions?"

User: "Should I buy or rent in Austin?"
Avatar: "🦫 With Austin's median home at $550K and rent 
         at $1,800/mo, renting saves ~$800/mo in costs. 
         Need a savings plan?"
```

## 🔄 Function Calling System

### Available Functions
```python
FUNCTIONS = [
    {
        "name": "add_expense",
        "description": "Add a new expense",
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {"type": "number"},
                "category": {"type": "string"},
                "description": {"type": "string"},
                "date": {"type": "string"}
            },
            "required": ["amount", "category", "date"]
        }
    },
    {
        "name": "set_budget",
        "description": "Set monthly budget",
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {"type": "number"},
                "month": {"type": "string"}
            },
            "required": ["amount"]
        }
    }
]
```

### Execution Flow
```
User: "Add $20 coffee expense"
    ↓
LLM generates function call:
{
  "function": "add_expense",
  "arguments": {
    "amount": 20,
    "category": "Food",
    "description": "coffee",
    "date": "2026-02-17"
  }
}
    ↓
Validator checks schema
    ↓
Execute function → Insert to DB
    ↓
Return confirmation
```

## 🎯 UX Requirements Implementation

1. **Default Focus**: Manual Entry tab
2. **Auto-switch**: After "Parse & Fill" → Manual Entry
3. **No scroll jumps**: `scrollIntoView: false`
4. **Chatbot focus**: After Enter/Send → cursor returns to input
5. **Mobile-friendly**: Responsive design

## 📊 Data Flow Example

### Adding Expense via Natural Language
```
1. User types: "Dinner at Olive Garden $45"
2. Frontend POST /api/parse-expense
3. Backend LLM Pipeline:
   - LLM #1 extracts data
   - LLM #2 normalizes
   - Validator checks schema
4. Backend POST to Supabase
5. Frontend updates UI
6. Calendar auto-updates
```

## 🚀 Deployment Strategy

### Backend (FastAPI)
- **Platform**: Railway / Render (free tier)
- **Environment Variables**:
  - `GEMINI_API_KEY`
  - `SUPABASE_URL`
  - `SUPABASE_KEY`
  - `RAPIDAPI_KEY`

### Frontend (React/Vite)
- **Platform**: Vercel / Netlify (free tier)
- **Build**: `npm run build`
- **Deploy**: Git-based deployment

### Database
- **Supabase**: Free tier (500MB, 2GB bandwidth)

## 📦 Tech Stack

### Backend
- **Framework**: FastAPI 0.110+
- **LLM**: Google Gemini 1.5 Flash
- **Database**: Supabase (PostgreSQL)
- **Validation**: Pydantic
- **OCR/Vision**: Gemini Vision API

### Frontend
- **Framework**: React 18 + Vite
- **UI**: Radix UI + Tailwind CSS
- **State**: React Hooks + localStorage
- **Calendar**: date-fns + custom component

### APIs
- **LLM**: Google Gemini (free tier)
- **Cost of Living**: RapidAPI (free tier)
- **Database**: Supabase REST API

## 🔒 Security Considerations

1. **No sensitive auth**: Username-only (acceptable for course project)
2. **API keys**: Environment variables only
3. **Input validation**: Pydantic schemas
4. **SQL injection**: Supabase parameterized queries
5. **Rate limiting**: FastAPI middleware

## ✅ Project Requirements Coverage

✓ LLM Integration (Gemini)
✓ Prompt Design (System prompts, few-shot)
✓ Structured Outputs (JSON Schema)
✓ Function Calling (add_expense, set_budget)
✓ Multimodal Input (Receipt photos)
✓ Vision Extraction (Gemini Vision)
✓ External API (Cost of Living)
✓ Persistent Storage (Supabase)
✓ Authentication (Username-based)
✓ Modular Architecture (Clean separation)
✓ Error Handling (Try-catch, fallbacks)
✓ Deployment Feasibility (Free tier services)

---

**Graduate-level LLM course project ✓**
**Lightweight, modular, production-ready ✓**
