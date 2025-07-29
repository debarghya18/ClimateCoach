"""
Sentiment and Motivation Scoring Service for ClimateCoach
Uses RoBERTa and BERT for contextual sentiment analysis
"""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import numpy as np
import logging
from typing import Dict, List, Any, Optional
import os

logger = logging.getLogger(__name__)

class SentimentMotivationService:
    """
    Service for analyzing sentiment and motivation scores using transformer models
    """
    
    def __init__(self, model_name: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"):
        """
        Initialize sentiment and motivation scoring service
        
        Args:
            model_name: Pre-trained model name for sentiment analysis
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load sentiment analysis pipeline
        self._load_sentiment_model()
        
        # Climate-specific motivation keywords
        self.motivation_keywords = {
            'high_motivation': [
                'excited', 'motivated', 'committed', 'determined', 'passionate',
                'inspired', 'dedicated', 'eager', 'enthusiastic', 'ready'
            ],
            'medium_motivation': [
                'interested', 'willing', 'considering', 'thinking', 'planning',
                'hoping', 'trying', 'working', 'attempting', 'exploring'
            ],
            'low_motivation': [
                'reluctant', 'hesitant', 'unsure', 'doubtful', 'confused',
                'overwhelmed', 'difficult', 'challenging', 'impossible', 'frustrated'
            ]
        }
        
        logger.info(f"Sentiment and Motivation Service initialized with model: {model_name}")
    
    def _load_sentiment_model(self):
        """Load RoBERTa sentiment analysis model"""
        try:
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                tokenizer=self.model_name,
                device=0 if self.device == "cuda" else -1
            )
            logger.info("Sentiment analysis model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading sentiment model: {e}")
            self.sentiment_pipeline = None
    
    def analyze_sentiment(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze sentiment of given texts
        
        Args:
            texts: List of text strings to analyze
            
        Returns:
            List of sentiment analysis results
        """
        if not self.sentiment_pipeline:
            return self._get_fallback_sentiment(texts)
        
        try:
            results = []
            for text in texts:
                # Get sentiment prediction
                sentiment_result = self.sentiment_pipeline(text)[0]
                
                # Normalize labels
                normalized_sentiment = self._normalize_sentiment_label(sentiment_result['label'])
                
                results.append({
                    'text': text,
                    'sentiment': normalized_sentiment,
                    'confidence': sentiment_result['score'],
                    'raw_label': sentiment_result['label']
                })
            
            logger.info(f"Analyzed sentiment for {len(texts)} texts")
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return self._get_fallback_sentiment(texts)
    
    def _normalize_sentiment_label(self, label: str) -> str:
        """Normalize sentiment labels to consistent format"""
        label_lower = label.lower()
        
        if 'positive' in label_lower or 'pos' in label_lower:
            return 'positive'
        elif 'negative' in label_lower or 'neg' in label_lower:
            return 'negative'
        else:
            return 'neutral'
    
    def calculate_motivation_score(self, text: str) -> Dict[str, Any]:
        """
        Calculate motivation score based on text content
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary containing motivation analysis
        """
        try:
            text_lower = text.lower()
            
            # Count motivation keywords
            high_count = sum(1 for word in self.motivation_keywords['high_motivation'] 
                           if word in text_lower)
            medium_count = sum(1 for word in self.motivation_keywords['medium_motivation'] 
                             if word in text_lower)
            low_count = sum(1 for word in self.motivation_keywords['low_motivation'] 
                          if word in text_lower)
            
            # Calculate total keyword matches
            total_matches = high_count + medium_count + low_count
            
            if total_matches == 0:
                # Use sentiment as fallback
                sentiment_result = self.analyze_sentiment([text])[0]
                if sentiment_result['sentiment'] == 'positive':
                    motivation_level = 'medium'
                    motivation_score = 0.6
                elif sentiment_result['sentiment'] == 'negative':
                    motivation_level = 'low'
                    motivation_score = 0.3
                else:
                    motivation_level = 'medium'
                    motivation_score = 0.5
            else:
                # Calculate weighted motivation score
                weighted_score = (high_count * 1.0 + medium_count * 0.6 + low_count * 0.2) / total_matches
                
                if weighted_score >= 0.7:
                    motivation_level = 'high'
                elif weighted_score >= 0.4:
                    motivation_level = 'medium'
                else:
                    motivation_level = 'low'
                
                motivation_score = weighted_score
            
            return {
                'text': text,
                'motivation_level': motivation_level,
                'motivation_score': motivation_score,
                'keyword_matches': {
                    'high': high_count,
                    'medium': medium_count,
                    'low': low_count
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating motivation score: {e}")
            return {
                'text': text,
                'motivation_level': 'medium',
                'motivation_score': 0.5,
                'keyword_matches': {'high': 0, 'medium': 0, 'low': 0}
            }
    
    def analyze_climate_engagement(self, user_messages: List[str]) -> Dict[str, Any]:
        """
        Analyze user's climate engagement based on messages
        
        Args:
            user_messages: List of user messages/responses
            
        Returns:
            Comprehensive engagement analysis
        """
        if not user_messages:
            return self._get_default_engagement()
        
        try:
            # Analyze sentiment for all messages
            sentiment_results = self.analyze_sentiment(user_messages)
            
            # Calculate motivation scores
            motivation_results = [self.calculate_motivation_score(msg) for msg in user_messages]
            
            # Aggregate results
            positive_count = sum(1 for r in sentiment_results if r['sentiment'] == 'positive')
            negative_count = sum(1 for r in sentiment_results if r['sentiment'] == 'negative')
            neutral_count = len(sentiment_results) - positive_count - negative_count
            
            avg_sentiment_confidence = np.mean([r['confidence'] for r in sentiment_results])
            avg_motivation_score = np.mean([r['motivation_score'] for r in motivation_results])
            
            # Determine overall engagement level
            if avg_motivation_score >= 0.7 and positive_count >= len(user_messages) * 0.6:
                engagement_level = 'high'
            elif avg_motivation_score >= 0.4 and positive_count >= len(user_messages) * 0.3:
                engagement_level = 'medium'
            else:
                engagement_level = 'low'
            
            return {
                'engagement_level': engagement_level,
                'avg_motivation_score': round(avg_motivation_score, 3),
                'avg_sentiment_confidence': round(avg_sentiment_confidence, 3),
                'sentiment_distribution': {
                    'positive': positive_count,
                    'negative': negative_count,
                    'neutral': neutral_count
                },
                'total_messages': len(user_messages),
                'recommendations': self._get_engagement_recommendations(engagement_level)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing climate engagement: {e}")
            return self._get_default_engagement()
    
    def _get_engagement_recommendations(self, engagement_level: str) -> List[str]:
        """Get recommendations based on engagement level"""
        recommendations = {
            'high': [
                "Great enthusiasm! Consider becoming a climate advocate in your community.",
                "Share your sustainable practices with friends and family.",
                "Set ambitious carbon reduction goals and track your progress."
            ],
            'medium': [
                "You're on the right track! Try setting weekly sustainability challenges.",
                "Connect with local environmental groups for motivation.",
                "Focus on one area (transport, energy, food) to build momentum."
            ],
            'low': [
                "Start small with easy wins like switching to LED bulbs.",
                "Find climate actions that align with your interests and values.",
                "Consider the co-benefits: saving money, improving health, etc."
            ]
        }
        
        return recommendations.get(engagement_level, recommendations['medium'])
    
    def _get_fallback_sentiment(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Provide fallback sentiment analysis when model is not available"""
        results = []
        for text in texts:
            # Simple keyword-based sentiment
            text_lower = text.lower()
            positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'like', 'happy']
            negative_words = ['bad', 'terrible', 'hate', 'dislike', 'awful', 'horrible', 'sad']
            
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                sentiment = 'positive'
                confidence = 0.7
            elif negative_count > positive_count:
                sentiment = 'negative'
                confidence = 0.7
            else:
                sentiment = 'neutral'
                confidence = 0.5
            
            results.append({
                'text': text,
                'sentiment': sentiment,
                'confidence': confidence,
                'raw_label': sentiment
            })
        
        return results
    
    def _get_default_engagement(self) -> Dict[str, Any]:
        """Get default engagement analysis"""
        return {
            'engagement_level': 'medium',
            'avg_motivation_score': 0.5,
            'avg_sentiment_confidence': 0.5,
            'sentiment_distribution': {'positive': 1, 'negative': 0, 'neutral': 1},
            'total_messages': 2,
            'recommendations': self._get_engagement_recommendations('medium')
        }
    
    def generate_personalized_nudges(self, engagement_analysis: Dict[str, Any]) -> List[str]:
        """
        Generate personalized nudges based on engagement analysis
        
        Args:
            engagement_analysis: Results from analyze_climate_engagement
            
        Returns:
            List of personalized nudge messages
        """
        engagement_level = engagement_analysis.get('engagement_level', 'medium')
        motivation_score = engagement_analysis.get('avg_motivation_score', 0.5)
        
        nudges = []
        
        if engagement_level == 'high':
            nudges = [
                "🌟 Your commitment to climate action is inspiring! Ready for today's eco-challenge?",
                "💚 You're making a real difference! Share your progress with friends?",
                "🎯 High achiever alert! Time to tackle that advanced sustainability goal!"
            ]
        elif engagement_level == 'medium':
            nudges = [
                "🌱 You're building great habits! One small step today?",
                "💡 Quick reminder: Your energy-saving tip is ready to try!",
                "🚀 Ready to level up your climate impact this week?"
            ]
        else:  # low engagement
            nudges = [
                "🌍 Even small actions matter! How about trying one eco-tip today?",
                "💰 Did you know? Going green can save you money too!",
                "🎁 Start easy: Turn off lights when leaving a room. You've got this!"
            ]
        
        # Add motivation-specific nudges
        if motivation_score < 0.3:
            nudges.append("🤗 Remember: Every expert was once a beginner. Your journey matters!")
        elif motivation_score > 0.8:
            nudges.append("🔥 Your passion for the planet is amazing! Keep up the momentum!")
        
        return nudges[:2]  # Return top 2 nudges

# Example usage
if __name__ == "__main__":
    service = SentimentMotivationService()
    
    # Test sentiment analysis
    test_texts = [
        "I'm excited to reduce my carbon footprint!",
        "Climate change is overwhelming and I don't know where to start.",
        "I tried biking to work today and it felt great!"
    ]
    
    sentiment_results = service.analyze_sentiment(test_texts)
    print("Sentiment Results:", sentiment_results)
    
    # Test motivation scoring
    motivation_result = service.calculate_motivation_score(test_texts[0])
    print("Motivation Result:", motivation_result)
    
    # Test engagement analysis
    engagement_analysis = service.analyze_climate_engagement(test_texts)
    print("Engagement Analysis:", engagement_analysis)
