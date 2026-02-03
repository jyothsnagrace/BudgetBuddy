# Deploying BudgetBuddy to Streamlit Cloud

## Quick Start

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/BB_Project.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your GitHub repository
   - Set main file path: `streamlit_app.py`
   - Click "Deploy"

## Configuration

### Required Secrets (Optional)

If you want to use the backend API features, add these secrets in Streamlit Cloud:

1. Go to your app settings on Streamlit Cloud
2. Click "Secrets" in the left sidebar
3. Add the following:

```toml
# Backend API URL (optional - app works without it)
api_base = "http://127.0.0.1:8000"

# If you have deployed your FastAPI backend separately:
# api_base = "https://your-backend-api.com"
```

### Backend API (Optional)

The Streamlit app can run standalone without the backend API. However, for full functionality (AI-powered summaries and plans), you'll need to:

1. **Option A: Deploy backend separately**
   - Deploy the FastAPI app (`app/main.py`) to a service like:
     - Railway.app
     - Render.com
     - Heroku
     - Google Cloud Run
   - Update the `api_base` secret in Streamlit Cloud with your backend URL

2. **Option B: Use without backend**
   - The app will work in read-only mode
   - Users can track income/expenses and view analysis
   - AI features will show fallback content

### Environment Variables for Backend

If deploying the backend, set these environment variables:

```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
BUDGETBUDDY_DATA_DIR=data
```

## Local Development

1. **Install dependencies:**
   ```bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1  # Windows PowerShell
   pip install -r requirements.txt
   ```

2. **Run Streamlit app:**
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Run FastAPI backend (optional):**
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```

## File Structure

```
BB_Project/
├── streamlit_app.py          # Main Streamlit app (entry point)
├── requirements.txt           # Python dependencies
├── .streamlit/
│   ├── config.toml           # Streamlit configuration
│   └── secrets.toml.example  # Example secrets file
├── app/                      # Backend API (optional)
│   ├── main.py
│   ├── db.py
│   ├── llm.py
│   └── ...
├── lib/                      # Helper functions
├── data/                     # Data files
└── docs/                     # Documentation
```

## Troubleshooting

### App won't start
- Check that `requirements.txt` is valid
- Ensure `streamlit_app.py` is in the root directory
- Check Streamlit Cloud logs for errors

### Backend API not working
- Verify the `api_base` secret is set correctly
- Ensure your backend is deployed and accessible
- Check backend API health endpoint

### Dependencies issues
- Make sure all packages in `requirements.txt` are compatible
- Some packages may need specific versions for Streamlit Cloud

## Support

For issues with:
- **Streamlit Cloud**: [Streamlit Community Forum](https://discuss.streamlit.io/)
- **This App**: Open an issue on GitHub

## Notes

- The app is designed to work standalone without the backend
- Backend features enhance functionality but aren't required
- Keep your secrets secure and never commit them to GitHub
- Free tier on Streamlit Cloud has resource limitations
