"""
User Authentication System for ClimateCoach
"""

import hashlib
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import streamlit as st

class UserAuth:
    def __init__(self, db_path: str = "climatecoach.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                location TEXT,
                diet_preference TEXT DEFAULT 'omnivore',
                transport_preference TEXT DEFAULT 'car',
                household_size INTEGER DEFAULT 2,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        
        # Daily activities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                transport_mode TEXT,
                distance_km REAL,
                energy_kwh REAL,
                water_usage REAL,
                waste_kg REAL,
                food_meals_meat INTEGER DEFAULT 0,
                food_meals_veg INTEGER DEFAULT 0,
                shopping_items INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, date)
            )
        """)
        
        # Carbon footprint calculations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS carbon_footprints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                transport_co2 REAL,
                energy_co2 REAL,
                food_co2 REAL,
                shopping_co2 REAL,
                total_co2 REAL,
                calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Community posts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS community_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                likes INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Community comments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS community_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES community_posts (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # User achievements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                achievement_type TEXT NOT NULL,
                achievement_name TEXT NOT NULL,
                description TEXT,
                points INTEGER DEFAULT 0,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username: str, email: str, password: str, full_name: str, 
                     location: str = "", diet_preference: str = "omnivore", 
                     transport_preference: str = "car", household_size: int = 2) -> bool:
        """Register a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, full_name, location, 
                                 diet_preference, transport_preference, household_size)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (username, email, password_hash, full_name, location, 
                  diet_preference, transport_preference, household_size))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"Registration error: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user login"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute("""
                SELECT id, username, email, full_name, location, diet_preference, 
                       transport_preference, household_size
                FROM users 
                WHERE username = ? AND password_hash = ?
            """, (username, password_hash))
            
            user_data = cursor.fetchone()
            
            if user_data:
                # Update last login
                cursor.execute("""
                    UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
                """, (user_data[0],))
                conn.commit()
                
                # Return user info as dictionary
                user_info = {
                    'id': user_data[0],
                    'username': user_data[1],
                    'email': user_data[2],
                    'full_name': user_data[3],
                    'location': user_data[4],
                    'diet_preference': user_data[5],
                    'transport_preference': user_data[6],
                    'household_size': user_data[7]
                }
                
                conn.close()
                return user_info
            
            conn.close()
            return None
            
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user information by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, email, full_name, location, diet_preference, 
                       transport_preference, household_size
                FROM users WHERE id = ?
            """, (user_id,))
            
            user_data = cursor.fetchone()
            conn.close()
            
            if user_data:
                return {
                    'id': user_data[0],
                    'username': user_data[1],
                    'email': user_data[2],
                    'full_name': user_data[3],
                    'location': user_data[4],
                    'diet_preference': user_data[5],
                    'transport_preference': user_data[6],
                    'household_size': user_data[7]
                }
            return None
            
        except Exception as e:
            print(f"Error getting user: {e}")
            return None

class ActivityTracker:
    def __init__(self, db_path: str = "climatecoach.db"):
        self.db_path = db_path
    
    def log_daily_activity(self, user_id: int, date: str, activities: Dict) -> bool:
        """Log daily activities for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO daily_activities 
                (user_id, date, transport_mode, distance_km, energy_kwh, water_usage, 
                 waste_kg, food_meals_meat, food_meals_veg, shopping_items)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, date,
                activities.get('transport_mode', ''),
                activities.get('distance_km', 0),
                activities.get('energy_kwh', 0),
                activities.get('water_usage', 0),
                activities.get('waste_kg', 0),
                activities.get('food_meals_meat', 0),
                activities.get('food_meals_veg', 0),
                activities.get('shopping_items', 0)
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error logging activity: {e}")
            return False
    
    def get_user_activities(self, user_id: int, days: int = 30) -> List[Dict]:
        """Get user's recent activities"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT date, transport_mode, distance_km, energy_kwh, water_usage,
                       waste_kg, food_meals_meat, food_meals_veg, shopping_items
                FROM daily_activities 
                WHERE user_id = ? 
                ORDER BY date DESC 
                LIMIT ?
            """, (user_id, days))
            
            activities = []
            for row in cursor.fetchall():
                activities.append({
                    'date': row[0],
                    'transport_mode': row[1],
                    'distance_km': row[2],
                    'energy_kwh': row[3],
                    'water_usage': row[4],
                    'waste_kg': row[5],
                    'food_meals_meat': row[6],
                    'food_meals_veg': row[7],
                    'shopping_items': row[8]
                })
            
            conn.close()
            return activities
            
        except Exception as e:
            print(f"Error getting activities: {e}")
            return []

