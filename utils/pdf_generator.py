"""
Professional PDF report generator for ValueX valuation reports.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
import numpy as np
import logging

# Handle fpdf2 import with fallback
try:
    from fpdf2 import FPDF
    PDF_AVAILABLE = True
except ImportError:
    print("Warning: fpdf2 not installed. PDF generation will be disabled.")
    print("Install with: pip install fpdf2")
    PDF_AVAILABLE = False
    
    # Create a dummy FPDF class for when fpdf2 is not available
    class FPDF:
        def __init__(self):
            pass

logger = logging.getLogger(__name__)

class ValuationReportPDF:
    """Generate professional PDF valuation reports."""
    
    def __init__(self):
        """Initialize PDF report generator."""
        if not PDF_AVAILABLE:
            logger.warning("PDF generation not available - fpdf2 not installed")
            self.pdf = None
        else:
            self.pdf = FPDF()
            self.pdf.set_auto_page_break(auto=True, margin=15)
    
    def generate_comprehensive_report(self, company_data: Dict, valuation_results: Dict, 
                                    risk_analysis: Dict, output_path: str = None) -> str:
        """Generate a comprehensive valuation report."""
        
        # Check if PDF generation is available
        if not PDF_AVAILABLE:
            logger.warning("PDF generation not available, falling back to text report")
            return self.generate_text_report(company_data, valuation_results, risk_analysis, output_path)
        
        try:
            # Initialize PDF
            self.pdf = FPDF()
            self.pdf.set_auto_page_break(auto=True, margin=15)
            
            # Cover page
            self._add_cover_page(company_data)
            
            # Executive summary
            self._add_executive_summary(company_data, valuation_results)
            
            # Company overview
            self._add_company_overview(company_data)
            
            # Valuation methodology
            self._add_valuation_methodology(valuation_results)
            
            # DCF Analysis
            self._add_dcf_analysis(valuation_results.get('dcf', {}))
            
            # Relative valuation
            self._add_relative_valuation(valuation_results.get('relative', {}))
            
            # Risk analysis
            self._add_risk_analysis(risk_analysis)
            
            # Scenario analysis
            if 'scenario_analysis' in risk_analysis:
                self._add_scenario_analysis(risk_analysis['scenario_analysis'])
            
            # Investment recommendation
            self._add_investment_recommendation(valuation_results.get('summary', {}))
            
            # Appendices
            self._add_appendices(company_data, valuation_results)
            
            # Save PDF
            if output_path is None:
                output_path = f"reports/ValueX_Report_{company_data.get('ticker', 'Unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # Create reports directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else 'reports', exist_ok=True)
            
            self.pdf.output(output_path)
            logger.info(f"Report generated: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            return f"Error: {str(e)}"
    
    def _add_cover_page(self, company_data: Dict):
        """Add cover page."""
        self.pdf.add_page()
        
        # Title
        self.pdf.set_font('Arial', 'B', 24)
        self.pdf.cell(0, 20, 'ValueX Equity Valuation Report', 0, 1, 'C')
        
        self.pdf.ln(20)
        
        # Company info
        self.pdf.set_font('Arial', 'B', 18)
        self.pdf.cell(0, 15, f"{company_data.get('company_name', 'Unknown Company')}", 0, 1, 'C')
        
        self.pdf.set_font('Arial', '', 14)
        self.pdf.cell(0, 10, f"Ticker: {company_data.get('ticker', 'N/A')}", 0, 1, 'C')
        self.pdf.cell(0, 10, f"Sector: {company_data.get('sector', 'N/A')}", 0, 1, 'C')
        self.pdf.cell(0, 10, f"Industry: {company_data.get('industry', 'N/A')}", 0, 1, 'C')
        
        self.pdf.ln(30)
        
        # Date and logo placeholder
        self.pdf.set_font('Arial', '', 12)
        self.pdf.cell(0, 10, f"Report Date: {datetime.now().strftime('%B %d, %Y')}", 0, 1, 'C')
        
        self.pdf.ln(40)
        
        # Disclaimer
        self.pdf.set_font('Arial', 'I', 10)
        disclaimer = ("This report is generated by ValueX for informational purposes only. "
                     "It should not be considered as investment advice. Please consult with "
                     "a qualified financial advisor before making investment decisions.")
        self.pdf.multi_cell(0, 5, disclaimer, 0, 'C')
    
    def _add_executive_summary(self, company_data: Dict, valuation_results: Dict):
        """Add executive summary page."""
        self.pdf.add_page()
        
        self._add_section_header("Executive Summary")
        
        # Key metrics table
        current_price = company_data.get('current_price', 0)
        
        summary = valuation_results.get('summary', {})
        avg_intrinsic = summary.get('average_intrinsic_value', 0)
        recommendation = summary.get('recommendation', 'N/A')
        upside = summary.get('upside_potential', 0)
        
        self.pdf.set_font('Arial', '', 11)
        
        # Key metrics
        metrics = [
            ['Current Market Price', f"₹{current_price:.2f}"],
            ['Average Intrinsic Value', f"₹{avg_intrinsic:.2f}"],
            ['Upside/(Downside)', f"{upside:.1f}%"],
            ['Investment Recommendation', recommendation],
            ['Market Cap', f"₹{company_data.get('market_cap', 0):,.0f}"],
            ['Beta', f"{company_data.get('beta', 0):.2f}"],
            ['Data Quality', company_data.get('data_quality', 'N/A')]
        ]
        
        for metric in metrics:
            self.pdf.cell(80, 8, metric[0], 1)
            self.pdf.cell(80, 8, metric[1], 1)
            self.pdf.ln()
        
        self.pdf.ln(10)
        
        # Summary text
        summary_text = f"""
