import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key from .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_available_gemini_model():
    try:
        models = genai.list_models()
        for preferred in ['gemini-1.5-pro', 'gemini-1.5-flash']:
            for m in models:
                if preferred in m.name:
                    return m.name
        if models:
            return models[0].name
    except Exception as e:
        pass
    return None

def generate_report(company, intrinsic_value, market_price, discount, assumptions):
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            return "⚠️ Gemini API key not configured. Please set GEMINI_API_KEY in your .env file."

        prompt = f"""
        You are a financial analyst writing a valuation summary for {company}. Based on a DCF analysis, here are the details:

        - Intrinsic Value per Share: ₹{intrinsic_value:.2f}
        - Current Market Price: ₹{market_price:.2f}
        - Estimated Discount: {discount:.2f}%
        - Assumptions Used:
          - Free Cash Flow Growth Rate: {assumptions['growth']*100:.2f}%
          - WACC: {assumptions['wacc']*100:.2f}%
          - Terminal Growth Rate: {assumptions['terminal']*100:.2f}%

        Write a 2-paragraph professional report summarizing the valuation outcome, the reasoning behind the assumptions, and whether the stock is undervalued or overvalued.
        """
        model_names = ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-pro']
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                return response.text.strip()
            except Exception:
                continue
        auto_model = get_available_gemini_model()
        if auto_model:
            try:
                model = genai.GenerativeModel(auto_model)
                response = model.generate_content(prompt)
                return response.text.strip()
            except Exception:
                pass
        upside_downside = "undervalued" if discount > 0 else "overvalued" if discount < 0 else "fairly valued"
        return f"""
        Manual Investment Summary for {company}:
        
        Based on our DCF analysis, {company} has an intrinsic value of ₹{intrinsic_value:.2f} per share, 
        compared to the current market price of ₹{market_price:.2f}. This suggests the stock is {upside_downside} 
        by {abs(discount):.1f}%.
        
        Key assumptions used: {assumptions['growth']*100:.1f}% FCF growth, {assumptions['wacc']*100:.1f}% WACC, 
        and {assumptions['terminal']*100:.1f}% terminal growth. These parameters appear reasonable for a 
        company of this size and sector.
        
        Note: AI-generated report unavailable due to API issues. Please conduct additional research before making investment decisions.
        """
    except Exception as e:
        return f"⚠️ Could not generate AI report: {str(e)}"
