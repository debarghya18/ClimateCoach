"""
Enhanced Activity Tracker for ClimateCoach
Provides comprehensive activity logging and carbon footprint calculation
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

class EnhancedActivityTracker:
    def __init__(self, db_path: str = "climatecoach.db"):
        self.db_path = db_path
        self.emission_factors = {
            'transport': {
                'car': 0.2,      # kg CO2 per km
                'bus': 0.05,     # kg CO2 per km
                'train': 0.04,   # kg CO2 per km
                'bike': 0.0,     # kg CO2 per km
                'walk': 0.0,     # kg CO2 per km
                'plane': 0.25,   # kg CO2 per km
                'electric_car': 0.06,  # kg CO2 per km
                'hybrid_car': 0.12,    # kg CO2 per km
                'motorcycle': 0.15,     # kg CO2 per km
                'scooter': 0.08         # kg CO2 per km
            },
            'energy': {
                'electricity': 0.5,     # kg CO2 per kWh
                'natural_gas': 2.0,     # kg CO2 per m³
                'heating_oil': 2.7,     # kg CO2 per liter
                'propane': 1.6,         # kg CO2 per liter
                'solar': 0.0,           # kg CO2 per kWh
                'wind': 0.0             # kg CO2 per kWh
            },
            'food': {
                'beef': 13.3,           # kg CO2 per kg
                'lamb': 13.3,           # kg CO2 per kg
                'pork': 5.8,            # kg CO2 per kg
                'chicken': 2.9,         # kg CO2 per kg
                'fish': 3.0,            # kg CO2 per kg
                'eggs': 1.4,            # kg CO2 per kg
                'dairy': 1.4,           # kg CO2 per kg
                'vegetables': 0.4,      # kg CO2 per kg
                'fruits': 0.4,          # kg CO2 per kg
                'grains': 0.5,          # kg CO2 per kg
                'nuts': 0.3,            # kg CO2 per kg
                'plant_based': 0.3      # kg CO2 per kg
            },
            'shopping': {
                'clothing': 0.5,        # kg CO2 per item
                'electronics': 2.0,     # kg CO2 per item
                'furniture': 5.0,       # kg CO2 per item
                'books': 0.1,           # kg CO2 per item
                'cosmetics': 0.2,       # kg CO2 per item
                'household': 0.3,       # kg CO2 per item
                'food_items': 0.1,      # kg CO2 per item
                'second_hand': 0.05     # kg CO2 per item (reduced impact)
            },
            'waste': {
                'landfill': 0.5,        # kg CO2 per kg
                'recycling': 0.1,       # kg CO2 per kg
                'composting': 0.0       # kg CO2 per kg
            },
            'water': {
                'usage': 0.0003         # kg CO2 per liter
            }
        }
    
    def log_detailed_activity(self, user_id: int, date: str, activities: Dict) -> Dict:
        """Log detailed activities and calculate comprehensive carbon footprint"""
        
        # Calculate carbon footprint
        footprint = self.calculate_comprehensive_footprint(activities)
        
        # Save to database
        self.save_activity_data(user_id, date, activities, footprint)
        
        return {
            'success': True,
            'footprint': footprint,
            'activities': activities,
            'date': date
        }
    
    def calculate_comprehensive_footprint(self, activities: Dict) -> Dict:
        """Calculate comprehensive carbon footprint from detailed activities"""
        
        # Transport calculations
        transport_co2 = self.calculate_transport_emissions(activities)
        
        # Energy calculations
        energy_co2 = self.calculate_energy_emissions(activities)
        
        # Food calculations
        food_co2 = self.calculate_food_emissions(activities)
        
        # Shopping calculations
        shopping_co2 = self.calculate_shopping_emissions(activities)
        
        # Waste calculations
        waste_co2 = self.calculate_waste_emissions(activities)
        
        # Water calculations
        water_co2 = self.calculate_water_emissions(activities)
        
        total_co2 = transport_co2 + energy_co2 + food_co2 + shopping_co2 + waste_co2 + water_co2
        
        return {
            'transport_co2': round(transport_co2, 2),
            'energy_co2': round(energy_co2, 2),
            'food_co2': round(food_co2, 2),
            'shopping_co2': round(shopping_co2, 2),
            'waste_co2': round(waste_co2, 2),
            'water_co2': round(water_co2, 2),
            'total_co2': round(total_co2, 2),
            'breakdown': {
                'transport_percent': round((transport_co2 / total_co2 * 100) if total_co2 > 0 else 0, 1),
                'energy_percent': round((energy_co2 / total_co2 * 100) if total_co2 > 0 else 0, 1),
                'food_percent': round((food_co2 / total_co2 * 100) if total_co2 > 0 else 0, 1),
                'shopping_percent': round((shopping_co2 / total_co2 * 100) if total_co2 > 0 else 0, 1),
                'waste_percent': round((waste_co2 / total_co2 * 100) if total_co2 > 0 else 0, 1),
                'water_percent': round((water_co2 / total_co2 * 100) if total_co2 > 0 else 0, 1)
            }
        }
    
    def calculate_transport_emissions(self, activities: Dict) -> float:
        """Calculate transport emissions"""
        transport_co2 = 0
        
        # Handle multiple transport modes
        transport_activities = activities.get('transport', [])
        if isinstance(transport_activities, list):
            for trip in transport_activities:
                mode = trip.get('mode', 'car')
                distance = trip.get('distance_km', 0)
                transport_co2 += distance * self.emission_factors['transport'].get(mode, 0.2)
        else:
            # Legacy single transport mode
            mode = activities.get('transport_mode', 'car')
            distance = activities.get('distance_km', 0)
            transport_co2 = distance * self.emission_factors['transport'].get(mode, 0.2)
        
        return transport_co2
    
    def calculate_energy_emissions(self, activities: Dict) -> float:
        """Calculate energy emissions"""
        energy_co2 = 0
        
        # Electricity usage
        electricity_kwh = activities.get('electricity_kwh', 0)
        energy_co2 += electricity_kwh * self.emission_factors['energy']['electricity']
        
        # Natural gas usage
        gas_m3 = activities.get('natural_gas_m3', 0)
        energy_co2 += gas_m3 * self.emission_factors['energy']['natural_gas']
        
        # Heating oil
        heating_oil_liters = activities.get('heating_oil_liters', 0)
        energy_co2 += heating_oil_liters * self.emission_factors['energy']['heating_oil']
        
        return energy_co2
    
    def calculate_food_emissions(self, activities: Dict) -> float:
        """Calculate food emissions"""
        food_co2 = 0
        
        # Detailed food items
        food_items = activities.get('food_items', {})
        for food_type, amount_kg in food_items.items():
            if food_type in self.emission_factors['food']:
                food_co2 += amount_kg * self.emission_factors['food'][food_type]
        
        # Legacy meal-based calculation
        meat_meals = activities.get('food_meals_meat', 0)
        veg_meals = activities.get('food_meals_veg', 0)
        food_co2 += meat_meals * 2.5  # kg CO2 per meat meal
        food_co2 += veg_meals * 0.5   # kg CO2 per veg meal
        
        return food_co2
    
    def calculate_shopping_emissions(self, activities: Dict) -> float:
        """Calculate shopping emissions"""
        shopping_co2 = 0
        
        # Detailed shopping items
        shopping_items = activities.get('shopping_items', {})
        for item_type, count in shopping_items.items():
            if item_type in self.emission_factors['shopping']:
                shopping_co2 += count * self.emission_factors['shopping'][item_type]
        
        # Legacy simple calculation
        total_items = activities.get('shopping_items_count', 0)
        shopping_co2 += total_items * 0.1  # kg CO2 per item
        
        return shopping_co2
    
    def calculate_waste_emissions(self, activities: Dict) -> float:
        """Calculate waste emissions"""
        waste_co2 = 0
        
        landfill_kg = activities.get('waste_landfill_kg', 0)
        recycling_kg = activities.get('waste_recycling_kg', 0)
        composting_kg = activities.get('waste_composting_kg', 0)
        
        waste_co2 += landfill_kg * self.emission_factors['waste']['landfill']
        waste_co2 += recycling_kg * self.emission_factors['waste']['recycling']
        waste_co2 += composting_kg * self.emission_factors['waste']['composting']
        
        return waste_co2
    
    def calculate_water_emissions(self, activities: Dict) -> float:
        """Calculate water emissions"""
        water_usage_liters = activities.get('water_usage_liters', 0)
        return water_usage_liters * self.emission_factors['water']['usage']
    
    def save_activity_data(self, user_id: int, date: str, activities: Dict, footprint: Dict) -> bool:
        """Save activity data and footprint to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Save detailed activities
            cursor.execute("""
                INSERT OR REPLACE INTO daily_activities
                (user_id, date, activities_json, created_at)
                VALUES (?, ?, ?, ?)
            """, (user_id, date, json.dumps(activities), datetime.now().isoformat()))
            
            # Save carbon footprint
            cursor.execute("""
                INSERT OR REPLACE INTO carbon_footprints
                (user_id, date, transport_co2, energy_co2, food_co2, shopping_co2, 
                 waste_co2, water_co2, total_co2, calculated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, date,
                footprint['transport_co2'],
                footprint['energy_co2'],
                footprint['food_co2'],
                footprint['shopping_co2'],
                footprint['waste_co2'],
                footprint['water_co2'],
                footprint['total_co2'],
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error saving activity data: {e}")
            return False
    
    def get_user_activity_summary(self, user_id: int, days: int = 30) -> Dict:
        """Get comprehensive user activity summary"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get recent activities
            cursor.execute("""
                SELECT date, activities_json, total_co2
                FROM daily_activities da
                LEFT JOIN carbon_footprints cf ON da.user_id = cf.user_id AND da.date = cf.date
                WHERE da.user_id = ? AND da.date >= date('now', '-{} days')
                ORDER BY da.date DESC
            """.format(days), (user_id,))
            
            activities = []
            total_co2 = 0
            activity_count = 0
            
            for row in cursor.fetchall():
                date, activities_json, co2 = row
                if activities_json:
                    activities.append({
                        'date': date,
                        'activities': json.loads(activities_json),
                        'co2': co2 or 0
                    })
                    total_co2 += co2 or 0
                    activity_count += 1
            
            conn.close()
            
            return {
                'activities': activities,
                'total_co2': round(total_co2, 2),
                'avg_daily_co2': round(total_co2 / max(activity_count, 1), 2),
                'activity_count': activity_count,
                'days_tracked': len(activities)
            }
            
        except Exception as e:
            print(f"Error getting activity summary: {e}")
            return {'activities': [], 'total_co2': 0, 'avg_daily_co2': 0, 'activity_count': 0, 'days_tracked': 0}

# Create global instance
activity_tracker = EnhancedActivityTracker() 