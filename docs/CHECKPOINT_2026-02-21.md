# Checkpoint — 2026-02-21

## Status
- Frontend running: http://localhost:5176
- Backend running: http://localhost:8000
- Backend health endpoint: http://localhost:8000/health

## Running Terminals
- Frontend terminal ID: `1c7dbdfe-9b22-4b61-891d-faa5b3d79970`
- Backend terminal ID: `f4cfd548-0209-4ea2-9048-88d79aa14619`

## Restart Commands
From repository root:

```powershell
# Backend
Set-Location backend
C:/Users/jyoth/Downloads/Project_0210/BudgetBuddy/.venv-3/Scripts/python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (run in another terminal at repo root)
npm run dev -- --host 0.0.0.0 --port 5176
```

## Deployment Baseline
This checkpoint was created before adding online deployment configuration for Railway (backend) + Vercel (frontend).

## Deployment URLs (Updated)
- Railway backend URL: https://budgetbuddy-prod.up.railway.app/
- Vercel frontend URL: https://budget-buddy-tau-cyan.vercel.app/