Based on our comprehensive valuation analysis using multiple methodologies including DCF, 
relative valuation, and risk assessment, we arrive at an average intrinsic value of 
₹{avg_intrinsic:.2f} per share for {company_data.get('company_name', 'the company')}.

With the current market price of ₹{current_price:.2f}, this represents a 
{upside:.1f}% {'upside' if upside > 0 else 'downside'} potential.

Our recommendation is: {recommendation}
        """
        
        self.pdf.multi_cell(0, 6, summary_text.strip())
    
    def _add_company_overview(self, company_data: Dict):
        """Add company overview."""
        self.pdf.add_page()
        
        self._add_section_header("Company Overview")
        
        self.pdf.set_font('Arial', '', 11)
        
        # Company details
        details = f"""
Company Name: {company_data.get('company_name', 'N/A')}
Ticker Symbol: {company_data.get('ticker', 'N/A')}
Sector: {company_data.get('sector', 'N/A')}
Industry: {company_data.get('industry', 'N/A')}

Financial Highlights:
• Revenue: ₹{company_data.get('revenue', 0):,.0f}
• Free Cash Flow: ₹{company_data.get('fcf', 0):,.0f}
• Shares Outstanding: {company_data.get('shares_outstanding', 0):,.0f}
• Total Debt: ₹{company_data.get('total_debt', 0):,.0f}

Market Data:
• Current Price: ₹{company_data.get('current_price', 0):.2f}
• Market Capitalization: ₹{company_data.get('market_cap', 0):,.0f}
• Beta: {company_data.get('beta', 0):.2f}
• Volatility: {company_data.get('volatility', 0)*100:.1f}%
• P/E Ratio: {company_data.get('pe_ratio', 0):.1f}
        """
        
        self.pdf.multi_cell(0, 6, details.strip())
    
    def _add_valuation_methodology(self, valuation_results: Dict):
        """Add valuation methodology section."""
        self.pdf.add_page()
        
        self._add_section_header("Valuation Methodology")
        
        self.pdf.set_font('Arial', '', 11)
        
        methodology_text = """
Our valuation approach employs multiple methodologies to arrive at a comprehensive 
assessment of intrinsic value:

1. Discounted Cash Flow (DCF) Analysis
   - Projects future free cash flows for 5 years
   - Applies terminal value using Gordon Growth Model
   - Discounts to present value using WACC

2. Relative Valuation
   - P/E ratio comparison with industry peers
   - EV/EBITDA multiple analysis
   - Price-to-Sales ratio assessment

3. Risk Analysis
   - Monte Carlo simulation for parameter uncertainty
   - Scenario analysis (bear, base, bull cases)
   - Stress testing under extreme conditions

4. Risk-Adjusted Valuation
   - Applies risk premiums based on identified risk factors
   - Considers company-specific and market risks

