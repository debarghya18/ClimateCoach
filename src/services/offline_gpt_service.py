"""
Offline GPT Service for ClimateCoach
Enables AI language model usage without internet connectivity
"""

import torch
import os
import logging
from transformers import GPT2LMHeadModel, GPT2Tokenizer, pipeline
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)

class OfflineGPTService:
    """
    Service for offline GPT capabilities using transformers
    """
    
    def __init__(self, model_name: str = "gpt2", cache_dir: str = "./models"):
        """
        Initialize offline GPT service
        
        Args:
            model_name: Name of the model to use
            cache_dir: Directory to cache models
        """
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Ensure cache directory exists
        os.makedirs(cache_dir, exist_ok=True)
        
        # Load model and tokenizer
        self._load_model()
        
        # Climate-specific prompts
        self.climate_prompts = {
            "transport": "How can I reduce my carbon footprint from transportation?",
            "energy": "What are the best ways to save energy at home?",
            "food": "How can I eat more sustainably?",
            "shopping": "What are eco-friendly shopping practices?",
            "general": "How can I live more sustainably?"
        }
        
        logger.info(f"Offline GPT Service initialized with model: {model_name}")
    
    def _load_model(self):
        """Load GPT model and tokenizer"""
        try:
            self.tokenizer = GPT2Tokenizer.from_pretrained(
                self.model_name,
                cache_dir=self.cache_dir
            )
            self.model = GPT2LMHeadModel.from_pretrained(
                self.model_name,
                cache_dir=self.cache_dir
            )
            
            # Add padding token if it doesn't exist
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Move model to device
            self.model.to(self.device)
            self.model.eval()
            
            # Create text generation pipeline
            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1
            )
            
            logger.info("GPT model and tokenizer loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading GPT model: {e}")
            self.model = None
            self.tokenizer = None
            self.generator = None
    
    def generate_climate_advice(self, user_input: str, category: str = "general") -> str:
        """
        Generate climate advice based on user input
        
        Args:
            user_input: User's question or input
            category: Category of advice (transport, energy, food, shopping, general)
            
        Returns:
            Generated climate advice text
        """
        if not self.generator:
            return self._get_fallback_advice(category)
        
        try:
            # Create context-aware prompt
            prompt = self._create_climate_prompt(user_input, category)
            
            # Generate response
            response = self.generator(
                prompt,
                max_length=200,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Extract generated text
            generated_text = response[0]['generated_text']
            
            # Clean up the response
            advice = self._clean_generated_text(generated_text, prompt)
            
            return advice
            
        except Exception as e:
            logger.error(f"Error generating climate advice: {e}")
            return self._get_fallback_advice(category)
    
    def _create_climate_prompt(self, user_input: str, category: str) -> str:
        """Create a climate-focused prompt"""
        base_prompt = self.climate_prompts.get(category, self.climate_prompts["general"])
        
        # Create context-aware prompt
        prompt = f"""As an expert climate advisor, provide practical advice on reducing carbon footprint.

Question: {user_input}
Context: {base_prompt}

Advice:"""
        
        return prompt
    
    def _clean_generated_text(self, generated_text: str, original_prompt: str) -> str:
        """Clean and format generated text"""
        # Remove the original prompt from generated text
        advice = generated_text.replace(original_prompt, "").strip()
        
        # Take only the first paragraph or sentence
        sentences = advice.split('.')
        if len(sentences) > 0:
            # Take first few sentences
            clean_advice = '. '.join(sentences[:3]).strip()
            if clean_advice and not clean_advice.endswith('.'):
                clean_advice += '.'
            return clean_advice
        
        return advice[:300] + "..." if len(advice) > 300 else advice
    
    def _get_fallback_advice(self, category: str) -> str:
        """Provide fallback advice when GPT is not available"""
        fallback_advice = {
            "transport": "Consider using public transportation, cycling, or walking for short trips. Carpooling and remote work can also significantly reduce your transport emissions.",
            "energy": "Switch to LED bulbs, use a programmable thermostat, unplug devices when not in use, and consider renewable energy sources like solar panels.",
            "food": "Eat more plant-based meals, buy local and seasonal produce, reduce food waste, and choose organic options when possible.",
            "shopping": "Buy only what you need, choose durable products, shop second-hand, support eco-friendly brands, and reduce packaging waste.",
            "general": "Focus on the three R's: Reduce, Reuse, Recycle. Small daily changes in energy use, transportation, and consumption can make a big difference."
        }
        
        return fallback_advice.get(category, fallback_advice["general"])
    
    def get_personalized_recommendations(self, user_profile: Dict) -> List[str]:
        """
        Generate personalized recommendations based on user profile
        
        Args:
            user_profile: Dictionary containing user information
            
        Returns:
            List of personalized recommendations
        """
        recommendations = []
        
        # Analyze user profile
        transport_mode = user_profile.get('transport_preference', 'car')
        diet_type = user_profile.get('diet_type', 'omnivore')
        energy_usage = user_profile.get('energy_usage', 'medium')
        
        # Generate recommendations based on profile
        if transport_mode == 'car':
            transport_advice = self.generate_climate_advice(
                "I mainly drive a car for transportation",
                "transport"
            )
            recommendations.append(transport_advice)
        
        if diet_type == 'omnivore':
            food_advice = self.generate_climate_advice(
                "I eat meat regularly",
                "food"
            )
            recommendations.append(food_advice)
        
        if energy_usage == 'high':
            energy_advice = self.generate_climate_advice(
                "I use a lot of energy at home",
                "energy"
            )
            recommendations.append(energy_advice)
        
        return recommendations
    
    def batch_generate_advice(self, questions: List[str]) -> List[str]:
        """
        Generate advice for multiple questions in batch
        
        Args:
            questions: List of questions
            
        Returns:
            List of advice responses
        """
        advice_list = []
        
        for question in questions:
            # Determine category based on keywords
            category = self._categorize_question(question)
            advice = self.generate_climate_advice(question, category)
            advice_list.append(advice)
        
        return advice_list
    
    def _categorize_question(self, question: str) -> str:
        """Categorize question based on keywords"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['transport', 'car', 'drive', 'bus', 'train']):
            return "transport"
        elif any(word in question_lower for word in ['energy', 'electricity', 'heating', 'cooling']):
            return "energy"
        elif any(word in question_lower for word in ['food', 'eat', 'diet', 'meal']):
            return "food"
        elif any(word in question_lower for word in ['shop', 'buy', 'purchase']):
            return "shopping"
        else:
            return "general"
    
    def save_model_cache(self) -> bool:
        """Save model to cache for offline use"""
        try:
            if self.model and self.tokenizer:
                self.model.save_pretrained(self.cache_dir)
                self.tokenizer.save_pretrained(self.cache_dir)
                logger.info("Model cache saved successfully")
                return True
        except Exception as e:
            logger.error(f"Error saving model cache: {e}")
        
        return False

# Example usage
if __name__ == "__main__":
    offline_gpt = OfflineGPTService()
    
    # Test generation
    advice = offline_gpt.generate_climate_advice(
        "How can I reduce my carbon footprint from daily commuting?",
        "transport"
    )
    print("Generated Advice:", advice)
