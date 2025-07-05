
# 💼 ValueX: Intelligent DCF-Based Equity Valuation Tool

**ValueX** is a comprehensive, production-ready Python application for equity valuation that combines traditional DCF modeling with modern AI-powered insights. Designed for investment analysts, finance students, and algorithmic traders, it provides enterprise-grade valuation capabilities with multiple methodologies, advanced risk analysis, and professional reporting.

---

## 🌟 Key Features

### 📊 **Comprehensive Valuation Methods**
- **DCF Analysis**: 5-year FCF projections with terminal value calculations
- **Relative Valuation**: P/E, EV/EBITDA, P/S ratio analysis
- **Dividend Discount Model**: Gordon Growth Model implementation
- **Asset-Based Valuation**: Book value and liquidation estimates

### 🤖 **AI-Powered Intelligence**
- **Assumption Validation**: AI analysis of growth rates, WACC, and terminal values
- **Investment Reports**: Professional AI-generated valuation summaries
- **Risk Assessment**: Intelligent risk factor identification
- **Market Context**: Sector and industry-specific insights

### 📈 **Advanced Risk Analytics**
- **Monte Carlo Simulation**: Parameter uncertainty modeling (10,000+ simulations)
- **Scenario Analysis**: Bear, base, and bull case projections
- **Stress Testing**: Recession, inflation, and market crash scenarios  
- **Sensitivity Analysis**: WACC and growth rate sensitivity matrices
- **VaR Calculations**: Value-at-Risk metrics with confidence intervals

### 📋 **Professional Reporting**
- **PDF Reports**: Comprehensive 15+ page professional reports
- **Executive Summaries**: Key metrics and recommendations
- **Risk Dashboards**: Visual risk assessment and factor analysis
- **Comparison Tables**: Multi-stock comparative analysis

### 🖥️ **Multiple Interfaces**
- **Enhanced CLI**: Rich terminal interface with progress bars and tables
- **Streamlit Dashboard**: Interactive web-based interface
- **Batch Processing**: Compare multiple stocks simultaneously
- **API Integration**: Programmatic access for automated workflows

---

## 🏗️ **Enhanced Architecture**

```
ValueX/
├── 📊 models/
│   ├── dcf_model.py              # Enhanced DCF with validation & logging
│   ├── valuation_methods.py     # Multi-method valuation suite  
│   ├── risk_analysis.py         # Monte Carlo & scenario analysis
│   └── sensitivity_analysis.py  # Parameter sensitivity modeling
├── 🔧 utils/
│   ├── data_collection.py       # Robust data fetching & validation
│   ├── preprocess.py           # Data cleaning & quality assessment
│   └── pdf_generator.py        # Professional PDF report generation
├── 🤖 agents/
│   ├── assumption_explainer.py  # AI assumption validation
│   └── report_generator.py     # AI investment report generation
├── 📊 visualizations/
│   ├── valuation_chart.py      # FCF projection & value charts
│   └── sensitivity_plot.py     # Risk heatmaps & sensitivity plots
├── 🖥️ interface/
│   ├── cli.py                  # Enhanced CLI with Rich formatting
│   └── streamlit_ui.py         # Interactive web dashboard
├── 🧪 tests/
│   └── test_valuex.py          # Comprehensive test suite
├── 📁 data/
│   ├── example_fcf_data.csv    # Sample financial data
│   └── cache/                  # Cached API responses
├── 📄 reports/                 # Generated PDF reports
├── 📋 config.py               # Configuration & constants
├── 🚀 main.py                 # Enhanced entry point
├── ⚙️ setup.py                # Automated setup script
├── 📦 requirements.txt        # Complete dependency list
└── 📖 README.md              # This comprehensive guide
```

---

## ⚡ **Quick Installation**

### **Option 1: Automated Setup (Recommended)**
```bash
# Clone the repository
git clone https://github.com/yourusername/valuex.git
cd valuex

# Run automated setup
python setup.py
```

### **Option 2: Manual Installation**
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your Gemini API key

# Test installation
python tests/test_valuex.py
```

---

## 🚀 **Usage Examples**

### **1. Quick Analysis**
```bash
# Basic quick valuation
python -m interface.cli quick AAPL

# Interactive mode
python main.py
```

### **2. Comprehensive Analysis**
```bash
# Full analysis with PDF export
python -m interface.cli analyze AAPL \
  --growth 0.08 \
  --wacc 0.10 \
  --terminal 0.03 \
  --comprehensive \
  --pdf

# With Monte Carlo simulation
python -m interface.cli analyze MSFT \
  --comprehensive \
  --monte-carlo \
  --simulations 10000
```

### **3. Stock Comparison**
```bash
# Compare multiple stocks
python -m interface.cli compare "AAPL,MSFT,GOOGL" \
  --growth 0.07 \
  --wacc 0.09
```

### **4. Streamlit Web Interface**
```bash
# Launch interactive dashboard
python main.py
# Select 'ui' option
```

---

## 📊 **Advanced Features**

### **Monte Carlo Simulation**
```python
from models.risk_analysis import RiskAnalyzer

