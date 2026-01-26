# 💰 BudgetBuddy - Personal Finance Management Assistant

A comprehensive, AI-powered personal finance management application that helps you track income, analyze expenses, and create actionable financial plans with personalized recommendations.

## ✨ Features

- 💵 **Income & Expense Tracking** - Easy-to-use interface to log multiple income sources and expenses
- 📊 **Smart Analytics** - Visual expense breakdowns by category with interactive charts
- 📈 **Financial Projections** - 6+ month savings forecasts with dual saving strategies
- 💡 **Personalized Recommendations** - Tailored saving strategies and expense reduction plans
- 🤖 **AI-Powered Summaries** - LLM-generated creative financial narratives and insights
- 📋 **Action Planning** - 12-month phased financial action plan with concrete milestones
- 🎯 **Smart Features**:
  - Auto-generated User IDs from names
  - Edit/Delete capabilities for income and expenses
  - Real-time financial metrics and calculations
  - Multi-page dashboard with tabbed interfaces
  - Seamless data flow between pages

## 🚀 Quick Start

### Prerequisites

```bash
pip install streamlit streamlit-option-menu pandas altair requests python-dotenv
```

### Setup

1. Clone the repository:
```bash
git clone https://github.com/YourUsername/BudgetBuddy.git
cd BudgetBuddy
```

2. Create `.streamlit/secrets.toml`:
```toml
api_base = "http://127.0.0.1:8000"
```

3. Ensure your backend API is running on port 8000

4. Run the Streamlit app:
```bash
streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501` (or next available port)

## 💬 Usage Guide

### **Page 1: Home - Financial Data Entry**

#### Step 1: Enter Your Information
```
👤 User Information:
   - Your Name: John Doe
   - User ID: john_doe (auto-generated)
   - Savings Goal: $5,000
```

#### Step 2: Add Income Sources
```
💵 Income Sources:
   - Salary: $4,500
   - Freelance: $500
   ✅ Total Income: $5,000
```

#### Step 3: Add Expenses
```
💸 Expenses:
   - Rent: $1,500 (Housing)
   - Groceries: $400 (Food)
   - Gas: $150 (Transportation)
   - Utilities: $200 (Utilities)
   ✅ Total Expenses: $2,250
```

#### Step 4: Submit Data
```
📤 Submit Your Data
   ✅ Confirm → Success message with submission details
   Remaining: $2,750/month
```

### **Page 2: Data Analysis - Smart Insights**

#### Expense Breakdown
```
💸 Expense Breakdown by Category
   - Pie chart visualization
   - Category breakdown with percentages
   - Housing: $1,500 (66.7%)
   - Utilities: $200 (8.9%)
```

#### Saving Strategies
```
💡 Personalized Saving Strategies

📈 Aggressive Strategy:
   - Target: $1,250/month (25% of income)
   - Timeline: 4 months to $5,000 goal
   
🎯 Balanced Strategy:
   - Target: $750/month (15% of income)
   - Timeline: 6.7 months to $5,000 goal
```

#### Financial Projections
```
🔮 Financial Projections (6 months)
   - Interactive line chart of cumulative savings
   - Monthly Surplus: $2,750
   - Total Savings (6m): $16,500
   - Progress to Goal: 330%
```

#### Expense Reduction Plan
```
📋 Expense Reduction Opportunities
   - Top 3 categories identified
   - 15% reduction targets with dollar amounts
   - Actionable monthly savings
```

### **Page 3: Summary Dashboard - Action Planning**

#### Creative Summary
```
✨ Generate Creative Summary
   AI-powered personalized financial narrative showing:
   - Income and savings assessment
   - Financial strengths and trajectory
   - Annual projection
   - Encouragement and next steps
```

#### 12-Month Action Plan
```
📋 Action Plan - 3 Phases

🏗️ Phase 1: Foundation (M1-3)
   - Establish emergency fund
   - Weekly expense tracking
   - Subscription cuts (-10%)
   
⚡ Phase 2: Acceleration (M4-6)
   - Build 3-month fund
   - 15% expense reduction
   - Complete automation
   
🚀 Phase 3: Investment (M7-12)
   - 6-month emergency fund
   - Start investing 10%
   - Achieve savings goal
```

#### Financial Tips
```
💡 Essential Financial Tips
   10 actionable tips covering:
   - 50/30/20 budgeting rule
   - Emergency fund building
   - Debt management strategies
   - Investment principles
   - And more...
```

## 🛠️ Architecture

