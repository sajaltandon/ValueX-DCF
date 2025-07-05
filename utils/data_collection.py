import yfinance as yf
import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional, Union
import requests
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCollectionError(Exception):
    """Custom exception for data collection errors."""
    pass

def fetch_financials(ticker: str) -> Dict[str, Union[float, int, str]]:
    """
    Fetch comprehensive financial data for a given ticker.
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        Dictionary containing financial metrics
    """
    try:
        # Clean and validate ticker
        ticker = ticker.strip().upper()
        
        # Common ticker corrections
        ticker_corrections = {
            "APPLE": "AAPL",
            "MICROSOFT": "MSFT", 
            "GOOGLE": "GOOGL",
            "AMAZON": "AMZN",
            "TESLA": "TSLA",
            "NETFLIX": "NFLX",
            "META": "META",
            "NVIDIA": "NVDA",
            "ADOBE": "ADBE",
            "SALESFORCE": "CRM"
        }
        
        # Apply correction if needed
        original_ticker = ticker
        if ticker in ticker_corrections:
            ticker = ticker_corrections[ticker]
            logger.info(f"Corrected ticker from {original_ticker} to {ticker}")
        
        logger.info(f"Fetching financial data for {ticker}")
        stock = yf.Ticker(ticker)
        
        # Basic company info
        info = stock.info
        
        if not info:
            raise DataCollectionError(f"No data found for ticker: {ticker}")
        
        # Get financial statements
        financials = stock.financials
        cashflow = stock.cashflow
        balance_sheet = stock.balance_sheet
        
        # Calculate Free Cash Flow
        fcf = calculate_free_cash_flow(cashflow)
        
        # Get historical prices for volatility calculation
        hist_data = stock.history(period="2y")
        
        # Calculate metrics
        market_cap = info.get("marketCap", 0)
        shares_outstanding = info.get("sharesOutstanding", 0)
        current_price = info.get("currentPrice", 0)
        
        # Validate critical data
        if market_cap == 0:
            raise DataCollectionError(f"No market cap data for {ticker}")
        
        if shares_outstanding == 0:
            raise DataCollectionError(f"No shares outstanding data for {ticker}")
        
        if fcf == 0:
            logger.warning(f"Free Cash Flow is zero for {ticker}. This may indicate data issues.")
        
        # Fallback for missing current price
        if current_price == 0 and not hist_data.empty:
            current_price = hist_data['Close'].iloc[-1]
        
        # Calculate additional metrics
        beta = info.get("beta", 1.0)
        pe_ratio = info.get("trailingPE", 0)
        revenue = get_latest_revenue(financials)
        total_debt = get_total_debt(balance_sheet)
        
        # Risk metrics
        volatility = calculate_volatility(hist_data) if not hist_data.empty else 0.25
        
        result = {
            "ticker": ticker,
            "company_name": info.get("longName", ticker),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
            "fcf": fcf,
            "revenue": revenue,
            "shares_outstanding": max(shares_outstanding, 1),  # Prevent division by zero
            "current_price": current_price,
            "market_cap": market_cap,
            "beta": beta,
            "pe_ratio": pe_ratio,
            "total_debt": total_debt,
            "volatility": volatility,
            "data_quality": assess_data_quality(fcf, revenue, shares_outstanding, current_price),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        logger.info(f"Successfully fetched data for {ticker}")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching financials for {ticker}: {e}")
        # Return minimal safe data to prevent crashes
        return {
            "ticker": ticker,
            "company_name": ticker,
            "sector": "Unknown",
            "industry": "Unknown",
            "fcf": 0,
            "revenue": 0,
            "shares_outstanding": 1,
            "current_price": 0,
            "market_cap": 0,
            "beta": 1.0,
            "pe_ratio": 0,
            "total_debt": 0,
            "volatility": 0.25,
            "data_quality": "Poor",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error": str(e)
        }

def calculate_free_cash_flow(cashflow: pd.DataFrame) -> float:
    """Calculate Free Cash Flow from cash flow statement."""
    try:
        if cashflow.empty:
            return 0
        
        # Try different possible field names
        operating_cf_fields = [
            "Total Cash From Operating Activities",
            "Operating Cash Flow",
            "Cash Flow From Operations",
            "Net Cash From Operating Activities"
        ]
        
        capex_fields = [
            "Capital Expenditures",
            "Capital Expenditure",
            "Capex",
            "Cash Flow From Investing Activities"
        ]
        
        operating_cf = 0
        for field in operating_cf_fields:
            if field in cashflow.index:
                operating_cf = cashflow.loc[field].iloc[0] if not cashflow.loc[field].empty else 0
                break
        
        capex = 0
        for field in capex_fields:
            if field in cashflow.index:
                capex = cashflow.loc[field].iloc[0] if not cashflow.loc[field].empty else 0
                break
        
        # CapEx is usually negative, so we add it (double negative = positive FCF)
        fcf = operating_cf + capex if capex < 0 else operating_cf - abs(capex)
        
        return fcf if not pd.isna(fcf) else 0
        
    except Exception as e:
        logger.warning(f"Error calculating FCF: {e}")
        return 0

def get_latest_revenue(financials: pd.DataFrame) -> float:
    """Extract latest revenue from financial statements."""
    try:
        if financials.empty:
            return 0
        
        revenue_fields = [
            "Total Revenue",
            "Revenue",
            "Net Sales",
            "Total Revenues"
        ]
        
        for field in revenue_fields:
            if field in financials.index:
                revenue = financials.loc[field].iloc[0] if not financials.loc[field].empty else 0
                return revenue if not pd.isna(revenue) else 0
        
        return 0
        
    except Exception as e:
        logger.warning(f"Error getting revenue: {e}")
        return 0

def get_total_debt(balance_sheet: pd.DataFrame) -> float:
    """Calculate total debt from balance sheet."""
    try:
        if balance_sheet.empty:
            return 0
        
        debt_fields = [
            "Total Debt",
            "Long Term Debt",
            "Short Long Term Debt",
            "Net Debt"
        ]
        
        total_debt = 0
        for field in debt_fields:
            if field in balance_sheet.index:
                debt_value = balance_sheet.loc[field].iloc[0] if not balance_sheet.loc[field].empty else 0
                if not pd.isna(debt_value):
                    total_debt += debt_value
        
        return total_debt
        
    except Exception as e:
        logger.warning(f"Error calculating total debt: {e}")
        return 0

def calculate_volatility(hist_data: pd.DataFrame, period_days: int = 252) -> float:
    """Calculate annualized volatility from historical price data."""
    try:
        if hist_data.empty or len(hist_data) < 10:
            return 0.25  # Default volatility
        
        # Calculate daily returns
        returns = hist_data['Close'].pct_change().dropna()
        
        if returns.empty:
            return 0.25
        
        # Annualized volatility
        volatility = returns.std() * np.sqrt(period_days)
        
        return volatility if not pd.isna(volatility) else 0.25
        
    except Exception as e:
        logger.warning(f"Error calculating volatility: {e}")
        return 0.25

def assess_data_quality(fcf: float, revenue: float, shares: float, price: float) -> str:
    """Assess the quality of fetched financial data."""
    try:
        quality_score = 0
        
        # Check if key metrics are available and reasonable
        if fcf != 0:
            quality_score += 25
        if revenue > 0:
            quality_score += 25
        if shares > 0:
            quality_score += 25
        if price > 0:
            quality_score += 25
        
        if quality_score >= 75:
            return "Good"
        elif quality_score >= 50:
            return "Fair"
        else:
            return "Poor"
            
    except Exception:
        return "Unknown"

def get_risk_free_rate() -> float:
    """
    Fetch current risk-free rate (10-year government bond yield).
    This is a simplified implementation - in production, you'd use a financial data API.
    """
    try:
        # For demonstration, return a reasonable default
        # In production, fetch from FRED, Bloomberg, or similar
        return 0.06  # 6% default risk-free rate
    except Exception as e:
        logger.warning(f"Could not fetch risk-free rate: {e}")
        return 0.06

def validate_ticker(ticker: str) -> bool:
    """Validate if ticker exists and has data."""
    try:
        # Clean the ticker symbol
        ticker = ticker.strip().upper()
        
        # Common ticker corrections
        ticker_corrections = {
            "APPLE": "AAPL",
            "MICROSOFT": "MSFT", 
            "GOOGLE": "GOOGL",
            "AMAZON": "AMZN",
            "TESLA": "TSLA",
            "NETFLIX": "NFLX",
            "META": "META",
            "NVIDIA": "NVDA",
            "ADOBE": "ADBE",
            "SALESFORCE": "CRM"
        }
        
        # Apply correction if needed
        if ticker in ticker_corrections:
            ticker = ticker_corrections[ticker]
        
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Check if we got actual data
        if not info or not info.get("symbol"):
            return False
            
        # Check if we have basic financial data
        if info.get("marketCap", 0) == 0:
            return False
            
        return True
        
    except Exception as e:
        logger.warning(f"Ticker validation failed for {ticker}: {e}")
        return False
