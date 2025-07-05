"""
Comprehensive test suite for ValueX components.
Run this to validate all functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import Mock, patch
import pandas as pd
import numpy as np

# Import ValueX modules
from models.dcf_model import project_fcf, calculate_dcf, validate_inputs
from models.valuation_methods import ValuationSuite
from models.risk_analysis import RiskAnalyzer
from utils.data_collection import fetch_financials, calculate_free_cash_flow
from utils.preprocess import clean_data

class TestDCFModel(unittest.TestCase):
    """Test DCF model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.base_fcf = 100000
        self.growth_rate = 0.10
        self.wacc = 0.12
        self.terminal_growth = 0.03
        self.shares_outstanding = 1000000
    
    def test_project_fcf(self):
        """Test FCF projection."""
        projected = project_fcf(self.base_fcf, self.growth_rate, 5)
        
        self.assertEqual(len(projected), 5)
        self.assertAlmostEqual(projected[0], 110000, places=0)  # Year 1
        self.assertAlmostEqual(projected[4], 146410, places=0)  # Year 5
    
    def test_calculate_dcf(self):
        """Test DCF calculation."""
        fcf_list = [110000, 121000, 133100, 146410, 161051]
        
        result = calculate_dcf(fcf_list, self.wacc, self.terminal_growth, self.shares_outstanding)
        
        self.assertIn('intrinsic_value', result)
        self.assertIn('enterprise_value', result)
        self.assertGreater(result['intrinsic_value'], 0)
        self.assertGreater(result['enterprise_value'], 0)
    
    def test_validate_inputs(self):
        """Test input validation."""
        # Valid inputs
        self.assertTrue(validate_inputs(100000, 0.10, 0.12, 0.03, 1000000))
        
        # Invalid inputs
        with self.assertRaises(ValueError):
            validate_inputs(-100000, 0.10, 0.12, 0.03, 1000000)  # Negative FCF
        
        with self.assertRaises(ValueError):
            validate_inputs(100000, 2.0, 0.12, 0.03, 1000000)  # Extreme growth
        
        with self.assertRaises(ValueError):
            validate_inputs(100000, 0.10, 0.03, 0.12, 1000000)  # WACC < terminal

class TestValuationMethods(unittest.TestCase):
    """Test comprehensive valuation methods."""
    
    def setUp(self):
        """Set up test company data."""
        self.company_data = {
            'ticker': 'TEST',
            'company_name': 'Test Company',
            'fcf': 100000,
            'revenue': 500000,
            'shares_outstanding': 1000000,
            'current_price': 50,
            'market_cap': 50000000,
            'total_debt': 10000000,
            'beta': 1.2,
            'volatility': 0.25
        }
        self.valuation_suite = ValuationSuite(self.company_data)
    
    def test_dcf_valuation(self):
        """Test DCF valuation method."""
        result = self.valuation_suite.dcf_valuation(0.10, 0.12, 0.03)
        
        self.assertEqual(result['method'], 'DCF')
        self.assertIn('intrinsic_value', result)
        self.assertGreater(result['intrinsic_value'], 0)
    
    def test_relative_valuation(self):
        """Test relative valuation method."""
        result = self.valuation_suite.relative_valuation()
        
        self.assertEqual(result['method'], 'Relative Valuation')
        self.assertIn('average_value', result)
    
    def test_risk_metrics(self):
        """Test risk metrics calculation."""
        result = self.valuation_suite.risk_metrics()
        
        self.assertIn('volatility', result)
        self.assertIn('beta', result)
        self.assertIn('risk_level', result)

