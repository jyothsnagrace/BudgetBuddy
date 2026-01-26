"""
BudgetBuddy - Personal Finance Management Application
A comprehensive Streamlit app for tracking income, expenses, and financial planning.
"""

import streamlit as st
import json
import requests
import pandas as pd
import altair as alt
from app.schemas import UserFinanceInput
from lib.functions import page_config
from streamlit_option_menu import option_menu

# ============================================================================
# CONFIGURATION & INITIALIZATION
# ============================================================================

API_BASE = st.secrets.get("api_base", "http://127.0.0.1:8000")

# Page config
page_config()

# Load CSS styling
with open('lib/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load sample data
@st.cache_data
def load_sample_data():
    try:
        with open("data/sample_user.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

sample = load_sample_data()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def auto_generate_user_id(full_name: str) -> str:
    """Auto-generate user ID from full name (firstname_lastname)."""
    if not full_name:
        return "user_001"
    name_parts = full_name.strip().split()
    if len(name_parts) >= 2:
        return f"{name_parts[0].lower()}_{name_parts[-1].lower()}"
    return name_parts[0].lower()

def calculate_totals():
    """Calculate total income, expenses, and remaining balance."""
    total_income = sum([i["amount"] for i in st.session_state.incomes]) if "incomes" in st.session_state else 0
    total_expenses = sum([e["amount"] for e in st.session_state.expenses]) if "expenses" in st.session_state else 0
    return total_income, total_expenses, total_income - total_expenses

def display_metric_row(col1_label, col1_value, col2_label, col2_value, col3_label, col3_value):
    """Display three metrics in a row."""
    col1, col2, col3 = st.columns(3)
    col1.metric(col1_label, col1_value)
    col2.metric(col2_label, col2_value)
    col3.metric(col3_label, col3_value)

def display_metric_row_4(col1_label, col1_value, col2_label, col2_value, col3_label, col3_value, col4_label, col4_value):
    """Display four metrics in a row."""
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(col1_label, col1_value)
    col2.metric(col2_label, col2_value)
    col3.metric(col3_label, col3_value)
    col4.metric(col4_label, col4_value)

def submit_data(user_id, user_name, incomes, expenses, savings_goal):
    """Submit data to backend API with confirmation."""
    if not user_name.strip():
        st.error("❌ Please enter your name before submitting data.")
        return
    
    if not incomes or not expenses:
        st.warning("⚠️ Please add at least one income source and one expense before submitting.")
        return
    
    # Show confirmation dialog
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 Submit", type="primary", use_container_width=True):
            with st.spinner("📤 Submitting your data..."):
                payload = {
                    "user_id": user_id,
                    "name": user_name,
                    "incomes": incomes,
                    "expenses": expenses,
                    "savings_goal": savings_goal
                }
                try:
                    r = requests.post(f"{API_BASE}/ingest", json=payload, timeout=30)
                    if r.status_code == 200:
                        st.balloons()
                        st.success("✅ **Data Submitted Successfully!**")
                        st.info(f"""
                        **Submission Details:**
                        - **User:** {user_name} ({user_id})
                        - **Total Income:** ${sum([i['amount'] for i in incomes]):,.2f}
                        - **Total Expenses:** ${sum([e['amount'] for e in expenses]):,.2f}
                        - **Savings Goal:** ${savings_goal:,.2f}
                        
                        View your analysis on the **Data Analysis** page.
                        """)
                        st.session_state.data_submitted = True
                    else:
                        st.error(f"❌ Submission failed: {r.text}")
                except requests.exceptions.Timeout:
                    st.error("❌ **Request Timeout**: Backend API is taking too long to respond. Please try again or check if the server is under heavy load.")
                except requests.exceptions.ConnectionError:
                    st.error(f"❌ **Connection Error**: Could not connect to backend at {API_BASE}. Please ensure the server is running.")
                except Exception as e:
                    st.error(f"❌ **Error**: {str(e)}")
    
    with col2:
        if st.button("❌ Cancel"):
            st.info("Submission cancelled.")

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

with st.sidebar:
    page = option_menu(
        menu_title="📍 Navigation",
        options=["📊 Home", "📈 Data Analysis", "💡 Summary Dashboard"],
        default_index=0,
    )
    
    st.markdown("---")
    st.markdown("### 💡 About BudgetBuddy")
    st.info("""
    **BudgetBuddy** helps you:
    - 📊 Track income & expenses
    - 📈 Analyze spending patterns
    - 💰 Plan savings goals
    - 🎯 Create financial action plans
    """)

# ============================================================================
# PAGE 1: HOME - User Input and Financial Tracking
# ============================================================================

if page == "📊 Home":
    st.markdown("### 💼 Personal Finance Dashboard")
    st.markdown("Add your income and expenses, then track them in a table.")
    
    # User Information Section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 User Information")
        user_name = st.text_input(
            "Your Name",
            value=(sample.get("name", "") if sample else ""),
            help="Enter your full name (used to auto-generate User ID)"
        )
        user_id = auto_generate_user_id(user_name)
        st.text_input("User ID", value=user_id, disabled=True, help="Auto-generated from your name")
        # Store in session state for use on other pages
        st.session_state.user_id = user_id
        st.session_state.user_name = user_name
    
    with col2:
        st.subheader("🎯 Financial Goal")
        savings_goal = st.number_input(
            "Savings Goal ($)",
            value=float(sample["savings_goal"] if sample and sample.get("savings_goal") else 5000),
            min_value=100.0,
            step=500.0,
            help="Your target savings amount"
        )
    
    st.markdown("---")
    
    # Income Section
    st.subheader("💵 Income Sources")
    income_col1, income_col2, income_btn = st.columns([2, 2, 1])
    
    with income_col1:
        income_source = st.text_input("Income Source", value="Salary", placeholder="e.g., Job A, Freelance")
    with income_col2:
        income_amount = st.number_input("Amount ($)", value=4500.0, min_value=0.0, step=100.0)
    with income_btn:
        st.write("")  # Align button
        if st.button("➕ Add", key="add_income"):
            if "incomes" not in st.session_state:
                st.session_state.incomes = []
            if income_source.strip() and income_amount > 0:
                st.session_state.incomes.append({"source": income_source, "amount": income_amount})
                st.success(f"✅ Added {income_source}: ${income_amount:,.2f}")
            else:
                st.error("Please enter valid income details.")
    
    # Display Income List
    if "incomes" in st.session_state and st.session_state.incomes:
        st.subheader("📋 Income List")
        for idx, income in enumerate(st.session_state.incomes):
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            with col1:
                st.write(f"**{income['source']}**")
            with col2:
                st.write(f"${income['amount']:,.2f}")
            with col3:
                if st.button("✏️", key=f"edit_income_{idx}", help="Edit"):
                    st.session_state[f"edit_income_{idx}"] = True
            with col4:
                if st.button("🗑️", key=f"delete_income_{idx}", help="Delete"):
                    st.session_state.incomes.pop(idx)
                    st.rerun()
            
            # Edit Mode
            if st.session_state.get(f"edit_income_{idx}"):
                col1, col2 = st.columns(2)
                with col1:
                    new_source = st.text_input("Source", value=income['source'], key=f"edit_source_{idx}")
                with col2:
                    new_amount = st.number_input("Amount", value=income['amount'], key=f"edit_amount_{idx}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Save", key=f"save_income_{idx}"):
                        st.session_state.incomes[idx] = {"source": new_source, "amount": new_amount}
                        st.session_state[f"edit_income_{idx}"] = False
                        st.rerun()
                with col2:
                    if st.button("❌ Cancel", key=f"cancel_income_{idx}"):
                        st.session_state[f"edit_income_{idx}"] = False
                        st.rerun()
    
    st.markdown("---")
    
    # Expense Section
    st.subheader("💸 Expenses")
    exp_col1, exp_col2, exp_col3, exp_btn = st.columns([2, 1.5, 1.5, 0.8])
    
    with exp_col1:
        expense_name = st.text_input("Expense Name", value="Rent", placeholder="e.g., Groceries")
    with exp_col2:
        expense_amount = st.number_input("Amount ($)", value=1500.0, min_value=0.0, step=100.0, key="expense_amount")
    with exp_col3:
        expense_category = st.selectbox("Category", ["Housing", "Food", "Transportation", "Entertainment", "Utilities", "Other"])
    with exp_btn:
        st.write("")  # Align button
        if st.button("➕", key="add_expense", help="Add"):
            if "expenses" not in st.session_state:
                st.session_state.expenses = []
            if expense_name.strip() and expense_amount > 0:
                st.session_state.expenses.append({
                    "name": expense_name,
                    "amount": expense_amount,
                    "category": expense_category
                })
                st.success(f"✅ Added {expense_name}: ${expense_amount:,.2f}")
            else:
                st.error("Please enter valid expense details.")
    
    # Display Expense List
    if "expenses" in st.session_state and st.session_state.expenses:
        st.subheader("📋 Expense List")
        for idx, expense in enumerate(st.session_state.expenses):
            col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1.5, 0.7, 0.7])
            with col1:
                st.write(f"**{expense['name']}**")
            with col2:
                st.write(f"${expense['amount']:,.2f}")
            with col3:
                st.write(f"*{expense['category']}*")
            with col4:
                if st.button("✏️", key=f"edit_expense_{idx}", help="Edit"):
                    st.session_state[f"edit_expense_{idx}"] = True
            with col5:
                if st.button("🗑️", key=f"delete_expense_{idx}", help="Delete"):
                    st.session_state.expenses.pop(idx)
                    st.rerun()
            
            # Edit Mode
            if st.session_state.get(f"edit_expense_{idx}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    new_name = st.text_input("Name", value=expense['name'], key=f"edit_name_{idx}")
                with col2:
                    new_amount = st.number_input("Amount", value=expense['amount'], key=f"edit_exp_amount_{idx}")
                with col3:
                    new_category = st.selectbox("Category", ["Housing", "Food", "Transportation", "Entertainment", "Utilities", "Other"], 
                                               index=["Housing", "Food", "Transportation", "Entertainment", "Utilities", "Other"].index(expense['category']), 
                                               key=f"edit_category_{idx}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Save", key=f"save_expense_{idx}"):
                        st.session_state.expenses[idx] = {"name": new_name, "amount": new_amount, "category": new_category}
                        st.session_state[f"edit_expense_{idx}"] = False
                        st.rerun()
                with col2:
                    if st.button("❌ Cancel", key=f"cancel_expense_{idx}"):
                        st.session_state[f"edit_expense_{idx}"] = False
                        st.rerun()
        
        # Summary & Submission
        st.markdown("---")
        st.subheader("💰 Financial Summary")
        
        total_income, total_expenses, remaining = calculate_totals()
        display_metric_row(
            "Total Income", f"${total_income:,.2f}",
            "Total Expenses", f"${total_expenses:,.2f}",
            "Remaining", f"${remaining:,.2f}"
        )
        
        st.markdown("---")
        st.subheader("📤 Submit Your Data")
        st.info("Review your information above, then click the button to submit your financial data.")
        
        submit_data(user_id, user_name, st.session_state.incomes, st.session_state.expenses, savings_goal)

# ============================================================================
# PAGE 2: DATA ANALYSIS - Charts and Budget Plan
# ============================================================================

elif page == "📈 Data Analysis":
    st.title("📈 Expense Analysis & Financial Projections")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        user_id = st.text_input(
            "User ID",
            value=st.session_state.get("user_id", sample["user_id"] if sample else ""),
            help="Auto-populated from Home page",
            disabled=True
        )
    with col2:
        months = st.slider("Projection Period (months)", min_value=1, max_value=60, value=6)
    
    if st.button("📊 Generate Analysis", type="primary", use_container_width=True):
        total_income, total_expenses, monthly_savings = calculate_totals()
        
        if total_income == 0 and total_expenses == 0:
            st.warning("⚠️ Please add income and expenses on the Home page first.")
        else:
            savings_goal = 5000
            months_to_goal = savings_goal / monthly_savings if monthly_savings > 0 else float('inf')
            
            # Expense Breakdown
            if "expenses" in st.session_state and st.session_state.expenses:
                st.subheader("💸 Expense Breakdown by Category")
                expenses_df = pd.DataFrame(st.session_state.expenses)
                category_totals = expenses_df.groupby("category")["amount"].sum().reset_index().sort_values("amount", ascending=False)
                
                col1, col2 = st.columns(2)
                with col1:
                    pie_chart = alt.Chart(category_totals).mark_arc().encode(
                        theta="amount:Q",
                        color="category:N",
                        tooltip=["category:N", "amount:Q"]
                    ).properties(height=350)
                    st.altair_chart(pie_chart, use_container_width=True)
                
                with col2:
                    st.markdown("**Spending by Category:**")
                    for _, row in category_totals.iterrows():
                        pct = (row['amount'] / total_expenses * 100) if total_expenses > 0 else 0
                        st.write(f"📌 **{row['category']}**: ${row['amount']:,.2f} ({pct:.1f}%)")
            
            st.markdown("---")
            
            # Saving Strategies
            st.subheader("💡 Personalized Saving Strategies")
            strat_col1, strat_col2 = st.columns(2)
            
            with strat_col1:
                with st.container(border=True):
                    st.markdown("### 📈 Aggressive Strategy")
                    target_aggressive = total_income * 0.25
                    months_aggressive = savings_goal / target_aggressive if target_aggressive > 0 else float('inf')
                    st.write(f"**Target:** ${target_aggressive:,.2f}/month")
                    st.write(f"**Timeline:** {months_aggressive:.1f} months to goal")
                    st.write("**Focus:** Cut entertainment & utilities, minimize subscriptions")
            
            with strat_col2:
                with st.container(border=True):
                    st.markdown("### 🎯 Balanced Strategy")
                    target_balanced = total_income * 0.15
                    months_balanced = savings_goal / target_balanced if target_balanced > 0 else float('inf')
                    st.write(f"**Target:** ${target_balanced:,.2f}/month")
                    st.write(f"**Timeline:** {months_balanced:.1f} months to goal")
                    st.write("**Focus:** Reduce subscriptions, moderate spending cuts")
            
            st.markdown("---")
            
            # Financial Projections
            st.subheader("🔮 Financial Projections")
            
            projection_data = []
            cumulative_savings = 0
            
            for month in range(1, months + 1):
                cumulative_savings += monthly_savings
                projection_data.append({
                    "Month": month,
                    "Cumulative Savings": cumulative_savings,
                })
            
            proj_df = pd.DataFrame(projection_data)
            
            col1, col2 = st.columns(2)
            with col1:
                if not proj_df.empty:
                    proj_chart = alt.Chart(proj_df).mark_line(point=True, size=3, color="#1f77b4").encode(
                        x=alt.X('Month:O', title='Month'),
                        y=alt.Y('Cumulative Savings:Q', title='Cumulative Savings ($)'),
                        tooltip=['Month', 'Cumulative Savings']
                    ).properties(height=300, title="Cumulative Savings Over Time")
                    st.altair_chart(proj_chart, use_container_width=True)
            
            with col2:
                st.markdown("### 📊 Key Metrics")
                display_metric_row_4(
                    "Monthly Surplus", f"${monthly_savings:,.2f}",
                    f"Total ({months}m)", f"${cumulative_savings:,.2f}",
                    "To Goal", f"{months_to_goal:.1f}m" if months_to_goal != float('inf') else "∞",
                    "Progress", f"{min(100, (cumulative_savings/savings_goal*100)):.1f}%"
                )
            
            st.markdown("---")
            
            # Expense Reduction Opportunities
            if "expenses" in st.session_state and st.session_state.expenses and not category_totals.empty:
                st.subheader("📋 Expense Reduction Opportunities")
                st.markdown("*Potential 15% reduction targets by category:*")
                
                high_expense_categories = category_totals.nlargest(3, 'amount')
                for idx, (_, row) in enumerate(high_expense_categories.iterrows()):
                    potential_savings = row['amount'] * 0.15
                    new_target = row['amount'] - potential_savings
                    
                    with st.container(border=True):
                        col1, col2, col3 = st.columns(3)
                        col1.metric(f"{row['category']}", f"${row['amount']:,.2f}")
                        col2.metric("Target", f"${new_target:,.2f}")
                        col3.metric("Potential Savings", f"${potential_savings:,.2f}")

# ============================================================================
# PAGE 3: SUMMARY - Creative Summary, Action Plan, and Tips
# ============================================================================

elif page == "💡 Summary Dashboard":
    st.title("📊 Financial Insights & Planning")
    
    # User Inputs
    col1, col2, col3 = st.columns(3)
    with col1:
        user_id = st.text_input(
            "User ID",
            value=st.session_state.get("user_id", sample["user_id"] if sample else ""),
            help="Auto-populated from Home page",
            disabled=True
        )
    with col2:
        name = st.text_input(
            "Your Name",
            value=st.session_state.get("user_name", sample.get("name", "") if sample else ""),
            help="Auto-populated from Home page",
            disabled=True
        )
    with col3:
        months = st.number_input("Planning Horizon (months)", min_value=1, max_value=24, value=12)
    
    # Calculate metrics
    total_income, total_expenses, monthly_savings = calculate_totals()
    savings_goal = 5000
    progress_pct = min(100, (monthly_savings * 6 / savings_goal * 100)) if savings_goal > 0 else 0
    
    # Display Key Metrics
    st.subheader("🎯 Financial Overview")
    display_metric_row_4(
        "Monthly Income", f"${total_income:,.2f}",
        "Monthly Expenses", f"${total_expenses:,.2f}",
        "Monthly Savings", f"${monthly_savings:,.2f}",
        "Progress to Goal", f"{progress_pct:.0f}%"
    )
    
    st.markdown("---")
    
    # Tabbed Interface
    tab1, tab2, tab3 = st.tabs(["📝 Creative Summary", "📋 Action Plan", "💡 Financial Tips"])
    
    with tab1:
        st.header("Your Financial Story")
        if st.button("✨ Generate Creative Summary", type="primary", use_container_width=True):
            if not user_id or not name:
                st.error("❌ Please enter your name and user ID.")
            else:
                with st.spinner("✨ Generating your creative summary..."):
                    req = {
                        "user_id": user_id,
                        "name": name,
                        "total_income": total_income,
                        "total_expenses": total_expenses,
                        "savings": monthly_savings,
                        "goal": savings_goal
                    }
                    try:
                        r = requests.post(f"{API_BASE}/creative", json=req, timeout=30)
                        if r.status_code == 200:
                            result = r.json()
                            creative_text = result.get("creative_summary", "")
                            if creative_text:
                                st.markdown("### ✨ Your Financial Journey")
                                st.write(creative_text)
                            else:
                                st.warning("No summary generated. Showing default...")
                                st.success(f"""
                                ### ✨ Your Financial Journey
                                
                                Dear **{name}**,
                                
                                Your financial awareness demonstrates discipline and forward-thinking. 
                                With **${monthly_savings:,.2f}** saved monthly, you're building a strong foundation.
                                
                                **Annual Projection:** ${monthly_savings * 12:,.2f} will bring you closer to financial freedom.
                                
                                Keep tracking, stay focused, and celebrate your progress! 🚀
                                """)
                        else:
                            st.warning(f"⚠️ LLM service returned error. Showing default summary...")
                            st.success(f"""
                            ### ✨ Your Financial Journey
                            
                            Dear **{name}**,
                            
                            Your financial awareness demonstrates discipline and forward-thinking. 
                            With **${monthly_savings:,.2f}** saved monthly, you're building a strong foundation.
                            
                            **Annual Projection:** ${monthly_savings * 12:,.2f} will bring you closer to financial freedom.
                            
                            Keep tracking, stay focused, and celebrate your progress! 🚀
                            """)
                    except requests.exceptions.Timeout:
                        st.error("❌ **Timeout**: Creative summary generation took too long. Showing default summary...")
                        st.success(f"""
                        ### ✨ Your Financial Journey
                        
                        Dear **{name}**,
                        
                        You're on a solid financial path with **${monthly_savings:,.2f}** saved monthly.
                        Keep up the excellent work toward your goals! 💪
                        """)
                    except requests.exceptions.ConnectionError:
                        st.error(f"❌ **Connection Error**: Could not reach LLM service at {API_BASE}. Showing default summary...")
                        st.success(f"""
                        ### ✨ Your Financial Journey
                        
                        Dear **{name}**,
                        
                        You're on a solid financial path with **${monthly_savings:,.2f}** saved monthly.
                        Keep up the excellent work toward your goals! 💪
                        """)
                    except Exception as e:
                        st.error(f"❌ **Error**: {str(e)}")
                        st.success(f"""
                        ### ✨ Your Financial Journey
                        
                        Dear **{name}**,
                        
                        You're on a solid financial path with **${monthly_savings:,.2f}** saved monthly.
                        Keep up the excellent work toward your goals! 💪
                        """)
    
    with tab2:
        st.header("12-Month Action Plan")
        
        with st.expander("🏗️ Phase 1: Foundation (Months 1-3)", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Goals:**")
                st.write(f"• Emergency fund: ${total_income * 0.5:,.2f}")
                st.write("• Weekly expense tracking")
                st.write("• Identify top 3 categories")
            with col2:
                st.markdown("**Actions:**")
                st.write("1. Open high-yield savings")
                st.write("2. Automate tracking")
                st.write("3. Reduce subscriptions by 10%")
            st.info(f"**Target Savings:** ${monthly_savings * 3:,.2f}")
        
        with st.expander("⚡ Phase 2: Acceleration (Months 4-6)"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Goals:**")
                st.write("• 3-month emergency fund")
                st.write("• Reduce expenses by 15%")
                st.write("• Full savings automation")
            with col2:
                st.markdown("**Actions:**")
                st.write(f"1. Increase savings to ${monthly_savings * 0.8:,.2f}")
                st.write("2. Renegotiate bills")
                st.write("3. Implement 50/30/20 rule")
            st.info(f"**Target Savings:** ${monthly_savings * 3:,.2f}")
        
        with st.expander("🚀 Phase 3: Investment (Months 7-12)"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Goals:**")
                st.write("• 6-month emergency fund")
                st.write("• Invest 10% of income")
                st.write("• Achieve savings goal")
            with col2:
                st.markdown("**Actions:**")
                st.write(f"1. Open investment account")
                st.write(f"2. Invest ${total_income * 0.10:,.2f}/month")
                st.write("3. Plan next milestone")
            st.info(f"**Target Savings:** ${monthly_savings * 6:,.2f}")
    
    with tab3:
        st.header("💡 Essential Financial Tips")
        
        tips = [
            ("🎯 The 50/30/20 Rule", "Allocate 50% to needs, 30% to wants, 20% to savings/debt"),
            ("💰 Emergency Fund", "Build 3-6 months of expenses before aggressive investing"),
            ("📊 Track Everything", "Monitor spending to identify patterns and opportunities"),
            ("🏦 Automate Savings", "Auto-transfer on payday removes temptation"),
            ("💳 Debt First", "Eliminate high-interest debt before investing"),
            ("📈 Invest Early", "Compound interest is powerful; start ASAP"),
            ("🛍️ Avoid Lifestyle Creep", "Keep spending stable as income grows"),
            ("🎓 Financial Education", "Continuously learn about investing & taxes"),
            ("💬 Get Professional Help", "Consider a financial advisor for major decisions"),
            ("🔄 Review Annually", "Reassess goals and strategies yearly"),
        ]
        
        col1, col2 = st.columns(2)
        for idx, (tip_title, tip_text) in enumerate(tips):
            with col1 if idx % 2 == 0 else col2:
                st.info(f"**{tip_title}**\n\n{tip_text}")


