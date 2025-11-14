"""
Main Entry Point for ADE Data Lake Pipeline
Orchestrates the complete Bronze -> Silver -> Gold transformation
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.logger import get_logger
from src.transformations.bronze_to_silver import BronzeToSilverTransform
from src.transformations.silver_to_gold import SilverToGoldTransform

# Setup logging
log_file = os.path.join("logs", f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logger = get_logger(__name__, log_file)


def main():
    """Execute the full data pipeline"""
    
    try:
        logger.info("=" * 80)
        logger.info("Starting ADE Data Lake Pipeline Execution")
        logger.info("=" * 80)
        
        # Define paths
        bronze_input = "data/bronze/customers_raw.csv"
        silver_output = "data/silver"
        gold_input = os.path.join(silver_output, "customers_silver.parquet")
        gold_output = "data/gold"
        
        # STEP 1: Bronze to Silver Transformation
        logger.info("\n[STEP 1] Executing Bronze -> Silver Transformation")
        logger.info("-" * 80)
        
        b2s_transformer = BronzeToSilverTransform(
            input_path=bronze_input,
            output_dir=silver_output
        )
        silver_df = b2s_transformer.transform(formats=['csv', 'parquet'])
        
        logger.info("Bronze to Silver transformation completed")
        logger.info(f"Silver data sample:\n{silver_df.head()}\n")
        
        # STEP 2: Silver to Gold Transformation
        logger.info("[STEP 2] Executing Silver -> Gold Transformation")
        logger.info("-" * 80)
        
        s2g_transformer = SilverToGoldTransform(
            input_path=gold_input,
            output_dir=gold_output
        )
        gold_df = s2g_transformer.transform(formats=['csv', 'parquet'])
        
        logger.info("Silver to Gold transformation completed")
        logger.info(f"Gold data sample:\n{gold_df}\n")
        
        # Summary
        logger.info("=" * 80)
        logger.info("PIPELINE EXECUTION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"✓ Bronze Records Loaded: {len(b2s_transformer.df) + sum(b2s_transformer.df['name'].isna())}")
        logger.info(f"✓ Silver Records Created: {len(silver_df)}")
        logger.info(f"✓ Gold Aggregations Created: {len(gold_df)}")
        logger.info(f"✓ Output Formats: CSV, Parquet")
        logger.info(f"✓ Log File: {log_file}")
        logger.info("=" * 80)
        logger.info("Pipeline execution completed successfully!")
        logger.info("=" * 80)
        
        return 0
    
    except Exception as e:
        logger.error("=" * 80)
        logger.error("PIPELINE EXECUTION FAILED")
        logger.error("=" * 80)
        logger.error(f"Error: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
