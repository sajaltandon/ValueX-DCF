"""
Advanced risk analysis and scenario modeling for equity valuation.
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional
from scipy import stats
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

class RiskAnalyzer:
    """Advanced risk analysis and scenario modeling."""
    
    def __init__(self, company_data: Dict):
        """Initialize with company data."""
        self.data = company_data
        self.ticker = company_data.get('ticker', 'Unknown')
    
    def monte_carlo_simulation(self, base_fcf: float, growth_params: Dict, 
                             wacc_params: Dict, terminal_params: Dict, 
                             simulations: int = 10000) -> Dict:
        """
        Monte Carlo simulation for DCF valuation with parameter uncertainty.
        
        Args:
            base_fcf: Base Free Cash Flow
            growth_params: {'mean': float, 'std': float} for growth rate
            wacc_params: {'mean': float, 'std': float} for WACC
            terminal_params: {'mean': float, 'std': float} for terminal growth
            simulations: Number of simulation runs
        """
        try:
            from models.dcf_model import calculate_dcf, project_fcf
            
            results = []
            
            for _ in range(simulations):
                # Sample parameters from normal distributions
                growth = np.random.normal(growth_params['mean'], growth_params['std'])
                wacc = np.random.normal(wacc_params['mean'], wacc_params['std'])
                terminal = np.random.normal(terminal_params['mean'], terminal_params['std'])
                
                # Ensure logical constraints
                growth = max(-0.5, min(1.0, growth))  # -50% to 100%
                wacc = max(0.01, min(0.5, wacc))      # 1% to 50%
                terminal = max(-0.1, min(0.15, terminal))  # -10% to 15%
                
                # Ensure WACC > terminal growth
                if wacc <= terminal:
                    terminal = wacc - 0.01
                
                try:
                    fcf_proj = project_fcf(base_fcf, growth, 5)
                    dcf_result = calculate_dcf(fcf_proj, wacc, terminal, self.data['shares_outstanding'])
                    results.append({
                        'intrinsic_value': dcf_result['intrinsic_value'],
                        'growth': growth,
                        'wacc': wacc,
                        'terminal': terminal
                    })
                except:
                    continue  # Skip invalid combinations
            
            if not results:
                return {'error': 'No valid simulation results'}
            
            # Analyze results
            values = [r['intrinsic_value'] for r in results]
            
            return {
                'simulation_count': len(results),
                'mean_value': np.mean(values),
                'median_value': np.median(values),
                'std_dev': np.std(values),
                'min_value': np.min(values),
                'max_value': np.max(values),
                'percentiles': {
                    '5th': np.percentile(values, 5),
                    '25th': np.percentile(values, 25),
                    '75th': np.percentile(values, 75),
                    '95th': np.percentile(values, 95)
                },
                'var_95': np.percentile(values, 5),  # Value at Risk (95% confidence)
                'probability_positive': sum(1 for v in values if v > 0) / len(values),
                'current_price': self.data.get('current_price', 0),
                'detailed_results': results[:1000]  # Store first 1000 for analysis
            }
            
        except Exception as e:
            logger.error(f"Monte Carlo simulation error: {e}")
            return {'error': str(e)}
    
    def scenario_analysis(self, base_params: Dict) -> Dict:
        """Perform scenario analysis (bear, base, bull cases)."""
        try:
            from models.dcf_model import calculate_dcf, project_fcf
            
            scenarios = {
                'bear': {
                    'growth': base_params['growth'] - 0.05,  # 5% lower growth
                    'wacc': base_params['wacc'] + 0.02,      # 2% higher WACC
                    'terminal': base_params['terminal'] - 0.01,  # 1% lower terminal
                    'description': 'Conservative/pessimistic scenario'
                },
                'base': {
                    'growth': base_params['growth'],
                    'wacc': base_params['wacc'],
                    'terminal': base_params['terminal'],
                    'description': 'Most likely scenario'
                },
                'bull': {
                    'growth': base_params['growth'] + 0.05,  # 5% higher growth
                    'wacc': base_params['wacc'] - 0.01,      # 1% lower WACC
                    'terminal': base_params['terminal'] + 0.01,  # 1% higher terminal
                    'description': 'Optimistic scenario'
                }
            }
            
            results = {}
            
            for scenario_name, params in scenarios.items():
                try:
                    # Ensure valid parameters
                    growth = max(-0.5, min(1.0, params['growth']))
                    wacc = max(0.01, min(0.5, params['wacc']))
                    terminal = max(-0.1, min(0.15, params['terminal']))
                    
                    if wacc <= terminal:
                        terminal = wacc - 0.01
                    
                    fcf_proj = project_fcf(self.data['fcf'], growth, 5)
                    dcf_result = calculate_dcf(fcf_proj, wacc, terminal, self.data['shares_outstanding'])
                    
                    results[scenario_name] = {
                        'intrinsic_value': dcf_result['intrinsic_value'],
                        'enterprise_value': dcf_result['enterprise_value'],
                        'parameters': {
                            'growth': growth,
                            'wacc': wacc,
                            'terminal': terminal
                        },
                        'description': params['description'],
                        'projected_fcf': fcf_proj
                    }
                    
                except Exception as e:
                    results[scenario_name] = {'error': str(e)}
            
            # Calculate scenario statistics
            valid_values = [r['intrinsic_value'] for r in results.values() 
                           if 'intrinsic_value' in r]
            
            if valid_values:
                current_price = self.data.get('current_price', 0)
                
                summary = {
                    'scenarios': results,
                    'value_range': {
                        'min': min(valid_values),
                        'max': max(valid_values),
                        'spread': max(valid_values) - min(valid_values)
                    },
                    'current_price': current_price,
                    'upside_downside': {
                        'bull_upside': ((results.get('bull', {}).get('intrinsic_value', 0) - current_price) / current_price * 100) if current_price > 0 else 0,
                        'bear_downside': ((results.get('bear', {}).get('intrinsic_value', 0) - current_price) / current_price * 100) if current_price > 0 else 0
                    }
                }
                
                return summary
            
            return {'error': 'No valid scenario results'}
            
        except Exception as e:
            logger.error(f"Scenario analysis error: {e}")
            return {'error': str(e)}
    
    def sensitivity_analysis_detailed(self, base_params: Dict, 
                                    param_ranges: Dict = None) -> Dict:
        """Detailed sensitivity analysis for multiple parameters."""
        try:
            from models.dcf_model import calculate_dcf, project_fcf
            
            if param_ranges is None:
                param_ranges = {
                    'growth': np.linspace(base_params['growth'] - 0.05, 
                                        base_params['growth'] + 0.05, 11),
                    'wacc': np.linspace(base_params['wacc'] - 0.02, 
                                      base_params['wacc'] + 0.02, 11),
                    'terminal': np.linspace(base_params['terminal'] - 0.02, 
                                          base_params['terminal'] + 0.02, 11)
                }
            
            results = {}
            
            # Single parameter sensitivity
            for param_name, param_values in param_ranges.items():
                param_results = []
                
                for value in param_values:
                    test_params = base_params.copy()
                    test_params[param_name] = value
                    
                    try:
                        # Ensure valid parameters
                        growth = max(-0.5, min(1.0, test_params['growth']))
                        wacc = max(0.01, min(0.5, test_params['wacc']))
                        terminal = max(-0.1, min(0.15, test_params['terminal']))
                        
                        if wacc <= terminal:
                            continue  # Skip invalid combinations
                        
                        fcf_proj = project_fcf(self.data['fcf'], growth, 5)
                        dcf_result = calculate_dcf(fcf_proj, wacc, terminal, 
                                                 self.data['shares_outstanding'])
                        
                        param_results.append({
                            'parameter_value': value,
                            'intrinsic_value': dcf_result['intrinsic_value']
                        })
                        
                    except:
                        continue
                
                if param_results:
                    # Calculate sensitivity metrics
                    values = [r['intrinsic_value'] for r in param_results]
                    param_values_used = [r['parameter_value'] for r in param_results]
                    
                    # Linear regression to find sensitivity
                    if len(values) > 1:
                        slope, intercept, r_value, p_value, std_err = stats.linregress(
                            param_values_used, values)
                        
                        results[param_name] = {
                            'results': param_results,
                            'sensitivity': slope,  # Change in value per unit change in parameter
                            'correlation': r_value,
                            'base_value': base_params[param_name],
                            'value_range': {'min': min(values), 'max': max(values)},
                            'elasticity': self._calculate_elasticity(param_values_used, values)
                        }
                    else:
                        results[param_name] = {'results': param_results, 'error': 'Insufficient data'}
            
            return results
            
        except Exception as e:
            logger.error(f"Detailed sensitivity analysis error: {e}")
            return {'error': str(e)}
    
    def stress_testing(self, base_params: Dict) -> Dict:
        """Perform stress testing under extreme scenarios."""
        try:
            from models.dcf_model import calculate_dcf, project_fcf
            
            stress_scenarios = {
                'recession': {
                    'growth': -0.20,  # -20% FCF decline
                    'wacc': base_params['wacc'] + 0.05,  # +5% WACC
                    'terminal': 0.01,  # 1% terminal growth
                    'description': 'Economic recession scenario'
                },
                'high_inflation': {
                    'growth': base_params['growth'] - 0.10,  # Reduced growth
                    'wacc': base_params['wacc'] + 0.08,      # Much higher WACC
                    'terminal': base_params['terminal'] + 0.02,  # Higher terminal
                    'description': 'High inflation environment'
                },
                'market_crash': {
                    'growth': -0.30,  # -30% FCF decline
                    'wacc': base_params['wacc'] + 0.10,  # +10% WACC
                    'terminal': -0.05,  # -5% terminal (decline)
                    'description': 'Market crash scenario'
                },
                'industry_disruption': {
                    'growth': -0.15,  # Industry disruption
                    'wacc': base_params['wacc'] + 0.03,
                    'terminal': 0.005,  # Very low terminal growth
                    'description': 'Industry disruption scenario'
                }
            }
            
            results = {}
            current_price = self.data.get('current_price', 0)
            
            for scenario_name, params in stress_scenarios.items():
                try:
                    # Ensure parameters are within bounds
                    growth = max(-0.5, min(1.0, params['growth']))
                    wacc = max(0.01, min(0.5, params['wacc']))
                    terminal = max(-0.1, min(0.15, params['terminal']))
                    
                    if wacc <= terminal:
                        terminal = wacc - 0.01
                    
                    fcf_proj = project_fcf(self.data['fcf'], growth, 5)
                    dcf_result = calculate_dcf(fcf_proj, wacc, terminal, 
                                             self.data['shares_outstanding'])
                    
                    # Calculate stress impact
                    base_fcf_proj = project_fcf(self.data['fcf'], base_params['growth'], 5)
                    base_dcf = calculate_dcf(base_fcf_proj, base_params['wacc'], 
                                           base_params['terminal'], self.data['shares_outstanding'])
                    
                    impact = ((dcf_result['intrinsic_value'] - base_dcf['intrinsic_value']) / 
                             base_dcf['intrinsic_value'] * 100) if base_dcf['intrinsic_value'] > 0 else 0
                    
                    results[scenario_name] = {
                        'intrinsic_value': dcf_result['intrinsic_value'],
                        'parameters': {'growth': growth, 'wacc': wacc, 'terminal': terminal},
                        'description': params['description'],
                        'impact_vs_base': impact,
                        'downside_from_current': ((dcf_result['intrinsic_value'] - current_price) / 
                                                current_price * 100) if current_price > 0 else 0
                    }
                    
                except Exception as e:
                    results[scenario_name] = {'error': str(e)}
            
            # Summary metrics
            valid_values = [r['intrinsic_value'] for r in results.values() 
                           if 'intrinsic_value' in r]
            
            if valid_values:
                summary = {
                    'stress_scenarios': results,
                    'worst_case_value': min(valid_values),
                    'maximum_downside': min([r.get('downside_from_current', 0) 
                                           for r in results.values() 
                                           if 'downside_from_current' in r]),
                    'stress_resilience': self._assess_stress_resilience(results, current_price)
                }
                
                return summary
            
            return {'error': 'No valid stress test results'}
            
        except Exception as e:
            logger.error(f"Stress testing error: {e}")
            return {'error': str(e)}
    
    def _calculate_elasticity(self, x_values: List[float], y_values: List[float]) -> float:
        """Calculate elasticity (percentage change in value for 1% change in parameter)."""
        try:
            if len(x_values) < 2 or len(y_values) < 2:
                return 0
            
            # Use midpoint method for elasticity
            x_mid = np.mean(x_values)
            y_mid = np.mean(y_values)
            
            # Linear regression slope
            slope, _, _, _, _ = stats.linregress(x_values, y_values)
            
            # Elasticity = (slope * x_mid) / y_mid
            elasticity = (slope * x_mid) / y_mid if y_mid != 0 else 0
            
            return elasticity
            
        except:
            return 0
    
    def _assess_stress_resilience(self, stress_results: Dict, current_price: float) -> str:
        """Assess how resilient the valuation is to stress scenarios."""
        try:
            downsides = [r.get('downside_from_current', 0) 
                        for r in stress_results.values() 
                        if 'downside_from_current' in r]
            
            if not downsides:
                return "Unknown"
            
            max_downside = min(downsides)  # Most negative value
            
            if max_downside > -20:
                return "High Resilience"
            elif max_downside > -40:
                return "Medium Resilience"
            else:
                return "Low Resilience"
                
        except:
            return "Unknown"
    
    def risk_adjusted_valuation(self, base_valuation: float, risk_factors: List[str]) -> Dict:
        """Apply risk adjustments to base valuation."""
        try:
            risk_discount = 0.0
            
            # Risk factor adjustments
            risk_adjustments = {
                'High debt levels': 0.10,
                'Negative free cash flow': 0.15,
                'High price volatility': 0.08,
                'High market sensitivity': 0.05,
                'Industry cyclicality': 0.07,
                'Regulatory risk': 0.12,
                'Currency risk': 0.06,
                'Liquidity risk': 0.09
            }
            
            applied_adjustments = {}
            
            for factor in risk_factors:
                if factor in risk_adjustments:
                    risk_discount += risk_adjustments[factor]
                    applied_adjustments[factor] = risk_adjustments[factor]
            
            # Cap total risk adjustment at 40%
            risk_discount = min(risk_discount, 0.40)
            
            risk_adjusted_value = base_valuation * (1 - risk_discount)
            
            return {
                'base_valuation': base_valuation,
                'risk_adjusted_valuation': risk_adjusted_value,
                'total_risk_discount': risk_discount,
                'applied_adjustments': applied_adjustments,
                'risk_factors': risk_factors
            }
            
        except Exception as e:
            logger.error(f"Risk adjusted valuation error: {e}")
            return {'error': str(e)}
