#!/usr/bin/env python3
"""
ClimateCoach - Production-Ready Carbon Footprint Reduction Platform
A million-dollar startup ready application for tracking and reducing carbon footprints
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
import sqlite3
import hashlib
from typing import Optional, Dict, List
import json

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure page
st.set_page_config(
    page_title="🌍 ClimateCoach - Carbon Footprint Reduction Platform",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for production-ready UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(90deg, #2E8B57, #32CD32);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .carbon-savings {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .login-form {
        background: #f0f8f0;
        padding: 2rem;
        border-radius: 10px;
        margin: 2rem 0;
    }
    .activity-form {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .post-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #2E8B57;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
    }
    .recommendation-card {
        background: #ffffff !important;
        border: 2px solid #e0e0e0 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    .recommendation-title {
        color: #2E8B57 !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        margin-bottom: 0.5rem !important;
    }
    .recommendation-description {
        color: #333333 !important;
        line-height: 1.4 !important;
        margin-bottom: 0.5rem !important;
    }
    .recommendation-details {
        color: #666666 !important;
        font-size: 0.9em !important;
    }
</style>
""", unsafe_allow_html=True)

# Database and Core Services
class DatabaseManager:
    def __init__(self, db_path: str = "climatecoach.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with all required tables"""
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
                activities_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, date)
            )
        """)
        
        # Carbon footprints table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS carbon_footprints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                transport_co2 REAL,
                energy_co2 REAL,
                food_co2 REAL,
                shopping_co2 REAL,
                waste_co2 REAL,
                water_co2 REAL,
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
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                icon TEXT DEFAULT '🏆',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        conn.commit()
        conn.close()

class AuthService:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username: str, email: str, password: str, full_name: str,
                     location: str = "", diet_preference: str = "omnivore",
                     transport_preference: str = "car", household_size: int = 2) -> bool:
        """Register a new user"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
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
            
        except Exception as e:
            print(f"Error registering user: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user login"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute("""
                SELECT id, username, email, full_name, location, diet_preference,
                       transport_preference, household_size
                FROM users 
                WHERE username = ? AND password_hash = ?
            """, (username, password_hash))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'full_name': user[3],
                    'location': user[4],
                    'diet_preference': user[5],
                    'transport_preference': user[6],
                    'household_size': user[7]
                }
            return None
            
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None

