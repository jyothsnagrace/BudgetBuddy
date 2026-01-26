# BudgetBuddy: AI-Powered Personal Finance Management System

## Project Proposal
### Course: 6010 Applications of Large Language Models (UNCC Spring 2026)
### Submitted: January 27, 2026

---

## 1. PROBLEM STATEMENT

### The Problem
Most personal finance management tools are reactive—they track historical spending but fail to provide meaningful, personalized insights or forward-looking guidance. Users struggle with:

- **Lack of Personalization**: Generic tips that don't fit individual financial situations
- **Analysis Paralysis**: Too much raw data, not enough actionable recommendations
- **Limited Accessibility**: Professional financial advisors are expensive; traditional budgeting apps are impersonal
- **No Narrative Context**: Numbers alone don't inspire change or build financial literacy

### Target Users
**Primary:** Individuals aged 25-45, tech-savvy, seeking to understand and improve their financial situation
- Young professionals managing their first significant income
- Self-employed individuals with variable income
- Couples/families coordinating finances
- Anyone wanting to optimize savings and reach financial goals

**Secondary:** Financial educators, financial wellness programs in companies

### Market Opportunity
The global personal finance software market is worth $2.3B (2024) with 12% CAGR. AI-powered personalization is the next frontier, with competitors like Copper, Rocket Money, and emerging AI financial assistants capturing mindshare.

---

## 2. PROPOSED SOLUTION

### Core Value Proposition
**"Turn your financial data into personalized stories and actionable plans"**

BudgetBuddy combines AI-powered narrative generation with traditional financial analysis to:
1. Provide intelligent analysis of spending patterns
2. Generate personalized financial narratives (creative summaries)
3. Create actionable 12-month financial plans
4. Offer data-driven insights and recommendations

### Key Features

#### **Page 1: Home - Financial Data Entry**
- User registration with auto-generated IDs (firstname_lastname)
- Income source tracking (salary, freelance, investments, etc.)
- Expense management with categories (Housing, Food, Transportation, etc.)
- Full CRUD operations with inline editing and deletion
- Real-time financial metrics and validation

#### **Page 2: Data Analysis - Smart Insights**
- Interactive expense breakdown visualization (pie chart)
- Dual saving strategies: Aggressive (25% of income) and Balanced (15% of income)
- 6-month financial projections with cumulative savings visualization
- Category-level expense reduction opportunities (15% cut targets)
- Automatic calculation of time to reach savings goals

#### **Page 3: Summary Dashboard - AI-Powered Planning**
- **Creative Summary Tab**: LLM-generated personalized financial narrative
  - Unique narrative about user's financial situation
  - Strengths and opportunities identified
  - Annual income projection
  - Motivation and encouragement
  
- **Action Plan Tab**: 12-month phased financial plan
  - Phase 1 (Months 1-3): Foundation building
  - Phase 2 (Months 4-6): Acceleration phase
  - Phase 3 (Months 7-12): Investment & scaling
  - Expandable sections with specific goals and actions
  
- **Tips Tab**: 10 personalized financial tips
  - 50/30/20 budgeting rule
  - Emergency fund strategies
  - Debt management techniques
  - Long-term investment principles

### Technical Approach

**Architecture Pattern:** Full-stack LLM application with RAG (Retrieval-Augmented Generation)

**Frontend-Backend Separation:**
- Frontend: Streamlit UI (user-friendly, rapid development)
- Backend: FastAPI (modular, REST API endpoints)
- Communication: HTTP requests with JSON payloads

**LLM Integration:**
- Model: OpenAI GPT-4o (selected after model comparison)
- Technique: Prompt engineering + RAG
- Context: Financial documents and user data vectorized for retrieval
- Fallback: Graceful degradation with template-based summaries

---

## 3. TECHNICAL STACK

### Frontend
- **Framework:** Streamlit (Python web framework for rapid development)
- **Navigation:** streamlit-option-menu (multi-page navigation)
- **Visualization:** Altair (interactive charts and graphs)
- **Data Management:** Pandas DataFrames, Streamlit session_state

### Backend
- **Framework:** FastAPI (modern, fast Python web framework)
- **Server:** Uvicorn ASGI server (port 8000)
- **Data Validation:** Pydantic models for strict type checking
- **HTTP Client:** Requests library with timeout and error handling

### AI/ML Components
- **LLM API:** OpenAI GPT-4o (primary) with fallback options
- **Embeddings:** SentenceTransformers all-MiniLM-L6-v2 (384-dim)
- **Vector Database:** FAISS (Facebook AI Similarity Search)
- **Document Processing:** Chunking (512 tokens, 100-token overlap)

### Data & Storage
- **Primary Storage:** JSON files (data/sample_user.json)
- **Vector Store:** FAISS indices (data/vectorstore/)
- **Configuration:** Environment variables (.env), Streamlit secrets

