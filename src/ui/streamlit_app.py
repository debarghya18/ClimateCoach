import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from streamlit_option_menu import option_menu
from streamlit_folium import st_folium
import folium

# Import services (with fallbacks for missing dependencies)
try:
    # Try to import services if available
    pass  # We'll implement fallbacks for now
except ImportError:
    pass

# Configure page
st.set_page_config(
    page_title="🌍 ClimateCoach",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
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
    .challenge-card {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

def load_sample_data():
    """Load sample data for demonstration"""
    # Sample carbon footprint data
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    carbon_data = pd.DataFrame({
        'date': dates,
        'transport': np.random.normal(5.2, 1.5, len(dates)),
        'energy': np.random.normal(8.3, 2.1, len(dates)),
        'shopping': np.random.normal(3.1, 0.8, len(dates)),
        'food': np.random.normal(4.5, 1.2, len(dates))
    })
    carbon_data['total'] = carbon_data[['transport', 'energy', 'shopping', 'food']].sum(axis=1)
    
    return carbon_data

def create_dashboard():
    """Create the main dashboard"""
    st.markdown('<h1 class="main-header">🌍 ClimateCoach Dashboard</h1>', unsafe_allow_html=True)
    
    # Load sample data
    carbon_data = load_sample_data()
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="carbon-savings">
            <h3>Total CO₂ Saved</h3>
            <h2>2,847 kg</h2>
            <p>This month: +12%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>Green Actions</h3>
            <h2>156</h2>
            <p>This week: +8</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>Eco Score</h3>
            <h2>847/1000</h2>
            <p>Level: Eco Champion</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>Community Rank</h3>
            <h2>#23</h2>
            <p>Top 5% globally</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Carbon footprint trends
    st.subheader("📊 Your Carbon Footprint Trends")
    
    # Create interactive chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=carbon_data['date'][-30:], 
        y=carbon_data['total'][-30:],
        mode='lines+markers',
        name='Daily Carbon Footprint',
        line=dict(color='#2E8B57', width=3)
    ))
    
    fig.update_layout(
        title="Daily Carbon Footprint (kg CO₂)",
        xaxis_title="Date",
        yaxis_title="CO₂ (kg)",
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Breakdown by category
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏷️ Footprint Breakdown")
        categories = ['Transport', 'Energy', 'Shopping', 'Food']
        values = [5.2, 8.3, 3.1, 4.5]
        
        fig_pie = px.pie(
            values=values,
            names=categories,
            title="Carbon Footprint by Category",
            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Weekly Goals Progress")
        goals = {
            'Use public transport': 85,
            'Reduce energy consumption': 72,
            'Buy local products': 91,
            'Eat plant-based meals': 68
        }
        
        for goal, progress in goals.items():
            st.write(f"**{goal}**")
            st.progress(progress / 100)
            st.write(f"{progress}% complete")
            st.write("---")

def create_ai_recommendations():
    """Create AI recommendations page"""
    st.header("🤖 AI-Powered Recommendations")
    
    # Personalized insights
    st.subheader("💡 Personalized Insights")
    
    insights = [
        {
            'icon': '🚌',
            'title': 'Transportation Optimization',
            'description': 'Switch to public transport for your commute to save 2.3 kg CO₂ daily',
            'impact': 'High Impact',
            'difficulty': 'Easy'
        },
        {
            'icon': '💡',
            'title': 'Smart Energy Usage',
            'description': 'Adjust your thermostat by 2°C to reduce energy consumption by 15%',
            'impact': 'Medium Impact',
            'difficulty': 'Easy'
        },
        {
            'icon': '🛒',
            'title': 'Sustainable Shopping',
            'description': 'Choose local brands to reduce packaging waste by 40%',
            'impact': 'Medium Impact',
            'difficulty': 'Medium'
        },
        {
            'icon': '🥗',
            'title': 'Plant-Based Meals',
            'description': 'Try 3 plant-based meals this week to save 8.7 kg CO₂',
            'impact': 'High Impact',
            'difficulty': 'Medium'
        }
    ]
    
    for insight in insights:
        with st.container():
            col1, col2, col3, col4 = st.columns([1, 6, 2, 2])
            
            with col1:
                st.markdown(f"<h1 style='text-align: center;'>{insight['icon']}</h1>", unsafe_allow_html=True)
            
            with col2:
                st.write(f"**{insight['title']}**")
                st.write(insight['description'])
            
            with col3:
                color = '#4CAF50' if insight['impact'] == 'High Impact' else '#FF9800'
                st.markdown(f"<span style='color: {color}; font-weight: bold;'>{insight['impact']}</span>", unsafe_allow_html=True)
            
            with col4:
                if st.button("Take Action", key=insight['title']):
                    st.success(f"Great! You've committed to: {insight['title']}")
            
            st.write("---")
    
    # Real-time nudges
    st.subheader("⚡ Real-Time Nudges")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("🚗 **Driving Alert**: Heavy traffic detected on your usual route. Taking public transport could save 45 minutes and 3.2 kg CO₂.")
        
    with col2:
        st.warning("🛒 **Shopping Nudge**: You're near EcoMart, which has 30% lower carbon footprint than regular stores. Perfect time for groceries!")

def create_gamification():
    """Create gamification and challenges page"""
    st.header("🎮 Challenges & Achievements")
    
    # Current challenges
    st.subheader("🏆 Active Challenges")
    
    challenges = [
        {
            'title': '🌱 Green Week Challenge',
            'description': 'Reduce your weekly carbon footprint by 20%',
            'progress': 67,
            'reward': '50 EcoPoints + Tree Badge',
            'days_left': 3
        },
        {
            'title': '🚲 Bike to Work Week',
            'description': 'Use sustainable transport for 5 days',
            'progress': 40,
            'reward': '100 EcoPoints + Cyclist Badge',
            'days_left': 5
        },
        {
            'title': '🥬 Plant-Based Pioneer',
            'description': 'Try 10 plant-based meals this month',
            'progress': 80,
            'reward': '75 EcoPoints + Vegan Badge',
            'days_left': 12
        }
    ]
    
    for challenge in challenges:
        with st.container():
            st.markdown(f"""
            <div class="challenge-card">
                <h3>{challenge['title']}</h3>
                <p>{challenge['description']}</p>
                <p><strong>Reward:</strong> {challenge['reward']}</p>
                <p><strong>Days left:</strong> {challenge['days_left']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.progress(challenge['progress'] / 100)
            st.write(f"Progress: {challenge['progress']}%")
            st.write("---")
    
    # Leaderboard
    st.subheader("🏅 Community Leaderboard")
    
    leaderboard_data = pd.DataFrame({
        'Rank': range(1, 11),
        'User': ['EcoWarrior123', 'GreenGuru', 'You', 'ClimateChamp', 'EarthLover', 
                'SustainableSam', 'CarbonCrusher', 'NatureNinja', 'GreenThumb', 'EcoExplorer'],
        'EcoPoints': [2847, 2634, 2156, 2089, 1967, 1834, 1723, 1656, 1589, 1445],
        'CO₂ Saved (kg)': [847, 789, 645, 623, 589, 534, 489, 456, 434, 398]
    })
    
    # Highlight user row
    def highlight_user(row):
        return ['background-color: #90EE90' if row.name == 2 else '' for _ in row]
    
    st.dataframe(leaderboard_data.style.apply(highlight_user, axis=1), use_container_width=True)
    
    # Achievements
    st.subheader("🏆 Your Achievements")
    
    col1, col2, col3, col4 = st.columns(4)
    
    achievements = [
        {'badge': '🌱', 'title': 'Eco Starter', 'description': 'Completed first green action'},
        {'badge': '🚲', 'title': 'Bike Enthusiast', 'description': 'Biked 100km this month'},
        {'badge': '💡', 'title': 'Energy Saver', 'description': 'Reduced energy by 25%'},
        {'badge': '🌟', 'title': 'Carbon Neutral', 'description': 'Net-zero carbon week'}
    ]
    
    for i, achievement in enumerate(achievements):
        with [col1, col2, col3, col4][i]:
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; border: 2px solid #4CAF50; border-radius: 10px; margin: 0.5rem;">
                <h1>{achievement['badge']}</h1>
                <h4>{achievement['title']}</h4>
                <p>{achievement['description']}</p>
            </div>
            """, unsafe_allow_html=True)

def create_community():
    """Create community features page"""
    st.header("👥 Community & Social Impact")
    
    # Community stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Active Users", "47,832", "↗️ +12%")
    
    with col2:
        st.metric("Total CO₂ Saved", "2.4M kg", "↗️ +8%")
    
    with col3:
        st.metric("Trees Planted", "15,647", "↗️ +15%")
    
    # Global impact map
    st.subheader("🌍 Global Impact Map")
    
    # Create sample map data
    map_data = pd.DataFrame({
        'lat': [40.7128, 51.5074, 35.6762, -33.8688, 19.4326],
        'lon': [-74.0060, -0.1278, 139.6503, 151.2093, -99.1332],
        'city': ['New York', 'London', 'Tokyo', 'Sydney', 'Mexico City'],
        'co2_saved': [15670, 12340, 18950, 8760, 6540]
    })
    
    # Create folium map
    m = folium.Map(location=[20, 0], zoom_start=2)
    
    for idx, row in map_data.iterrows():
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=row['co2_saved']/1000,
            popup=f"{row['city']}: {row['co2_saved']} kg CO₂ saved",
            color='green',
            fill=True,
            fillColor='lightgreen'
        ).add_to(m)
    
    st_folium(m, width=700, height=400)
    
    # Community challenges
    st.subheader("🤝 Community Challenges")
    
    community_challenges = [
        {
            'title': '🌍 Global Climate Week',
            'participants': 12847,
            'goal': 'Reduce global emissions by 50,000 kg CO₂',
            'progress': 73,
            'days_left': 4
        },
        {
            'title': '🚌 Public Transport Month',
            'participants': 8934,
            'goal': 'Complete 100,000 sustainable trips',
            'progress': 56,
            'days_left': 18
        }
    ]
    
    for challenge in community_challenges:
        with st.container():
            st.write(f"**{challenge['title']}**")
            st.write(f"👥 {challenge['participants']} participants")
            st.write(f"🎯 Goal: {challenge['goal']}")
            st.progress(challenge['progress'] / 100)
            st.write(f"Progress: {challenge['progress']}% | {challenge['days_left']} days left")
            
            if st.button(f"Join Challenge", key=challenge['title']):
                st.success(f"You've joined: {challenge['title']}!")
            
            st.write("---")

def create_chat_interface():
    """Create a chat interface for ClimateCoach Chatbot"""
    st.header("💬 ClimateCoach Chatbot")
    st.write("Ask me anything about reducing your carbon footprint! I'm here to help with personalized advice.")
    
    # Initialize session state for chat history
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
        # Add a welcome message
        st.session_state['chat_history'].append((
            "", 
            "Hello! I'm ClimateCoach, your AI assistant for reducing carbon footprint. How can I help you today?"
        ))
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for user_msg, bot_msg in st.session_state['chat_history']:
            if user_msg:  # Don't show empty user messages (like welcome message)
                st.markdown(f"**👤 You:** {user_msg}")
            st.markdown(f"**🤖 ClimateCoach:** {bot_msg}")
            st.markdown("---")
    
    # Chat input
    user_input = st.text_input(
        "Your message:", 
        key="chat_input",
        placeholder="Ask about transportation, energy, food choices, or any climate topic..."
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        send_button = st.button("💬 Send")
    
    if send_button and user_input:
        # Create a simple chatbot response (fallback when OpenAI is not available)
        try:
            # Try to use ChatbotService if available
            if os.getenv('OPENAI_API_KEY'):
                chatbot_service = ChatbotService(openai_api_key=os.getenv('OPENAI_API_KEY'))
                response = chatbot_service.generate_response(user_input)
            else:
                response = get_fallback_response(user_input)
        except:
            response = get_fallback_response(user_input)
        
        # Add to chat history
        st.session_state['chat_history'].append((user_input, response))
        
        # Clear input and rerun to show new message
        st.rerun()
    
    # Quick action buttons
    st.subheader("⚡ Quick Questions")
    col1, col2, col3 = st.columns(3)
    
    quick_questions = [
        "How can I reduce transport emissions?",
        "What are the best energy-saving tips?",
        "How do I eat more sustainably?"
    ]
    
    for i, question in enumerate(quick_questions):
        with [col1, col2, col3][i]:
            if st.button(question, key=f"quick_{i}"):
                response = get_fallback_response(question)
                st.session_state['chat_history'].append((question, response))
                st.rerun()

def get_fallback_response(user_input: str) -> str:
    """Generate fallback responses when OpenAI is not available"""
    user_input_lower = user_input.lower()
    
    if any(word in user_input_lower for word in ['transport', 'car', 'drive', 'commute', 'travel']):
        return (
            "🚌 Great question about transportation! Here are some effective ways to reduce transport emissions:\n\n"
            "1. **Use public transport** - Can reduce your emissions by up to 60%\n"
            "2. **Walk or cycle** for short trips - Zero emissions and great exercise!\n"
            "3. **Carpool or ride-share** - Split the emissions with others\n"
            "4. **Work from home** when possible - Eliminates commute emissions\n"
            "5. **Choose efficient vehicles** - Electric or hybrid cars for necessary trips\n\n"
            "Would you like specific advice for your commute?"
        )
    
    elif any(word in user_input_lower for word in ['energy', 'electricity', 'heating', 'cooling']):
        return (
            "💡 Energy efficiency is a great place to start! Here are my top recommendations:\n\n"
            "1. **Smart thermostat** - Can save 10-15% on heating/cooling\n"
            "2. **LED bulbs** - Use 75% less energy than incandescent\n"
            "3. **Unplug devices** - Phantom loads can account for 10% of energy use\n"
            "4. **Insulation** - Keep your home comfortable with less energy\n"
            "5. **Energy-efficient appliances** - Look for Energy Star ratings\n\n"
            "These changes can significantly reduce your carbon footprint and save money!"
        )
    
    elif any(word in user_input_lower for word in ['food', 'eat', 'diet', 'meal', 'plant']):
        return (
            "🌱 Food choices have a huge impact on climate! Here's how to eat more sustainably:\n\n"
            "1. **Eat more plants** - Plant-based meals have 10x lower emissions\n"
            "2. **Buy local produce** - Reduces transportation emissions\n"
            "3. **Reduce food waste** - Plan meals and use leftovers creatively\n"
            "4. **Choose seasonal foods** - They're fresher and more efficient to grow\n"
            "5. **Less meat, especially beef** - Beef has the highest carbon footprint\n\n"
            "Even small changes like 'Meatless Monday' can make a difference!"
        )
    
    elif any(word in user_input_lower for word in ['shopping', 'buy', 'purchase', 'clothes']):
        return (
            "🛒 Sustainable shopping is key to reducing your footprint! Try these tips:\n\n"
            "1. **Buy less, choose quality** - Durable items last longer\n"
            "2. **Shop second-hand** - Reduces demand for new production\n"
            "3. **Local and ethical brands** - Support sustainable businesses\n"
            "4. **Repair instead of replace** - Extend the life of your items\n"
            "5. **Consider the packaging** - Choose minimal, recyclable packaging\n\n"
            "Remember: the most sustainable purchase is often the one you don't make!"
        )
    
    else:
        return (
            "🌍 I'm here to help you reduce your carbon footprint! I can provide advice on:\n\n"
            "• **Transportation** - Public transit, cycling, efficient vehicles\n"
            "• **Energy use** - Home efficiency, renewable energy\n"
            "• **Food choices** - Plant-based eating, local produce\n"
            "• **Shopping habits** - Sustainable consumption, waste reduction\n"
            "• **Daily habits** - Small changes with big impact\n\n"
            "What specific area would you like to focus on?"
        )

def create_settings():
    """Create settings and profile page"""
    st.header("⚙️ Settings & Profile")
    
    # User profile
    st.subheader("👤 Profile Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("Name", value="Alex Green")
        st.text_input("Email", value="alex.green@email.com")
        st.selectbox("Location", ["New York, USA", "London, UK", "Tokyo, Japan", "Sydney, Australia"])
    
    with col2:
        st.selectbox("Preferred Transport", ["Public Transport", "Bicycle", "Walking", "Car", "Mixed"])
        st.selectbox("Diet Preference", ["Omnivore", "Vegetarian", "Vegan", "Flexitarian"])
        st.slider("Household Size", 1, 10, 2)
    
    # Notification preferences
    st.subheader("🔔 Notification Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.checkbox("Daily carbon footprint summary", value=True)
        st.checkbox("Real-time behavioral nudges", value=True)
        st.checkbox("Weekly challenge updates", value=True)
    
    with col2:
        st.checkbox("Community achievements", value=True)
        st.checkbox("Goal reminders", value=False)
        st.checkbox("Monthly impact reports", value=True)
    
    # Privacy settings
    st.subheader("🔒 Privacy & Data Control")
    
    st.checkbox("Share data with research institutions (anonymized)", value=False)
    st.checkbox("Allow location-based recommendations", value=True)
    st.checkbox("Participate in community leaderboards", value=True)
    
    # Data export
    if st.button("Export My Data"):
        st.info("Your data export will be ready in 24 hours. You'll receive an email with the download link.")
    
    # Account actions
    st.subheader("🔧 Account Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Reset Progress"):
            st.warning("Are you sure? This action cannot be undone.")
    
    with col2:
        if st.button("Sync Data"):
            st.success("Data synchronized successfully!")
    
    with col3:
        if st.button("Delete Account"):
            st.error("Account deletion requested. Contact support for assistance.")


def main():
    """Main application"""
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🌍 ClimateCoach")
        st.markdown("*Your AI Climate Companion*")
        
        selected = option_menu(
            menu_title=None,
            options=["Dashboard", "AI Recommendations", "Challenges", "Community", "Chat", "Settings"],
            icons=["speedometer2", "robot", "trophy", "people", "chat", "gear"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#f0f2f6"},
                "icon": {"color": "#2E8B57", "font-size": "18px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#eee",
                },
                "nav-link-selected": {"background-color": "#2E8B57"},
            },
        )
        
        # Quick stats in sidebar
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        st.metric("Today's CO₂", "12.3 kg", "↘️ -2.1 kg")
        st.metric("This Week", "89.7 kg", "↘️ -15%")
        st.metric("EcoPoints", "2,156", "↗️ +45")
    
    # Main content based on selection
    if selected == "Dashboard":
        create_dashboard()
    elif selected == "AI Recommendations":
        create_ai_recommendations()
    elif selected == "Challenges":
        create_gamification()
    elif selected == "Community":
        create_community()
    elif selected == "Chat":
        create_chat_interface()
    elif selected == "Settings":
        create_settings()

if __name__ == "__main__":
    main()
