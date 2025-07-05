import matplotlib.pyplot as plt
import matplotlib
import os

def plot_fcf_projection(fcf_list):
    """
    Plots the projected Free Cash Flows over 5 years.
    """
    try:
        if not fcf_list or len(fcf_list) == 0:
            raise ValueError("No FCF data to plot")
        
        # Set backend for non-interactive environments
        if 'DISPLAY' not in os.environ or os.environ['DISPLAY'] == '':
            matplotlib.use('Agg')
        
        years = [f"Year {i+1}" for i in range(len(fcf_list))]

        plt.figure(figsize=(10, 5))
        plt.plot(years, fcf_list, marker='o', linestyle='-', color='blue', label='Projected FCF')
        plt.fill_between(years, fcf_list, alpha=0.1, color='blue')
        
        # Remove emoji from title to avoid font issues
        plt.title("Projected Free Cash Flow (5-Year Forecast)", fontsize=14)
        plt.xlabel("Future Years")
        plt.ylabel("FCF (₹ Crores)")
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend()
        plt.tight_layout()
        
        # Save chart instead of showing in non-interactive environments
        try:
            plt.show()
        except:
            # Save to file if display is not available
            import os
            charts_dir = "charts"
            if not os.path.exists(charts_dir):
                os.makedirs(charts_dir)
            
            chart_path = os.path.join(charts_dir, "fcf_projection.png")
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            print(f"Chart saved as: {chart_path}")
            plt.close()
        
    except Exception as e:
        print(f"Error plotting FCF projection: {e}")
        # Return a simple text representation if plotting fails
        return f"FCF Projection: {fcf_list}"