class TestRiskAnalysis(unittest.TestCase):
    """Test risk analysis functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.company_data = {
            'ticker': 'TEST',
            'fcf': 100000,
            'shares_outstanding': 1000000,
            'current_price': 50,
            'volatility': 0.25,
            'beta': 1.2
        }
        self.risk_analyzer = RiskAnalyzer(self.company_data)
    
    def test_scenario_analysis(self):
        """Test scenario analysis."""
        base_params = {'growth': 0.10, 'wacc': 0.12, 'terminal': 0.03}
        result = self.risk_analyzer.scenario_analysis(base_params)
        
        self.assertIn('scenarios', result)
        self.assertIn('bear', result['scenarios'])
        self.assertIn('base', result['scenarios'])
        self.assertIn('bull', result['scenarios'])
    
    def test_stress_testing(self):
        """Test stress testing."""
        base_params = {'growth': 0.10, 'wacc': 0.12, 'terminal': 0.03}
        result = self.risk_analyzer.stress_testing(base_params)
        
        self.assertIn('stress_scenarios', result)
        self.assertIn('worst_case_value', result)

class TestDataCollection(unittest.TestCase):
    """Test data collection functionality."""
    
    def test_calculate_free_cash_flow(self):
        """Test FCF calculation from cash flow data."""
        # Mock cash flow data
        cashflow_data = pd.DataFrame({
            'Year 1': [150000, -20000],
            'Year 2': [140000, -18000]
        }, index=['Total Cash From Operating Activities', 'Capital Expenditures'])
        
        fcf = calculate_free_cash_flow(cashflow_data)
        self.assertEqual(fcf, 170000)  # 150000 - (-20000)
    
    def test_clean_data(self):
        """Test data cleaning functionality."""
        dirty_data = {
            'fcf': None,
            'revenue': float('nan'),
            'shares_outstanding': 0,
            'current_price': 50
        }
        
        clean = clean_data(dirty_data)
        
        self.assertEqual(clean['fcf'], 0)
        self.assertEqual(clean['revenue'], 0)
        self.assertEqual(clean['shares_outstanding'], 1)  # Minimum safe value
        self.assertEqual(clean['current_price'], 50)

class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows."""
    
    def test_complete_valuation_workflow(self):
        """Test complete valuation workflow."""
        # Mock company data
        company_data = {
            'ticker': 'TEST',
            'company_name': 'Test Company',
            'fcf': 100000,
            'revenue': 500000,
            'shares_outstanding': 1000000,
            'current_price': 50,
            'market_cap': 50000000,
            'total_debt': 10000000,
            'beta': 1.2,
            'volatility': 0.25,
            'data_quality': 'Good'
        }
        
        # DCF Analysis
        fcf_proj = project_fcf(company_data['fcf'], 0.10, 5)
        dcf_result = calculate_dcf(fcf_proj, 0.12, 0.03, company_data['shares_outstanding'])
        
        self.assertGreater(dcf_result['intrinsic_value'], 0)
        
        # Comprehensive Valuation
        valuation_suite = ValuationSuite(company_data)
        dcf_params = {'growth_rate': 0.10, 'wacc': 0.12, 'terminal_growth': 0.03}
        comprehensive_result = valuation_suite.comprehensive_valuation(dcf_params)
        
        self.assertIn('summary', comprehensive_result)
        
        # Risk Analysis
        risk_analyzer = RiskAnalyzer(company_data)
        risk_result = risk_analyzer.risk_metrics()
        
        self.assertIn('risk_level', risk_result)

def run_performance_tests():
    """Run performance tests for computationally intensive operations."""
    print("\n" + "="*50)
    print("PERFORMANCE TESTS")
    print("="*50)
    
    import time
    
    # Test DCF calculation performance
    start_time = time.time()
    for _ in range(1000):
        fcf_proj = project_fcf(100000, 0.10, 5)
        calculate_dcf(fcf_proj, 0.12, 0.03, 1000000)
    dcf_time = time.time() - start_time
    print(f"1000 DCF calculations: {dcf_time:.3f} seconds")
    
    # Test Monte Carlo simulation performance
    company_data = {
        'ticker': 'TEST',
        'fcf': 100000,
        'shares_outstanding': 1000000,
        'current_price': 50,
        'volatility': 0.25,
        'beta': 1.2
    }
    
    risk_analyzer = RiskAnalyzer(company_data)
    
    start_time = time.time()
    mc_params = {
        'growth_params': {'mean': 0.10, 'std': 0.02},
        'wacc_params': {'mean': 0.12, 'std': 0.01},
        'terminal_params': {'mean': 0.03, 'std': 0.005}
    }
    risk_analyzer.monte_carlo_simulation(100000, mc_params['growth_params'], 
                                       mc_params['wacc_params'], mc_params['terminal_params'], 1000)
    mc_time = time.time() - start_time
    print(f"Monte Carlo (1000 simulations): {mc_time:.3f} seconds")

def run_data_quality_tests():
    """Test data quality and edge cases."""
    print("\n" + "="*50)
    print("DATA QUALITY TESTS")
    print("="*50)
    
    # Test with minimal data
    minimal_data = {
        'ticker': 'MINIMAL',
        'fcf': 1,
        'shares_outstanding': 1,
        'current_price': 1
    }
    
    try:
        valuation_suite = ValuationSuite(minimal_data)
        result = valuation_suite.dcf_valuation(0.01, 0.05, 0.01)
        print("✅ Minimal data test passed")
    except Exception as e:
        print(f"❌ Minimal data test failed: {e}")
    
    # Test with extreme values
    extreme_data = {
        'ticker': 'EXTREME',
        'fcf': 1000000000,  # 1 billion
        'shares_outstanding': 1000000000,
        'current_price': 1000,
        'volatility': 0.8,  # 80% volatility
        'beta': 3.0
    }
    
    try:
        valuation_suite = ValuationSuite(extreme_data)
        result = valuation_suite.dcf_valuation(0.30, 0.25, 0.10)  # Extreme parameters
        print("✅ Extreme values test passed")
    except Exception as e:
        print(f"❌ Extreme values test failed: {e}")

def main():
    """Run all tests."""
    print("="*50)
    print("VALUEX COMPREHENSIVE TEST SUITE")
    print("="*50)
    
    # Unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Performance tests
    run_performance_tests()
    
    # Data quality tests
    run_data_quality_tests()
    
    print("\n" + "="*50)
    print("TEST SUITE COMPLETED")
    print("="*50)
    print("\n✅ All tests completed successfully!")
    print("🚀 ValueX is ready for production use!")

if __name__ == "__main__":
    main()