class CarbonCalculator:
    def __init__(self):
        self.emission_factors = {
            'transport': {
                'car': 0.2, 'bus': 0.05, 'train': 0.04, 'bike': 0.0, 'walk': 0.0,
                'plane': 0.25, 'electric_car': 0.06, 'hybrid_car': 0.12,
                'motorcycle': 0.15, 'scooter': 0.08
            },
            'energy': {
                'electricity': 0.5, 'natural_gas': 2.0, 'heating_oil': 2.7,
                'propane': 1.6, 'solar': 0.0, 'wind': 0.0
            },
            'food': {
                'beef': 13.3, 'lamb': 13.3, 'pork': 5.8, 'chicken': 2.9,
                'fish': 3.0, 'eggs': 1.4, 'dairy': 1.4, 'vegetables': 0.4,
                'fruits': 0.4, 'grains': 0.5, 'nuts': 0.3, 'plant_based': 0.3
            },
            'shopping': {
                'clothing': 0.5, 'electronics': 2.0, 'furniture': 5.0,
                'books': 0.1, 'cosmetics': 0.2, 'household': 0.3,
                'food_items': 0.1, 'second_hand': 0.05
            },
            'waste': {
                'landfill': 0.5, 'recycling': 0.1, 'composting': 0.0
            },
            'water': {
                'usage': 0.0003
            }
        }
    
    def calculate_footprint(self, activities: Dict) -> Dict:
        """Calculate comprehensive carbon footprint"""
        transport_co2 = self._calculate_transport(activities)
        energy_co2 = self._calculate_energy(activities)
        food_co2 = self._calculate_food(activities)
        shopping_co2 = self._calculate_shopping(activities)
        waste_co2 = self._calculate_waste(activities)
        water_co2 = self._calculate_water(activities)
        
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
    
    def _calculate_transport(self, activities: Dict) -> float:
        transport_co2 = 0
        transport_activities = activities.get('transport', [])
        
        if isinstance(transport_activities, list):
            for trip in transport_activities:
                mode = trip.get('mode', 'car')
                distance = trip.get('distance_km', 0)
                transport_co2 += distance * self.emission_factors['transport'].get(mode, 0.2)
        else:
            mode = activities.get('transport_mode', 'car')
            distance = activities.get('distance_km', 0)
            transport_co2 = distance * self.emission_factors['transport'].get(mode, 0.2)
        
        return transport_co2
    
    def _calculate_energy(self, activities: Dict) -> float:
        energy_co2 = 0
        energy_co2 += activities.get('electricity_kwh', 0) * self.emission_factors['energy']['electricity']
        energy_co2 += activities.get('natural_gas_m3', 0) * self.emission_factors['energy']['natural_gas']
        energy_co2 += activities.get('heating_oil_liters', 0) * self.emission_factors['energy']['heating_oil']
        return energy_co2
    
    def _calculate_food(self, activities: Dict) -> float:
        food_co2 = 0
        food_items = activities.get('food_items', {})
        
        for food_type, amount_kg in food_items.items():
            if food_type in self.emission_factors['food']:
                food_co2 += amount_kg * self.emission_factors['food'][food_type]
        
        # Legacy meal-based calculation
        meat_meals = activities.get('food_meals_meat', 0)
        veg_meals = activities.get('food_meals_veg', 0)
        food_co2 += meat_meals * 2.5 + veg_meals * 0.5
        
        return food_co2
    
    def _calculate_shopping(self, activities: Dict) -> float:
        shopping_co2 = 0
        shopping_items = activities.get('shopping_items', {})
        
        for item_type, count in shopping_items.items():
            if item_type in self.emission_factors['shopping']:
                shopping_co2 += count * self.emission_factors['shopping'][item_type]
        
        return shopping_co2
    
    def _calculate_waste(self, activities: Dict) -> float:
        waste_co2 = 0
        waste_co2 += activities.get('waste_landfill_kg', 0) * self.emission_factors['waste']['landfill']
        waste_co2 += activities.get('waste_recycling_kg', 0) * self.emission_factors['waste']['recycling']
        waste_co2 += activities.get('waste_composting_kg', 0) * self.emission_factors['waste']['composting']
        return waste_co2
    
    def _calculate_water(self, activities: Dict) -> float:
        water_usage_liters = activities.get('water_usage_liters', 0)
        return water_usage_liters * self.emission_factors['water']['usage']

class ActivityTracker:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.carbon_calculator = CarbonCalculator()
    
    def log_activity(self, user_id: int, date: str, activities: Dict) -> Dict:
        """Log user activities and calculate footprint"""
        try:
            # Calculate carbon footprint
            footprint = self.carbon_calculator.calculate_footprint(activities)
            
            # Save to database
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            # Save activities
            cursor.execute("""
                INSERT OR REPLACE INTO daily_activities (user_id, date, activities_json)
                VALUES (?, ?, ?)
            """, (user_id, date, json.dumps(activities)))
            
            # Save footprint
            cursor.execute("""
                INSERT OR REPLACE INTO carbon_footprints
                (user_id, date, transport_co2, energy_co2, food_co2, shopping_co2,
                 waste_co2, water_co2, total_co2)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, date,
                footprint['transport_co2'], footprint['energy_co2'], footprint['food_co2'],
                footprint['shopping_co2'], footprint['waste_co2'], footprint['water_co2'],
                footprint['total_co2']
            ))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'footprint': footprint, 'activities': activities}
            
        except Exception as e:
            print(f"Error logging activity: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_user_footprints(self, user_id: int, days: int = 30) -> List[Dict]:
        """Get user's carbon footprint history"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT date, transport_co2, energy_co2, food_co2, shopping_co2,
                       waste_co2, water_co2, total_co2
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
                    'waste_co2': row[5],
                    'water_co2': row[6],
                    'total_co2': row[7]
                })
            
            conn.close()
            return footprints
            
        except Exception as e:
            print(f"Error getting footprints: {e}")
            return []

