-- ============================================================
-- BudgetBuddy Unified Schema (Supabase PostgreSQL)
-- ============================================================
-- This file combines:
--   - Core table schema
--   - Monthly budget summary migration
--   - Triggers/functions/views
--   - Current working RLS behavior used by backend writes
--
-- Run this file in Supabase SQL Editor.
-- ============================================================

BEGIN;

-- ------------------------------------------------------------
-- STEP 0: Extension
-- ------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ------------------------------------------------------------
-- STEP 1: Drop views
-- ------------------------------------------------------------
DROP VIEW IF EXISTS budget_comparison;
DROP VIEW IF EXISTS monthly_spending_summary;

-- ------------------------------------------------------------
-- STEP 2: Drop triggers
-- ------------------------------------------------------------
DROP TRIGGER IF EXISTS trigger_mbs_expense_update ON expenses;
DROP TRIGGER IF EXISTS trigger_mbs_expense_delete ON expenses;
DROP TRIGGER IF EXISTS trigger_mbs_expense_insert ON expenses;
DROP TRIGGER IF EXISTS trigger_mbs_updated_at ON monthly_budget_summary;
DROP TRIGGER IF EXISTS trigger_create_calendar_entry ON expenses;
DROP TRIGGER IF EXISTS trigger_budgets_updated_at ON budgets;
DROP TRIGGER IF EXISTS trigger_expenses_updated_at ON expenses;

-- ------------------------------------------------------------
-- STEP 3: Drop functions
-- ------------------------------------------------------------
DROP FUNCTION IF EXISTS mbs_on_expense_update();
DROP FUNCTION IF EXISTS mbs_on_expense_delete();
DROP FUNCTION IF EXISTS mbs_on_expense_insert();
DROP FUNCTION IF EXISTS create_calendar_entry();
DROP FUNCTION IF EXISTS update_updated_at_column();
DROP FUNCTION IF EXISTS cleanup_expired_cache();

-- ------------------------------------------------------------
-- STEP 4: Drop tables
-- ------------------------------------------------------------
DROP TABLE IF EXISTS monthly_budget_summary CASCADE;
DROP TABLE IF EXISTS calendar_entries CASCADE;
DROP TABLE IF EXISTS budgets CASCADE;
DROP TABLE IF EXISTS expenses CASCADE;
DROP TABLE IF EXISTS chat_history CASCADE;
DROP TABLE IF EXISTS api_cache CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ------------------------------------------------------------
-- STEP 5: Recreate tables
-- ------------------------------------------------------------
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  username TEXT UNIQUE NOT NULL,
  display_name TEXT,
  selected_pet TEXT DEFAULT 'penguin' CHECK (selected_pet IN ('penguin', 'dragon', 'capybara', 'cat')),
  friendship_level INTEGER DEFAULT 1 CHECK (friendship_level BETWEEN 1 AND 10),
  last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  CONSTRAINT username_length CHECK (char_length(username) >= 3 AND char_length(username) <= 30)
);

CREATE TABLE expenses (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  amount DECIMAL(10, 2) NOT NULL CHECK (amount >= 0),
  category TEXT NOT NULL,
  description TEXT,
  expense_date DATE NOT NULL DEFAULT CURRENT_DATE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  metadata JSONB DEFAULT '{}',
  CONSTRAINT category_valid CHECK (category IN (
    'Food', 'Transportation', 'Entertainment', 'Shopping',
    'Bills', 'Healthcare', 'Education', 'Other'
  ))
);

CREATE TABLE budgets (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  monthly_limit DECIMAL(10, 2) NOT NULL CHECK (monthly_limit > 0),
  category TEXT,
  month DATE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  CONSTRAINT category_or_total CHECK (
    category IS NULL OR
    category IN ('Food', 'Transportation', 'Entertainment', 'Shopping', 'Bills', 'Healthcare', 'Education', 'Other')
  ),
  UNIQUE(user_id, month, category)
);

CREATE TABLE calendar_entries (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  expense_id UUID NOT NULL REFERENCES expenses(id) ON DELETE CASCADE,
  display_date DATE NOT NULL,
  label TEXT NOT NULL,
  category TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(expense_id)
);

