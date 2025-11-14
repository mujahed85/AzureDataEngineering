"""
Bronze to Silver Transformation Layer
Handles data cleaning and standardization
"""

import pandas as pd
import os
from typing import Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BronzeToSilverTransform:
    """Transform raw bronze data to cleaned silver layer"""
    
    def __init__(self, input_path: str, output_dir: str):
        """
        Initialize the transformation.
        
        Args:
            input_path: Path to bronze CSV file
            output_dir: Output directory for silver files
        """
        self.input_path = input_path
        self.output_dir = output_dir
        self.df = None
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def load_bronze_data(self) -> pd.DataFrame:
        """Load raw bronze data"""
        try:
            logger.info(f"Loading bronze data from {self.input_path}")
            self.df = pd.read_csv(self.input_path)
            logger.info(f"Loaded {len(self.df)} rows from bronze layer")
            return self.df
        except Exception as e:
            logger.error(f"Error loading bronze data: {str(e)}")
            raise
    
    def clean_data(self) -> pd.DataFrame:
        """
        Apply cleaning transformations:
        - Remove missing names
        - Standardize name format
        - Filter by business rules
        - Remove duplicates
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_bronze_data() first")
        
        logger.info("Starting data cleaning...")
        initial_rows = len(self.df)
        
        # 1. Remove rows with missing names
        logger.info("Removing rows with missing names")
        self.df = self.df.dropna(subset=["name"])
        logger.info(f"Removed {initial_rows - len(self.df)} rows with missing names")
        
        # 2. Standardize name format (Title Case)
        logger.info("Standardizing name format to Title Case")
        self.df["name"] = self.df["name"].str.title()
        
        # 3. Apply business rule: salary >= 50000
        logger.info("Filtering by salary >= 50000")
        before_filter = len(self.df)
        self.df = self.df[self.df["salary"] >= 50000]
        logger.info(f"Filtered out {before_filter - len(self.df)} rows based on salary rule")
        
        # 4. Remove duplicates
        logger.info("Removing duplicate rows")
        before_dedup = len(self.df)
        self.df = self.df.drop_duplicates()
        logger.info(f"Removed {before_dedup - len(self.df)} duplicate rows")
        
        # 5. Reset index
        self.df = self.df.reset_index(drop=True)
        
        logger.info(f"Cleaning complete. Final row count: {len(self.df)}")
        return self.df
    
    def save_silver_data(self, formats: list = None) -> None:
        """
        Save cleaned data in multiple formats.
        
        Args:
            formats: List of formats to save ('csv', 'parquet'). Default: ['csv', 'parquet']
        """
        if self.df is None:
            raise ValueError("No data to save. Run clean_data() first")
        
        if formats is None:
            formats = ['csv', 'parquet']
        
        try:
            if 'csv' in formats:
                csv_path = os.path.join(self.output_dir, 'customers_silver.csv')
                self.df.to_csv(csv_path, index=False)
                logger.info(f"Saved silver CSV to {csv_path}")
            
            if 'parquet' in formats:
                parquet_path = os.path.join(self.output_dir, 'customers_silver.parquet')
                self.df.to_parquet(parquet_path, engine="pyarrow", index=False)
                logger.info(f"Saved silver Parquet to {parquet_path}")
        
        except Exception as e:
            logger.error(f"Error saving silver data: {str(e)}")
            raise
    
    def transform(self, formats: list = None) -> pd.DataFrame:
        """
        Execute full transformation pipeline.
        
        Args:
            formats: Output formats
            
        Returns:
            Transformed DataFrame
        """
        self.load_bronze_data()
        self.clean_data()
        self.save_silver_data(formats)
        
        logger.info("Bronze to Silver transformation completed successfully")
        return self.df