### **Technology Stack**
- **Frontend**: Streamlit (Python web framework)
- **Navigation**: streamlit-option-menu
- **Data Visualization**: Altair (interactive charts)
- **Backend**: FastAPI/Uvicorn REST API (port 8000)
- **Data Management**: Pandas, JSON, FAISS vector store
- **AI Integration**: OpenAI LLM (optional for creative summaries)
- **NLP**: SentenceTransformers for embeddings

### **Project Structure**
```
BudgetBuddy/
├── streamlit_app.py          # Main frontend application (630+ lines)
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── .streamlit/
│   └── secrets.toml         # API configuration
├── app/
│   ├── db.py               # Database operations
│   ├── llm.py              # LLM integration and generation
│   ├── main.py             # FastAPI backend server
│   ├── schemas.py          # Pydantic data models
│   ├── vector_migration.py # Vector store setup
│   └── vectorstore.py      # FAISS vector store operations
├── lib/
│   └── style.css           # Custom CSS styling
├── data/
│   ├── sample_user.json    # Sample financial data
│   └── vectorstore/        # FAISS vector database files
├── prompts/
│   └── system_prompt.txt   # LLM system prompt
└── tests/
    ├── test_api.py         # Backend API tests
    └── test_integration.py # Full integration tests
```

### **Data Flow**

```
User Input (Page 1)
    ↓
Session State Storage (Streamlit)
    ↓
API Submission (POST /ingest)
    ↓
Backend Vector Store Processing (FAISS)
    ↓
Data Analysis (Page 2)
    ↓
LLM Creative Summary Generation (Page 3)
    ↓
Action Plan & Recommendations
```

## 🔄 Key Features Explained

### **Auto-Generated User IDs**
```python
# From name "John Doe"
# Automatically becomes "john_doe"
# No manual entry needed!
```

### **Session State Management**
- User data persists across page navigation
- User ID and name auto-populate on subsequent pages
- Income/expense data maintained throughout session
- Seamless experience without re-entering information

### **Smart Error Handling**
- API timeout management (30-second timeout)
- Connection error detection with helpful messages
- Graceful fallbacks for unavailable services
- Input validation before submission

### **Real-Time Calculations**
- Instant income/expense totals
- Dynamic savings projections
- Automatic progress tracking
- Category-based analysis

## 📊 Data Schema

### User Financial Input
```python
{
    "user_id": "john_doe",
    "name": "John Doe",
    "incomes": [
        {"source": "Salary", "amount": 4500},
        {"source": "Freelance", "amount": 500}
    ],
    "expenses": [
        {"name": "Rent", "amount": 1500, "category": "Housing"},
        {"name": "Groceries", "amount": 400, "category": "Food"}
    ],
    "savings_goal": 5000
}
```

### Expense Categories
- **Housing** - Rent, mortgage, property tax
- **Food** - Groceries, dining out
- **Transportation** - Gas, public transit, car payments
- **Entertainment** - Movies, hobbies, games
- **Utilities** - Electricity, water, internet
- **Other** - Miscellaneous expenses

## 📋 API Endpoints

The FastAPI backend provides three main endpoints:

### POST `/ingest`
Ingests user financial data and stores it in the vector store for context retrieval.
```bash
curl -X POST http://127.0.0.1:8000/ingest \
  -H "Content-Type: application/json" \
  -d @data/sample_user.json
```

### POST `/plan`
Generates a structured 12-month financial action plan.
```bash
curl -X POST http://127.0.0.1:8000/plan \
  -H "Content-Type: application/json" \
  -d '{"user_id": "john_doe"}'
```

### POST `/creative`
Produces a creative, personalized financial narrative and summary.
```bash
curl -X POST http://127.0.0.1:8000/creative \
  -H "Content-Type: application/json" \
  -d '{"user_id": "john_doe"}'
```

## 🎯 Workflow Example

### Day 1: Setup
```
1. Open Home page
2. Enter name "Alice Smith"
3. Add monthly salary: $4,000
4. Add side income: $1,000
5. Add expenses (Rent, Food, Transport, etc.)
6. Click Submit
7. ✅ Data submitted successfully!
```

### Day 2: Analysis
```
1. Navigate to Data Analysis page
2. User ID auto-populated: "alice_smith"
3. View expense breakdown chart
4. Compare saving strategies (Aggressive vs Balanced)
5. See 6-month projection with savings trajectory
```

### Day 3: Planning
```
1. Navigate to Summary Dashboard
2. User info auto-populated from Page 1
3. Click "Generate Creative Summary"
4. Read AI-generated personalized financial story
5. Review 12-month action plan (3 phases)
6. Study financial tips
7. Plan next steps based on recommendations
```

## 🔧 Development & Backend Setup

### Windows PowerShell Quick Start

