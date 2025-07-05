"""
Comprehensive valuation methods module including DCF, relative valuation, and risk metrics.
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Optional, Tuple, Union
from models.dcf_model import calculate_dcf, project_fcf

logger = logging.getLogger(__name__)

class ValuationSuite:
    """Comprehensive valuation suite with multiple methodologies."""
    
    def __init__(self, company_data: Dict):
        """Initialize with company financial data."""
        self.data = company_data
        self.ticker = company_data.get('ticker', 'Unknown')
        
    def dcf_valuation(self, growth_rate: float, wacc: float, terminal_growth: float, years: int = 5) -> Dict:
        """Perform DCF valuation."""
        try:
            fcf_proj = project_fcf(self.data['fcf'], growth_rate, years)
            dcf_result = calculate_dcf(fcf_proj, wacc, terminal_growth, self.data['shares_outstanding'])
            
            return {
                'method': 'DCF',
                'intrinsic_value': dcf_result['intrinsic_value'],
                'enterprise_value': dcf_result['enterprise_value'],
                'projected_fcf': fcf_proj,
                'assumptions': {
                    'growth_rate': growth_rate,
                    'wacc': wacc,
                    'terminal_growth': terminal_growth,
                    'years': years
                }
            }
        except Exception as e:
            logger.error(f"DCF valuation error: {e}")
            return {'method': 'DCF', 'error': str(e)}
    
    def relative_valuation(self, sector_multiples: Optional[Dict] = None) -> Dict:
        """Perform relative valuation using P/E, EV/EBITDA, P/S ratios."""
        try:
            # Default sector multiples (in practice, fetch from market data)
            default_multiples = {
                'pe_ratio': 15.0,
                'ev_ebitda': 10.0,
                'price_sales': 2.0,
                'price_book': 1.5
            }
            
            multiples = sector_multiples or default_multiples
            
            # Calculate EBITDA estimate (simplified)
            ebitda = self.data.get('revenue', 0) * 0.15  # Assume 15% EBITDA margin
            
            # P/E valuation
            earnings = self.data.get('revenue', 0) * 0.10  # Assume 10% net margin
            eps = earnings / self.data['shares_outstanding'] if self.data['shares_outstanding'] > 0 else 0
            pe_value = eps * multiples['pe_ratio']
            
            # EV/EBITDA valuation
            enterprise_value = ebitda * multiples['ev_ebitda']
            ev_ebitda_value = (enterprise_value - self.data.get('total_debt', 0)) / self.data['shares_outstanding']
            
            # P/S valuation
            revenue_per_share = self.data.get('revenue', 0) / self.data['shares_outstanding']
            ps_value = revenue_per_share * multiples['price_sales']
            
            # Average of methods
            values = [v for v in [pe_value, ev_ebitda_value, ps_value] if v > 0]
            avg_value = np.mean(values) if values else 0
            
            return {
                'method': 'Relative Valuation',
                'pe_valuation': pe_value,
                'ev_ebitda_valuation': ev_ebitda_value,
                'price_sales_valuation': ps_value,
                'average_value': avg_value,
                'multiples_used': multiples,
                'metrics': {
                    'eps': eps,
                    'ebitda': ebitda,
                    'revenue_per_share': revenue_per_share
                }
            }
            
        except Exception as e:
            logger.error(f"Relative valuation error: {e}")
            return {'method': 'Relative Valuation', 'error': str(e)}
    
    def dividend_discount_model(self, dividend_growth: float = 0.03, required_return: float = 0.10) -> Dict:
        """Gordon Growth Model for dividend-paying stocks."""
        try:
            # Estimate dividend (simplified - would need actual dividend data)
            estimated_dividend = self.data.get('revenue', 0) * 0.03 / self.data['shares_outstanding']  # 3% payout
            
            if required_return <= dividend_growth:
                raise ValueError("Required return must be greater than dividend growth rate")
            
            ddm_value = estimated_dividend * (1 + dividend_growth) / (required_return - dividend_growth)
            
            return {
                'method': 'Dividend Discount Model',
                'intrinsic_value': ddm_value,
                'estimated_dividend': estimated_dividend,
                'assumptions': {
                    'dividend_growth': dividend_growth,
                    'required_return': required_return
                }
            }
            
        except Exception as e:
            logger.error(f"DDM valuation error: {e}")
            return {'method': 'Dividend Discount Model', 'error': str(e)}
    
    def asset_based_valuation(self) -> Dict:
        """Book value and liquidation value estimation."""
        try:
            # Simplified asset-based valuation
            book_value_per_share = self.data.get('market_cap', 0) / self.data['shares_outstanding']
            
            # Estimate liquidation value (typically 60-80% of book value)
            liquidation_value = book_value_per_share * 0.7
            
            return {
                'method': 'Asset-Based Valuation',
                'book_value_per_share': book_value_per_share,
                'liquidation_value': liquidation_value,
                'note': 'Simplified estimation - requires actual balance sheet analysis'
            }
            
        except Exception as e:
            logger.error(f"Asset-based valuation error: {e}")
            return {'method': 'Asset-Based Valuation', 'error': str(e)}
    
    def risk_metrics(self) -> Dict:
        """Calculate various risk metrics."""
        try:
            current_price = self.data.get('current_price', 0)
            volatility = self.data.get('volatility', 0.25)
            beta = self.data.get('beta', 1.0)
            
            # Value at Risk (simplified 95% confidence)
            var_95 = current_price * volatility * 1.645  # 95% confidence interval
            
            # Sharpe ratio estimation (would need actual returns)
            risk_free_rate = 0.05  # 5% assumption
            estimated_return = 0.10  # 10% assumption
            sharpe_ratio = (estimated_return - risk_free_rate) / volatility if volatility > 0 else 0
            
            # Risk categories
            risk_level = self._categorize_risk(volatility, beta)
            
            return {
                'volatility': volatility,
                'beta': beta,
                'var_95': var_95,
                'sharpe_ratio': sharpe_ratio,
                'risk_level': risk_level,
                'risk_factors': self._identify_risk_factors()
            }
            
        except Exception as e:
            logger.error(f"Risk metrics error: {e}")
            return {'error': str(e)}
    
    def comprehensive_valuation(self, dcf_params: Dict, sector_multiples: Optional[Dict] = None) -> Dict:
        """Run all valuation methods and provide summary."""
        try:
            results = {}
            
            # DCF Valuation
            dcf_result = self.dcf_valuation(**dcf_params)
            results['dcf'] = dcf_result
            
            # Relative Valuation
            rel_result = self.relative_valuation(sector_multiples)
            results['relative'] = rel_result
            
            # Dividend Discount Model
            ddm_result = self.dividend_discount_model()
            results['ddm'] = ddm_result
            
            # Asset-Based Valuation
            asset_result = self.asset_based_valuation()
            results['asset_based'] = asset_result
            
            # Risk Metrics
            risk_result = self.risk_metrics()
            results['risk_metrics'] = risk_result
            
            # Summary and recommendation
            summary = self._create_valuation_summary(results)
            results['summary'] = summary
            
            return results
            
        except Exception as e:
            logger.error(f"Comprehensive valuation error: {e}")
            return {'error': str(e)}
    
    def _categorize_risk(self, volatility: float, beta: float) -> str:
        """Categorize risk level based on volatility and beta."""
        if volatility > 0.4 or beta > 1.5:
            return "High Risk"
        elif volatility > 0.25 or beta > 1.2:
            return "Medium Risk"
        else:
            return "Low Risk"
    
    def _identify_risk_factors(self) -> List[str]:
        """Identify potential risk factors based on company data."""
        factors = []
        
        if self.data.get('total_debt', 0) > self.data.get('market_cap', 0):
            factors.append("High debt levels")
        
        if self.data.get('fcf', 0) <= 0:
            factors.append("Negative free cash flow")
        
        if self.data.get('volatility', 0) > 0.4:
            factors.append("High price volatility")
        
        if self.data.get('beta', 1.0) > 1.5:
            factors.append("High market sensitivity")
        
        return factors or ["No major risk factors identified"]
    
    def _create_valuation_summary(self, results: Dict) -> Dict:
        """Create a summary of all valuation methods."""
        try:
            valuations = []
            current_price = self.data.get('current_price', 0)
            
            # Collect valid valuations
            if 'dcf' in results and 'intrinsic_value' in results['dcf']:
                valuations.append(('DCF', results['dcf']['intrinsic_value']))
            
            if 'relative' in results and 'average_value' in results['relative']:
                valuations.append(('Relative', results['relative']['average_value']))
            
            if 'ddm' in results and 'intrinsic_value' in results['ddm']:
                valuations.append(('DDM', results['ddm']['intrinsic_value']))
            
            # Calculate metrics
            if valuations:
                values = [v[1] for v in valuations if v[1] > 0]
                avg_intrinsic = np.mean(values) if values else 0
                median_intrinsic = np.median(values) if values else 0
                
                # Recommendation logic
                if current_price > 0 and avg_intrinsic > 0:
                    upside = (avg_intrinsic - current_price) / current_price * 100
                    
                    if upside > 20:
                        recommendation = "Strong Buy"
                    elif upside > 10:
                        recommendation = "Buy"
                    elif upside > -10:
                        recommendation = "Hold"
                    elif upside > -20:
                        recommendation = "Sell"
                    else:
                        recommendation = "Strong Sell"
                else:
                    recommendation = "Insufficient Data"
                    upside = 0
                
                return {
                    'valuations': valuations,
                    'average_intrinsic_value': avg_intrinsic,
                    'median_intrinsic_value': median_intrinsic,
                    'current_price': current_price,
                    'upside_potential': upside,
                    'recommendation': recommendation,
                    'confidence': self._calculate_confidence(results)
                }
            
            return {'error': 'No valid valuations available'}
            
        except Exception as e:
            logger.error(f"Summary creation error: {e}")
            return {'error': str(e)}
    
    def _calculate_confidence(self, results: Dict) -> str:
        """Calculate confidence level based on data quality and consistency."""
        score = 0
        
        # Data quality
        if self.data.get('data_quality') == 'Good':
            score += 30
        elif self.data.get('data_quality') == 'Fair':
            score += 15
        
        # Method availability
        valid_methods = sum(1 for method in ['dcf', 'relative', 'ddm'] 
                           if method in results and 'error' not in results[method])
        score += valid_methods * 20
        
        # Risk factors
        if 'risk_metrics' in results:
            risk_factors = results['risk_metrics'].get('risk_factors', [])
            if len(risk_factors) <= 2:
                score += 20
        
        if score >= 80:
            return "High"
        elif score >= 50:
            return "Medium"
        else:
            return "Low"