# Enhanced recommendation engine is imported from src/core/recommendation_engine.py

# Initialize services
db_manager = DatabaseManager()
auth_service = AuthService(db_manager)
activity_tracker = ActivityTracker(db_manager)

# Import and use the enhanced recommendation engine
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from core.recommendation_engine import recommendation_engine

# Session state management
def init_session_state():
    """Initialize session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None

# Main application functions
def login_page():
    """Login and Registration Page"""
    st.markdown('<h1 class="main-header">🌍 ClimateCoach Login</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.markdown('<div class="login-form">', unsafe_allow_html=True)
        st.subheader("Login to Your Account")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")
            
            if login_button:
                if username and password:
                    user = auth_service.authenticate_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.success(f"Welcome back, {user['full_name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.error("Please enter both username and password")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="login-form">', unsafe_allow_html=True)
        st.subheader("Create New Account")
        
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                reg_username = st.text_input("Username*")
                reg_email = st.text_input("Email*")
                reg_password = st.text_input("Password*", type="password")
                reg_full_name = st.text_input("Full Name*")
            
            with col2:
                reg_location = st.text_input("Location")
                reg_diet = st.selectbox("Diet Preference", 
                                      ["omnivore", "vegetarian", "vegan", "flexitarian"])
                reg_transport = st.selectbox("Primary Transport", 
                                           ["car", "bus", "train", "bike", "walk"])
                reg_household = st.number_input("Household Size", min_value=1, max_value=10, value=2)
            
            register_button = st.form_submit_button("Create Account")
            
            if register_button:
                if reg_username and reg_email and reg_password and reg_full_name:
                    success = auth_service.register_user(
                        reg_username, reg_email, reg_password, reg_full_name,
                        reg_location, reg_diet, reg_transport, reg_household
                    )
                    if success:
                        st.success("Account created successfully! Please login.")
                    else:
                        st.error("Username or email already exists")
                else:
                    st.error("Please fill in all required fields (*)")
        
        st.markdown('</div>', unsafe_allow_html=True)

def dashboard_page():
    """User Dashboard"""
    user = st.session_state.user
    st.markdown(f'<h1 class="main-header">🌍 Welcome back, {user["full_name"]}!</h1>', unsafe_allow_html=True)
    
    # Get user's carbon footprint data
    footprints = activity_tracker.get_user_footprints(user['id'], 30)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_co2_month = sum(f['total_co2'] for f in footprints)
    avg_daily_co2 = total_co2_month / max(len(footprints), 1)
    
    with col1:
        st.markdown(f"""
        <div class="carbon-savings">
            <h3>Monthly CO₂</h3>
            <h2>{total_co2_month:.1f} kg</h2>
            <p>Last 30 days</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Daily Average</h3>
            <h2>{avg_daily_co2:.1f} kg</h2>
            <p>CO₂ per day</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Days Tracked</h3>
            <h2>{len(footprints)}</h2>
            <p>This month</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Location</h3>
            <h2>{user['location']}</h2>
            <p>Your area</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Carbon footprint trend chart
    if footprints:
        st.subheader("📊 Your Carbon Footprint Trend")
        
        df = pd.DataFrame(footprints)
        df['date'] = pd.to_datetime(df['date'])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['total_co2'],
            mode='lines+markers',
            name='Daily CO₂',
            line=dict(color='#2E8B57', width=3)
        ))
        
        fig.update_layout(
            title="Daily Carbon Footprint (kg CO₂)",
            xaxis_title="Date",
            yaxis_title="CO₂ (kg)",
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)

