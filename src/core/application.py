"""
Main Application Service for ClimateCoach
Integrates all components into a cohesive platform
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio

# Import all services
from ..services.secure_computation_service import SecureComputationService
from ..services.offline_gpt_service import OfflineGPTService
from ..services.habit_detection_service import HabitDetectionService
from ..services.sentiment_motivation_service import SentimentMotivationService
from ..services.monitoring_service import get_monitoring_service
from ..services.global_climate_service import GlobalClimateService
from ..services.aws_s3_service import S3Service
from ..services.weather_service import WeatherService
from ..services.satellite_service import SatelliteService
from ..services.chatbot_service import ChatbotService
from ..agents.carbon_estimator import CarbonEstimator
from ..agents.recommendation_engine import RecommendationEngine

logger = logging.getLogger(__name__)

class ClimateCoachApplication:
    """
    Main application class that orchestrates all ClimateCoach services
    """
    
    def __init__(self):
        """Initialize the ClimateCoach application with all services"""
        self.config = self._load_configuration()
        
        # Initialize monitoring first
        self.monitoring_service = get_monitoring_service()
        logger.info("Monitoring service initialized")
        
        # Initialize core services
        self._initialize_core_services()
        
        # Initialize AI/ML services
        self._initialize_ai_services()
        
        # Initialize data services
        self._initialize_data_services()
        
        # Initialize global services
        self._initialize_global_services()
        
        # Application state
        self.is_running = False
        self.startup_time = datetime.utcnow()
        
        logger.info("ClimateCoach Application initialized successfully")
    
    def _load_configuration(self) -> Dict[str, Any]:
        """Load application configuration from environment variables"""
        return {
            # Core settings
            'app_name': os.getenv('APP_NAME', 'ClimateCoach'),
            'app_version': os.getenv('APP_VERSION', '1.0.0'),
            'debug': os.getenv('DEBUG', 'false').lower() == 'true',
            'environment': os.getenv('ENVIRONMENT', 'development'),
            
            # Service enablement flags
            'offline_gpt_enabled': os.getenv('OFFLINE_GPT_ENABLED', 'true').lower() == 'true',
            'sentiment_analysis_enabled': os.getenv('SENTIMENT_ANALYSIS_ENABLED', 'true').lower() == 'true',
            'habit_detection_enabled': os.getenv('HABIT_DETECTION_ENABLED', 'true').lower() == 'true',
            'secure_computation_enabled': os.getenv('SECURE_COMPUTATION_ENABLED', 'false').lower() == 'true',
            'global_climate_enabled': os.getenv('GLOBAL_CLIMATE_ENABLED', 'true').lower() == 'true',
            's3_storage_enabled': os.getenv('S3_STORAGE_ENABLED', 'false').lower() == 'true',
            'prometheus_enabled': os.getenv('PROMETHEUS_ENABLED', 'false').lower() == 'true',
            
            # API keys
            'openai_api_key': os.getenv('OPENAI_API_KEY'),
            'nasa_api_key': os.getenv('NASA_API_KEY'),
            'weather_api_key': os.getenv('WEATHER_API_KEY'),
            'meteostat_api_key': os.getenv('METEOSTAT_API_KEY'),
            'openweather_api_key': os.getenv('OPENWEATHER_API_KEY'),
        }
    
    def _initialize_core_services(self):
        """Initialize core application services"""
        try:
            # Carbon estimation engine
            self.carbon_estimator = CarbonEstimator(
                weather_api_key=self.config['weather_api_key'],
                nasa_api_key=self.config['nasa_api_key']
            )
            
            # AI recommendation engine
            if self.config['openai_api_key']:
                self.recommendation_engine = RecommendationEngine(
                    openai_api_key=self.config['openai_api_key']
                )
            else:
                self.recommendation_engine = None
                logger.warning("OpenAI API key not provided, recommendation engine disabled")
            
            # Chatbot service
            if self.config['openai_api_key']:
                self.chatbot_service = ChatbotService(
                    openai_api_key=self.config['openai_api_key']
                )
            else:
                self.chatbot_service = None
                logger.warning("OpenAI API key not provided, chatbot service disabled")
            
            logger.info("Core services initialized")
            
        except Exception as e:
            logger.error(f"Error initializing core services: {e}")
            raise
    
    def _initialize_ai_services(self):
        """Initialize AI/ML services"""
        try:
            # Offline GPT service
            if self.config['offline_gpt_enabled']:
                self.offline_gpt_service = OfflineGPTService()
            else:
                self.offline_gpt_service = None
            
            # Sentiment and motivation analysis
            if self.config['sentiment_analysis_enabled']:
                self.sentiment_service = SentimentMotivationService()
            else:
                self.sentiment_service = None
            
            # Habit detection
            if self.config['habit_detection_enabled']:
                self.habit_detection_service = HabitDetectionService()
            else:
                self.habit_detection_service = None
            
            # Secure computation (optional)
            if self.config['secure_computation_enabled']:
                try:
                    self.secure_computation_service = SecureComputationService()
                except Exception as e:
                    logger.warning(f"Secure computation service failed to initialize: {e}")
                    self.secure_computation_service = None
            else:
                self.secure_computation_service = None
            
            logger.info("AI services initialized")
            
        except Exception as e:
            logger.error(f"Error initializing AI services: {e}")
            # Don't raise - these are optional services
    
    def _initialize_data_services(self):
        """Initialize data storage and processing services"""
        try:
            # AWS S3 service
            if self.config['s3_storage_enabled']:
                self.s3_service = S3Service()
            else:
                self.s3_service = None
            
            # Weather service
            if self.config['weather_api_key']:
                self.weather_service = WeatherService(
                    api_key=self.config['weather_api_key']
                )
            else:
                self.weather_service = None
                logger.warning("Weather API key not provided")
            
            # Satellite service
            if self.config['nasa_api_key']:
                self.satellite_service = SatelliteService(
                    api_key=self.config['nasa_api_key']
                )
            else:
                self.satellite_service = None
                logger.warning("NASA API key not provided")
            
            logger.info("Data services initialized")
            
        except Exception as e:
            logger.error(f"Error initializing data services: {e}")
            # Don't raise - these are optional services
    
    def _initialize_global_services(self):
        """Initialize global climate services"""
        try:
            # Global climate service
            if self.config['global_climate_enabled']:
                self.global_climate_service = GlobalClimateService(
                    nasa_api_key=self.config['nasa_api_key'],
                    meteostat_api_key=self.config['meteostat_api_key']
                )
            else:
                self.global_climate_service = None
            
            logger.info("Global services initialized")
            
        except Exception as e:
            logger.error(f"Error initializing global services: {e}")
            # Don't raise - these are optional services
    
    async def startup(self):
        """Start the application and all services"""
        try:
            self.is_running = True
            self.startup_time = datetime.utcnow()
            
            # Record startup metrics
            self.monitoring_service.record_user_interaction('application_startup')
            
            # Initialize global climate data cache if enabled
            if self.global_climate_service:
                try:
                    await self._initialize_climate_cache()
                    logger.info("Global climate cache initialized")
                except Exception as e:
                    logger.warning(f"Failed to initialize climate cache: {e}")
            
            # Backup models to S3 if enabled
            if self.s3_service and self.carbon_estimator:
                try:
                    self.carbon_estimator.backup_models_to_s3()
                    logger.info("Models backed up to S3")
                except Exception as e:
                    logger.warning(f"Failed to backup models to S3: {e}")
            
            logger.info("ClimateCoach Application started successfully")
            
        except Exception as e:
            logger.error(f"Error starting application: {e}")
            self.is_running = False
            raise
    
    async def shutdown(self):
        """Shutdown the application gracefully"""
        try:
            self.is_running = False
            
            # Record shutdown metrics
            self.monitoring_service.record_user_interaction('application_shutdown')
            
            # Perform final data backup if S3 is enabled
            if self.s3_service:
                try:
                    # Create application state backup
                    app_state = {
                        'shutdown_time': datetime.utcnow().isoformat(),
                        'uptime_seconds': (datetime.utcnow() - self.startup_time).total_seconds(),
                        'final_metrics': self.monitoring_service.get_health_status()
                    }
                    self.s3_service.create_backup(app_state, 'application_state')
                    logger.info("Final backup created")
                except Exception as e:
                    logger.warning(f"Failed to create final backup: {e}")
            
            logger.info("ClimateCoach Application shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    async def _initialize_climate_cache(self):
        """Initialize global climate data cache"""
        if self.global_climate_service:
            # Fetch initial global climate data
            global_data = await self.global_climate_service.get_global_climate_overview()
            
            # Cache the data if S3 is available
            if self.s3_service and global_data:
                self.s3_service.upload_climate_data(
                    climate_data=global_data,
                    location='global',
                    data_type='overview_cache'
                )
    
    def get_carbon_estimation(self, user_data: Dict[str, Any], user_id: str = None, 
                            location: str = None) -> Dict[str, Any]:
        """
        Get comprehensive carbon estimation with all available enhancements
        
        Args:
            user_data: User's activity data
            user_id: User identifier (optional)
            location: User's location (optional)
            
        Returns:
            Comprehensive carbon estimation results
        """
        try:
            # Record the calculation
            self.monitoring_service.record_carbon_calculation(
                user_id or 'anonymous', 
                'comprehensive'
            )
            
            # Basic carbon estimation
            emissions = self.carbon_estimator.estimate_total_daily_emissions(user_data)
            insights = self.carbon_estimator.get_category_insights(emissions)
            
            result = {
                'emissions': emissions,
                'insights': insights,
                'timestamp': datetime.utcnow().isoformat(),
                'estimation_type': 'basic'
            }
            
            # Enhanced estimation with real-time data if location provided
            if location and (self.weather_service or self.satellite_service):
                try:
                    # Try to get coordinates
                    if self.global_climate_service:
                        coords = self.global_climate_service._geocode_location(location)
                        if coords:
                            enhanced_result = self.carbon_estimator.estimate_with_real_time_data(
                                user_data, coords['lat'], coords['lon']
                            )
                            result.update(enhanced_result)
                            result['estimation_type'] = 'enhanced'
                except Exception as e:
                    logger.warning(f"Failed to get enhanced estimation: {e}")
            
            # Add AI recommendations if available
            if self.recommendation_engine:
                try:
                    recommendations = self.recommendation_engine.generate_personalized_recommendations(
                        user_data, emissions
                    )
                    result['ai_recommendations'] = recommendations
                except Exception as e:
                    logger.warning(f"Failed to generate AI recommendations: {e}")
            
            # Log to S3 if enabled
            if self.s3_service and user_id and location:
                try:
                    self.carbon_estimator.log_carbon_estimation(
                        user_id, location, user_data, emissions, insights
                    )
                except Exception as e:
                    logger.warning(f"Failed to log to S3: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in carbon estimation: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def analyze_user_sentiment(self, user_messages: List[str]) -> Dict[str, Any]:
        """
        Analyze user sentiment and motivation
        
        Args:
            user_messages: List of user messages
            
        Returns:
            Sentiment and motivation analysis results
        """
        if not self.sentiment_service:
            return {'error': 'Sentiment analysis service not available'}
        
        try:
            self.monitoring_service.record_sentiment_analysis()
            
            # Analyze sentiment
            sentiment_results = self.sentiment_service.analyze_sentiment(user_messages)
            
            # Analyze engagement
            engagement_analysis = self.sentiment_service.analyze_climate_engagement(user_messages)
            
            # Generate personalized nudges
            nudges = self.sentiment_service.generate_personalized_nudges(engagement_analysis)
            
            return {
                'sentiment_results': sentiment_results,
                'engagement_analysis': engagement_analysis,
                'personalized_nudges': nudges,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return {'error': str(e)}
    
    def detect_user_habits(self, time_series_data) -> Dict[str, Any]:
        """
        Detect user habits from time-series data
        
        Args:
            time_series_data: Time series data for habit detection
            
        Returns:
            Habit detection results
        """
        if not self.habit_detection_service:
            return {'error': 'Habit detection service not available'}
        
        try:
            self.monitoring_service.record_habit_detection()
            
            # Detect habit patterns
            clustering_results = self.habit_detection_service.detect_habits(time_series_data)
            
            return {
                'habit_patterns': clustering_results,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in habit detection: {e}")
            return {'error': str(e)}
    
    async def get_global_climate_data(self) -> Dict[str, Any]:
        """
        Get global climate overview
        
        Returns:
            Global climate data and insights
        """
        if not self.global_climate_service:
            return {'error': 'Global climate service not available'}
        
        try:
            # Get global climate overview
            global_data = await self.global_climate_service.get_global_climate_overview()
            
            return global_data
            
        except Exception as e:
            logger.error(f"Error getting global climate data: {e}")
            return {'error': str(e)}
    
    def get_location_climate_summary(self, location: str) -> Dict[str, Any]:
        """
        Get climate summary for specific location
        
        Args:
            location: Location name
            
        Returns:
            Location-specific climate data
        """
        if not self.global_climate_service:
            return {'error': 'Global climate service not available'}
        
        try:
            return self.global_climate_service.get_location_climate_summary(location)
            
        except Exception as e:
            logger.error(f"Error getting location climate summary: {e}")
            return {'error': str(e)}
    
    def get_ai_chat_response(self, user_message: str, context: Dict = None) -> str:
        """
        Get AI chat response
        
        Args:
            user_message: User's message
            context: Optional context information
            
        Returns:
            AI response
        """
        try:
            # Try online chatbot first
            if self.chatbot_service:
                response = self.chatbot_service.generate_response(user_message, context)
                return response
            
            # Fallback to offline GPT
            elif self.offline_gpt_service:
                response = self.offline_gpt_service.generate_climate_advice(user_message)
                return response
            
            else:
                return "I'm sorry, the AI chat service is currently unavailable. Please try again later."
                
        except Exception as e:
            logger.error(f"Error in AI chat response: {e}")
            return "I encountered an error processing your message. Please try again."
    
    def get_application_status(self) -> Dict[str, Any]:
        """
        Get comprehensive application status
        
        Returns:
            Application status and health information
        """
        try:
            # Get monitoring metrics
            health_status = self.monitoring_service.get_health_status()
            
            # Service availability
            services_status = {
                'carbon_estimator': self.carbon_estimator is not None,
                'recommendation_engine': self.recommendation_engine is not None,
                'chatbot_service': self.chatbot_service is not None,
                'offline_gpt_service': self.offline_gpt_service is not None,
                'sentiment_service': self.sentiment_service is not None,
                'habit_detection_service': self.habit_detection_service is not None,
                'secure_computation_service': self.secure_computation_service is not None,
                'global_climate_service': self.global_climate_service is not None,
                's3_service': self.s3_service is not None,
                'weather_service': self.weather_service is not None,
                'satellite_service': self.satellite_service is not None
            }
            
            return {
                'application': {
                    'name': self.config['app_name'],
                    'version': self.config['app_version'],
                    'environment': self.config['environment'],
                    'is_running': self.is_running,
                    'startup_time': self.startup_time.isoformat(),
                    'uptime_seconds': (datetime.utcnow() - self.startup_time).total_seconds()
                },
                'services': services_status,
                'health': health_status,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting application status: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

# Global application instance
app_instance = None

def get_application() -> ClimateCoachApplication:
    """Get global application instance"""
    global app_instance
    if app_instance is None:
        app_instance = ClimateCoachApplication()
    return app_instance

async def startup_application():
    """Start the ClimateCoach application"""
    app = get_application()
    await app.startup()
    return app

async def shutdown_application():
    """Shutdown the ClimateCoach application"""
    global app_instance
    if app_instance:
        await app_instance.shutdown()
        app_instance = None

# Example usage
if __name__ == "__main__":
    async def main():
        # Start application
        app = await startup_application()
        
        # Test carbon estimation
        sample_data = {
            'transport': {'distance_km': 20, 'transport_mode': 'car'},
            'energy': {'temperature': 15, 'house_size_m2': 100},
            'shopping': {'income': 50000, 'age': 30},
            'food': {'diet_type': 'omnivore', 'age': 30}
        }
        
        result = app.get_carbon_estimation(sample_data, 'test_user', 'New York, USA')
        print("Carbon Estimation Result:", result)
        
        # Test global climate data
        global_data = await app.get_global_climate_data()
        print("Global Climate Data:", global_data)
        
        # Shutdown application
        await shutdown_application()
    
    # Run example
    asyncio.run(main())
