#!/usr/bin/env python3
"""
ClimateCoach Activity Logging Demo
Shows how users enter activities and get carbon footprint calculations
"""

import sys
import os
sys.path.append('src')

from core.auth import UserAuth, ActivityTracker, CarbonCalculator
from core.recommendation_engine import recommendation_engine
from datetime import datetime, date

def demo_activity_logging():
    """Demonstrate activity logging and carbon footprint calculation"""
    
    print("🌍 ClimateCoach Activity Logging Demo")
    print("=" * 50)
    
    # Initialize services
    auth = UserAuth()
    activity_tracker = ActivityTracker()
    carbon_calculator = CarbonCalculator()
    
    # Sample user activities
    sample_activities = [
        {
            "name": "Car Commuter",
            "activities": {
                "transport_mode": "car",
                "distance_km": 25.0,
                "energy_kwh": 15.0,
                "water_usage": 150.0,
                "waste_kg": 2.0,
                "food_meals_meat": 2,
                "food_meals_veg": 1,
                "shopping_items": 3
            }
        },
        {
            "name": "Eco-Conscious User",
            "activities": {
                "transport_mode": "bike",
                "distance_km": 10.0,
                "energy_kwh": 8.0,
                "water_usage": 80.0,
                "waste_kg": 0.5,
                "food_meals_meat": 0,
                "food_meals_veg": 3,
                "shopping_items": 1
            }
        },
        {
            "name": "Public Transport User",
            "activities": {
                "transport_mode": "bus",
                "distance_km": 20.0,
                "energy_kwh": 12.0,
                "water_usage": 120.0,
                "waste_kg": 1.5,
                "food_meals_meat": 1,
                "food_meals_veg": 2,
                "shopping_items": 2
            }
        }
    ]
    
    print("\n📊 Sample Activity Scenarios:")
    print("-" * 30)
    
    for i, scenario in enumerate(sample_activities, 1):
        print(f"\n{i}. {scenario['name']}")
        print("   Activities:")
        for key, value in scenario['activities'].items():
            print(f"   - {key}: {value}")
        
        # Calculate carbon footprint
        footprint = carbon_calculator.calculate_daily_footprint(scenario['activities'])
        
        print(f"\n   📈 Carbon Footprint Results:")
        print(f"   - Total CO₂: {footprint['total_co2']} kg")
        print(f"   - Transport: {footprint['transport_co2']} kg")
        print(f"   - Energy: {footprint['energy_co2']} kg")
        print(f"   - Food: {footprint['food_co2']} kg")
        print(f"   - Shopping: {footprint['shopping_co2']} kg")
        
        # Generate recommendations
        recommendations = recommendation_engine.generate_personalized_recommendations(
            1, scenario['activities'], footprint, {"diet_preference": "omnivore"}
        )
        
        print(f"\n   💡 Top Recommendations:")
        for j, rec in enumerate(recommendations[:3], 1):
            print(f"   {j}. {rec['title']} ({rec['impact']} impact)")
            print(f"      {rec['description']}")
    
    print("\n" + "=" * 50)
    print("🎯 Key Features Demonstrated:")
    print("✅ Real-time carbon footprint calculation")
    print("✅ Detailed activity tracking")
    print("✅ Personalized AI recommendations")
    print("✅ Impact assessment and savings potential")
    print("✅ Multiple transport and lifestyle options")

