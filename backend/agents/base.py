import os
import json
from typing import Dict, Any, Optional
import google.generativeai as genai

def call_gemini(prompt: str, system_instruction: Optional[str] = None, json_mode: bool = False) -> str:
    """
    Call Google Gemini model using official SDK.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("ERROR: GEMINI_API_KEY is missing from environment variables.")
        raise ValueError("GEMINI_API_KEY not found in environment.")
        
    genai.configure(api_key=api_key)
    
    # We will use gemini-1.5-flash or gemini-2.5-flash
    # Since gemini-1.5-flash is widely supported and standard, let's use gemini-1.5-flash as default, 
    # but try gemini-2.5-flash first since it's the latest and greatest.
    model_name = "gemini-1.5-flash"
    
    generation_config = {}
    if json_mode:
        generation_config["response_mime_type"] = "application/json"
        
    try:
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction,
            generation_config=generation_config
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error calling Gemini model {model_name}: {e}. Retrying with gemini-2.5-flash...")
        try:
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction=system_instruction,
                generation_config=generation_config
            )
            response = model.generate_content(prompt)
            return response.text
        except Exception as e2:
            print(f"All Gemini models failed: {e2}")
            raise e2
            
def parse_json_response(response_text: str) -> Dict[str, Any]:
    """
    Parse a JSON string from a model, stripping markdown block delimiters if present.
    """
    cleaned = response_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    return json.loads(cleaned)
