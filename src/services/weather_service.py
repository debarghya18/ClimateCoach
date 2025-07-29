"""
Weather Service for ClimateCoach
Uses MeteoStat API to fetch and process weather data
"""

import requests
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class WeatherService:
    """
    Weather service for fetching data from MeteoStat API.
    """
    
    BASE_URL = "https://api.meteostat.net/v2"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            'x-api-key': self.api_key
        }
    
    def fetch_current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Fetch current weather data based on latitude and longitude.
        """
        try:
            endpoint = f"{self.BASE_URL}/point/current"
            params = {
                'lat': lat,
                'lon': lon
            }
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json().get('data', [])
            if data:
                return data[0]
            else:
                logger.error("No weather data found for the given location.")
                return {}
        except requests.RequestException as e:
            logger.error(f"Error fetching weather data: {e}")
            return {}

# Example usage
if __name__ == "__main__":
    weather_service = WeatherService(api_key="YOUR_METEOSTAT_API_KEY")
    weather = weather_service.fetch_current_weather(lat=40.7128, lon=-74.0060)  # New York example
    print("Current Weather:", weather)