class CarbonCalculator:
    def __init__(self, db_path: str = "climatecoach.db"):
        self.db_path = db_path
        
        # Carbon emission factors (kg CO2 per unit)
        self.emission_factors = {
            'transport': {
                'car': 0.21,      # per km
                'bus': 0.08,      # per km
                'train': 0.04,    # per km
                'bike': 0.0,      # per km
                'walk': 0.0,      # per km
                'plane': 0.25     # per km
            },
            'energy': 0.45,       # per kWh
            'food': {
                'meat_meal': 7.2,     # per meal
                'veg_meal': 1.5       # per meal
            },
            'shopping': 2.3,      # per item (average)
            'water': 0.36,        # per liter
            'waste': 0.5          # per kg
        }
    
    def calculate_daily_footprint(self, activities: Dict) -> Dict:
        """Calculate carbon footprint from daily activities"""
        # Transport emissions
        transport_mode = activities.get('transport_mode', 'car')
        distance = activities.get('distance_km', 0)
        transport_co2 = distance * self.emission_factors['transport'].get(transport_mode, 0.21)
        
        # Energy emissions
        energy_kwh = activities.get('energy_kwh', 0)
        energy_co2 = energy_kwh * self.emission_factors['energy']
        
        # Food emissions
        meat_meals = activities.get('food_meals_meat', 0)
        veg_meals = activities.get('food_meals_veg', 0)
        food_co2 = (meat_meals * self.emission_factors['food']['meat_meal'] + 
                   veg_meals * self.emission_factors['food']['veg_meal'])
        
        # Shopping emissions
        shopping_items = activities.get('shopping_items', 0)
        shopping_co2 = shopping_items * self.emission_factors['shopping']
        
        # Water and waste (bonus calculations)
        water_usage = activities.get('water_usage', 0)
        waste_kg = activities.get('waste_kg', 0)
        water_co2 = water_usage * self.emission_factors['water']
        waste_co2 = waste_kg * self.emission_factors['waste']
        
        total_co2 = transport_co2 + energy_co2 + food_co2 + shopping_co2 + water_co2 + waste_co2
        
        return {
            'transport_co2': round(transport_co2, 2),
            'energy_co2': round(energy_co2, 2),
            'food_co2': round(food_co2, 2),
            'shopping_co2': round(shopping_co2, 2),
            'water_co2': round(water_co2, 2),
            'waste_co2': round(waste_co2, 2),
            'total_co2': round(total_co2, 2)
        }
    
    def save_carbon_footprint(self, user_id: int, date: str, footprint: Dict) -> bool:
        """Save calculated carbon footprint to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO carbon_footprints
                (user_id, date, transport_co2, energy_co2, food_co2, shopping_co2, total_co2)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, date,
                footprint['transport_co2'],
                footprint['energy_co2'],
                footprint['food_co2'],
                footprint['shopping_co2'],
                footprint['total_co2']
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error saving footprint: {e}")
            return False
    
    def get_user_footprints(self, user_id: int, days: int = 30) -> List[Dict]:
        """Get user's carbon footprint history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT date, transport_co2, energy_co2, food_co2, shopping_co2, total_co2
                FROM carbon_footprints 
                WHERE user_id = ? 
                ORDER BY date DESC 
                LIMIT ?
            """, (user_id, days))
            
            footprints = []
            for row in cursor.fetchall():
                footprints.append({
                    'date': row[0],
                    'transport_co2': row[1],
                    'energy_co2': row[2],
                    'food_co2': row[3],
                    'shopping_co2': row[4],
                    'total_co2': row[5]
                })
            
            conn.close()
            return footprints
            
        except Exception as e:
            print(f"Error getting footprints: {e}")
            return []

class RecommendationEngine:
    def __init__(self):
        pass
    
    def generate_recommendations(self, activities: Dict, footprint: Dict, user_profile: Dict) -> List[Dict]:
        """Generate personalized recommendations based on user data"""
        recommendations = []
        
        # Transport recommendations
        if footprint['transport_co2'] > 5:  # High transport emissions
            if activities.get('transport_mode') == 'car':
                recommendations.append({
                    'category': 'transport',
                    'title': '🚌 Switch to Public Transport',
                    'description': f"You could save {footprint['transport_co2'] * 0.6:.1f} kg CO₂ daily by using public transport instead of driving.",
                    'impact': 'High',
                    'difficulty': 'Easy',
                    'potential_savings': footprint['transport_co2'] * 0.6
                })
            
            recommendations.append({
                'category': 'transport',
                'title': '🚲 Try Cycling or Walking',
                'description': f"For trips under 5km, cycling could eliminate {footprint['transport_co2']:.1f} kg CO₂ daily.",
                'impact': 'High',
                'difficulty': 'Medium',
                'potential_savings': footprint['transport_co2']
            })
        
        # Energy recommendations
        if footprint['energy_co2'] > 8:  # High energy usage
            recommendations.append({
                'category': 'energy',
                'title': '💡 Optimize Energy Usage',
                'description': f"Reducing energy consumption by 20% could save {footprint['energy_co2'] * 0.2:.1f} kg CO₂ daily.",
                'impact': 'Medium',
                'difficulty': 'Easy',
                'potential_savings': footprint['energy_co2'] * 0.2
            })
        
        # Food recommendations
        if activities.get('food_meals_meat', 0) > 2:  # High meat consumption
            recommendations.append({
                'category': 'food',
                'title': '🌱 Try Plant-Based Meals',
                'description': f"Replacing 1 meat meal with a vegetarian meal could save {7.2 - 1.5:.1f} kg CO₂ per meal.",
                'impact': 'High',
                'difficulty': 'Medium',
                'potential_savings': 5.7
            })
        
        # Shopping recommendations
        if footprint['shopping_co2'] > 5:  # High shopping emissions
            recommendations.append({
                'category': 'shopping',
                'title': '🛒 Buy Less, Choose Better',
                'description': f"Reducing impulse purchases by 30% could save {footprint['shopping_co2'] * 0.3:.1f} kg CO₂.",
                'impact': 'Medium',
                'difficulty': 'Medium',
                'potential_savings': footprint['shopping_co2'] * 0.3
            })
        
        return recommendations

# Initialize services
auth_service = UserAuth()
activity_tracker = ActivityTracker()
carbon_calculator = CarbonCalculator()
recommendation_engine = RecommendationEngine()
