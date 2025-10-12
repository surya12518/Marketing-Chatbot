import streamlit as st
import requests
import json

st.title("Streamlit integration with n8n")

user_input = st.text_input("Enter some text:")
if st.button("Send to n8n"):
    if user_input:
        webhook_url = "https://ruinous-gussie-deeper.ngrok-free.dev/webhook/streamlit-input"

        data = {"text": user_input}

        # Try sending as raw text instead of JSONs
        try:
            response = requests.post(webhook_url, json=data)
            if response.status_code == 200:
                st.success("Data sent successfully!")
                st.json(response.json())
            else:
                st.error(f"Failed to send data. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred: {e}")