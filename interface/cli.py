import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_collection import fetch_financials, validate_ticker
from models.dcf_model import calculate_dcf, project_fcf
from models.valuation_methods import ValuationSuite
from models.risk_analysis import RiskAnalyzer
from models.sensitivity_analysis import generate_sensitivity_matrix
from agents.report_generator import generate_report
from agents.assumption_explainer import explain_assumptions
from utils.pdf_generator import ValuationReportPDF
from config import *

console = Console()
app = typer.Typer(help="💼 ValueX - Comprehensive DCF Valuation Tool")

@app.command()
def analyze(
    ticker: str = typer.Argument(..., help="Stock ticker symbol (e.g., TCS.NS, AAPL)"),
    growth: Optional[float] = typer.Option(None, "--growth", "-g", help="FCF growth rate (as decimal, e.g., 0.10 for 10%)"),
    wacc: Optional[float] = typer.Option(None, "--wacc", "-w", help="WACC/discount rate (as decimal, e.g., 0.09 for 9%)"),
    terminal: Optional[float] = typer.Option(None, "--terminal", "-t", help="Terminal growth rate (as decimal, e.g., 0.03 for 3%)"),
    comprehensive: bool = typer.Option(False, "--comprehensive", "-c", help="Run comprehensive analysis with all methods"),
    export_pdf: bool = typer.Option(False, "--pdf", "-p", help="Export results to PDF report"),
    monte_carlo: bool = typer.Option(False, "--monte-carlo", "-mc", help="Run Monte Carlo simulation"),
    simulations: int = typer.Option(10000, "--simulations", "-s", help="Number of Monte Carlo simulations")
):
    """
    Perform comprehensive equity valuation analysis.
    
    Example:
        valuex analyze AAPL --growth 0.08 --wacc 0.10 --terminal 0.03 --comprehensive --pdf
    """
    
    try:
        with console.status("[bold blue]Initializing analysis...") as status:
            # Input validation and prompts
            ticker = ticker.upper()
            
            # Validate ticker
            status.update("[bold blue]Validating ticker...")
            if not validate_ticker(ticker):
                rprint(f"[bold red]❌ Invalid ticker: {ticker}")
                raise typer.Exit(1)
            
            # Get user inputs if not provided
            if growth is None:
                growth = typer.prompt("FCF Growth Rate (e.g., 0.10 for 10%)", default=DEFAULT_GROWTH, type=float)
            
            if wacc is None:
                wacc = typer.prompt("WACC/Discount Rate (e.g., 0.09 for 9%)", default=DEFAULT_WACC, type=float)
            
            if terminal is None:
                terminal = typer.prompt("Terminal Growth Rate (e.g., 0.03 for 3%)", default=DEFAULT_TERMINAL_GROWTH, type=float)
            
            # Fetch company data
            status.update(f"[bold blue]Fetching financial data for {ticker}...")
            company_data = fetch_financials(ticker)
            
            if 'error' in company_data:
                rprint(f"[bold red]❌ Data fetch error: {company_data['error']}")
                raise typer.Exit(1)
            
            # Display company info
            _display_company_info(company_data)
            
            # Basic DCF Analysis
            status.update("[bold blue]Running DCF analysis...")
            dcf_results = _run_basic_dcf(company_data, growth, wacc, terminal)
            _display_dcf_results(dcf_results, company_data)
            
            # Comprehensive analysis if requested
            if comprehensive:
                status.update("[bold blue]Running comprehensive valuation...")
                comprehensive_results = _run_comprehensive_analysis(company_data, growth, wacc, terminal)
                _display_comprehensive_results(comprehensive_results)
                
                # Risk analysis
                status.update("[bold blue]Performing risk analysis...")
                risk_results = _run_risk_analysis(company_data, growth, wacc, terminal, monte_carlo, simulations)
                _display_risk_results(risk_results)
                
                # AI-powered insights
                status.update("[bold blue]Generating AI insights...")
                _display_ai_insights(growth, wacc, terminal, dcf_results, company_data)
                
                # PDF Export
                if export_pdf:
                    status.update("[bold blue]Generating PDF report...")
                    _export_pdf_report(company_data, comprehensive_results, risk_results)
            
            # Sensitivity analysis
            status.update("[bold blue]Generating sensitivity analysis...")
            _display_sensitivity_analysis(company_data, growth)
            
        rprint("\n[bold green]✅ Analysis completed successfully!")
        
    except KeyboardInterrupt:
        rprint("\n[bold yellow]⚠️ Analysis interrupted by user")
        raise typer.Exit(1)
    except Exception as e:
        rprint(f"\n[bold red]❌ Analysis failed: {str(e)}")
        raise typer.Exit(1)

