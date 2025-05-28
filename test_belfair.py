print("=== Acumidata API Test for Redondo Beach Property Valuation (GET) ===")

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API details
base_url = "https://api.acumidata.com"  # Production URL
api_key = os.getenv("ACUMIDATA_PROD_KEY", "YOUR_PROD_KEY_HERE")  # Use production key

# Step 1: Get valuation for Redondo Beach property (GET request)
print("\nStep 1: Getting valuation for Redondo Beach property (GET)...")

params = {
    "streetAddress": "109 Via La Soledad",
    "city": "Redondo Beach",
    "state": "CA",
    "zip": "90277"
}

try:
    valuation_response = requests.get(
        f"{base_url}/api/Valuation/simple",
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        params=params
    )
    
    print(f"Status Code: {valuation_response.status_code}")
    print(f"Response Headers: {json.dumps(dict(valuation_response.headers), indent=2)}")
    
    if valuation_response.status_code != 200:
        print(f"❌ Valuation API call failed: {valuation_response.text}")
        exit(1)
    
    valuation_data = valuation_response.json()
    print("✓ Valuation API call successful!")
    
    # Display valuation details
    print("\n=== Redondo Beach Property Valuation ===")
    print(json.dumps(valuation_data, indent=2))
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print("Type:", type(e))

print("\nTest complete") 