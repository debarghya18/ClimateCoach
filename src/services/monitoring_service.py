"""
Monitoring Service for ClimateCoach
Collects and exposes metrics for Prometheus
"""

from prometheus_client import Counter, Histogram, Gauge, start_http_server, CollectorRegistry
import time
import psutil
import logging
from typing import Dict, Any
import threading
import os

logger = logging.getLogger(__name__)

class MonitoringService:
    """
    Service for collecting and exposing application metrics
    """
    
    def __init__(self, port: int = 8502):
        """
        Initialize monitoring service
        
        Args:
            port: Port to expose metrics on
        """
        self.port = port
        self.registry = CollectorRegistry()
        
        # Application metrics
        self.carbon_calculations = Counter(
            'carbon_calculations_total',
            'Total number of carbon footprint calculations',
            registry=self.registry
        )
        
        self.user_interactions = Counter(
            'user_interactions_total',
            'Total number of user interactions',
            ['interaction_type'],
            registry=self.registry
        )
        
        self.recommendation_requests = Counter(
            'recommendation_requests_total',
            'Total number of AI recommendation requests',
            registry=self.registry
        )
        
        self.sentiment_analyses = Counter(
            'sentiment_analyses_total',
            'Total number of sentiment analyses performed',
            registry=self.registry
        )
        
        # Performance metrics
        self.request_duration = Histogram(
            'request_duration_seconds',
            'Request duration in seconds',
            ['endpoint'],
            registry=self.registry
        )
        
        self.active_users = Gauge(
            'active_users',
            'Number of currently active users',
            registry=self.registry
        )
        
        # System metrics
        self.cpu_usage = Gauge(
            'cpu_usage_percent',
            'CPU usage percentage',
            registry=self.registry
        )
        
        self.memory_usage = Gauge(
            'memory_usage_bytes',
            'Memory usage in bytes',
            registry=self.registry
        )
        
        self.disk_usage = Gauge(
            'disk_usage_percent',
            'Disk usage percentage',
            registry=self.registry
        )
        
        # Climate-specific metrics
        self.co2_saved = Counter(
            'co2_saved_kg_total',
            'Total CO2 saved in kilograms',
            registry=self.registry
        )
        
        self.green_actions = Counter(
            'green_actions_total',
            'Total number of green actions taken',
            ['action_type'],
            registry=self.registry
        )
        
        self.habit_detections = Counter(
            'habit_detections_total',
            'Total number of habit pattern detections',
            registry=self.registry
        )
        
        # Model performance metrics
        self.model_predictions = Counter(
            'model_predictions_total',
            'Total number of ML model predictions',
            ['model_type'],
            registry=self.registry
        )
        
        self.model_accuracy = Gauge(
            'model_accuracy',
            'Current model accuracy score',
            ['model_type'],
            registry=self.registry
        )
        
        # Start monitoring thread
        self._start_system_monitoring()
        
        logger.info(f"Monitoring service initialized on port {port}")
    
    def start_metrics_server(self):
        """Start Prometheus metrics server"""
        try:
            start_http_server(self.port, registry=self.registry)
            logger.info(f"Metrics server started on port {self.port}")
        except Exception as e:
            logger.error(f"Failed to start metrics server: {e}")
    
    def record_carbon_calculation(self, user_id: str, calculation_type: str):
        """Record a carbon footprint calculation"""
        self.carbon_calculations.inc()
        logger.debug(f"Recorded carbon calculation for user {user_id[:8]}...")
    
    def record_user_interaction(self, interaction_type: str):
        """Record user interaction"""
        self.user_interactions.labels(interaction_type=interaction_type).inc()
        logger.debug(f"Recorded user interaction: {interaction_type}")
    
    def record_recommendation_request(self):
        """Record AI recommendation request"""
        self.recommendation_requests.inc()
        logger.debug("Recorded recommendation request")
    
    def record_sentiment_analysis(self):
        """Record sentiment analysis"""
        self.sentiment_analyses.inc()
        logger.debug("Recorded sentiment analysis")
    
    def record_request_duration(self, endpoint: str, duration: float):
        """Record request duration"""
        self.request_duration.labels(endpoint=endpoint).observe(duration)
        logger.debug(f"Recorded request duration for {endpoint}: {duration}s")
    
    def update_active_users(self, count: int):
        """Update active users count"""
        self.active_users.set(count)
        logger.debug(f"Updated active users count: {count}")
    
    def record_co2_saved(self, amount_kg: float):
        """Record CO2 saved"""
        self.co2_saved.inc(amount_kg)
        logger.debug(f"Recorded CO2 saved: {amount_kg} kg")
    
    def record_green_action(self, action_type: str):
        """Record green action taken"""
        self.green_actions.labels(action_type=action_type).inc()
        logger.debug(f"Recorded green action: {action_type}")
    
    def record_habit_detection(self):
        """Record habit pattern detection"""
        self.habit_detections.inc()
        logger.debug("Recorded habit detection")
    
    def record_model_prediction(self, model_type: str):
        """Record ML model prediction"""
        self.model_predictions.labels(model_type=model_type).inc()
        logger.debug(f"Recorded model prediction: {model_type}")
    
    def update_model_accuracy(self, model_type: str, accuracy: float):
        """Update model accuracy score"""
        self.model_accuracy.labels(model_type=model_type).set(accuracy)
        logger.debug(f"Updated model accuracy for {model_type}: {accuracy}")
    
    def _start_system_monitoring(self):
        """Start system monitoring in background thread"""
        def monitor_system():
            while True:
                try:
                    # CPU usage
                    cpu_percent = psutil.cpu_percent(interval=1)
                    self.cpu_usage.set(cpu_percent)
                    
                    # Memory usage
                    memory = psutil.virtual_memory()
                    self.memory_usage.set(memory.used)
                    
                    # Disk usage
                    disk = psutil.disk_usage('/')
                    disk_percent = (disk.used / disk.total) * 100
                    self.disk_usage.set(disk_percent)
                    
                    time.sleep(30)  # Update every 30 seconds
                    
                except Exception as e:
                    logger.error(f"Error monitoring system metrics: {e}")
                    time.sleep(60)  # Wait longer on error
        
        monitoring_thread = threading.Thread(target=monitor_system, daemon=True)
        monitoring_thread.start()
        logger.info("Started system monitoring thread")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get application health status"""
        try:
            return {
                'status': 'healthy',
                'timestamp': time.time(),
                'metrics': {
                    'carbon_calculations': self.carbon_calculations._value._value,
                    'user_interactions': sum(
                        metric._value._value for metric in 
                        self.user_interactions._metrics.values()
                    ),
                    'cpu_usage': self.cpu_usage._value._value,
                    'memory_usage': self.memory_usage._value._value,
                    'active_users': self.active_users._value._value
                }
            }
        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            return {
                'status': 'error',
                'timestamp': time.time(),
                'error': str(e)
            }
    
    def export_metrics(self) -> str:
        """Export metrics in Prometheus format"""
        try:
            from prometheus_client import generate_latest
            return generate_latest(self.registry).decode('utf-8')
        except Exception as e:
            logger.error(f"Error exporting metrics: {e}")
            return ""

# Global monitoring instance
monitoring_service = None

def get_monitoring_service() -> MonitoringService:
    """Get global monitoring service instance"""
    global monitoring_service
    if monitoring_service is None:
        monitoring_service = MonitoringService()
        if os.getenv('PROMETHEUS_ENABLED', 'false').lower() == 'true':
            monitoring_service.start_metrics_server()
    return monitoring_service

# Decorator for monitoring function execution time
def monitor_execution_time(endpoint: str):
    """Decorator to monitor function execution time"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                get_monitoring_service().record_request_duration(endpoint, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                get_monitoring_service().record_request_duration(f"{endpoint}_error", duration)
                raise e
        return wrapper
    return decorator

# Example usage
if __name__ == "__main__":
    # Initialize monitoring service
    monitoring = MonitoringService()
    monitoring.start_metrics_server()
    
    # Simulate some metrics
    monitoring.record_carbon_calculation("user123", "daily")
    monitoring.record_user_interaction("dashboard_view")
    monitoring.record_co2_saved(2.5)
    
    print("Monitoring service running. Check http://localhost:8502/metrics")
    
    # Keep running
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("Monitoring service stopped")
