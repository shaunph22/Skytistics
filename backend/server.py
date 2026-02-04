import os
from flask import Flask, jsonify, request
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from the hidden .env file
env_path = Path(__file__).parent / '.env'
file_exists = env_path.exists()
env_loaded = load_dotenv(dotenv_path=env_path)

print("\n=== SKYTISTICS BACKEND DEBUGGING ===")
print(f"Current Working Directory: {os.getcwd()}")
print(f"Does .env file physically exist where expected? {file_exists}")
print(f"Did load_dotenv() successfully read the file? {env_loaded}")
print(f"Raw Key extracted from environment: {os.getenv('FLIGHTAWARE_KEY')}")
print("========================================\n")

app = Flask(__name__)

# Retrieve the API key securely from the environment
AEROAPI_KEY = os.getenv("FLIGHTAWARE_KEY")
AEROAPI_BASE_URL = "https://aeroapi.flightaware.com/aeroapi"

# Helper to inject our required FlightAware authorization headers
headers = {
    "x-apikey": AEROAPI_KEY
}

@app.route("/api/flight/<flight_number>", methods=["GET"])
def get_flight(flight_number):
    """
    FlightView Endpoint: Fetches data for a specific flight identifier (e.g., SQ37)
    """
    if not AEROAPI_KEY:
        return jsonify({"error": "API Key is missing from backend configuration"}), 500
        
    url = f"{AEROAPI_BASE_URL}/flights/{flight_number}"
    
    try:
        response = requests.get(url, headers=headers)
        # If FlightAware gives an error (like a bad flight number), forward that status code
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch from FlightAware", "details": response.text}), response.status_code
            
        return jsonify(response.json())
        
    except Exception as e:
        return jsonify({"error": "Internal backend error", "message": str(e)}), 500


@app.route("/api/airport/<airport_code>", methods=["GET"])
def get_airport_board(airport_code):
    url = f"{AEROAPI_BASE_URL}/airports/{airport_code}/flights"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch airport data", "details": response.text}), response.status_code
            
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": "Internal backend error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)