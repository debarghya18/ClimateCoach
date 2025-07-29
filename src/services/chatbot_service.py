"""
Chatbot Service for ClimateCoach
Integrates with OpenAI to provide conversational AI capabilities.
"""

import openai
import os
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class ChatbotService:
    """
    Service for interacting with OpenAI's GPT models to create a chatbot.
    """
    
    def __init__(self, openai_api_key: str):
        self.api_key = openai_api_key
        openai.api_key = self.api_key

    def generate_response(self, prompt: str, user_context: Dict = None) -> str:
        """
        Generate a response to a given prompt using OpenAI's completion API.
        """
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=150,
                temperature=0.7
            )
            return response.choices[0].text.strip()
        except Exception as e:
            logger.error(f"Error generating chatbot response: {e}")
            return "I'm sorry, but I couldn't process your request right now. Please try again later."

# Example chatbot interaction
if __name__ == "__main__":
    chatbot_service = ChatbotService(openai_api_key="YOUR_OPENAI_API_KEY")
    user_input = "How can I reduce my carbon footprint in daily transportation?"
    response = chatbot_service.generate_response(user_input)
    print("Chatbot Response:", response)