The final recommendation is based on the convergence of these methodologies,
weighted by the quality and reliability of available data.
        """
        
        self.pdf.multi_cell(0, 6, methodology_text.strip())
    
    def _add_dcf_analysis(self, dcf_results: Dict):
        """Add DCF analysis section."""
        self.pdf.add_page()
        
        self._add_section_header("DCF Analysis")
        
        if 'error' in dcf_results:
            self.pdf.set_font('Arial', '', 11)
            self.pdf.multi_cell(0, 6, f"DCF Analysis Error: {dcf_results['error']}")
            return
        
        # Assumptions table
        assumptions = dcf_results.get('assumptions', {})
        
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.cell(0, 10, 'Key Assumptions:', 0, 1)
        
        self.pdf.set_font('Arial', '', 11)
        
        assumption_data = [
            ['FCF Growth Rate', f"{assumptions.get('growth_rate', 0)*100:.1f}%"],
            ['WACC (Discount Rate)', f"{assumptions.get('wacc', 0)*100:.1f}%"],
            ['Terminal Growth Rate', f"{assumptions.get('terminal_growth', 0)*100:.1f}%"],
            ['Projection Period', f"{assumptions.get('years', 5)} years"]
        ]
        
        for row in assumption_data:
            self.pdf.cell(80, 8, row[0], 1)
            self.pdf.cell(80, 8, row[1], 1)
            self.pdf.ln()
        
        self.pdf.ln(10)
        
        # Results
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.cell(0, 10, 'DCF Results:', 0, 1)
        
        self.pdf.set_font('Arial', '', 11)
        
        results_data = [
            ['Enterprise Value', f"₹{dcf_results.get('enterprise_value', 0):,.0f}"],
            ['Intrinsic Value per Share', f"₹{dcf_results.get('intrinsic_value', 0):.2f}"]
        ]
        
        for row in results_data:
            self.pdf.cell(80, 8, row[0], 1)
            self.pdf.cell(80, 8, row[1], 1)
            self.pdf.ln()
    
    def _add_relative_valuation(self, relative_results: Dict):
        """Add relative valuation section."""
        self.pdf.add_page()
        
        self._add_section_header("Relative Valuation")
        
        if 'error' in relative_results:
            self.pdf.set_font('Arial', '', 11)
            self.pdf.multi_cell(0, 6, f"Relative Valuation Error: {relative_results['error']}")
            return
        
        self.pdf.set_font('Arial', '', 11)
        
        # Valuation results table
        valuation_data = [
            ['P/E Valuation', f"₹{relative_results.get('pe_valuation', 0):.2f}"],
            ['EV/EBITDA Valuation', f"₹{relative_results.get('ev_ebitda_valuation', 0):.2f}"],
            ['Price/Sales Valuation', f"₹{relative_results.get('price_sales_valuation', 0):.2f}"],
            ['Average Value', f"₹{relative_results.get('average_value', 0):.2f}"]
        ]
        
        for row in valuation_data:
            self.pdf.cell(80, 8, row[0], 1)
            self.pdf.cell(80, 8, row[1], 1)
            self.pdf.ln()
        
        self.pdf.ln(10)
        
        # Multiples used
        multiples = relative_results.get('multiples_used', {})
        self.pdf.set_font('Arial', 'B', 11)
        self.pdf.cell(0, 8, 'Multiples Used:', 0, 1)
        
        self.pdf.set_font('Arial', '', 10)
        for multiple, value in multiples.items():
            self.pdf.cell(0, 6, f"• {multiple.replace('_', ' ').title()}: {value:.1f}x", 0, 1)
    
    def _add_risk_analysis(self, risk_analysis: Dict):
        """Add risk analysis section."""
        self.pdf.add_page()
        
        self._add_section_header("Risk Analysis")
        
        self.pdf.set_font('Arial', '', 11)
        
        # Risk metrics
        risk_metrics = risk_analysis.get('risk_metrics', {})
        
        if 'error' not in risk_metrics:
            risk_data = [
                ['Volatility', f"{risk_metrics.get('volatility', 0)*100:.1f}%"],
                ['Beta', f"{risk_metrics.get('beta', 0):.2f}"],
                ['Value at Risk (95%)', f"₹{risk_metrics.get('var_95', 0):.2f}"],
                ['Risk Level', risk_metrics.get('risk_level', 'Unknown')]
            ]
            
            for row in risk_data:
                self.pdf.cell(80, 8, row[0], 1)
                self.pdf.cell(80, 8, row[1], 1)
                self.pdf.ln()
            
            self.pdf.ln(10)
            
            # Risk factors
            risk_factors = risk_metrics.get('risk_factors', [])
            self.pdf.set_font('Arial', 'B', 11)
            self.pdf.cell(0, 8, 'Identified Risk Factors:', 0, 1)
            
            self.pdf.set_font('Arial', '', 10)
            for factor in risk_factors:
                self.pdf.cell(0, 6, f"• {factor}", 0, 1)
    
    def _add_scenario_analysis(self, scenario_results: Dict):
        """Add scenario analysis section."""
        self.pdf.add_page()
        
        self._add_section_header("Scenario Analysis")
        
        if 'error' in scenario_results:
            self.pdf.set_font('Arial', '', 11)
            self.pdf.multi_cell(0, 6, f"Scenario Analysis Error: {scenario_results['error']}")
            return
        
        self.pdf.set_font('Arial', '', 11)
        
        scenarios = scenario_results.get('scenarios', {})
        
        for scenario_name, scenario_data in scenarios.items():
            if 'error' in scenario_data:
                continue
                
            self.pdf.set_font('Arial', 'B', 11)
            self.pdf.cell(0, 8, f"{scenario_name.title()} Case:", 0, 1)
            
            self.pdf.set_font('Arial', '', 10)
            self.pdf.cell(0, 6, f"Intrinsic Value: ₹{scenario_data.get('intrinsic_value', 0):.2f}", 0, 1)
            self.pdf.cell(0, 6, f"Description: {scenario_data.get('description', 'N/A')}", 0, 1)
            self.pdf.ln(5)
        
        # Summary
        upside_downside = scenario_results.get('upside_downside', {})
        self.pdf.set_font('Arial', 'B', 11)
        self.pdf.cell(0, 8, 'Upside/Downside Summary:', 0, 1)
        
        self.pdf.set_font('Arial', '', 10)
        self.pdf.cell(0, 6, f"Bull Case Upside: {upside_downside.get('bull_upside', 0):.1f}%", 0, 1)
        self.pdf.cell(0, 6, f"Bear Case Downside: {upside_downside.get('bear_downside', 0):.1f}%", 0, 1)
    
    def _add_investment_recommendation(self, summary: Dict):
        """Add investment recommendation."""
        self.pdf.add_page()
        
        self._add_section_header("Investment Recommendation")
        
        self.pdf.set_font('Arial', '', 11)
        
        recommendation = summary.get('recommendation', 'N/A')
        confidence = summary.get('confidence', 'Unknown')
        upside = summary.get('upside_potential', 0)
        
        recommendation_text = f"""