@app.command()
def quick(ticker: str = typer.Argument(..., help="Stock ticker symbol")):
    """Quick valuation with default parameters."""
    
    with console.status(f"[bold blue]Running quick analysis for {ticker}..."):
        try:
            ticker = ticker.upper()
            company_data = fetch_financials(ticker)
            
            if 'error' in company_data:
                rprint(f"[bold red]❌ Error: {company_data['error']}")
                return
            
            # Use default parameters
            dcf_results = _run_basic_dcf(company_data, DEFAULT_GROWTH, DEFAULT_WACC, DEFAULT_TERMINAL_GROWTH)
            
            # Quick summary
            intrinsic_value = dcf_results.get('intrinsic_value', 0)
            current_price = company_data.get('current_price', 0)
            upside = ((intrinsic_value - current_price) / current_price * 100) if current_price > 0 else 0
            
            # Quick results table
            table = Table(title=f"Quick Valuation: {company_data.get('company_name', ticker)}")
            table.add_column("Metric", style="bold")
            table.add_column("Value", style="cyan")
            
            table.add_row("Current Price", f"₹{current_price:.2f}")
            table.add_row("Intrinsic Value", f"₹{intrinsic_value:.2f}")
            table.add_row("Upside/(Downside)", f"{upside:.1f}%")
            table.add_row("Recommendation", _get_quick_recommendation(upside))
            
            console.print(table)
            
        except Exception as e:
            rprint(f"[bold red]❌ Quick analysis failed: {str(e)}")

@app.command()
def compare(
    tickers: str = typer.Argument(..., help="Comma-separated ticker symbols (e.g., TCS.NS,INFY.NS,WIPRO.NS)"),
    growth: float = typer.Option(DEFAULT_GROWTH, help="Common FCF growth rate"),
    wacc: float = typer.Option(DEFAULT_WACC, help="Common WACC"),
    terminal: float = typer.Option(DEFAULT_TERMINAL_GROWTH, help="Common terminal growth rate")
):
    """Compare multiple stocks using the same parameters."""
    
    ticker_list = [t.strip().upper() for t in tickers.split(',')]
    
    if len(ticker_list) > 10:
        rprint("[bold red]❌ Maximum 10 tickers allowed for comparison")
        return
    
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Analyzing stocks...", total=len(ticker_list))
        
        for ticker in ticker_list:
            progress.update(task, description=f"Analyzing {ticker}...")
            
            try:
                company_data = fetch_financials(ticker)
                if 'error' not in company_data:
                    dcf_results = _run_basic_dcf(company_data, growth, wacc, terminal)
                    
                    results.append({
                        'ticker': ticker,
                        'company_name': company_data.get('company_name', ticker),
                        'current_price': company_data.get('current_price', 0),
                        'intrinsic_value': dcf_results.get('intrinsic_value', 0),
                        'market_cap': company_data.get('market_cap', 0),
                        'pe_ratio': company_data.get('pe_ratio', 0)
                    })
                
            except Exception as e:
                rprint(f"[bold red]❌ Error analyzing {ticker}: {str(e)}")
            
            progress.advance(task)
    
    # Display comparison table
    _display_comparison_results(results)

def _display_company_info(data: dict):
    """Display company information."""
    info_panel = Panel(
        f"""[bold]{data.get('company_name', 'Unknown')}[/bold]
Ticker: {data.get('ticker', 'N/A')} | Sector: {data.get('sector', 'N/A')}
Market Cap: ₹{data.get('market_cap', 0):,.0f} | Beta: {data.get('beta', 0):.2f}
Data Quality: {data.get('data_quality', 'Unknown')}""",
        title="Company Information",
        border_style="blue"
    )
    console.print(info_panel)

