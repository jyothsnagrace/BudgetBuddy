# BudgetBuddy Online Deployment

This project is now prepared for:
- **Backend** on Railway (using `railway.toml`)
- **Frontend** on Vercel (using `vercel.json`)

Local working checkpoint saved at: `docs/CHECKPOINT_2026-02-21.md`

---

## 1) Deploy Backend (Railway)

1. Push your repository to GitHub.
2. In Railway, choose **New Project → Deploy from GitHub Repo**.
3. Select this repo.
4. Railway will use `railway.toml` automatically.
5. Add these Railway environment variables:

```env
GEMINI_API_KEY=...
GROQ_API_KEY=...
LLM_PROVIDER=groq
GROQ_MODEL=llama-3.1-8b-instant
SUPABASE_URL=...
SUPABASE_KEY=...
JWT_SECRET_KEY=replace-with-secure-random-value
RAPIDAPI_KEY=... # optional
FRONTEND_URL=https://<your-frontend>.vercel.app
# OR preferred:
# CORS_ORIGINS=https://<your-frontend>.vercel.app,http://localhost:5176

# This deployment
FRONTEND_URL=https://budget-buddy-tau-cyan.vercel.app
# OR preferred:
# CORS_ORIGINS=https://budget-buddy-tau-cyan.vercel.app,http://localhost:5176
```

6. After deploy, verify:
  - `https://budgetbuddy-prod.up.railway.app/health`

---

## 2) Deploy Frontend (Vercel)

1. In Vercel, choose **Add New → Project → Import Git Repository**.
2. Select this repo.
3. Vercel will detect `vercel.json` and Vite settings.
4. Add environment variable:

```env
VITE_API_URL=https://budgetbuddy-prod.up.railway.app
```

5. Deploy and verify the site loads.

---

## 3) Final CORS Check

If login/API requests fail due to CORS:
- Ensure backend env has either:
  - `FRONTEND_URL=https://budget-buddy-tau-cyan.vercel.app`, or
  - `CORS_ORIGINS=https://budget-buddy-tau-cyan.vercel.app`
- Redeploy backend after changing env vars.

---

## 4) Security Before Going Public

- Never commit real `.env` secrets.
- Rotate any API keys that were exposed in logs/chat/history.
- Use a strong random value for `JWT_SECRET_KEY` in production.