risk_analyzer = RiskAnalyzer(company_data)
mc_results = risk_analyzer.monte_carlo_simulation(
    base_fcf=100000,
    growth_params={'mean': 0.10, 'std': 0.02},
    wacc_params={'mean': 0.12, 'std': 0.01},
    terminal_params={'mean': 0.03, 'std': 0.005},
    simulations=10000
)
```

### **Comprehensive Valuation**
```python
from models.valuation_methods import ValuationSuite

valuation_suite = ValuationSuite(company_data)
results = valuation_suite.comprehensive_valuation({
    'growth_rate': 0.10,
    'wacc': 0.12,
    'terminal_growth': 0.03
})
```

### **PDF Report Generation**
```python
from utils.pdf_generator import ValuationReportPDF

pdf_generator = ValuationReportPDF()
report_path = pdf_generator.generate_comprehensive_report(
    company_data, valuation_results, risk_analysis
)
```

---

## 🔧 **Configuration**

### **Environment Variables (.env)**
```bash
# Gemini AI API Key (Required for AI features)
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: OpenAI API Key
OPENAI_API_KEY=your_openai_key_here

# Default Parameters
DEFAULT_WACC=0.10
DEFAULT_GROWTH=0.08
DEFAULT_TERMINAL=0.03
```

### **Configuration (config.py)**
```python
# Valuation parameters
DEFAULT_YEARS = 5
DEFAULT_GROWTH = 0.10
DEFAULT_WACC = 0.10
DEFAULT_TERMINAL_GROWTH = 0.03

# Sensitivity analysis ranges  
WACC_RANGE = [x / 100 for x in range(8, 13)]
TERMINAL_GROWTH_RANGE = [x / 100 for x in range(2, 6)]

# AI model settings
EXPLAINER_MODEL = "gemini-pro"
REPORT_MODEL = "gemini-pro"
```

---

## 📈 **Output Examples**

### **CLI Output**
```
💼 ValueX - Comprehensive DCF Valuation Tool

Company Information
┌─────────────────────────────────────────────────┐
│ Apple Inc                                       │
│ Ticker: AAPL | Sector: Technology               │
│ Market Cap: ₹2,950,000,000,000 | Beta: 1.25     │
│ Data Quality: Good                              │
└─────────────────────────────────────────────────┘

DCF Valuation Results
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric                  ┃ Value                   ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Intrinsic Value        │ ₹195.50                │
│ Current Price          │ ₹185.00                │
│ Upside                 │ 5.7%                   │
│ Recommendation         │ Buy                    │
└─────────────────────────┴─────────────────────────┘
```

### **PDF Report Structure**
1. **Executive Summary** - Key metrics and recommendation
2. **Company Overview** - Business and financial highlights  
3. **Valuation Methodology** - Approach and framework
4. **DCF Analysis** - Detailed cash flow projections
5. **Relative Valuation** - Peer comparison analysis
6. **Risk Analysis** - Risk metrics and stress testing
7. **Scenario Analysis** - Bear, base, bull projections
8. **Investment Recommendation** - Final assessment
9. **Appendices** - Data sources and limitations

---

## 🧪 **Testing & Quality Assurance**

### **Run Test Suite**
```bash
# Complete test suite
python tests/test_valuex.py

# Individual components
python -m pytest tests/ -v

# Performance benchmarks
python tests/test_valuex.py --performance
```

### **Test Coverage**
- ✅ **DCF Model**: Projection accuracy, edge cases, validation
- ✅ **Data Collection**: API reliability, error handling, data quality
- ✅ **Risk Analysis**: Monte Carlo convergence, scenario consistency
- ✅ **Valuation Methods**: Cross-method validation, outlier detection
- ✅ **Integration**: End-to-end workflows, error propagation

---

## 🔒 **Security & Best Practices**

### **API Key Management**
- Store API keys in `.env` file (never commit to version control)
- Use environment variables for production deployment
- Implement API rate limiting and error handling

### **Data Validation**
- Input sanitization and range validation
- Financial data consistency checks  
- Error handling with graceful degradation

### **Performance Optimization**
- Caching for repeated API calls
- Efficient numerical computations
- Memory-optimized data structures

---

## 📚 **Dependencies**

### **Core Financial**
- `yfinance==0.2.28` - Financial data API
- `pandas==2.1.4` - Data manipulation
- `numpy==1.25.2` - Numerical computing
- `scipy==1.11.4` - Statistical functions

### **Visualization & UI**
- `matplotlib==3.8.2` - Plotting and charts
- `seaborn==0.13.0` - Statistical visualization
- `streamlit==1.29.0` - Web dashboard
- `rich==13.7.0` - CLI formatting

### **AI & ML**
- `google-generativeai==0.3.2` - Gemini AI integration
- `openai==1.6.1` - OpenAI API (optional)

### **Reporting & Export**
- `fpdf2==2.7.6` - PDF generation
- `openpyxl==3.1.2` - Excel export

---

### **Development Setup**
```bash
# Clone and setup development environment
git clone https://github.com/sajaltandon/ValueX-DCF
cd valuex
python setup.py

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests before committing
python tests/test_valuex.py
```
