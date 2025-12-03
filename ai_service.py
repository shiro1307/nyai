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