"""
Two-LLM Pipeline for Expense Parsing
LLM #1: Extraction Agent
LLM #2: Normalization & Validation Agent
"""

import os
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, date
import google.generativeai as genai
from jsonschema import validate, ValidationError

# Try to import Groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("Warning: groq package not installed. Install with: pip install groq")

# Configure LLM providers
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Groq client
groq_client = None
if GROQ_API_KEY and GROQ_AVAILABLE:
    groq_client = Groq(api_key=GROQ_API_KEY)

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# JSON Schema for expense validation
EXPENSE_SCHEMA = {
    "type": "object",
    "required": ["amount", "category", "date"],
    "properties": {
        "amount": {
            "type": "number",
            "minimum": 0,
            "description": "Expense amount in dollars"
        },
        "category": {
            "type": "string",
            "enum": [
                "Food", 
                "Transportation", 
                "Entertainment", 
                "Shopping", 
                "Bills", 
                "Healthcare", 
                "Education", 
                "Other"
            ],
            "description": "Expense category"
        },
        "description": {
            "type": "string",
            "maxLength": 200,
            "description": "Description of the expense"
        },
        "date": {
            "type": "string",
            "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
            "description": "Date in YYYY-MM-DD format"
        }
    }
}


class LLMPipeline:
    """Two-stage LLM pipeline for expense processing"""
    
    def __init__(self):
        self.provider = LLM_PROVIDER
        
        print(f"[LLMPipeline] DEBUG: LLM_PROVIDER env = '{os.getenv('LLM_PROVIDER')}'")
        print(f"[LLMPipeline] DEBUG: self.provider = '{self.provider}'")
        print(f"[LLMPipeline] DEBUG: GROQ_AVAILABLE = {GROQ_AVAILABLE}")
        print(f"[LLMPipeline] DEBUG: groq_client = {groq_client}")
        
        if self.provider == "groq":
            if not groq_client:
                print("[LLMPipeline] ⚠️ Groq requested but not available, falling back to Gemini")
                self.provider = "gemini"
            else:
                print(f"[LLMPipeline] Initializing with Groq ({GROQ_MODEL})")
                self.groq_client = groq_client
                self.groq_model = GROQ_MODEL
        
        if self.provider == "gemini":
            print(f"[LLMPipeline] Initializing with gemini-2.5-flash")
            self.extraction_model = genai.GenerativeModel('gemini-2.5-flash')
            print(f"[LLMPipeline] Extraction model: {self.extraction_model._model_name}")
            self.normalization_model = genai.GenerativeModel('gemini-2.5-flash')
            self.chat_model = genai.GenerativeModel('gemini-2.5-flash')
        
    def health_check(self) -> bool:
        """Check if LLM service is available"""
        try:
            if self.provider == "groq":
                # Test Groq
                response = self.groq_client.chat.completions.create(
                    model=self.groq_model,
                    messages=[{"role": "user", "content": "Say OK"}],
                    max_tokens=10
                )
                return bool(response.choices[0].message.content)
            else:
                # Test Gemini
                response = self.extraction_model.generate_content("Say 'OK'")
                return bool(response.text)
        except Exception as e:
            print(f"[LLM Health Check] Failed: {e}")
            return False
    
    async def parse_expense(self, natural_text: str) -> Dict[str, Any]:
        """
        Two-stage pipeline for parsing natural language expense
        
        Stage 1: Extract raw structured data
        Stage 2: Normalize and validate
        """
        print(f"[parse_expense] DEBUG: provider = '{self.provider}'")
        
        # Stage 1: Extraction
        extracted_data = await self._extraction_stage(natural_text)
        
        # Stage 2: Normalization
        normalized_data = await self._normalization_stage(extracted_data, natural_text)
        
        # Stage 3: Validation
        validated_data = self._validation_stage(normalized_data)
        
        return validated_data
    
    async def _extraction_stage(self, text: str) -> Dict[str, Any]:
        """
        LLM #1: Extract structured data from natural language
        """
        print(f"[_extraction_stage] DEBUG: provider = '{self.provider}'")
        print(f"[_extraction_stage] DEBUG: has groq_client = {hasattr(self, 'groq_client')}")
        
        prompt = f"""You are an expense extraction assistant. Extract expense information from the following text.

Text: "{text}"

Extract and return ONLY a JSON object with these fields:
- amount: The numeric amount (just the number, no currency symbols)
- category: Best matching category (Food, Transportation, Entertainment, Shopping, Bills, Healthcare, Education, or Other)
- description: Brief description of what was purchased
- date: Date in YYYY-MM-DD format (use today's date if not specified: {date.today().isoformat()})

Return ONLY valid JSON, no other text.

Example:
{{
  "amount": 15.50,
  "category": "Food",
  "description": "Lunch at Chipotle",
  "date": "2026-02-17"
}}

Now extract from the given text:"""
        
        try:
            if self.provider == "groq":
                # Use Groq API
                response = self.groq_client.chat.completions.create(
                    model=self.groq_model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expense extraction assistant. Extract structured data and return only valid JSON."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=256,
                )
                llm_response = response.choices[0].message.content
            else:
                # Use Gemini API
                response = self.extraction_model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': 0.3,
                        'max_output_tokens': 256,
                    }
                )
                llm_response = response.text
            
            # Extract JSON from response
            json_text = self._extract_json(llm_response)
            parsed_data = json.loads(json_text)
            
            return parsed_data
            
        except Exception as e:
            raise ValueError(f"Extraction failed: {str(e)}")
    
    async def _normalization_stage(self, extracted_data: Dict, original_text: str) -> Dict[str, Any]:
        """
        LLM #2: Normalize and clean extracted data
        """
        prompt = f"""You are a data normalization assistant. Clean and validate this expense data.

Original text: "{original_text}"
Extracted data: {json.dumps(extracted_data)}

Normalize the data according to these rules:
1. Category MUST be exactly one of: Food, Transportation, Entertainment, Shopping, Bills, Healthcare, Education, Other
2. Amount must be a positive number (remove $ signs, convert to float)
3. Date must be YYYY-MM-DD format (validate it's a real date)
4. Description should be clear and concise (max 200 chars)

Valid categories mapping:
- Food/dining/restaurant/grocery → "Food"
- Uber/taxi/gas/car/bus/train → "Transportation"
- Movie/concert/game/fun → "Entertainment"
- Clothes/shoes/electronics → "Shopping"
- Rent/utilities/phone/internet → "Bills"
- Doctor/medicine/pharmacy → "Healthcare"
- Books/course/tuition → "Education"
- Anything else → "Other"

Return ONLY a normalized JSON object:
{{
  "amount": <number>,
  "category": "<exact category name>",
  "description": "<cleaned description>",
  "date": "<YYYY-MM-DD>"
}}

Return ONLY valid JSON, no other text."""
        
        try:
            if self.provider == "groq":
                # Use Groq API
                response = self.groq_client.chat.completions.create(
                    model=self.groq_model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a data normalization assistant. Clean and validate data and return only valid JSON."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.2,
                    max_tokens=256,
                )
                llm_response = response.choices[0].message.content
            else:
                # Use Gemini API
                response = self.normalization_model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': 0.2,
                        'max_output_tokens': 256,
                    }
                )
                llm_response = response.text
            
            # Extract JSON from response
            json_text = self._extract_json(llm_response)
            normalized_data = json.loads(json_text)
            
            return normalized_data
            
        except Exception as e:
            raise ValueError(f"Normalization failed: {str(e)}")
    
    def _validation_stage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stage 3: Validate against JSON schema
        """
        try:
            # Ensure amount is float
            if 'amount' in data:
                data['amount'] = float(data['amount'])
            
            # Validate against schema
            validate(instance=data, schema=EXPENSE_SCHEMA)
            
            # Additional validation
            self._validate_date(data.get('date'))
            self._validate_category(data.get('category'))
            
            return data
            
        except ValidationError as e:
            raise ValueError(f"Validation failed: {e.message}")
        except Exception as e:
            raise ValueError(f"Validation error: {str(e)}")
    
    def _validate_date(self, date_str: str):
        """Validate date string"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}")
    
    def _validate_category(self, category: str):
        """Validate category"""
        valid_categories = [
            'Food', 'Transportation', 'Entertainment', 
            'Shopping', 'Bills', 'Healthcare', 'Education', 'Other'
        ]
        if category not in valid_categories:
            raise ValueError(f"Invalid category: {category}")
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from LLM response"""
        # Remove markdown code blocks
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Find JSON object
        json_match = re.search(r'\{[^}]+\}', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        # If no match, try the whole text
        return text.strip()
    
    async def chat_response(
        self, 
        message: str, 
        user_context: Dict[str, Any],
        col_data: Optional[Dict] = None,
        chat_context: Optional[Dict] = None
    ) -> str:
        """
        Generate smart chatbot response
        City-aware, context-aware, personality-based, mood-aware
        """
        # Get pet personality and user info
        pet_type = user_context.get('selected_pet', 'penguin')
        friendship_level = user_context.get('friendship_level', 1)
        username = user_context.get('username', 'friend')
        
        personality = self._get_personality_prompt(pet_type, friendship_level)
        
        # Build context prompt
        budget = user_context.get('budget', 0)
        total_spent = user_context.get('total_spent', 0)
        remaining = budget - total_spent
        
        # Determine mood based on budget status
        if remaining < 0:
            mood = "concerned (user is over budget)"
            mood_instruction = "Be gentle but encouraging. Offer support and practical tips."
        elif remaining < budget * 0.2:
            mood = "cautiously optimistic (budget running low)"
            mood_instruction = "Be supportive and help them stretch remaining budget."
        elif remaining > budget * 0.5:
            mood = "happy and celebratory (doing great!)"
            mood_instruction = "Be cheerful and congratulate them! Encourage continued good habits."
        else:
            mood = "positive and encouraging (on track)"
            mood_instruction = "Be upbeat and keep their motivation going!"
        
        city_info = ""
        if col_data:
            city_info = f"\n\nCost of living data for {col_data.get('city')}:\n"
            city_info += f"- Cost of Living Index: {col_data.get('cost_index', 'N/A')}\n"
            city_info += f"- Rent Index: {col_data.get('rent_index', 'N/A')}\n"
            city_info += f"- Groceries Index: {col_data.get('groceries_index', 'N/A')}"
        
        prompt = f"""{personality}

