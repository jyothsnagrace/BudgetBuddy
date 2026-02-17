
# BudgetBuddy 🐧💰

> **An LLM-Powered Expense Tracking App for Graduate-Level AI Course**

BudgetBuddy is a lightweight, intelligent expense tracking application that showcases modern LLM integration patterns, multimodal input processing, and clean software architecture. Built as a graduate-level course project demonstrating production-ready AI application development.

---

## ✨ Key Features

### 🤖 Dual-LLM Pipeline
- **LLM #1**: Extracts structured data from natural language
- **LLM #2**: Normalizes categories, validates dates, cleans amounts
- **Validation**: JSON Schema enforcement for data integrity

### 📝 Three Input Methods
1. **Quick Add** - Type naturally: "Lunch at Chipotle $15"
2. **Receipt Photo** - Upload receipt → AI extracts data
3. **Manual Entry** - Traditional form input

### 🎯 Structured Function Calling
- `add_expense()` - Add new expense with validation
- `set_budget()` - Set monthly budget limits
- `query_expenses()` - Retrieve filtered expenses
- `get_budget_status()` - Check budget vs actual

### 👁️ Vision Processing
- Gemini Vision API for receipt OCR
- Automatic expense extraction from images
- Multi-item receipt parsing support

### 🌍 Cost of Living Integration
- Real-time data for 50+ US cities
- Budget recommendations based on location
- City comparison tools
- Graceful fallback when API unavailable

### 💬 Smart Money Avatar
- Context-aware responses
- City-specific advice
- Friendship-level personality adaptation
- Multiple pet companions (Penguin, Dragon, Capybara, Cat)

### 🗄️ Production-Ready Backend
- FastAPI Python backend
- Supabase PostgreSQL database
- JWT authentication
- RESTful API design

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│              React Frontend (Vite)                      │
│   SpendingForm | BudgetBuddy | Calendar | Analytics    │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│         FastAPI Backend (Python)                        │
├─────────────────────────────────────────────────────────┤
│  LLM Pipeline | Function Calling | Vision Processing   │
│  Auth Manager | Database Client | Cost of Living API   │
└─────────────┬──────────────────────────┬────────────────┘
              │                          │
              ▼                          ▼
    ┌──────────────────┐      ┌──────────────────┐
    │    Supabase      │      │  External APIs   │
    │   PostgreSQL     │      │  - RapidAPI      │
    └──────────────────┘      │  - Gemini        │
                              └──────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Gemini API key (free)
- Supabase account (free)

### 1. Clone & Install

```bash
git clone https://github.com/jyothsnagrace/BudgetBuddy.git
cd BudgetBuddy

# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys

# Frontend
cd ..
npm install
cp .env.example .env
# Edit .env with backend URL
```

### 2. Setup Database

1. Create Supabase project at https://supabase.com
2. Run `database/schema.sql` in SQL Editor
3. Copy URL and anon key to `backend/.env`

### 3. Run Application

```bash
# Terminal 1: Backend
cd backend
python main.py

# Terminal 2: Frontend
npm run dev
```

Open http://localhost:5173

**📖 Full setup guide:** [SETUP.md](SETUP.md)

---

## 🎓 Course Project Requirements

| Requirement | Status | Implementation |
|------------|--------|----------------|
| LLM Integration | ✅ | Gemini 1.5 Flash |
| Prompt Design | ✅ | System prompts + context injection |
| Structured Outputs | ✅ | JSON Schema validation |
| Function Calling | ✅ | Schema-based execution |
| Multimodal Input | ✅ | Receipt photo processing |
| Voice Input | ⚠️ | Optional (browser Speech API) |
| Vision Processing | ✅ | Gemini Vision for receipts |
| External API | ✅ | Cost of Living API |
| Persistent Storage | ✅ | Supabase PostgreSQL |
| Authentication | ✅ | Username + JWT tokens |
| Modular Architecture | ✅ | Clean separation of concerns |
| Error Handling | ✅ | Try-catch + fallbacks |
| Deployment Ready | ✅ | Free tier compatible |

**13/14 Requirements Met** ✅

---

## 📸 Screenshots

### SpendingForm - Three Input Methods
```
┌────────────────────────────────────────┐
│  Quick Add │ Receipt Photo │ Manual ✓ │
├────────────────────────────────────────┤
│  Type naturally:                       │
│  "Lunch at Chipotle $15"              │
│                                        │
│  [Parse & Fill] ← Switches to Manual │
└────────────────────────────────────────┘
```

