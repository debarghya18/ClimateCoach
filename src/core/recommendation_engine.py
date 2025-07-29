"""
Enhanced AI Recommendation Engine for ClimateCoach
Provides personalized carbon reduction recommendations based on user activities and patterns
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import sqlite3

class EnhancedRecommendationEngine:
    def __init__(self, db_path: str = "climatecoach.db"):
        self.db_path = db_path
        self.recommendation_database = self._load_recommendation_database()
    
    def _load_recommendation_database(self) -> Dict:
        """Load comprehensive recommendation database"""
        return {
            "transport": {
                "high_impact": [
                    {
                        "title": "Switch to Public Transport",
                        "description": "Replace car trips with bus or train. Saves 0.15 kg CO2 per km.",
                        "impact": "High",
                        "difficulty": "Medium",
                        "co2_savings": 0.15,
                        "category": "transport",
                        "tags": ["public_transport", "daily_commute"]
                    },
                    {
                        "title": "Start Carpooling",
                        "description": "Share rides with colleagues or neighbors. Reduces emissions by 50% per trip.",
                        "impact": "High",
                        "difficulty": "Medium",
                        "co2_savings": 0.1,
                        "category": "transport",
                        "tags": ["carpooling", "social"]
                    },
                    {
                        "title": "Switch to Electric Vehicle",
                        "description": "Consider an electric vehicle for your next car purchase. 70% lower emissions.",
                        "impact": "High",
                        "difficulty": "Hard",
                        "co2_savings": 0.14,
                        "category": "transport",
                        "tags": ["ev", "investment"]
                    }
                ],
                "medium_impact": [
                    {
                        "title": "Optimize Your Route",
                        "description": "Use GPS to find the most efficient route and avoid traffic.",
                        "impact": "Medium",
                        "difficulty": "Easy",
                        "co2_savings": 0.02,
                        "category": "transport",
                        "tags": ["efficiency", "technology"]
                    },
                    {
                        "title": "Maintain Your Vehicle",
                        "description": "Regular maintenance improves fuel efficiency by 10-15%.",
                        "impact": "Medium",
                        "difficulty": "Easy",
                        "co2_savings": 0.03,
                        "category": "transport",
                        "tags": ["maintenance", "efficiency"]
                    }
                ]
            },
            "energy": {
                "high_impact": [
                    {
                        "title": "Switch to LED Bulbs",
                        "description": "Replace all light bulbs with LED equivalents. 75% less energy usage.",
                        "impact": "High",
                        "difficulty": "Easy",
                        "co2_savings": 0.1,
                        "category": "energy",
                        "tags": ["lighting", "home"]
                    },
                    {
                        "title": "Install Smart Thermostat",
                        "description": "Automate heating/cooling to optimize energy usage.",
                        "impact": "High",
                        "difficulty": "Medium",
                        "co2_savings": 0.15,
                        "category": "energy",
                        "tags": ["smart_home", "automation"]
                    },
                    {
                        "title": "Switch to Renewable Energy",
                        "description": "Consider solar panels or green energy provider.",
                        "impact": "High",
                        "difficulty": "Hard",
                        "co2_savings": 0.5,
                        "category": "energy",
                        "tags": ["renewable", "investment"]
                    }
                ],
                "medium_impact": [
                    {
                        "title": "Unplug Electronics",
                        "description": "Unplug devices when not in use to prevent phantom energy usage.",
                        "impact": "Medium",
                        "difficulty": "Easy",
                        "co2_savings": 0.02,
                        "category": "energy",
                        "tags": ["habits", "home"]
                    },
                    {
                        "title": "Use Natural Light",
                        "description": "Open curtains and use natural light instead of artificial lighting.",
                        "impact": "Medium",
                        "difficulty": "Easy",
                        "co2_savings": 0.03,
                        "category": "energy",
                        "tags": ["natural", "free"]
                    }
                ]
            },
            "food": {
                "high_impact": [
                    {
                        "title": "Reduce Meat Consumption",
                        "description": "Try Meatless Mondays or reduce meat portions. 2.5 kg CO2 saved per meal.",
                        "impact": "High",
                        "difficulty": "Medium",
                        "co2_savings": 2.5,
                        "category": "food",
                        "tags": ["diet", "health"]
                    },
                    {
                        "title": "Buy Local Produce",
                        "description": "Choose locally grown food to reduce transportation emissions.",
                        "impact": "High",
                        "difficulty": "Medium",
                        "co2_savings": 0.5,
                        "category": "food",
                        "tags": ["local", "seasonal"]
                    },
                    {
                        "title": "Reduce Food Waste",
                        "description": "Plan meals and use leftovers. 30% of food is wasted globally.",
                        "impact": "High",
                        "difficulty": "Medium",
                        "co2_savings": 1.0,
                        "category": "food",
                        "tags": ["waste", "planning"]
                    }
                ],
                "medium_impact": [
                    {
                        "title": "Grow Your Own Herbs",
                        "description": "Start with easy-to-grow herbs like basil and mint.",
                        "impact": "Medium",
                        "difficulty": "Easy",
                        "co2_savings": 0.1,
                        "category": "food",
                        "tags": ["gardening", "hobby"]
                    },
                    {
                        "title": "Use Reusable Containers",
                        "description": "Bring your own containers for takeout and leftovers.",
                        "impact": "Medium",
                        "difficulty": "Easy",
                        "co2_savings": 0.05,
                        "category": "food",
                        "tags": ["reusable", "plastic_free"]
                    }
                ]
            },
            "shopping": {
                "high_impact": [
                    {
                        "title": "Buy Second-Hand",
                        "description": "Choose used items over new ones. Reduces manufacturing emissions.",
                        "impact": "High",
                        "difficulty": "Medium",
                        "co2_savings": 0.5,
                        "category": "shopping",
                        "tags": ["reuse", "thrift"]
                    },
                    {
                        "title": "Choose Sustainable Brands",
                        "description": "Support companies with eco-friendly practices.",
                        "impact": "High",
                        "difficulty": "Medium",
                        "co2_savings": 0.3,
                        "category": "shopping",
                        "tags": ["sustainable", "ethical"]
                    },
                    {
                        "title": "Reduce Online Shopping",
                        "description": "Combine orders and choose slower shipping options.",
                        "impact": "High",
                        "difficulty": "Easy",
                        "co2_savings": 0.2,
                        "category": "shopping",
                        "tags": ["delivery", "consolidation"]
                    }
                ],
                "medium_impact": [
                    {
                        "title": "Use Reusable Bags",
                        "description": "Bring your own shopping bags to avoid plastic.",
                        "impact": "Medium",
                        "difficulty": "Easy",
                        "co2_savings": 0.01,
                        "category": "shopping",
                        "tags": ["plastic_free", "habits"]
                    },
                    {
                        "title": "Buy in Bulk",
                        "description": "Purchase larger quantities to reduce packaging waste.",
                        "impact": "Medium",
                        "difficulty": "Easy",
                        "co2_savings": 0.05,
                        "category": "shopping",
                        "tags": ["bulk", "packaging"]
                    }
                ]
            }
        }
    
    def analyze_user_patterns(self, user_id: int, days: int = 30) -> Dict:
        """Analyze user's activity patterns to identify improvement areas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get user's recent activities
            cursor.execute("""
                SELECT transport_mode, distance_km, energy_kwh, 
                       food_meals_meat, food_meals_veg, shopping_items
                FROM daily_activities 
                WHERE user_id = ? AND date >= date('now', '-{} days')
            """.format(days), (user_id,))
            
            activities = cursor.fetchall()
            conn.close()
            
            if not activities:
                return {"patterns": {}, "high_impact_areas": []}
            
            # Calculate averages and patterns
            total_distance = sum(row[1] or 0 for row in activities)
            total_energy = sum(row[2] or 0 for row in activities)
            total_meat_meals = sum(row[3] or 0 for row in activities)
            total_veg_meals = sum(row[4] or 0 for row in activities)
            total_shopping = sum(row[5] or 0 for row in activities)
            
            # Identify high-impact areas
            high_impact_areas = []
            
            if total_distance > 50:  # High transport usage
                high_impact_areas.append("transport")
            if total_energy > 30:  # High energy usage
                high_impact_areas.append("energy")
            if total_meat_meals > total_veg_meals:  # High meat consumption
                high_impact_areas.append("food")
            if total_shopping > 20:  # High shopping frequency
                high_impact_areas.append("shopping")
            
            return {
                "patterns": {
                    "avg_daily_distance": total_distance / len(activities),
                    "avg_daily_energy": total_energy / len(activities),
                    "meat_meals_ratio": total_meat_meals / max(total_meat_meals + total_veg_meals, 1),
                    "avg_daily_shopping": total_shopping / len(activities)
                },
                "high_impact_areas": high_impact_areas
            }
            
        except Exception as e:
            print(f"Error analyzing user patterns: {e}")
            return {"patterns": {}, "high_impact_areas": []}
    
    def generate_personalized_recommendations(self, user_id: int, activities: Dict, 
                                           footprint: Dict, user_profile: Dict) -> List[Dict]:
        """Generate personalized recommendations based on user data"""
        
        # Analyze user patterns
        patterns = self.analyze_user_patterns(user_id)
        high_impact_areas = patterns.get("high_impact_areas", [])
        
        recommendations = []
        
        # Generate recommendations based on high-impact areas
        for area in high_impact_areas:
            area_recs = self.recommendation_database.get(area, {})
            
            # Add high impact recommendations first
            for rec in area_recs.get("high_impact", []):
                if self._is_recommendation_suitable(rec, user_profile, activities):
                    recommendations.append(rec)
            
            # Add medium impact recommendations
            for rec in area_recs.get("medium_impact", []):
                if self._is_recommendation_suitable(rec, user_profile, activities):
                    recommendations.append(rec)
        
        # If no high-impact areas, provide general recommendations
        if not high_impact_areas:
            general_recs = []
            for area in ["transport", "energy", "food", "shopping"]:
                area_recs = self.recommendation_database.get(area, {})
                general_recs.extend(area_recs.get("medium_impact", [])[:1])
            
            recommendations.extend(general_recs)
        
        # Limit to top 5 recommendations
        return recommendations[:5]
    
    def _is_recommendation_suitable(self, recommendation: Dict, user_profile: Dict, 
                                   activities: Dict) -> bool:
        """Check if a recommendation is suitable for the user"""
        
        # Check user preferences
        if recommendation["category"] == "transport":
            if user_profile.get("transport_preference") == "bike" and "car" in recommendation["title"].lower():
                return False
        
        if recommendation["category"] == "food":
            if user_profile.get("diet_preference") == "vegan" and "meat" in recommendation["title"].lower():
                return False
        
        # Check current activities
        if recommendation["category"] == "transport" and activities.get("distance_km", 0) < 5:
            return False
        
        if recommendation["category"] == "energy" and activities.get("energy_kwh", 0) < 5:
            return False
        
        return True
    
    def calculate_potential_savings(self, recommendation: Dict, user_patterns: Dict) -> float:
        """Calculate potential CO2 savings for a recommendation"""
        base_savings = recommendation.get("co2_savings", 0)
        
        # Adjust based on user patterns
        if recommendation["category"] == "transport":
            daily_distance = user_patterns.get("avg_daily_distance", 0)
            return base_savings * daily_distance * 0.3  # 30% adoption rate
        
        elif recommendation["category"] == "energy":
            daily_energy = user_patterns.get("avg_daily_energy", 0)
            return base_savings * daily_energy * 0.2  # 20% adoption rate
        
        elif recommendation["category"] == "food":
            meat_ratio = user_patterns.get("meat_meals_ratio", 0.5)
            return base_savings * meat_ratio * 0.4  # 40% adoption rate
        
        else:  # shopping
            daily_shopping = user_patterns.get("avg_daily_shopping", 1)
            return base_savings * daily_shopping * 0.25  # 25% adoption rate
    
    def get_community_recommendations(self, user_id: int) -> List[Dict]:
        """Get recommendations based on community success stories"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get popular community posts about successful changes
            cursor.execute("""
                SELECT title, content, likes, category
                FROM community_posts 
                WHERE category IN ('tips', 'success') AND likes > 5
                ORDER BY likes DESC
                LIMIT 3
            """)
            
            community_tips = cursor.fetchall()
            conn.close()
            
            recommendations = []
            for tip in community_tips:
                recommendations.append({
                    "title": f"Community Tip: {tip[0]}",
                    "description": tip[1][:100] + "...",
                    "impact": "Medium",
                    "difficulty": "Easy",
                    "co2_savings": 0.1,
                    "category": "community",
                    "tags": ["community", "proven"],
                    "likes": tip[2]
                })
            
            return recommendations
            
        except Exception as e:
            print(f"Error getting community recommendations: {e}")
            return []

# Create a global instance
recommendation_engine = EnhancedRecommendationEngine() 