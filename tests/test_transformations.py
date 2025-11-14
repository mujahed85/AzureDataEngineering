"""Unit tests for transformation modules"""

import pytest
import pandas as pd
import tempfile
import os
from src.transformations.bronze_to_silver import BronzeToSilverTransform
from src.transformations.silver_to_gold import SilverToGoldTransform


@pytest.fixture
def sample_bronze_data():
    """Create sample bronze data for testing"""
    data = {
        'id': [1, 2, 3, 4, 5],
        'name': ['Rohit', 'Neha', 'Amit', None, 'Meera'],
        'city': ['Mumbai', 'Pune', 'Delhi', 'Bangalore', 'Mumbai'],
        'age': [28, 31, 24, 29, 30],
        'salary': [50000, 62000, 45000, 55000, 70000]
    }
    return pd.DataFrame(data)


@pytest.fixture
def temp_dir():
    """Create temporary directory for test outputs"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestBronzeToSilverTransform:
    """Test cases for Bronze to Silver transformation"""
    
    def test_load_bronze_data(self, sample_bronze_data, temp_dir):
        """Test loading bronze data"""
        # Save sample data to temporary file
        input_file = os.path.join(temp_dir, 'input.csv')
        sample_bronze_data.to_csv(input_file, index=False)
        
        transformer = BronzeToSilverTransform(input_file, temp_dir)
        df = transformer.load_bronze_data()
        
        assert len(df) == 5
        assert list(df.columns) == ['id', 'name', 'city', 'age', 'salary']
    
    def test_clean_removes_null_names(self, sample_bronze_data, temp_dir):
        """Test that null names are removed"""
        input_file = os.path.join(temp_dir, 'input.csv')
        sample_bronze_data.to_csv(input_file, index=False)
        
        transformer = BronzeToSilverTransform(input_file, temp_dir)
        transformer.load_bronze_data()
        cleaned_df = transformer.clean_data()
        
        assert len(cleaned_df) == 3  # One row with null name should be removed
        assert cleaned_df['name'].isna().sum() == 0
    
    def test_clean_filters_salary(self, sample_bronze_data, temp_dir):
        """Test that salary filtering is applied"""
        input_file = os.path.join(temp_dir, 'input.csv')
        sample_bronze_data.to_csv(input_file, index=False)
        
        transformer = BronzeToSilverTransform(input_file, temp_dir)
        transformer.load_bronze_data()
        cleaned_df = transformer.clean_data()
        
        # Salary < 50000 should be removed (Amit with 45000)
        assert all(cleaned_df['salary'] >= 50000)
    
    def test_save_silver_data(self, sample_bronze_data, temp_dir):
        """Test saving silver data in multiple formats"""
        input_file = os.path.join(temp_dir, 'input.csv')
        sample_bronze_data.to_csv(input_file, index=False)
        
        transformer = BronzeToSilverTransform(input_file, temp_dir)
        transformer.transform(formats=['csv', 'parquet'])
        
        # Check that files were created
        assert os.path.exists(os.path.join(temp_dir, 'customers_silver.csv'))
        assert os.path.exists(os.path.join(temp_dir, 'customers_silver.parquet'))


class TestSilverToGoldTransform:
    """Test cases for Silver to Gold transformation"""
    
    def test_load_silver_data(self, sample_bronze_data, temp_dir):
        """Test loading silver data"""
        # Create and save silver data
        silver_file = os.path.join(temp_dir, 'input.parquet')
        sample_bronze_data.to_parquet(silver_file, index=False)
        
        transformer = SilverToGoldTransform(silver_file, temp_dir)
        df = transformer.load_silver_data()
        
        assert len(df) == 5
    
    def test_create_aggregations(self, sample_bronze_data, temp_dir):
        """Test creating gold aggregations"""
        silver_file = os.path.join(temp_dir, 'input.parquet')
        sample_bronze_data.to_parquet(silver_file, index=False)
        
        transformer = SilverToGoldTransform(silver_file, temp_dir)
        transformer.load_silver_data()
        gold_df = transformer.create_aggregations()
        
        # Should have 3 cities
        assert len(gold_df) == 3
        # Should have aggregated columns
        assert 'avg_salary' in gold_df.columns
        assert 'max_salary' in gold_df.columns
        assert 'customer_count' in gold_df.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
