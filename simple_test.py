print("=== Acumidata API Test ===")

from acumidata_client import AcumidataClient

print("A. Creating client...")
client = AcumidataClient(environment="uat")

test_params = {
    "streetAddress": "531 NE Beck Rd",
    "city": "Belfair",
    "state": "WA",
    "zip": "98528"
}

print("B. Starting test...")

try:
    print("C. Making API request...")
    response = client._make_request(
        endpoint="api/Comps/advantage",
        params=test_params
    )
    
    print("D. Got response:", type(response))
    print("E. Response data:", response)
    
except Exception as e:
    print(f"F. Error in test script: {str(e)}")

print("G. Test complete")
