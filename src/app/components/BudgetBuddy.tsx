import { useState, useEffect, useRef } from "react";
import { motion } from "motion/react";
import { Send, Sparkles, Heart } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { ScrollArea } from "./ui/scroll-area";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { FriendshipStatus, updateLastActivity } from "./FriendshipStatus";

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

const GEMINI_API_KEY = import.meta.env.VITE_GEMINI_API_KEY;

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

/* ================= GEMINI CHAT ================= */

async function chatWithGemini(messages: Message[], context: string, petType: 'penguin' | 'dragon' | 'capybara' | 'cat') {
  const formatted = messages.map((m) => ({
    role: m.sender === "user" ? "user" : "model",
    parts: [{ text: m.text }],
  }));

  const petPersonality = petType === 'penguin'
    ? "You are Penny the Penguin 🐧, a friendly and warm budgeting assistant. Keep replies short, cheerful, and practical."
    : petType === 'dragon'
    ? "You are Esper the Dragon 🐉, a wise and enthusiastic budgeting guardian. Keep replies short, magical, and inspiring with a bit of dragon flair."
    : petType === 'cat'
    ? "You are Mochi the Cat 🐱, a playful and sweet budgeting assistant. Keep replies short, cute, and encouraging with a bit of cat charm."
    : "You are Capy the Capybara 🦫, a calm and thoughtful budgeting buddy. Keep replies short, relaxed, and helpful.";

  // Inject system + budget context
  formatted.unshift({
    role: "user",
    parts: [
      {
        text: `${petPersonality}

Current user context:
${context}
`,
      },
    ],
  });

  const res = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${GEMINI_API_KEY}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        contents: formatted,
        generationConfig: {
          temperature: 0.7,
          maxOutputTokens: 512,
        },
      }),
    }
  );

  const data = await res.json();

  const petName = petType === 'penguin' ? 'Penny' : petType === 'dragon' ? 'Esper' : petType === 'cat' ? 'Mochi' : 'Capy';
  return (
    data?.candidates?.[0]?.content?.parts?.[0]?.text ||
    `Sorry — ${petName} got tongue-tied 😅`
  );
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
  const [buddyMood, setBuddyMood] = useState<"happy" | "worried" | "excited">(
    "happy"
  );
  const scrollRef = useRef<HTMLDivElement>(null);
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
    const greetingText = petType === 'penguin'
      ? "Hi! I'm Penny 🐧 — your budgeting buddy. Ask me anything about your spending!"
      : petType === 'dragon'
      ? "Greetings! I'm Esper 🐉 — your wise budget guardian. Ask me anything about your treasure hoard!"
      : petType === 'cat'
      ? "Hello! I'm Mochi 🐱 — your playful budgeting assistant. Ask me anything about your finances!"
      : "Hello! I'm Capy 🦫 — your calm budgeting buddy. Ask me anything about your finances!";
    
    setMessages([
      {
        id: "1",
        text: greetingText,
        sender: "buddy",
        timestamp: new Date(),
      },
    ]);
  }, [petType]);

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

    const updated = [...messages, userMessage];
    setMessages(updated);
    setInput("");
    setPetAnimation((p) => p + 1);

    const context = `
Budget: $${budget}
Total spent: $${totalSpent}
Remaining: $${(budget - totalSpent).toFixed(2)}

Category totals:
${JSON.stringify(categoryTotals, null, 2)}

Recent expenses:
${JSON.stringify(recentExpenses.slice(0, 5), null, 2)}
`;

    try {
      const reply = await chatWithGemini(updated, context, petType);

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          text: reply,
          sender: "buddy",
          timestamp: new Date(),
        },
      ]);
    } catch {
      const petName = getPetName();
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          text: `Oops — ${petName} couldn't reach Gemini 😢`,
          sender: "buddy",
          timestamp: new Date(),
        },
      ]);
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
        <CardHeader>
          <CardTitle>Chat with {getPetName()}</CardTitle>
        </CardHeader>

        <CardContent className="space-y-3">
          <ScrollArea className="h-64 border rounded p-3">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`mb-2 flex ${
                  m.sender === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`px-3 py-2 rounded-xl max-w-[80%] ${
                    m.sender === "user"
                      ? "bg-blue-500 text-white"
                      : "bg-white border"
                  }`}
                >
                  {m.text}
                </div>
              </div>
            ))}
            <div ref={scrollRef} />
          </ScrollArea>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex gap-2"
          >
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={`Ask ${getPetName()} anything...`}
            />

            <Button type="submit" size="icon">
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}