def _run_basic_dcf(data: dict, growth: float, wacc: float, terminal: float) -> dict:
    """Run basic DCF analysis."""
    try:
        fcf_proj = project_fcf(data['fcf'], growth)
        dcf_results = calculate_dcf(fcf_proj, wacc, terminal, data['shares_outstanding'])
        
        return {
            'intrinsic_value': dcf_results['intrinsic_value'],
            'enterprise_value': dcf_results['enterprise_value'],
            'projected_fcf': fcf_proj,
            'discounted_fcf': dcf_results['discounted_fcf'],
            'terminal_value': dcf_results.get('terminal_value', 0),
            'assumptions': {
                'growth': growth,
                'wacc': wacc,
                'terminal': terminal
            }
        }
    except Exception as e:
        return {'error': str(e)}

def _display_dcf_results(dcf_results: dict, company_data: dict):
    """Display DCF analysis results."""
    if 'error' in dcf_results:
        rprint(f"[bold red]❌ DCF Error: {dcf_results['error']}")
        return
    
    # Main results table
    table = Table(title="DCF Valuation Results")
    table.add_column("Metric", style="bold")
    table.add_column("Value", style="green")
    
    current_price = company_data.get('current_price', 0)
    intrinsic_value = dcf_results['intrinsic_value']
    upside = ((intrinsic_value - current_price) / current_price * 100) if current_price > 0 else 0
    
    table.add_row("Enterprise Value", f"₹{dcf_results['enterprise_value']:,.0f}")
    table.add_row("Intrinsic Value per Share", f"₹{intrinsic_value:.2f}")
    table.add_row("Current Market Price", f"₹{current_price:.2f}")
    table.add_row("Upside/(Downside)", f"{upside:.1f}%")
    table.add_row("Terminal Value", f"₹{dcf_results.get('terminal_value', 0):,.0f}")
    
    console.print(table)
    
    # Assumptions table
    assumptions = dcf_results['assumptions']
    assumption_table = Table(title="Key Assumptions")
    assumption_table.add_column("Parameter", style="bold")
    assumption_table.add_column("Value", style="cyan")
    
    assumption_table.add_row("FCF Growth Rate", f"{assumptions['growth']*100:.1f}%")
    assumption_table.add_row("WACC", f"{assumptions['wacc']*100:.1f}%")
    assumption_table.add_row("Terminal Growth", f"{assumptions['terminal']*100:.1f}%")
    
    console.print(assumption_table)

def _run_comprehensive_analysis(data: dict, growth: float, wacc: float, terminal: float) -> dict:
    """Run comprehensive valuation analysis."""
    try:
        valuation_suite = ValuationSuite(data)
        
        dcf_params = {
            'growth_rate': growth,
            'wacc': wacc,
            'terminal_growth': terminal
        }
        
        return valuation_suite.comprehensive_valuation(dcf_params)
        
    except Exception as e:
        return {'error': str(e)}

def _display_comprehensive_results(results: dict):
    """Display comprehensive valuation results."""
    if 'error' in results:
        rprint(f"[bold red]❌ Comprehensive Analysis Error: {results['error']}")
        return
    
    # Summary table
    summary = results.get('summary', {})
    
    if 'error' not in summary:
        summary_table = Table(title="Comprehensive Valuation Summary")
        summary_table.add_column("Method", style="bold")
        summary_table.add_column("Value", style="green")
        
        for method, value in summary.get('valuations', []):
            summary_table.add_row(method, f"₹{value:.2f}")
        
        summary_table.add_row("Average", f"₹{summary.get('average_intrinsic_value', 0):.2f}")
        summary_table.add_row("Recommendation", summary.get('recommendation', 'N/A'))
        summary_table.add_row("Confidence", summary.get('confidence', 'Unknown'))
        
        console.print(summary_table)

