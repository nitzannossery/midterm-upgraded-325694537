"""
Google Gemini API Client
Handles all LLM interactions using Google's Gemini API
"""
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from app.config import settings

class GoogleLLMClient:
    """Client for Google Gemini API."""
    
    def __init__(self):
        """Initialize Google Gemini client."""
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY not set in environment variables")
        
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel(settings.google_model)
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text using Google Gemini.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt (Gemini uses it differently)
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
        
        Returns:
            Generated text
        """
        try:
            # Combine system prompt and user prompt if provided
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Configure generation parameters
            generation_config = {
                "temperature": temperature,
            }
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            
            # Generate response
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            return response.text
            
        except Exception as e:
            raise Exception(f"Google API error: {str(e)}")
    
    def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.0
    ) -> Dict[str, Any]:
        """
        Generate structured output (JSON-like) from Gemini.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (use 0.0 for deterministic)
        
        Returns:
            Dictionary with structured output
        """
        # Add JSON formatting instruction
        json_prompt = f"{prompt}\n\nPlease respond in valid JSON format."
        
        response_text = self.generate(
            prompt=json_prompt,
            system_prompt=system_prompt,
            temperature=temperature
        )
        
        # Try to parse JSON from response
        import json
        try:
            # Extract JSON if wrapped in markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            return json.loads(response_text)
        except json.JSONDecodeError:
            # If not valid JSON, return as text
            return {"text": response_text}
