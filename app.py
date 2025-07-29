"""
Multi-User ClimateCoach Application
Main Streamlit app with authentication, activity tracking, and community features
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys

# Add src to path for imports
sys.path.append('src')

from src.core.auth import auth_service, activity_tracker, carbon_calculator
from src.core.recommendation_engine import recommendation_engine
from src.services.community_service import community_service

# Configure page
st.set_page_config(
    page_title="🌍 ClimateCoach - Multi-User Platform",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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

def init_session_state():
    """Initialize session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Login'

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
    footprints = carbon_calculator.get_user_footprints(user['id'], 30)
    activities = activity_tracker.get_user_activities(user['id'], 30)
    
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
            <h3>Activities Logged</h3>
            <h2>{len(activities)}</h2>
            <p>This month</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        community_stats = community_service.get_user_stats(user['id'])
        st.markdown(f"""
        <div class="metric-card">
            <h3>Community Posts</h3>
            <h2>{community_stats['posts_count']}</h2>
            <p>{community_stats['total_likes']} likes</p>
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
        
        # Breakdown chart
        col1, col2 = st.columns(2)
        
        with col1:
            if len(footprints) > 0:
                latest = footprints[0]
                categories = ['Transport', 'Energy', 'Food', 'Shopping']
                values = [latest['transport_co2'], latest['energy_co2'], 
                         latest['food_co2'], latest['shopping_co2']]
                
                fig_pie = px.pie(
                    values=values,
                    names=categories,
                    title="Today's Footprint Breakdown",
                    color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.subheader("🎯 Recent Achievements")
            st.info("🌱 **Eco Starter** - Logged your first activity!")
            if len(activities) >= 7:
                st.success("🔥 **Week Warrior** - 7 days of tracking!")
            if avg_daily_co2 < 20:
                st.success("🌿 **Low Carbon** - Below average emissions!")

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
            
            # Calculate carbon footprint using enhanced tracker
            from src.core.activity_tracker import activity_tracker
            result = activity_tracker.log_detailed_activity(user['id'], str(today), activities)
            
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
                
                import plotly.express as px
                fig = px.pie(
                    values=values,
                    names=categories,
                    title="Carbon Footprint Breakdown",
                    color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Generate and display recommendations
                recommendations = recommendation_engine.generate_personalized_recommendations(
                    user['id'], activities, footprint, user
                )
                
                if recommendations:
                    st.subheader("💡 Personalized Recommendations")
                    for i, rec in enumerate(recommendations[:5]):  # Show top 5
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

def community_page():
    """Community Discussion Page"""
    user = st.session_state.user
    st.header("👥 Community Discussions")
    
    tab1, tab2, tab3 = st.tabs(["📖 Recent Posts", "✍️ Create Post", "📈 Trending"])
    
    with tab1:
        # Filter options
        col1, col2 = st.columns([3, 1])
        with col1:
            category_filter = st.selectbox(
                "Filter by category:",
                ["all", "general", "transport", "energy", "food", "shopping", "tips"]
            )
        with col2:
            if st.button("🔄 Refresh"):
                st.rerun()
        
        # Get and display posts
        posts = community_service.get_posts(category_filter if category_filter != "all" else None)
        
        for post in posts:
            st.markdown(f"""
            <div class="post-card">
                <h4>{post['title']}</h4>
                <p><strong>By:</strong> {post['full_name']} (@{post['username']}) | 
                   <strong>Category:</strong> {post['category'].title()} | 
                   <strong>Likes:</strong> ❤️ {post['likes']}</p>
                <p>{post['content']}</p>
                <small>Posted: {post['created_at']}</small>
            </div>
            """, unsafe_allow_html=True)
            
            # Like and comment buttons
            col1, col2, col3 = st.columns([1, 1, 8])
            with col1:
                if st.button("❤️ Like", key=f"like_{post['id']}"):
                    community_service.like_post(post['id'])
                    st.rerun()
            
            with col2:
                if st.button("💬 Comments", key=f"comments_{post['id']}"):
                    st.session_state[f"show_comments_{post['id']}"] = True
            
            # Show comments if toggled
            if st.session_state.get(f"show_comments_{post['id']}", False):
                comments = community_service.get_comments(post['id'])
                
                if comments:
                    st.write("**Comments:**")
                    for comment in comments:
                        st.markdown(f"""
                        <div style="margin-left: 2rem; padding: 0.5rem; background: #f0f0f0; border-radius: 5px; margin: 0.5rem 0;">
                            <strong>{comment['full_name']}:</strong> {comment['content']}<br>
                            <small>{comment['created_at']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Add comment form
                with st.form(f"comment_form_{post['id']}"):
                    comment_text = st.text_area("Add a comment:", key=f"comment_{post['id']}")
                    if st.form_submit_button("Post Comment"):
                        if comment_text:
                            community_service.add_comment(post['id'], user['id'], comment_text)
                            st.success("Comment added!")
                            st.rerun()
    
    with tab2:
        st.subheader("Create a New Post")
        
        with st.form("create_post_form"):
            post_title = st.text_input("Post Title*")
            post_category = st.selectbox(
                "Category:",
                ["general", "transport", "energy", "food", "shopping", "tips"]
            )
            post_content = st.text_area("Content*", height=150)
            
            if st.form_submit_button("Create Post"):
                if post_title and post_content:
                    success = community_service.create_post(
                        user['id'], post_title, post_content, post_category
                    )
                    if success:
                        st.success("Post created successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to create post")
                else:
                    st.error("Please fill in all required fields")
    
    with tab3:
        st.subheader("📈 Trending Topics")
        trending = community_service.get_trending_topics()
        
        if trending:
            for topic in trending:
                st.markdown(f"""
                <div style="padding: 1rem; margin: 0.5rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                           color: white; border-radius: 10px;">
                    <h4>#{topic['category'].title()}</h4>
                    <p>{topic['post_count']} posts this week | {topic['total_likes']} total likes</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No trending topics this week. Be the first to start a discussion!")

def challenges_page():
    """Community Challenges Page"""
    user = st.session_state.user
    st.header("🏆 Community Challenges")
    
    tab1, tab2, tab3 = st.tabs(["🎯 Active Challenges", "📊 Leaderboard", "🏅 My Achievements"])
    
    with tab1:
        st.subheader("Join a Challenge")
        
        # Sample challenges (in a real app, these would come from the database)
        challenges = [
            {
                "title": "🚗 Car-Free Week",
                "description": "Go car-free for 7 days and track your carbon savings!",
                "category": "transport",
                "duration": "7 days",
                "participants": 45,
                "target_savings": 10.5,
                "current_savings": 8.2
            },
            {
                "title": "💡 Energy Efficiency",
                "description": "Reduce your daily energy consumption by 20%",
                "category": "energy",
                "duration": "14 days",
                "participants": 32,
                "target_savings": 15.0,
                "current_savings": 12.8
            },
            {
                "title": "🥗 Meatless Monday",
                "description": "Try vegetarian meals every Monday for a month",
                "category": "food",
                "duration": "30 days",
                "participants": 67,
                "target_savings": 25.0,
                "current_savings": 18.5
            }
        ]
        
        for challenge in challenges:
            progress = (challenge["current_savings"] / challenge["target_savings"]) * 100
            
            st.markdown(f"""
            <div style="border: 2px solid #2E8B57; border-radius: 10px; padding: 1rem; margin: 1rem 0;">
                <h4>{challenge['title']}</h4>
                <p>{challenge['description']}</p>
                <p><strong>Category:</strong> {challenge['category'].title()} | 
                   <strong>Duration:</strong> {challenge['duration']} | 
                   <strong>Participants:</strong> {challenge['participants']}</p>
                <div style="background: #f0f0f0; border-radius: 5px; height: 20px; margin: 10px 0;">
                    <div style="background: #4CAF50; height: 100%; width: {progress}%; border-radius: 5px;"></div>
                </div>
                <p><strong>Progress:</strong> {challenge['current_savings']:.1f} / {challenge['target_savings']:.1f} kg CO₂ saved</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("Join Challenge", key=f"join_{challenge['title']}"):
                    st.success("Challenge joined! Start tracking your progress.")
            with col2:
                if st.button("View Details", key=f"details_{challenge['title']}"):
                    st.info("Detailed challenge information and tips coming soon!")
    
    with tab2:
        st.subheader("🏆 Community Leaderboard")
        
        # Sample leaderboard data
        leaders = [
            {"name": "Sarah Green", "co2_saved": 45.2, "badges": 8, "rank": 1},
            {"name": "Mike Johnson", "co2_saved": 38.7, "badges": 6, "rank": 2},
            {"name": "Emma Wilson", "co2_saved": 32.1, "badges": 5, "rank": 3},
            {"name": "David Chen", "co2_saved": 28.9, "badges": 4, "rank": 4},
            {"name": "Lisa Brown", "co2_saved": 25.4, "badges": 3, "rank": 5}
        ]
        
        for i, leader in enumerate(leaders):
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
            st.markdown(f"""
            <div style="display: flex; align-items: center; padding: 0.5rem; margin: 0.5rem 0; 
                       background: {'#FFD700' if i < 3 else '#f8f9fa'}; border-radius: 5px;">
                <span style="font-size: 1.5rem; margin-right: 1rem;">{medal}</span>
                <div style="flex-grow: 1;">
                    <strong>{leader['name']}</strong><br>
                    <small>{leader['co2_saved']:.1f} kg CO₂ saved | {leader['badges']} badges</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.subheader("🏅 Your Achievements")
        
        # Sample achievements
        achievements = [
            {"title": "🌱 Eco Starter", "description": "Logged your first activity", "earned": "2024-01-15", "icon": "🌱"},
            {"title": "🔥 Week Warrior", "description": "Tracked activities for 7 days", "earned": "2024-01-22", "icon": "🔥"},
            {"title": "🌿 Low Carbon", "description": "Achieved below-average emissions", "earned": "2024-01-25", "icon": "🌿"},
            {"title": "🚗 Transport Hero", "description": "Used public transport 5 days in a row", "earned": "2024-01-28", "icon": "🚗"}
        ]
        
        for achievement in achievements:
            st.markdown(f"""
            <div style="display: flex; align-items: center; padding: 1rem; margin: 0.5rem 0; 
                       background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       color: white; border-radius: 10px;">
                <span style="font-size: 2rem; margin-right: 1rem;">{achievement['icon']}</span>
                <div>
                    <h4>{achievement['title']}</h4>
                    <p>{achievement['description']}</p>
                    <small>Earned: {achievement['earned']}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)

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
                ["Dashboard", "Log Activities", "Community", "Challenges", "Profile", "Logout"]
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
        elif page == "Community":
            community_page()
        elif page == "Challenges":
            challenges_page()
        elif page == "Profile":
            st.header("👤 User Profile")
            st.json(user)
            
            if st.button("Update Profile"):
                st.info("Profile update feature coming soon!")

if __name__ == "__main__":
    main()