### Smart Chatbot
```
User: "Budget restaurant in Seattle?"
Penny 🐧: Dick's Drive-In! $5-8/meal, 
         Seattle icon since 1954! 🍔
```

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.110+
- **LLM**: Google Gemini 1.5 Flash
- **Database**: Supabase (PostgreSQL)
- **Validation**: Pydantic + JSON Schema
- **Auth**: JWT (python-jose)

### Frontend
- **Framework**: React 18 + Vite
- **UI**: Radix UI + Tailwind CSS
- **State**: React Hooks
- **Charts**: Recharts

### APIs
- **LLM**: Google Gemini (free tier: 60 req/min)
- **Database**: Supabase (free: 500MB)
- **Cost of Living**: RapidAPI (optional)

---

## 📁 Project Structure

```
BudgetBuddy/
├── backend/                   # Python FastAPI
│   ├── main.py               # API routes
│   ├── llm_pipeline.py       # Two-LLM system
│   ├── function_calling.py   # Structured calling
│   ├── receipt_parser.py     # Vision processing
│   ├── cost_of_living.py     # COL API
│   ├── database.py           # Supabase client
│   └── auth.py               # Authentication
├── database/
│   └── schema.sql            # Database schema
├── src/app/components/
│   ├── SpendingForm.tsx      # 3-method input
│   ├── BudgetBuddy.tsx       # AI chatbot
│   └── ...                   # Other components
├── ARCHITECTURE.md           # System design
├── SETUP.md                  # Installation guide
└── README.md                 # This file
```

---

## 🔑 API Endpoints

### Authentication
```
POST /api/auth/login          # Username-only login
```

### Expenses
```
POST /api/expenses            # Create expense
GET  /api/expenses            # List expenses
POST /api/parse-expense       # Parse natural language
POST /api/parse-receipt       # Parse receipt photo
```

### AI Features
```
POST /api/chat                # Chatbot interaction
POST /api/function-call       # Execute LLM function
GET  /api/insights            # AI-generated insights
```

### Utilities
```
GET  /api/cost-of-living/{city}  # COL data
GET  /api/cities                 # Supported cities
```

**Full API docs:** http://localhost:8000/docs (when backend running)

---

## 🎯 UX Highlights

✅ **Default Focus**: Manual Entry tab on page load  
✅ **Smart Navigation**: Auto-switch after "Parse & Fill"  
✅ **No Scroll Jumps**: Prevents page repositioning  
✅ **Chatbot Focus**: Cursor returns after sending  
✅ **Mobile Responsive**: Works on all screen sizes  

---

## 🌐 Deployment

### Free Tier Options

**Backend:** Railway / Render  
**Frontend:** Vercel / Netlify  
**Database:** Supabase  

**Deployment guide:** [SETUP.md#deployment](SETUP.md#deployment)

---

## 🔒 Security Notes

⚠️ **Educational Project**

This app uses simplified authentication (username-only) suitable for a course project. For production:

- Add password hashing (bcrypt)
- Implement refresh tokens
- Add rate limiting
- Enable HTTPS only
- Sanitize all inputs
- Add CSRF protection

---

## 📊 Performance

| Operation | Time |
|-----------|------|
| LLM Parse | ~2s |
| Receipt OCR | ~3s |
| Database Query | <100ms |
| API Response | <50ms |

---

## 🤝 Contributing

This is a course project, but suggestions welcome!

1. Fork the repository
2. Create feature branch
3. Make changes
4. Submit pull request

---

## 📄 License

This project is for educational purposes.

---

## 🙏 Acknowledgments

- **Google Gemini** - Free LLM API
- **Supabase** - Open-source Firebase alternative
- **Radix UI** - Accessible UI components
- **Shadcn/ui** - Component library
- **FastAPI** - Modern Python web framework

---

## 📞 Support

- **Documentation**: See [SETUP.md](SETUP.md) and [ARCHITECTURE.md](ARCHITECTURE.md)
- **Issues**: [GitHub Issues](https://github.com/jyothsnagrace/BudgetBuddy/issues)
- **API Docs**: http://localhost:8000/docs

---

## 🎓 Course Context

**Project Type**: Graduate-Level LLM Application Development  
**Key Learning**: Production LLM integration patterns  
**Technologies**: Multi-agent systems, structured outputs, multimodal AI  

**Built with ❤️ for learning and demonstrating modern AI application architecture**

---

This is a code bundle for Budgeting app with AI companion. The original project is available at https://www.figma.com/design/xxZc4Cv2Rx4n3PLo8vfpmN/Budgeting-app-with-AI-companion.

## Running the code

Run `npm i` to install the dependencies.

Run `npm run dev` to start the development server.