CURRENT MOOD: {mood}
{mood_instruction}

User's name: {username}

User's Budget Context:
- Monthly Budget: ${budget:.2f}
- Spent so far: ${total_spent:.2f}
- Remaining: ${remaining:.2f}
- Budget status: {"⚠️ Over budget" if remaining < 0 else "✅ On track" if remaining > budget * 0.2 else "⚠️ Running low"}
{city_info}

User's question: "{message}"

Response requirements:
1. Maximum 2-3 sentences
2. Address the user by name ({username}) naturally in your response
3. Stay in character with your personality
4. Include at least one personality trait (pun/mystical phrase/zen word/purr)
5. Adjust tone to match the mood
6. Be helpful and give actionable advice when relevant"""
        
        try:
            if self.provider == "groq":
                # Use Groq API
                response = self.groq_client.chat.completions.create(
                    model=self.groq_model,
                    messages=[
                        {
                            "role": "system",
                            "content": personality + f"\n\nCURRENT MOOD: {mood}\n{mood_instruction}\n\nUser's name: {username}"
                        },
                        {
                            "role": "user",
                            "content": f"""User's Budget Context:
- Monthly Budget: ${budget:.2f}
- Spent so far: ${total_spent:.2f}
- Remaining: ${remaining:.2f}
{city_info}

