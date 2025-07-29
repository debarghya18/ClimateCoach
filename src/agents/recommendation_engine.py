"""
AI Recommendation Engine for ClimateCoach
Uses LangChain and OpenAI GPT-4 for contextual recommendations and behavioral nudging
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

# LangChain imports
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage

# Local imports
from .carbon_estimator import CarbonEstimator

logger = logging.getLogger(__name__)

@dataclass
class UserContext:
    """User context for personalized recommendations"""
    user_id: str
    location: str
    age: int
    income: float
    diet_preference: str
    transport_preference: str
    household_size: int
    recent_emissions: Dict[str, float]
    goals: List[str]
    past_actions: List[Dict]
    current_weather: Dict
    time_of_day: int

@dataclass
class Recommendation:
    """Recommendation structure"""
    id: str
    category: str
    title: str
    description: str
    impact_level: str  # 'high', 'medium', 'low'
    difficulty: str    # 'easy', 'medium', 'hard'
    potential_savings: float  # kg CO2
    personalization_score: float  # 0-1
    urgency: str      # 'immediate', 'today', 'this_week', 'this_month'
    action_steps: List[str]
    resources: List[Dict]
    gamification: Dict

class RecommendationEngine:
    """
    Advanced AI-powered recommendation engine using LangChain and OpenAI
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the recommendation engine"""
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            logger.warning("OpenAI API key not found. Using fallback recommendations.")
        
        self.carbon_estimator = CarbonEstimator()
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        # Initialize LangChain components
        self._initialize_llm()
        self._initialize_prompts()
        self._initialize_chains()
        self._initialize_tools()
        
        # Recommendation templates
        self.recommendation_templates = self._load_recommendation_templates()
        
    def _initialize_llm(self):
        """Initialize the language model"""
        if self.openai_api_key:
            self.llm = ChatOpenAI(
                model_name="gpt-4",
                temperature=0.7,
                openai_api_key=self.openai_api_key,
                max_tokens=500
            )
            
            self.fast_llm = ChatOpenAI(
                model_name="gpt-3.5-turbo",
                temperature=0.5,
                openai_api_key=self.openai_api_key,
                max_tokens=300
            )
        else:
            # Fallback to mock responses
            self.llm = None
            self.fast_llm = None
    
    def _initialize_prompts(self):
        """Initialize prompt templates"""
        self.recommendation_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=\"\"\"You are ClimateCoach, an AI assistant specializing in personalized carbon footprint reduction recommendations. 
            You provide actionable, contextual advice based on user behavior, location, and preferences.
            
            Your recommendations should be:
            1. Personalized to the user's context
            2. Actionable with clear steps
            3. Impactful for carbon reduction
            4. Realistic and achievable
            5. Motivational and positive
            
            Always include specific carbon savings estimates and make recommendations engaging.\"\"\"),
            HumanMessage(content=\"{user_input}\")
        ])\n        \n        self.nudge_prompt = ChatPromptTemplate.from_messages([\n            SystemMessage(content=\"\"\"You are a behavioral nudging expert for ClimateCoach. \n            Create real-time, contextual nudges that encourage sustainable behavior.\n            \n            Nudges should be:\n            1. Timely and relevant to current situation\n            2. Brief and actionable (1-2 sentences)\n            3. Positive and encouraging\n            4. Specific with clear alternatives\n            5. Include environmental benefit\n            \n            Format: Provide a short, engaging message with a specific call-to-action.\"\"\"),\n            HumanMessage(content=\"{context}\")\n        ])\n        \n        self.habit_analysis_prompt = ChatPromptTemplate.from_messages([\n            SystemMessage(content=\"\"\"You are a habit analysis expert for ClimateCoach.\n            Analyze user behavior patterns and identify opportunities for sustainable habits.\n            \n            Focus on:\n            1. Identifying recurring patterns\n            2. Finding sustainable alternatives\n            3. Suggesting habit-forming strategies\n            4. Estimating long-term impact\n            5. Creating motivation through progress tracking\"\"\"),\n            HumanMessage(content=\"{habit_data}\")\n        ])\n    \n    def _initialize_chains(self):\n        \"\"\"Initialize LangChain chains\"\"\"\n        if self.llm:\n            self.recommendation_chain = LLMChain(\n                llm=self.llm,\n                prompt=self.recommendation_prompt,\n                memory=self.memory,\n                verbose=False\n            )\n            \n            self.nudge_chain = LLMChain(\n                llm=self.fast_llm,\n                prompt=self.nudge_prompt,\n                verbose=False\n            )\n            \n            self.habit_chain = LLMChain(\n                llm=self.llm,\n                prompt=self.habit_analysis_prompt,\n                verbose=False\n            )\n    \n    def _initialize_tools(self):\n        \"\"\"Initialize tools for the agent\"\"\"\n        self.tools = [\n            Tool(\n                name=\"carbon_calculator\",\n                description=\"Calculate carbon footprint for various activities\",\n                func=self._calculate_carbon_footprint\n            ),\n            Tool(\n                name=\"weather_impact\",\n                description=\"Analyze weather impact on carbon emissions\",\n                func=self._analyze_weather_impact\n            ),\n            Tool(\n                name=\"local_alternatives\",\n                description=\"Find local sustainable alternatives\",\n                func=self._find_local_alternatives\n            )\n        ]\n    \n    def _load_recommendation_templates(self) -> Dict:\n        \"\"\"Load recommendation templates for fallback\"\"\"\n        return {\n            'transport': {\n                'high_emission': {\n                    'bike': {\n                        'title': 'Switch to Cycling',\n                        'description': 'Replace short car trips with cycling to dramatically reduce emissions',\n                        'steps': ['Get a bike or use bike-sharing', 'Plan safe cycling routes', 'Start with 1-2 trips per week'],\n                        'savings': 8.5\n                    },\n                    'public_transport': {\n                        'title': 'Use Public Transportation',\n                        'description': 'Take buses or trains instead of driving alone',\n                        'steps': ['Download transit apps', 'Buy monthly pass', 'Plan journey times'],\n                        'savings': 6.2\n                    }\n                }\n            },\n            'energy': {\n                'high_consumption': {\n                    'smart_thermostat': {\n                        'title': 'Install Smart Thermostat',\n                        'description': 'Optimize heating and cooling automatically',\n                        'steps': ['Research compatible models', 'Install or hire professional', 'Set optimal schedules'],\n                        'savings': 4.8\n                    },\n                    'led_bulbs': {\n                        'title': 'Switch to LED Bulbs',\n                        'description': 'Replace all incandescent bulbs with efficient LEDs',\n                        'steps': ['Audit current bulbs', 'Buy LED replacements', 'Replace gradually'],\n                        'savings': 2.1\n                    }\n                }\n            },\n            'food': {\n                'high_emission': {\n                    'plant_based': {\n                        'title': 'Try Plant-Based Meals',\n                        'description': 'Incorporate more plant-based meals into your diet',\n                        'steps': ['Start with 1 plant-based day per week', 'Explore new recipes', 'Join online communities'],\n                        'savings': 12.3\n                    },\n                    'local_food': {\n                        'title': 'Buy Local Produce',\n                        'description': 'Choose locally grown fruits and vegetables',\n                        'steps': ['Find local farmers markets', 'Join CSA program', 'Check grocery store labels'],\n                        'savings': 3.4\n                    }\n                }\n            }\n        }\n    \n    def generate_personalized_recommendations(self, user_context: UserContext) -> List[Recommendation]:\n        \"\"\"Generate personalized recommendations based on user context\"\"\"\n        recommendations = []\n        \n        try:\n            # Analyze user's carbon footprint\n            emissions = user_context.recent_emissions\n            \n            # Generate AI-powered recommendations if OpenAI is available\n            if self.llm:\n                ai_recommendations = self._generate_ai_recommendations(user_context)\n                recommendations.extend(ai_recommendations)\n            \n            # Generate template-based recommendations as fallback/supplement\n            template_recommendations = self._generate_template_recommendations(user_context)\n            recommendations.extend(template_recommendations)\n            \n            # Rank and filter recommendations\n            recommendations = self._rank_recommendations(recommendations, user_context)\n            \n            return recommendations[:5]  # Return top 5 recommendations\n            \n        except Exception as e:\n            logger.error(f\"Error generating recommendations: {e}\")\n            return self._get_fallback_recommendations()\n    \n    def _generate_ai_recommendations(self, user_context: UserContext) -> List[Recommendation]:\n        \"\"\"Generate recommendations using AI\"\"\"\n        recommendations = []\n        \n        try:\n            # Prepare user context for AI\n            context_str = self._format_user_context(user_context)\n            \n            # Generate recommendations\n            response = self.recommendation_chain.run(user_input=context_str)\n            \n            # Parse AI response and convert to recommendation objects\n            # This is a simplified version - in production, you'd have more sophisticated parsing\n            ai_recommendations = self._parse_ai_response(response, user_context)\n            \n            return ai_recommendations\n            \n        except Exception as e:\n            logger.error(f\"Error generating AI recommendations: {e}\")\n            return []\n    \n    def _generate_template_recommendations(self, user_context: UserContext) -> List[Recommendation]:\n        \"\"\"Generate recommendations using templates\"\"\"\n        recommendations = []\n        emissions = user_context.recent_emissions\n        \n        # Transport recommendations\n        if emissions.get('transport', 0) > 10:\n            if user_context.location in ['urban', 'city']:\n                rec = self._create_recommendation_from_template(\n                    'transport', 'high_emission', 'public_transport', user_context\n                )\n                recommendations.append(rec)\n        \n        # Energy recommendations\n        if emissions.get('energy', 0) > 15:\n            rec = self._create_recommendation_from_template(\n                'energy', 'high_consumption', 'smart_thermostat', user_context\n            )\n            recommendations.append(rec)\n        \n        # Food recommendations\n        if emissions.get('food', 0) > 10 and user_context.diet_preference != 'vegan':\n            rec = self._create_recommendation_from_template(\n                'food', 'high_emission', 'plant_based', user_context\n            )\n            recommendations.append(rec)\n        \n        return recommendations\n    \n    def _create_recommendation_from_template(self, category: str, emission_level: str, \n                                           action: str, user_context: UserContext) -> Recommendation:\n        \"\"\"Create a recommendation from template\"\"\"\n        template = self.recommendation_templates[category][emission_level][action]\n        \n        return Recommendation(\n            id=f\"{category}_{action}_{datetime.now().strftime('%Y%m%d_%H%M%S')}\",\n            category=category,\n            title=template['title'],\n            description=template['description'],\n            impact_level='high' if template['savings'] > 8 else 'medium' if template['savings'] > 4 else 'low',\n            difficulty='easy',\n            potential_savings=template['savings'],\n            personalization_score=self._calculate_personalization_score(category, user_context),\n            urgency='this_week',\n            action_steps=template['steps'],\n            resources=[],\n            gamification={\n                'points': int(template['savings'] * 10),\n                'badge': f\"{category.title()} Champion\",\n                'challenge': f\"Complete this action to earn {int(template['savings'] * 10)} EcoPoints!\"\n            }\n        )\n    \n    def generate_real_time_nudge(self, context: Dict) -> str:\n        \"\"\"Generate real-time behavioral nudge\"\"\"\n        try:\n            if self.nudge_chain:\n                context_str = json.dumps(context, indent=2)\n                nudge = self.nudge_chain.run(context=context_str)\n                return nudge.strip()\n            else:\n                return self._get_fallback_nudge(context)\n        except Exception as e:\n            logger.error(f\"Error generating nudge: {e}\")\n            return self._get_fallback_nudge(context)\n    \n    def analyze_habit_patterns(self, user_data: Dict) -> Dict:\n        \"\"\"Analyze user habit patterns\"\"\"\n        try:\n            if self.habit_chain:\n                habit_data_str = json.dumps(user_data, indent=2)\n                analysis = self.habit_chain.run(habit_data=habit_data_str)\n                return {'analysis': analysis, 'recommendations': []}\n            else:\n                return self._get_fallback_habit_analysis(user_data)\n        except Exception as e:\n            logger.error(f\"Error analyzing habits: {e}\")\n            return {'analysis': 'Unable to analyze habits at this time.', 'recommendations': []}\n    \n    def _format_user_context(self, user_context: UserContext) -> str:\n        \"\"\"Format user context for AI prompt\"\"\"\n        return f\"\"\"\n        User Profile:\n        - Location: {user_context.location}\n        - Age: {user_context.age}\n        - Income: ${user_context.income:,.0f}\n        - Diet: {user_context.diet_preference}\n        - Transportation: {user_context.transport_preference}\n        - Household Size: {user_context.household_size}\n        \n        Recent Emissions (kg CO2/day):\n        - Transport: {user_context.recent_emissions.get('transport', 0):.1f}\n        - Energy: {user_context.recent_emissions.get('energy', 0):.1f}\n        - Food: {user_context.recent_emissions.get('food', 0):.1f}\n        - Shopping: {user_context.recent_emissions.get('shopping', 0):.1f}\n        - Total: {user_context.recent_emissions.get('total', 0):.1f}\n        \n        Goals: {', '.join(user_context.goals)}\n        \n        Current Context:\n        - Time: {user_context.time_of_day}:00\n        - Weather: {user_context.current_weather.get('condition', 'clear')}, {user_context.current_weather.get('temperature', 20)}°C\n        \n        Please provide 3-5 personalized recommendations to reduce carbon footprint.\n        \"\"\"\n    \n    def _parse_ai_response(self, response: str, user_context: UserContext) -> List[Recommendation]:\n        \"\"\"Parse AI response into recommendation objects\"\"\"\n        # This is a simplified parser - in production, you'd want more sophisticated parsing\n        recommendations = []\n        \n        # For now, create a single recommendation from the AI response\n        rec = Recommendation(\n            id=f\"ai_{datetime.now().strftime('%Y%m%d_%H%M%S')}\",\n            category='general',\n            title='AI Recommendation',\n            description=response[:200] + '...' if len(response) > 200 else response,\n            impact_level='medium',\n            difficulty='easy',\n            potential_savings=5.0,\n            personalization_score=0.8,\n            urgency='today',\n            action_steps=['Follow AI guidance'],\n            resources=[],\n            gamification={'points': 50, 'badge': 'AI Advisor', 'challenge': 'Complete AI recommendation!'}\n        )\n        \n        recommendations.append(rec)\n        return recommendations\n    \n    def _calculate_personalization_score(self, category: str, user_context: UserContext) -> float:\n        \"\"\"Calculate how personalized a recommendation is for the user\"\"\"\n        score = 0.5  # Base score\n        \n        # Adjust based on user's emission levels in this category\n        if user_context.recent_emissions.get(category, 0) > 10:\n            score += 0.3\n        \n        # Adjust based on user preferences\n        if category == 'transport' and user_context.transport_preference == 'public':\n            score += 0.2\n        \n        return min(1.0, score)\n    \n    def _rank_recommendations(self, recommendations: List[Recommendation], \n                            user_context: UserContext) -> List[Recommendation]:\n        \"\"\"Rank recommendations by relevance and impact\"\"\"\n        def score_recommendation(rec: Recommendation) -> float:\n            score = 0\n            score += rec.potential_savings * 0.3  # Impact weight\n            score += rec.personalization_score * 0.3  # Personalization weight\n            score += (0.3 if rec.difficulty == 'easy' else 0.2 if rec.difficulty == 'medium' else 0.1) * 0.2  # Difficulty weight\n            score += (0.3 if rec.urgency == 'immediate' else 0.2 if rec.urgency == 'today' else 0.1) * 0.2  # Urgency weight\n            return score\n        \n        return sorted(recommendations, key=score_recommendation, reverse=True)\n    \n    def _get_fallback_recommendations(self) -> List[Recommendation]:\n        \"\"\"Get fallback recommendations when AI is unavailable\"\"\"\n        return [\n            Recommendation(\n                id=\"fallback_1\",\n                category=\"transport\",\n                title=\"Walk or Bike for Short Trips\",\n                description=\"Replace car trips under 3km with walking or cycling\",\n                impact_level=\"high\",\n                difficulty=\"easy\",\n                potential_savings=8.5,\n                personalization_score=0.7,\n                urgency=\"today\",\n                action_steps=[\"Identify short trips you make regularly\", \"Plan walking/cycling routes\", \"Start with one trip per day\"],\n                resources=[],\n                gamification={'points': 85, 'badge': 'Active Commuter', 'challenge': 'Walk or bike instead of driving!'}\n            )\n        ]\n    \n    def _get_fallback_nudge(self, context: Dict) -> str:\n        \"\"\"Get fallback nudge when AI is unavailable\"\"\"\n        nudges = [\n            \"🚶 Perfect weather for a walk! Skip the car for this short trip and save CO2.\",\n            \"🚌 Public transport is running on time - a great alternative to driving today!\",\n            \"💡 It's peak energy hours - consider turning off non-essential appliances.\",\n            \"🥗 How about a plant-based meal today? Your planet will thank you!\"\n        ]\n        return nudges[hash(str(context)) % len(nudges)]\n    \n    def _get_fallback_habit_analysis(self, user_data: Dict) -> Dict:\n        \"\"\"Get fallback habit analysis when AI is unavailable\"\"\"\n        return {\n            'analysis': 'Based on your recent activity, focus on consistent daily actions like walking instead of driving for short trips.',\n            'recommendations': ['Establish a daily walking routine', 'Set weekly plant-based meal goals']\n        }\n    \n    # Tool functions for LangChain agent\n    def _calculate_carbon_footprint(self, activity_data: str) -> str:\n        \"\"\"Tool function to calculate carbon footprint\"\"\"\n        try:\n            data = json.loads(activity_data)\n            emissions = self.carbon_estimator.estimate_total_daily_emissions(data)\n            return f\"Estimated daily emissions: {emissions['total']:.1f} kg CO2\"\n        except Exception as e:\n            return f\"Error calculating footprint: {str(e)}\"\n    \n    def _analyze_weather_impact(self, weather_data: str) -> str:\n        \"\"\"Tool function to analyze weather impact\"\"\"\n        return \"Cold weather increases heating emissions. Consider bundling up instead of raising thermostat.\"\n    \n    def _find_local_alternatives(self, location: str) -> str:\n        \"\"\"Tool function to find local alternatives\"\"\"\n        return f\"Local alternatives in {location}: bike sharing, farmers markets, public transit.\"\n\n# Example usage\nif __name__ == \"__main__\":\n    # Initialize engine\n    engine = RecommendationEngine()\n    \n    # Create sample user context\n    user_context = UserContext(\n        user_id=\"user123\",\n        location=\"urban\",\n        age=32,\n        income=65000,\n        diet_preference=\"omnivore\",\n        transport_preference=\"car\",\n        household_size=2,\n        recent_emissions={'transport': 12.5, 'energy': 18.2, 'food': 8.9, 'shopping': 4.1, 'total': 43.7},\n        goals=[\"reduce_transport_emissions\", \"eat_more_plants\"],\n        past_actions=[],\n        current_weather={'condition': 'sunny', 'temperature': 22},\n        time_of_day=14\n    )\n    \n    # Generate recommendations\n    recommendations = engine.generate_personalized_recommendations(user_context)\n    \n    print(\"Generated Recommendations:\")\n    for rec in recommendations:\n        print(f\"- {rec.title}: {rec.description} (Savings: {rec.potential_savings} kg CO2)\")\n    \n    # Generate a nudge\n    nudge_context = {\n        'location': 'near_coffee_shop',\n        'time': '8:00 AM',\n        'weather': 'sunny',\n        'usual_transport': 'car',\n        'distance': '0.8 km'\n    }\n    \n    nudge = engine.generate_real_time_nudge(nudge_context)\n    print(f\"\\nReal-time Nudge: {nudge}\")