### Development & Deployment
- **Language:** Python 3.11.7
- **Environment:** Conda virtual environment
- **Package Management:** pip with requirements.txt
- **Version Control:** Git + GitHub
- **Testing:** pytest for unit and integration tests
- **Deployment Target:** Streamlit Cloud or HuggingFace Spaces

---

## 4. SYSTEM ARCHITECTURE

### High-Level Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                   FRONTEND (Streamlit)                   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Page 1: Home (CRUD Operations)                  │   │
│  │  ├─ User registration & auto-ID generation       │   │
│  │  ├─ Income/expense entry & management            │   │
│  │  └─ Submit financial data to backend              │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Page 2: Data Analysis (Analytics)               │   │
│  │  ├─ Expense visualization (pie chart)            │   │
│  │  ├─ Saving strategies & projections              │   │
│  │  └─ Reduction opportunities                      │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Page 3: Summary Dashboard (AI Insights)         │   │
│  │  ├─ Creative Summary (LLM-generated)             │   │
│  │  ├─ 12-month Action Plan (3 phases)              │   │
│  │  └─ Financial Tips (10 actionable items)         │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                         │ HTTP
                         ↓
         ┌────────────────────────────────────┐
         │   BACKEND (FastAPI on port 8000)   │
         │  ┌──────────────────────────────┐  │
         │  │  Endpoints:                  │  │
         │  │  POST /ingest  (Store data)  │  │
         │  │  POST /plan    (Generate)    │  │
         │  │  POST /creative (LLM call)   │  │
         │  └──────────────────────────────┘  │
         └────────────────────────────────────┘
                  │           │            │
        ┌─────────┴────┐   ┌──┴────────┐  └────────────┐
        │              │   │           │               │
        ↓              ↓   ↓           ↓               ↓
   ┌────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
   │ FAISS  │   │  System  │   │ OpenAI  │   │  Error   │
   │ Vector │   │  Prompt  │   │ GPT-4o  │   │ Handling │
   │ Store  │   │          │   │  API    │   │& Logging │
   └────────┘   └──────────┘   └──────────┘   └──────────┘
