# Receipt Parser Setup Guide

The receipt parser has been updated to support multiple parsing methods with automatic fallback:

## Parsing Methods

### Method 1: Groq + Tesseract OCR (Recommended)
**Advantages:**
- Cost-effective (Groq has generous free tier)
- Fast processing
- Good accuracy for clear receipts

**Setup:**

1. **Install Python packages:**
   ```bash
   pip install groq pytesseract pillow
   ```

2. **Install Tesseract OCR:**
   - **Windows:** Download and install from https://github.com/UB-Mannheim/tesseract/wiki
     - Add to PATH or the code will auto-detect at `C:\Program Files\Tesseract-OCR\tesseract.exe`
   - **Mac:** `brew install tesseract`
   - **Linux:** `sudo apt-get install tesseract-ocr`

3. **Get Groq API Key:**
   - Visit https://console.groq.com/
   - Create account and get your API key
   - Add to `.env`:
     ```
     GROQ_API_KEY=your_api_key_here
     ```

### Method 2: Gemini Vision (Fallback)
**Advantages:**
- No OCR installation needed
- Works well with blurry/complex receipts
- Single-step vision parsing

**Setup:**

1. **Use existing setup:**
   ```bash
   pip install google-generativeai pillow
   ```

2. **Gemini API key already configured in `.env`:**
   ```
   GEMINI_API_KEY=AIzaSyBsZovmJG_i_3aWpNZCf-Y8nYxcfTEgclo
   ```

## How It Works

The parser automatically tries methods in order:

1. **Primary:** Groq + Tesseract
   - Extracts text from image using OCR
   - Parses text with Groq LLM (llama-3.1-8b-instant)
   
2. **Fallback:** Gemini Vision
   - Direct image analysis
   - Vision-based text extraction and parsing

If the primary method fails, it automatically falls back to the next available method.

## Testing

Test the receipt parser:

```python
import asyncio
from receipt_parser import ReceiptParser

async def test():
    parser = ReceiptParser()
    
    with open("sample_receipt.jpg", "rb") as f:
        image_data = f.read()
    
    result = await parser.parse_receipt(image_data)
    print(result)

asyncio.run(test())
```

## API Endpoint

The `/api/parse-receipt` endpoint automatically uses the best available method:

```bash
curl -X POST http://localhost:8000/api/parse-receipt \
  -F "file=@receipt.jpg"
```

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WEBP (.webp)

## Troubleshooting

### Tesseract not found
**Error:** `TesseractNotFoundError`

**Solution:**
- Windows: Install from https://github.com/UB-Mannheim/tesseract/wiki
- Ensure it's in PATH or at `C:\Program Files\Tesseract-OCR\tesseract.exe`

### Groq API errors
**Error:** `AuthenticationError`

**Solution:**
- Check GROQ_API_KEY in `.env`
- Verify key is valid at https://console.groq.com/

### Poor OCR accuracy
**Solution:**
- Ensure receipt image is clear and well-lit
- Try higher resolution image
- Will automatically fall back to Gemini Vision

## Cost Comparison

| Method | Cost | Speed | Accuracy |
|--------|------|-------|----------|
| Groq + Tesseract | Free (generous tier) | Fast | Good for clear receipts |
| Gemini Vision | $0.001/request | Medium | Excellent for all receipts |

## Dependencies

```
groq==0.4.2              # Groq LLM API
pytesseract==0.3.10      # Python wrapper for Tesseract OCR
pillow==10.2.0           # Image processing
google-generativeai==0.4.0  # Gemini Vision (fallback)
```