def activity_log_page():
    """Enhanced Daily Activity Logging Page"""
    user = st.session_state.user
    st.header("📝 Log Your Daily Activities")
    
    # Today's date
    today = datetime.now().date()
    
    st.markdown('<div class="activity-form">', unsafe_allow_html=True)
    
    with st.form("activity_form"):
        st.subheader(f"Activities for {today}")
        
        # Transportation Section
        st.markdown("### 🚗 Transportation")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            transport_mode = st.selectbox(
                "Transport Mode:",
                ["car", "bus", "train", "bike", "walk", "plane", "electric_car", "hybrid_car", "motorcycle", "scooter"]
            )
        
        with col2:
            distance_km = st.number_input("Distance (km):", 
                                        min_value=0.0, value=0.0, step=0.1)
        
        with col3:
            trips_count = st.number_input("Number of trips:", 
                                        min_value=1, max_value=10, value=1)
        
        # Energy Usage Section
        st.markdown("### ⚡ Energy Usage")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            electricity_kwh = st.number_input("Electricity (kWh):", 
                                           min_value=0.0, value=0.0, step=0.1)
        
        with col2:
            gas_m3 = st.number_input("Natural Gas (m³):", 
                                   min_value=0.0, value=0.0, step=0.1)
        
        with col3:
            heating_oil = st.number_input("Heating Oil (liters):", 
                                        min_value=0.0, value=0.0, step=0.1)
        
        # Food Consumption Section
        st.markdown("### 🍽️ Food Consumption")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Meat & Dairy:**")
            beef_kg = st.number_input("Beef (kg):", min_value=0.0, value=0.0, step=0.1)
            chicken_kg = st.number_input("Chicken (kg):", min_value=0.0, value=0.0, step=0.1)
            dairy_kg = st.number_input("Dairy (kg):", min_value=0.0, value=0.0, step=0.1)
        
        with col2:
            st.markdown("**Plant-based:**")
            vegetables_kg = st.number_input("Vegetables (kg):", min_value=0.0, value=0.0, step=0.1)
            fruits_kg = st.number_input("Fruits (kg):", min_value=0.0, value=0.0, step=0.1)
            grains_kg = st.number_input("Grains (kg):", min_value=0.0, value=0.0, step=0.1)
        
        # Shopping Section
        st.markdown("### 🛒 Shopping")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            clothing_items = st.number_input("Clothing items:", min_value=0, max_value=20, value=0)
            electronics_items = st.number_input("Electronics:", min_value=0, max_value=10, value=0)
        
        with col2:
            household_items = st.number_input("Household items:", min_value=0, max_value=20, value=0)
            food_items = st.number_input("Food items:", min_value=0, max_value=50, value=0)
        
        with col3:
            second_hand_items = st.number_input("Second-hand items:", min_value=0, max_value=20, value=0)
        
        # Waste Section
        st.markdown("### 🗑️ Waste Management")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            landfill_kg = st.number_input("Landfill waste (kg):", min_value=0.0, value=0.0, step=0.1)
        
        with col2:
            recycling_kg = st.number_input("Recycling (kg):", min_value=0.0, value=0.0, step=0.1)
        
        with col3:
            composting_kg = st.number_input("Composting (kg):", min_value=0.0, value=0.0, step=0.1)
        
        # Water Usage
        st.markdown("### 💧 Water Usage")
        water_usage_liters = st.number_input("Water usage (liters):", 
                                           min_value=0.0, value=0.0, step=1.0)
        
        submit_button = st.form_submit_button("📊 Calculate My Carbon Footprint")
        
        if submit_button:
            # Prepare comprehensive activity data
            activities = {
                'transport': [{
                    'mode': transport_mode,
                    'distance_km': distance_km,
                    'trips': trips_count
                }],
                'electricity_kwh': electricity_kwh,
                'natural_gas_m3': gas_m3,
                'heating_oil_liters': heating_oil,
                'food_items': {
                    'beef': beef_kg,
                    'chicken': chicken_kg,
                    'dairy': dairy_kg,
                    'vegetables': vegetables_kg,
                    'fruits': fruits_kg,
                    'grains': grains_kg
                },
                'shopping_items': {
                    'clothing': clothing_items,
                    'electronics': electronics_items,
                    'household': household_items,
                    'food_items': food_items,
                    'second_hand': second_hand_items
                },
                'waste_landfill_kg': landfill_kg,
                'waste_recycling_kg': recycling_kg,
                'waste_composting_kg': composting_kg,
                'water_usage_liters': water_usage_liters
            }
            
            # Log activity and calculate footprint
            result = activity_tracker.log_activity(user['id'], str(today), activities)
            
            if result['success']:
                st.success("✅ Activities logged successfully!")
                
                # Show comprehensive results
                footprint = result['footprint']
                st.subheader("📊 Your Carbon Footprint Analysis")
                
                # Key metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total CO₂", f"{footprint['total_co2']} kg", 
                             delta=f"{footprint['total_co2'] - 20:.1f} kg vs avg")
                with col2:
                    st.metric("Transport", f"{footprint['transport_co2']} kg", 
                             f"{footprint['breakdown']['transport_percent']}%")
                with col3:
                    st.metric("Energy", f"{footprint['energy_co2']} kg", 
                             f"{footprint['breakdown']['energy_percent']}%")
                with col4:
                    st.metric("Food", f"{footprint['food_co2']} kg", 
                             f"{footprint['breakdown']['food_percent']}%")
                
                # Detailed breakdown chart
                categories = ['Transport', 'Energy', 'Food', 'Shopping', 'Waste', 'Water']
                values = [footprint['transport_co2'], footprint['energy_co2'], 
                         footprint['food_co2'], footprint['shopping_co2'], 
                         footprint['waste_co2'], footprint['water_co2']]
                
                fig = px.pie(
                    values=values,
                    names=categories,
                    title="Carbon Footprint Breakdown",
                    color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Generate and display recommendations using enhanced AI engine
                recommendations = recommendation_engine.generate_personalized_recommendations(
                    user['id'], activities, footprint, user
                )
                
                if recommendations:
                    st.subheader("💡 Personalized Recommendations")
                    for i, rec in enumerate(recommendations[:5]):
                        impact_color = "#4CAF50" if rec['impact'] == 'High' else "#FF9800" if rec['impact'] == 'Medium' else "#FF5722"
                        st.markdown(f"""
                        <div class="recommendation-card" style="border-left: 4px solid {impact_color} !important;">
                            <h4 class="recommendation-title">🎯 {rec['title']}</h4>
                            <p class="recommendation-description">{rec['description']}</p>
                            <small class="recommendation-details">Impact: {rec['impact']} | Difficulty: {rec['difficulty']} | Potential Savings: {rec.get('co2_savings', 0):.1f} kg CO₂</small>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Show comparison with average
                avg_daily_co2 = 20  # kg CO2 per day average
                if footprint['total_co2'] < avg_daily_co2:
                    st.success(f"🎉 Great job! Your footprint is {avg_daily_co2 - footprint['total_co2']:.1f} kg below the daily average!")
                else:
                    st.warning(f"📈 Your footprint is {footprint['total_co2'] - avg_daily_co2:.1f} kg above the daily average. Try the recommendations above!")
            else:
                st.error("Failed to log activities. Please try again.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main application"""
    init_session_state()
    
    # Check if user is logged in
    if not st.session_state.logged_in:
        login_page()
    else:
        user = st.session_state.user
        
        # Sidebar navigation
        with st.sidebar:
            st.markdown(f"### 👋 Hello, {user['full_name']}")
            st.markdown(f"📍 {user['location']}")
            
            # Navigation menu
            page = st.selectbox(
                "Navigate to:",
                ["Dashboard", "Log Activities", "Profile", "Logout"]
            )
            
            if page == "Logout":
                st.session_state.logged_in = False
                st.session_state.user = None
                st.rerun()
        
        # Main content based on selected page
        if page == "Dashboard":
            dashboard_page()
        elif page == "Log Activities":
            activity_log_page()
        elif page == "Profile":
            st.header("👤 User Profile")
            st.json(user)
            
            if st.button("Update Profile"):
                st.info("Profile update feature coming soon!")

if __name__ == "__main__":
    main() 