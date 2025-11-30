import pandas as pd
import json

def search_kb(query):
    """Search knowledge base (mock FAQ)"""
    faq_data = {
        "reset password": "To reset your password, click 'Forgot Password' on login screen and follow email instructions.",
        "payment failed": "Payment failures occur due to: 1) Card expired 2) Insufficient funds 3) Bank blocks. Try different card or contact bank.",
        "order status": "Check order status in your account dashboard or use tracking link in confirmation email.",
        "app crash": "Clear app cache, update to latest version, or contact support with device details."
    }
    
    for keyword, answer in faq_data.items():
        if keyword in query.lower():
            return {"answer": answer, "confidence": 0.9}
    return {"answer": "No matching FAQ found", "confidence": 0.3}

def get_customer_profile(customer_id):
    """Get customer profile"""
    df = pd.read_csv('data/customer_profiles.csv')
    profile = df[df['customer_id'] == int(customer_id)].iloc[0].to_dict()
    return profile