CREATE TABLE chat_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  message TEXT NOT NULL,
  sender TEXT NOT NULL CHECK (sender IN ('user', 'assistant')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  metadata JSONB DEFAULT '{}'
);

CREATE TABLE api_cache (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  cache_key TEXT UNIQUE NOT NULL,
  cache_value JSONB NOT NULL,
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE monthly_budget_summary (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  month DATE NOT NULL,
  monthly_limit DECIMAL(10, 2) NOT NULL DEFAULT 2000.00 CHECK (monthly_limit > 0),
  total_spent DECIMAL(10, 2) NOT NULL DEFAULT 0.00 CHECK (total_spent >= 0),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, month)
);

-- ------------------------------------------------------------
-- STEP 6: Recreate indexes
-- ------------------------------------------------------------
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_last_activity ON users(last_activity);

CREATE INDEX idx_expenses_user_id ON expenses(user_id);
CREATE INDEX idx_expenses_date ON expenses(expense_date DESC);
CREATE INDEX idx_expenses_category ON expenses(category);
CREATE INDEX idx_expenses_user_date ON expenses(user_id, expense_date DESC);

CREATE INDEX idx_budgets_user_id ON budgets(user_id);
CREATE INDEX idx_budgets_month ON budgets(month DESC);
CREATE INDEX idx_budgets_user_month ON budgets(user_id, month DESC);

CREATE INDEX idx_calendar_user_id ON calendar_entries(user_id);
CREATE INDEX idx_calendar_date ON calendar_entries(display_date);
CREATE INDEX idx_calendar_user_date ON calendar_entries(user_id, display_date);

CREATE INDEX idx_chat_user_id ON chat_history(user_id);
CREATE INDEX idx_chat_created_at ON chat_history(created_at DESC);
CREATE INDEX idx_chat_user_recent ON chat_history(user_id, created_at DESC);

CREATE INDEX idx_api_cache_key ON api_cache(cache_key);
CREATE INDEX idx_api_cache_expires ON api_cache(expires_at);

CREATE INDEX idx_mbs_user_id ON monthly_budget_summary(user_id);
CREATE INDEX idx_mbs_month ON monthly_budget_summary(month DESC);
CREATE INDEX idx_mbs_user_month ON monthly_budget_summary(user_id, month DESC);

