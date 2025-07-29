"""
Carbon Estimation Engine for ClimateCoach
Uses ML models trained on lifecycle data to estimate carbon footprint
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import joblib
import os
from typing import Dict, List, Tuple, Optional
import logging

# Import weather and satellite services
from ..services.weather_service import WeatherService
from ..services.satellite_service import SatelliteService
from ..services.aws_s3_service import S3Service

logger = logging.getLogger(__name__)

class CarbonEstimator:
    """
    Advanced carbon footprint estimation engine using machine learning
    """
    
    def __init__(self, weather_api_key: Optional[str] = None, nasa_api_key: Optional[str] = None):
        self.models = {}
        self.scalers = {}
        self.categories = ['transport', 'energy', 'shopping', 'food']
        
        # Initialize external data services
        self.weather_service = WeatherService(weather_api_key) if weather_api_key else None
        self.satellite_service = SatelliteService(nasa_api_key) if nasa_api_key else None
        self.s3_service = S3Service() if os.getenv('S3_STORAGE_ENABLED', 'false').lower() == 'true' else None
        self.base_emissions = {
            'transport': {
                'car_km': 0.21,  # kg CO2 per km
                'bus_km': 0.08,
                'train_km': 0.04,
                'flight_km': 0.25,
                'bike_km': 0.0,
                'walk_km': 0.0
            },
            'energy': {
                'electricity_kwh': 0.45,  # kg CO2 per kWh
                'gas_kwh': 0.18,
                'heating_kwh': 0.23
            },
            'shopping': {
                'clothing_item': 15.2,  # kg CO2 per item
                'electronics_item': 85.4,
                'books_item': 1.2,
                'furniture_item': 45.6
            },
            'food': {
                'beef_kg': 27.0,  # kg CO2 per kg
                'pork_kg': 12.1,
                'chicken_kg': 6.9,
                'fish_kg': 5.4,
                'vegetables_kg': 0.4,
                'dairy_kg': 3.2
            }
        }
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize ML models for each category"""
        for category in self.categories:
            # Random Forest for complex patterns
            self.models[f'{category}_rf'] = RandomForestRegressor(
                n_estimators=100,
                random_state=42,
                max_depth=10
            )
            
            # Linear regression for baseline
            self.models[f'{category}_lr'] = LinearRegression()
            
            # Scaler for feature normalization
            self.scalers[category] = StandardScaler()
        
        # Train models with synthetic data
        self._train_initial_models()
    
    def _train_initial_models(self):
        """Train models with synthetic baseline data"""
        # Generate synthetic training data
        n_samples = 1000
        
        for category in self.categories:
            # Create synthetic features and targets
            X_train, y_train = self._generate_synthetic_data(category, n_samples)
            
            # Scale features
            X_scaled = self.scalers[category].fit_transform(X_train)
            
            # Train models
            self.models[f'{category}_rf'].fit(X_scaled, y_train)
            self.models[f'{category}_lr'].fit(X_scaled, y_train)
    
    def _generate_synthetic_data(self, category: str, n_samples: int) -> Tuple[np.ndarray, np.ndarray]:
        """Generate synthetic training data for initial model training"""
        np.random.seed(42)
        
        if category == 'transport':
            # Features: distance, mode, time_of_day, weather
            X = np.random.rand(n_samples, 4)
            X[:, 0] *= 100  # distance (0-100 km)
            X[:, 1] *= 5    # mode (0-5: walk, bike, bus, train, car, plane)
            X[:, 2] *= 24   # time_of_day (0-24)
            X[:, 3] *= 1    # weather factor (0-1)
            
            # Calculate target based on realistic emissions
            y = np.zeros(n_samples)
            for i in range(n_samples):
                distance = X[i, 0]
                mode = int(X[i, 1])
                mode_emissions = [0, 0, 0.08, 0.04, 0.21, 0.25][mode]
                y[i] = distance * mode_emissions * (1 + 0.1 * np.random.randn())
        
        elif category == 'energy':
            # Features: temperature, house_size, occupants, appliances
            X = np.random.rand(n_samples, 4)
            X[:, 0] = X[:, 0] * 40 - 10  # temperature (-10 to 30°C)
            X[:, 1] *= 300   # house_size (0-300 m²)
            X[:, 2] *= 6     # occupants (0-6)
            X[:, 3] *= 20    # appliances (0-20)
            
            y = np.zeros(n_samples)
            for i in range(n_samples):
                temp = X[i, 0]
                size = X[i, 1]
                occupants = X[i, 2]
                appliances = X[i, 3]
                
                base_consumption = size * 0.1 + occupants * 2 + appliances * 0.5
                temp_factor = 1 + abs(temp - 20) * 0.02  # More energy for extreme temps
                daily_kwh = base_consumption * temp_factor
                y[i] = daily_kwh * 0.45  # Convert to CO2
        
        elif category == 'shopping':
            # Features: income, age, season, online_vs_offline
            X = np.random.rand(n_samples, 4)
            X[:, 0] *= 100000  # income (0-100k)
            X[:, 1] *= 80      # age (0-80)
            X[:, 2] *= 4       # season (0-4)
            X[:, 3] *= 1       # online_vs_offline (0-1)
            
            y = np.zeros(n_samples)
            for i in range(n_samples):
                income = X[i, 0]
                age = X[i, 1]
                season = X[i, 2]
                online = X[i, 3]
                
                base_shopping = income * 0.0001 + age * 0.1
                seasonal_factor = 1.5 if season in [3, 4] else 1  # Higher in winter/holiday
                online_factor = 0.8 if online > 0.5 else 1  # Less packaging online
                
                y[i] = base_shopping * seasonal_factor * online_factor
        
        else:  # food
            # Features: diet_type, age, income, season
            X = np.random.rand(n_samples, 4)
            X[:, 0] *= 4     # diet_type (0=vegan, 1=vegetarian, 2=pescatarian, 3=omnivore)
            X[:, 1] *= 80    # age (0-80)
            X[:, 2] *= 100000  # income (0-100k)
            X[:, 3] *= 4     # season (0-4)
            
            y = np.zeros(n_samples)
            for i in range(n_samples):
                diet = X[i, 0]
                age = X[i, 1]
                income = X[i, 2]
                season = X[i, 3]
                
                # Base emissions by diet type
                diet_emissions = [2, 4, 6, 12][int(diet)]  # kg CO2 per day
                age_factor = 1 + (age - 40) * 0.005  # Peak consumption around 40
                income_factor = 1 + income * 0.000005
                
                y[i] = diet_emissions * age_factor * income_factor
        
        return X, y
    
    def estimate_transport_emissions(self, data: Dict) -> float:
        """Estimate transport-related carbon emissions"""
        try:
            # Extract features
            distance = data.get('distance_km', 0)
            mode = data.get('transport_mode', 'car')
            time_of_day = data.get('time_of_day', 12)
            weather_factor = data.get('weather_factor', 1.0)
            
            # Map transport mode to numeric
            mode_map = {'walk': 0, 'bike': 1, 'bus': 2, 'train': 3, 'car': 4, 'plane': 5}
            mode_numeric = mode_map.get(mode, 4)
            
            # Prepare features
            features = np.array([[distance, mode_numeric, time_of_day, weather_factor]])
            features_scaled = self.scalers['transport'].transform(features)
            
            # Get prediction from ensemble
            rf_pred = self.models['transport_rf'].predict(features_scaled)[0]
            lr_pred = self.models['transport_lr'].predict(features_scaled)[0]
            
            # Ensemble prediction (weighted average)
            prediction = 0.7 * rf_pred + 0.3 * lr_pred
            
            return max(0, prediction)  # Ensure non-negative
            
        except Exception as e:
            logger.error(f"Error estimating transport emissions: {e}")
            # Fallback to simple calculation
            distance = data.get('distance_km', 0)
            mode = data.get('transport_mode', 'car')
            return distance * self.base_emissions['transport'].get(f'{mode}_km', 0.21)
    
    def estimate_energy_emissions(self, data: Dict) -> float:
        """Estimate energy-related carbon emissions"""
        try:
            temperature = data.get('temperature', 20)
            house_size = data.get('house_size_m2', 100)
            occupants = data.get('occupants', 2)
            appliances = data.get('appliances_count', 10)
            
            features = np.array([[temperature, house_size, occupants, appliances]])
            features_scaled = self.scalers['energy'].transform(features)
            
            rf_pred = self.models['energy_rf'].predict(features_scaled)[0]
            lr_pred = self.models['energy_lr'].predict(features_scaled)[0]
            
            prediction = 0.7 * rf_pred + 0.3 * lr_pred
            return max(0, prediction)
            
        except Exception as e:
            logger.error(f"Error estimating energy emissions: {e}")
            # Fallback calculation
            kwh_usage = data.get('kwh_usage', 20)
            return kwh_usage * self.base_emissions['energy']['electricity_kwh']
    
    def estimate_shopping_emissions(self, data: Dict) -> float:
        """Estimate shopping-related carbon emissions"""
        try:
            income = data.get('income', 50000)
            age = data.get('age', 35)
            season = data.get('season', 1)  # 1-4
            online_ratio = data.get('online_ratio', 0.5)
            
            features = np.array([[income, age, season, online_ratio]])
            features_scaled = self.scalers['shopping'].transform(features)
            
            rf_pred = self.models['shopping_rf'].predict(features_scaled)[0]
            lr_pred = self.models['shopping_lr'].predict(features_scaled)[0]
            
            prediction = 0.7 * rf_pred + 0.3 * lr_pred
            return max(0, prediction)
            
        except Exception as e:
            logger.error(f"Error estimating shopping emissions: {e}")
            # Fallback calculation
            items_bought = data.get('items_bought', 1)
            return items_bought * 5  # Average 5 kg CO2 per item
    
    def estimate_food_emissions(self, data: Dict) -> float:
        """Estimate food-related carbon emissions"""
        try:
            diet_type = data.get('diet_type', 'omnivore')
            age = data.get('age', 35)
            income = data.get('income', 50000)
            season = data.get('season', 1)
            
            # Map diet type to numeric
            diet_map = {'vegan': 0, 'vegetarian': 1, 'pescatarian': 2, 'omnivore': 3}
            diet_numeric = diet_map.get(diet_type, 3)
            
            features = np.array([[diet_numeric, age, income, season]])
            features_scaled = self.scalers['food'].transform(features)
            
            rf_pred = self.models['food_rf'].predict(features_scaled)[0]
            lr_pred = self.models['food_lr'].predict(features_scaled)[0]
            
            prediction = 0.7 * rf_pred + 0.3 * lr_pred
            return max(0, prediction)
            
        except Exception as e:
            logger.error(f"Error estimating food emissions: {e}")
            # Fallback calculation based on diet
            diet_emissions = {'vegan': 2, 'vegetarian': 4, 'pescatarian': 6, 'omnivore': 12}
            return diet_emissions.get(data.get('diet_type', 'omnivore'), 12)
    
    def estimate_total_daily_emissions(self, user_data: Dict) -> Dict[str, float]:
        """Estimate total daily carbon emissions across all categories"""
        emissions = {
            'transport': self.estimate_transport_emissions(user_data.get('transport', {})),
            'energy': self.estimate_energy_emissions(user_data.get('energy', {})),
            'shopping': self.estimate_shopping_emissions(user_data.get('shopping', {})),
            'food': self.estimate_food_emissions(user_data.get('food', {}))
        }
        
        emissions['total'] = sum(emissions.values())
        return emissions
    
    def get_category_insights(self, emissions: Dict[str, float]) -> List[Dict]:
        """Generate insights based on emission categories"""
        insights = []
        
        # Transport insights
        if emissions['transport'] > 10:
            insights.append({
                'category': 'transport',
                'type': 'high_emission',
                'message': 'Your transport emissions are high. Consider public transport or cycling.',
                'potential_savings': emissions['transport'] * 0.6
            })
        
        # Energy insights
        if emissions['energy'] > 15:
            insights.append({
                'category': 'energy',
                'type': 'high_emission',
                'message': 'Energy consumption is above average. Consider smart thermostat and LED bulbs.',
                'potential_savings': emissions['energy'] * 0.3
            })
        
        # Shopping insights
        if emissions['shopping'] > 8:
            insights.append({
                'category': 'shopping',
                'type': 'high_emission',
                'message': 'Consider buying local and second-hand products to reduce shopping footprint.',
                'potential_savings': emissions['shopping'] * 0.4
            })
        
        # Food insights
        if emissions['food'] > 10:
            insights.append({
                'category': 'food',
                'type': 'high_emission',
                'message': 'Try incorporating more plant-based meals to reduce food emissions.',
                'potential_savings': emissions['food'] * 0.5
            })
        
        return insights
    
    def get_weather_enhanced_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get weather data to enhance carbon calculations"""
        if not self.weather_service:
            logger.warning("Weather service not initialized. Using default weather data.")
            return {'temperature': 20, 'humidity': 50, 'wind_speed': 10, 'condition': 'clear'}
        
        try:
            weather_data = self.weather_service.fetch_current_weather(lat, lon)
            return {
                'temperature': weather_data.get('temp', 20),
                'humidity': weather_data.get('rhum', 50),
                'wind_speed': weather_data.get('wspd', 10),
                'condition': weather_data.get('coco', 1)  # Weather condition code
            }
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return {'temperature': 20, 'humidity': 50, 'wind_speed': 10, 'condition': 'clear'}
    
    def get_environmental_context(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get environmental context from satellite data"""
        if not self.satellite_service:
            logger.warning("Satellite service not initialized. Using default environmental data.")
            return {
                'air_quality_index': 85,
                'vegetation_index': 0.75,
                'risk_level': 'Low',
                'recommendations': []
            }
        
        try:
            environmental_data = self.satellite_service.analyze_environmental_impact(lat, lon)
            return {
                'air_quality_index': environmental_data.get('data', {}).get('air_quality_index', 85),
                'vegetation_index': environmental_data.get('data', {}).get('vegetation_index', 0.75),
                'risk_level': environmental_data.get('risk_level', 'Low'),
                'recommendations': environmental_data.get('recommendations', [])
            }
        except Exception as e:
            logger.error(f"Error fetching environmental data: {e}")
            return {
                'air_quality_index': 85,
                'vegetation_index': 0.75,
                'risk_level': 'Low',
                'recommendations': []
            }
    
    def estimate_with_real_time_data(self, user_data: Dict, lat: float, lon: float) -> Dict[str, Any]:
        """Enhanced estimation using real-time weather and satellite data"""
        # Get real-time data
        weather_data = self.get_weather_enhanced_data(lat, lon)
        environmental_data = self.get_environmental_context(lat, lon)
        
        # Enhance user data with real-time information
        enhanced_data = user_data.copy()
        
        # Enhance transport data with weather
        if 'transport' in enhanced_data:
            enhanced_data['transport']['weather_factor'] = self._calculate_weather_factor(weather_data)
        
        # Enhance energy data with temperature
        if 'energy' in enhanced_data:
            enhanced_data['energy']['temperature'] = weather_data['temperature']
        
        # Calculate standard emissions
        emissions = self.estimate_total_daily_emissions(enhanced_data)
        
        # Apply environmental adjustments
        emissions = self._apply_environmental_adjustments(emissions, environmental_data)
        
        return {
            'emissions': emissions,
            'weather_data': weather_data,
            'environmental_data': environmental_data,
            'enhanced_insights': self._get_enhanced_insights(emissions, weather_data, environmental_data)
        }
    
    def _calculate_weather_factor(self, weather_data: Dict) -> float:
        """Calculate weather impact factor for transport"""
        base_factor = 1.0
        
        # Temperature impact
        temp = weather_data.get('temperature', 20)
        if temp < 0:  # Very cold - more energy needed
            base_factor += 0.2
        elif temp > 35:  # Very hot - more AC usage
            base_factor += 0.15
        
        # Weather condition impact
        condition = weather_data.get('condition', 'clear')
        if condition in ['rain', 'snow', 'storm']:  # Bad weather encourages car use
            base_factor += 0.3
        elif condition == 'clear':  # Good weather encourages walking/cycling
            base_factor -= 0.1
        
        return max(0.5, base_factor)  # Ensure factor doesn't go below 0.5
    
    def _apply_environmental_adjustments(self, emissions: Dict[str, float], 
                                       environmental_data: Dict) -> Dict[str, float]:
        """Apply environmental context adjustments to emissions"""
        adjusted_emissions = emissions.copy()
        
        # Air quality adjustment
        air_quality = environmental_data.get('air_quality_index', 85)
        if air_quality < 50:  # Poor air quality
            # Increase transport emissions impact (more concern about adding to pollution)
            adjusted_emissions['transport'] *= 1.2
        
        # Vegetation index adjustment
        vegetation = environmental_data.get('vegetation_index', 0.75)
        if vegetation < 0.5:  # Low vegetation
            # Increase overall impact awareness
            for category in ['transport', 'energy']:
                adjusted_emissions[category] *= 1.1
        
        # Recalculate total
        adjusted_emissions['total'] = sum(v for k, v in adjusted_emissions.items() if k != 'total')
        
        return adjusted_emissions
    
    def _get_enhanced_insights(self, emissions: Dict[str, float], 
                             weather_data: Dict, environmental_data: Dict) -> List[Dict]:
        """Generate enhanced insights using weather and environmental data"""
        insights = self.get_category_insights(emissions)
        
        # Add weather-specific insights
        temp = weather_data.get('temperature', 20)
        condition = weather_data.get('condition', 'clear')
        
        if temp < 5:
            insights.append({
                'category': 'weather',
                'type': 'cold_weather',
                'message': f'Cold weather ({temp}°C) increases energy usage. Consider extra insulation.',
                'potential_savings': 2.3
            })
        
        if condition in ['rain', 'snow']:
            insights.append({
                'category': 'weather',
                'type': 'bad_weather',
                'message': 'Bad weather conditions. Consider remote work to reduce transport emissions.',
                'potential_savings': 4.5
            })
        
        # Add environmental insights
        risk_level = environmental_data.get('risk_level', 'Low')
        if risk_level in ['High', 'Critical']:
            insights.append({
                'category': 'environment',
                'type': 'high_risk',
                'message': f'Your area has {risk_level} environmental risk. Extra care needed for emissions.',
                'potential_savings': 0,
                'recommendations': environmental_data.get('recommendations', [])
            })
        
        return insights
    
    def log_carbon_estimation(self, user_id: str, location: str, 
                            user_data: Dict, emissions: Dict[str, float],
                            insights: List[Dict]) -> bool:
        """Log carbon estimation data to S3"""
        if not self.s3_service:
            logger.info("S3 service not available. Skipping carbon data logging.")
            return False
        
        try:
            # Prepare comprehensive log data
            log_data = {
                'user_data': user_data,
                'emissions': emissions,
                'insights': insights,
                'location': location,
                'calculation_method': 'ml_ensemble',
                'models_used': ['random_forest', 'linear_regression']
            }
            
            # Upload to S3
            success = self.s3_service.upload_climate_data(
                climate_data=log_data,
                location=location,
                data_type='carbon_estimation'
            )
            
            if success:
                logger.info(f"Successfully logged carbon estimation for user {user_id[:8]}...")
            
            return success
            
        except Exception as e:
            logger.error(f"Error logging carbon estimation: {e}")
            return False
    
    def log_user_carbon_history(self, user_id: str, emissions_history: List[Dict]) -> bool:
        """Log user's carbon history to S3"""
        if not self.s3_service:
            logger.info("S3 service not available. Skipping carbon history logging.")
            return False
        
        try:
            # Prepare user history data
            history_data = {
                'emissions_history': emissions_history,
                'analysis_period': f'{len(emissions_history)} days',
                'trends': self._analyze_carbon_trends(emissions_history)
            }
            
            # Upload to S3
            success = self.s3_service.upload_user_data(
                user_id=user_id,
                data=history_data,
                data_category='carbon_history'
            )
            
            if success:
                logger.info(f"Successfully logged carbon history for user {user_id[:8]}...")
            
            return success
            
        except Exception as e:
            logger.error(f"Error logging carbon history: {e}")
            return False
    
    def _analyze_carbon_trends(self, emissions_history: List[Dict]) -> Dict[str, Any]:
        """Analyze trends in carbon emissions history"""
        if not emissions_history:
            return {'trend': 'no_data', 'change_rate': 0}
        
        try:
            # Extract total emissions over time
            totals = [day.get('total', 0) for day in emissions_history]
            
            if len(totals) < 2:
                return {'trend': 'insufficient_data', 'change_rate': 0}
            
            # Calculate trend
            recent_avg = np.mean(totals[-7:]) if len(totals) >= 7 else np.mean(totals)
            overall_avg = np.mean(totals)
            
            change_rate = (recent_avg - overall_avg) / overall_avg * 100 if overall_avg > 0 else 0
            
            if change_rate > 5:
                trend = 'increasing'
            elif change_rate < -5:
                trend = 'decreasing'
            else:
                trend = 'stable'
            
            return {
                'trend': trend,
                'change_rate': round(change_rate, 2),
                'recent_average': round(recent_avg, 2),
                'overall_average': round(overall_avg, 2),
                'best_day': min(totals),
                'worst_day': max(totals)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing carbon trends: {e}")
            return {'trend': 'analysis_error', 'change_rate': 0}
    
    def backup_models_to_s3(self) -> bool:
        """Backup trained models to S3"""
        if not self.s3_service:
            logger.info("S3 service not available. Skipping model backup.")
            return False
        
        try:
            # Prepare model data for backup
            model_data = {
                'models_info': {
                    'categories': self.categories,
                    'model_types': ['random_forest', 'linear_regression'],
                    'training_samples': 1000,
                    'features': {
                        'transport': ['distance', 'mode', 'time_of_day', 'weather_factor'],
                        'energy': ['temperature', 'house_size', 'occupants', 'appliances'],
                        'shopping': ['income', 'age', 'season', 'online_ratio'],
                        'food': ['diet_type', 'age', 'income', 'season']
                    }
                },
                'base_emissions': self.base_emissions,
                'version': '1.0',
                'trained_at': datetime.now().isoformat()
            }
            
            # Create backup
            success = self.s3_service.create_backup(
                data=model_data,
                backup_type='carbon_models'
            )
            
            if success:
                logger.info("Successfully backed up carbon estimation models to S3")
            
            return success
            
        except Exception as e:
            logger.error(f"Error backing up models to S3: {e}")
            return False
    
    def save_models(self, directory: str):
        """Save trained models to disk"""
        os.makedirs(directory, exist_ok=True)
        
        for name, model in self.models.items():
            joblib.dump(model, os.path.join(directory, f'{name}.pkl'))
        
        for name, scaler in self.scalers.items():
            joblib.dump(scaler, os.path.join(directory, f'{name}_scaler.pkl'))
    
    def load_models(self, directory: str):
        """Load trained models from disk"""
        try:
            for category in self.categories:
                # Load models
                rf_path = os.path.join(directory, f'{category}_rf.pkl')
                lr_path = os.path.join(directory, f'{category}_lr.pkl')
                scaler_path = os.path.join(directory, f'{category}_scaler.pkl')
                
                if os.path.exists(rf_path):
                    self.models[f'{category}_rf'] = joblib.load(rf_path)
                if os.path.exists(lr_path):
                    self.models[f'{category}_lr'] = joblib.load(lr_path)
                if os.path.exists(scaler_path):
                    self.scalers[category] = joblib.load(scaler_path)
                    
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            self._initialize_models()  # Fallback to fresh models

# Example usage
if __name__ == "__main__":
    estimator = CarbonEstimator()
    
    # Sample user data
    sample_data = {
        'transport': {
            'distance_km': 25,
            'transport_mode': 'car',
            'time_of_day': 8,
            'weather_factor': 1.0
        },
        'energy': {
            'temperature': 15,
            'house_size_m2': 120,
            'occupants': 3,
            'appliances_count': 12
        },
        'shopping': {
            'income': 65000,
            'age': 32,
            'season': 2,
            'online_ratio': 0.7
        },
        'food': {
            'diet_type': 'omnivore',
            'age': 32,
            'income': 65000,
            'season': 2
        }
    }
    
    # Get emissions estimate
    emissions = estimator.estimate_total_daily_emissions(sample_data)
    print("Daily Emissions Estimate:", emissions)
    
    # Get insights
    insights = estimator.get_category_insights(emissions)
    print("Insights:", insights)