def _run_risk_analysis(data: dict, growth: float, wacc: float, terminal: float, 
                      monte_carlo: bool, simulations: int) -> dict:
    """Run risk analysis."""
    try:
        risk_analyzer = RiskAnalyzer(data)
        results = {}
        
        # Basic risk metrics
        results['risk_metrics'] = risk_analyzer.risk_metrics()
        
        # Scenario analysis
        base_params = {'growth': growth, 'wacc': wacc, 'terminal': terminal}
        results['scenario_analysis'] = risk_analyzer.scenario_analysis(base_params)
        
        # Stress testing
        results['stress_testing'] = risk_analyzer.stress_testing(base_params)
        
        # Monte Carlo if requested
        if monte_carlo:
            mc_params = {
                'growth_params': {'mean': growth, 'std': 0.02},
                'wacc_params': {'mean': wacc, 'std': 0.01},
                'terminal_params': {'mean': terminal, 'std': 0.005}
            }
            results['monte_carlo'] = risk_analyzer.monte_carlo_simulation(
                data['fcf'], mc_params['growth_params'], 
                mc_params['wacc_params'], mc_params['terminal_params'], 
                simulations
            )
        
        return results
        
    except Exception as e:
        return {'error': str(e)}

def _display_risk_results(results: dict):
    """Display risk analysis results."""
    if 'error' in results:
        rprint(f"[bold red]❌ Risk Analysis Error: {results['error']}")
        return
    
    # Risk metrics
    risk_metrics = results.get('risk_metrics', {})
    if 'error' not in risk_metrics:
        risk_table = Table(title="Risk Metrics")
        risk_table.add_column("Metric", style="bold")
        risk_table.add_column("Value", style="yellow")
        
        risk_table.add_row("Volatility", f"{risk_metrics.get('volatility', 0)*100:.1f}%")
        risk_table.add_row("Beta", f"{risk_metrics.get('beta', 0):.2f}")
        risk_table.add_row("VaR (95%)", f"₹{risk_metrics.get('var_95', 0):.2f}")
        risk_table.add_row("Risk Level", risk_metrics.get('risk_level', 'Unknown'))
        
        console.print(risk_table)
    
    # Scenario analysis
    scenario_analysis = results.get('scenario_analysis', {})
    if 'error' not in scenario_analysis:
        scenario_table = Table(title="Scenario Analysis")
        scenario_table.add_column("Scenario", style="bold")
        scenario_table.add_column("Intrinsic Value", style="cyan")
        
        scenarios = scenario_analysis.get('scenarios', {})
        for scenario_name, scenario_data in scenarios.items():
            if 'error' not in scenario_data:
                scenario_table.add_row(
                    scenario_name.title(),
                    f"₹{scenario_data.get('intrinsic_value', 0):.2f}"
                )
        
        console.print(scenario_table)
    
    # Monte Carlo results if available
    monte_carlo = results.get('monte_carlo', {})
    if 'error' not in monte_carlo and monte_carlo:
        mc_table = Table(title="Monte Carlo Simulation Results")
        mc_table.add_column("Statistic", style="bold")
        mc_table.add_column("Value", style="magenta")
        
        mc_table.add_row("Mean Value", f"₹{monte_carlo.get('mean_value', 0):.2f}")
        mc_table.add_row("Median Value", f"₹{monte_carlo.get('median_value', 0):.2f}")
        mc_table.add_row("Standard Deviation", f"₹{monte_carlo.get('std_dev', 0):.2f}")
        mc_table.add_row("5th Percentile", f"₹{monte_carlo.get('percentiles', {}).get('5th', 0):.2f}")
        mc_table.add_row("95th Percentile", f"₹{monte_carlo.get('percentiles', {}).get('95th', 0):.2f}")
        
        console.print(mc_table)

