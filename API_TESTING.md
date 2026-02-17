# BudgetBuddy API Testing Guide

Test your backend API independently using these curl commands.

## Prerequisites

1. Backend running on `http://localhost:8000`
2. curl installed (or use Postman)
3. `jq` for pretty JSON (optional): `choco install jq` on Windows

---

## Health Check

### Test API is running
```bash
curl http://localhost:8000/
```

**Expected:**
```json
{
  "status": "healthy",
  "service": "BudgetBuddy API",
  "version": "1.0.0"
}
```

### Detailed health check
```bash
curl http://localhost:8000/health
```

---

## Authentication

### Login (create user)
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"testuser\"}"
```

**Save the token from response!**

```json
{
  "user_id": "abc123...",
  "username": "testuser",
  "token": "eyJhbGc..."
}
```

### Set token as variable (PowerShell)
```powershell
$TOKEN = "eyJhbGc..."  # Replace with your actual token
```

### Verify token
```bash
curl http://localhost:8000/api/auth/verify?token=$TOKEN
```

---

## Expenses

### Create expense (manual)
```bash
curl -X POST http://localhost:8000/api/expenses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"amount\": 15.50,
    \"category\": \"Food\",
    \"description\": \"Lunch at Chipotle\",
    \"date\": \"2026-02-17\"
  }"
```

### Get expenses
```bash
curl http://localhost:8000/api/expenses \
  -H "Authorization: Bearer $TOKEN"
```

### Get expenses by category
```bash
curl "http://localhost:8000/api/expenses?category=Food" \
  -H "Authorization: Bearer $TOKEN"
```

### Get expenses by date range
```bash
curl "http://localhost:8000/api/expenses?start_date=2026-02-01&end_date=2026-02-28" \
  -H "Authorization: Bearer $TOKEN"
```

### Delete expense
```bash
curl -X DELETE http://localhost:8000/api/expenses/EXPENSE_ID \
  -H "Authorization: Bearer $TOKEN"
```

---

## Natural Language Parsing

### Parse natural language expense
```bash
curl -X POST http://localhost:8000/api/parse-expense \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"text\": \"Dinner at Olive Garden forty-five dollars\"}"
```

**Expected:**
```json
{
  "success": true,
  "parsed_data": {
    "amount": 45.0,
    "category": "Food",
    "description": "Dinner at Olive Garden",
    "date": "2026-02-17"
  }
}
```

### Test various formats
```bash
# Informal
curl -X POST http://localhost:8000/api/parse-expense \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"text\": \"coffee 5 bucks\"}"

# With date
curl -X POST http://localhost:8000/api/parse-expense \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"text\": \"uber to airport $25 yesterday\"}"

# Multiple items
curl -X POST http://localhost:8000/api/parse-expense \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"text\": \"groceries 120.50\"}"
```

---

## Receipt Parsing

### Parse receipt image

**Windows PowerShell:**
```powershell
curl -X POST http://localhost:8000/api/parse-receipt `
  -H "Authorization: Bearer $TOKEN" `
  -F "file=@C:\path\to\receipt.jpg"
```

**Mac/Linux:**
```bash
curl -X POST http://localhost:8000/api/parse-receipt \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/receipt.jpg"
```

---

## Function Calling

### Execute function via natural language
```bash
curl -X POST http://localhost:8000/api/function-call \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"message\": \"Add a 30 dollar expense for movie tickets\"}"
```

### Set budget
```bash
curl -X POST http://localhost:8000/api/function-call \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"message\": \"Set my food budget to 500 dollars\"}"
```

### Query expenses
```bash
curl -X POST http://localhost:8000/api/function-call \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"message\": \"Show me all food expenses this month\"}"
```

---

## Budgets

### Create budget
```bash
curl -X POST http://localhost:8000/api/budgets \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"monthly_limit\": 2000.00,
    \"category\": null,
    \"month\": \"2026-02\"
  }"
```

### Get budgets
```bash
curl http://localhost:8000/api/budgets \
  -H "Authorization: Bearer $TOKEN"
```

### Budget comparison
```bash
curl http://localhost:8000/api/budget-comparison \
  -H "Authorization: Bearer $TOKEN"
```

---

## Chatbot