1. Create and activate virtual environment:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:
```powershell
pip install -r requirements.txt
```

3. Set up environment:
```powershell
copy .env.example .env
# Edit .env to add OPENAI_API_KEY for LLM features
```

4. Run tests:
```powershell
python -m pytest -q
```

5. Start backend server:
```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

6. In another terminal, start Streamlit frontend:
```powershell
streamlit run streamlit_app.py
```

### Code Style & Quality

```bash
# Format code
black streamlit_app.py app/

# Lint code
flake8 streamlit_app.py app/

# Run tests with coverage
pytest --cov=app tests/
```

## 🚀 Future Enhancements

### Short Term
- [ ] Database persistence (SQLite/PostgreSQL)
- [ ] User authentication & profiles
- [ ] Email export functionality
- [ ] PDF report generation
- [ ] Budget alerts & notifications

### Medium Term
- [ ] Mobile app version
- [ ] Dark mode theme
- [ ] Multi-currency support
- [ ] Historical data tracking
- [ ] Advanced analytics (trends, forecasts)

### Long Term
- [ ] Bank account integration
- [ ] Investment tracking
- [ ] Cryptocurrency support
- [ ] Family/couple budgeting
- [ ] Mobile notifications
- [ ] Voice input capability

## 🔐 Security Considerations

- API key stored in `.env` and `.streamlit/secrets.toml` (never commit!)
- Input validation on all user data
- Timeout protection for API calls (30 seconds)
- Error messages don't expose sensitive data
- Session state isolated per user per browser
- FAISS vector store for secure document retrieval

## 🤝 Contributing

### Ideas for Contributions
- 🎨 UI/UX improvements
- 📈 Additional visualization types
- 🤖 More sophisticated AI insights
- 🔌 Third-party integrations
- 📚 Documentation improvements
- 🧪 Additional test coverage

### How to Contribute
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🐛 Known Limitations

- Some packages (faiss-cpu, sentence-transformers) may require compatible Python environment
- Vector store stored in memory/disk - not scalable for many users
- LLM responses depend on API availability and quota

## 📞 Support & Contact

### Get Help
1. Review code comments and docstrings
2. Check [test files](tests/) for usage examples
3. Review [Issues](https://github.com/YourUsername/BudgetBuddy/issues)
4. Create a new issue with detailed description

### Report Bugs
- Describe the issue clearly
- Include steps to reproduce
- Share error messages and stack traces
- Mention Python version and OS

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/) for rapid UI development
- Backend powered by [FastAPI](https://fastapi.tiangolo.com/)
- AI features using [OpenAI](https://openai.com/)
- Charts created with [Altair](https://altair-viz.github.io/)
- Vector search with [FAISS](https://github.com/facebookresearch/faiss) and [SentenceTransformers](https://www.sbert.net/)
- Navigation with [streamlit-option-menu](https://github.com/victoryhb/streamlit-option-menu)
- Inspired by personal finance management best practices

---

**Made with ❤️ for smarter personal finance management**

💰 **Track • Analyze • Plan • Succeed**

*Last Updated: January 25, 2026*

Files of interest:
- `app/main.py` — FastAPI app
- `app/vectorstore.py` — small FAISS wrapper
- `app/llm.py` — LLM wrapper (OpenAI + fallback)
- `prompts/system_prompt.txt` — main system prompt used for budgeting
- `tests/test_api.py` — basic API tests

Next steps / ideas:
- Persist vector store to disk or use a hosted vector DB (Pinecone / Chroma / Weaviate)
 - Persist vector store to disk or use a hosted vector DB (Pinecone / Chroma / Weaviate)
 - Structured JSON output: the LLM is asked to return a JSON budget plan; the code falls back to a heuristic structured plan when OpenAI is not available.

Optional higher-quality embeddings
- By default the project uses a TF-IDF fallback (scikit-learn) for small demos and portability.
- If you want higher-quality embeddings and faster NN search, install `sentence-transformers` and `faiss-cpu` in your environment. Example:

```powershell
# optional: install heavy dependencies for better embeddings (may require build tools)
& ".\.venv\Scripts\python.exe" -m pip install sentence-transformers faiss-cpu
```

Persistence
- The vector store supports `save(path)` and `load(path)` (see `app/vectorstore.py`) which will persist metadatas and the index/docs depending on the backend.

Notes on LLM behavior
- Set `OPENAI_API_KEY` in `.env` to enable real OpenAI calls. Without a key the project uses a deterministic fallback so the demo works offline.
- Add authentication + per-user storage
- Create a React/Streamlit UI for interactive flows
- Add deeper financial logic and risk checks
