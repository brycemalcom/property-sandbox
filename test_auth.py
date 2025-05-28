print("=== Acumidata API Authentication Test ===")

import requests
import json
import sys

# Credentials from the screenshot
username = "bmushaney1"
password = "relar2024"
api_key = "J+mZiF5ERbq+qbtCkowTIrQCN5kBYYjlV0PR8ha4LeA="

# Base URL
base_url = "https://uat.api.acumidata.com"

def test_auth_methods():
    """Test different authentication methods with the API"""
    
    # Method 1: Direct Bearer token with API key
    print("\n=== Testing Bearer Token Authentication ===")
    headers_bearer = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        response = requests.get(
            f"{base_url}/api/Comps/advantage",
            headers=headers_bearer,
            params={
                "streetAddress": "2555 N Pearl St",
                "city": "Dallas",
                "state": "TX",
                "zip": "75201"
            }
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✓ Bearer token authentication successful!")
            print("Response preview:")
            response_json = response.json()
            print(json.dumps(response_json, indent=2)[:500] + "..." if len(json.dumps(response_json, indent=2)) > 500 else json.dumps(response_json, indent=2))
        else:
            print(f"❌ Bearer token authentication failed: {response.text}")
    except Exception as e:
        print(f"❌ Error testing bearer token: {str(e)}")
    
    # Method 2: Try to login using the /api/Account/login endpoint
    print("\n=== Testing Login with /api/Account/login ===")
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
        
        print(f"Login Status Code: {login_response.status_code}")
        if login_response.status_code == 200:
            print("✓ Login successful!")
            login_result = login_response.json()
            
            # Extract the API key from the login response
            new_api_key = None
            if 'data' in login_result and 'acumiAPIKey' in login_result['data']:
                new_api_key = login_result['data']['acumiAPIKey']
                print(f"API Key found in response: {new_api_key[:20]}..." if len(new_api_key) > 20 else f"API Key: {new_api_key}")
            else:
                print("❌ No API key found in login response")
                return
            
            # Use the new API key for subsequent requests
            headers_new_key = {
                "Accept": "application/json",
                "Authorization": f"Bearer {new_api_key}"
            }
            
            # Try the Dallas property first (known to work)
            print("\n=== Testing Dallas Property with New API Key ===")
            dallas_response = requests.get(
                f"{base_url}/api/Comps/advantage",
                headers=headers_new_key,
                params={
                    "streetAddress": "2555 N Pearl St",
                    "city": "Dallas",
                    "state": "TX",
                    "zip": "75201"
                }
            )
            
            print(f"Dallas Property API Call Status Code: {dallas_response.status_code}")
            if dallas_response.status_code == 200:
                print("✓ Dallas property API call successful!")
                dallas_json = dallas_response.json()
                print("Response preview:")
                print(json.dumps(dallas_json, indent=2)[:500] + "..." if len(json.dumps(dallas_json, indent=2)) > 500 else json.dumps(dallas_json, indent=2))
                
                # Now try the Belfair property
                print("\n=== Testing Belfair Property with New API Key ===")
                belfair_response = requests.get(
                    f"{base_url}/api/Comps/advantage",
                    headers=headers_new_key,
                    params={
                        "streetAddress": "531 NE Beck Rd",
                        "city": "Belfair",
                        "state": "WA",
                        "zip": "98528"
                    }
                )
                
                print(f"Belfair Property API Call Status Code: {belfair_response.status_code}")
                if belfair_response.status_code == 200:
                    print("✓ Belfair property API call successful!")
                    print("Response preview:")
                    belfair_json = belfair_response.json()
                    print(json.dumps(belfair_json, indent=2)[:500] + "..." if len(json.dumps(belfair_json, indent=2)) > 500 else json.dumps(belfair_json, indent=2))
                else:
                    print(f"❌ Belfair property API call failed: {belfair_response.text}")
                    
                    # Try the Parcels endpoint for Belfair
                    print("\n=== Testing Belfair with Parcels Endpoint ===")
                    parcels_response = requests.get(
                        f"{base_url}/api/Parcels",
                        headers=headers_new_key,
                        params={
                            "address": "531 NE Beck Rd",
                            "city": "Belfair",
                            "state": "WA",
                            "zip": "98528"
                        }
                    )
                    
                    print(f"Belfair Parcels API Call Status Code: {parcels_response.status_code}")
                    if parcels_response.status_code == 200:
                        print("✓ Belfair parcels API call successful!")
                        print("Response preview:")
                        parcels_json = parcels_response.json()
                        print(json.dumps(parcels_json, indent=2)[:500] + "..." if len(json.dumps(parcels_json, indent=2)) > 500 else json.dumps(parcels_json, indent=2))
                    else:
                        print(f"❌ Belfair parcels API call failed: {parcels_response.text}")
                        
                        # Try other endpoints that might work for Belfair
                        endpoints_to_try = [
                            {"name": "Parcels Detail", "endpoint": "api/Parcels/detail", "params": {"address": "531 NE Beck Rd", "city": "Belfair", "state": "WA", "zip": "98528"}},
                            {"name": "Parcels Detail With Comp", "endpoint": "api/Parcels/detailWithComp", "params": {"address": "531 NE Beck Rd", "city": "Belfair", "state": "WA", "zip": "98528"}},
                            {"name": "Valuation Simple", "endpoint": "api/Valuation/simple", "params": {"address": "531 NE Beck Rd", "city": "Belfair", "state": "WA", "zip": "98528"}}
                        ]
                        
                        for endpoint_info in endpoints_to_try:
                            print(f"\n=== Testing {endpoint_info['name']} Endpoint ===")
                            try:
                                endpoint_response = requests.get(
                                    f"{base_url}/{endpoint_info['endpoint']}",
                                    headers=headers_new_key,
                                    params=endpoint_info['params']
                                )
                                
                                print(f"Status Code: {endpoint_response.status_code}")
                                if endpoint_response.status_code == 200:
                                    print(f"✓ {endpoint_info['name']} API call successful!")
                                    print("Response preview:")
                                    endpoint_json = endpoint_response.json()
                                    print(json.dumps(endpoint_json, indent=2)[:500] + "..." if len(json.dumps(endpoint_json, indent=2)) > 500 else json.dumps(endpoint_json, indent=2))
                                else:
                                    print(f"❌ {endpoint_info['name']} API call failed: {endpoint_response.text}")
                            except Exception as e:
                                print(f"❌ Error testing {endpoint_info['name']}: {str(e)}")
            else:
                print(f"❌ Dallas property API call failed: {dallas_response.text}")
        else:
            print(f"❌ Login failed: {login_response.text}")
    except Exception as e:
        print(f"❌ Error testing login: {str(e)}")

if __name__ == "__main__":
    print("Starting authentication tests...")
    test_auth_methods()
    print("\nTests completed.") 