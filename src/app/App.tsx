import { useState, useEffect } from "react";
import { Sparkles } from "lucide-react";
import { BudgetSummary } from "./components/BudgetSummary";
import { SpendingForm } from "./components/SpendingForm";
import { ExpenseList } from "./components/ExpenseList";
import { BudgetBuddy } from "./components/BudgetBuddy";
import { BudgetSettings } from "./components/BudgetSettings";
import { SpendingGraph } from "./components/SpendingGraph";
import { SpendingCalendar } from "./components/SpendingCalendar";
import { CompanionSelector } from "./components/CompanionSelector";
import { updateLastActivity } from "./components/FriendshipStatus";
import snowyBackground from "figma:asset/24c342c9b907dd7af46c17a7505a42b4711e2299.png";
import dragonBackground from "figma:asset/37fa4f83743a018706213713ff43d568f0c96eaf.png";
import capybaraBackground from "figma:asset/d21921f8a15a74720c7407c80f0c3278886fcea6.png";
import catBackground from "figma:asset/a0e9233cd7bfbcb758aa16b4bb7865d422456acf.png";

interface Expense {
  id: string;
  amount: number;
  category: string;
  description: string;
  date: string;
}

export default function App() {
  const [budget, setBudget] = useState(() => {
    const saved = localStorage.getItem("budget");
    return saved ? parseFloat(saved) : 2000;
  });

  const [expenses, setExpenses] = useState<Expense[]>(() => {
    const saved = localStorage.getItem("expenses");
    return saved ? JSON.parse(saved) : [];
  });

  const [selectedPet, setSelectedPet] = useState<'penguin' | 'dragon' | 'capybara' | 'cat'>(() => {
    const saved = localStorage.getItem('selectedPet');
    return (saved as 'penguin' | 'dragon' | 'capybara' | 'cat') || 'penguin';
  });

  // Update activity on app load
  useEffect(() => {
    updateLastActivity();
  }, []);

  // Listen for pet changes from localStorage
  useEffect(() => {
    const handleStorageChange = () => {
      const saved = localStorage.getItem('selectedPet');
      setSelectedPet((saved as 'penguin' | 'dragon' | 'capybara' | 'cat') || 'penguin');
    };
    
    window.addEventListener('storage', handleStorageChange);
    
    // Also check periodically for same-tab changes
    const interval = setInterval(() => {
      const saved = localStorage.getItem('selectedPet');
      const currentPet = (saved as 'penguin' | 'dragon' | 'capybara' | 'cat') || 'penguin';
      if (currentPet !== selectedPet) {
        setSelectedPet(currentPet);
      }
    }, 100);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      clearInterval(interval);
    };
  }, [selectedPet]);

  // Save to localStorage whenever data changes
  useEffect(() => {
    localStorage.setItem("budget", budget.toString());
  }, [budget]);

  useEffect(() => {
    localStorage.setItem("expenses", JSON.stringify(expenses));
  }, [expenses]);

  const handleAddExpense = (
    expenseData: Omit<Expense, "id">,
  ) => {
    const newExpense: Expense = {
      ...expenseData,
      id: Date.now().toString(),
    };
    setExpenses((prev) => [...prev, newExpense]);
  };

  const handleDeleteExpense = (id: string) => {
    setExpenses((prev) =>
      prev.filter((expense) => expense.id !== id),
    );
  };

  const handleUpdateBudget = (newBudget: number) => {
    setBudget(newBudget);
  };

  // Calculate totals
  const totalSpent = expenses.reduce(
    (sum, expense) => sum + expense.amount,
    0,
  );

  const categoryTotals = expenses.reduce(
    (acc, expense) => {
      acc[expense.category] =
        (acc[expense.category] || 0) + expense.amount;
      return acc;
    },
    {} as { [key: string]: number },
  );

  return (
    <div className="min-h-screen bg-cyan-100 pb-8 relative">
      {/* Dynamic Background with Smooth Transition */}
      <div
        className="fixed inset-0 z-0 transition-opacity duration-700"
        style={{
          backgroundImage: `url(${selectedPet === 'penguin' ? snowyBackground : selectedPet === 'dragon' ? dragonBackground : selectedPet === 'capybara' ? capybaraBackground : catBackground})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundAttachment: "fixed",
        }}
      >
        {/* Overlay for better readability */}
        <div className="absolute inset-0 bg-white/40 backdrop-blur-[2px]" />
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Header */}
        <header className={`bg-white/90 backdrop-blur-md border-b ${
          selectedPet === 'penguin' ? 'border-cyan-300' : 
          selectedPet === 'dragon' ? 'border-purple-300' : 
          selectedPet === 'capybara' ? 'border-green-300' : 
          'border-pink-300'
        } sticky top-0 z-20 shadow-sm transition-colors duration-500`}>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 sm:py-4">
            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2 sm:gap-3">
                <div className={`${
                  selectedPet === 'penguin' ? 'bg-gradient-to-br from-cyan-500 to-blue-500' : 
                  selectedPet === 'dragon' ? 'bg-gradient-to-br from-purple-500 to-pink-500' : 
                  selectedPet === 'capybara' ? 'bg-gradient-to-br from-green-500 to-lime-500' : 
                  'bg-gradient-to-br from-pink-500 to-red-500'
                } p-1.5 sm:p-2 rounded-xl sm:rounded-2xl shadow-lg transition-all duration-500`}>
                  <Sparkles className="h-5 w-5 sm:h-6 sm:w-6 text-white" />
                </div>
                <div>
                  <h1 className={`text-xl sm:text-2xl font-bold ${
                    selectedPet === 'penguin' ? 'bg-gradient-to-r from-cyan-600 to-blue-600' : 
                    selectedPet === 'dragon' ? 'bg-gradient-to-r from-purple-600 to-pink-600' : 
                    selectedPet === 'capybara' ? 'bg-gradient-to-r from-green-600 to-lime-600' : 
                    'bg-gradient-to-r from-pink-600 to-red-600'
                  } bg-clip-text text-transparent transition-all duration-500`}>
                    Budget Buddy
                  </h1>
                  <p className="text-xs sm:text-sm text-gray-600 hidden sm:block">
                    Your adorable spending companion
                  </p>
                </div>
              </div>
              <BudgetSettings
                currentBudget={budget}
                onUpdateBudget={handleUpdateBudget}
              />
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">
          <div className="space-y-4 sm:space-y-6">
            {/* Main Grid Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
              {/* Penny the Penguin - First on mobile, right column on desktop */}
              <div className="lg:col-span-1 lg:order-2">
                <BudgetBuddy
                  totalSpent={totalSpent}
                  budget={budget}
                  recentExpenses={expenses.slice(-5)}
                  categoryTotals={categoryTotals}
                />
              </div>

              {/* Left Column - Budget Summary, Form & Expenses (2 columns on desktop) */}
              <div className="lg:col-span-2 lg:order-1 space-y-4 sm:space-y-6">
                {/* Budget Summary */}
                <BudgetSummary
                  totalSpent={totalSpent}
                  budget={budget}
                  categories={categoryTotals}
                  onUpdateBudget={handleUpdateBudget}
                />
                
                <SpendingForm onAddExpense={handleAddExpense} />
                <SpendingGraph 
                  expenses={expenses}
                  budget={budget}
                  categoryTotals={categoryTotals}
                />
                <SpendingCalendar expenses={expenses} />
                <ExpenseList
                  expenses={expenses}
                  onDeleteExpense={handleDeleteExpense}
                />
              </div>
            </div>

            {/* Companion Selector at the Bottom */}
            <CompanionSelector />
          </div>
        </main>
      </div>
    </div>
  );
}