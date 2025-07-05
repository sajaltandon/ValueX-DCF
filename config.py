# ========================
# 📁 ValueX Configuration
# ========================

# Default projection settings
DEFAULT_YEARS = 5
DEFAULT_GROWTH = 0.10           # 10% annual FCF growth
DEFAULT_WACC = 0.10             # 10% discount rate
DEFAULT_TERMINAL_GROWTH = 0.03  # 3% terminal growth

# Sensitivity grid settings
WACC_RANGE = [x / 100 for x in range(8, 13)]  # 8% to 12%
TERMINAL_GROWTH_RANGE = [x / 100 for x in range(2, 6)]  # 2% to 5%

# Chart settings
CHART_COLORS = {
    "fcf": "blue",
    "intrinsic": "green",
    "market": "red"
}

# Safe fallback for missing data
MINIMUM_SHARES = 1

# Gemini / LLM
EXPLAINER_MODEL = "gemini-1.5-pro"
REPORT_MODEL = "gemini-1.5-pro"

# Project meta
APP_NAME = "ValueX"
VERSION = "1.0"