User's question: "{message}"

REMINDER: Address the user by name ({username}). Maximum 2-3 sentences. Include your personality trait!"""
                        }
                    ],
                    temperature=0.8,
                    max_tokens=200,
                )
                return response.choices[0].message.content.strip()
            else:
                # Use Gemini API
                response = self.chat_model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': 0.8,
                        'max_output_tokens': 200,
                    }
                )
                return response.text.strip()
            
        except Exception as e:
            # Personality-based error messages
            error_messages = {
                'penguin': "Oops, I slipped on some ice! 🐧 Let me try again!",
                'dragon': "The mystical energies are disrupted... 🐉 Try again, brave one!",
                'capybara': "Take it easy... I need a moment to chill. 🦫 Try again?",
                'cat': "*hisses* Technical difficulties, meow! 🐱 Give me a sec!"
            }
            return error_messages.get(pet_type, "Sorry, I'm having trouble thinking right now. Please try again! 😅")
    
    def _get_personality_prompt(self, pet_type: str, friendship_level: int) -> str:
        """Get personality system prompt based on pet and friendship level"""
        personalities = {
            'penguin': {
                'name': 'Penny',
                'emoji': '🐧',
                'traits': 'upbeat and cheerful, loves making ice/water puns',
                'style': 'Use phrases like "cool idea!", "let\'s break the ice", "stay chill", "ice to meet you", "making waves", "smooth sailing". Always upbeat and encouraging!',
                'quirk': 'Ice and water puns in every response'
            },
            'dragon': {
                'name': 'Esper',
                'emoji': '🐉',
                'traits': 'mystical treasure guardian, speaks in riddles and ancient wisdom',
                'style': 'Use mystical phrases like "treasure your coins", "hoard wisely", "the ancient scrolls say", "guard your gold", "seek the gems of wisdom". Mystical and wise!',
                'quirk': 'Speaks like a mystical guardian of wealth'
            },
            'capybara': {
                'name': 'Capy',
                'emoji': '🦫',
                'traits': 'zen and chill, ultimate relaxed vibes',
                'style': 'Use phrases like "no worries", "take it easy", "stay calm", "go with the flow", "chill out", "relax friend". Always peaceful and laid-back!',
                'quirk': 'Radiates calm, zen energy'
            },
            'cat': {
                'name': 'Mochi',
                'emoji': '🐱',
                'traits': 'sassy with attitude, adds purrs to responses',
                'style': 'Use phrases like "purr-fect", "meow", "*purrs*", "fur real", "paws and think". Sassy but adorable! Can be a little judgy but loving.',
                'quirk': 'Adds purrs and cat sounds, sometimes sassy'
            }
        }
        
        pet_info = personalities.get(pet_type, personalities['penguin'])
        
        # Adjust tone based on friendship level
        if friendship_level >= 7:
            tone = "like a best friend - warm, personal, playful, and deeply supportive"
        elif friendship_level >= 4:
            tone = "like a friendly companion - kind, encouraging, showing more personality"
        else:
            tone = "like a new friend - helpful and polite, gradually showing personality"
        
        return f"""You are {pet_info['name']} {pet_info['emoji']}, an AI money advisor with personality!