Investment Recommendation: {recommendation}
Confidence Level: {confidence}
Upside/(Downside) Potential: {upside:.1f}%

Rationale:
Based on our comprehensive valuation analysis, we recommend a {recommendation.lower()} 
position in this security. This recommendation is based on:

1. Fundamental valuation indicating {'undervaluation' if upside > 0 else 'overvaluation'}
2. Risk-adjusted analysis considering company-specific factors
3. Scenario analysis across different market conditions
4. Relative valuation compared to industry peers

Investment Considerations:
• Monitor key assumptions for changes in business fundamentals
• Consider position sizing based on risk tolerance
• Review recommendation quarterly or upon material news
• This analysis is based on current market conditions and available data

Risk Warning:
All investments carry risk of loss. Past performance does not guarantee future results.
This analysis is for informational purposes only and should not be considered as 
personalized investment advice.
        """
        
        self.pdf.multi_cell(0, 6, recommendation_text.strip())
    
    def _add_appendices(self, company_data: Dict, valuation_results: Dict):
        """Add appendices with detailed calculations."""
        self.pdf.add_page()
        
        self._add_section_header("Appendices")
        
        self.pdf.set_font('Arial', '', 10)
        
        # Data sources and limitations
        appendix_text = f"""
A. Data Sources and Quality
• Financial data sourced from Yahoo Finance
• Data quality assessment: {company_data.get('data_quality', 'Unknown')}
• Last updated: {company_data.get('last_updated', 'Unknown')}

B. Model Limitations
• DCF model sensitivity to assumptions
• Terminal value represents significant portion of valuation
• Historical data may not predict future performance
• Market conditions can change rapidly

C. Methodology Notes
• Free Cash Flow calculation: Operating CF - CapEx
• WACC estimation based on standard finance models
• Relative valuation multiples are industry estimates
• Risk adjustments are model-based estimates

