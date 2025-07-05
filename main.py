import typer
import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from interface.cli import app as cli_app

console = Console()

def main():
    """
    Main entry point for ValueX - DCF Valuation Tool.
    Launches ValueX in CLI or Streamlit UI mode based on user input.
    """
    
    # Welcome message
    welcome_panel = Panel(
        """[bold blue]� Welcome to ValueX - Intelligent DCF Valuation Tool[/bold blue]

[cyan]Features:[/cyan]
• Comprehensive DCF Analysis with multiple valuation methods
• AI-powered assumption validation and report generation  
• Risk analysis with Monte Carlo simulation and stress testing
• Sensitivity analysis and scenario modeling
• Professional PDF report generation
• Stock comparison and benchmarking

[yellow]Available Commands:[/yellow]
• [bold]analyze[/bold] - Full comprehensive analysis
• [bold]quick[/bold] - Quick valuation with defaults  
• [bold]compare[/bold] - Compare multiple stocks

[green]Example Usage:[/green]
valuex analyze AAPL --growth 0.08 --wacc 0.10 --terminal 0.03 --comprehensive --pdf
        """,
        title="ValueX v1.0",
        border_style="blue"
    )
    
    console.print(welcome_panel)
    
    # Ask for mode selection
    while True:
        mode = typer.prompt(
            "\nChoose mode [cli/ui/help]", 
            default="cli"
        ).strip().lower()
        
        if mode in ["cli", "ui", "help"]:
            break
        else:
            rprint(f"[bold red]❌ Invalid choice: {mode}[/bold red]")
            rprint("[yellow]Please choose: cli, ui, or help[/yellow]")

    if mode == "cli":
        rprint("[bold blue]🧠 Launching CLI Mode...[/bold blue]")
        rprint("Use 'python main.py --help' or add arguments directly")
        rprint("Example: python -m interface.cli analyze AAPL --comprehensive")
        
        # Check if arguments were provided
        if len(sys.argv) > 1:
            # Arguments provided, run CLI directly
            cli_app()
        else:
            # No arguments, show help
            rprint("\n[yellow]No command specified. Use --help to see available commands.[/yellow]")
            rprint("[cyan]Quick start: Try 'python -m interface.cli quick AAPL'[/cyan]")
            
    elif mode == "ui":
        rprint("[bold blue]🚀 Launching Streamlit UI...[/bold blue]")
        try:
            os.system("streamlit run interface/streamlit_ui.py")
        except Exception as e:
            rprint(f"[bold red]❌ Failed to launch Streamlit: {e}[/bold red]")
            rprint("[yellow]Make sure Streamlit is installed: pip install streamlit[/yellow]")
            
    elif mode == "help":
        rprint("\n[bold cyan]ValueX Help & Documentation[/bold cyan]")
        help_text = """
[bold]Command Line Usage:[/bold]

1. [green]Quick Analysis:[/green]
   python -m interface.cli quick AAPL
   
2. [green]Comprehensive Analysis:[/green]
   python -m interface.cli analyze AAPL --growth 0.08 --wacc 0.10 --terminal 0.03 --comprehensive --pdf
   
3. [green]Stock Comparison:[/green]
   python -m interface.cli compare "AAPL,MSFT,GOOGL" --growth 0.07
   
4. [green]Monte Carlo Simulation:[/green]
   python -m interface.cli analyze AAPL --monte-carlo --simulations 10000

[bold]Parameters:[/bold]
• --growth: FCF growth rate (decimal, e.g., 0.10 for 10%)
• --wacc: Weighted Average Cost of Capital (decimal)
• --terminal: Terminal growth rate (decimal)
• --comprehensive: Run all valuation methods
• --pdf: Export results to PDF
• --monte-carlo: Run Monte Carlo simulation

[bold]Streamlit UI:[/bold]
Run 'python main.py' and select 'ui' for interactive web interface.

[bold]Configuration:[/bold]
• Set GEMINI_API_KEY in .env file for AI features
• Modify config.py for default parameters
• Check requirements.txt for dependencies
        """
        console.print(Panel(help_text, title="Help & Documentation", border_style="cyan"))
        
    else:
        rprint(f"[bold red]❌ Invalid mode selected: {mode}[/bold red]")
        rprint("[yellow]Please choose 'cli', 'ui', or 'help'[/yellow]")
        sys.exit(1)

if __name__ == "__main__":
    # Check if command line arguments are provided
    if len(sys.argv) > 1:
        # Direct CLI execution with arguments
        cli_app()
    else:
        # Interactive mode selection
        main()