-- ------------------------------------------------------------
-- STEP 7: Recreate functions
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION create_calendar_entry()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO calendar_entries (user_id, expense_id, display_date, label, category)
    VALUES (
        NEW.user_id,
        NEW.id,
        NEW.expense_date,
        COALESCE(NEW.description, NEW.category),
        NEW.category
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION mbs_on_expense_insert()
RETURNS TRIGGER AS $$
DECLARE
    v_month DATE;
BEGIN
    v_month := DATE_TRUNC('month', NEW.expense_date)::DATE;

    INSERT INTO monthly_budget_summary (user_id, month, monthly_limit, total_spent)
    VALUES (NEW.user_id, v_month, 2000.00, NEW.amount)
    ON CONFLICT (user_id, month) DO UPDATE
        SET total_spent = monthly_budget_summary.total_spent + NEW.amount,
            updated_at = NOW();

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION mbs_on_expense_delete()
RETURNS TRIGGER AS $$
DECLARE
    v_month DATE;
BEGIN
    v_month := DATE_TRUNC('month', OLD.expense_date)::DATE;

    UPDATE monthly_budget_summary
       SET total_spent = GREATEST(0, total_spent - OLD.amount),
           updated_at = NOW()
     WHERE user_id = OLD.user_id
       AND month = v_month;

    RETURN OLD;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION mbs_on_expense_update()
RETURNS TRIGGER AS $$
DECLARE
    v_old_month DATE;
    v_new_month DATE;
BEGIN
    v_old_month := DATE_TRUNC('month', OLD.expense_date)::DATE;
    v_new_month := DATE_TRUNC('month', NEW.expense_date)::DATE;

    IF v_old_month = v_new_month THEN
        UPDATE monthly_budget_summary
           SET total_spent = GREATEST(0, total_spent + NEW.amount - OLD.amount),
               updated_at = NOW()
         WHERE user_id = NEW.user_id
           AND month = v_new_month;
    ELSE
        UPDATE monthly_budget_summary
           SET total_spent = GREATEST(0, total_spent - OLD.amount),
               updated_at = NOW()
         WHERE user_id = OLD.user_id
           AND month = v_old_month;

        INSERT INTO monthly_budget_summary (user_id, month, monthly_limit, total_spent)
        VALUES (NEW.user_id, v_new_month, 2000.00, NEW.amount)
        ON CONFLICT (user_id, month) DO UPDATE
            SET total_spent = monthly_budget_summary.total_spent + NEW.amount,
                updated_at = NOW();
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS void AS $$
BEGIN
    DELETE FROM api_cache WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------
-- STEP 8: Recreate triggers
-- ------------------------------------------------------------
CREATE TRIGGER trigger_expenses_updated_at
    BEFORE UPDATE ON expenses
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_budgets_updated_at
    BEFORE UPDATE ON budgets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_create_calendar_entry
    AFTER INSERT ON expenses
    FOR EACH ROW
    EXECUTE FUNCTION create_calendar_entry();

CREATE TRIGGER trigger_mbs_updated_at
    BEFORE UPDATE ON monthly_budget_summary
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_mbs_expense_insert
    AFTER INSERT ON expenses
    FOR EACH ROW
    EXECUTE FUNCTION mbs_on_expense_insert();

CREATE TRIGGER trigger_mbs_expense_delete
    AFTER DELETE ON expenses
    FOR EACH ROW
    EXECUTE FUNCTION mbs_on_expense_delete();

CREATE TRIGGER trigger_mbs_expense_update
    AFTER UPDATE ON expenses
    FOR EACH ROW
    EXECUTE FUNCTION mbs_on_expense_update();

-- ------------------------------------------------------------
-- STEP 9: Recreate views
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW monthly_spending_summary AS
SELECT
    user_id,
    DATE_TRUNC('month', expense_date) AS month,
    category,
    SUM(amount) AS total_amount,
    COUNT(*) AS transaction_count,
    AVG(amount) AS avg_amount
FROM expenses
GROUP BY user_id, DATE_TRUNC('month', expense_date), category;

CREATE OR REPLACE VIEW budget_comparison AS
SELECT
    b.user_id,
    b.month,
    b.category,
    b.monthly_limit AS budget,
    COALESCE(SUM(e.amount), 0) AS actual_spent,
    b.monthly_limit - COALESCE(SUM(e.amount), 0) AS remaining,
    CASE
        WHEN COALESCE(SUM(e.amount), 0) > b.monthly_limit THEN 'over'
        WHEN COALESCE(SUM(e.amount), 0) > b.monthly_limit * 0.8 THEN 'warning'
        ELSE 'safe'
    END AS status
FROM budgets b
LEFT JOIN expenses e ON
    b.user_id = e.user_id
    AND b.category = e.category
    AND DATE_TRUNC('month', e.expense_date) = b.month
GROUP BY b.user_id, b.month, b.category, b.monthly_limit;

-- ------------------------------------------------------------
-- STEP 10: RLS mode used by this app
-- ------------------------------------------------------------
-- NOTE:
-- Backend writes currently rely on application-level auth checks.
-- RLS is disabled on user-scoped tables to match the working setup.

ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE expenses DISABLE ROW LEVEL SECURITY;
ALTER TABLE budgets DISABLE ROW LEVEL SECURITY;
ALTER TABLE calendar_entries DISABLE ROW LEVEL SECURITY;
ALTER TABLE chat_history DISABLE ROW LEVEL SECURITY;
ALTER TABLE monthly_budget_summary DISABLE ROW LEVEL SECURITY;

-- Optional: keep cache table unrestricted as it is not user-scoped
ALTER TABLE api_cache DISABLE ROW LEVEL SECURITY;

COMMIT;

-- ============================================================
-- DONE
-- Database schema is fully recreated in one file.
-- ============================================================