D. Contact Information
Generated by ValueX - Intelligent DCF Valuation Tool
Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        self.pdf.multi_cell(0, 5, appendix_text.strip())
    
    def _add_section_header(self, title: str):
        """Add a section header."""
        self.pdf.set_font('Arial', 'B', 16)
        self.pdf.cell(0, 15, title, 0, 1)
        self.pdf.ln(5)
    
    def generate_text_report(self, company_data: Dict, valuation_results: Dict, 
                            risk_analysis: Dict, output_path: str = None) -> str:
        """Generate a text-based report when PDF is not available."""
        try:
            if output_path is None:
                output_path = f"reports/ValueX_Report_{company_data.get('ticker', 'Unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            # Create reports directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else 'reports', exist_ok=True)
            
            # Generate text report content
            report_content = self._generate_text_content(company_data, valuation_results, risk_analysis)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logger.info(f"Text report generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating text report: {e}")
            return f"Error: {str(e)}"
    
    def _generate_text_content(self, company_data: Dict, valuation_results: Dict, risk_analysis: Dict) -> str:
        """Generate text content for the report."""
        content = []
        
        # Header
        content.append("="*80)
        content.append("VALUEX EQUITY VALUATION REPORT")
        content.append("="*80)
        content.append(f"Company: {company_data.get('company_name', 'Unknown')}")
        content.append(f"Ticker: {company_data.get('ticker', 'N/A')}")
        content.append(f"Report Date: {datetime.now().strftime('%B %d, %Y')}")
        content.append("="*80)
        content.append("")
        
        # Executive Summary
        content.append("EXECUTIVE SUMMARY")
        content.append("-"*50)
        
        summary = valuation_results.get('summary', {})
        current_price = company_data.get('current_price', 0)
        avg_intrinsic = summary.get('average_intrinsic_value', 0)
        recommendation = summary.get('recommendation', 'N/A')
        upside = summary.get('upside_potential', 0)
        
        content.append(f"Current Market Price: ₹{current_price:.2f}")
        content.append(f"Average Intrinsic Value: ₹{avg_intrinsic:.2f}")
        content.append(f"Upside/(Downside): {upside:.1f}%")
        content.append(f"Investment Recommendation: {recommendation}")
        content.append(f"Market Cap: ₹{company_data.get('market_cap', 0):,.0f}")
        content.append(f"Beta: {company_data.get('beta', 0):.2f}")
        content.append("")
        
        # Company Overview
        content.append("COMPANY OVERVIEW")
        content.append("-"*50)
        content.append(f"Sector: {company_data.get('sector', 'N/A')}")
        content.append(f"Industry: {company_data.get('industry', 'N/A')}")
        content.append(f"Revenue: ₹{company_data.get('revenue', 0):,.0f}")
        content.append(f"Free Cash Flow: ₹{company_data.get('fcf', 0):,.0f}")
        content.append(f"Shares Outstanding: {company_data.get('shares_outstanding', 0):,.0f}")
        content.append("")
        
        # DCF Analysis
        dcf_results = valuation_results.get('dcf', {})
        if 'error' not in dcf_results:
            content.append("DCF ANALYSIS")
            content.append("-"*50)
            assumptions = dcf_results.get('assumptions', {})
            content.append(f"FCF Growth Rate: {assumptions.get('growth_rate', 0)*100:.1f}%")
            content.append(f"WACC: {assumptions.get('wacc', 0)*100:.1f}%")
            content.append(f"Terminal Growth: {assumptions.get('terminal_growth', 0)*100:.1f}%")
            content.append(f"Enterprise Value: ₹{dcf_results.get('enterprise_value', 0):,.0f}")
            content.append(f"Intrinsic Value per Share: ₹{dcf_results.get('intrinsic_value', 0):.2f}")
            content.append("")
        
        # Risk Analysis
        risk_metrics = risk_analysis.get('risk_metrics', {})
        if 'error' not in risk_metrics:
            content.append("RISK ANALYSIS")
            content.append("-"*50)
            content.append(f"Volatility: {risk_metrics.get('volatility', 0)*100:.1f}%")
            content.append(f"Beta: {risk_metrics.get('beta', 0):.2f}")
            content.append(f"Risk Level: {risk_metrics.get('risk_level', 'Unknown')}")
            
            risk_factors = risk_metrics.get('risk_factors', [])
            if risk_factors:
                content.append("Risk Factors:")
                for factor in risk_factors:
                    content.append(f"• {factor}")
            content.append("")
        
        # Scenario Analysis
        scenario_analysis = risk_analysis.get('scenario_analysis', {})
        if 'error' not in scenario_analysis:
            content.append("SCENARIO ANALYSIS")
            content.append("-"*50)
            scenarios = scenario_analysis.get('scenarios', {})
            for scenario_name, scenario_data in scenarios.items():
                if 'error' not in scenario_data:
                    content.append(f"{scenario_name.title()} Case: ₹{scenario_data.get('intrinsic_value', 0):.2f}")
            content.append("")
        
        # Investment Recommendation
        content.append("INVESTMENT RECOMMENDATION")
        content.append("-"*50)
        content.append(f"Recommendation: {recommendation}")
        content.append(f"Confidence Level: {summary.get('confidence', 'Unknown')}")
        content.append(f"Upside Potential: {upside:.1f}%")
        content.append("")
        content.append("This analysis is for informational purposes only and should not be")
        content.append("considered as personalized investment advice.")
        content.append("")
        
        # Footer
        content.append("="*80)
        content.append("Generated by ValueX - Intelligent DCF Valuation Tool")
        content.append(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append("="*80)
        
        return "\n".join(content)