def _display_ai_insights(growth: float, wacc: float, terminal: float, dcf_results: dict, company_data: dict):
    """Display AI-powered insights."""
    try:
        # Assumption explanation
        explanation = explain_assumptions(growth, wacc, terminal)
        explanation_panel = Panel(
            explanation,
            title="🧠 AI Assumption Analysis",
            border_style="cyan"
        )
        console.print(explanation_panel)
        
        # Investment report
        current_price = company_data.get('current_price', 0)
        intrinsic_value = dcf_results.get('intrinsic_value', 0)
        discount = ((intrinsic_value - current_price) / current_price * 100) if current_price > 0 else 0
        
        report = generate_report(
            company=company_data.get('ticker', 'Unknown'),
            intrinsic_value=intrinsic_value,
            market_price=current_price,
            discount=discount,
            assumptions={'growth': growth, 'wacc': wacc, 'terminal': terminal}
        )
        
        report_panel = Panel(
            report,
            title="📄 AI Investment Report",
            border_style="green"
        )
        console.print(report_panel)
        
    except Exception as e:
        rprint(f"[bold red]❌ AI Insights Error: {str(e)}")

def _display_sensitivity_analysis(data: dict, growth: float):
    """Display sensitivity analysis."""
    try:
        matrix = generate_sensitivity_matrix(
            data['fcf'], data['shares_outstanding'], growth,
            WACC_RANGE, TERMINAL_GROWTH_RANGE
        )
        
        # Create sensitivity table
        sens_table = Table(title="Sensitivity Analysis (Intrinsic Value)")
        sens_table.add_column("WACC\\Terminal Growth", style="bold")
        
        # Add column headers
        for tg in TERMINAL_GROWTH_RANGE:
            sens_table.add_column(f"{tg*100:.1f}%", style="cyan")
        
        # Add rows
        for wacc_pct, values in matrix.items():
            row = [f"{wacc_pct}%"] + [f"₹{v:.2f}" if v else "N/A" for v in values]
            sens_table.add_row(*row)
        
        console.print(sens_table)
        
    except Exception as e:
        rprint(f"[bold red]❌ Sensitivity Analysis Error: {str(e)}")

def _display_comparison_results(results: list):
    """Display stock comparison results."""
    if not results:
        rprint("[bold red]❌ No valid results for comparison")
        return
    
    comparison_table = Table(title="Stock Comparison")
    comparison_table.add_column("Ticker", style="bold")
    comparison_table.add_column("Company", style="cyan")
    comparison_table.add_column("Current Price", style="green")
    comparison_table.add_column("Intrinsic Value", style="green")
    comparison_table.add_column("Upside", style="yellow")
    comparison_table.add_column("Market Cap", style="blue")
    
    for result in results:
        current_price = result['current_price']
        intrinsic_value = result['intrinsic_value']
        upside = ((intrinsic_value - current_price) / current_price * 100) if current_price > 0 else 0
        
        comparison_table.add_row(
            result['ticker'],
            result['company_name'][:20] + "..." if len(result['company_name']) > 20 else result['company_name'],
            f"₹{current_price:.2f}",
            f"₹{intrinsic_value:.2f}",
            f"{upside:.1f}%",
            f"₹{result['market_cap']:,.0f}"
        )
    
    console.print(comparison_table)

def _export_pdf_report(company_data: dict, valuation_results: dict, risk_results: dict):
    """Export comprehensive PDF report."""
    try:
        from utils.pdf_generator import ValuationReportPDF
        
        pdf_generator = ValuationReportPDF()
        output_path = pdf_generator.generate_comprehensive_report(
            company_data, valuation_results, risk_results
        )
        
        if "Error" not in output_path:
            if output_path.endswith('.pdf'):
                rprint(f"[bold green]✅ PDF report exported: {output_path}")
            else:
                rprint(f"[bold yellow]📄 Text report exported: {output_path}")
                rprint("[dim]Note: PDF generation requires fpdf2. Install with: pip install fpdf2")
        else:
            rprint(f"[bold red]❌ Report export failed: {output_path}")
            
    except Exception as e:
        rprint(f"[bold red]❌ Report Export Error: {str(e)}")
        rprint("[dim]Try: pip install fpdf2")

def _get_quick_recommendation(upside: float) -> str:
    """Get quick recommendation based on upside."""
    if upside > 20:
        return "[bold green]Strong Buy[/bold green]"
    elif upside > 10:
        return "[green]Buy[/green]"
    elif upside > -10:
        return "[yellow]Hold[/yellow]"
    elif upside > -20:
        return "[red]Sell[/red]"
    else:
        return "[bold red]Strong Sell[/bold red]"

if __name__ == "__main__":
    app()
