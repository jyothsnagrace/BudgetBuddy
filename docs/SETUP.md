# BudgetBuddy — Setup Guide

## Live Deployments

| Service | URL |
|---|---|
| Frontend (Vercel) | https://budget-buddy-llm-app.vercel.app |
| Backend (Railway) | https://budgetbuddy-group3.up.railway.app |
| API Docs | https://budgetbuddy-group3.up.railway.app/docs |

---

## Prerequisites

### Required:
- **Python 3.12+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/))

### API Accounts (Free Tier):

1. **Google AI Studio** — Gemini Vision (receipt parsing)
   - https://aistudio.google.com/app/apikey

2. **Groq Cloud** — LLaMA 3.1 (chat & expense parsing)
   - https://console.groq.com/keys

3. **Supabase** — PostgreSQL database & auth
   - https://supabase.com → New project → Settings → API

4. **RapidAPI** *(optional)* — Cost of Living data
   - https://rapidapi.com → App falls back to estimates if not configured

---

## Local Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/uncc-llm/Spring-2026-DSBA-6010-Group-3-Budget-Buddy.git
cd Spring-2026-DSBA-6010-Group-3-Budget-Buddy
```

### Step 2: Database Setup

1. Open your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Copy the contents of `database/schema.sql` and run it

### Step 3: Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Create `backend/.env`:

```env
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
JWT_SECRET=generate-a-random-secure-string
RAPIDAPI_KEY=your_rapidapi_key_or_leave_blank
CORS_ORIGINS=http://localhost:5174,http://localhost:5173
```

### Step 4: Frontend Setup

```bash
# From project root
npm install
```

Create `.env` in the project root:

```env
VITE_API_URL=http://localhost:8000
```

---

## Running the Application

### Terminal 1 — Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/

### Terminal 2 — Frontend

```bash
# From project root
npm run dev
```

- App: http://localhost:5174

---

## Testing Features

### 1. Authentication
- Open the app in your browser
- Register or log in with email/password (Supabase Auth)

### 2. Natural Language Expense Entry
- Click **"Quick Add"** tab
- Type: `"Lunch at Chipotle $15"`
- Click **"Parse & Fill"** → review in Manual tab → **"Add Expense"**

### 3. Receipt Photo Parsing
- Click **"Receipt"** tab
- Upload a receipt image (JPG/PNG)
- Click **"Parse Receipt"** → review and submit

### 4. Manual Entry
- Click **"Manual"** tab
- Fill in the form fields → **"Add Expense"**

### 5. AI Chatbot (Cafe Companion)
- Scroll to the companion section
- Ask: `"What did I spend on food this week?"`
- Ask: `"Set my dining budget to $200"`
- Ask: `"How does the cost of living in Austin compare to Charlotte?"`

### 6. Budget Tracking
- Navigate to **Budget Settings** to configure monthly limits
- View **Budget Summary** for category breakdowns

---

## Project Structure

```
Group-3-Budget-Buddy/
├── backend/                    # FastAPI Python backend
│   ├── main.py                # API entry point & routes
│   ├── llm_pipeline.py        # Two-LLM extraction pipeline
│   ├── function_calling.py    # Structured function calling
│   ├── cafe_agents.py         # Companion AI agent
│   ├── receipt_parser.py      # Gemini Vision receipt OCR
│   ├── cost_of_living.py      # RapidAPI cost-of-living integration
│   ├── rag.py                 # Retrieval-Augmented Generation
│   ├── database.py            # Supabase client
│   ├── auth.py                # JWT authentication
│   └── requirements.txt       # Python dependencies
│
├── database/
│   └── schema.sql             # Supabase schema (run once)
│
├── src/
│   └── app/
│       ├── App.tsx            # Root React component
│       └── components/        # UI components
│
├── docs/
│   └── SETUP.md               # This file
├── README.md                  # Project overview
└── package.json               # Node dependencies
```

---

## Troubleshooting

### Backend won't start

**`ModuleNotFoundError`**
```bash
# Must run uvicorn from inside the backend/ directory
cd backend
uvicorn main:app --reload --port 8000
```

**`Supabase connection failed`**
- Verify `SUPABASE_URL` and `SUPABASE_KEY` in `backend/.env`
- Confirm the Supabase project is active and schema has been applied

### Frontend API calls fail

**`Network Error` or CORS error**
- Confirm backend is running on port 8000
- Check `VITE_API_URL=http://localhost:8000` in root `.env`
- Ensure `CORS_ORIGINS` in `backend/.env` includes your frontend port

