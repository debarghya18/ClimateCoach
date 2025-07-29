"""
Global Climate Data Service for ClimateCoach
Integrates satellite and weather APIs for worldwide climate monitoring
"""

import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from meteostat import Point, Daily, Hourly
import asyncio
import aiohttp
from geopy.geocoders import Nominatim
import os

logger = logging.getLogger(__name__)

class GlobalClimateService:
    """
    Service for fetching and analyzing global climate data
    """
    
    def __init__(self, nasa_api_key: Optional[str] = None, meteostat_api_key: Optional[str] = None):
        """
        Initialize global climate service
        
        Args:
            nasa_api_key: NASA API key for satellite data
            meteostat_api_key: Meteostat API key for weather data
        """
        self.nasa_api_key = nasa_api_key or os.getenv('NASA_API_KEY')
        self.meteostat_api_key = meteostat_api_key or os.getenv('METEOSTAT_API_KEY')
        self.geolocator = Nominatim(user_agent="climatecoach")
        
        # API endpoints
        self.nasa_base_url = "https://api.nasa.gov/planetary"
        self.earth_data_url = "https://appeears.earthdatacloud.nasa.gov/api/v1"
        
        # Climate indicators thresholds
        self.climate_thresholds = {
            'temperature': {
                'extreme_hot': 40,
                'hot': 30,
                'warm': 25,
                'moderate': 15,
                'cold': 5,
                'extreme_cold': -10
            },
            'precipitation': {
                'drought': 0.1,
                'low': 5,
                'moderate': 20,
                'high': 50,
                'extreme': 100
            },
            'air_quality': {
                'good': 50,
                'moderate': 100,
                'unhealthy_sensitive': 150,
                'unhealthy': 200,
                'very_unhealthy': 250,
                'hazardous': 300
            }
        }
        
        logger.info("Global Climate Service initialized")
    
    async def get_global_climate_overview(self) -> Dict[str, Any]:
        """
        Get global climate overview with key indicators
        
        Returns:
            Dictionary containing global climate data
        """
        try:
            # Major cities for global overview
            major_cities = [
                {'name': 'New York', 'lat': 40.7128, 'lon': -74.0060},
                {'name': 'London', 'lat': 51.5074, 'lon': -0.1278},
                {'name': 'Tokyo', 'lat': 35.6762, 'lon': 139.6503},
                {'name': 'Sydney', 'lat': -33.8688, 'lon': 151.2093},
                {'name': 'São Paulo', 'lat': -23.5505, 'lon': -46.6333},
                {'name': 'Cairo', 'lat': 30.0444, 'lon': 31.2357},
                {'name': 'Mumbai', 'lat': 19.0760, 'lon': 72.8777},
                {'name': 'Lagos', 'lat': 6.5244, 'lon': 3.3792}
            ]
            
            # Collect data for all cities
            city_data = []
            
            async with aiohttp.ClientSession() as session:
                tasks = []
                for city in major_cities:
                    task = self._get_city_climate_data(session, city)
                    tasks.append(task)
                
                city_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(city_results):
                if not isinstance(result, Exception) and result:
                    city_data.append({
                        'city': major_cities[i]['name'],
                        **result
                    })
            
            # Calculate global indicators
            global_indicators = self._calculate_global_indicators(city_data)
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'global_indicators': global_indicators,
                'city_data': city_data,
                'climate_alerts': self._generate_climate_alerts(city_data),
                'recommendations': self._generate_global_recommendations(global_indicators)
            }
            
        except Exception as e:
            logger.error(f"Error getting global climate overview: {e}")
            return self._get_fallback_global_data()
    
    async def _get_city_climate_data(self, session: aiohttp.ClientSession, city: Dict) -> Dict[str, Any]:
        """Get climate data for a specific city"""
        try:
            # Get weather data
            weather_data = await self._get_weather_data(city['lat'], city['lon'])
            
            # Get air quality data
            air_quality = await self._get_air_quality_data(session, city['lat'], city['lon'])
            
            # Get satellite data
            satellite_data = await self._get_satellite_environmental_data(session, city['lat'], city['lon'])
            
            return {
                'coordinates': {'lat': city['lat'], 'lon': city['lon']},
                'weather': weather_data,
                'air_quality': air_quality,
                'environmental': satellite_data,
                'climate_risk': self._assess_climate_risk(weather_data, air_quality, satellite_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting climate data for {city.get('name', 'unknown')}: {e}")
            return {}
    
    async def _get_weather_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get weather data using Meteostat"""
        try:
            # Create Point
            location = Point(lat, lon)
            
            # Get current data (last 7 days)
            end = datetime.now()
            start = end - timedelta(days=7)
            
            # Get daily data
            data = Daily(location, start, end)
            df = data.fetch()
            
            if df.empty:
                return self._get_fallback_weather_data()
            
            # Get latest data
            latest = df.iloc[-1]
            
            return {
                'temperature': {
                    'current': float(latest.get('tavg', 20)) if pd.notna(latest.get('tavg')) else 20.0,
                    'min': float(latest.get('tmin', 15)) if pd.notna(latest.get('tmin')) else 15.0,
                    'max': float(latest.get('tmax', 25)) if pd.notna(latest.get('tmax')) else 25.0
                },
                'precipitation': float(latest.get('prcp', 0)) if pd.notna(latest.get('prcp')) else 0.0,
                'humidity': float(latest.get('rhum', 50)) if pd.notna(latest.get('rhum')) else 50.0,
                'wind_speed': float(latest.get('wspd', 10)) if pd.notna(latest.get('wspd')) else 10.0,
                'pressure': float(latest.get('pres', 1013)) if pd.notna(latest.get('pres')) else 1013.0,
                'weekly_trend': self._calculate_weather_trend(df)
            }
            
        except Exception as e:
            logger.error(f"Error getting weather data: {e}")
            return self._get_fallback_weather_data()
    
    async def _get_air_quality_data(self, session: aiohttp.ClientSession, lat: float, lon: float) -> Dict[str, Any]:
        """Get air quality data"""
        try:
            # Try OpenWeatherMap Air Pollution API (free)
            api_key = os.getenv('OPENWEATHER_API_KEY')
            if api_key:
                url = f"http://api.openweathermap.org/data/2.5/air_pollution"
                params = {'lat': lat, 'lon': lon, 'appid': api_key}
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        components = data['list'][0]['components']
                        aqi = data['list'][0]['main']['aqi']
                        
                        return {
                            'aqi': aqi,
                            'pm2_5': components.get('pm2_5', 15),
                            'pm10': components.get('pm10', 25),
                            'no2': components.get('no2', 30),
                            'so2': components.get('so2', 10),
                            'co': components.get('co', 200),
                            'o3': components.get('o3', 80),
                            'quality_level': self._get_air_quality_level(aqi)
                        }
            
            # Fallback to estimated values based on location
            return self._estimate_air_quality(lat, lon)
            
        except Exception as e:
            logger.error(f"Error getting air quality data: {e}")
            return self._get_fallback_air_quality()
    
    async def _get_satellite_environmental_data(self, session: aiohttp.ClientSession, lat: float, lon: float) -> Dict[str, Any]:
        """Get environmental data from satellite APIs"""
        try:
            # Use NASA Earth API if available
            if self.nasa_api_key:
                # Land Surface Temperature
                lst_data = await self._get_nasa_lst_data(session, lat, lon)
                
                # Vegetation Index
                ndvi_data = await self._get_nasa_ndvi_data(session, lat, lon)
                
                return {
                    'land_surface_temperature': lst_data,
                    'vegetation_health': ndvi_data,
                    'environmental_risk': self._calculate_environmental_risk(lst_data, ndvi_data)
                }
            else:
                # Fallback to estimated data
                return self._estimate_satellite_data(lat, lon)
                
        except Exception as e:
            logger.error(f"Error getting satellite data: {e}")
            return self._get_fallback_satellite_data()
    
    async def _get_nasa_lst_data(self, session: aiohttp.ClientSession, lat: float, lon: float) -> Dict[str, Any]:
        """Get Land Surface Temperature from NASA"""
        try:
            # NASA Earth API for LST
            url = f"{self.nasa_base_url}/earth/temperature"
            params = {
                'lon': lon,
                'lat': lat,
                'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                'dim': 0.1,
                'api_key': self.nasa_api_key
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'temperature': data.get('temperature', 25.0),
                        'date': params['date'],
                        'quality': 'satellite'
                    }
                
        except Exception as e:
            logger.error(f"Error getting NASA LST data: {e}")
        
        # Fallback
        return {'temperature': 25.0, 'quality': 'estimated'}
    
    async def _get_nasa_ndvi_data(self, session: aiohttp.ClientSession, lat: float, lon: float) -> Dict[str, Any]:
        """Get NDVI (vegetation) data from NASA"""
        try:
            # Placeholder for NDVI data - would use NASA MODIS or Landsat
            # For production, integrate with NASA Earth Data API
            
            # Estimate based on location
            vegetation_index = self._estimate_vegetation_index(lat, lon)
            
            return {
                'ndvi': vegetation_index,
                'vegetation_health': self._categorize_vegetation_health(vegetation_index),
                'quality': 'estimated'
            }
            
        except Exception as e:
            logger.error(f"Error getting NDVI data: {e}")
            return {'ndvi': 0.5, 'vegetation_health': 'moderate', 'quality': 'estimated'}
    
    def get_location_climate_summary(self, location: str) -> Dict[str, Any]:
        """
        Get climate summary for a specific location
        
        Args:
            location: Location name or coordinates
            
        Returns:
            Climate summary for the location
        """
        try:
            # Geocode location
            coords = self._geocode_location(location)
            if not coords:
                return {'error': 'Location not found'}
            
            lat, lon = coords['lat'], coords['lon']
            
            # Get comprehensive climate data
            climate_data = asyncio.run(self._get_city_climate_data(None, {
                'name': location,
                'lat': lat,
                'lon': lon
            }))
            
            # Add location context
            climate_data['location'] = {
                'name': location,
                'coordinates': coords,
                'timezone': self._get_timezone_info(lat, lon)
            }
            
            # Generate location-specific insights
            climate_data['insights'] = self._generate_location_insights(climate_data)
            
            return climate_data
            
        except Exception as e:
            logger.error(f"Error getting climate summary for {location}: {e}")
            return {'error': str(e)}
    
    def _geocode_location(self, location: str) -> Optional[Dict[str, float]]:
        """Geocode location to coordinates"""
        try:
            location_data = self.geolocator.geocode(location)
            if location_data:
                return {
                    'lat': location_data.latitude,
                    'lon': location_data.longitude
                }
        except Exception as e:
            logger.error(f"Error geocoding location {location}: {e}")
        
        return None
    
    def _calculate_global_indicators(self, city_data: List[Dict]) -> Dict[str, Any]:
        """Calculate global climate indicators"""
        if not city_data:
            return {}
        
        try:
            # Extract temperature data
            temperatures = []
            precipitation = []
            air_quality = []
            
            for city in city_data:
                if 'weather' in city and 'temperature' in city['weather']:
                    temperatures.append(city['weather']['temperature']['current'])
                    precipitation.append(city['weather'].get('precipitation', 0))
                
                if 'air_quality' in city:
                    air_quality.append(city['air_quality'].get('aqi', 3))
            
            return {
                'global_temperature': {
                    'average': np.mean(temperatures) if temperatures else 20.0,
                    'range': [min(temperatures), max(temperatures)] if temperatures else [15.0, 25.0],
                    'trend': 'stable'  # Would calculate from historical data
                },
                'precipitation_patterns': {
                    'average': np.mean(precipitation) if precipitation else 5.0,
                    'distribution': 'normal'  # Would analyze patterns
                },
                'global_air_quality': {
                    'average_aqi': np.mean(air_quality) if air_quality else 3,
                    'pollution_hotspots': len([aqi for aqi in air_quality if aqi >= 4])
                },
                'climate_change_indicators': {
                    'warming_trend': 'moderate',
                    'extreme_events': 'increasing',
                    'sea_level_trend': 'rising'
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating global indicators: {e}")
            return {}
    
    def _generate_climate_alerts(self, city_data: List[Dict]) -> List[Dict[str, Any]]:
        """Generate climate alerts based on current conditions"""
        alerts = []
        
        for city in city_data:
            city_name = city.get('city', 'Unknown')
            
            # Temperature alerts
            if 'weather' in city:
                temp = city['weather']['temperature']['current']
                if temp > self.climate_thresholds['temperature']['extreme_hot']:
                    alerts.append({
                        'type': 'extreme_heat',
                        'location': city_name,
                        'severity': 'high',
                        'message': f"Extreme heat warning in {city_name}: {temp}°C",
                        'recommendations': ['Stay indoors', 'Drink plenty of water', 'Avoid outdoor activities']
                    })
                elif temp < self.climate_thresholds['temperature']['extreme_cold']:
                    alerts.append({
                        'type': 'extreme_cold',
                        'location': city_name,
                        'severity': 'high',
                        'message': f"Extreme cold warning in {city_name}: {temp}°C",
                        'recommendations': ['Dress warmly', 'Limit outdoor exposure', 'Check heating systems']
                    })
            
            # Air quality alerts
            if 'air_quality' in city:
                aqi = city['air_quality'].get('aqi', 3)
                if aqi >= 4:  # Unhealthy levels
                    alerts.append({
                        'type': 'air_pollution',
                        'location': city_name,
                        'severity': 'medium',
                        'message': f"Poor air quality in {city_name}",
                        'recommendations': ['Limit outdoor activities', 'Use air purifiers', 'Wear masks outdoors']
                    })
        
        return alerts
    
    def _generate_global_recommendations(self, global_indicators: Dict) -> List[str]:
        """Generate global climate action recommendations"""
        recommendations = []
        
        if global_indicators:
            avg_temp = global_indicators.get('global_temperature', {}).get('average', 20)
            if avg_temp > 25:
                recommendations.append("Global temperatures are elevated. Focus on energy efficiency and renewable energy adoption.")
            
            avg_aqi = global_indicators.get('global_air_quality', {}).get('average_aqi', 3)
            if avg_aqi >= 3:
                recommendations.append("Air quality concerns detected. Promote clean transportation and industrial emission controls.")
            
            recommendations.extend([
                "Support climate adaptation measures in vulnerable communities",
                "Invest in sustainable urban planning and green infrastructure",
                "Promote international cooperation on climate change mitigation"
            ])
        
        return recommendations
    
    def _assess_climate_risk(self, weather: Dict, air_quality: Dict, environmental: Dict) -> Dict[str, Any]:
        """Assess climate risk for a location"""
        risk_factors = []
        risk_score = 0
        
        # Temperature risk
        temp = weather.get('temperature', {}).get('current', 20)
        if temp > 35 or temp < 0:
            risk_factors.append('extreme_temperature')
            risk_score += 30
        elif temp > 30 or temp < 5:
            risk_factors.append('high_temperature_variation')
            risk_score += 15
        
        # Air quality risk
        aqi = air_quality.get('aqi', 3)
        if aqi >= 4:
            risk_factors.append('poor_air_quality')
            risk_score += 25
        elif aqi >= 3:
            risk_factors.append('moderate_air_quality')
            risk_score += 10
        
        # Environmental risk
        vegetation_health = environmental.get('vegetation_health', {}).get('ndvi', 0.5)
        if vegetation_health < 0.3:
            risk_factors.append('poor_vegetation')
            risk_score += 20
        
        # Determine risk level
        if risk_score >= 60:
            risk_level = 'high'
        elif risk_score >= 30:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'recommendations': self._get_risk_recommendations(risk_level, risk_factors)
        }
    
    def _get_risk_recommendations(self, risk_level: str, risk_factors: List[str]) -> List[str]:
        """Get recommendations based on climate risk"""
        recommendations = []
        
        if 'extreme_temperature' in risk_factors:
            recommendations.append("Take precautions for extreme temperature conditions")
        
        if 'poor_air_quality' in risk_factors:
            recommendations.append("Limit outdoor activities and use air filtration")
        
        if 'poor_vegetation' in risk_factors:
            recommendations.append("Support local reforestation and green space initiatives")
        
        if risk_level == 'high':
            recommendations.append("Consider climate adaptation strategies for your area")
        
        return recommendations
    
    # Fallback and helper methods
    def _get_fallback_global_data(self) -> Dict[str, Any]:
        """Fallback global climate data"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'global_indicators': {
                'global_temperature': {'average': 20.0, 'trend': 'stable'},
                'global_air_quality': {'average_aqi': 3}
            },
            'city_data': [],
            'climate_alerts': [],
            'recommendations': [
                "Monitor local weather conditions",
                "Reduce personal carbon footprint",
                "Support sustainable practices"
            ]
        }
    
    def _get_fallback_weather_data(self) -> Dict[str, Any]:
        """Fallback weather data"""
        return {
            'temperature': {'current': 20.0, 'min': 15.0, 'max': 25.0},
            'precipitation': 0.0,
            'humidity': 50.0,
            'wind_speed': 10.0,
            'pressure': 1013.0,
            'weekly_trend': 'stable'
        }
    
    def _get_fallback_air_quality(self) -> Dict[str, Any]:
        """Fallback air quality data"""
        return {
            'aqi': 3,
            'pm2_5': 15,
            'pm10': 25,
            'quality_level': 'moderate'
        }
    
    def _get_fallback_satellite_data(self) -> Dict[str, Any]:
        """Fallback satellite data"""
        return {
            'land_surface_temperature': {'temperature': 25.0, 'quality': 'estimated'},
            'vegetation_health': {'ndvi': 0.5, 'vegetation_health': 'moderate'},
            'environmental_risk': 'low'
        }
    
    def _calculate_weather_trend(self, df: pd.DataFrame) -> str:
        """Calculate weather trend from historical data"""
        if len(df) < 3:
            return 'stable'
        
        temps = df['tavg'].dropna()
        if len(temps) < 3:
            return 'stable'
        
        # Simple trend calculation
        recent_avg = temps.tail(3).mean()
        older_avg = temps.head(3).mean()
        
        if recent_avg - older_avg > 2:
            return 'warming'
        elif older_avg - recent_avg > 2:
            return 'cooling'
        else:
            return 'stable'
    
    def _get_air_quality_level(self, aqi: int) -> str:
        """Convert AQI number to quality level"""
        levels = {1: 'good', 2: 'fair', 3: 'moderate', 4: 'poor', 5: 'very_poor'}
        return levels.get(aqi, 'moderate')
    
    def _estimate_air_quality(self, lat: float, lon: float) -> Dict[str, Any]:
        """Estimate air quality based on location"""
        # Simple estimation based on latitude (equator tends to have better air quality)
        base_aqi = 3  # Moderate
        
        # Adjust based on latitude (very rough estimation)
        if abs(lat) < 30:  # Tropical regions
            estimated_aqi = 2
        elif abs(lat) > 60:  # Polar regions
            estimated_aqi = 2
        else:  # Temperate regions (often more industrialized)
            estimated_aqi = 3
        
        return {
            'aqi': estimated_aqi,
            'pm2_5': 15,
            'pm10': 25,
            'quality_level': self._get_air_quality_level(estimated_aqi)
        }
    
    def _estimate_satellite_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Estimate satellite data based on location"""
        return {
            'land_surface_temperature': {'temperature': 25.0, 'quality': 'estimated'},
            'vegetation_health': {'ndvi': 0.5, 'vegetation_health': 'moderate'},
            'environmental_risk': 'low'
        }
    
    def _estimate_vegetation_index(self, lat: float, lon: float) -> float:
        """Estimate vegetation index based on location"""
        # Simple estimation: tropical regions have higher NDVI
        if abs(lat) < 23.5:  # Tropical
            return 0.7
        elif abs(lat) < 45:  # Temperate
            return 0.5
        else:  # Cold regions
            return 0.3
    
    def _categorize_vegetation_health(self, ndvi: float) -> str:
        """Categorize vegetation health based on NDVI"""
        if ndvi > 0.6:
            return 'excellent'
        elif ndvi > 0.4:
            return 'good'
        elif ndvi > 0.2:
            return 'moderate'
        else:
            return 'poor'
    
    def _get_timezone_info(self, lat: float, lon: float) -> str:
        """Get timezone information for coordinates"""
        # Simple timezone estimation based on longitude
        # In production, use a proper timezone API
        timezone_offset = int(lon / 15)
        return f"UTC{timezone_offset:+d}"
    
    def _generate_location_insights(self, climate_data: Dict) -> List[str]:
        """Generate location-specific climate insights"""
        insights = []
        
        if 'weather' in climate_data:
            temp = climate_data['weather']['temperature']['current']
            if temp > 30:
                insights.append("High temperatures detected. Focus on cooling efficiency and heat protection.")
            elif temp < 5:
                insights.append("Cold conditions present. Optimize heating systems and insulation.")
        
        if 'air_quality' in climate_data:
            aqi = climate_data['air_quality'].get('aqi', 3)
            if aqi >= 4:
                insights.append("Poor air quality. Consider indoor air filtration and limit outdoor exposure.")
        
        if 'climate_risk' in climate_data:
            risk_level = climate_data['climate_risk'].get('risk_level', 'low')
            if risk_level == 'high':
                insights.append("High climate risk area. Implement comprehensive adaptation strategies.")
        
        return insights

# Example usage
if __name__ == "__main__":
    climate_service = GlobalClimateService()
    
    # Get global climate overview
    global_data = asyncio.run(climate_service.get_global_climate_overview())
    print("Global Climate Overview:", global_data)
    
    # Get location-specific data
    location_data = climate_service.get_location_climate_summary("New York, USA")
    print("Location Climate Summary:", location_data)
