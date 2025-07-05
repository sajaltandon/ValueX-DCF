import numpy as np
import logging
from typing import List, Dict, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_inputs(base_fcf: float, growth_rate: float, wacc: float, terminal_growth: float, shares_outstanding: float) -> bool:
    """Validate DCF model inputs for reasonable ranges and logical consistency."""
    if base_fcf <= 0:
        raise ValueError(f"Base FCF must be positive, got: {base_fcf}")
    
    if not (-0.5 <= growth_rate <= 1.0):  # -50% to 100% growth
        raise ValueError(f"Growth rate should be between -50% and 100%, got: {growth_rate*100:.1f}%")
    
    if not (0.01 <= wacc <= 0.50):  # 1% to 50% WACC
        raise ValueError(f"WACC should be between 1% and 50%, got: {wacc*100:.1f}%")
    
    if not (-0.10 <= terminal_growth <= 0.15):  # -10% to 15% terminal growth
        raise ValueError(f"Terminal growth should be between -10% and 15%, got: {terminal_growth*100:.1f}%")
    
    if wacc <= terminal_growth:
        raise ValueError(f"WACC ({wacc*100:.1f}%) must be greater than terminal growth ({terminal_growth*100:.1f}%)")
    
    if shares_outstanding <= 0:
        raise ValueError(f"Shares outstanding must be positive, got: {shares_outstanding}")
    
    return True

def project_fcf(base_fcf: float, growth_rate: float, years: int = 5) -> List[float]:
    """
    Project Free Cash Flow for specified years with compound growth.
    
    Args:
        base_fcf: Base year Free Cash Flow
        growth_rate: Annual growth rate (as decimal)
        years: Number of years to project
    
    Returns:
        List of projected FCF values
    """
    try:
        validate_inputs(base_fcf, growth_rate, 0.1, 0.03, 1)  # Basic validation
        projected_fcf = []
        
        for i in range(1, years + 1):
            fcf_year = base_fcf * ((1 + growth_rate) ** i)
            projected_fcf.append(fcf_year)
            logger.info(f"Year {i} FCF: ₹{fcf_year:,.0f}")
        
        return projected_fcf
    
    except Exception as e:
        logger.error(f"Error in FCF projection: {e}")
        raise

def calculate_dcf(fcf_list: List[float], wacc: float, terminal_growth: float, shares_outstanding: float) -> Dict[str, Union[float, List[float]]]:
    """
    Calculate DCF valuation with comprehensive error handling and detailed breakdown.
    
    Args:
        fcf_list: List of projected FCF values
        wacc: Weighted Average Cost of Capital
        terminal_growth: Long-term growth rate
        shares_outstanding: Number of shares outstanding
    
    Returns:
        Dictionary containing valuation results
    """
    try:
        # Validate inputs
        if not fcf_list:
            raise ValueError("FCF list cannot be empty")
        
        validate_inputs(fcf_list[0], 0.1, wacc, terminal_growth, shares_outstanding)
        
        # Calculate present value of projected FCFs
        discounted_fcf = []
        for i, fcf in enumerate(fcf_list):
            pv_fcf = fcf / ((1 + wacc) ** (i + 1))
            discounted_fcf.append(pv_fcf)
            logger.info(f"Year {i+1} PV of FCF: ₹{pv_fcf:,.0f}")
        
        # Calculate terminal value
        final_fcf = fcf_list[-1]
        terminal_fcf = final_fcf * (1 + terminal_growth)
        terminal_value = terminal_fcf / (wacc - terminal_growth)
        
        # Present value of terminal value
        discounted_terminal = terminal_value / ((1 + wacc) ** len(fcf_list))
        
        # Enterprise value and intrinsic value
        pv_explicit_fcf = sum(discounted_fcf)
        enterprise_value = pv_explicit_fcf + discounted_terminal
        intrinsic_value = enterprise_value / shares_outstanding
        
        logger.info(f"PV of Explicit FCFs: ₹{pv_explicit_fcf:,.0f}")
        logger.info(f"PV of Terminal Value: ₹{discounted_terminal:,.0f}")
        logger.info(f"Enterprise Value: ₹{enterprise_value:,.0f}")
        logger.info(f"Intrinsic Value per Share: ₹{intrinsic_value:.2f}")
        
        return {
            'enterprise_value': enterprise_value,
            'intrinsic_value': intrinsic_value,
            'discounted_fcf': discounted_fcf,
            'discounted_terminal': discounted_terminal,
            'terminal_value': terminal_value,
            'pv_explicit_fcf': pv_explicit_fcf,
            'terminal_fcf': terminal_fcf
        }
    
    except ZeroDivisionError:
        logger.error("Division by zero: WACC must be greater than terminal growth rate")
        raise ValueError("WACC must be greater than terminal growth rate")
    
    except Exception as e:
        logger.error(f"Error in DCF calculation: {e}")
        raise

def calculate_wacc(risk_free_rate: float, market_risk_premium: float, beta: float, 
                   tax_rate: float = 0.25, debt_equity_ratio: float = 0.0, 
                   cost_of_debt: float = 0.05) -> float:
    """
    Calculate Weighted Average Cost of Capital (WACC).
    
    Args:
        risk_free_rate: Risk-free rate (government bond yield)
        market_risk_premium: Market risk premium
        beta: Stock's beta coefficient
        tax_rate: Corporate tax rate
        debt_equity_ratio: Debt-to-equity ratio
        cost_of_debt: Pre-tax cost of debt
    
    Returns:
        WACC as decimal
    """
    try:
        cost_of_equity = risk_free_rate + (beta * market_risk_premium)
        
        # Weight of equity and debt
        weight_equity = 1 / (1 + debt_equity_ratio)
        weight_debt = debt_equity_ratio / (1 + debt_equity_ratio)
        
        # After-tax cost of debt
        after_tax_cost_debt = cost_of_debt * (1 - tax_rate)
        
        wacc = (weight_equity * cost_of_equity) + (weight_debt * after_tax_cost_debt)
        
        logger.info(f"Calculated WACC: {wacc*100:.2f}%")
        return wacc
    
    except Exception as e:
        logger.error(f"Error calculating WACC: {e}")
        raise
