"""
Receipt Parser using Gemini Vision API
Extracts structured expense data from receipt images
"""

import os
import json
import re
from typing import Dict, Any
from datetime import date
import google.generativeai as genai
from PIL import Image
import io

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)


class ReceiptParser:
    """Parse receipt images using Gemini Vision"""
    
    def __init__(self):
        self.vision_model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def parse_receipt(self, image_data: bytes) -> Dict[str, Any]:
        """
        Parse receipt image and extract expense data
        
        Args:
            image_data: Image bytes
            
        Returns:
            Parsed expense data
        """
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            
            # Stage 1: Extract text from image
            extracted_text = await self._extract_text(image)
            
            # Stage 2: Parse structured data
            parsed_data = await self._parse_structure(extracted_text)
            
            return parsed_data
            
        except Exception as e:
            raise ValueError(f"Receipt parsing failed: {str(e)}")
    
    async def _extract_text(self, image: Image.Image) -> str:
        """Extract text from receipt image using Vision API"""
        
        prompt = """Analyze this receipt image and extract all visible text.

Pay special attention to:
- Total amount
- Store/merchant name
- Date
- Individual items and prices
- Tax
- Payment method

Return a structured text summary."""
        
        try:
            response = self.vision_model.generate_content(
                [prompt, image],
                generation_config={
                    'temperature': 0.2,
                    'max_output_tokens': 1024,
                }
            )
            
            return response.text
            
        except Exception as e:
            raise ValueError(f"Text extraction failed: {str(e)}")
    
    async def _parse_structure(self, extracted_text: str) -> Dict[str, Any]:
        """Parse extracted text into structured expense data"""
        
        prompt = f"""Parse this receipt text into structured expense data.

Receipt text:
{extracted_text}

Extract and return ONLY a JSON object with these fields:
- amount: The total amount paid (number only, no $ symbol)
- category: Best matching category from [Food, Transportation, Entertainment, Shopping, Bills, Healthcare, Education, Other]
- description: Brief description (merchant name + main items)
- date: Date in YYYY-MM-DD format (use today if not found: {date.today().isoformat()})
- metadata: Additional info like tax, items list, payment method (optional)

Category mapping guidelines:
- Restaurant, grocery, food → "Food"
- Gas station, uber, parking → "Transportation"
- Movie, concert, entertainment venue → "Entertainment"
- Retail stores, clothing, electronics → "Shopping"
- Utilities, phone, subscriptions → "Bills"
- Pharmacy, doctor, hospital → "Healthcare"
- Bookstore, school, courses → "Education"
- Everything else → "Other"

Return ONLY valid JSON:
{{
  "amount": <number>,
  "category": "<category>",
  "description": "<description>",
  "date": "<YYYY-MM-DD>",
  "metadata": {{
    "merchant": "<name>",
    "items": ["item1", "item2"],
    "tax": <number>,
    "payment_method": "<method>"
  }}
}}

Return ONLY JSON, no other text."""
        
        try:
            response = self.vision_model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.3,
                    'max_output_tokens': 512,
                }
            )
            
            # Extract and parse JSON
            json_text = self._extract_json(response.text)
            parsed_data = json.loads(json_text)
            
            # Validate and clean
            parsed_data = self._validate_parsed_data(parsed_data)
            
            return parsed_data
            
        except Exception as e:
            raise ValueError(f"Structure parsing failed: {str(e)}")
    
    def _validate_parsed_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean parsed data"""
        # Ensure required fields
        if 'amount' not in data:
            raise ValueError("Amount not found in receipt")
        
        if 'category' not in data:
            data['category'] = 'Other'
        
        if 'date' not in data:
            data['date'] = date.today().isoformat()
        
        if 'description' not in data:
            data['description'] = 'Receipt expense'
        
        # Clean amount
        data['amount'] = float(data['amount'])
        
        # Validate category
        valid_categories = [
            'Food', 'Transportation', 'Entertainment', 
            'Shopping', 'Bills', 'Healthcare', 'Education', 'Other'
        ]
        
        if data['category'] not in valid_categories:
            data['category'] = 'Other'
        
        # Validate date format
        try:
            from datetime import datetime
            datetime.strptime(data['date'], '%Y-%m-%d')
        except ValueError:
            data['date'] = date.today().isoformat()
        
        return data
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from LLM response"""
        # Remove markdown code blocks
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Find JSON object
        json_match = re.search(r'\{[^}]+\}', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        return text.strip()
    
    async def extract_multiple_items(self, image_data: bytes) -> list[Dict[str, Any]]:
        """
        Extract multiple expense items from a single receipt
        Useful for itemized receipts
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            
            prompt = """Parse this receipt and extract EACH item as a separate expense.

For each item, extract:
- Item name/description
- Price
- Category (best guess from item name)

Return a JSON array of expense objects:
[
  {{
    "description": "Item 1",
    "amount": 10.50,
    "category": "Food"
  }},
  {{
    "description": "Item 2",
    "amount": 5.00,
    "category": "Food"
  }}
]

Return ONLY the JSON array, no other text."""
            
            response = self.vision_model.generate_content(
                [prompt, image],
                generation_config={
                    'temperature': 0.3,
                    'max_output_tokens': 1024,
                }
            )
            
            # Extract and parse JSON array
            json_text = self._extract_json_array(response.text)
            items = json.loads(json_text)
            
            # Add today's date to each item
            today = date.today().isoformat()
            for item in items:
                item['date'] = today
            
            return items
            
        except Exception as e:
            raise ValueError(f"Multi-item extraction failed: {str(e)}")
    
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
        parser = ReceiptParser()
        
        # Test with sample image (replace with actual receipt image)
        with open("sample_receipt.jpg", "rb") as f:
            image_data = f.read()
        
        result = await parser.parse_receipt(image_data)
        print("Parsed receipt:", json.dumps(result, indent=2))
    
    # Uncomment to test
    # asyncio.run(test())
    
    print("Receipt parser module loaded successfully")