```

### Component Descriptions

**Frontend (Streamlit)**
- Multi-page interface with sidebar navigation
- Session state for cross-page data persistence
- Real-time validation and error messages
- Interactive visualizations with Altair

**Backend (FastAPI)**
- RESTful API with three main endpoints
- Pydantic validation for all inputs
- Error handling with meaningful messages
- Timeout protection (30 seconds per request)

**Vector Store (FAISS)**
- Financial best-practices documents
- Embeddings for semantic search
- Retrieved context injected into prompts
- Fast similarity search (<100ms)

**LLM Integration**
- System prompt for financial domain context
- Few-shot examples for narrative generation
- Chain-of-thought reasoning for plan generation
- Fallback templates when API unavailable

---

## 5. SUCCESS CRITERIA & EVALUATION METRICS

### Functional Requirements
✅ All three pages work without errors  
✅ CRUD operations persist across sessions  
✅ API requests complete within 30 seconds  
✅ Graceful fallback when API unavailable  

### Performance Metrics
- **Page Load Time:** <2 seconds (p95)
- **Data Submission:** <5 seconds (p95)
- **Creative Summary Generation:** <10 seconds (p95)
- **API Error Rate:** <1%

### Quality Metrics

**Financial Accuracy**
- Income total verification: Exact match
- Expense categorization: 95%+ accuracy
- Savings calculation: ±$1 tolerance

**Narrative Quality**
- Faithfulness: Generated facts aligned with data (>0.8)
- Relevance: Recommendations fit user profile (>0.8)
- Clarity: User understands suggestions (4/5 stars)

**RAG Quality**
- Retrieval precision@3: >0.9 (top-3 docs relevant)
- Hallucination rate: <5% unsupported claims
- Source attribution: All facts backed by retrieved docs

**Cost Efficiency**
- API cost per user session: <$0.05
- Infrastructure cost: <$0.01 per session
- Embedding storage: <1MB per user

### User Satisfaction
- 4/5 or higher rating on clarity of recommendations
- 4/5 or higher on actionability of advice
- 4/5 or higher on trustworthiness of narratives

---

## 6. IMPLEMENTATION TIMELINE & MILESTONES

### Weeks 1-3: Foundation (Weeks 1-3)
- ✅ Team formation and ideation (Milestone 1)
- ✅ Project proposal submission (Milestone 2)
- ✅ LLM model comparison and selection (Milestone 3)

### Weeks 4-7: Core Development (Weeks 4-7)
- ✅ Core prompt engineering (Milestone 4)
- ✅ Tool calling and API endpoints (Milestone 5)
- ✅ Fine-tuning evaluation (Milestone 6)
- ✅ RAG pipeline implementation (Milestone 7)

### Weeks 8-10: Features & Agents (Weeks 8-10)
- ✅ Multimodal capabilities [OPTIONAL] (Milestone 8)
- ✅ MVP submission (Milestone 9)
- ✅ Agent architecture design (Milestone 10)

### Weeks 11-15: Polish & Deployment (Weeks 11-15)
- 📊 Performance evaluation (Milestone 11) - **IN PROGRESS**
- 🔒 Security audit (Milestone 12)
- 🚀 Production deployment (Milestone 13)
- 📈 Scaling and cost analysis (Milestone 14)
- 🎉 Final wrap-up and launch (Milestone 15)

---

## 7. EXPECTED OUTCOMES & DELIVERABLES

### Code & Documentation
- Clean, well-commented Python codebase (700+ lines)
- Comprehensive README with setup and usage instructions
- Architecture documentation with diagrams
- API documentation (Swagger/OpenAPI)
- Design decision document with rationale

### Application
- Fully functional Streamlit application
- FastAPI backend with 3+ endpoints
- FAISS vector store for RAG
- Error handling and graceful degradation
- Monitoring and logging framework

### Evaluation & Analysis
- Comprehensive evaluation metrics (accuracy, quality, cost)
- Security audit report with red teaming results
- Performance benchmark results
- Cost analysis and scaling projections

### Presentation Materials
- 10-minute demo video
- Slide deck with technical details
- Final presentation (10-min + Q&A)
- Project repository on GitHub

---

## 8. COMPETITIVE ADVANTAGE & INNOVATION

### What Makes This Project Unique
1. **Personalized Narratives**: Unlike traditional budgeting apps, BudgetBuddy generates unique, engaging financial stories
2. **Actionable AI**: Not just analysis, but specific, phased plans with concrete actions
3. **Privacy-First**: No third-party integrations, user data stays local
4. **Modular Design**: Easy to extend with additional models, strategies, or visualizations
5. **Production-Ready**: Error handling, monitoring, and deployment built in from day one

### Potential Extensions
- Receipt OCR with vision API (multimodal)
- Voice input for quick expense logging
- Bank account integration (OAuth)
- Multiple user support with authentication
- Investment recommendation engine
- Tax planning and optimization
- Collaborative family budgeting

---

## 9. RISK ANALYSIS & MITIGATION

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|-----------|
| LLM API rate limits | Project blocked | Medium | Implement caching, fallback templates, rate limiting |
| Poor narrative quality | Low user satisfaction | Low | Use fallback templates, iterate prompts, A/B test |
| High API costs | Budget exceeded | Medium | Model selection (GPT-3.5 fallback), caching, batching |
| Data privacy concerns | Legal issues | Low | No data logging, local storage, compliance docs |
| Model hallucinations | Inaccurate advice | Medium | Source attribution, fact-checking, user disclaimers |
| Deployment issues | Missed deadline | Low | Early testing, Docker containerization, CI/CD setup |

---

## 10. CONCLUSION

BudgetBuddy demonstrates the practical application of large language models to real-world problems. By combining prompt engineering, RAG, and agent architecture, this project delivers personalized financial insights that go beyond traditional budgeting apps.

The modular design and comprehensive evaluation framework ensure that the application is not just functional, but production-ready and measurable. The project aligns with all course learning objectives while maintaining focus on user value and business viability.

**Timeline:** 15 weeks (January 20 - April 28, 2026)  
**Team:** 1 student (individual project)  
**Estimated Effort:** 200+ hours

---

**Prepared by:** [Student Name]  
**Date:** January 27, 2026  
**Course:** 6010 Applications of Large Language Models  
**Institution:** University of North Carolina at Charlotte

---

## APPENDIX: Technical Specifications

### System Requirements
- Python 3.8+
- 2GB RAM (minimum)
- Internet connection (for API calls)
- 500MB disk space

### API Endpoints

```
POST /ingest
├─ Input: UserFinanceInput (user_id, name, incomes[], expenses[], savings_goal)
├─ Processing: Store in FAISS vector store
└─ Output: Success/error message

POST /plan
├─ Input: {user_id: string}
├─ Processing: Retrieve context, generate 12-month plan
└─ Output: JSON with 3 phases and action items

POST /creative
├─ Input: {user_id: string}
├─ Processing: RAG + LLM generation
└─ Output: Creative narrative summary
```

### Dependencies
```
streamlit==1.28.0
fastapi==0.104.0
pandas==2.1.0
altair==5.0.0
requests==2.31.0
pydantic==2.4.0
faiss-cpu==1.7.4
sentence-transformers==2.2.2
python-dotenv==1.0.0
```

### Environment Variables
```
OPENAI_API_KEY=sk-...
API_BASE=http://127.0.0.1:8000
LOG_LEVEL=INFO
```

---
