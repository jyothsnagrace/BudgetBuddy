import { useState, useRef, useEffect } from 'react';
import { Plus, Calendar as CalendarIcon, Sparkles, Camera, Edit3 } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Popover, PopoverContent, PopoverTrigger } from './ui/popover';
import { Calendar } from './ui/calendar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Textarea } from './ui/textarea';
import { format } from 'date-fns';
import { cn } from './ui/utils';

interface SpendingFormProps {
  onAddExpense: (expense: {
    amount: number;
    category: string;
    description: string;
    date: string;
  }) => void;
}

const categories = [
  '🍕 Food',
  '🏠 Housing',
  '🚗 Transportation',
  '🎮 Entertainment',
  '🛍️ Shopping',
  '💊 Healthcare',
  '📚 Education',
  '💰 Other'
];

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function SpendingForm({ onAddExpense }: SpendingFormProps) {
  // Manual entry state
  const [amount, setAmount] = useState('');
  const [category, setCategory] = useState('');
  const [description, setDescription] = useState('');
  const [date, setDate] = useState<Date>(new Date());
  const [isCalendarOpen, setIsCalendarOpen] = useState(false);
  
  // Quick add state
  const [quickText, setQuickText] = useState('');
  const [isParsingQuick, setIsParsingQuick] = useState(false);
  
  // Receipt photo state
  const [receiptImage, setReceiptImage] = useState<File | null>(null);
  const [isParsingReceipt, setIsParsingReceipt] = useState(false);
  const [receiptPreview, setReceiptPreview] = useState<string | null>(null);
  
  // Tab control - Default to Manual Entry
  const [activeTab, setActiveTab] = useState('manual');
  
  // Refs for focus management
  const manualFormRef = useRef<HTMLDivElement>(null);
  const quickInputRef = useRef<HTMLTextAreaElement>(null);
  
  // Focus on manual tab on mount
  useEffect(() => {
    if (activeTab === 'manual' && manualFormRef.current) {
      const firstInput = manualFormRef.current.querySelector('input');
      if (firstInput) {
        (firstInput as HTMLInputElement).focus();
      }
    }
  }, [activeTab]);

  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (amount && category) {
      onAddExpense({
        amount: parseFloat(amount),
        category,
        description,
        date: date.toISOString()
      });
      
      // Reset form without scrolling
      setAmount('');
      setCategory('');
      setDescription('');
      setDate(new Date());
      
      // Prevent page scroll
      window.scrollTo({ top: window.scrollY, behavior: 'auto' });
    }
  };


  const handleDateSelect = (selectedDate: Date | undefined) => {
    if (selectedDate) {
      setDate(selectedDate);
      setIsCalendarOpen(false);
    }
  };
  
  // Quick Add: Parse natural language
  const handleParseQuickAdd = async () => {
    if (!quickText.trim()) return;
    
    setIsParsingQuick(true);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/parse-expense`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: quickText })
      });
      
      if (!response.ok) throw new Error('Failed to parse expense');
      
      const data = await response.json();
      const parsed = data.parsed_data;
      
      // Fill manual form with parsed data
      setAmount(parsed.amount.toString());
      setCategory(mapCategoryToEmoji(parsed.category));
      setDescription(parsed.description || '');
      setDate(new Date(parsed.date));
      
      // Switch to manual tab and focus
      setActiveTab('manual');
      setQuickText('');
      
      // Focus on manual form
      setTimeout(() => {
        if (manualFormRef.current) {
          const firstInput = manualFormRef.current.querySelector('input');
          if (firstInput) (firstInput as HTMLInputElement).focus();
        }
      }, 100);
      
    } catch (error) {
      console.error('Parse error:', error);
      alert('Failed to parse expense. Please try again or use manual entry.');
    } finally {
      setIsParsingQuick(false);
    }
  };
  
  // Receipt Photo: Parse image
  const handleReceiptUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    setReceiptImage(file);
    
    // Create preview
    const reader = new FileReader();
    reader.onload = (event) => {
      setReceiptPreview(event.target?.result as string);
    };
    reader.readAsDataURL(file);
  };
  
  const handleParseReceipt = async () => {
    if (!receiptImage) return;
    
    setIsParsingReceipt(true);
    
    try {
      const formData = new FormData();
      formData.append('file', receiptImage);
      
      const response = await fetch(`${API_BASE_URL}/api/parse-receipt`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) throw new Error('Failed to parse receipt');
      
      const data = await response.json();
      const parsed = data.parsed_data;
      
      // Fill manual form with parsed data
      setAmount(parsed.amount.toString());
      setCategory(mapCategoryToEmoji(parsed.category));
      setDescription(parsed.description || '');
      setDate(new Date(parsed.date));
      
      // Switch to manual tab
      setActiveTab('manual');
      setReceiptImage(null);
      setReceiptPreview(null);
      
      // Focus on manual form
      setTimeout(() => {
        if (manualFormRef.current) {
          const firstInput = manualFormRef.current.querySelector('input');
          if (firstInput) (firstInput as HTMLInputElement).focus();
        }
      }, 100);
      
    } catch (error) {
      console.error('Receipt parse error:', error);
      alert('Failed to parse receipt. Please try manual entry.');
    } finally {
      setIsParsingReceipt(false);
    }
  };
  
  // Helper: Map backend category to emoji category
  const mapCategoryToEmoji = (category: string): string => {
    const mapping: Record<string, string> = {
      'Food': '🍔 Food',
      'Transportation': '🚗 Transportation',
      'Entertainment': '🎬 Entertainment',
      'Shopping': '🛒 Shopping',
      'Bills': '🏠 Bills',
      'Healthcare': '💊 Healthcare',
      'Education': '📚 Education',
      'Other': '✨ Other'
    };
    return mapping[category] || '✨ Other';
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base sm:text-lg">Add New Expense</CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-4">
            <TabsTrigger value="quick" className="text-xs sm:text-sm">
              <Sparkles className="w-4 h-4 mr-1" />
              Quick Add
            </TabsTrigger>
            <TabsTrigger value="photo" className="text-xs sm:text-sm">
              <Camera className="w-4 h-4 mr-1" />
              Receipt
            </TabsTrigger>
            <TabsTrigger value="manual" className="text-xs sm:text-sm">
              <Edit3 className="w-4 h-4 mr-1" />
              Manual
            </TabsTrigger>
          </TabsList>
          
          {/* Quick Add Tab */}
          <TabsContent value="quick" className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="quick-input">Type naturally</Label>
              <Textarea
                id="quick-input"
                ref={quickInputRef}
                placeholder='Example: "Lunch at Chipotle $15" or "Coffee $5.50 today"'
                value={quickText}
                onChange={(e) => setQuickText(e.target.value)}
                rows={3}
                className="resize-none"
              />
            </div>
            <Button
              onClick={handleParseQuickAdd}
              disabled={!quickText.trim() || isParsingQuick}
              className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
            >
              {isParsingQuick ? (
                <>Processing...</>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  Parse & Fill
                </>
              )}
            </Button>
            <p className="text-xs text-muted-foreground text-center">
              AI will extract the details and switch to Manual tab for review
            </p>
          </TabsContent>
          
          {/* Receipt Photo Tab */}
          <TabsContent value="photo" className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="receipt-upload">Upload Receipt Photo</Label>
              <Input
                id="receipt-upload"
                type="file"
                accept="image/*"
                onChange={handleReceiptUpload}
                className="cursor-pointer"
              />
            </div>
            
            {receiptPreview && (
              <div className="relative">
                <img 
                  src={receiptPreview} 
                  alt="Receipt preview" 
                  className="w-full max-h-64 object-contain rounded-lg border"
                />
              </div>
            )}
            
            <Button
              onClick={handleParseReceipt}
              disabled={!receiptImage || isParsingReceipt}
              className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600"
            >
              {isParsingReceipt ? (
                <>Analyzing Receipt...</>
              ) : (
                <>
                  <Camera className="mr-2 h-4 w-4" />
                  Parse Receipt
                </>
              )}
            </Button>
            <p className="text-xs text-muted-foreground text-center">
              Vision AI will extract expense data and auto-fill the form
            </p>
          </TabsContent>
          
          {/* Manual Entry Tab */}
          <TabsContent value="manual" className="space-y-4">
            <form onSubmit={handleManualSubmit} className="space-y-4" ref={manualFormRef}>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="amount">Amount</Label>
                  <Input
                    id="amount"
                    type="number"
                    step="0.01"
                    placeholder="0.00"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="category">Category</Label>
                  <Select value={category} onValueChange={setCategory} required>
                    <SelectTrigger id="category">
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="🍔 Food">🍔 Food</SelectItem>
                      <SelectItem value="🚗 Transportation">🚗 Transportation</SelectItem>
                      <SelectItem value="🎬 Entertainment">🎬 Entertainment</SelectItem>
                      <SelectItem value="🛒 Shopping">🛒 Shopping</SelectItem>
                      <SelectItem value="🏠 Bills">🏠 Bills</SelectItem>
                      <SelectItem value="💊 Healthcare">💊 Healthcare</SelectItem>
                      <SelectItem value="📚 Education">📚 Education</SelectItem>
                      <SelectItem value="✨ Other">✨ Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description (optional)</Label>
                <Input
                  id="description"
                  type="text"
                  placeholder="What did you buy?"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="date">Date</Label>
                <Popover open={isCalendarOpen} onOpenChange={setIsCalendarOpen}>
                  <PopoverTrigger asChild>
                    <Button
                      id="date"
                      variant="outline"
                      className={cn(
                        "w-full justify-start text-left font-normal",
                        !date && "text-muted-foreground"
                      )}
                      type="button"
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {date ? format(date, 'PPP') : <span>Pick a date</span>}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0 bg-white" align="start">
                    <Calendar
                      mode="single"
                      selected={date}
                      onSelect={handleDateSelect}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
              </div>
              <Button 
                type="submit" 
                className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
              >
                <Plus className="mr-2 h-4 w-4" />
                Add Expense
              </Button>
            </form>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}