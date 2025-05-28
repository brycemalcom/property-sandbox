print("Starting test script...")

from acumidata_client import AcumidataClient
import json
import sys

def test_basic_connection():
    print("\n=== Acumidata API Connection Test ===")
    
    # Test UAT environment
    print("\nTesting UAT Environment...")
    try:
        uat_client = AcumidataClient(environment="uat")
        print(f"✓ Client initialized")
        print(f"UAT API Key: {'*' * len(uat_client.api_key)}")
        print(f"UAT Base URL: {uat_client.base_url}")
    except Exception as e:
        print("\n❌ Failed to initialize client!")
        print(f"Error: {str(e)}")
        sys.exit(1)
    
    # Try different endpoints to check API capabilities
    endpoints_to_try = [
        {
            "name": "Comps Advantage for Dallas property",
            "endpoint": "api/Comps/advantage",
            "params": {"streetAddress": "2555 N Pearl St", "city": "Dallas", "state": "TX", "zip": "75201"}
        },
        {
            "name": "Comps Advantage for Belfair property",
            "endpoint": "api/Comps/advantage",
            "params": {"streetAddress": "531 NE Beck Rd", "city": "Belfair", "state": "WA", "zip": "98528"}
        },
        {
            "name": "API Status or Info (if available)",
            "endpoint": "api/status",
            "params": {}
        }
    ]
    
    success = False
    
    for test_case in endpoints_to_try:
        try:
            print(f"\n\nTesting: {test_case['name']}")
            print(f"Endpoint: {test_case['endpoint']}")
            print(f"Params: {test_case['params']}")
            
            response = uat_client._make_request(
                endpoint=test_case['endpoint'],
                params=test_case['params']
            )
            
            print("\n✓ Response received!")
            
            # Validate response structure
            if isinstance(response, dict):
                if 'error' in response:
                    print(f"❌ API returned an error: {response['error']}")
                    continue
                    
                print("Response Summary:")
                print(f"Keys in response: {list(response.keys())}")
                
                # Print a sample of the response
                print("\nSample response data:")
                response_str = json.dumps(response, indent=2)
                print(response_str[:500] + "..." if len(response_str) > 500 else response_str)
                
                success = True
            else:
                print(f"⚠️ Warning: Response is not in expected format. Type: {type(response)}")
            
        except Exception as e:
            print(f"❌ Test Failed: {str(e)}")
    
    return success

if __name__ == "__main__":
    print("Running test function...")
    success = test_basic_connection()
    print("\nTest completed.")
    print(f"Final status: {'✓ SUCCESS' if success else '❌ FAILED'}")
    sys.exit(0 if success else 1)
