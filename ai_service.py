import os
from groq import Groq

# Initialize Groq client once (outside the function)
client = Groq(
    api_key="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",
)

def call_ai_api(prompt):
    """
    Calls Groq API with Llama model
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
            max_tokens=500,
            temperature=0.7,
        )
        
        return chat_completion.choices[0].message.content
        
    except Exception as e:
        return f"Error calling AI: {str(e)}"

# Add this new function at the end of the file

def get_risk_score(text):
    """
    Analyzes text and returns a risk score from 0-100
    0-30 = Low Risk, 31-60 = Medium Risk, 61-100 = High Risk
    """
    # Limit text to avoid token limits
    text_sample = text[:1000] if len(text) > 1000 else text
    
    prompt = f"""Analyze this legal document and provide ONLY a numerical risk score from 0-100.

Risk Scale:
- 0-30: Low Risk (minimal issues, standard terms)
- 31-60: Medium Risk (some concerning clauses, review recommended)
- 61-100: High Risk (serious issues, legal review essential)

Consider: unfavorable terms, missing protections, vague language, one-sided clauses, liability issues.

Document excerpt:
{text_sample}

Respond with ONLY the risk score number (e.g., "45" or "72")."""
    
    try:
        response = call_ai_api(prompt)
        # Extract first number found in response
        import re
        numbers = re.findall(r'\d+', response)
        if numbers:
            score = int(numbers[0])
            # Ensure score is within valid range
            return max(0, min(100, score))
        return 50  # Default to medium risk if parsing fails
    except Exception as e:
        print(f"Error calculating risk score: {e}")
        return 50  # Default to medium risk on error