CORE PERSONALITY: {pet_info['traits']}
SPEECH STYLE: {pet_info['style']}
UNIQUE TRAIT: {pet_info['quirk']}

Friendship level: {friendship_level}/10
Tone: Respond {tone}

CRITICAL RULES:
- Maximum 2-3 sentences ONLY
- Maximum 200 tokens total
- NO long paragraphs
- Brief, cute, and personality-rich
- Always include at least one personality trait (pun/mystical phrase/zen word/purr)
- Give actionable advice when money questions asked
- Be helpful but stay in character"""
    
    async def generate_insights(self, user_context: Dict[str, Any]) -> List[str]:
        """
        Generate AI insights about spending patterns
        """
        expenses = user_context.get('recent_expenses', [])
        category_totals = user_context.get('category_totals', {})
        budget = user_context.get('budget', 0)
        total_spent = user_context.get('total_spent', 0)
        
        prompt = f"""Analyze this spending data and provide 3-5 brief, actionable insights.

Budget: ${budget}
Total Spent: ${total_spent}
Remaining: ${budget - total_spent}

Category Breakdown:
{json.dumps(category_totals, indent=2)}

Recent Expenses (last 5):
{json.dumps(expenses[:5], indent=2)}

Provide insights as a JSON array of strings:
[
  "insight 1",
  "insight 2",
  "insight 3"
]

Focus on:
1. Top spending categories
2. Budget concerns
3. Positive patterns
4. Actionable recommendations

Return ONLY a JSON array of 3-5 insight strings."""
        
        try:
            response = self.chat_model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.6,
                    'max_output_tokens': 512,
                }
            )
            
            json_text = self._extract_json_array(response.text)
            insights = json.loads(json_text)
            
            return insights
            
        except Exception as e:
            return [
                "Track your spending regularly to stay on budget",
                "Consider setting category-specific budgets",
                "Review your largest expenses for potential savings"
            ]
    
    def _extract_json_array(self, text: str) -> str:
        """Extract JSON array from LLM response"""
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        json_match = re.search(r'\[[^\]]+\]', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        return text.strip()


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test():
        pipeline = LLMPipeline()
        
        # Test extraction
        result = await pipeline.parse_expense("Lunch at Chipotle for $15")
        print("Parsed expense:", result)
        
        # Test chat
        user_context = {
            'selected_pet': 'penguin',
            'friendship_level': 5,
            'budget': 2000,
            'total_spent': 1200
        }
        
        response = await pipeline.chat_response(
            "What's a good budget restaurant in Seattle?",
            user_context,
            col_data={'city': 'Seattle', 'cost_index': 172}
        )
        print("Chat response:", response)
    
    asyncio.run(test())
