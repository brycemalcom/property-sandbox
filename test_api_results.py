import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_acumidata_api():
    """
    Test the Acumidata API and display the results
    """
    print("=== Acumidata API Test ===")
    
    # Get credentials from .env file
    username = os.getenv("ACUMIDATA_USERNAME", "bmushaney1")
    password = os.getenv("ACUMIDATA_PASSWORD", "relar2024")
    
    # Base URL for UAT environment
    base_url = "https://uat.api.acumidata.com"
    
    # Step 1: Login to get API key
    print("\nStep 1: Logging in to get API key...")
    try:
        login_data = {
            "username": username,
            "password": password
        }
        
        login_response = requests.post(
            f"{base_url}/api/Account/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return
        
        login_result = login_response.json()
        
        # Extract the API key from the login response
        if 'data' not in login_result or 'acumiAPIKey' not in login_result['data']:
            print("❌ No API key found in login response")
            return
        
        api_key = login_result['data']['acumiAPIKey']
        print(f"✓ Successfully logged in as {username}")
        print(f"✓ API Key: {api_key[:10]}...")
        
        # Step 2: Test with Dallas property
        print("\nStep 2: Testing Dallas property...")
        dallas_response = requests.get(
            f"{base_url}/api/Comps/advantage",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            params={
                "streetAddress": "2555 N Pearl St",
                "city": "Dallas",
                "state": "TX",
                "zip": "75201"
            }
        )
        
        if dallas_response.status_code != 200:
            print(f"❌ Dallas property API call failed: {dallas_response.text}")
            return
        
        dallas_data = dallas_response.json()
        print("✓ Dallas property API call successful!")
        
        # Display property details
        print("\n=== Dallas Property Details ===")
        if "mlsData" in dallas_data and dallas_data["mlsData"]:
            mls_data = dallas_data["mlsData"]
            print(f"Address: {mls_data.get('address', 'N/A')}, {mls_data.get('city', 'N/A')}, {mls_data.get('state', 'N/A')} {mls_data.get('zip', 'N/A')}")
            print(f"Beds: {mls_data.get('beds', 'N/A')}")
            print(f"Baths: {mls_data.get('baths', 'N/A')}")
            print(f"Year Built: {mls_data.get('yearBuilt', 'N/A')}")
            print(f"Size: {mls_data.get('size', 'N/A')} sq ft")
            print(f"Lot Size: {mls_data.get('lotSize', 'N/A')}")
            print(f"Predicted Price: ${mls_data.get('predictedPrice', 'N/A')}")
        else:
            print("No MLS data found for Dallas property")
        
        # Step 3: Test with Belfair property
        print("\nStep 3: Testing Belfair property...")
        belfair_response = requests.get(
            f"{base_url}/api/Comps/advantage",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            params={
                "streetAddress": "531 NE Beck Rd",
                "city": "Belfair",
                "state": "WA",
                "zip": "98528"
            }
        )
        
        if belfair_response.status_code != 200:
            print(f"❌ Belfair property API call failed: {belfair_response.text}")
            return
        
        belfair_data = belfair_response.json()
        print("✓ Belfair property API call successful!")
        
        # Display property details
        print("\n=== Belfair Property Details ===")
        if "mlsData" in belfair_data and belfair_data["mlsData"]:
            mls_data = belfair_data["mlsData"]
            print(f"Address: {mls_data.get('address', 'N/A')}, {mls_data.get('city', 'N/A')}, {mls_data.get('state', 'N/A')} {mls_data.get('zip', 'N/A')}")
            print(f"Beds: {mls_data.get('beds', 'N/A')}")
            print(f"Baths: {mls_data.get('baths', 'N/A')}")
            print(f"Year Built: {mls_data.get('yearBuilt', 'N/A')}")
            print(f"Size: {mls_data.get('size', 'N/A')} sq ft")
            print(f"Lot Size: {mls_data.get('lotSize', 'N/A')}")
            print(f"Predicted Price: ${mls_data.get('predictedPrice', 'N/A')}")
        else:
            print("No MLS data found for Belfair property")
        
        # Option to save raw data
        save_option = input("\nWould you like to save the raw API response data to files? (y/n): ")
        if save_option.lower() == 'y':
            with open("dallas_property_data.json", 'w') as f:
                json.dump(dallas_data, f, indent=2)
            with open("belfair_property_data.json", 'w') as f:
                json.dump(belfair_data, f, indent=2)
            print("Data saved to dallas_property_data.json and belfair_property_data.json")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_acumidata_api() 