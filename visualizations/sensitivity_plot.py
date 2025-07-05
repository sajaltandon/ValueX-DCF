import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
import os

def plot_sensitivity(matrix, terminal_growth_range):
    """
    Visualizes the sensitivity matrix as a heatmap (WACC vs Terminal Growth).
    """
    try:
        if not matrix or not terminal_growth_range:
            raise ValueError("No sensitivity data to plot")
        
        # Set backend for non-interactive environments
        if 'DISPLAY' not in os.environ or os.environ['DISPLAY'] == '':
            matplotlib.use('Agg')
        
        tg_labels = [f"{x*100:.1f}%" for x in terminal_growth_range]
        df = pd.DataFrame(matrix, index=tg_labels).T
        plt.figure(figsize=(10, 6))
        sns.heatmap(df, annot=True, fmt=".2f", cmap="YlOrRd", linewidths=0.5)
        plt.title("DCF Sensitivity: Intrinsic Value vs WACC & Terminal Growth")
        plt.xlabel("Terminal Growth Rate (%)")
        plt.ylabel("WACC (%)")
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
            
            chart_path = os.path.join(charts_dir, "sensitivity_matrix.png")
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            print(f"Sensitivity chart saved as: {chart_path}")
            plt.close()
        
    except Exception as e:
        print(f"Error plotting sensitivity matrix: {e}")
        return f"Sensitivity Matrix: {matrix}"