def demo_detailed_activities():
    """Demonstrate detailed activity logging"""
    
    print("\n🔍 Detailed Activity Logging Demo")
    print("=" * 50)
    
    # Enhanced activity data
    detailed_activities = {
        "transport": [
            {"mode": "car", "distance_km": 15.0, "trips": 2},
            {"mode": "bike", "distance_km": 5.0, "trips": 1}
        ],
        "electricity_kwh": 12.5,
        "natural_gas_m3": 2.0,
        "heating_oil_liters": 0.0,
        "food_items": {
            "beef": 0.2,
            "chicken": 0.3,
            "dairy": 0.5,
            "vegetables": 1.0,
            "fruits": 0.8,
            "grains": 0.4
        },
        "shopping_items": {
            "clothing": 1,
            "electronics": 0,
            "household": 2,
            "food_items": 5,
            "second_hand": 1
        },
        "waste_landfill_kg": 1.0,
        "waste_recycling_kg": 0.8,
        "waste_composting_kg": 0.3,
        "water_usage_liters": 120.0
    }
    
    print("📝 Detailed Activity Input:")
    for category, data in detailed_activities.items():
        print(f"\n{category.upper()}:")
        if isinstance(data, dict):
            for key, value in data.items():
                print(f"  - {key}: {value}")
        elif isinstance(data, list):
            for item in data:
                print(f"  - {item}")
        else:
            print(f"  - {data}")
    
    # Calculate footprint (simplified for demo)
    transport_co2 = sum(trip['distance_km'] * 0.2 for trip in detailed_activities['transport'] if trip['mode'] == 'car')
    transport_co2 += sum(trip['distance_km'] * 0.0 for trip in detailed_activities['transport'] if trip['mode'] == 'bike')
    
    energy_co2 = detailed_activities['electricity_kwh'] * 0.5 + detailed_activities['natural_gas_m3'] * 2.0
    
    food_co2 = (detailed_activities['food_items']['beef'] * 13.3 + 
                detailed_activities['food_items']['chicken'] * 2.9 +
                detailed_activities['food_items']['dairy'] * 1.4 +
                detailed_activities['food_items']['vegetables'] * 0.4 +
                detailed_activities['food_items']['fruits'] * 0.4 +
                detailed_activities['food_items']['grains'] * 0.5)
    
    shopping_co2 = (detailed_activities['shopping_items']['clothing'] * 0.5 +
                    detailed_activities['shopping_items']['household'] * 0.3 +
                    detailed_activities['shopping_items']['food_items'] * 0.1 +
                    detailed_activities['shopping_items']['second_hand'] * 0.05)
    
    waste_co2 = (detailed_activities['waste_landfill_kg'] * 0.5 +
                 detailed_activities['waste_recycling_kg'] * 0.1 +
                 detailed_activities['waste_composting_kg'] * 0.0)
    
    water_co2 = detailed_activities['water_usage_liters'] * 0.0003
    
    total_co2 = transport_co2 + energy_co2 + food_co2 + shopping_co2 + waste_co2 + water_co2
    
    print(f"\n📊 Calculated Carbon Footprint:")
    print(f"Transport: {transport_co2:.2f} kg CO₂")
    print(f"Energy: {energy_co2:.2f} kg CO₂")
    print(f"Food: {food_co2:.2f} kg CO₂")
    print(f"Shopping: {shopping_co2:.2f} kg CO₂")
    print(f"Waste: {waste_co2:.2f} kg CO₂")
    print(f"Water: {water_co2:.2f} kg CO₂")
    print(f"TOTAL: {total_co2:.2f} kg CO₂")
    
    # Calculate percentages
    if total_co2 > 0:
        print(f"\n📈 Breakdown:")
        print(f"Transport: {(transport_co2/total_co2)*100:.1f}%")
        print(f"Energy: {(energy_co2/total_co2)*100:.1f}%")
        print(f"Food: {(food_co2/total_co2)*100:.1f}%")
        print(f"Shopping: {(shopping_co2/total_co2)*100:.1f}%")
        print(f"Waste: {(waste_co2/total_co2)*100:.1f}%")
        print(f"Water: {(water_co2/total_co2)*100:.1f}%")

def demo_recommendations():
    """Demonstrate AI-powered recommendations"""
    
    print("\n🤖 AI Recommendation Engine Demo")
    print("=" * 50)
    
    # Sample user profile and activities
    user_profile = {
        "diet_preference": "vegetarian",
        "transport_preference": "car",
        "location": "New York",
        "household_size": 2
    }
    
    activities = {
        "transport_mode": "car",
        "distance_km": 30.0,
        "energy_kwh": 20.0,
        "food_meals_meat": 0,
        "food_meals_veg": 3,
        "shopping_items": 5
    }
    
    footprint = {
        "transport_co2": 6.0,
        "energy_co2": 10.0,
        "food_co2": 1.5,
        "shopping_co2": 0.5,
        "total_co2": 18.0
    }
    
    print("👤 User Profile:")
    for key, value in user_profile.items():
        print(f"  - {key}: {value}")
    
    print("\n📊 Current Activities:")
    for key, value in activities.items():
        print(f"  - {key}: {value}")
    
    print(f"\n🌍 Current Footprint: {footprint['total_co2']} kg CO₂/day")
    
    # Generate recommendations
    recommendations = recommendation_engine.generate_personalized_recommendations(
        1, activities, footprint, user_profile
    )
    
    print("\n💡 AI-Generated Recommendations:")
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"\n{i}. {rec['title']}")
        print(f"   Impact: {rec['impact']} | Difficulty: {rec['difficulty']}")
        print(f"   Description: {rec['description']}")
        print(f"   Potential Savings: {rec.get('co2_savings', 0):.1f} kg CO₂")

if __name__ == "__main__":
    demo_activity_logging()
    demo_detailed_activities()
    demo_recommendations()
    
    print("\n" + "=" * 50)
    print("🎉 Demo Complete!")
    print("\nTo run the full application:")
    print("1. streamlit run app.py")
    print("2. Open http://localhost:8501")
    print("3. Login with demo_user / demo123")
    print("4. Try logging your own activities!") 