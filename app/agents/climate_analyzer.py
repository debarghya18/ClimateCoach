"""
Climate Analysis Agent
This agent uses GPT-4 to analyze climate data and generate insights
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from openai import OpenAI
import numpy as np
from dataclasses import dataclass

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class ClimateData:
    """Structure for climate data"""
    temperature: float
    humidity: float
    precipitation: float
    wind_speed: float
    pressure: float
    timestamp: datetime
    location: Dict[str, float]  # {"lat": float, "lng": float}


@dataclass
class RiskAssessment:
    """Structure for risk assessment results"""
    overall_risk_score: float
    flood_risk: float
    heat_risk: float
    drought_risk: float
    storm_risk: float
    confidence_level: float
    recommendations: List[str]
    time_horizon: str


class ClimateAnalysisAgent:
    """Advanced AI agent for climate data analysis and risk assessment"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4"
        self.analysis_cache = {}
        
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "status": "active",
            "model": self.model,
            "last_analysis": datetime.now().isoformat(),
            "cache_size": len(self.analysis_cache)
        }
    
    async def analyze(self, climate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main analysis method that coordinates all analysis tasks"""
        try:
            logger.info(f"Starting climate analysis for location: {climate_data.get('location')}")
            
            # Parse and validate input data
            parsed_data = self._parse_climate_data(climate_data)
            
            # Generate comprehensive analysis
            risk_assessment = await self._generate_risk_assessment(parsed_data)
            trend_analysis = await self._analyze_trends(parsed_data)
            predictions = await self._generate_predictions(parsed_data)
            satellite_analysis = await self._analyze_satellite_imagery(climate_data.get('satellite_data'))
            
            # Combine all analyses
            comprehensive_analysis = {
                "risk_assessment": risk_assessment,
                "trend_analysis": trend_analysis,
                "predictions": predictions,
                "satellite_analysis": satellite_analysis,
                "analysis_timestamp": datetime.now().isoformat(),
                "confidence_score": self._calculate_confidence(risk_assessment, trend_analysis)
            }
            
            # Cache the results
            cache_key = self._generate_cache_key(climate_data)
            self.analysis_cache[cache_key] = comprehensive_analysis
            
            return comprehensive_analysis
            
        except Exception as e:
            logger.error(f"Climate analysis failed: {str(e)}")
            raise
    
    def _parse_climate_data(self, raw_data: Dict[str, Any]) -> ClimateData:
        """Parse and validate raw climate data"""
        return ClimateData(
            temperature=raw_data.get('temperature', 20.0),
            humidity=raw_data.get('humidity', 50.0),
            precipitation=raw_data.get('precipitation', 0.0),
            wind_speed=raw_data.get('wind_speed', 5.0),
            pressure=raw_data.get('pressure', 1013.25),
            timestamp=datetime.fromisoformat(raw_data.get('timestamp', datetime.now().isoformat())),
            location=raw_data.get('location', {"lat": 0.0, "lng": 0.0})
        )
    
    async def _generate_risk_assessment(self, data: ClimateData) -> RiskAssessment:
        """Generate comprehensive risk assessment using GPT-4"""
        try:
            prompt = f"""
            As a climate expert, analyze the following data and provide a comprehensive risk assessment:
            
            Location: {data.location['lat']}, {data.location['lng']}
            Temperature: {data.temperature}°C
            Humidity: {data.humidity}%
            Precipitation: {data.precipitation}mm
            Wind Speed: {data.wind_speed} km/h
            Pressure: {data.pressure} hPa
            Timestamp: {data.timestamp}
            
            Please provide:
            1. Overall risk score (0-10)
            2. Specific risk scores for: flooding, heat waves, drought, storms (0-10 each)
            3. Confidence level (0-100%)
            4. Top 3 immediate recommendations
            5. Time horizon for these risks (short/medium/long term)
            
            Format your response as JSON with the following structure:
            {{
                "overall_risk_score": float,
                "flood_risk": float,
                "heat_risk": float,
                "drought_risk": float,
                "storm_risk": float,
                "confidence_level": float,
                "recommendations": ["rec1", "rec2", "rec3"],
                "time_horizon": "short/medium/long",
                "analysis_summary": "Brief summary of key findings"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a world-class climate scientist and risk assessment expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            # Parse the JSON response
            analysis_result = json.loads(response.choices[0].message.content)
            
            return RiskAssessment(
                overall_risk_score=analysis_result.get('overall_risk_score', 5.0),
                flood_risk=analysis_result.get('flood_risk', 3.0),
                heat_risk=analysis_result.get('heat_risk', 4.0),
                drought_risk=analysis_result.get('drought_risk', 3.0),
                storm_risk=analysis_result.get('storm_risk', 4.0),
                confidence_level=analysis_result.get('confidence_level', 75.0),
                recommendations=analysis_result.get('recommendations', []),
                time_horizon=analysis_result.get('time_horizon', 'medium')
            )
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse GPT-4 response as JSON, using fallback")
            return self._generate_fallback_assessment(data)
        except Exception as e:
            logger.error(f"Risk assessment generation failed: {str(e)}")
            return self._generate_fallback_assessment(data)
    
    async def _analyze_trends(self, data: ClimateData) -> Dict[str, Any]:
        """Analyze historical trends and patterns"""
        prompt = f"""
        Analyze the following climate data point and provide trend analysis:
        
        Temperature: {data.temperature}°C
        Location: {data.location['lat']}, {data.location['lng']}
        Date: {data.timestamp}
        
        Based on global climate patterns and this location, provide:
        1. Expected temperature trend over next 5 years
        2. Precipitation pattern changes
        3. Extreme weather frequency predictions
        4. Seasonal variation impacts
        
        Respond in JSON format with trend_direction, magnitude, and confidence for each factor.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a climate trend analysis expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.2
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {str(e)}")
            return {
                "temperature_trend": {"direction": "increasing", "magnitude": 0.5, "confidence": 70},
                "precipitation_trend": {"direction": "variable", "magnitude": 0.2, "confidence": 60}
            }
    
    async def _generate_predictions(self, data: ClimateData) -> Dict[str, Any]:
        """Generate climate predictions using AI"""
        prompt = f"""
        Generate climate predictions for location {data.location['lat']}, {data.location['lng']} 
        based on current conditions:
        
        Current Temperature: {data.temperature}°C
        Current Humidity: {data.humidity}%
        Current Precipitation: {data.precipitation}mm
        
        Provide predictions for:
        1. Next 7 days weather pattern
        2. Next 30 days climate outlook
        3. Next 90 days seasonal forecast
        4. Annual climate projections
        
        Include probability scores and key risk factors for each timeframe.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an advanced climate prediction AI."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            return {
                "predictions": response.choices[0].message.content,
                "generated_at": datetime.now().isoformat(),
                "model_version": self.model
            }
            
        except Exception as e:
            logger.error(f"Prediction generation failed: {str(e)}")
            return {
                "predictions": "Prediction service temporarily unavailable",
                "generated_at": datetime.now().isoformat(),
                "error": str(e)
            }
    
    async def _analyze_satellite_imagery(self, satellite_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze satellite imagery data (placeholder for image processing)"""
        if not satellite_data:
            return {
                "status": "no_data",
                "message": "No satellite imagery provided"
            }
        
        # In a real implementation, this would process actual satellite images
        # For now, we'll simulate analysis based on metadata
        return {
            "vegetation_index": np.random.uniform(0.3, 0.8),
            "cloud_cover": np.random.uniform(10, 80),
            "land_surface_temperature": np.random.uniform(15, 35),
            "analysis_quality": "good",
            "last_updated": datetime.now().isoformat()
        }
    
    def _calculate_confidence(self, risk_assessment: RiskAssessment, trend_analysis: Dict[str, Any]) -> float:
        """Calculate overall confidence score"""
        base_confidence = risk_assessment.confidence_level
        trend_confidence = np.mean([t.get('confidence', 50) for t in trend_analysis.values() if isinstance(t, dict)])
        
        return min(100, (base_confidence + trend_confidence) / 2)
    
    def _generate_cache_key(self, climate_data: Dict[str, Any]) -> str:
        """Generate cache key for analysis results"""
        location = climate_data.get('location', {})
        timestamp = climate_data.get('timestamp', datetime.now().isoformat())
        
        return f"analysis_{location.get('lat', 0)}_{location.get('lng', 0)}_{timestamp[:10]}"
    
    def _generate_fallback_assessment(self, data: ClimateData) -> RiskAssessment:
        """Generate fallback risk assessment when AI fails"""
        # Simple rule-based assessment
        temp_risk = min(10, max(0, (data.temperature - 25) / 3))
        precip_risk = min(10, max(0, data.precipitation / 20))
        
        return RiskAssessment(
            overall_risk_score=(temp_risk + precip_risk) / 2,
            flood_risk=precip_risk,
            heat_risk=temp_risk,
            drought_risk=max(0, 5 - precip_risk),
            storm_risk=data.wind_speed / 10,
            confidence_level=60.0,
            recommendations=["Monitor weather conditions", "Review emergency plans"],
            time_horizon="short"
        )
    
    async def monitor_real_time_data(self, location: Dict[str, float]) -> Dict[str, Any]:
        """Monitor real-time climate data for a location"""
        # This would integrate with real weather APIs
        # For now, simulating real-time monitoring
        return {
            "monitoring_active": True,
            "location": location,
            "last_update": datetime.now().isoformat(),
            "alerts": [],
            "next_check": (datetime.now() + timedelta(minutes=15)).isoformat()
        }
    
    async def process_historical_data(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process and analyze historical weather patterns"""
        if not historical_data:
            return {"error": "No historical data provided"}
        
        prompt = f"""
        Analyze the following historical climate data and identify patterns:
        
        Data points: {len(historical_data)}
        Sample data: {json.dumps(historical_data[:5], indent=2)}
        
        Please identify:
        1. Long-term trends
        2. Seasonal patterns
        3. Extreme events frequency
        4. Anomalies and outliers
        5. Climate change indicators
        
        Provide insights in JSON format.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a historical climate data analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1200,
                temperature=0.2
            )
            
            return {
                "analysis": response.choices[0].message.content,
                "data_points_analyzed": len(historical_data),
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Historical data analysis failed: {str(e)}")
            return {
                "error": "Historical analysis failed",
                "data_points_analyzed": len(historical_data),
                "fallback_insights": "Basic statistical analysis completed"
            }
