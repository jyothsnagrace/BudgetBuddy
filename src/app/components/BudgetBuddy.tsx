import { useState, useEffect, useRef } from "react";
import { motion } from "motion/react";
import { Send, Sparkles, Heart, MapPin } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { ScrollArea } from "./ui/scroll-area";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { FriendshipStatus, updateLastActivity } from "./FriendshipStatus";
import { API_URL } from "../../config";

import penguinHappy from "../../assets/penguin-happy.png";
import penguinWorried from "../../assets/penguin-worried.png";
import penguinExcited from "../../assets/penguin-excited.png";
import dragonHappy from "../../assets/dragon-happy.png";
import dragonSad from "../../assets/dragon-sad.png";
import capybaraHappy from "../../assets/capybara-happy.png";
import capybaraStressed from "../../assets/capybara-stressed.png";
import capybaraCalm from "../../assets/capybara-sad.png";
import catHappy from "../../assets/cat-happy.png";
import catSad from "../../assets/cat-sad.png";

interface Message {
  id: string;
  text: string;
  sender: "user" | "buddy";
  timestamp: Date;
}

interface BudgetBuddyProps {
  totalSpent: number;
  budget: number;
  recentExpenses: Array<{
    amount: number;
    category: string;
    description: string;
  }>;
  categoryTotals: { [key: string]: number };
}

/* ================= ENHANCED BACKEND CHAT ================= */

