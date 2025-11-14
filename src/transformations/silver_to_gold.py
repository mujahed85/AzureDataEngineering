"""
Silver to Gold Transformation Layer
Handles data aggregation and analytics preparation
"""

import pandas as pd
import os
from typing import Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SilverToGoldTransform:
    """Transform cleaned silver data to aggregated gold layer"""
    
    def __init__(self, input_path: str, output_dir: str):
        """
        Initialize the transformation.
        
        Args:
            input_path: Path to silver Parquet file
            output_dir: Output directory for gold files
        """
        self.input_path = input_path
        self.output_dir = output_dir
        self.df = None
        self.gold_df = None
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def load_silver_data(self) -> pd.DataFrame:
        """Load cleaned silver data"""
        try:
            logger.info(f"Loading silver data from {self.input_path}")
            
            # Detect file format
            if self.input_path.endswith('.parquet'):
                self.df = pd.read_parquet(self.input_path)
            elif self.input_path.endswith('.csv'):
                self.df = pd.read_csv(self.input_path)
            else:
                raise ValueError("Unsupported file format. Use .parquet or .csv")
            
            logger.info(f"Loaded {len(self.df)} rows from silver layer")
            return self.df
        except Exception as e:
            logger.error(f"Error loading silver data: {str(e)}")
            raise
    
    def create_aggregations(self) -> pd.DataFrame:
        """
        Create gold layer aggregations:
        - Average salary by city
        - Maximum salary by city
        - Customer count by city
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_silver_data() first")
        
        logger.info("Creating gold layer aggregations...")
        
        try:
            self.gold_df = self.df.groupby("city").agg(
                avg_salary=("salary", "mean"),
                max_salary=("salary", "max"),
                min_salary=("salary", "min"),
                customer_count=("id", "count")
            ).reset_index()
            
            # Round salary columns to 2 decimals
            self.gold_df["avg_salary"] = self.gold_df["avg_salary"].round(2)
            self.gold_df["max_salary"] = self.gold_df["max_salary"].round(2)
            self.gold_df["min_salary"] = self.gold_df["min_salary"].round(2)
            
            # Sort by average salary descending
            self.gold_df = self.gold_df.sort_values("avg_salary", ascending=False)
            
            logger.info(f"Created gold aggregations with {len(self.gold_df)} city records")
            return self.gold_df
        except Exception as e:
            logger.error(f"Error creating aggregations: {str(e)}")
            raise
    
    def save_gold_data(self, formats: list = None) -> None:
        """
        Save aggregated data in multiple formats.
        
        Args:
            formats: List of formats to save ('csv', 'parquet'). Default: ['csv', 'parquet']
        """
        if self.gold_df is None:
            raise ValueError("No aggregation data to save. Run create_aggregations() first")
        
        if formats is None:
            formats = ['csv', 'parquet']
        
        try:
            if 'csv' in formats:
                csv_path = os.path.join(self.output_dir, 'customers_gold.csv')
                self.gold_df.to_csv(csv_path, index=False)
                logger.info(f"Saved gold CSV to {csv_path}")
            
            if 'parquet' in formats:
                parquet_path = os.path.join(self.output_dir, 'customers_gold.parquet')
                self.gold_df.to_parquet(parquet_path, engine="pyarrow", index=False)
                logger.info(f"Saved gold Parquet to {parquet_path}")
        
        except Exception as e:
            logger.error(f"Error saving gold data: {str(e)}")
            raise
    
    def transform(self, formats: list = None) -> pd.DataFrame:
        """
        Execute full transformation pipeline.
        
        Args:
            formats: Output formats
            
        Returns:
            Aggregated DataFrame
        """
        self.load_silver_data()
        self.create_aggregations()
        self.save_gold_data(formats)
        
        logger.info("Silver to Gold transformation completed successfully")
        return self.gold_df
