import { useState } from 'react';
import { Plus, Calendar as CalendarIcon } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Popover, PopoverContent, PopoverTrigger } from './ui/popover';
import { Calendar } from './ui/calendar';
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

export function SpendingForm({ onAddExpense }: SpendingFormProps) {
  const [amount, setAmount] = useState('');
  const [category, setCategory] = useState('');
  const [description, setDescription] = useState('');
  const [date, setDate] = useState<Date>(new Date());
  const [isCalendarOpen, setIsCalendarOpen] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (amount && category) {
      onAddExpense({
        amount: parseFloat(amount),
        category,
        description,
        date: date.toISOString()
      });
      setAmount('');
      setCategory('');
      setDescription('');
      setDate(new Date());
    }
  };

  const handleDateSelect = (selectedDate: Date | undefined) => {
    if (selectedDate) {
      setDate(selectedDate);
      setIsCalendarOpen(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base sm:text-lg">Add New Expense</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
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
              <Select value={category} onValueChange={setCategory}>
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
      </CardContent>
    </Card>
  );
}