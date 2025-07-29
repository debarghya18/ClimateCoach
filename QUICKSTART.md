# 🚀 ClimateCoach Quick Start Guide

Get ClimateCoach running in under 5 minutes!

## Prerequisites

- Python 3.8 or higher
- Internet connection (for initial setup)

## Option 1: Automatic Setup (Recommended)

1. **Run the setup script:**
   ```bash
   python setup.py
   ```

2. **Start the application:**
   ```bash
   streamlit run app.py
   ```

3. **Open your browser:**
   Go to http://localhost:8501

4. **Login with demo account:**
   - Username: `demo_user`
   - Password: `demo123`

## Option 2: Manual Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize database:**
   ```bash
   python -c "from src.core.auth import UserAuth; UserAuth()"
   ```

3. **Start the application:**
   ```bash
   streamlit run app.py
   ```

## 🎯 What You Can Do

### 1. User Registration & Login
- Create your account with preferences
- Login with secure authentication
- Update your profile and preferences

### 2. Carbon Footprint Tracking
- Log daily activities (transport, energy, food, shopping)
- View real-time carbon calculations
- Track your progress over time

### 3. AI-Powered Recommendations
- Get personalized suggestions to reduce your footprint
- See potential CO2 savings for each recommendation
- Filter by difficulty and impact level

### 4. Community Features
- Join discussions about sustainability
- Share tips and experiences
- Like and comment on posts
- View trending topics

### 5. Challenges & Gamification
- Join community challenges
- Earn badges and achievements
- Compete on leaderboards
- Track your progress

## 📊 Sample Activities to Try

### Transportation
- Log a 10km car trip → See CO2 impact
- Switch to bus for the same trip → Compare savings
- Try cycling → Zero emissions!

### Energy
- Log 15 kWh daily energy usage
- Try reducing to 10 kWh → See recommendations
- Install LED bulbs → Track savings

### Food
- Log 2 meat meals per day
- Try vegetarian alternatives
- Buy local produce

### Shopping
- Log 5 items purchased
- Try buying second-hand
- Reduce online shopping

## 🔧 Configuration Options

### Environment Variables (.env file)
```bash
# Optional: OpenAI API for enhanced AI features
OPENAI_API_KEY=your_api_key_here

# Optional: Weather data
METEOSTAT_API_KEY=your_api_key_here

# Optional: AWS S3 for file storage
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_S3_BUCKET=your_bucket
```

### Docker Deployment
```bash
# Full production setup with PostgreSQL, Redis, monitoring
docker-compose up --build
```

## 🐛 Troubleshooting

### Common Issues

1. **Import errors:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Database errors:**
   ```bash
   rm climatecoach.db  # Delete and recreate
   python setup.py
   ```

3. **Port already in use:**
   ```bash
   streamlit run app.py --server.port 8502
   ```

4. **Permission errors:**
   ```bash
   python -m pip install --user -r requirements.txt
   ```

### Getting Help

- Check the README.md for detailed documentation
- Review the console output for error messages
- Ensure all dependencies are installed correctly

## 🎉 Next Steps

1. **Explore the dashboard** - View your carbon footprint trends
2. **Log your first activity** - Start tracking your daily impact
3. **Join the community** - Connect with other eco-conscious users
4. **Try challenges** - Participate in sustainability challenges
5. **Get recommendations** - See AI-powered suggestions for improvement

## 🌟 Pro Tips

- **Be consistent** - Log activities daily for best results
- **Set goals** - Use the platform to track progress toward sustainability goals
- **Engage with community** - Share your journey and learn from others
- **Try new things** - Experiment with different sustainable practices
- **Stay motivated** - Use achievements and challenges to stay engaged

---

**Ready to start your sustainability journey? Let's reduce your carbon footprint together! 🌱** 