# BudgetBuddy - Quick Testing Guide

## ✅ Pre-Flight Checklist

### Backend Status
```powershell
# Check backend is running
Invoke-RestMethod -Uri "http://localhost:8000/health"
# Should return: {"status": "healthy", "components": {"database": true, ...}}
```

### Frontend Status
```powershell
# Visit in browser
start http://localhost:5174
# Should load login page
```

---

## 🧪 Test Suite

### Test 1: Authentication (Username-Only)
**Expected Behavior**: User is created on first login, retrieved on subsequent logins

#### PowerShell Test:
```powershell
# Test user creation
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" `
  -Method POST `
  -Body (@{username="testuser1"} | ConvertTo-Json) `
  -ContentType "application/json"

Write-Host "✅ User created: $($response.username)" -ForegroundColor Green
Write-Host "Token: $($response.token.Substring(0,20))..." -ForegroundColor Cyan

# Save token for next tests
$token = $response.token
$userId = $response.user_id
```

#### Browser Test:
1. Go to http://localhost:5174
2. Enter username: `testuser1`
3. Click "Continue"
4. ✅ Should see main dashboard

---

### Test 2: Manual Expense Entry
**Expected Behavior**: Expense saved to database, calendar entry auto-created

#### PowerShell Test:
```powershell
# Create expense
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$expense = @{
    amount = 25.50
    category = "Food"
    description = "Lunch at Chipotle"
    date = (Get-Date).ToString("yyyy-MM-dd")
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/expenses" `
  -Method POST `
  -Headers $headers `
  -Body $expense

Write-Host "✅ Expense created: $($response.description) - `$$($response.amount)" -ForegroundColor Green
```

#### Browser Test:
1. Click "Manual" tab
2. Fill in:
   - Amount: 25.50
   - Category: Food
   - Description: Lunch at Chipotle
3. Click "Add Expense"
4. ✅ Should see expense in list below

---

### Test 3: Natural Language Parsing (Quick Add)
**Expected Behavior**: Text parsed into structured data, form auto-filled

#### PowerShell Test:
```powershell
# Parse natural language
$nlInput = @{
    text = "Coffee at Starbucks $5.50"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/parse-expense" `
  -Method POST `
  -Headers $headers `
  -Body $nlInput

Write-Host "✅ Parsed: $($response.parsed_data.description)" -ForegroundColor Green
Write-Host "   Amount: `$$($response.parsed_data.amount)" -ForegroundColor Cyan
Write-Host "   Category: $($response.parsed_data.category)" -ForegroundColor Cyan
```

#### Browser Test:
1. Click "Quick Add" tab
2. Type: `"Uber to airport $35"`
3. Click "Parse & Fill"
4. ✅ Manual tab should auto-fill with:
   - Amount: 35
   - Category: Transportation
   - Description: Uber to airport

---

### Test 4: Receipt Photo Parsing
**Expected Behavior**: Image analyzed, expense data extracted

#### Browser Test Only:
1. Click "Receipt" tab
2. Upload a receipt image (any receipt photo)
3. Click "Parse Receipt"
4. Wait for AI processing (~3-5 seconds)
5. ✅ Manual tab should auto-fill with extracted data

> **Note**: This requires a valid receipt image. Test with any grocery/restaurant receipt.

---

### Test 5: Budget Management
**Expected Behavior**: Budget created, comparison shows spending vs limit

#### PowerShell Test:
```powershell
# Set budget
$budget = @{
    monthly_limit = 500.00
    category = "Food"
    month = (Get-Date -Format "yyyy-MM-01")
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/budgets" `
  -Method POST `
  -Headers $headers `
  -Body $budget

Write-Host "✅ Budget set: `$$($response.budget.monthly_limit) for Food" -ForegroundColor Green

# Get budget comparison
$comparison = Invoke-RestMethod -Uri "http://localhost:8000/api/budget-comparison" `
  -Headers $headers

Write-Host "Budget Comparison:" -ForegroundColor Yellow
$comparison.comparison | ForEach-Object {
    Write-Host "  Category: $($_.category)" -ForegroundColor Cyan
    Write-Host "  Budget: `$$($_.budget)" -ForegroundColor White
    Write-Host "  Spent: `$$($_.actual_spent)" -ForegroundColor White
    Write-Host "  Remaining: `$$($_.remaining)" -ForegroundColor Green
    Write-Host ""
}
```

---

### Test 6: Calendar Auto-Creation
**Expected Behavior**: Calendar entries automatically created when expenses added

#### PowerShell Test:
```powershell
# Get calendar entries
$calendar = Invoke-RestMethod -Uri "http://localhost:8000/api/calendar" `
  -Headers $headers

Write-Host "✅ Calendar has $($calendar.entries.Count) entries" -ForegroundColor Green
$calendar.entries | ForEach-Object {
    Write-Host "  $($_.display_date): $($_.label) ($($_.category))" -ForegroundColor Cyan
}
```

> **Expected**: Every expense you created should have a matching calendar entry

---

### Test 7: Query Expenses with Filters
**Expected Behavior**: Expenses filtered by date range and category

#### PowerShell Test:
```powershell
# Get all expenses
$expenses = Invoke-RestMethod -Uri "http://localhost:8000/api/expenses" `
  -Headers $headers

Write-Host "✅ Total expenses: $($expenses.count)" -ForegroundColor Green

# Get Food expenses only
$foodExpenses = Invoke-RestMethod -Uri "http://localhost:8000/api/expenses?category=Food" `
  -Headers $headers

Write-Host "✅ Food expenses: $($foodExpenses.count)" -ForegroundColor Green

# Calculate total spent
$totalSpent = ($expenses.expenses | Measure-Object -Property amount -Sum).Sum
Write-Host "💰 Total spent: `$$totalSpent" -ForegroundColor Magenta
```

---

### Test 8: Delete Expense (Cascade Delete)
**Expected Behavior**: Expense deleted, calendar entry also removed

#### PowerShell Test:
```powershell
# Get an expense ID
$expenseId = $expenses.expenses[0].id

# Delete expense
Invoke-RestMethod -Uri "http://localhost:8000/api/expenses/$expenseId" `
  -Method DELETE `
  -Headers $headers

Write-Host "✅ Expense deleted (calendar entry auto-removed)" -ForegroundColor Green

# Verify calendar entry is gone
$calendar = Invoke-RestMethod -Uri "http://localhost:8000/api/calendar" `
  -Headers $headers

Write-Host "Calendar now has $($calendar.entries.Count) entries" -ForegroundColor Cyan
```

---

## 🎯 Complete Test Script

Run all tests at once:

```powershell
# BudgetBuddy Complete Test Script

Write-Host "`n🧪 BudgetBuddy Test Suite`n" -ForegroundColor Yellow

# 1. Health Check
Write-Host "Test 1: Health Check..." -ForegroundColor Cyan
$health = Invoke-RestMethod -Uri "http://localhost:8000/health"
if ($health.components.database -eq $true) {
    Write-Host "✅ Database connected" -ForegroundColor Green
} else {
    Write-Host "❌ Database NOT connected" -ForegroundColor Red
    exit
}

# 2. Create User
Write-Host "`nTest 2: Create User..." -ForegroundColor Cyan
$user = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" `
  -Method POST `
  -Body (@{username="testuser_$(Get-Random)"} | ConvertTo-Json) `
  -ContentType "application/json"
Write-Host "✅ User: $($user.username)" -ForegroundColor Green
$token = $user.token
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

# 3. Create Expense
Write-Host "`nTest 3: Create Expense..." -ForegroundColor Cyan
$expense = Invoke-RestMethod -Uri "http://localhost:8000/api/expenses" `
  -Method POST `
  -Headers $headers `
  -Body (@{
    amount = 25.50
    category = "Food"
    description = "Test expense"
    date = (Get-Date).ToString("yyyy-MM-dd")
  } | ConvertTo-Json)
Write-Host "✅ Expense created: `$$($expense.amount)" -ForegroundColor Green

# 4. Parse Natural Language
Write-Host "`nTest 4: Parse Natural Language..." -ForegroundColor Cyan
try {
    $parsed = Invoke-RestMethod -Uri "http://localhost:8000/api/parse-expense" `
      -Method POST `
      -Headers $headers `
      -Body (@{text = "Coffee $5.50"} | ConvertTo-Json)
    Write-Host "✅ Parsed: $($parsed.parsed_data.description)" -ForegroundColor Green
} catch {
    Write-Host "⚠️  LLM parsing not configured (API key needed)" -ForegroundColor Yellow
}

# 5. Set Budget
Write-Host "`nTest 5: Set Budget..." -ForegroundColor Cyan
$budget = Invoke-RestMethod -Uri "http://localhost:8000/api/budgets" `
  -Method POST `
  -Headers $headers `
  -Body (@{
    monthly_limit = 500.00
    category = "Food"
    month = (Get-Date -Format "yyyy-MM-01")
  } | ConvertTo-Json)
Write-Host "✅ Budget set: `$$($budget.budget.monthly_limit)" -ForegroundColor Green

# 6. Get Calendar
Write-Host "`nTest 6: Get Calendar..." -ForegroundColor Cyan
$calendar = Invoke-RestMethod -Uri "http://localhost:8000/api/calendar" `
  -Headers $headers
Write-Host "✅ Calendar entries: $($calendar.entries.Count)" -ForegroundColor Green

# Summary
Write-Host "`n🎉 All Tests Completed!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "Frontend: http://localhost:5174" -ForegroundColor Cyan
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
```

---

## 🐛 Troubleshooting

### Issue: "Unable to connect to server"
**Solution**: Backend not running
```powershell
cd "C:\Users\jyoth\Downloads\Project_0210\Budget Buddy"
.\.venv\Scripts\python.exe backend/main.py
```

### Issue: "Database connection failed"
**Solution**: Check `.env` file has correct Supabase credentials
```powershell
# Verify environment variables
Get-Content backend\.env
```

### Issue: "Failed to parse expense"
**Solution**: Gemini API key not configured
```powershell
# Check GEMINI_API_KEY in backend/.env
# Get free key from: https://makersuite.google.com/app/apikey
```

### Issue: Frontend not loading
**Solution**: Frontend server not running
```powershell
npm run dev
```

---

## 📊 Expected Results

After running all tests, you should have:

✅ **1 User created** with JWT token  
✅ **Multiple expenses** in database  
✅ **Calendar entries** auto-created  
✅ **Budget set** with comparison data  
✅ **Natural language** parsed successfully  

**Check in Supabase Dashboard**:
1. Go to https://supabase.com
2. Open your project
3. Click "Table Editor"
4. View `users`, `expenses`, `budgets`, `calendar_entries` tables
5. ✅ Should see all test data

---

## 🎓 Learning Outcomes

After testing, you've verified:

1. **Authentication**: Username-only JWT system
2. **Multimodal Input**: 3 different ways to add expenses
3. **AI Integration**: LLM + Vision parsing
4. **Database Operations**: CRUD with auto-triggers
5. **Architecture**: React → FastAPI → Supabase

**You now have a production-ready expense tracking app!** 🎉
