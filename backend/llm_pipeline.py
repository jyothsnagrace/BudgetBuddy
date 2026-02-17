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

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
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
        print(f"[LLMPipeline] Initializing with gemini-2.5-flash")
        self.extraction_model = genai.GenerativeModel('gemini-2.5-flash')
        print(f"[LLMPipeline] Extraction model: {self.extraction_model._model_name}")
        self.normalization_model = genai.GenerativeModel('gemini-2.5-flash')
        self.chat_model = genai.GenerativeModel('gemini-2.5-flash')
        
    def health_check(self) -> bool:
        """Check if LLM service is available"""
        try:
            # Simple test generation
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
            response = self.extraction_model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.3,  # Low temperature for consistency
                    'max_output_tokens': 256,
                }
            )
            
            # Extract JSON from response
            json_text = self._extract_json(response.text)
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
            response = self.normalization_model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.2,  # Very low temperature for consistency
                    'max_output_tokens': 256,
                }
            )
            
            # Extract JSON from response
            json_text = self._extract_json(response.text)
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
        City-aware, context-aware, personality-based
        """
        # Get pet personality
        pet_type = user_context.get('selected_pet', 'penguin')
        friendship_level = user_context.get('friendship_level', 1)
        
        personality = self._get_personality_prompt(pet_type, friendship_level)
        
        # Build context prompt
        budget = user_context.get('budget', 0)
        total_spent = user_context.get('total_spent', 0)
        remaining = budget - total_spent
        
        city_info = ""
        if col_data:
            city_info = f"\n\nCost of living data for {col_data.get('city')}:\n"
            city_info += f"- Cost of Living Index: {col_data.get('cost_index', 'N/A')}\n"
            city_info += f"- Rent Index: {col_data.get('rent_index', 'N/A')}\n"
            city_info += f"- Groceries Index: {col_data.get('groceries_index', 'N/A')}"
        
        prompt = f"""{personality}

User's Budget Context:
- Monthly Budget: ${budget:.2f}
- Spent so far: ${total_spent:.2f}
- Remaining: ${remaining:.2f}
- Budget status: {"⚠️ Over budget" if remaining < 0 else "✅ On track" if remaining > budget * 0.2 else "⚠️ Running low"}
{city_info}

User's question: "{message}"

Provide a brief, helpful, and personality-appropriate response. Keep it under 100 words.
Be conversational, use the pet's personality, and give actionable advice when relevant."""
        
        try:
            response = self.chat_model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.8,  # Higher for creativity
                    'max_output_tokens': 200,
                }
            )
            
            return response.text.strip()
            
        except Exception as e:
            return f"Sorry, I'm having trouble thinking right now. Please try again! 😅"
    
    def _get_personality_prompt(self, pet_type: str, friendship_level: int) -> str:
        """Get personality system prompt based on pet and friendship level"""
        personalities = {
            'penguin': {
                'name': 'Penny',
                'emoji': '🐧',
                'traits': 'friendly, warm, practical, encouraging'
            },
            'dragon': {
                'name': 'Esper',
                'emoji': '🐉',
                'traits': 'wise, enthusiastic, mystical, inspiring'
            },
            'capybara': {
                'name': 'Capy',
                'emoji': '🦫',
                'traits': 'calm, thoughtful, relaxed, zen-like'
            },
            'cat': {
                'name': 'Mochi',
                'emoji': '🐱',
                'traits': 'playful, sweet, charming, sometimes sassy'
            }
        }
        
        pet_info = personalities.get(pet_type, personalities['penguin'])
        
        # Adjust tone based on friendship level
        if friendship_level >= 7:
            tone = "like a close friend - warm, personal, and supportive"
        elif friendship_level >= 4:
            tone = "like a friendly companion - helpful and encouraging"
        else:
            tone = "like a helpful assistant - polite and informative"
        
        return f"""You are {pet_info['name']} the {pet_type.title()} {pet_info['emoji']}, a budgeting assistant.

Your personality: {pet_info['traits']}
Friendship level: {friendship_level}/10
Tone: Respond {tone}

Keep responses:
- Brief (under 100 words)
- Cute and personality-appropriate
- Actionable and helpful
- Include relevant emoji occasionally"""
    
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
