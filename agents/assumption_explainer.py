import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key from .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_available_gemini_model():
    try:
        models = genai.list_models()
        # Prefer pro/flash models
        for preferred in ['gemini-1.5-pro', 'gemini-1.5-flash']:
            for m in models:
                if preferred in m.name:
                    return m.name
        # Fallback: return first model
        if models:
            return models[0].name
    except Exception as e:
        pass
    return None

def explain_assumptions(growth, wacc, terminal_growth):
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            return "⚠️ Gemini API key not configured. Please set GEMINI_API_KEY in your .env file."

        prompt = f"""
        Please explain the following financial valuation assumptions as if you're an equity research analyst:

        - Free Cash Flow (FCF) Growth Rate: {growth*100:.2f}%
        - Weighted Average Cost of Capital (WACC): {wacc*100:.2f}%
        - Terminal Growth Rate: {terminal_growth*100:.2f}%

        Comment on whether these values are aggressive, conservative, or balanced, and how they might impact the DCF valuation.
        """
        # Try preferred models first
        model_names = ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-pro']
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                return response.text.strip()
            except Exception:
                continue
        # Try to auto-detect available model
        auto_model = get_available_gemini_model()
        if auto_model:
            try:
                model = genai.GenerativeModel(auto_model)
                response = model.generate_content(prompt)
                return response.text.strip()
            except Exception:
                pass
        # Fallback: manual explanation
        return f"""
        Manual Assumption Analysis:\n\n- FCF Growth Rate: {growth*100:.2f}% - This is {'aggressive' if growth > 0.15 else 'conservative' if growth < 0.05 else 'reasonable'} for most companies\n- WACC: {wacc*100:.2f}% - This discount rate is {'high' if wacc > 0.15 else 'low' if wacc < 0.08 else 'reasonable'}\n- Terminal Growth: {terminal_growth*100:.2f}% - This long-term growth rate is {'optimistic' if terminal_growth > 0.05 else 'conservative' if terminal_growth < 0.02 else 'realistic'}\n\nNote: AI analysis unavailable due to API issues. Please verify these assumptions against industry benchmarks.\n"""
    except Exception as e:
        return f"⚠️ Could not generate AI explanation: {str(e)}"
