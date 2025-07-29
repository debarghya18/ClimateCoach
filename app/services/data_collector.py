"""
Data Collection Service
Collects climate data from various sources including weather APIs, satellite data, and user input
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class LocationData:
    """Structure for location information"""
    latitude: float
    longitude: float
    address: str
    city: str
    country: str
    property_type: str
    size_sqm: Optional[float] = None


@dataclass
class WeatherData:
    """Structure for weather information"""
    temperature: float
    humidity: float
    precipitation: float
    wind_speed: float
    pressure: float
    visibility: float
    uv_index: float
    timestamp: datetime


@dataclass
class PropertySpecs:
    """Structure for property specifications"""
    property_type: str
    size_sqm: float
    construction_year: int
    building_materials: List[str]
    energy_efficiency_rating: str
    insulation_type: str
    heating_system: str
    cooling_system: str


class DataCollectionService:
    """Service for collecting climate and property data from multiple sources"""
    
    def __init__(self):
        self.session = None
        self.geocoder = Nominatim(user_agent="climate-ai-platform")
        self.data_cache = {}
        
    async def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            "status": "active",
            "cache_size": len(self.data_cache),
            "last_collection": datetime.now().isoformat()
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def collect_climate_data(self, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main method to collect comprehensive climate data"""
        try:
            logger.info(f"Starting data collection for location: {location_data}")
            
            # Parse location
            location = self._parse_location_data(location_data)
            
            # Collect data from multiple sources
            weather_data = await self._collect_weather_data(location)
            historical_data = await self._collect_historical_data(location)
            satellite_data = await self._collect_satellite_data(location)
            infrastructure_data = await self._collect_infrastructure_data(location)
            
            # Combine all collected data
            comprehensive_data = {
                "location": location.__dict__,
                "current_weather": weather_data.__dict__ if weather_data else None,
                "historical_data": historical_data,
                "satellite_data": satellite_data,
                "infrastructure": infrastructure_data,
                "collection_timestamp": datetime.now().isoformat(),
                "data_quality": self._assess_data_quality(weather_data, historical_data)
            }
            
            # Cache the results
            cache_key = f"{location.latitude}_{location.longitude}_{datetime.now().strftime('%Y%m%d')}"
            self.data_cache[cache_key] = comprehensive_data
            
            return comprehensive_data
            
        except Exception as e:
            logger.error(f"Data collection failed: {str(e)}")
            raise
    
    def _parse_location_data(self, raw_data: Dict[str, Any]) -> LocationData:
        """Parse and validate location data"""
        latitude = raw_data.get('latitude', raw_data.get('lat', 0.0))
        longitude = raw_data.get('longitude', raw_data.get('lng', 0.0))
        
        # Reverse geocode if address not provided
        address = raw_data.get('address', '')
        if not address and latitude and longitude:
            try:
                location_info = self.geocoder.reverse(f"{latitude}, {longitude}")
                address = location_info.address if location_info else f"{latitude}, {longitude}"
            except Exception:
                address = f"{latitude}, {longitude}"
        
        return LocationData(
            latitude=float(latitude),
            longitude=float(longitude),
            address=address,
            city=raw_data.get('city', ''),
            country=raw_data.get('country', ''),
            property_type=raw_data.get('property_type', 'residential'),
            size_sqm=raw_data.get('size_sqm')
        )
    
    async def _collect_weather_data(self, location: LocationData) -> Optional[WeatherData]:
        """Collect current weather data from weather APIs"""
        try:
            # Using OpenWeatherMap API (example)
            if not settings.WEATHER_API_KEY:
                logger.warning("No weather API key configured, using mock data")
                return self._generate_mock_weather_data(location)
            
            session = await self._get_session()
            url = f"https://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': location.latitude,
                'lon': location.longitude,
                'appid': settings.WEATHER_API_KEY,
                'units': 'metric'
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return WeatherData(
                        temperature=data['main']['temp'],
                        humidity=data['main']['humidity'],
                        precipitation=data.get('rain', {}).get('1h', 0.0),
                        wind_speed=data['wind']['speed'],
                        pressure=data['main']['pressure'],
                        visibility=data.get('visibility', 10000) / 1000,  # Convert to km
                        uv_index=0.0,  # Would need separate UV API call
                        timestamp=datetime.now()
                    )
                else:
                    logger.warning(f"Weather API returned status {response.status}")
                    return self._generate_mock_weather_data(location)
                    
        except Exception as e:
            logger.error(f"Weather data collection failed: {str(e)}")
            return self._generate_mock_weather_data(location)
    
    def _generate_mock_weather_data(self, location: LocationData) -> WeatherData:
        """Generate mock weather data for testing"""
        import random
        
        # Generate realistic values based on location
        base_temp = 20 + (location.latitude / 10)  # Rough temperature estimate
        
        return WeatherData(
            temperature=base_temp + random.uniform(-5, 5),
            humidity=random.uniform(30, 80),
            precipitation=random.uniform(0, 10),
            wind_speed=random.uniform(0, 20),
            pressure=random.uniform(1000, 1030),
            visibility=random.uniform(5, 15),
            uv_index=random.uniform(0, 11),
            timestamp=datetime.now()
        )
    
    async def _collect_historical_data(self, location: LocationData) -> List[Dict[str, Any]]:
        """Collect historical weather patterns"""
        try:
            # This would typically call multiple APIs for historical data
            # For now, generating sample historical data
            historical_data = []
            
            for i in range(30):  # Last 30 days
                date = datetime.now() - timedelta(days=i)
                historical_data.append({
                    "date": date.isoformat(),
                    "temperature_max": 20 + (i % 10),
                    "temperature_min": 15 + (i % 8),
                    "precipitation": max(0, 5 - (i % 7)),
                    "humidity": 50 + (i % 20),
                    "wind_speed": 5 + (i % 10)
                })
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Historical data collection failed: {str(e)}")
            return []
    
    async def _collect_satellite_data(self, location: LocationData) -> Dict[str, Any]:
        """Collect satellite imagery and data"""
        try:
            # This would integrate with satellite APIs like NASA Earth or Sentinel
            # For now, simulating satellite data
            return {
                "vegetation_index": 0.6,
                "land_surface_temperature": 25.5,
                "cloud_cover_percent": 30,
                "soil_moisture": 0.4,
                "image_date": datetime.now().isoformat(),
                "image_quality": "good",
                "source": "satellite_simulation"
            }
            
        except Exception as e:
            logger.error(f"Satellite data collection failed: {str(e)}")
            return {"error": "Satellite data unavailable"}
    
    async def _collect_infrastructure_data(self, location: LocationData) -> Dict[str, Any]:
        """Collect local infrastructure information"""
        try:
            # This would query government databases and mapping services
            # For now, generating sample infrastructure data
            return {
                "nearest_hospital": {
                    "name": "General Hospital",
                    "distance_km": 2.5,
                    "emergency_capacity": "high"
                },
                "nearest_fire_station": {
                    "distance_km": 1.8,
                    "response_time_minutes": 5
                },
                "power_grid": {
                    "reliability_score": 85,
                    "renewable_percentage": 30,
                    "backup_systems": True
                },
                "water_infrastructure": {
                    "supply_reliability": "high",
                    "treatment_capacity": "adequate",
                    "flood_protection": "moderate"
                },
                "transportation": {
                    "road_quality": "good",
                    "public_transport": True,
                    "evacuation_routes": 3
                }
            }
            
        except Exception as e:
            logger.error(f"Infrastructure data collection failed: {str(e)}")
            return {"error": "Infrastructure data unavailable"}
    
    def _assess_data_quality(self, weather_data: Optional[WeatherData], historical_data: List[Dict[str, Any]]) -> str:
        """Assess the quality of collected data"""
        quality_score = 0
        
        if weather_data:
            quality_score += 30
        
        if historical_data and len(historical_data) > 0:
            quality_score += 40
            
        if len(historical_data) >= 30:
            quality_score += 20
            
        # Additional quality checks would go here
        quality_score += 10  # Base score
        
        if quality_score >= 80:
            return "excellent"
        elif quality_score >= 60:
            return "good"
        elif quality_score >= 40:
            return "fair"
        else:
            return "poor"
    
    async def collect_user_property_data(self, user_input: Dict[str, Any]) -> PropertySpecs:
        """Collect and validate user property specifications"""
        try:
            return PropertySpecs(
                property_type=user_input.get('property_type', 'residential'),
                size_sqm=float(user_input.get('size_sqm', 100)),
                construction_year=int(user_input.get('construction_year', 2000)),
                building_materials=user_input.get('building_materials', ['concrete', 'steel']),
                energy_efficiency_rating=user_input.get('energy_rating', 'C'),
                insulation_type=user_input.get('insulation_type', 'standard'),
                heating_system=user_input.get('heating_system', 'gas'),
                cooling_system=user_input.get('cooling_system', 'electric')
            )
            
        except (ValueError, TypeError) as e:
            logger.error(f"Property data validation failed: {str(e)}")
            # Return default property specs
            return PropertySpecs(
                property_type='residential',
                size_sqm=100,
                construction_year=2000,
                building_materials=['concrete'],
                energy_efficiency_rating='C',
                insulation_type='standard',
                heating_system='gas',
                cooling_system='electric'
            )
    
    async def collect_budget_constraints(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Collect user budget and timeline constraints"""
        return {
            "total_budget": user_input.get('total_budget', 50000),
            "budget_breakdown": {
                "emergency_fund": user_input.get('emergency_budget', 10000),
                "adaptation_budget": user_input.get('adaptation_budget', 30000),
                "maintenance_budget": user_input.get('maintenance_budget', 10000)
            },
            "timeline": {
                "immediate_actions": user_input.get('immediate_timeline', '1-3 months'),
                "short_term_goals": user_input.get('short_term_timeline', '6-12 months'),
                "long_term_vision": user_input.get('long_term_timeline', '2-5 years')
            },
            "priority_areas": user_input.get('priority_areas', ['safety', 'efficiency', 'comfort'])
        }
    
    async def validate_coordinates(self, latitude: float, longitude: float) -> bool:
        """Validate GPS coordinates"""
        return (-90 <= latitude <= 90) and (-180 <= longitude <= 180)
    
    async def get_nearby_locations(self, location: LocationData, radius_km: float = 50) -> List[Dict[str, Any]]:
        """Get nearby locations for comparative analysis"""
        try:
            # This would query location databases
            # For now, generating sample nearby locations
            nearby = []
            for i in range(5):
                # Generate points within radius
                lat_offset = (i - 2) * 0.01
                lng_offset = (i - 2) * 0.01
                
                nearby.append({
                    "name": f"Location {i+1}",
                    "latitude": location.latitude + lat_offset,
                    "longitude": location.longitude + lng_offset,
                    "distance_km": geodesic(
                        (location.latitude, location.longitude),
                        (location.latitude + lat_offset, location.longitude + lng_offset)
                    ).kilometers,
                    "similarity_score": 0.8 - (i * 0.1)
                })
            
            return nearby
            
        except Exception as e:
            logger.error(f"Nearby locations search failed: {str(e)}")
            return []
    
    async def close(self):
        """Clean up resources"""
        if self.session and not self.session.closed:
            await self.session.close()