### LLM errors

**`Invalid API key`**
- Check `GEMINI_API_KEY` and `GROQ_API_KEY` in `backend/.env`
- Groq: https://console.groq.com/keys
- Gemini: https://aistudio.google.com/app/apikey

**`Rate limit exceeded`**
- Groq free tier: 30 req/min for LLaMA 3.1-8b
- Gemini free tier: 15 req/min for Gemini 2.5 Flash

### Receipt parsing not working
- Image must be JPG or PNG, under 10 MB
- Verify `GEMINI_API_KEY` is set and valid

### Cost of living data unavailable
- Expected if `RAPIDAPI_KEY` is not set — app uses fallback estimates automatically

---

## Production Deployment

### Backend (Railway)

1. Create account at https://railway.app
2. New project → **Deploy from GitHub** → select this repo
3. Start command is configured via `railway.toml`: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables:
   - `GEMINI_API_KEY`, `GROQ_API_KEY`
   - `SUPABASE_URL`, `SUPABASE_KEY`
   - `JWT_SECRET`, `RAPIDAPI_KEY`
   - `CORS_ORIGINS=https://budget-buddy-llm-app.vercel.app`
5. Deploy

**Live backend:** https://budgetbuddy-group3.up.railway.app

### Frontend (Vercel)

1. Create account at https://vercel.com
2. **Import GitHub repository**
3. Build settings:
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. Add environment variable:
   - `VITE_API_URL=https://budgetbuddy-group3.up.railway.app`
5. Deploy

**Live frontend:** https://budget-buddy-llm-app.vercel.app

---

## API Reference

Interactive docs: https://budgetbuddy-group3.up.railway.app/docs

### Key Endpoints

```
POST   /auth/register              # Register new user
POST   /auth/login                 # Login, returns JWT
GET    /expenses                   # List expenses
POST   /expenses                   # Create expense
POST   /parse-expense              # Natural language → expense
POST   /parse-receipt              # Receipt image → expense
POST   /chat                       # Companion chatbot
GET    /cost-of-living/{city}      # Cost of living data
```

---

## Course Project Features

| Feature | Status |
|---|---|
| Two-LLM pipeline (Groq + Gemini) | Done |
| Function calling with JSON Schema | Done |
| Multimodal receipt parsing (Vision) | Done |
| RAG-backed companion memory | Done |
| Cost of Living API integration | Done |
| Supabase persistent storage | Done |
| JWT authentication | Done |
| Vercel + Railway deployment | Done |

---

## Notes

### Free Tier Limits

| Service | Limit |
|---|---|
| Groq (LLaMA 3.1-8b) | 30 req/min |
| Gemini 2.5 Flash | 15 req/min |
| Supabase | 500 MB storage, 2 GB bandwidth |
| RapidAPI | 500 req/month (optional) |

### Security

This is a course project. For production hardening:
- Use hashed passwords + refresh tokens
- Add rate limiting middleware
- Enable HTTPS-only cookies
- Rotate `JWT_SECRET` regularly

---

## Support

1. Check [Issues](https://github.com/uncc-llm/Spring-2026-DSBA-6010-Group-3-Budget-Buddy/issues)
2. Test backend at https://budgetbuddy-group3.up.railway.app/docs
3. Check browser console for frontend errors