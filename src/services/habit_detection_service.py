"""
Habit Detection Service for ClimateCoach
Utilizes time-series analysis and clustering for habit detection
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any
from tslearn.clustering import TimeSeriesKMeans
from prophet import Prophet
import logging

logger = logging.getLogger(__name__)

class HabitDetectionService:
    """
    Service for analyzing and detecting user habits over time
    """

    def __init__(self, n_clusters: int = 3):
        """
        Initialize the habit detection service
        
        Args:
            n_clusters: Number of clusters for k-means
        """
        self.n_clusters = n_clusters
        logger.info("Habit Detection Service initialized")

    def detect_habits(self, time_series_data: np.ndarray) -> Dict[str, Any]:
        """
        Detect habits by clustering time-series data
        
        Args:
            time_series_data: Array of shape (n_samples, n_timepoints)

        Returns:
            Clustering results and labels
        """
        try:
            # K-Means Clustering with Euclidean distance
            km = TimeSeriesKMeans(
                n_clusters=self.n_clusters,
                metric="euclidean",
                random_state=42
            )
            labels = km.fit_predict(time_series_data)
            
            logger.info("Habit clustering completed")
            return {
                'labels': labels,
                'centers': km.cluster_centers_,
                'inertia': km.inertia_
            }
        except Exception as e:
            logger.error(f"Error detecting habits: {e}")
            return {}
        
    def forecast_habits(self, df: pd.DataFrame, periods: int = 30) -> pd.DataFrame:
        """
        Forecast habits using Prophet

        Args:
            df: DataFrame with columns 'ds' and 'y'
            periods: Forecast period

        Returns:
            DataFrame with forecast results
        """
        try:
            model = Prophet()
            model.fit(df)
            future = model.make_future_dataframe(periods=periods)
            forecast = model.predict(future)
            
            logger.info("Habit forecasting completed")
            return forecast
        except Exception as e:
            logger.error(f"Error forecasting habits: {e}")
            return pd.DataFrame()

if __name__ == "__main__":
    # Example usage
    habit_detection_service = HabitDetectionService(n_clusters=3)
    
    # Synthetic example data
    time_series_data = np.random.rand(10, 24)  # 10 days of hourly data
    
    # Detect habits
    clustering_results = habit_detection_service.detect_habits(time_series_data)
    print("Clustering Results:", clustering_results)
    
    # Create example DataFrame for forecasting
    df = pd.DataFrame({
        'ds': pd.date_range(start='2022-01-01', periods=100),
        'y': np.random.rand(100)
    })
    
    # Forecast habits
    forecast_results = habit_detection_service.forecast_habits(df)
    print("Forecast Results:", forecast_results.head())
