import streamlit as st
import google.generativeai as genai
import os

# 🔐 API Key Configuration
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDCZMHfKGZNyA-EmUzcBvTmqHvjSsv2hNQ")
genai.configure(api_key=API_KEY)

def generate_prompt_response(prompt):
    """Fetches AI-generated response from Google Gemini API."""
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(prompt)
        return response.text.strip() if response.text else "No response generated."
    except Exception as e:
        return f"🚨 Error: Unable to fetch response. Please try again later.\n\n**Details:** {str(e)}"