async function chatWithBackend(message: string, city?: string) {
  const token = localStorage.getItem("token");
  
  if (!token) {
    return "Please login to chat with me! 🔒";
  }

  try {
    const response = await fetch(`${API_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify({
        message: message,
        city: city || null,
        context: {}
      }),
    });

    if (!response.ok) {
      throw new Error("Chat request failed");
    }

    const data = await response.json();
    return data.response || "Sorry, I couldn't generate a response 😅";
  } catch (error) {
    console.error("Chat error:", error);
    return "Oops, I'm having connection trouble! Try again? 💭";
  }
}

/* ================= COMPONENT ================= */

export function BudgetBuddy({
  totalSpent,
  budget,
  recentExpenses,
  categoryTotals,
}: BudgetBuddyProps) {
  const [petType, setPetType] = useState<'penguin' | 'dragon' | 'capybara' | 'cat'>(() => {
    const saved = localStorage.getItem('selectedPet');
    return (saved as 'penguin' | 'dragon' | 'capybara' | 'cat') || 'penguin';
  });
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [city, setCity] = useState("");
  const [buddyMood, setBuddyMood] = useState<"happy" | "worried" | "excited">(
    "happy"
  );
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const [petAnimation, setPetAnimation] = useState(0);

  /* ===== Save Pet Selection ===== */
  
  useEffect(() => {
    localStorage.setItem('selectedPet', petType);
  }, [petType]);

  /* ===== Listen for Pet Changes ===== */
  
  useEffect(() => {
    const handleStorageChange = () => {
      const saved = localStorage.getItem('selectedPet');
      if (saved && saved !== petType) {
        setPetType(saved as 'penguin' | 'dragon' | 'capybara' | 'cat');
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    
    // Also check periodically for same-tab changes
    const interval = setInterval(() => {
      const saved = localStorage.getItem('selectedPet');
      const currentPet = (saved as 'penguin' | 'dragon' | 'capybara' | 'cat') || 'penguin';
      if (currentPet !== petType) {
        setPetType(currentPet);
      }
    }, 100);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      clearInterval(interval);
    };
  }, [petType]);

  /* ===== Mood ===== */

  useEffect(() => {
    const percent = budget > 0 ? (totalSpent / budget) * 100 : 0;
    if (percent < 60) setBuddyMood("happy");
    else if (percent < 90) setBuddyMood("worried");
    else setBuddyMood("excited");
  }, [totalSpent, budget]);

  /* ===== Initial Greeting ===== */

  useEffect(() => {
    const petName = getPetName();
    const cityText = city ? ` I see you're in ${city}! 📍` : '';
    
    const greetingText = petType === 'penguin'
      ? `Hi! I'm Penny 🐧 — your budgeting buddy.${cityText} Ask me anything about your spending or local costs!`
      : petType === 'dragon'
      ? `Greetings! I'm Esper 🐉 — guardian of your treasure hoard.${cityText} Ask me for ancient wisdom about spending!`
      : petType === 'cat'
      ? `*Purrs* Hello! I'm Mochi 🐱 — your sassy money friend.${cityText} Ask me anything, fur real!`
      : `Hey there! I'm Capy 🦫 — your chill budgeting buddy.${cityText} No stress, just ask me anything!`
    
    setMessages([
      {
        id: "1",
        text: greetingText,
        sender: "buddy",
        timestamp: new Date(),
      },
    ]);
  }, [petType, city]);

  /* ===== Auto Scroll (only on new messages, not on pet change) ===== */

  const prevMessageLengthRef = useRef(messages.length);
  
  useEffect(() => {
    // Only scroll if a new message was added (not when messages were reset)
    if (messages.length > prevMessageLengthRef.current) {
      scrollRef.current?.scrollIntoView({ behavior: "smooth" });
    }
    prevMessageLengthRef.current = messages.length;
  }, [messages]);

  /* ===== Send Message ===== */

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: input,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input;
    setInput("");
    setPetAnimation((p) => p + 1);

    try {
      // Use enhanced backend API with city support
      const reply = await chatWithBackend(currentInput, city || undefined);

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          text: reply,
          sender: "buddy",
          timestamp: new Date(),
        },
      ]);
      
      // Update last activity for friendship level
      updateLastActivity();
    } catch (error) {
      const petName = getPetName();
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          text: `Oops — ${petName} couldn't connect! 😢 Try again?`,
          sender: "buddy",
          timestamp: new Date(),
        },
      ]);
    } finally {
      // Focus back on input for quick follow-up questions
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  /* ===== Helpers ===== */

  const getBuddyImage = () => {
    if (petType === 'penguin') {
      return buddyMood === "happy"
        ? penguinHappy
        : buddyMood === "worried"
        ? penguinWorried
        : penguinExcited;
    } else if (petType === 'dragon') {
      // Dragon: happy when budget is good, sad when bad
      const percent = budget > 0 ? (totalSpent / budget) * 100 : 0;
      return percent < 80 ? dragonHappy : dragonSad;
    } else if (petType === 'cat') {
      return buddyMood === "happy"
        ? catHappy
        : catSad;
    } else {
      // Capybara: happy when budget is good, stressed when bad
      const percent = budget > 0 ? (totalSpent / budget) * 100 : 0;
      return percent < 80 ? capybaraHappy : capybaraStressed;
    }
  };

  const getMoodDescription = () => {
    const percent = budget > 0 ? (totalSpent / budget) * 100 : 0;
    
    if (petType === 'penguin') {
      if (percent < 60) return "Feeling happy 😊";
      if (percent < 90) return "A bit worried 😟";
      return "Over budget 😱";
    } else if (petType === 'dragon') {
      // Dragon moods
      if (percent < 60) return "Guarding treasure ✨";
      if (percent < 80) return "Watching closely 👀";
      return "Treasure low! 🔥";
    } else if (petType === 'cat') {
      if (percent < 60) return "Playful and happy 😸";
      if (percent < 90) return "A bit concerned 🤔";
      return "Budget tight! 💰";
    } else {
      // Capybara moods
      if (percent < 60) return "Calm and collected 🧘‍♂️";
      if (percent < 80) return "Stressed but trying 🤔";
      return "Budget tight! 💰";
    }
  };

  const getPetName = () => petType === 'penguin' ? 'Penny' : petType === 'dragon' ? 'Esper' : petType === 'cat' ? 'Mochi' : 'Capy';
  const getPetTitle = () => petType === 'penguin' ? 'Penny the Penguin' : petType === 'dragon' ? 'Esper the Dragon' : petType === 'cat' ? 'Mochi the Cat' : 'Capy the Capybara';
  const getPetIcon = () => petType === 'penguin' ? '🐧' : petType === 'dragon' ? '🐉' : petType === 'cat' ? '🐱' : '🦫';

  const handlePetClick = () => setPetAnimation((p) => p + 1);

  const handlePetChange = (newPet: 'penguin' | 'dragon' | 'capybara' | 'cat') => {
    setPetType(newPet);
    setPetAnimation((p) => p + 1);
  };

  /* ================= UI ================= */

  return (
    <div className="space-y-4">
      {/* Pet Card */}

      <Card className={`border-2 ${petType === 'penguin' ? 'border-cyan-300' : petType === 'dragon' ? 'border-purple-300' : petType === 'cat' ? 'border-pink-300' : 'border-green-300'} bg-white/85 shadow-lg`}>
        <CardHeader className="text-center">
          <CardTitle className="flex justify-center gap-2">
            <Heart className="h-5 w-5 text-pink-500 fill-pink-500" />
            {getPetTitle()}
            <Heart className="h-5 w-5 text-pink-500 fill-pink-500" />
          </CardTitle>
        </CardHeader>

        <CardContent>
          <motion.div
            onClick={handlePetClick}
            className="flex flex-col items-center cursor-pointer"
            whileHover={{ scale: 1.05 }}
          >
            <motion.img
              key={petAnimation}
              src={getBuddyImage()}
              className="w-40 h-40 object-contain"
              animate={{ y: [0, -10, 0] }}
              transition={{ duration: 0.6 }}
            />

            <div className={`mt-2 px-4 py-1 rounded-full border ${petType === 'penguin' ? 'border-cyan-300 bg-cyan-50' : petType === 'dragon' ? 'border-purple-300 bg-purple-50' : petType === 'cat' ? 'border-pink-300 bg-pink-50' : 'border-green-300 bg-green-50'}`}>
              <span className="text-xs text-gray-500">Mood: </span>
              {getMoodDescription()}
            </div>

            <Sparkles className={`mt-2 ${petType === 'penguin' ? 'text-cyan-400' : petType === 'dragon' ? 'text-purple-400' : petType === 'cat' ? 'text-pink-400' : 'text-green-400'}`} />
          </motion.div>

          {/* Friendship Status Bar - Based on App Activity */}
          <div className="mt-6 pt-4 border-t">
            <p className="text-xs text-gray-500 mb-2">Friendship Level</p>
            <FriendshipStatus petType={petType} />
          </div>
        </CardContent>
      </Card>

      {/* Chat */}

      <Card className={`border-2 ${petType === 'penguin' ? 'border-cyan-300' : petType === 'dragon' ? 'border-purple-300' : petType === 'cat' ? 'border-pink-300' : 'border-green-300'} bg-white/85 shadow-lg`}>
        <CardHeader className="space-y-1 pb-3">
          <CardTitle className="text-xl font-bold">Ask Your AI Advisor</CardTitle>
          <p className="text-sm text-gray-600">
            Get location-aware financial advice from {getPetName()}!
          </p>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* City Selector */}
          <div className="flex items-center gap-2">
            <MapPin className="h-4 w-4 text-gray-500 flex-shrink-0" />
            <Select value={city} onValueChange={setCity}>
              <SelectTrigger className="flex-1">
                <SelectValue placeholder="Select a city (optional)" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="New York">New York, NY</SelectItem>
                <SelectItem value="Los Angeles">Los Angeles, CA</SelectItem>
                <SelectItem value="Chicago">Chicago, IL</SelectItem>
                <SelectItem value="Houston">Houston, TX</SelectItem>
                <SelectItem value="Phoenix">Phoenix, AZ</SelectItem>
                <SelectItem value="Philadelphia">Philadelphia, PA</SelectItem>
                <SelectItem value="San Antonio">San Antonio, TX</SelectItem>
                <SelectItem value="San Diego">San Diego, CA</SelectItem>
                <SelectItem value="Dallas">Dallas, TX</SelectItem>
                <SelectItem value="San Jose">San Jose, CA</SelectItem>
                <SelectItem value="Austin">Austin, TX</SelectItem>
                <SelectItem value="Jacksonville">Jacksonville, FL</SelectItem>
                <SelectItem value="Fort Worth">Fort Worth, TX</SelectItem>
                <SelectItem value="Columbus">Columbus, OH</SelectItem>
                <SelectItem value="Charlotte">Charlotte, NC</SelectItem>
                <SelectItem value="San Francisco">San Francisco, CA</SelectItem>
                <SelectItem value="Indianapolis">Indianapolis, IN</SelectItem>
                <SelectItem value="Seattle">Seattle, WA</SelectItem>
                <SelectItem value="Denver">Denver, CO</SelectItem>
                <SelectItem value="Boston">Boston, MA</SelectItem>
                <SelectItem value="Washington">Washington, DC</SelectItem>
                <SelectItem value="Nashville">Nashville, TN</SelectItem>
                <SelectItem value="Portland">Portland, OR</SelectItem>
                <SelectItem value="Las Vegas">Las Vegas, NV</SelectItem>
                <SelectItem value="Detroit">Detroit, MI</SelectItem>
                <SelectItem value="Miami">Miami, FL</SelectItem>
                <SelectItem value="Atlanta">Atlanta, GA</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Example Questions */}
          <div className="bg-white border border-gray-200 rounded-lg p-3 space-y-2">
            <p className="text-xs font-semibold text-gray-700 flex items-center gap-1">
              <Sparkles className="h-3 w-3" />
              Try asking:
            </p>
            <div className="space-y-1.5">
              <button
                type="button"
                onClick={() => {
                  setInput(`Is it smarter to buy or rent in ${city || 'Charlotte'}?`);
                  setTimeout(() => inputRef.current?.focus(), 50);
                }}
                className="flex items-start gap-2 text-sm text-gray-700 hover:text-purple-600 hover:bg-purple-50 w-full text-left p-1.5 rounded transition-colors"
              >
                <span className="text-base flex-shrink-0">🏠</span>
                <span>"Is it smarter to buy or rent in {city || 'Charlotte'}?"</span>
              </button>
              <button
                type="button"
                onClick={() => {
                  setInput(`Which are budget friendly restaurants in ${city || 'Charlotte'}?`);
                  setTimeout(() => inputRef.current?.focus(), 50);
                }}
                className="flex items-start gap-2 text-sm text-gray-700 hover:text-purple-600 hover:bg-purple-50 w-full text-left p-1.5 rounded transition-colors"
              >
                <span className="text-base flex-shrink-0">🍽️</span>
                <span>"Which are budget friendly restaurants in {city || 'Charlotte'}?"</span>
              </button>
              <button
                type="button"
                onClick={() => {
                  setInput(`How does my spending compare to ${city || 'Charlotte'} average?`);
                  setTimeout(() => inputRef.current?.focus(), 50);
                }}
                className="flex items-start gap-2 text-sm text-gray-700 hover:text-purple-600 hover:bg-purple-50 w-full text-left p-1.5 rounded transition-colors"
              >
                <span className="text-base flex-shrink-0">📊</span>
                <span>"How does my spending compare to {city || 'Charlotte'} average?"</span>
              </button>
              <button
                type="button"
                onClick={() => {
                  setInput(`What's the cost of living in ${city || 'Charlotte'}?`);
                  setTimeout(() => inputRef.current?.focus(), 50);
                }}
                className="flex items-start gap-2 text-sm text-gray-700 hover:text-purple-600 hover:bg-purple-50 w-full text-left p-1.5 rounded transition-colors"
              >
                <span className="text-base flex-shrink-0">🏠</span>
                <span>"What's the cost of living in {city || 'Charlotte'}?"</span>
              </button>
            </div>
          </div>

          {/* Chat Messages */}
          <ScrollArea className="h-64 bg-gray-50 border border-gray-200 rounded-lg p-3">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`mb-3 flex ${
                  m.sender === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`px-4 py-2.5 rounded-2xl max-w-[85%] shadow-sm ${
                    m.sender === "user"
                      ? "bg-blue-500 text-white"
                      : "bg-white border border-gray-200 text-gray-800"
                  }`}
                >
                  {m.text}
                </div>
              </div>
            ))}
            <div ref={scrollRef} />
          </ScrollArea>

          {/* Input Form */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex gap-2"
          >
            <Input
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={city ? `Ask about ${city}...` : `Ask about Charlotte...`}
              className="flex-1"
              autoFocus
            />

            <Button 
              type="submit" 
              size="icon"
              className="bg-black hover:bg-gray-800 rounded-lg"
            >
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}