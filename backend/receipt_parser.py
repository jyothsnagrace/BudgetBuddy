"""
Receipt Parser using Groq LLM + Tesseract OCR
Extracts structured expense data from receipt images

Two-stage approach:
1. Tesseract OCR extracts text from image
2. Groq LLM parses text into structured data

Falls back to Gemini Vision if Tesseract is not available.
"""

import os
import json
import re
from typing import Dict, Any
from datetime import date
import io

# Try to import Groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("Warning: groq package not installed. Install with: pip install groq")

# Try to import Tesseract
try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
    # Try to set tesseract path for Windows
    try:
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    except:
        pass
except ImportError:
    TESSERACT_AVAILABLE = False
    print("Warning: pytesseract not installed. Install with: pip install pytesseract")
    print("Also install Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki")

# Fallback to Gemini Vision if needed
try:
    import google.generativeai as genai
    from PIL import Image
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Configure APIs
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GROQ_API_KEY and GROQ_AVAILABLE:
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    groq_client = None

if GEMINI_API_KEY and GEMINI_AVAILABLE:
    genai.configure(api_key=GEMINI_API_KEY)


class ReceiptParser:
    """Parse receipt images using Groq + Tesseract OCR (or Gemini Vision as fallback)"""
    
    def __init__(self):
        self.use_groq = GROQ_AVAILABLE and groq_client is not None
        self.use_tesseract = TESSERACT_AVAILABLE
        self.use_gemini = GEMINI_AVAILABLE and GEMINI_API_KEY is not None
        
        if self.use_gemini:
            self.vision_model = genai.GenerativeModel('gemini-2.5-flash')
        
        print(f"ReceiptParser initialized:")
        print(f"  - Groq: {'✓' if self.use_groq else '✗'}")
        print(f"  - Tesseract: {'✓' if self.use_tesseract else '✗'}")
        print(f"  - Gemini Vision: {'✓' if self.use_gemini else '✗'}")
    
    async def parse_receipt(self, image_data: bytes) -> Dict[str, Any]:
        """
        Parse receipt image and extract expense data
        
        Priority:
        1. Try Groq + Tesseract OCR (text-based parsing)
        2. Fall back to Gemini Vision (vision-based parsing)
        
        Args:
            image_data: Image bytes
            
        Returns:
            Parsed expense data
        """
        try:
            # Method 1: Groq + Tesseract (preferred for cost and speed)
            if self.use_groq and self.use_tesseract:
                try:
                    return await self._parse_with_groq_ocr(image_data)
                except Exception as e:
                    print(f"Groq+OCR failed: {e}, falling back to Gemini Vision")
            
            # Method 2: Gemini Vision (fallback)
            if self.use_gemini:
                return await self._parse_with_gemini_vision(image_data)
            
            # No methods available
            raise ValueError(
                "No parsing method available. Please install either:\n"
                "1. Groq + Tesseract: pip install groq pytesseract, and install Tesseract OCR\n"
                "2. Gemini: pip install google-generativeai and set GEMINI_API_KEY"
            )
            
        except Exception as e:
            raise ValueError(f"Receipt parsing failed: {str(e)}")
    
    async def _parse_with_groq_ocr(self, image_data: bytes) -> Dict[str, Any]:
        """Parse receipt using Tesseract OCR + Groq LLM"""
        from PIL import Image
        import io
        
        try:
            # Step 1: Extract text using Tesseract OCR
            image = Image.open(io.BytesIO(image_data))
            extracted_text = pytesseract.image_to_string(image)
            
            if not extracted_text or len(extracted_text.strip()) < 10:
                raise ValueError("Could not extract text from image. Image may be too blurry or corrupted.")
            
            print(f"OCR extracted {len(extracted_text)} characters")
            
            # Step 2: Parse text using Groq LLM
            parse_prompt = f"""Parse this receipt text and extract structured expense information.

Receipt Text:
{extracted_text}

Extract and return ONLY valid JSON in this exact format:
{{
  "amount": <total_amount_as_number>,
  "category": "<category>",
  "description": "<merchant_name - items>",
  "date": "YYYY-MM-DD",
  "merchant": "<merchant_name>"
}}

Category selection (choose the best match):
- Restaurant, grocery, cafe, food → "Food"
- Gas station, uber, lyft, taxi, parking → "Transportation"
- Movie, concert, games → "Entertainment"
- Retail, clothing, electronics, amazon → "Shopping"
- Utilities, phone, internet → "Bills"
- Pharmacy, doctor, hospital → "Healthcare"
- School, books, courses → "Education"
- Everything else → "Other"

Rules:
- Use the TOTAL amount (not subtotal)
- If date not found, use today: {date.today().isoformat()}
- Return ONLY the JSON object, no explanation or markdown
- Amount must be a number without $ or commas"""

            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a receipt parser. Extract structured data and return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": parse_prompt
                    }
                ],
                temperature=0.1,
                max_tokens=300,
            )
            
            llm_response = response.choices[0].message.content
            print(f"Groq LLM response: {llm_response[:200]}")
            
            # Parse JSON from response
            json_text = self._extract_json(llm_response)
            parsed_data = json.loads(json_text)
            
            # Validate and clean
            parsed_data = self._validate_parsed_data(parsed_data)
            
            return parsed_data
            
        except Exception as groq_error:
            print(f"[Groq+OCR Error] {type(groq_error).__name__}: {str(groq_error)}")
            raise ValueError(f"Text extraction failed: {str(groq_error)}")
    
    async def _parse_with_gemini_vision(self, image_data: bytes) -> Dict[str, Any]:
        """Parse receipt using Gemini Vision API (fallback method)"""
        # Convert image bytes to base64
        import base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Determine image format
        mime_type = 'image/jpeg'
        if image_data.startswith(b'\x89PNG'):
            mime_type = 'image/png'
        elif image_data.startswith(b'GIF'):
            mime_type = 'image/gif'
        elif image_data.startswith(b'RIFF') and image_data[8:12] == b'WEBP':
            mime_type = 'image/webp'
        
        prompt = f"""Analyze this receipt image and extract structured expense data.

Extract and return ONLY a JSON object with these exact fields:
- amount: The TOTAL amount paid (number only, no $ symbol or commas)
- category: Best matching category from [Food, Transportation, Entertainment, Shopping, Bills, Healthcare, Education, Other]
- description: Brief description (merchant name + key items, max 100 chars)
- date: Date in YYYY-MM-DD format (use today if not visible: {date.today().isoformat()})
- merchant: Store/restaurant name

Category mapping:
- Restaurant, grocery, cafe, food → "Food"
- Gas station, uber, lyft, taxi, parking → "Transportation"
- Movie, concert, games → "Entertainment"
- Retail, clothing, electronics, amazon → "Shopping"
- Utilities, phone, internet → "Bills"
- Pharmacy, doctor, hospital → "Healthcare"
- School, books, courses → "Education"
- Everything else → "Other"

Return ONLY valid JSON like this:
{{
  "amount": 13.32,
  "category": "Food",
  "description": "The Breakfast Club - Chicken waffle meal",
  "date": "2020-03-04",
  "merchant": "The Breakfast Club"
}}

Be accurate with the total amount. Return ONLY the JSON object, no explanations."""

        try:
            # Use Gemini with inline image data
            response = self.vision_model.generate_content(
                [
                    {
                        "mime_type": mime_type,
                        "data": image_base64
                    },
                    prompt
                ],
                generation_config={
                    'temperature': 0.1,
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
            raise ValueError(f"Gemini Vision parsing failed: {str(e)}")
    
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