### Send message to chatbot
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"message\": \"What's a good budget restaurant in Seattle?\",
    \"city\": \"Seattle, WA\"
  }"
```

### Ask about budgeting
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"message\": \"Am I spending too much on food?\"
  }"
```

### City-specific advice
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"message\": \"Should I buy or rent in Austin?\",
    \"city\": \"Austin, TX\"
  }"
```

---

## Cost of Living

### Get city data
```bash
curl http://localhost:8000/api/cost-of-living/Seattle,%20WA
```

### Get supported cities
```bash
curl http://localhost:8000/api/cities
```

---

## Calendar

### Get calendar entries
```bash
curl http://localhost:8000/api/calendar \
  -H "Authorization: Bearer $TOKEN"
```

### Get calendar for date range
```bash
curl "http://localhost:8000/api/calendar?start_date=2026-02-01&end_date=2026-02-28" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Insights

### Get AI-generated insights
```bash
curl http://localhost:8000/api/insights \
  -H "Authorization: Bearer $TOKEN"
```

---

## Complete Test Flow

### Step 1: Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"testuser123\"}" > response.json

# Extract token (requires jq)
TOKEN=$(cat response.json | jq -r '.token')
echo "Token: $TOKEN"
```

### Step 2: Parse natural language
```bash
curl -X POST http://localhost:8000/api/parse-expense \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"text\": \"Lunch 15 dollars\"}" | jq
```

### Step 3: Create expense
```bash
curl -X POST http://localhost:8000/api/expenses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"amount\": 15.00,
    \"category\": \"Food\",
    \"description\": \"Lunch\",
    \"date\": \"2026-02-17\"
  }" | jq
```

### Step 4: Get expenses
```bash
curl http://localhost:8000/api/expenses \
  -H "Authorization: Bearer $TOKEN" | jq
```

### Step 5: Chat with bot
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"message\": \"How am I doing with my budget?\"}" | jq
```

---

## Testing Error Handling

### Invalid token
```bash
curl http://localhost:8000/api/expenses \
  -H "Authorization: Bearer invalid_token"
```

**Expected: 401 Unauthorized**

### Invalid data
```bash
curl -X POST http://localhost:8000/api/expenses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"amount\": -10}"
```

**Expected: 422 Validation Error**

### Missing fields
```bash
curl -X POST http://localhost:8000/api/expenses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"description\": \"test\"}"
```

**Expected: 422 Validation Error**

---

## API Documentation

For complete interactive API docs, visit while backend is running:

**Swagger UI:** http://localhost:8000/docs  
**ReDoc:** http://localhost:8000/redoc

---

## Performance Testing

### Measure response time
```bash
curl -w "\nTime: %{time_total}s\n" \
  -X POST http://localhost:8000/api/parse-expense \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"text\": \"coffee 5 dollars\"}"
```

### Load test (10 requests)
**PowerShell:**
```powershell
1..10 | ForEach-Object {
  curl -X POST http://localhost:8000/api/parse-expense `
    -H "Content-Type: application/json" `
    -H "Authorization: Bearer $TOKEN" `
    -d "{\"text\": \"test $($_)\"}"
}
```

---

## Troubleshooting

### Connection refused
```
Error: Failed to connect to localhost:8000
```
**Fix:** Ensure backend is running: `cd backend && python main.py`

### 401 Unauthorized
```
{"error": "Invalid token"}
```
**Fix:** Get new token via `/api/auth/login`

### 422 Validation Error
```
{"error": "Validation failed"}
```
**Fix:** Check request body matches schema

### 500 Internal Server Error
```
{"error": "Internal server error"}
```
**Fix:** 
1. Check backend logs
2. Verify environment variables
3. Check Supabase connection

---

## Tips

1. **Pretty JSON**: Pipe to `jq` for formatted output
   ```bash
   curl ... | jq
   ```

2. **Save responses**: Redirect to file
   ```bash
   curl ... > response.json
   ```

3. **Verbose mode**: Add `-v` for debugging
   ```bash
   curl -v ...
   ```

4. **Follow redirects**: Add `-L`
   ```bash
   curl -L ...
   ```

---

**Happy Testing! 🚀**

For issues, check backend logs or see SETUP.md for troubleshooting.
